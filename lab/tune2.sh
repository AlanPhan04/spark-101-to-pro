#!/usr/bin/env bash
cd "$(dirname "$0")"
rm -f out/tune2_done.txt
bash run.sh exp_tune_parts.py > out/tune_parts.log 2>&1
EXTRA_CONF="--properties-file /lab/props.conf" bash run.sh exp_tune_conf.py plain 2>&1 | grep RESULT > out/tune_conf_1.txt
EXTRA_CONF="--properties-file /lab/props.conf --conf spark.sql.shuffle.partitions=222 --conf spark.executor.memory=5g" bash run.sh exp_tune_conf.py plain 2>&1 | grep RESULT > out/tune_conf_2.txt
EXTRA_CONF="--properties-file /lab/props.conf --conf spark.sql.shuffle.partitions=222 --conf spark.executor.memory=5g" bash run.sh exp_tune_conf.py code 2>&1 | grep RESULT > out/tune_conf_3.txt
DA="--conf spark.dynamicAllocation.enabled=true --conf spark.dynamicAllocation.minExecutors=0 --conf spark.dynamicAllocation.maxExecutors=4 --conf spark.dynamicAllocation.executorIdleTimeout=5s --conf spark.dynamicAllocation.schedulerBacklogTimeout=1s"
bash run_standalone.sh exp_dynalloc.py shuffle "$DA --conf spark.dynamicAllocation.shuffleTracking.enabled=true" > out/dyn_shuffle.log 2>&1
bash run_standalone.sh exp_dynalloc.py noshuf "$DA --conf spark.dynamicAllocation.shuffleTracking.enabled=true" > out/dyn_noshuf.log 2>&1
bash run_standalone.sh exp_dynalloc.py shuffle "$DA --conf spark.dynamicAllocation.shuffleTracking.enabled=true --conf spark.dynamicAllocation.shuffleTracking.timeout=8s" > out/dyn_shuffle_timeout.log 2>&1
bash run_standalone.sh exp_dynalloc.py shuffle "$DA --conf spark.dynamicAllocation.shuffleTracking.enabled=false" > out/dyn_notracking.log 2>&1
echo done > out/tune2_done.txt
