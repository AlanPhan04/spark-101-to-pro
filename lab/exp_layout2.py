"""Chapter 11, part 2: sort order vs Z-order, write distribution modes, and the hot key under bucket + hash."""
import json
import time

from labutil import OUT, run_scan as run, session, show

spark = session("exp-layout2")
spark.conf.set("spark.sql.adaptive.enabled", "false")
T = "TIMESTAMP"
res = {}


def tm(fn):
    t = time.time(); fn(); return round(time.time() - t, 1)


# --- D. sort order vs Z-order: lookups on one column, the other, and both ------------------------------------------------------
SUB = f"SELECT * FROM orders WHERE order_ts < {T} '2026-03-11 00:00:00'"
for t in ("t_zbase", "t_zsort", "t_zorder"):
    spark.sql(f"DROP TABLE IF EXISTS {t} PURGE")
    spark.sql(f"CREATE TABLE {t} USING iceberg TBLPROPERTIES ('write.target-file-size-bytes'='8388608') AS {SUB}")
OPT = "options => map('target-file-size-bytes','8388608','min-input-files','1','rewrite-all','true')"
spark.sql("CALL lab.system.rewrite_data_files(table => 'db.t_zsort', strategy => 'sort', sort_order => 'customer_id ASC NULLS LAST, product_id ASC NULLS LAST', " + OPT + ")")
spark.sql("CALL lab.system.rewrite_data_files(table => 'db.t_zorder', strategy => 'sort', sort_order => 'zorder(customer_id, product_id)', " + OPT + ")")
for t in ("t_zbase", "t_zsort", "t_zorder"):
    show(spark, f"z1_files_{t}", f"SELECT count(*) AS files, round(avg(file_size_in_bytes)/1e6,1) AS avg_mb FROM lab.db.{t}.files")
cust = spark.sql("SELECT customer_id FROM t_zbase LIMIT 1").collect()[0][0]
prod = spark.sql("SELECT product_id FROM t_zbase WHERE product_id <> 'p0000042' LIMIT 1").collect()[0][0]
print("lookup keys", cust, prod)
PRED = {"customer": f"customer_id = '{cust}'", "product": f"product_id = '{prod}'", "both": f"customer_id = '{cust}' AND product_id = '{prod}'"}
for t in ("t_zbase", "t_zsort", "t_zorder"):
    for k, p in PRED.items():
        run(spark, f"z2_{t}_{k}", f"SELECT count(*) AS n, sum(order_total) AS s FROM {t} WHERE {p}")

# --- E. write distribution mode into a partitioned table from a table whose rows are NOT ordered by day -------------------------------
spark.sql("DROP TABLE IF EXISTS t_src PURGE")
spark.sql(f"CREATE TABLE t_src USING iceberg AS {SUB}")
for mode in ("none", "hash", "range"):
    t = f"t_dist_{mode}"
    spark.sql(f"DROP TABLE IF EXISTS {t} PURGE")
    spark.sql(f"CREATE TABLE {t} (order_id string, order_ts timestamp, product_id string, customer_id string, promised_days int, delivery_days int, order_total double) USING iceberg PARTITIONED BY (days(order_ts)) TBLPROPERTIES ('write.distribution-mode'='{mode}','write.spark.fanout.enabled'='true')")
    res[f"{mode}_insert_s"] = tm(lambda: spark.sql(f"INSERT INTO {t} SELECT /*+ REPARTITION(10) */ * FROM t_src"))
    show(spark, f"z3_dist_{mode}", f"SELECT count(*) AS files, round(avg(file_size_in_bytes)/1e6,2) AS avg_mb, round(min(file_size_in_bytes)/1e6,2) AS min_mb FROM lab.db.{t}.files")

# --- F. hot key under bucket + hash distribution ---------------------------------------------------------------------------------------------------
spark.sql("DROP TABLE IF EXISTS t_bkt PURGE")
spark.sql(f"CREATE TABLE t_bkt USING iceberg PARTITIONED BY (bucket(16, product_id)) TBLPROPERTIES ('write.distribution-mode'='hash') AS {SUB}")
show(spark, "z4_bucket_files", "SELECT partition, record_count, file_count, round(total_data_file_size_in_bytes/1e6,1) AS mb FROM lab.db.t_bkt.partitions ORDER BY record_count DESC", n=20)
json.dump(res, open(f"{OUT}/layout2_results.json", "w"), indent=1)
print("DONE")
