#!/usr/bin/env bash
cd "$(dirname "$0")"
while [ ! -f out/wave7_done.txt ]; do sleep 10; done
touch out/wave8_marker
DA="--conf spark.dynamicAllocation.enabled=true --conf spark.dynamicAllocation.minExecutors=0 --conf spark.dynamicAllocation.maxExecutors=4 --conf spark.dynamicAllocation.executorIdleTimeout=5s --conf spark.dynamicAllocation.schedulerBacklogTimeout=1s"
bash run_standalone.sh exp_dynalloc.py shuffle "$DA --conf spark.dynamicAllocation.shuffleTracking.enabled=true" > out/dyn2_shuffle.log 2>&1
bash run_standalone.sh exp_dynalloc.py shuffle "$DA --conf spark.dynamicAllocation.shuffleTracking.enabled=true --conf spark.dynamicAllocation.shuffleTracking.timeout=8s" > out/dyn2_shuffle_timeout.log 2>&1
export WORKERS=2
bash run_standalone.sh exp_debug_cluster.py straggler "--conf spark.speculation=false" > out/dbg_straggler_off.log 2>&1
bash run_standalone.sh exp_debug_cluster.py straggler "--conf spark.speculation=true --conf spark.speculation.interval=1s --conf spark.speculation.multiplier=1.5 --conf spark.speculation.quantile=0.75" > out/dbg_straggler_on.log 2>&1
bash run_standalone.sh exp_debug_cluster.py fetchfail "--conf spark.local.dir=/tmp" > out/dbg_fetch.log 2>&1
sed -i 's/^/#/' /dev/null
# container OOM, with a heap above Spark's 450 MiB minimum
JAVA_HEAP=700m bash run_oom.sh > out/debug_oom_container.run.txt 2>&1
echo done > out/wave8_done.txt
