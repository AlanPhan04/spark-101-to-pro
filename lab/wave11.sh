#!/usr/bin/env bash
cd "$(dirname "$0")"
while [ ! -f out/wave10_done.txt ]; do sleep 10; done
touch out/wave11_marker
bash run.sh exp_catalyst.py > out/catalyst.log 2>&1
echo done > out/wave11_done.txt
