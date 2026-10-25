"""Chapter 2: what each optimizer rule is worth. Same query, one rule excluded at a time; bytes read, rows out of the scan, seconds."""
import json
import statistics
import time

from labutil import OUT, plan_text, session

spark = session("catalyst")
spark.conf.set("spark.sql.adaptive.enabled", "false")
spark.conf.set("spark.sql.shuffle.partitions", "40")
Q = """SELECT p.category, sum(o.order_total * (1 + 0.05 + 0.02)) AS gross
       FROM orders o JOIN dim_product p ON o.product_id = p.product_id
       WHERE o.order_ts >= TIMESTAMP '2026-03-05 00:00:00' AND o.order_ts < TIMESTAMP '2026-03-08 00:00:00' AND 1 = 1
       GROUP BY p.category"""
text = []
df = spark.sql(Q)
text.append(plan_text(df, "extended"))
open(f"{OUT}/cat_extended.txt", "w").write(text[0])
PKG = "org.apache.spark.sql.catalyst.optimizer."
variants = [("all rules", ""),
            ("without ColumnPruning", PKG + "ColumnPruning"),
            ("without PushDownPredicates", PKG + "PushDownPredicates"),
            ("without ConstantFolding", PKG + "ConstantFolding"),
            ("without V2 scan pushdown", "org.apache.spark.sql.execution.datasources.v2.V2ScanRelationPushDown"),
            ("without all four", ",".join([PKG + "ColumnPruning", PKG + "PushDownPredicates", PKG + "ConstantFolding", "org.apache.spark.sql.execution.datasources.v2.V2ScanRelationPushDown"]))]
spark.sql(Q).collect(); spark.sql(Q).collect()   # warm-up so the first variant is not charged for the JIT
res = []
for i, (name, ex) in enumerate(variants):
    spark.conf.set("spark.sql.optimizer.excludedRules", ex)
    group = f"cat_{i}"
    spark.sparkContext.setJobGroup(group, group)
    ts = []
    for _ in range(3):
        t = time.time(); r = spark.sql(Q).collect(); ts.append(time.time() - t)
    p = plan_text(spark.sql(Q), "formatted")
    res.append({"variant": name, "group": group, "seconds": round(statistics.median(ts), 2), "rows": len(r)})
    print(res[-1])
spark.conf.set("spark.sql.optimizer.excludedRules", "")
json.dump(res, open(f"{OUT}/catalyst_results.json", "w"), indent=1)
