"""The book's specimen query under default settings: plans before/after, stages, tasks."""
from labutil import OUT, plan_text, run, session

spark = session("exp-specimen")

SPECIMEN = """SELECT p.category,
       AVG(CASE WHEN o.delivery_days <= o.promised_days THEN 1.0 ELSE 0.0 END) AS on_time_rate
FROM orders o JOIN dim_product p ON o.product_id = p.product_id
WHERE o.order_ts >= TIMESTAMP '2026-03-01 00:00:00' AND o.order_ts < TIMESTAMP '2026-03-08 00:00:00'
GROUP BY p.category ORDER BY on_time_rate"""

df = spark.sql(SPECIMEN)
for mode in ("simple", "formatted", "cost"):
    with open(f"{OUT}/s1_specimen_before.{mode}.txt", "w", encoding="utf-8") as f:
        f.write(plan_text(df, mode))
run(spark, "s1_specimen_after", SPECIMEN)
print("DONE")
