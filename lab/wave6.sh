#!/usr/bin/env bash
cd "$(dirname "$0")"
while [ ! -f out/wave5_done.txt ]; do sleep 10; done
bash run.sh exp_jvm.py > out/jvm.log 2>&1
bash run_scala.sh ser.scala > out/ser.txt 2>&1
bash exp_gc.sh
echo done > out/wave6_done.txt
