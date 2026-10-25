"""Median vs maximum task of the stage with the largest max/median duration in a job group (the four numbers of Chapter 15).

    python task_table.py out/wave3_marker debug_skew > ../book/figures/data/debug_skew_tasks.json
"""
import glob
import json
import os
import statistics
import sys

cut = os.path.getmtime(sys.argv[1])
group = sys.argv[2]
best = None
for path in glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), "events", "*")):
    if os.path.getmtime(path) <= cut:
        continue
    jobs, stage_group, tasks = {}, {}, {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                e = json.loads(line)
            except ValueError:
                continue
            ev = e.get("Event", "")
            if ev.endswith("JobStart"):
                g = e.get("Properties", {}).get("spark.jobGroup.id", "-")
                for s in e["Stage IDs"]:
                    stage_group[s] = g
            elif ev.endswith("TaskEnd") and stage_group.get(e["Stage ID"]) == group:
                m = e.get("Task Metrics") or {}
                ti = e["Task Info"]
                dur = ti["Finish Time"] - ti["Launch Time"]
                run = m.get("Executor Run Time", 0)
                deser = m.get("Executor Deserialize Time", 0)
                ser = m.get("Result Serialization Time", 0)
                sr = m.get("Shuffle Read Metrics", {})
                tasks.setdefault(e["Stage ID"], []).append({
                    "index": ti["Index"], "duration_ms": dur, "run_ms": run, "sched_delay_ms": max(0, dur - run - deser - ser),
                    "shuffle_read_mb": round((sr.get("Remote Bytes Read", 0) + sr.get("Local Bytes Read", 0)) / 1e6, 1),
                    "shuffle_records": sr.get("Total Records Read", 0),
                    "mem_spill_mb": round(m.get("Memory Bytes Spilled", 0) / 1e6), "disk_spill_mb": round(m.get("Disk Bytes Spilled", 0) / 1e6),
                    "gc_ms": m.get("JVM GC Time", 0), "input_mb": round(m.get("Input Metrics", {}).get("Bytes Read", 0) / 1e6, 1)})
    for sid, ts in tasks.items():
        d = sorted(t["duration_ms"] for t in ts)
        ratio = d[-1] / max(1, statistics.median(d))
        if len(ts) >= 8 and (best is None or ratio > best[0]):
            best = (ratio, sid, ts)
ratio, sid, ts = best
ts.sort(key=lambda t: t["duration_ms"])
med = ts[len(ts) // 2]
out = {"stage": sid, "tasks": len(ts), "ratio_max_over_median": round(ratio, 1), "median_task": med, "max_task": ts[-1], "all": ts}
json.dump(out, sys.stdout, indent=1)
