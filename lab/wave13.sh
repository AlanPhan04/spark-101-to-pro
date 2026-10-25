#!/usr/bin/env bash
cd "$(dirname "$0")"
touch out/wave13_marker
for m in bucketskew rangerebal dangling; do bash run.sh exp_claims.py $m > out/claims_$m.log 2>&1; done
EXTRA_CONF="--conf spark.memory.offHeap.enabled=true --conf spark.memory.offHeap.size=1g" bash run.sh exp_claims.py offheapcache > out/claims_offheap.log 2>&1
bash run.sh exp_claims.py replay first > out/claims_replay1.log 2>&1
bash run.sh exp_claims.py replay second > out/claims_replay2.log 2>&1
EXTRA_CONF="--jars /lab/jars/sqlite-jdbc.jar" bash run.sh exp_claims.py jdbccat > out/claims_jdbc.log 2>&1
for v in default nohuge; do
  if [ $v = nohuge ]; then export JAVA_TOOL_OPTIONS="-XX:-DontCompileHugeMethods"; else unset JAVA_TOOL_OPTIONS; fi
  bash run.sh exp_wide.py $v > out/wide_$v.log 2>&1
done
unset JAVA_TOOL_OPTIONS
# event log size: rolling+compressed vs plain, same job
EXTRA_CONF="--conf spark.eventLog.compress=true" DRIVER_MEM=1g CORES=4 bash run.sh exp_debug_skew.py > out/evlog_compress.log 2>&1
# profiler
export JAVA_TOOL_OPTIONS="-agentpath:/lab/prof/async-profiler-3.0-linux-x64/lib/libasyncProfiler.so=start,event=itimer,interval=10ms,collapsed,file=/lab/out/prof.collapsed"
DRIVER_MEM=1g CORES=4 bash run.sh exp_debug_skew.py > out/prof.log 2>&1
unset JAVA_TOOL_OPTIONS
# cold vs warm AQE, standalone, dynamic allocation
DA="--conf spark.dynamicAllocation.enabled=true --conf spark.dynamicAllocation.minExecutors=0 --conf spark.dynamicAllocation.maxExecutors=4 --conf spark.dynamicAllocation.shuffleTracking.enabled=true --conf spark.dynamicAllocation.executorIdleTimeout=60s"
bash run_standalone.sh exp_cold.py x "$DA" > out/cold.log 2>&1
echo done > out/wave13_done.txt
