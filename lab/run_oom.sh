#!/usr/bin/env bash
# Container-OOM demo: JVM heap fits the cgroup limit, off-heap allocation does not. Prints the exit code and Docker's OOMKilled flag.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
docker rm -f lab-oom >/dev/null 2>&1
MSYS_NO_PATHCONV=1 docker run --name lab-oom --user root --memory 1g --memory-swap 1g \
  -v "$(cygpath -w "$HERE" 2>/dev/null || echo "$HERE")":/lab -w /lab \
  apache/spark:3.5.2-scala2.12-java17-python3-ubuntu /opt/spark/bin/spark-submit --master "local[4]" --driver-memory ${JAVA_HEAP:-700m} \
  --jars /lab/jars/iceberg-spark-runtime-3.5_2.12-1.6.1.jar \
  --conf spark.sql.extensions=org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions \
  --conf spark.sql.catalog.lab=org.apache.iceberg.spark.SparkCatalog --conf spark.sql.catalog.lab.type=hadoop \
  --conf spark.sql.catalog.lab.warehouse=/lab/warehouse --conf spark.memory.offHeap.enabled=true --conf spark.memory.offHeap.size=2g \
  --conf spark.ui.enabled=false /lab/exp_debug_oom.py sort > out/debug_oom_container.log 2>&1
code=$?
echo "exit=$code oomkilled=$(docker inspect lab-oom --format '{{.State.OOMKilled}}')" | tee out/debug_oom_container.txt
grep -c "OutOfMemoryError" out/debug_oom_container.log | sed 's/^/OutOfMemoryError lines in log: /' | tee -a out/debug_oom_container.txt
docker rm -f lab-oom >/dev/null 2>&1
