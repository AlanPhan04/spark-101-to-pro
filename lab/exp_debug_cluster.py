"""Chapter 15/18 on a standalone cluster (run_standalone.sh): speculation and fetch failures.

  straggler : 8 tasks, partition 3's first attempt sleeps 40 s; run with and without spark.speculation
  fetchfail : shuffle job, then delete one executor's shuffle files, then rerun the job
"""
import glob
import os
import sys
import time

from labutil import session

scn = sys.argv[1]
spark = session("dbgc-" + scn)
spark.conf.set("spark.sql.adaptive.enabled", "false")
sc = spark.sparkContext
t0 = time.time()
if scn == "straggler":
    def work(idx, it):
        from pyspark import TaskContext
        ctx = TaskContext.get()
        time.sleep(40 if (idx == 3 and ctx.attemptNumber() == 0) else 3)
        yield idx
    sc.setJobGroup("dbgc_straggler", "straggler")
    sc.parallelize(range(8), 8).mapPartitionsWithIndex(work).collect()
    print("RESULT seconds", round(time.time() - t0, 1))
else:
    spark.conf.set("spark.sql.shuffle.partitions", "8")
    df = spark.sql("SELECT sum(c) FROM (SELECT customer_id, count(*) c FROM orders GROUP BY customer_id)")
    sc.setJobGroup("dbgc_fetch1", "first")
    df.collect()
    victims = sorted(glob.glob("/tmp/spark-*/executor-*/blockmgr-*/**/shuffle_*", recursive=True))
    byexec = {}
    for f in victims:
        byexec.setdefault(f.split("/")[3], []).append(f)
    print("shuffle files per executor:", {k[-8:]: len(v) for k, v in byexec.items()})
    gone = max(byexec, key=lambda k: len(byexec[k]))
    for f in byexec[gone]:
        os.remove(f)
    print("deleted", len(byexec[gone]), "shuffle files of", gone, "of", len(byexec), "executors")
    sc.setJobGroup("dbgc_fetch2", "second")
    t1 = time.time()
    df.collect()
    print("RESULT second run seconds", round(time.time() - t1, 1))
