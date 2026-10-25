#!/usr/bin/env bash
cd "$(dirname "$0")"
while [ ! -f out/wave6_done.txt ]; do sleep 10; done
touch out/wave7_marker
for c in lz4 snappy zstd lzf; do EXTRA_CONF="--conf spark.io.compression.codec=$c" bash run.sh exp_shuffle.py $c > out/shuffle_$c.log 2>&1; done
EXTRA_CONF="--conf spark.shuffle.compress=false" bash run.sh exp_shuffle.py none > out/shuffle_none.log 2>&1
echo done > out/wave7_done.txt
