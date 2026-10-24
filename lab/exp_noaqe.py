"""The specimen with AQE off: the classic physical plan with whole-stage codegen markers."""
from labutil import OUT, plan_text, run, session

spark = session("exp-noaqe")
spark.conf.set("spark.sql.adaptive.enabled", "false")
SPECIMEN = """SELECT p.category,
       AVG(CASE WHEN o.delivery_days <= o.promised_days THEN 1.0 ELSE 0.0 END) AS on_time_rate
FROM orders o JOIN dim_product p ON o.product_id = p.product_id
WHERE o.order_ts >= TIMESTAMP '2026-03-01 00:00:00' AND o.order_ts < TIMESTAMP '2026-03-08 00:00:00'
GROUP BY p.category ORDER BY on_time_rate"""
run(spark, "n1_specimen_aqe_off", SPECIMEN)
print("DONE")
