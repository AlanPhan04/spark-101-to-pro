#!/usr/bin/env bash
cd "$(dirname "$0")"
for h in 1 2 4; do for c in 1 2 4 8; do
  DRIVER_MEM=${h}g CORES=$c bash run.sh exp_tune_spill.py h${h}c${c} > out/tune_h${h}c${c}.log 2>&1 || echo "failed h${h}c${c}" >> out/tune_failed.txt
done; done
echo done > out/tune_done.txt
