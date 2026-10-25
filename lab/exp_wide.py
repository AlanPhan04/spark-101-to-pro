"""Ch17: the 99-column projection with and without -XX:-DontCompileHugeMethods (set through JAVA_TOOL_OPTIONS)."""
import json
import sys
import time

from labutil import OUT, session

spark = session("wide-" + sys.argv[1])
spark.conf.set("spark.sql.adaptive.enabled", "false")
res = {}
for n in (50, 99):
    cols = ", ".join(f"order_total * {i + 1} + promised_days AS c{i}" for i in range(n))
    df = spark.sql(f"SELECT {cols} FROM orders")
    t = time.time(); df.write.format("noop").mode("overwrite").save(); res[n] = round(time.time() - t, 1)
print("RESULT", json.dumps(res)); json.dump(res, open(f"{OUT}/wide_{sys.argv[1]}.json", "w"))
