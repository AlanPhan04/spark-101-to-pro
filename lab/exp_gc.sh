#!/usr/bin/env bash
# Ch 3: the same stage under three collectors (4 GB heap, 8 cores). GC pauses go to out/gc_<name>.log via -Xlog.
cd "$(dirname "$0")"
for gc in G1 Parallel Z; do
  export JAVA_TOOL_OPTIONS="-XX:+Use${gc}GC -Xlog:gc:file=/lab/out/gc_${gc}.log"
  DRIVER_MEM=4g CORES=8 bash run.sh exp_tune_spill.py gc_${gc} > out/tune_gc_${gc}.log 2>&1
done
unset JAVA_TOOL_OPTIONS
