#!/usr/bin/env python3
"""Chapter 14 measured figures (lab/exp_tune_*.py; data in figures/data/).

  spill-heatmap        heap x cores grid: disk spill of one sort-heavy stage
  cores-time-gc        wall clock and GC time against cores, one line per heap
  spill-vs-share       the same twelve runs against execution memory per task
  partitions-vs-slots  one aggregate at 8..5000 shuffle partitions on 40 slots
  dynalloc-timeline    executors over time under dynamic allocation
  conf-precedence      the value a session sees at each layer
"""
import csv
import json
import os

import matplotlib.pyplot as plt
import numpy as np

from bookplot import C, save, use_book_style

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, "data")
LAB = os.path.join(HERE, "..", "..", "lab", "out")


def rows(name):
    with open(os.path.join(D, name)) as f:
        return list(csv.DictReader(f))


grid = rows("tune_grid.csv")
heaps = [1, 2, 4]
cores = [1, 2, 4, 8]
cell = {(int(r["heap_gb"]), int(r["cores"])): r for r in grid}

# --- spill heatmap ---------------------------------------------------------------------------------------------------------------------------
use_book_style(2.8)
fig, ax = plt.subplots(figsize=(6.3, 2.8))
ax.grid(False)
for i, h in enumerate(heaps):
    for j, c in enumerate(cores):
        r = cell[(h, c)]
        spill = float(r["disk_spill_mb"])
        fill = C["rose_fill"] if spill > 0 else C["green_fill"]
        edge = C["rose"] if spill > 0 else C["green"]
        ink = C["rose_ink"] if spill > 0 else C["green_ink"]
        ax.add_patch(plt.Rectangle((j, i), 0.94, 0.94, facecolor=fill, edgecolor=edge, linewidth=1.2))
        ax.text(j + 0.47, i + 0.62, f"{spill:,.0f} MB spilled" if spill else "no spill", ha="center", va="center", fontsize=9, color=ink, fontweight="bold")
        ax.text(j + 0.47, i + 0.30, f"{r['share_mb']} MB/task · {r['seconds']} s", ha="center", va="center", fontsize=8, color=C["gray_ink"])
ax.set_xlim(0, 4); ax.set_ylim(0, 3)
ax.set_xticks([c + 0.47 for c in range(4)]); ax.set_xticklabels([f"{c} core{'s' if c > 1 else ''}" for c in cores])
ax.set_yticks([i + 0.47 for i in range(3)]); ax.set_yticklabels([f"{h} GB heap" for h in heaps])
ax.tick_params(length=0)
for s in ax.spines.values():
    s.set_visible(False)
ax.set_title("disk spill of one sort-heavy stage, by executor shape", fontsize=10)
fig.tight_layout()
save(fig, "spill-heatmap")

# --- cores vs time and GC --------------------------------------------------------------------------------------------------------------------
use_book_style(2.8)
fig, (a, b) = plt.subplots(1, 2, figsize=(6.3, 2.8))
cols = {1: C["rose"], 2: C["blue"], 4: C["green"]}
for h in heaps:
    xs = cores
    ts = [float(cell[(h, c)]["seconds"]) for c in cores]
    spilled = [float(cell[(h, c)]["disk_spill_mb"]) > 0 for c in cores]
    a.plot(xs, ts, color=cols[h], marker="o", markersize=5, label=f"{h} GB heap")
    for x, t, s in zip(xs, ts, spilled):
        if s:
            a.plot([x], [t], marker="o", markersize=11, markerfacecolor="none", markeredgecolor=C["gray_ink"], markeredgewidth=1.3)
    b.plot(xs, [float(cell[(h, c)]["gc_ms"]) / 1000 for c in cores], color=cols[h], marker="o", markersize=5, label=f"{h} GB heap")
a.set_xscale("log", base=2); b.set_xscale("log", base=2)
for ax in (a, b):
    ax.set_xticks(cores); ax.set_xticklabels(cores); ax.set_xlabel("task slots (cores)")
a.set_ylabel("wall clock (s)"); a.set_title("time falls with cores (ring = spilled)", fontsize=9.5)
b.set_ylabel("GC time, all tasks (s)"); b.set_title("GC grows with cores", fontsize=9.5)
a.legend(loc="upper right")
fig.tight_layout()
save(fig, "cores-time-gc")

