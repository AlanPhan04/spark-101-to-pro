#!/usr/bin/env bash
# Run a PySpark script against the lab Iceberg warehouse in a Spark 3.5.2 / JDK 17 container.
#   ./run.sh gen_data.py 30000000
#   ./run.sh exp_aqe.py
# Local-mode stand-in for the reference stack (no HMS / GCS / GKE). spark.default.parallelism is
# pinned to 40 so AQE's parallelism term matches the book's 40-slot reference cluster.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
SCRIPT="$1"; shift || true
mkdir -p "$HERE/out" "$HERE/events" "$HERE/warehouse"
MSYS_NO_PATHCONV=1 docker run --rm --user root \
  --memory 6g \
  -v "$(cygpath -w "$HERE" 2>/dev/null || echo "$HERE")":/lab \
  -w /lab \
  apache/spark:3.5.2-scala2.12-java17-python3-ubuntu \
  /opt/spark/bin/spark-submit \
    --master "local[${CORES:-8}]" \
    --driver-memory "${DRIVER_MEM:-4g}" \
    --jars /lab/jars/iceberg-spark-runtime-3.5_2.12-1.6.1.jar \
    --conf spark.sql.extensions=org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions \
    --conf spark.sql.catalog.lab=org.apache.iceberg.spark.SparkCatalog \
    --conf spark.sql.catalog.lab.type=hadoop \
    --conf spark.sql.catalog.lab.warehouse=/lab/warehouse \
    --conf spark.default.parallelism=40 \
    --conf spark.eventLog.enabled=true \
    --conf spark.eventLog.dir=/lab/events \
    --conf spark.ui.enabled=false \
    --conf spark.local.dir=/tmp/spark-local \
    ${EXTRA_CONF:-} \
    "/lab/$SCRIPT" "$@"
