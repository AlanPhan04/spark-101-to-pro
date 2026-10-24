# Lab: a local Spark 3.5.2 + Iceberg stand-in for the book

Everything the book prints as captured output (plans, task counts, byte counts) comes from here.
Local mode, one Docker container, JDK 17, Iceberg 1.6.1, file-based Iceberg catalog. No HMS, GCS, or GKE.

```bash
# one time: the Iceberg runtime jar (not committed)
mkdir -p jars && curl -L -o jars/iceberg-spark-runtime-3.5_2.12-1.6.1.jar \
  https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-spark-runtime-3.5_2.12/1.6.1/iceberg-spark-runtime-3.5_2.12-1.6.1.jar

./run.sh gen_data.py 30000000   # orders star schema -> warehouse/ (about 1.2 GB)
./run.sh exp_aqe.py             # Ch 6: coalescing, broadcast promotion, skew (defaults)
./run.sh exp_aqe2.py            # Ch 6: advisory size, thresholds, skew with scaled thresholds
./run.sh exp_skew3.py           # Ch 6: skew that actually fires (advisory 8 MB, floor 32 MB)
./run.sh exp_pruning.py         # Ch 7: pruning variants, DPP, coalesce/repartition, bucketed join
./run.sh exp_dpp2.py            # Ch 7: DPP on an identity-partitioned fact table
./run.sh exp_capture.py         # specimen plans, explicit repartition, no-exchange plan
python events_summary.py > out/summary_all.txt   # task counts / durations / bytes per experiment
```

- Plans are written to `out/<experiment>.plan.txt` (`EXPLAIN FORMATTED`, after execution) and
  `out/<experiment>.simple.txt` (`EXPLAIN`, shows `isFinalPlan=`).
- `spark.default.parallelism` is pinned to 40 so AQE's coalescing arithmetic matches the book's 40-slot cluster.
- `events/` (Spark event logs) and `warehouse/` are git-ignored; regenerate them.
- The container is capped at 6 GB; data volume is sized for a 16 GB laptop.
