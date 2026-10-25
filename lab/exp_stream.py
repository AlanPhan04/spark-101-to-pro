"""Chapter 16 streaming experiments on the lab (rate source -> Iceberg sink or noop).

  cadence <trigger_s> <duration_s>   micro-batch cadence vs commits, files, file size
  killrun <duration_s>               long-running writer to be killed from outside (docker kill), checkpoint kept
  check                              duplicates + snapshot summary of the killed/restarted table
  state <watermark|none> <duration_s>  state-store rows over time
  modes                              rows emitted per batch under append / update / complete
  availnow                           Trigger.AvailableNow over a growing directory of files
"""
import json
import os
import shutil
import sys
import time

from pyspark.sql import functions as F

from labutil import OUT, session

mode = sys.argv[1]
spark = session("stream-" + mode)
spark.conf.set("spark.sql.shuffle.partitions", "4")
spark.conf.set("spark.sql.adaptive.enabled", "false")
CK = "/lab/ckpt"


def src(rows_per_s=20000, parts=4):
    return (spark.readStream.format("rate").option("rowsPerSecond", rows_per_s).option("numPartitions", parts).load()
            .select(F.col("value").alias("seq"), F.col("timestamp").alias("order_ts"),
                    F.concat(F.lit("c"), (F.col("value") % 1000).cast("string")).alias("customer_id"),
                    (F.col("value") % 97 + 0.5).alias("order_total")))


def make_table(name):
    spark.sql(f"DROP TABLE IF EXISTS {name} PURGE")
    spark.sql(f"CREATE TABLE {name} (seq BIGINT, order_ts TIMESTAMP, customer_id STRING, order_total DOUBLE) USING iceberg PARTITIONED BY (days(order_ts))")


def table_stats(name):
    sn = spark.sql(f"SELECT count(*) n FROM lab.db.{name}.snapshots").collect()[0][0]
    f = spark.sql(f"SELECT count(*) n, round(avg(file_size_in_bytes)/1e3,1) kb FROM lab.db.{name}.files").collect()[0]
    m = spark.sql(f"SELECT count(*) n FROM lab.db.{name}.manifests").collect()[0][0]
    return {"snapshots": sn, "files": f["n"], "avg_file_kb": f["kb"], "manifests": m}


if mode == "cadence":
    trig, dur = int(sys.argv[2]), int(sys.argv[3])
    name = f"s_cad_{trig}"
    make_table(name)
    shutil.rmtree(f"{CK}/{name}", ignore_errors=True)
    q = (src().writeStream.format("iceberg").outputMode("append").trigger(processingTime=f"{trig} seconds")
         .option("checkpointLocation", f"{CK}/{name}").toTable(f"lab.db.{name}"))
    time.sleep(dur); q.stop()
    rec = {"trigger_s": trig, "duration_s": dur, **table_stats(name)}
    rec["rows"] = spark.sql(f"SELECT count(*) FROM {name}").collect()[0][0]
    rec["summary_keys"] = spark.sql(f"SELECT summary FROM lab.db.{name}.snapshots ORDER BY committed_at DESC LIMIT 1").collect()[0][0]
    print("RESULT", json.dumps(rec, default=str))
    json.dump(rec, open(f"{OUT}/stream_cad_{trig}.json", "w"), indent=1, default=str)

elif mode == "killrun":
    dur = int(sys.argv[2])
    if not os.path.exists(f"{CK}/s_kill"):
        make_table("s_kill")
    q = (src(2000, 2).writeStream.format("iceberg").outputMode("append").trigger(processingTime="3 seconds")
         .option("checkpointLocation", f"{CK}/s_kill").toTable("lab.db.s_kill"))
    time.sleep(dur); q.stop()
    print("RESULT", json.dumps(table_stats("s_kill")))

elif mode == "check":
    rows = spark.sql("SELECT count(*) n, count(distinct seq) d, min(seq) lo, max(seq) hi FROM s_kill").collect()[0]
    snaps = spark.sql("SELECT snapshot_id, summary['spark.sql.streaming.epochId'] ep, summary['spark.sql.streaming.queryId'] qid, summary['added-records'] recs FROM lab.db.s_kill.snapshots ORDER BY committed_at").collect()
    out = {"rows": rows["n"], "distinct": rows["d"], "lo": rows["lo"], "hi": rows["hi"],
           "snapshots": [{"epoch": s["ep"], "query": (s["qid"] or "")[:8], "records": s["recs"]} for s in snaps]}
    print("RESULT", json.dumps(out))
    json.dump(out, open(f"{OUT}/stream_kill_check.json", "w"), indent=1)

