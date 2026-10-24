"""Chapter 7 experiments: static pruning variants, DPP on/off, coalesce vs repartition, bucketed (SPJ) join."""
from labutil import OUT, plan_text, run, session

spark = session("exp-pruning")
C = spark.conf.set
SUM = "SELECT sum(order_total) AS s FROM orders WHERE "

# --- E4: one-day filter written five ways ------------------------------------------------------------
variants = {
    "p1_range_day":   "order_ts >= TIMESTAMP '2026-03-03 00:00:00' AND order_ts < TIMESTAMP '2026-03-04 00:00:00'",
    "p2_date_func":   "date(order_ts) = DATE '2026-03-03'",
    "p3_cast_date":   "CAST(order_ts AS DATE) = DATE '2026-03-03'",
    "p4_cast_string": "CAST(order_ts AS STRING) LIKE '2026-03-03%'",
    "p5_arith":       "order_ts + INTERVAL 1 DAY > TIMESTAMP '2026-03-04 00:00:00' AND order_ts + INTERVAL 1 DAY <= TIMESTAMP '2026-03-05 00:00:00'",
    "p6_week_range":  "order_ts >= TIMESTAMP '2026-03-01 00:00:00' AND order_ts < TIMESTAMP '2026-03-08 00:00:00'",
}
for name, pred in variants.items():
    run(spark, f"e4_{name}", SUM + pred)

# --- E5: dynamic partition pruning ----------------------------------------------------------------------
DPP = """SELECT p.category, count(*) AS n
         FROM orders o
         JOIN dim_date d ON CAST(o.order_ts AS DATE) = d.date
         JOIN dim_product p ON o.product_id = p.product_id
         WHERE d.day_of_week = 'Sat' AND d.month = 3
         GROUP BY p.category"""
C("spark.sql.optimizer.dynamicPartitionPruning.enabled", "false")
run(spark, "e5a_dpp_off", DPP)
C("spark.sql.optimizer.dynamicPartitionPruning.enabled", "true")
run(spark, "e5b_dpp_on", DPP)

# --- E7: coalesce vs repartition before a write ------------------------------------------------------------
def noop(group, df):
    spark.sparkContext.setJobGroup(group, group)
    df.write.format("noop").mode("overwrite").save()
    with open(f"{OUT}/{group}.simple.txt", "w", encoding="utf-8") as f:
        f.write(plan_text(df, "simple"))
    print("===", group)

base = spark.table("orders").where("order_ts >= TIMESTAMP '2026-03-01 00:00:00' AND order_ts < TIMESTAMP '2026-03-15 00:00:00'")
noop("e7a_no_change", base)
noop("e7b_coalesce10", base.coalesce(10))
noop("e7c_repartition10", base.repartition(10))

# --- E6: bucketed (storage-partitioned) join --------------------------------------------------------------------
spark.sql("DROP TABLE IF EXISTS orders_b")
spark.sql("DROP TABLE IF EXISTS dim_customer_b")
spark.sql("CREATE TABLE orders_b USING iceberg PARTITIONED BY (bucket(16, customer_id)) AS SELECT * FROM orders")
spark.sql("CREATE TABLE dim_customer_b USING iceberg PARTITIONED BY (bucket(16, customer_id)) AS SELECT * FROM dim_customer")
JOIN_B = """SELECT c.segment, count(*) AS n
            FROM orders_b o JOIN dim_customer_b c ON o.customer_id = c.customer_id
            GROUP BY c.segment"""
C("spark.sql.autoBroadcastJoinThreshold", "-1")
C("spark.sql.sources.v2.bucketing.enabled", "false")
run(spark, "e6a_bucketed_spj_off", JOIN_B)
C("spark.sql.sources.v2.bucketing.enabled", "true")
C("spark.sql.iceberg.planning.preserve-data-grouping", "true")
C("spark.sql.requireAllClusterKeysForCoPartition", "false")
run(spark, "e6b_bucketed_spj_on", JOIN_B)
print("DONE")
