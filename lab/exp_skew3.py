"""Skew handling with the split target (advisory size) below the hot partition's size."""
from labutil import run, session

spark = session("exp-skew3")
C = spark.conf.set
JOIN_MONTH = """SELECT p.category, avg(CASE WHEN o.delivery_days <= o.promised_days THEN 1.0 ELSE 0.0 END) AS on_time
                FROM orders o JOIN dim_product p ON o.product_id = p.product_id
                GROUP BY p.category"""
C("spark.sql.autoBroadcastJoinThreshold", "-1")
C("spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes", str(32 * 1024 * 1024))
C("spark.sql.adaptive.advisoryPartitionSizeInBytes", str(8 * 1024 * 1024))
C("spark.sql.adaptive.skewJoin.enabled", "false")
run(spark, "e3g_skew_off_adv8", JOIN_MONTH)
C("spark.sql.adaptive.skewJoin.enabled", "true")
run(spark, "e3h_skew_on_adv8", JOIN_MONTH)
print("DONE")
