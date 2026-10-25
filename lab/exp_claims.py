"""Experiments that replace the book's remaining 'claim -- not tested' marks. Usage: exp_claims.py <mode>

  bucketskew   Ch7: a bucketed join on the hot key (task time spread)
  rangerebal   Ch7: repartitionByRange and REBALANCE under AQE (tasks that ran)
  offheapcache Ch8: StorageLevel.OFF_HEAP, where the bytes go
  dangling     Ch13: rewrite_data_files remove-dangling-deletes
  replay       Ch16: lose the last commit-log entry, restart, check for duplicates
  jdbccat      Ch10: a service-style (JDBC/sqlite) catalog, pointer row and a lost swap
"""
import json
import os
import shutil
import sys
import time

from pyspark.sql import functions as F

from labutil import OUT, session

mode = sys.argv[1]
spark = session("claims-" + mode)
spark.conf.set("spark.sql.adaptive.enabled", "false")
res = {}

if mode == "bucketskew":
    spark.sql("DROP TABLE IF EXISTS orders_bp PURGE")
    spark.sql("DROP TABLE IF EXISTS dim_product_bp PURGE")
    spark.sql("CREATE TABLE orders_bp USING iceberg PARTITIONED BY (bucket(16, product_id)) AS SELECT * FROM orders")
    spark.sql("CREATE TABLE dim_product_bp USING iceberg PARTITIONED BY (bucket(16, product_id)) AS SELECT * FROM dim_product")
    spark.conf.set("spark.sql.sources.v2.bucketing.enabled", "true")
    spark.conf.set("spark.sql.iceberg.planning.preserve-data-grouping", "true")
    spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "-1")
    spark.sparkContext.setJobGroup("claim_bucketskew", "b")
    spark.sql("SELECT p.category, count(*) FROM orders_bp o JOIN dim_product_bp p ON o.product_id = p.product_id GROUP BY p.category").collect()
    spark.sparkContext.setJobGroup("claim_bucketskew_plan", "b")
    plan = spark.sql("EXPLAIN SELECT p.category, count(*) FROM orders_bp o JOIN dim_product_bp p ON o.product_id = p.product_id GROUP BY p.category").collect()[0][0]
    res["exchange_count"] = plan.count("Exchange")
    res["plan_has_shuffle_before_join"] = "Exchange hashpartitioning(product_id" in plan

elif mode == "rangerebal":
    spark.conf.set("spark.sql.adaptive.enabled", "true")
    spark.conf.set("spark.sql.shuffle.partitions", "200")
    sc = spark.sparkContext
    cases = {"repartitionByRange(200, customer_id)": "SELECT /*+ REPARTITION_BY_RANGE(200, customer_id) */ order_id, customer_id FROM orders",
             "REBALANCE": "SELECT /*+ REBALANCE */ order_id, customer_id FROM orders",
             "REBALANCE(customer_id)": "SELECT /*+ REBALANCE(customer_id) */ order_id, customer_id FROM orders"}
    for i, (name, q) in enumerate(cases.items()):
        sc.setJobGroup(f"claim_rr_{i}", name)
        spark.sql(q).write.format("noop").mode("overwrite").save()
    res["cases"] = list(cases)

elif mode == "offheapcache":
    from pyspark import StorageLevel
    sc = spark.sparkContext
    df = spark.table("orders").select("order_id", "customer_id", "order_total").where("order_total > 10")
    df.persist(StorageLevel.OFF_HEAP)
    sc.setJobGroup("claim_offheap_fill", "f")
    df.count()
    info = [(i.name(), i.storageLevel().toString(), i.memSize(), i.diskSize()) for i in sc._jsc.sc().getRDDStorageInfo()]
    res["storage"] = [list(map(str, x)) for x in info]
    res["offheap_enabled"] = spark.conf.get("spark.memory.offHeap.enabled")
    res["offheap_size"] = spark.conf.get("spark.memory.offHeap.size")
    mm = sc._jsc.sc().env().memoryManager()
    res["offheap_storage_used_mb"] = round(mm.offHeapStorageMemoryUsed() / 1e6, 1)
    res["onheap_storage_used_mb"] = round(mm.onHeapStorageMemoryUsed() / 1e6, 1)

