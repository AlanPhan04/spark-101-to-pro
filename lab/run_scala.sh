#!/usr/bin/env bash
# spark-shell script in the lab container: ./run_scala.sh ser.scala
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
MSYS_NO_PATHCONV=1 docker run --rm --user root --memory 4g -v "$(cygpath -w "$HERE" 2>/dev/null || echo "$HERE")":/lab -w /lab \
  apache/spark:3.5.2-scala2.12-java17-python3-ubuntu /opt/spark/bin/spark-shell --master local[2] --conf spark.ui.enabled=false -i "/lab/$1" 2>&1 | grep -E "RESULT|error" 
