"""Chapter 14: one cell of the heap x cores grid. Same sort-heavy stage, different executor shape.

    DRIVER_MEM=2g CORES=4 ./run.sh exp_tune_spill.py <label>

Local mode makes the driver JVM the only executor, so DRIVER_MEM is the executor heap and CORES the slot count.
Eight shuffle partitions of about 4M rows each, AQE off, so the per-task execution-memory share is the only variable.
"""
import json
import sys
import time

from labutil import OUT, session

label = sys.argv[1]
spark = session("tune-" + label)
spark.conf.set("spark.sql.adaptive.enabled", "false")
spark.conf.set("spark.sql.shuffle.partitions", "8")
mm = spark.sparkContext._jsc.sc().env().memoryManager()
unified_mb = round(mm.maxOnHeapStorageMemory() / 1e6)
q = """SELECT count(*), sum(s) FROM (
         SELECT sum(order_total) OVER (PARTITION BY customer_id ORDER BY order_ts) AS s FROM orders)"""
spark.sparkContext.setJobGroup("tune_" + label, "tune_" + label)
t = time.time()
spark.sql(q).collect()
el = round(time.time() - t, 1)
rec = {"label": label, "unified_mb": unified_mb, "seconds": el}
print("RESULT", json.dumps(rec))
with open(f"{OUT}/tune_{label}.json", "w") as f:
    json.dump(rec, f)
