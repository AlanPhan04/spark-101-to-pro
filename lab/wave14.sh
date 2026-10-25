#!/usr/bin/env bash
cd "$(dirname "$0")"
touch out/wave14_marker
bash run.sh exp_claims.py dangling > out/claims_dangling.log 2>&1
bash run.sh exp_claims.py replay first > out/claims_replay1.log 2>&1
bash run.sh exp_claims.py replay second > out/claims_replay2.log 2>&1
EXTRA_CONF="--jars /lab/jars/iceberg-spark-runtime-3.5_2.12-1.6.1.jar,/lab/jars/sqlite-jdbc.jar" bash run.sh exp_claims.py jdbccat > out/claims_jdbc.log 2>&1
# event log: plain vs compressed, same job
touch out/evlog_marker
DRIVER_MEM=1g CORES=4 bash run.sh exp_debug_skew.py > out/evlog_plain.log 2>&1
EXTRA_CONF="--conf spark.eventLog.compress=true" DRIVER_MEM=1g CORES=4 bash run.sh exp_debug_skew.py > out/evlog_compress.log 2>&1
# profiler
mkdir -p prof && curl -sL -o prof/ap.tgz https://github.com/async-profiler/async-profiler/releases/download/v3.0/async-profiler-3.0-linux-x64.tar.gz
tar -xzf prof/ap.tgz -C prof > out/prof_untar.log 2>&1
export JAVA_TOOL_OPTIONS="-agentpath:/lab/prof/async-profiler-3.0-linux-x64/lib/libasyncProfiler.so=start,event=itimer,interval=10ms,collapsed,file=/lab/out/prof.collapsed"
DRIVER_MEM=1g CORES=4 bash run.sh exp_debug_skew.py > out/prof.log 2>&1
unset JAVA_TOOL_OPTIONS
echo done > out/wave14_done.txt
