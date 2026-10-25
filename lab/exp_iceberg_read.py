"""Chapter 12, part 2: pruning layers measured with Iceberg scan reports and task input bytes."""
from labutil import run_scan as run, session, show

spark = session("exp-iceberg-read")
spark.conf.set("spark.sql.adaptive.enabled", "false")   # so executedPlan() is a plain tree with scan metrics
C = spark.conf.set
T = "TIMESTAMP"

# --- A. manifest pruning: a table built by 31 daily commits has 31 manifests ------------------------------------
spark.sql("DROP TABLE IF EXISTS orders_inc")
spark.sql("CREATE TABLE orders_inc USING iceberg PARTITIONED BY (days(order_ts)) AS SELECT * FROM orders WHERE 1 = 0")
for d in range(1, 32):
    lo = f"2026-03-{d:02d} 00:00:00"
    hi = f"2026-03-{d + 1:02d} 00:00:00" if d < 31 else "2026-04-01 00:00:00"
    spark.sql(f"INSERT INTO orders_inc SELECT * FROM orders WHERE order_ts >= {T} '{lo}' AND order_ts < {T} '{hi}'")
show(spark, "r1_inc_manifests", "SELECT count(*) AS manifests, sum(added_data_files_count) AS files FROM lab.db.orders_inc.manifests")
WEEK = f"SELECT sum(order_total) AS s FROM {{t}} WHERE order_ts >= {T} '2026-03-01 00:00:00' AND order_ts < {T} '2026-03-08 00:00:00'"
print("### week_orders_inc"); run(spark, "r2_week_orders_inc", WEEK.format(t="orders_inc"))
print("### week_orders"); run(spark, "r3_week_orders", WEEK.format(t="orders"))
print("### month_orders_inc"); run(spark, "r4_month_orders_inc", "SELECT sum(order_total) AS s FROM orders_inc")

# --- B. file-level pruning needs statistics AND order: four copies of ten days ------------------------------------------
SUB = f"SELECT * FROM orders WHERE order_ts < {T} '2026-03-11 00:00:00'"
for t in ["t_plain", "t_bloom", "t_sorted", "t_sorted_counts"]:
    spark.sql(f"DROP TABLE IF EXISTS {t}")
spark.sql(f"CREATE TABLE t_plain USING iceberg AS {SUB}")
spark.sql(f"CREATE TABLE t_bloom USING iceberg TBLPROPERTIES ('write.parquet.bloom-filter-enabled.column.customer_id'='true') AS {SUB}")
spark.sql(f"CREATE TABLE t_sorted USING iceberg AS {SUB} ORDER BY customer_id")
spark.sql(f"CREATE TABLE t_sorted_counts USING iceberg TBLPROPERTIES ('write.metadata.metrics.default'='counts') AS {SUB} ORDER BY customer_id")
for t in ["t_plain", "t_bloom", "t_sorted", "t_sorted_counts"]:
    show(spark, f"r5_files_{t}", f"SELECT count(*) AS files, round(avg(file_size_in_bytes)/1e6,1) AS avg_mb FROM lab.db.{t}.files")
cust = spark.sql("SELECT customer_id FROM t_plain LIMIT 1").collect()[0][0]
print("lookup customer:", cust)
LOOK = "SELECT count(*) AS n, sum(order_total) AS s FROM {t} WHERE customer_id = '" + cust + "'"
for t in ["t_plain", "t_bloom", "t_sorted", "t_sorted_counts"]:
    print("### lookup_" + t); run(spark, f"r6_lookup_{t}", LOOK.format(t=t))
show(spark, "r7_sorted_bounds",
     "SELECT readable_metrics.customer_id.lower_bound AS lo, readable_metrics.customer_id.upper_bound AS hi FROM lab.db.t_sorted.files ORDER BY lo LIMIT 4")
show(spark, "r8_counts_bounds",
     "SELECT readable_metrics.customer_id.lower_bound AS lo, readable_metrics.customer_id.value_count AS n FROM lab.db.t_sorted_counts.files LIMIT 3")

# --- C. vectorized reads on/off ---------------------------------------------------------------------------------------------------
Q = "SELECT sum(order_total) AS s FROM t_plain"
print("### vec_on"); run(spark, "r9_vec_on", Q)
spark.sql("ALTER TABLE t_plain SET TBLPROPERTIES ('read.parquet.vectorization.enabled'='false')")
print("### vec_off"); run(spark, "r10_vec_off", Q)
spark.sql("ALTER TABLE t_plain SET TBLPROPERTIES ('read.parquet.vectorization.enabled'='true')")

# --- D. split planning: files per split ---------------------------------------------------------------------------------------
FULL = "SELECT sum(order_total) AS s FROM orders"
for label, size in [("default128", None), ("t8mb", 8 * 1024 * 1024), ("t512mb", 512 * 1024 * 1024)]:
    if size:
        spark.sql(f"ALTER TABLE orders SET TBLPROPERTIES ('read.split.target-size'='{size}')")
    print("### split_" + label); run(spark, f"r11_split_{label}", FULL)
spark.sql("ALTER TABLE orders UNSET TBLPROPERTIES ('read.split.target-size')")
print("DONE")
