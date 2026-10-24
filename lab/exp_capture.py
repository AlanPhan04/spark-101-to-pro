"""Extra captures for Ch6/Ch7: specimen under default settings, 'before' plan, explicit repartition, no-exchange plan."""
from labutil import OUT, plan_text, run, session

spark = session("exp-capture")
C = spark.conf.set

SPECIMEN = """SELECT p.category,
       AVG(CASE WHEN o.delivery_days <= o.promised_days THEN 1.0 ELSE 0.0 END) AS on_time_rate
FROM orders o JOIN dim_product p ON o.product_id = p.product_id
WHERE o.order_ts >= TIMESTAMP '2026-03-01 00:00:00' AND o.order_ts < TIMESTAMP '2026-03-08 00:00:00'
GROUP BY p.category ORDER BY on_time_rate"""

df = spark.sql(SPECIMEN)
with open(f"{OUT}/c1_specimen_before.simple.txt", "w", encoding="utf-8") as f:
    f.write(plan_text(df, "simple"))
with open(f"{OUT}/c1_specimen_before.plan.txt", "w", encoding="utf-8") as f:
    f.write(plan_text(df, "formatted"))
run(spark, "c1_specimen_after", SPECIMEN)

# explicit repartition(n) vs repartition(col) under AQE: does AQE honour the count?
def noop(group, d):
    spark.sparkContext.setJobGroup(group, group)
    d.write.format("noop").mode("overwrite").save()
    with open(f"{OUT}/{group}.simple.txt", "w", encoding="utf-8") as f:
        f.write(plan_text(d, "simple"))
    print("===", group)

week = spark.table("orders").where("order_ts >= TIMESTAMP '2026-03-01 00:00:00' AND order_ts < TIMESTAMP '2026-03-02 00:00:00'")
noop("c2a_repartition_200", week.repartition(200))
noop("c2b_repartition_200_by_col", week.repartition(200, "customer_id"))
noop("c2c_repartition_by_col_only", week.repartition("customer_id"))

# a query with no exchange: is it wrapped in AdaptiveSparkPlan?
d3 = spark.sql("SELECT order_id FROM orders WHERE order_total > 300 AND order_ts >= TIMESTAMP '2026-03-01 00:00:00' AND order_ts < TIMESTAMP '2026-03-02 00:00:00'")
d3.collect()
with open(f"{OUT}/c3_no_exchange.simple.txt", "w", encoding="utf-8") as f:
    f.write(plan_text(d3, "simple"))
print("DONE")
