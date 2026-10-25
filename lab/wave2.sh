#!/usr/bin/env bash
cd "$(dirname "$0")"
rm -f out/wave2_done.txt
bash run.sh exp_dsv2.py > out/dsv2.log 2>&1
EXTRA_CONF="--conf spark.sql.extensions=" bash run.sh exp_dsv2_noext.py > out/dsv2_noext.log 2>&1
bash run.sh exp_sched.py > out/sched.log 2>&1
echo done > out/wave2_done.txt
