"""Chapter 6 experiments: coalescing, broadcast promotion, skew handling."""
from labutil import run, session

spark = session("exp-aqe")
C = spark.conf.set

# --- E1: coalescing, 2000 shuffle partitions, three settings ------------------------------------
GROUPBY = """SELECT customer_id, count(*) AS n, sum(order_total) AS total
             FROM orders
             WHERE order_ts >= TIMESTAMP '2026-03-01 00:00:00' AND order_ts < TIMESTAMP '2026-03-08 00:00:00'
             GROUP BY customer_id"""
C("spark.sql.shuffle.partitions", "2000")

C("spark.sql.adaptive.enabled", "false")
run(spark, "e1a_coalesce_aqe_off", GROUPBY)

C("spark.sql.adaptive.enabled", "true")
C("spark.sql.adaptive.coalescePartitions.parallelismFirst", "true")
run(spark, "e1b_coalesce_pf_true", GROUPBY)

C("spark.sql.adaptive.coalescePartitions.parallelismFirst", "false")
run(spark, "e1c_coalesce_pf_false", GROUPBY)

# a bigger shuffle (whole month, high-cardinality key pair): the advisory size should now bind
BIG = """SELECT count(*) FROM (SELECT customer_id, product_id, count(*) AS n FROM orders GROUP BY customer_id, product_id)"""
C("spark.sql.adaptive.coalescePartitions.parallelismFirst", "true")
run(spark, "e1d_big_pf_true_adv64", BIG)
C("spark.sql.adaptive.advisoryPartitionSizeInBytes", str(16 * 1024 * 1024))
run(spark, "e1e_big_pf_true_adv16", BIG)
spark.conf.unset("spark.sql.adaptive.advisoryPartitionSizeInBytes")
C("spark.sql.shuffle.partitions", "200")

# --- E2: runtime broadcast promotion: dim_product is big on disk, small after the category filter -----------
FILTERED = """SELECT p.category, count(*) AS orders
              FROM orders o JOIN dim_product p ON o.product_id = p.product_id
              WHERE o.order_ts >= TIMESTAMP '2026-03-01 00:00:00' AND o.order_ts < TIMESTAMP '2026-03-08 00:00:00'
                AND p.category = 'books'
              GROUP BY p.category"""
spark.conf.unset("spark.sql.adaptive.autoBroadcastJoinThreshold")
run(spark, "e2a_promotion_defaults", FILTERED)
C("spark.sql.adaptive.autoBroadcastJoinThreshold", str(1024 * 1024))
run(spark, "e2b_threshold_1mb", FILTERED)
C("spark.sql.adaptive.autoBroadcastJoinThreshold", str(4 * 1024 * 1024))
run(spark, "e2c_threshold_4mb", FILTERED)
spark.conf.unset("spark.sql.adaptive.autoBroadcastJoinThreshold")

# --- E3: skew join, whole month, broadcast disabled ---------------------------------------------------
JOIN_MONTH = """SELECT p.category, avg(CASE WHEN o.delivery_days <= o.promised_days THEN 1.0 ELSE 0.0 END) AS on_time
                FROM orders o JOIN dim_product p ON o.product_id = p.product_id
                GROUP BY p.category"""
C("spark.sql.autoBroadcastJoinThreshold", "-1")   # dim_product is already too big to broadcast; make it explicit
C("spark.sql.adaptive.skewJoin.enabled", "false")
run(spark, "e3a_skew_off", JOIN_MONTH)
C("spark.sql.adaptive.skewJoin.enabled", "true")
run(spark, "e3b_skew_on", JOIN_MONTH)

print("DONE")