elif mode == "dangling":
    T = "TIMESTAMP"
    spark.sql("DROP TABLE IF EXISTS t_dang PURGE")
    spark.sql(f"CREATE TABLE t_dang USING iceberg PARTITIONED BY (days(order_ts)) AS SELECT * FROM orders WHERE order_ts < {T} '2026-03-04 00:00:00'")
    spark.sql("ALTER TABLE t_dang SET TBLPROPERTIES ('write.delete.mode'='merge-on-read','write.update.mode'='merge-on-read')")
    ids = [r[0] for r in spark.sql("SELECT order_id FROM t_dang LIMIT 30").collect()]
    for i in range(6):
        spark.sql("DELETE FROM t_dang WHERE order_id IN (%s)" % ",".join("'%s'" % x for x in ids[i * 5:(i + 1) * 5]))

    def counts():
        r = spark.sql("SELECT content, count(*) n FROM lab.db.t_dang.files GROUP BY content ORDER BY content").collect()
        return {int(x[0]): int(x[1]) for x in r}
    res["before"] = counts()
    spark.sql("CALL lab.system.rewrite_data_files(table => 'db.t_dang', options => map('rewrite-all','true'))").collect()
    res["after_rewrite"] = counts()
    try:
        spark.sql("CALL lab.system.rewrite_data_files(table => 'db.t_dang', options => map('rewrite-all','true','remove-dangling-deletes','true'))").collect()
        res["after_remove_dangling"] = counts()
    except Exception as e:
        j = getattr(e, "java_exception", None)
        res["remove_dangling_error"] = (j.getMessage() if j is not None else str(e)).strip().splitlines()[0][:220]
    try:
        spark.sql("CALL lab.system.rewrite_position_delete_files(table => 'db.t_dang')").show(truncate=False)
        res["after_rewrite_position_delete_files"] = counts()
    except Exception as e:
        j = getattr(e, "java_exception", None)
        res["rewrite_position_delete_files_error"] = (j.getMessage() if j is not None else str(e)).strip().splitlines()[0][:220]

elif mode == "replay":
    # run 1: stream until a few commits exist; then the host deletes the last commits/<n> entry; run 2 restarts
    CK = "/lab/ckpt/replay"
    phase = sys.argv[2]
    src = (spark.readStream.format("rate").option("rowsPerSecond", 1000).option("numPartitions", 1).load()
           .select(F.col("value").alias("seq"), F.col("timestamp").alias("order_ts"), F.lit("c").alias("customer_id"), F.lit(1.0).alias("order_total")))
    if phase == "first":
        spark.sql("DROP TABLE IF EXISTS s_replay PURGE")
        spark.sql("CREATE TABLE s_replay (seq BIGINT, order_ts TIMESTAMP, customer_id STRING, order_total DOUBLE) USING iceberg")
        shutil.rmtree(CK, ignore_errors=True)
    if phase == "second":
        last = max(int(x) for x in os.listdir(f"{CK}/commits") if x.isdigit())
        os.remove(f"{CK}/commits/{last}")
        if os.path.exists(f"{CK}/commits/.{last}.crc"):
            os.remove(f"{CK}/commits/.{last}.crc")
        res["removed_commit_entry"] = last
    q = src.writeStream.format("iceberg").trigger(processingTime="3 seconds").option("checkpointLocation", CK).toTable("lab.db.s_replay")
    time.sleep(25 if phase == "first" else 45)
    q.stop()
    r = spark.sql("SELECT count(*) n, count(distinct seq) d FROM s_replay").collect()[0]
    ep = [int(x[0]) for x in spark.sql("SELECT summary['spark.sql.streaming.epochId'] FROM lab.db.s_replay.snapshots ORDER BY committed_at").collect()]
    res.update({"phase": phase, "rows": r["n"], "distinct": r["d"], "epochs": ep, "commit_entries": sorted(int(x) for x in os.listdir(f"{CK}/commits") if x.isdigit())})

elif mode == "jdbccat":
    spark.conf.set("spark.sql.catalog.jd", "org.apache.iceberg.spark.SparkCatalog")
    spark.conf.set("spark.sql.catalog.jd.catalog-impl", "org.apache.iceberg.jdbc.JdbcCatalog")
    spark.conf.set("spark.sql.catalog.jd.uri", "jdbc:sqlite:/lab/jdbc_catalog.db")
    spark.conf.set("spark.sql.catalog.jd.warehouse", "/lab/jdbc_wh")
    spark.sql("CREATE NAMESPACE IF NOT EXISTS jd.db")
    spark.sql("DROP TABLE IF EXISTS jd.db.t PURGE")
    spark.sql("CREATE TABLE jd.db.t (id BIGINT) USING iceberg")
    spark.sql("INSERT INTO jd.db.t VALUES (1),(2)")
    import sqlite3
    c = sqlite3.connect("/lab/jdbc_catalog.db")
    cols = [r[1] for r in c.execute("PRAGMA table_info(iceberg_tables)")]
    row = c.execute("SELECT * FROM iceberg_tables WHERE table_name='t'").fetchone()
    res["catalog_table_columns"] = cols
    res["pointer_row"] = dict(zip(cols, row))
    # the conditional update: a stale writer's UPDATE ... WHERE previous_metadata_location = <old> touches 0 rows
    old = row[cols.index("previous_metadata_location")]
    cur = c.execute("UPDATE iceberg_tables SET metadata_location='x' WHERE table_name='t' AND metadata_location=?", (old,))
    res["stale_swap_rows_updated"] = cur.rowcount
    c.rollback()
    res["files_in_warehouse"] = sum(len(f) for _, _, f in os.walk("/lab/jdbc_wh"))

print("RESULT", json.dumps(res, default=str))
json.dump(res, open(f"{OUT}/claims_{mode}{'_' + sys.argv[2] if len(sys.argv) > 2 else ''}.json", "w"), indent=1, default=str)
