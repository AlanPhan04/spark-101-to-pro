"""Executors over time from event logs of apps whose name starts with a prefix.

    python executor_timeline.py out/tune2_marker dyn- > ../book/figures/data/dynalloc_timeline.json
Keys: <scenario>[_variant]; t in seconds from the first job start, n = live executors (the driver is not counted).
"""
import glob
import json
import os
import sys

cut = os.path.getmtime(sys.argv[1])
prefix = sys.argv[2]
out = {}
for path in sorted(glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), "events", "*"), recursive=False), key=os.path.getmtime):
    if os.path.getmtime(path) <= cut:
        continue
    app, evs, jobs = None, [], []
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                e = json.loads(line)
            except ValueError:
                continue
            ev = e.get("Event", "")
            if ev.endswith("ApplicationStart"):
                app = e["App Name"]
            elif ev.endswith("ExecutorAdded"):
                evs.append((e["Timestamp"], +1, e["Executor ID"]))
            elif ev.endswith("ExecutorRemoved"):
                evs.append((e["Timestamp"], -1, e["Executor ID"]))
            elif ev.endswith("JobStart"):
                jobs.append(("start", e["Submission Time"], e["Job ID"], e.get("Properties", {}).get("spark.jobGroup.id", "")))
            elif ev.endswith("JobEnd"):
                jobs.append(("end", e["Completion Time"], e["Job ID"], ""))
    if not app or not app.startswith(prefix) or not jobs:
        continue
    t0 = min(j[1] for j in jobs) - 1500
    evs.sort()
    n, ts, ns = 0, [0.0], [0]
    for t, d, _ in evs:
        n += d
        ts.append(round((t - t0) / 1000, 1)); ns.append(n)
    end = max(j[1] for j in jobs)
    ts.append(round((end - t0) / 1000 + 3, 1)); ns.append(n)
    marks = [("job1 ends", round((j[1] - t0) / 1000, 1)) for j in jobs if j[0] == "end"][:1]
    marks += [("job2 starts", round((j[1] - t0) / 1000, 1)) for j in jobs if j[0] == "start"][1:2]
    out[app + "|" + os.path.basename(path)] = {"t": ts, "n": ns, "jobs": marks}
json.dump(out, sys.stdout, indent=1)
