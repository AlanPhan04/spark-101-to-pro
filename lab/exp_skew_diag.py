"""Diagnose why AQE skew handling did not fire on the lab data."""
from labutil import run, session

spark = session("exp-skew-diag")
C = spark.conf.set
JOIN_MONTH = """SELECT p.category, avg(CASE WHEN o.delivery_days <= o.promised_days THEN 1.0 ELSE 0.0 END) AS on_time
                FROM orders o JOIN dim_product p ON o.product_id = p.product_id
                GROUP BY p.category"""
C("spark.sql.autoBroadcastJoinThreshold", "-1")
C("spark.sql.adaptive.skewJoin.enabled", "true")
C("spark.sql.adaptive.skewJoin.skewedPartitionFactor", "2")
C("spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes", str(1 * 1024 * 1024))
C("spark.sql.adaptive.coalescePartitions.enabled", "false")
run(spark, "e3e_diag_nocoalesce_lowthr", JOIN_MONTH)
C("spark.sql.adaptive.coalescePartitions.enabled", "true")
run(spark, "e3f_diag_coalesce_lowthr", JOIN_MONTH)
print("DONE")
