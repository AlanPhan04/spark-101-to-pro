"""Chapter 14: dynamic allocation timeline. Run through run_standalone.sh <scenario>.

  shuffle  -> a shuffle job, 25 s idle, the same DataFrame again (its map stage can be skipped if the shuffle files survive)
  noshuf   -> a job with no shuffle, 25 s idle, the same job again
"""
import json
import sys
import time

from labutil import OUT, session

scn = sys.argv[1]
spark = session("dyn-" + scn)
spark.conf.set("spark.sql.adaptive.enabled", "false")
spark.conf.set("spark.sql.shuffle.partitions", "8")
sc = spark.sparkContext
marks = {}
t0 = time.time()
if scn == "shuffle":
    df = spark.sql("SELECT customer_id, count(*) AS c FROM orders GROUP BY customer_id")
    sc.setJobGroup("dyn_job1", "j1"); df.agg({"c": "sum"}).collect(); marks["job1_end"] = time.time() - t0
    time.sleep(25)
    sc.setJobGroup("dyn_job2", "j2"); df.agg({"c": "max"}).collect(); marks["job2_end"] = time.time() - t0
else:
    rdd = spark.table("orders").rdd.mapPartitions(lambda it: [sum(1 for _ in it)])
    sc.setJobGroup("dyn_job1", "j1"); rdd.collect(); marks["job1_end"] = time.time() - t0
    time.sleep(25)
    sc.setJobGroup("dyn_job2", "j2"); rdd.collect(); marks["job2_end"] = time.time() - t0
print("RESULT", json.dumps(marks))
