#!/usr/bin/env bash
# One container with a standalone master + one 4-core worker, then spark-submit with dynamic allocation.
#   ./run_standalone.sh exp_dynalloc.py shuffle "<extra --conf flags>"
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
SCRIPT="$1"; ARG="$2"; EXTRA="${3:-}"
MSYS_NO_PATHCONV=1 docker run --rm --user root --memory 6g \
  -v "$(cygpath -w "$HERE" 2>/dev/null || echo "$HERE")":/lab -w /lab \
  apache/spark:3.5.2-scala2.12-java17-python3-ubuntu bash -c "
    export SPARK_LOCAL_IP=127.0.0.1 SPARK_MASTER_HOST=127.0.0.1
    /opt/spark/sbin/start-master.sh >/tmp/master.log 2>&1
    if [ \"${WORKERS:-1}\" = 2 ]; then
      # two workers under two different host names, so Spark sees two hosts (speculative copies avoid the original's host)
      /opt/spark/bin/spark-class org.apache.spark.deploy.worker.Worker spark://127.0.0.1:7077 --host 127.0.0.1 --port 7101 --webui-port 8101 -c 2 -m 2g >/tmp/w1.log 2>&1 &
      /opt/spark/bin/spark-class org.apache.spark.deploy.worker.Worker spark://127.0.0.1:7077 --host localhost --port 7102 --webui-port 8102 -c 2 -m 2g >/tmp/w2.log 2>&1 &
    else
      /opt/spark/sbin/start-worker.sh spark://127.0.0.1:7077 -c 4 -m 4g >/tmp/worker.log 2>&1
    fi
    sleep 5
    /opt/spark/bin/spark-submit --master spark://127.0.0.1:7077 --driver-memory 1g \
      --jars /lab/jars/iceberg-spark-runtime-3.5_2.12-1.6.1.jar \
      --conf spark.sql.extensions=org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions \
      --conf spark.sql.catalog.lab=org.apache.iceberg.spark.SparkCatalog \
      --conf spark.sql.catalog.lab.type=hadoop --conf spark.sql.catalog.lab.warehouse=/lab/warehouse \
      --conf spark.eventLog.enabled=true --conf spark.eventLog.dir=/lab/events --conf spark.ui.enabled=false \
      --conf spark.executor.cores=${EXEC_CORES:-1} --conf spark.executor.memory=1g \
      $EXTRA /lab/$SCRIPT $ARG"
