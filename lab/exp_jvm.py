"""Chapter 3: JIT warm-up. The same query eight times in a fresh JVM."""
import json
import time

from labutil import OUT, session

spark = session("jvm-warmup")
spark.conf.set("spark.sql.adaptive.enabled", "false")
q = "SELECT sum(order_total * 1.07 + promised_days) FROM orders WHERE order_total > 10"
res = []
for i in range(8):
    t = time.time(); spark.sql(q).collect(); res.append(round(time.time() - t, 2))
print("RESULT", res)
json.dump(res, open(f"{OUT}/jvm_warmup.json", "w"))
