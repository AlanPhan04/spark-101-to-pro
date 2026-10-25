"""Chapter 10: concurrent writers racing for the catalog pointer; how often a commit retries or fails."""
import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor

from labutil import OUT, enable_scan_reports, session, show

spark = session("exp-commits")
enable_scan_reports(spark)      # LoggingMetricsReporter prints a CommitReport (with attempts=) per commit
WRITERS, PER_WRITER = 12, 4
res = {}


def writer(w, table):
    ok, failed = 0, 0
    for s in range(PER_WRITER):
        try:
            spark.sql(f"INSERT INTO {table} SELECT id, {w} AS writer, {s} AS seq FROM range(20000)")
            ok += 1
        except Exception as e:   # CommitFailedException surfaces as a Py4J error
            failed += 1
    return ok, failed


for retries in (4, 0):
    table = f"t_race_r{retries}"
    spark.sql(f"DROP TABLE IF EXISTS {table}")
    spark.sql(f"CREATE TABLE {table} (id bigint, writer int, seq int) USING iceberg "
              f"TBLPROPERTIES ('commit.retry.num-retries'='{retries}', 'commit.retry.min-wait-ms'='20')")
    print(f"### setting retries={retries}")
    t0 = time.time()
    with ThreadPoolExecutor(WRITERS) as ex:
        out = list(ex.map(lambda w: writer(w, table), range(WRITERS)))
    wall = round(time.time() - t0, 1)
    ok = sum(o for o, _ in out)
    failed = sum(f for _, f in out)
    snaps = spark.sql(f"SELECT count(*) FROM lab.db.{table}.snapshots").collect()[0][0]
    rows = spark.sql(f"SELECT count(*) FROM {table}").collect()[0][0]
    res[f"retries_{retries}"] = {"attempted": WRITERS * PER_WRITER, "succeeded": ok, "failed": failed, "snapshots": snaps,
                                 "rows": rows, "expected_rows": ok * 20000, "wall_s": wall}
    print("RESULT", retries, res[f"retries_{retries}"])
    show(spark, f"k_snapshots_r{retries}", f"SELECT committed_at, snapshot_id, parent_id, operation FROM lab.db.{table}.snapshots ORDER BY committed_at", n=60, truncate=30)

json.dump(res, open(f"{OUT}/commits_results.json", "w"), indent=1)
print("DONE")
