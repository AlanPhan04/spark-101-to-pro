"""Export per-task shuffle-read bytes of one job group's reduce stage to CSV (for measured figures).

    python export_task_sizes.py <job_group> <min_tasks> <out.csv>
"""
import csv
import glob
import json
import os
import sys

group, min_tasks, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
here = os.path.dirname(os.path.abspath(__file__))
after = os.path.getmtime(os.path.join(here, "out", "gen_data.log"))
best = None
for path in sorted(glob.glob(os.path.join(here, "events", "*")), key=os.path.getmtime):
    if os.path.getmtime(path) <= after:
        continue
    job_group, stage_job, tasks = {}, {}, {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            e = json.loads(line)
            ev = e.get("Event", "")
            if ev.endswith("JobStart"):
                job_group[e["Job ID"]] = e.get("Properties", {}).get("spark.jobGroup.id", "-")
                for s in e["Stage IDs"]:
                    stage_job[s] = e["Job ID"]
            elif ev.endswith("TaskEnd"):
                m = e.get("Task Metrics") or {}
                sr = m.get("Shuffle Read Metrics", {})
                b = sr.get("Remote Bytes Read", 0) + sr.get("Local Bytes Read", 0)
                dur = e["Task Info"]["Finish Time"] - e["Task Info"]["Launch Time"]
                tasks.setdefault(e["Stage ID"], []).append((b, dur))
    for sid, ts in tasks.items():
        if job_group.get(stage_job.get(sid)) == group and len(ts) >= min_tasks:
            if best is None or sum(b for b, _ in ts) > sum(b for b, _ in best):
                best = ts
if best is None:
    sys.exit("no matching stage")
with open(out, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["shuffle_read_bytes", "duration_ms"])
    w.writerows(best)
print("wrote", out, len(best), "tasks; max", max(b for b, _ in best))
