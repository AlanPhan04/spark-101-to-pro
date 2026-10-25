#!/usr/bin/env bash
cd "$(dirname "$0")"
while [ ! -f out/wave9_done.txt ]; do sleep 10; done
DRIVER_MEM=2g bash run.sh exp_stream.py statebig default 120 > out/stream_big_default.log 2>&1
DRIVER_MEM=2g bash run.sh exp_stream.py statebig rocksdb 120 > out/stream_big_rocksdb.log 2>&1
echo done > out/wave10_done.txt
