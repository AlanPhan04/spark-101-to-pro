"""Event-log extracts for the cluster experiments of Chapters 15 and 18 (apps dbgc-straggler, dbgc-fetchfail), after out/wave8_marker.

    python extract_cluster.py > ../book/figures/data/cluster_extract.json
"""
import glob
import json
import os
import sys

here = os.path.dirname(os.path.abspath(__file__))
cut = os.path.getmtime(os.path.join(here, "out", "wave8_marker"))
out = {"straggler": [], "fetchfail": None}
for path in sorted(glob.glob(os.path.join(here, "events", "*")), key=os.path.getmtime):
    if os.path.getmtime(path) <= cut:
        continue
    app, tasks, stages, subm, fails, groups, sg = None, [], [], {}, [], {}, {}
    for line in open(path, encoding="utf-8"):
        try:
            e = json.loads(line)
        except ValueError:
            continue
        ev = e.get("Event", "")
        if ev.endswith("ApplicationStart"):
            app = e["App Name"]
        elif ev.endswith("JobStart"):
            for s in e["Stage IDs"]:
                sg[s] = e.get("Properties", {}).get("spark.jobGroup.id", "")
        elif ev.endswith("TaskEnd"):
            ti = e["Task Info"]
            tasks.append({"stage": e["Stage ID"], "attempt": e["Stage Attempt ID"], "task": ti["Index"], "start": ti["Launch Time"], "end": ti["Finish Time"],
                          "speculative": ti["Speculative"], "killed": ti["Killed"], "reason": e["Task End Reason"].get("Reason"), "locality": ti["Locality"], "executor": ti["Executor ID"]})
        elif ev.endswith("StageCompleted"):
            si = e["Stage Info"]
            stages.append({"stage": si["Stage ID"], "attempt": si["Stage Attempt ID"], "tasks": si["Number of Tasks"], "failure": si.get("Failure Reason", ""),
                           "submit": si.get("Submission Time"), "complete": si.get("Completion Time"), "group": sg.get(si["Stage ID"], "")})
    if app == "dbgc-straggler":
        t0 = min(t["start"] for t in tasks)
        spec = any(t["speculative"] for t in tasks)
        out["straggler"].append({"speculation": spec, "total": (max(t["end"] for t in tasks) - t0) / 1000,
                                 "tasks": [{"task": t["task"], "start": (t["start"] - t0) / 1000, "end": (t["end"] - t0) / 1000, "speculative": t["speculative"], "killed": t["killed"],
                                            "reason": t["reason"], "executor": t["executor"]} for t in tasks]})
    if app == "dbgc-fetchfail":
        second = [s for s in stages if s["group"] == "dbgc_fetch2"]
        t0 = min(s["submit"] for s in second)
        out["fetchfail"] = {"stages": [{"stage": s["stage"], "attempt": s["attempt"], "tasks": s["tasks"], "failed": bool(s["failure"]), "start": (s["submit"] - t0) / 1000,
                                         "end": (s["complete"] - t0) / 1000, "failure": s["failure"][:90]} for s in sorted(second, key=lambda x: x["submit"])],
                            "fetch_failed_tasks": sum(1 for t in tasks if t["reason"] == "FetchFailed"),
                            "locality": {k: sum(1 for t in tasks if t["locality"] == k) for k in {t["locality"] for t in tasks}}}
json.dump(out, sys.stdout, indent=1)