elif mode == "state":
    wm, dur = sys.argv[2], int(sys.argv[3])
    s = src(2000, 2)
    if wm == "watermark":
        s = s.withWatermark("order_ts", "10 seconds")
    agg = s.groupBy(F.window("order_ts", "5 seconds"), "customer_id").agg(F.count("*").alias("c"), F.sum("order_total").alias("s"))
    shutil.rmtree(f"{CK}/state_{wm}", ignore_errors=True)
    q = (agg.writeStream.format("noop").outputMode("update").trigger(processingTime="5 seconds")
         .option("checkpointLocation", f"{CK}/state_{wm}").start())
    series = []
    t0 = time.time()
    seen = set()
    while time.time() - t0 < dur:
        time.sleep(2)
        for p in q.recentProgress:
            if p["batchId"] in seen or not p.get("stateOperators"):
                continue
            seen.add(p["batchId"])
            so = p["stateOperators"][0]
            series.append({"t": round(time.time() - t0), "batch": p["batchId"], "state_rows": so["numRowsTotal"], "state_bytes": so["memoryUsedBytes"],
                           "evicted": so.get("numRowsRemoved", 0), "input_rows": p["numInputRows"], "batch_ms": p["batchDuration"] if "batchDuration" in p else p["durationMs"]["triggerExecution"]})
    q.stop()
    json.dump(series, open(f"{OUT}/stream_state_{wm}.json", "w"), indent=1)
    print("RESULT", wm, series[-1] if series else None, len(series))

elif mode == "modes":
    res = {}
    for om in ("append", "update", "complete"):
        counts = []
        s = src(1000, 2).withWatermark("order_ts", "5 seconds")
        agg = s.groupBy(F.window("order_ts", "5 seconds"), (F.col("seq") % 3).alias("k")).count()
        shutil.rmtree(f"{CK}/modes_{om}", ignore_errors=True)
        try:
            q = (agg.writeStream.outputMode(om).foreachBatch(lambda df, i, c=counts: c.append(df.count()))
                 .trigger(processingTime="3 seconds").option("checkpointLocation", f"{CK}/modes_{om}").start())
            time.sleep(40); q.stop()
            res[om] = counts
        except Exception as e:
            res[om] = "error: " + str(e).strip().splitlines()[0][:160]
        print(om, res[om])
    json.dump(res, open(f"{OUT}/stream_modes.json", "w"), indent=1)

elif mode == "availnow":
    d = "/lab/stream_in"
    shutil.rmtree(d, ignore_errors=True); shutil.rmtree(f"{CK}/avail", ignore_errors=True); os.makedirs(d)
    make_table("s_avail")
    res = []

    def land(n, start):
        spark.range(start, start + n).selectExpr("id AS seq", "current_timestamp() AS order_ts", "concat('c', id % 10) AS customer_id", "CAST(id AS DOUBLE) AS order_total").write.mode("append").parquet(d)

    sch = "seq BIGINT, order_ts TIMESTAMP, customer_id STRING, order_total DOUBLE"
    for run, (n, start) in enumerate([(100000, 0), (0, 0), (50000, 100000)]):
        if n:
            land(n, start)
        t = time.time()
        q = (spark.readStream.schema(sch).parquet(d).writeStream.format("iceberg").trigger(availableNow=True)
             .option("checkpointLocation", f"{CK}/avail").toTable("lab.db.s_avail"))
        q.awaitTermination()
        rows = spark.sql("SELECT count(*) FROM s_avail").collect()[0][0]
        sn = spark.sql("SELECT count(*) FROM lab.db.s_avail.snapshots").collect()[0][0]
        res.append({"run": run + 1, "landed_rows": n, "seconds": round(time.time() - t, 1), "table_rows": rows, "snapshots": sn})
        print(res[-1])
    json.dump(res, open(f"{OUT}/stream_avail.json", "w"), indent=1)

if mode == "statebig":
    prov, dur = sys.argv[2], int(sys.argv[3])
    if prov == "rocksdb":
        spark.conf.set("spark.sql.streaming.stateStore.providerClass", "org.apache.spark.sql.execution.streaming.state.RocksDBStateStoreProvider")
    s = (spark.readStream.format("rate").option("rowsPerSecond", 20000).option("numPartitions", 2).load()
         .select(F.col("timestamp").alias("order_ts"), (F.col("value") % 40000).cast("string").alias("customer_id")))
    agg = s.groupBy(F.window("order_ts", "10 seconds"), "customer_id").count()
    shutil.rmtree(f"{CK}/big_{prov}", ignore_errors=True)
    q = (agg.writeStream.format("noop").outputMode("update").trigger(processingTime="5 seconds")
         .option("checkpointLocation", f"{CK}/big_{prov}").start())
    series, seen, t0 = [], set(), time.time()
    while time.time() - t0 < dur:
        time.sleep(2)
        for p in q.recentProgress:
            if p["batchId"] in seen or not p.get("stateOperators"):
                continue
            seen.add(p["batchId"]); so = p["stateOperators"][0]
            series.append({"t": round(time.time() - t0), "state_rows": so["numRowsTotal"], "state_bytes": so["memoryUsedBytes"], "batch_ms": p["durationMs"]["triggerExecution"],
                           "commit_ms": so.get("commitTimeMs", None)})
    q.stop()
    json.dump(series, open(f"{OUT}/stream_big_{prov}.json", "w"), indent=1)
    print("RESULT", prov, series[-1] if series else None)
