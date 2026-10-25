"""Chapter 14: shuffle partitions vs slots when the reduce stage dominates (window over 30M rows). 8 slots (CORES=8), AQE off."""
import json
import time

from labutil import OUT, session

spark = session("tune-parts2")
spark.conf.set("spark.sql.adaptive.enabled", "false")
q = "SELECT count(*), sum(s) FROM (SELECT sum(order_total) OVER (PARTITION BY customer_id ORDER BY order_ts) AS s FROM orders)"
res = []
for p in (2, 4, 8, 16, 40, 200, 1000, 5000):
    spark.conf.set("spark.sql.shuffle.partitions", str(p))
    spark.sparkContext.setJobGroup(f"parts2_{p}", "p")
    t = time.time(); spark.sql(q).collect(); res.append({"partitions": p, "seconds": round(time.time() - t, 1)})
    print(res[-1])
json.dump(res, open(f"{OUT}/tune_parts2.json", "w"), indent=1)
