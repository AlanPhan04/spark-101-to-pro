"""Chapter 14: shuffle partitions vs task slots (40 slots). Same aggregate, AQE off, partition count varied."""
import json
import time

from labutil import OUT, session

spark = session("tune-parts")
spark.conf.set("spark.sql.adaptive.enabled", "false")
q = "SELECT count(*), sum(c) FROM (SELECT customer_id, count(*) AS c FROM orders GROUP BY customer_id)"
spark.sql(q).collect()   # warm the file cache
res = []
for p in (8, 20, 40, 41, 80, 200, 1000, 5000):
    spark.conf.set("spark.sql.shuffle.partitions", str(p))
    spark.sparkContext.setJobGroup(f"parts_{p}", f"parts_{p}")
    ts = []
    for _ in range(3):
        t = time.time(); spark.sql(q).collect(); ts.append(time.time() - t)
    res.append({"partitions": p, "seconds": round(sorted(ts)[1], 2)})
    print(res[-1])
json.dump(res, open(f"{OUT}/tune_parts.json", "w"), indent=1)
