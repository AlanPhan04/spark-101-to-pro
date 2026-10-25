#!/usr/bin/env bash
cd "$(dirname "$0")"
rm -f out/wave3_done.txt
bash run.sh exp_dsv2b.py > out/dsv2b.log 2>&1
bash run.sh exp_tungsten.py > out/tungsten.log 2>&1
bash run.sh exp_joins.py > out/joins.log 2>&1
for h in 512m 1g 2g 4g; do DRIVER_MEM=$h bash run.sh exp_memory.py $h > out/memory_$h.log 2>&1; done
for c in lz4 snappy zstd lzf none; do bash run.sh exp_shuffle.py $c > out/shuffle_$c.log 2>&1; done
DRIVER_MEM=1g CORES=4 bash run.sh exp_debug_skew.py > out/debug_skew.log 2>&1
DRIVER_MEM=512m bash run.sh exp_debug_oom.py driver > out/debug_oom_driver.log 2>&1
DRIVER_MEM=512m CORES=8 bash run.sh exp_debug_oom.py task > out/debug_oom_task.log 2>&1
bash run_oom.sh > out/debug_oom_container.run.txt 2>&1
bash run_standalone.sh exp_debug_cluster.py straggler "--conf spark.speculation=false" > out/dbg_straggler_off.log 2>&1
bash run_standalone.sh exp_debug_cluster.py straggler "--conf spark.speculation=true --conf spark.speculation.interval=1s --conf spark.speculation.multiplier=1.5 --conf spark.speculation.quantile=0.75" > out/dbg_straggler_on.log 2>&1
bash run_standalone.sh exp_debug_cluster.py fetchfail "--conf spark.local.dir=/tmp" > out/dbg_fetch.log 2>&1
echo done > out/wave3_done.txt
