"""Chapter 13: copy-on-write vs merge-on-read updates, MERGE predicates, metadata-only deletes, compaction, manifests, expiration, orphans."""
import json
import os
import statistics
import time

from labutil import OUT, session, show

spark = session("exp-maint")
spark.conf.set("spark.sql.adaptive.enabled", "false")
T = "TIMESTAMP"
res = {}
SUB = f"SELECT * FROM orders WHERE order_ts < {T} '2026-03-11 00:00:00'"
WH = "/lab/warehouse/db"


def dir_mb(t):
    total = 0
    for root, _, files in os.walk(f"{WH}/{t}"):
        for f in files:
            total += os.path.getsize(os.path.join(root, f))
    return round(total / 1e6, 1)


def bench(sql, n=3):
    spark.sql(sql).collect()                      # warm
    ts = []
    for _ in range(n):
        t = time.time(); spark.sql(sql).collect(); ts.append(time.time() - t)
    return round(statistics.median(ts), 2)


def last_snapshot(t):
    r = spark.sql(f"SELECT operation, summary['added-data-files'] AS af, summary['added-delete-files'] AS ad, summary['added-files-size'] AS bytes, summary['deleted-data-files'] AS df FROM lab.db.{t}.snapshots ORDER BY committed_at DESC LIMIT 1").collect()[0]
    return {k: r[k] for k in ("operation", "af", "ad", "bytes", "df")}


# --- M1: ten small updates, CoW vs MoR ------------------------------------------------------------------------------------
for t in ("t_cow", "t_mor"):
    spark.sql(f"DROP TABLE IF EXISTS {t} PURGE")
    spark.sql(f"CREATE TABLE {t} USING iceberg PARTITIONED BY (days(order_ts)) AS {SUB}")
spark.sql("ALTER TABLE t_mor SET TBLPROPERTIES ('write.update.mode'='merge-on-read','write.delete.mode'='merge-on-read','write.merge.mode'='merge-on-read')")
ids = [r[0] for r in spark.sql("SELECT order_id FROM t_cow WHERE order_ts >= TIMESTAMP '2026-03-02 00:00:00' LIMIT 50").collect()]
m1 = {}
for t in ("t_cow", "t_mor"):
    per = []
    for i in range(10):
        chunk = ",".join("'%s'" % x for x in ids[i * 5:(i + 1) * 5])
        t0 = time.time()
        spark.sql(f"UPDATE {t} SET order_total = order_total + 1 WHERE order_id IN ({chunk})")
        el = round(time.time() - t0, 2)
        per.append({"s": el, **last_snapshot(t)})
    m1[t] = per
    print(t, "mean update s", round(statistics.mean(p["s"] for p in per), 2), "mean MB", round(statistics.mean(float(p["bytes"] or 0) for p in per) / 1e6, 1), per[0])
res["M1_updates"] = m1
show(spark, "w1_files_cow", "SELECT content, count(*) AS files, round(sum(file_size_in_bytes)/1e6,1) AS mb FROM lab.db.t_cow.files GROUP BY content ORDER BY content")
show(spark, "w2_files_mor", "SELECT content, count(*) AS files, round(sum(file_size_in_bytes)/1e6,1) AS mb FROM lab.db.t_mor.files GROUP BY content ORDER BY content")
Q = "SELECT sum(order_total) FROM {t}"
res["M1_read_s"] = {"cow": bench(Q.format(t="t_cow")), "mor_before_compaction": bench(Q.format(t="t_mor"))}
spark.sql("CALL lab.system.rewrite_data_files(table => 'db.t_mor', options => map('delete-file-threshold','1'))").show(truncate=False)
show(spark, "w3_files_mor_after", "SELECT content, count(*) AS files, round(sum(file_size_in_bytes)/1e6,1) AS mb FROM lab.db.t_mor.files GROUP BY content ORDER BY content")
res["M1_read_s"]["mor_after_compaction"] = bench(Q.format(t="t_mor"))
print("read seconds", res["M1_read_s"])

# --- M2: MERGE with and without a partition predicate -----------------------------------------------------------------------
spark.sql("DROP TABLE IF EXISTS t_merge PURGE")
spark.sql(f"CREATE TABLE t_merge USING iceberg PARTITIONED BY (days(order_ts)) AS {SUB}")
spark.sql("CREATE OR REPLACE TEMP VIEW staged AS SELECT order_id, order_ts, product_id, customer_id, promised_days, delivery_days, order_total + 5 AS order_total FROM t_merge WHERE order_ts >= TIMESTAMP '2026-03-03 00:00:00' AND order_ts < TIMESTAMP '2026-03-04 00:00:00' LIMIT 1000")
spark.sql("CACHE TABLE staged")
spark.sql("SELECT count(*) FROM staged").collect()
MERGE = "MERGE INTO t_merge o USING staged s ON {on} WHEN MATCHED THEN UPDATE SET o.order_total = s.order_total"
for label, on in (("no_partition_predicate", "o.order_id = s.order_id"),
                  ("with_partition_predicate", "o.order_id = s.order_id AND o.order_ts >= TIMESTAMP '2026-03-03 00:00:00' AND o.order_ts < TIMESTAMP '2026-03-04 00:00:00'")):
    spark.sparkContext.setJobGroup(f"w_merge_{label}", f"w_merge_{label}")
    t0 = time.time()
    spark.sql(MERGE.format(on=on))
    res[f"M2_{label}"] = {"s": round(time.time() - t0, 2), **last_snapshot("t_merge")}
    print("MERGE", label, res[f"M2_{label}"])

