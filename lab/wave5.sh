#!/usr/bin/env bash
cd "$(dirname "$0")"
while [ ! -f out/wave4_done.txt ]; do sleep 10; done
bash run.sh exp_joins.py > out/joins.log 2>&1
echo done > out/wave5_done.txt
