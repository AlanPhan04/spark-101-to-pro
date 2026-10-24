"""Summarize Spark event logs per job group: tasks, task-time spread, shuffle read, input bytes.

Run on the host:  python events_summary.py [events_dir] > out/summary.txt
"""
import glob
import json
import os
import statistics
import sys

args = [a for a in sys.argv[1:] if not a.startswith("--")]
events_dir = args[0] if args else os.path.join(os.path.dirname(os.path.abspath(__file__)), "events")
# --after=FILE: only event logs written after FILE was last modified (skip runs on older data)
cutoff = 0
for a in sys.argv[1:]:
    if a.startswith("--after="):
        cutoff = os.path.getmtime(a.split("=", 1)[1])


def mb(x):
    return f"{x / 1e6:,.1f}"


for path in sorted(glob.glob(os.path.join(events_dir, "*")), key=os.path.getmtime):
    if os.path.getmtime(path) <= cutoff:
        continue
    app = None
    job_group = {}          # job id -> group
    stage_job = {}          # stage id -> job id
    stage_attempt_ok = {}   # stage id -> latest attempt id seen complete
    tasks = {}              # (stage, attempt) -> list of (duration_ms, shuffle_read, input_bytes, records)
    names = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                e = json.loads(line)
            except ValueError:
                continue
            ev = e.get("Event", "")
            if ev.endswith("ApplicationStart"):
                app = e.get("App Name")
            elif ev.endswith("JobStart"):
                grp = e.get("Properties", {}).get("spark.jobGroup.id", "-")
                job_group[e["Job ID"]] = grp
                for s in e["Stage IDs"]:
                    stage_job[s] = e["Job ID"]
            elif ev.endswith("StageCompleted"):
                si = e["Stage Info"]
                names[(si["Stage ID"], si["Stage Attempt ID"])] = si["Stage Name"][:48]
            elif ev.endswith("TaskEnd"):
                m = e.get("Task Metrics") or {}
                sr = m.get("Shuffle Read Metrics", {})
                inp = m.get("Input Metrics", {})
                key = (e["Stage ID"], e["Stage Attempt ID"])
                dur = e["Task Info"]["Finish Time"] - e["Task Info"]["Launch Time"]
                tasks.setdefault(key, []).append((
                    dur,
                    sr.get("Remote Bytes Read", 0) + sr.get("Local Bytes Read", 0),
                    inp.get("Bytes Read", 0),
                    sr.get("Total Records Read", 0)))
    print(f"##### app={app} file={os.path.basename(path)}")
    for (sid, att), ts in sorted(tasks.items()):
        grp = job_group.get(stage_job.get(sid), "-")
        d = sorted(t[0] for t in ts)
        sh = sum(t[1] for t in ts)
        inp = sum(t[2] for t in ts)
        shmax = max(t[1] for t in ts)
        print(f"{grp:32s} stage {sid:3d}.{att}  tasks={len(ts):5d}  dur_ms min/med/max="
              f"{d[0]}/{int(statistics.median(d))}/{d[-1]}  shuffleRead={mb(sh)}MB (max task {mb(shmax)}MB)"
              f"  input={mb(inp)}MB  {names.get((sid, att), '')}")