# --- M3: metadata-only delete of a whole partition ----------------------------------------------------------------------------
spark.sparkContext.setJobGroup("w_meta_delete", "w_meta_delete")
t0 = time.time()
spark.sql("DELETE FROM t_cow WHERE order_ts >= TIMESTAMP '2026-03-09 00:00:00' AND order_ts < TIMESTAMP '2026-03-10 00:00:00'")
res["M3_meta_delete"] = {"s": round(time.time() - t0, 2), **last_snapshot("t_cow")}
print("metadata delete", res["M3_meta_delete"])

# --- M4: compaction and manifest rewrite on a table of many tiny commits ------------------------------------------------------
spark.sql("DROP TABLE IF EXISTS t_stream PURGE")
spark.sql("CREATE TABLE t_stream USING iceberg AS SELECT * FROM orders WHERE 1 = 0")
for m in range(60):
    lo = f"2026-03-01 00:{m:02d}:00" if m < 59 else "2026-03-01 00:59:00"
    hi = f"2026-03-01 00:{m + 1:02d}:00" if m < 59 else "2026-03-01 01:00:00"
    spark.sql(f"INSERT INTO t_stream SELECT * FROM orders WHERE order_ts >= {T} '{lo}' AND order_ts < {T} '{hi}'")


def stream_stats(label):
    f = spark.sql("SELECT count(*) AS files, round(avg(file_size_in_bytes)/1e3,1) AS avg_kb FROM lab.db.t_stream.files").collect()[0]
    mn = spark.sql("SELECT count(*) AS n FROM lab.db.t_stream.manifests").collect()[0][0]
    sn = spark.sql("SELECT count(*) AS n FROM lab.db.t_stream.snapshots").collect()[0][0]
    secs = bench("SELECT sum(order_total) FROM t_stream", 5)
    res[f"M4_{label}"] = {"files": f["files"], "avg_kb": f["avg_kb"], "manifests": mn, "snapshots": sn, "scan_s": secs}
    print("stream", label, res[f"M4_{label}"])


stream_stats("before")
spark.sql("CALL lab.system.rewrite_data_files(table => 'db.t_stream')").show(truncate=False)
stream_stats("after_compaction")
spark.sql("CALL lab.system.rewrite_manifests('db.t_stream')").show(truncate=False)
stream_stats("after_manifests")

# --- M5: expire snapshots and remove orphan files ------------------------------------------------------------------------------
res["M5_dir_mb_before"] = dir_mb("t_mor")
res["M5_snapshots_before"] = spark.sql("SELECT count(*) FROM lab.db.t_mor.snapshots").collect()[0][0]
res["M5_files_before"] = spark.sql("SELECT count(*) FROM lab.db.t_mor.files").collect()[0][0]
future = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time() + 3600))
r = spark.sql(f"CALL lab.system.expire_snapshots(table => 'db.t_mor', older_than => TIMESTAMP '{future}', retain_last => 1)").collect()[0]
res["M5_expire_row"] = [str(x) for x in r]
res["M5_snapshots_after"] = spark.sql("SELECT count(*) FROM lab.db.t_mor.snapshots").collect()[0][0]
res["M5_dir_mb_after_expire"] = dir_mb("t_mor")
stray = f"{WH}/t_mor/data/stray-orphan.parquet"
with open(stray, "wb") as f:
    f.write(os.urandom(5000000))                  # a file no manifest references: the debris of a failed write
res["M5_dir_mb_with_orphan"] = dir_mb("t_mor")
try:
    spark.sql(f"CALL lab.system.remove_orphan_files(table => 'db.t_mor', older_than => TIMESTAMP '{future}')").collect()
except Exception as e:
    res["M5_short_interval_error"] = str(e).strip().splitlines()[0][:160]
old = time.time() - 72 * 3600
os.utime(stray, (old, old))                       # make the stray file three days old
cutoff = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time() - 48 * 3600))
dry = spark.sql(f"CALL lab.system.remove_orphan_files(table => 'db.t_mor', older_than => TIMESTAMP '{cutoff}', dry_run => true)").collect()
res["M5_orphans_found"] = [str(x[0]).split("/")[-1] for x in dry]
spark.sql(f"CALL lab.system.remove_orphan_files(table => 'db.t_mor', older_than => TIMESTAMP '{cutoff}')").collect()
res["M5_dir_mb_after_orphans"] = dir_mb("t_mor")
res["M5_rows_ok"] = spark.sql("SELECT count(*) FROM t_mor").collect()[0][0]
print("M5", res)
json.dump(res, open(f"{OUT}/maint_results.json", "w"), indent=1, default=str)
print("DONE")
