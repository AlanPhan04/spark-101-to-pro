#!/usr/bin/env bash
# Like run.sh, but installs pyarrow into the throwaway container first (the image does not ship it).
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
SCRIPT="$1"; shift || true
MSYS_NO_PATHCONV=1 docker run --rm --user root --memory 6g \
  -v "$(cygpath -w "$HERE" 2>/dev/null || echo "$HERE")":/lab -w /lab \
  apache/spark:3.5.2-scala2.12-java17-python3-ubuntu bash -c "pip install -q pyarrow pandas >/tmp/pip.log 2>&1; /opt/spark/bin/spark-submit --master local[8] --driver-memory 4g \
    --jars /lab/jars/iceberg-spark-runtime-3.5_2.12-1.6.1.jar \
    --conf spark.sql.extensions=org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions \
    --conf spark.sql.catalog.lab=org.apache.iceberg.spark.SparkCatalog --conf spark.sql.catalog.lab.type=hadoop \
    --conf spark.sql.catalog.lab.warehouse=/lab/warehouse --conf spark.default.parallelism=40 --conf spark.ui.enabled=false \
    /lab/$SCRIPT $*"
