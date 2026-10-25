#!/usr/bin/env bash
cd "$(dirname "$0")"
rm -f out/wave4_done.txt
while [ ! -f out/wave3_done.txt ]; do sleep 10; done
bash run.sh exp_dsv2c.py > out/dsv2c.log 2>&1
bash run_pip.sh exp_tungsten2.py > out/tungsten2.log 2>&1
DRIVER_MEM=2g CORES=4 EXTRA_CONF="--conf spark.memory.offHeap.enabled=true --conf spark.memory.offHeap.size=1g" bash run.sh exp_tune_spill.py oh2g1g_c4 > out/tune_oh.log 2>&1
DRIVER_MEM=1g CORES=4 EXTRA_CONF="--conf spark.memory.offHeap.enabled=true --conf spark.memory.offHeap.size=1g" bash run.sh exp_tune_spill.py oh1g1g_c4 > out/tune_oh2.log 2>&1
# streaming (Ch 16)
for t in 2 10 30; do bash run.sh exp_stream.py cadence $t 100 > out/stream_cad_$t.log 2>&1; done
bash run.sh exp_stream.py state none 100 > out/stream_state_none.log 2>&1
bash run.sh exp_stream.py state watermark 100 > out/stream_state_wm.log 2>&1
bash run.sh exp_stream.py modes > out/stream_modes.log 2>&1
bash run.sh exp_stream.py availnow > out/stream_avail.log 2>&1
rm -rf ckpt/s_kill
NAME=lab-kill bash run.sh exp_stream.py killrun 200 > out/stream_kill1.log 2>&1 &
sleep 60
docker kill lab-kill > /dev/null 2>&1
wait
bash run.sh exp_stream.py killrun 30 > out/stream_kill2.log 2>&1
bash run.sh exp_stream.py check > out/stream_kill_check.log 2>&1
echo done > out/wave4_done.txt
