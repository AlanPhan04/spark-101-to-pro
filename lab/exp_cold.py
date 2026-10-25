"""Ch6: AQE coalescing target depends on the cores registered NOW. Cold application (no executors yet) vs warm."""
import json
import time

from labutil import OUT, session

spark = session("cold")
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.shuffle.partitions", "200")
sc = spark.sparkContext
res = {"default_parallelism_at_start": sc.defaultParallelism}
q = "SELECT customer_id, count(*) c FROM orders GROUP BY customer_id"
sc.setJobGroup("cold_first", "c")
spark.sql(q).write.format("noop").mode("overwrite").save()
time.sleep(8)
res["default_parallelism_warm"] = sc.defaultParallelism
sc.setJobGroup("cold_second", "w")
spark.sql(q).write.format("noop").mode("overwrite").save()
print("RESULT", json.dumps(res)); json.dump(res, open(f"{OUT}/cold.json", "w"))