# --- spill vs per-task share -----------------------------------------------------------------------------------------------------------------
use_book_style(2.7)
fig, ax = plt.subplots(figsize=(6.3, 2.7))
xs = [float(r["share_mb"]) for r in grid]
ys = [float(r["disk_spill_mb"]) for r in grid]
sp = [y > 0 for y in ys]
ax.scatter([x for x, s in zip(xs, sp) if s], [y for y, s in zip(ys, sp) if s], s=60, color=C["rose"], zorder=3, label="spilled")
ax.scatter([x for x, s in zip(xs, sp) if not s], [y for y, s in zip(ys, sp) if not s], s=60, color=C["green"], zorder=3, label="no spill")
ax.set_xscale("log")
ax.axvspan(298, 456, color=C["amber_fill"], zorder=0)
ax.text(370, 200, "threshold\nbetween\n298 and 456", ha="center", fontsize=8.5, color=C["annot"])
ax.set_xlabel("unified memory ÷ cores (MB per concurrent task)")
ax.set_ylabel("disk spill (MB)")
ax.set_xticks([57, 114, 228, 456, 910, 2388]); ax.set_xticklabels(["57", "114", "228", "456", "910", "2388"])
ax.legend(loc="upper right")
fig.tight_layout()
save(fig, "spill-vs-share")

# --- partitions vs slots ---------------------------------------------------------------------------------------------------------------------
p1, p2 = os.path.join(LAB, "tune_parts.json"), os.path.join(LAB, "tune_parts2.json")
if os.path.exists(p1) and os.path.exists(p2):
    use_book_style(2.9)
    fig, axes = plt.subplots(1, 2, figsize=(6.3, 2.9))
    for ax, path, title in ((axes[0], p1, "scan-bound: partial aggregate"), (axes[1], p2, "shuffle-bound: window sort")):
        pr = json.load(open(path))
        xs = [r["partitions"] for r in pr]
        ts = [r["seconds"] for r in pr]
        ax.plot(range(len(xs)), ts, color=C["blue"], marker="o", markersize=5)
        for i, t in enumerate(ts):
            ax.text(i, t + max(ts) * 0.05, f"{t:g}", ha="center", fontsize=7.5, color=C["gray_ink"], bbox=dict(facecolor="white", edgecolor="none", pad=0.8, alpha=0.9), zorder=5)
        if 8 in xs:
            ax.axvline(xs.index(8), color=C["green"], linestyle="--", linewidth=1.2)
            ax.text(xs.index(8) + 0.12, max(ts) * 1.12, "8 slots", fontsize=8, color=C["green_ink"])
        ax.set_xticks(range(len(xs))); ax.set_xticklabels([str(x) for x in xs], fontsize=7.5)
        ax.set_xlabel("shuffle partitions"); ax.set_ylim(0, max(ts) * 1.22)
        ax.set_title(title, fontsize=9)
    axes[0].set_ylabel("seconds")
    fig.tight_layout()
    save(fig, "partitions-vs-slots")

# --- dynamic allocation timeline -------------------------------------------------------------------------------------------------------------
dyn = os.path.join(D, "dynalloc_timeline.json")
if os.path.exists(dyn):
    tl = json.load(open(dyn))
    use_book_style(3.0)
    names = [("shuffle", "job 1 leaves shuffle files\n(tracking on)"), ("shuffle_timeout", "same, tracking timeout 8 s"), ("noshuf", "job 1 leaves no shuffle files")]
    fig, axes = plt.subplots(1, 3, figsize=(6.3, 3.0), sharey=True)
    for ax, (key, title) in zip(axes, names):
        s_ = tl[key]
        ax.step(s_["t"], s_["n"], where="post", color=C["blue"], linewidth=2.2)
        ax.axvspan(s_["jobs"][0][1], s_["jobs"][1][1], color=C["amber_fill"], zorder=0)
        ax.text((s_["jobs"][0][1] + s_["jobs"][1][1]) / 2, 4.4, "idle", fontsize=8, ha="center", color=C["annot"])
        ax.set_title(title, fontsize=8.2)
        ax.set_xlabel("seconds"); ax.set_ylim(0, 4.8); ax.set_yticks(range(0, 5))
    axes[0].set_ylabel("executors")
    fig.tight_layout()
    save(fig, "dynalloc-timeline")
