"""Per job group: wall time, tasks, spill (memory/disk), GC time, from the event logs written after a cutoff file.

    python tune_summary.py out/gen_data.log tune_ > out/tune_grid.json
"""
import glob
import json
import os
import sys

cut = os.path.getmtime(sys.argv[1])
prefix = sys.argv[2]
res = {}
for path in glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), "events", "*")):
    if os.path.getmtime(path) <= cut:
        continue
    grp, jobs, st = {}, {}, {}
    if path.endswith((".zstd", ".lz4", ".snappy", ".lzf")):
        continue
    with open(path, encoding="utf-8", errors="ignore") as f:
        for line in f:
            try:
                e = json.loads(line)
            except ValueError:
                continue
            ev = e.get("Event", "")
            if ev.endswith("JobStart"):
                g = e.get("Properties", {}).get("spark.jobGroup.id", "-")
                jobs[e["Job ID"]] = g
                for s in e["Stage IDs"]:
                    grp[s] = g
            elif ev.endswith("TaskEnd"):
                g = grp.get(e["Stage ID"], "-")
                if not g.startswith(prefix):
                    continue
                m = e.get("Task Metrics") or {}
                d = res.setdefault(g, {"tasks": 0, "mem_spill": 0, "disk_spill": 0, "gc_ms": 0, "run_ms": 0, "peak_mem": 0, "failed": 0, "shuffle_write": 0, "shuffle_read": 0, "input_bytes": 0, "input_records": 0})
                d["tasks"] += 1
                d["mem_spill"] += m.get("Memory Bytes Spilled", 0)
                d["disk_spill"] += m.get("Disk Bytes Spilled", 0)
                d["gc_ms"] += m.get("JVM GC Time", 0)
                d["run_ms"] += m.get("Executor Run Time", 0)
                d["shuffle_write"] += m.get("Shuffle Write Metrics", {}).get("Shuffle Bytes Written", 0)
                sr = m.get("Shuffle Read Metrics", {})
                d["shuffle_read"] += sr.get("Remote Bytes Read", 0) + sr.get("Local Bytes Read", 0)
                d["input_bytes"] += m.get("Input Metrics", {}).get("Bytes Read", 0)
                d["input_records"] += m.get("Input Metrics", {}).get("Records Read", 0)
                d["peak_mem"] = max(d["peak_mem"], m.get("Peak Execution Memory", 0))
                if e["Task End Reason"].get("Reason") != "Success":
                    d["failed"] += 1
json.dump(res, sys.stdout, indent=1)
