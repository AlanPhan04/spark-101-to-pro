"""Chapter 6 experiments, round 2: make the advisory size bind, skew with lab-scaled thresholds, threshold edge cases."""
from labutil import run, session

spark = session("exp-aqe2")
C = spark.conf.set

BIG = """SELECT count(*) FROM (SELECT customer_id, product_id, count(*) AS n FROM orders GROUP BY customer_id, product_id)"""
C("spark.sql.shuffle.partitions", "2000")
C("spark.sql.adaptive.coalescePartitions.parallelismFirst", "true")
C("spark.sql.adaptive.advisoryPartitionSizeInBytes", str(4 * 1024 * 1024))
run(spark, "e1f_big_pf_true_adv4", BIG)
C("spark.sql.adaptive.coalescePartitions.parallelismFirst", "false")
C("spark.sql.adaptive.advisoryPartitionSizeInBytes", str(64 * 1024 * 1024))
run(spark, "e1g_big_pf_false_adv64", BIG)
spark.conf.unset("spark.sql.adaptive.advisoryPartitionSizeInBytes")
C("spark.sql.adaptive.coalescePartitions.parallelismFirst", "true")
C("spark.sql.shuffle.partitions", "200")

JOIN_WEEK = """SELECT p.category, count(*) AS orders
               FROM orders o JOIN dim_product p ON o.product_id = p.product_id
               WHERE o.order_ts >= TIMESTAMP '2026-03-01 00:00:00' AND o.order_ts < TIMESTAMP '2026-03-08 00:00:00'
               GROUP BY p.category"""
C("spark.sql.autoBroadcastJoinThreshold", "-1")
C("spark.sql.adaptive.autoBroadcastJoinThreshold", str(1 * 1024 * 1024))
run(spark, "e2c_threshold_1mb", JOIN_WEEK)
C("spark.sql.adaptive.autoBroadcastJoinThreshold", str(4 * 1024 * 1024))
run(spark, "e2d_threshold_4mb", JOIN_WEEK)
spark.conf.unset("spark.sql.adaptive.autoBroadcastJoinThreshold")

JOIN_MONTH = """SELECT p.category, avg(CASE WHEN o.delivery_days <= o.promised_days THEN 1.0 ELSE 0.0 END) AS on_time
                FROM orders o JOIN dim_product p ON o.product_id = p.product_id
                GROUP BY p.category"""
C("spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes", str(32 * 1024 * 1024))
C("spark.sql.adaptive.skewJoin.enabled", "false")
run(spark, "e3c_skew_off_thr32", JOIN_MONTH)
C("spark.sql.adaptive.skewJoin.enabled", "true")
run(spark, "e3d_skew_on_thr32", JOIN_MONTH)
print("DONE")
