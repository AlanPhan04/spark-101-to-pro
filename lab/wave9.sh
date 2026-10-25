#!/usr/bin/env bash
cd "$(dirname "$0")"
while [ ! -f out/wave8_done.txt ]; do sleep 10; done
bash run.sh exp_dsv2d.py > out/dsv2d.log 2>&1
echo done > out/wave9_done.txt
