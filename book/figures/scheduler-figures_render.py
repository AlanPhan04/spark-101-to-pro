#!/usr/bin/env python3
"""Chapter 18 measured figures (lab/exp_sched.py, exp_debug_cluster.py).

  shuffle-writer-grid   which shuffle writer each SQL shuffle gets, by partition count and query shape
  task-scheduling-cost  driver-side cost per task as the task count grows
  fetch-failure-stages  stage attempts of a job that lost one executor's shuffle files (if the data exist)
"""
import json
import os
from collections import Counter

import matplotlib.pyplot as plt

from bookplot import C, save, use_book_style

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, "data")
sched = json.load(open(os.path.join(D, "sched_results.json")))

# --- writer grid -----------------------------------------------------------------------------------------------------------------------------
parts = [50, 200, 201, 1000]
queries = ["repartition(n)", "GROUP BY", "sort-merge join", "ORDER BY", "window"]
cell = {(r["partitions"], r["query"]): r["writers"] for r in sched["writers"]}
style = {"BypassMergeSort": (C["blue_fill"], C["blue"], C["blue_ink"], "bypass"),
         "Serialized": (C["green_fill"], C["green"], C["green_ink"], "serialized"),
         "Base": (C["orange_fill"], C["orange"], C["orange_ink"], "sort")}
use_book_style(3.0)
fig, ax = plt.subplots(figsize=(6.3, 3.0))
ax.grid(False)
for i, q in enumerate(queries):
    for j, p in enumerate(parts):
        w = cell[(p, q)]
        cnt = Counter(w)
        main = max(cnt, key=lambda k: (cnt[k], k == "Serialized"))
        fill, edge, ink, name = style[main]
        label = name if len(cnt) == 1 else "2 × serialized\n+ 1 × bypass"
        ax.add_patch(plt.Rectangle((j, len(queries) - 1 - i), 0.94, 0.9, facecolor=fill, edgecolor=edge, linewidth=1.2))
        ax.text(j + 0.47, len(queries) - 1 - i + 0.45, label, ha="center", va="center", fontsize=8.5, color=ink, fontweight="bold")
ax.set_xlim(0, 4); ax.set_ylim(0, 5)
ax.set_xticks([j + 0.47 for j in range(4)]); ax.set_xticklabels([f"{p} partitions" for p in parts])
ax.set_yticks([len(queries) - 1 - i + 0.45 for i in range(len(queries))]); ax.set_yticklabels(queries)
ax.tick_params(length=0)
for s in ax.spines.values():
    s.set_visible(False)
ax.set_title("shuffle writer chosen, by partition count and query shape", fontsize=10)
fig.tight_layout()
save(fig, "shuffle-writer-grid")

# --- scheduling cost -------------------------------------------------------------------------------------------------------------------------
t = sched["task_scheduling"]
use_book_style(2.7)
fig, (a, b) = plt.subplots(1, 2, figsize=(6.3, 2.7))
xs = [r["tasks"] for r in t]
a.plot(range(len(xs)), [r["seconds"] for r in t], color=C["blue"], marker="o", markersize=5)
for i, r in enumerate(t):
    if i == 2:
        a.text(i - 0.1, r["seconds"] + 1.0, f"{r['seconds']:g} s", ha="right", fontsize=8, color=C["gray_ink"])
    elif i < len(t) - 1:
        a.text(i, r["seconds"] + 1.6, f"{r['seconds']:g} s", ha="center", fontsize=8, color=C["gray_ink"])
    else:
        a.text(i - 0.12, r["seconds"] - 0.5, f"{r['seconds']:g} s", ha="right", va="top", fontsize=8, color=C["gray_ink"])
a.set_xticks(range(len(xs))); a.set_xticklabels([f"{x:,}" for x in xs], fontsize=8)
a.set_xlabel("tasks in one stage"); a.set_ylabel("seconds"); a.set_title("whole stage", fontsize=9.5); a.set_ylim(0, 21)
bars = b.bar(range(len(xs)), [r["ms_per_task"] for r in t], color=[C["blue_fill"]] * 3 + [C["rose_fill"]], edgecolor=[C["blue"]] * 3 + [C["rose"]], linewidth=1.2)
for i, r in enumerate(t):
    b.text(i, r["ms_per_task"] + 0.006, f"{r['ms_per_task']:g}", ha="center", fontsize=8, color=C["gray_ink"])
b.set_xticks(range(len(xs))); b.set_xticklabels([f"{x:,}" for x in xs], fontsize=8)
b.set_xlabel("tasks in one stage"); b.set_ylabel("milliseconds per task"); b.set_title("per task", fontsize=9.5); b.set_ylim(0, 0.26)
b.grid(axis="x", visible=False)
fig.tight_layout()
save(fig, "task-scheduling-cost")
