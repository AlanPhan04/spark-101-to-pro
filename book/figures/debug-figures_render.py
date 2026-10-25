#!/usr/bin/env python3
"""Chapter 15 measured figures (lab/exp_debug_*.py; data in figures/data/).

  task-durations-skew   the 40 tasks of a skewed join stage, sorted by duration
  task-four-metrics     median vs maximum task: duration, scheduler delay, records read, spill, GC
  eventlog-anatomy      bytes in an event log by event type
  speculation-gantt     task attempts with and without speculation (if the data exist)
  fetch-failure-stages  stage attempts after one executor's shuffle files were deleted (if the data exist)
"""
import json
import os

import matplotlib.pyplot as plt

from bookplot import C, save, use_book_style

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, "data")

sk = json.load(open(os.path.join(D, "debug_skew_tasks.json")))
tasks = sorted(sk["all"], key=lambda t: t["duration_ms"])

# --- 40 tasks sorted ----------------------------------------------------------------------------------------------------------------------------
use_book_style(2.7)
fig, ax = plt.subplots(figsize=(6.3, 2.7))
durs = [t["duration_ms"] / 1000 for t in tasks]
cols = [C["rose"] if i == len(durs) - 1 else C["blue"] for i in range(len(durs))]
fills = [C["rose_fill"] if i == len(durs) - 1 else C["blue_fill"] for i in range(len(durs))]
ax.bar(range(len(durs)), durs, color=fills, edgecolor=cols, linewidth=1.0)
ax.axhline(sk["median_task"]["duration_ms"] / 1000, color=C["green"], linestyle="--", linewidth=1.2)
ax.text(1, sk["median_task"]["duration_ms"] / 1000 + 0.25, f"median {sk['median_task']['duration_ms'] / 1000:.2f} s", fontsize=8.5, color=C["green_ink"])
ax.text(len(durs) - 2.2, durs[-1] - 0.3, f"{durs[-1]:.1f} s: {sk['ratio_max_over_median']}× the median", fontsize=8.5, color=C["rose_ink"], ha="right", va="top")
ax.set_xlabel("the 40 tasks of the join stage, sorted by duration"); ax.set_ylabel("seconds"); ax.set_xticks([])
ax.grid(axis="x", visible=False)
fig.tight_layout()
save(fig, "task-durations-skew")

# --- four metrics -------------------------------------------------------------------------------------------------------------------------------
med, mx = sk["median_task"], sk["max_task"]
panels = [("duration (s)", med["duration_ms"] / 1000, mx["duration_ms"] / 1000, "{:.2f}"),
          ("scheduler\ndelay (ms)", med["sched_delay_ms"], mx["sched_delay_ms"], "{:g}"),
          ("records read\n(millions)", med["shuffle_records"] / 1e6, mx["shuffle_records"] / 1e6, "{:.2f}"),
          ("memory spilled\n(MB)", med["mem_spill_mb"], mx["mem_spill_mb"], "{:g}"),
          ("GC time\n(ms)", med["gc_ms"], mx["gc_ms"], "{:g}")]
use_book_style(2.6)
fig, axes = plt.subplots(1, 5, figsize=(6.3, 2.6))
for ax, (title, a, b, fmt) in zip(axes, panels):
    ax.bar([0, 1], [a, b], color=[C["green_fill"], C["rose_fill"]], edgecolor=[C["green"], C["rose"]], linewidth=1.2, width=0.7)
    top = max(a, b, 1e-9)
    for x, v in ((0, a), (1, b)):
        ax.text(x, v + top * 0.03, fmt.format(v), ha="center", fontsize=8, color=C["gray_ink"])
    ax.set_ylim(0, top * 1.25)
    ax.set_xticks([0, 1]); ax.set_xticklabels(["median", "max"], fontsize=8)
    ax.set_title(title, fontsize=8.5)
    ax.grid(axis="x", visible=False)
    ax.tick_params(axis="y", labelsize=7.5)
