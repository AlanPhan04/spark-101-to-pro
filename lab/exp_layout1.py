"""Chapter 11, part 1: partition evolution, partition granularity (hour vs day), and the identity-on-timestamp trap."""
import json
import time

from labutil import OUT, run_scan as run, session, show

spark = session("exp-layout1")
spark.conf.set("spark.sql.adaptive.enabled", "false")
T = "TIMESTAMP"
res = {}


def tm(fn):
    t = time.time(); fn(); return round(time.time() - t, 1)


# --- A. partition evolution: months -> days ------------------------------------------------------------------------------------------
spark.sql("DROP TABLE IF EXISTS t_evo PURGE")
spark.sql(f"CREATE TABLE t_evo USING iceberg PARTITIONED BY (months(order_ts)) AS SELECT * FROM orders WHERE order_ts < {T} '2026-03-16 00:00:00'")
spark.sql("ALTER TABLE t_evo REPLACE PARTITION FIELD months(order_ts) WITH days(order_ts)")
spark.sql(f"INSERT INTO t_evo SELECT * FROM orders WHERE order_ts >= {T} '2026-03-16 00:00:00'")
show(spark, "l1_evo_partitions", "SELECT spec_id, partition, record_count, file_count FROM lab.db.t_evo.partitions ORDER BY spec_id, partition LIMIT 6", truncate=40)
show(spark, "l2_evo_files_by_spec", "SELECT spec_id, count(*) AS files, round(avg(file_size_in_bytes)/1e6,1) AS avg_mb, round(max(file_size_in_bytes)/1e6,1) AS max_mb FROM lab.db.t_evo.files GROUP BY spec_id ORDER BY spec_id")
DAY = "SELECT sum(order_total) AS s FROM t_evo WHERE order_ts >= TIMESTAMP '2026-03-{d} 00:00:00' AND order_ts < TIMESTAMP '2026-03-{e} 00:00:00'"
run(spark, "l3_evo_query_old_day", DAY.format(d="05", e="06"))
run(spark, "l4_evo_query_new_day", DAY.format(d="20", e="21"))

# --- B. granularity: day vs hour partitions of the whole month ---------------------------------------------------------------------------
for name, tr in (("t_day", "days(order_ts)"), ("t_hour", "hours(order_ts)")):
    spark.sql(f"DROP TABLE IF EXISTS {name} PURGE")
    res[f"{name}_create_s"] = tm(lambda: spark.sql(f"CREATE TABLE {name} USING iceberg PARTITIONED BY ({tr}) AS SELECT * FROM orders"))
    show(spark, f"l5_files_{name}", f"SELECT count(*) AS files, round(avg(file_size_in_bytes)/1e6,2) AS avg_mb, round(min(file_size_in_bytes)/1e6,2) AS min_mb FROM lab.db.{name}.files")
    run(spark, f"l6_week_{name}", f"SELECT sum(order_total) AS s FROM {name} WHERE order_ts >= {T} '2026-03-01 00:00:00' AND order_ts < {T} '2026-03-08 00:00:00'")
    spark.sql(f"DROP TABLE IF EXISTS {name} PURGE") if name == "t_hour" else None
    if name == "t_hour":
        pass

# --- C. identity partition on a timestamp: one hour of orders ---------------------------------------------------------------------------------
spark.sql("DROP TABLE IF EXISTS t_ident PURGE")
res["ident_create_s"] = tm(lambda: spark.sql(f"CREATE TABLE t_ident USING iceberg PARTITIONED BY (order_ts) AS SELECT * FROM orders WHERE order_ts >= {T} '2026-03-02 00:00:00' AND order_ts < {T} '2026-03-02 01:00:00'"))
show(spark, "l7_files_ident", "SELECT count(*) AS files, round(avg(file_size_in_bytes)/1e3,1) AS avg_kb, sum(record_count) AS rows FROM lab.db.t_ident.files")
spark.sql("DROP TABLE IF EXISTS t_hour1 PURGE")
res["hour1_create_s"] = tm(lambda: spark.sql(f"CREATE TABLE t_hour1 USING iceberg PARTITIONED BY (hours(order_ts)) AS SELECT * FROM orders WHERE order_ts >= {T} '2026-03-02 00:00:00' AND order_ts < {T} '2026-03-02 01:00:00'"))
show(spark, "l8_files_hour1", "SELECT count(*) AS files, round(avg(file_size_in_bytes)/1e3,1) AS avg_kb, sum(record_count) AS rows FROM lab.db.t_hour1.files")
json.dump(res, open(f"{OUT}/layout1_results.json", "w"), indent=1)
print("DONE")
