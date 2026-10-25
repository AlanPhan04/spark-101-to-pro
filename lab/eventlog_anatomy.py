"""What is inside a Spark event log: event-type counts and bytes by type for one application.

    python eventlog_anatomy.py debug-skew > ../book/figures/data/eventlog_anatomy.json
"""
import collections
import glob
import json
import os
import sys

name = sys.argv[1]
here = os.path.dirname(os.path.abspath(__file__))
for path in sorted(glob.glob(os.path.join(here, "events", "*")), key=os.path.getmtime, reverse=True):
    cnt, size = collections.Counter(), collections.Counter()
    app = None
    total = 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            total += len(line.encode("utf-8"))
            try:
                e = json.loads(line)
            except ValueError:
                continue
            ev = e.get("Event", "").replace("org.apache.spark.", "").replace("sql.execution.ui.", "").replace("scheduler.", "")
            if ev.endswith("ApplicationStart"):
                app = e["App Name"]
            cnt[ev] += 1
            size[ev] += len(line.encode("utf-8"))
    if app == name:
        top = [{"event": k.replace("SparkListener", ""), "count": cnt[k], "bytes": size[k]} for k, _ in size.most_common(8)]
        json.dump({"app": app, "file": os.path.basename(path), "bytes": total, "events": sum(cnt.values()), "top": top,
                   "tasks": cnt.get("SparkListenerTaskEnd", 0), "bytes_per_task": round(size.get("SparkListenerTaskEnd", 0) / max(1, cnt.get("SparkListenerTaskEnd", 1)))}, sys.stdout, indent=1)
        break