fig.tight_layout()
save(fig, "task-four-metrics")

# --- event log anatomy ---------------------------------------------------------------------------------------------------------------------------
ev = json.load(open(os.path.join(D, "eventlog_anatomy.json")))
top = ev["top"][:6]
use_book_style(2.6)
fig, ax = plt.subplots(figsize=(6.3, 2.6))
ys = list(range(len(top)))[::-1]
ax.barh(ys, [t["bytes"] / 1e3 for t in top], color=C["blue_fill"], edgecolor=C["blue"], linewidth=1.2)
for y, t in zip(ys, top):
    ax.text(t["bytes"] / 1e3 + 10, y, f"{t['bytes'] / 1e3:,.0f} KB  ({t['count']} events)", va="center", fontsize=8.5, color=C["gray_ink"])
ax.set_yticks(ys); ax.set_yticklabels([t["event"] for t in top], fontsize=8.5)
ax.set_xlim(0, max(t["bytes"] for t in top) / 1e3 * 1.55)
ax.set_xlabel(f"kilobytes in a {ev['bytes'] / 1e6:.2f} MB event log ({ev['events']} events, {ev['tasks']} tasks)")
ax.grid(axis="y", visible=False)
fig.tight_layout()
save(fig, "eventlog-anatomy")

# --- speculation gantt -------------------------------------------------------------------------------------------------------------------------------
sp = os.path.join(D, "speculation_attempts.json")
if os.path.exists(sp):
    data = json.load(open(sp))
    use_book_style(3.0)
    fig, axes = plt.subplots(1, 2, figsize=(6.3, 3.0), sharey=True, sharex=True)
    for ax, key, title in zip(axes, ("off", "on"), ("speculation off", "speculation on")):
        for a in data[key]:
            y = a["task"] + (0.18 if a["speculative"] else -0.18 if any(b["task"] == a["task"] and b["speculative"] for b in data[key]) else 0)
            color = C["orange"] if a["speculative"] else C["blue"]
            fill = C["orange_fill"] if a["speculative"] else C["blue_fill"]
            if a["killed"]:
                fill = C["rose_fill"]; color = C["rose"]
            ax.barh(y, a["end"] - a["start"], left=a["start"], height=0.32, color=fill, edgecolor=color, linewidth=1.0)
        ax.set_title(f"{title}: {data[key + '_total']:.0f} s", fontsize=9)
        ax.set_xlabel("seconds"); ax.set_yticks(range(8)); ax.grid(axis="y", visible=False)
    axes[0].set_ylabel("task (partition)")
    fig.tight_layout()
    save(fig, "speculation-gantt")

# --- fetch failure stages -----------------------------------------------------------------------------------------------------------------------------
ff = os.path.join(D, "fetchfail_stages.json")
if os.path.exists(ff):
    data = json.load(open(ff))
    use_book_style(2.9)
    fig, ax = plt.subplots(figsize=(6.3, 2.9))
    labels = []
    for i, s in enumerate(data["stages"][::-1]):
        color = C["rose"] if s.get("failed") else C["blue"]
        fill = C["rose_fill"] if s.get("failed") else C["blue_fill"]
        ax.barh(i, s["end"] - s["start"], left=s["start"], height=0.55, color=fill, edgecolor=color, linewidth=1.1)
        ax.text(s["end"] + 0.1, i, f"{s['tasks']} tasks" + (" — FetchFailed" if s.get("failed") else ""), va="center", fontsize=8, color=C["gray_ink"])
        labels.append(s["label"])
    ax.set_yticks(range(len(labels))); ax.set_yticklabels(labels, fontsize=8)
    ax.set_xlabel("seconds since the second job started")
    ax.grid(axis="y", visible=False)
    ax.set_xlim(0, max(s["end"] for s in data["stages"]) * 1.35)
    fig.tight_layout()
    save(fig, "fetch-failure-stages")
