#!/usr/bin/env python3
"""Chapter 17 measured figures (lab/exp_tungsten.py, exp_tungsten2.py, exp_tune_spill.py with off-heap).

  wholestage-onoff   three queries with spark.sql.codegen.wholeStage on and off
  udf-cost           built-in expression vs Python UDF (vs pandas UDF)
  radix-sort         spark.sql.sort.enableRadixSort on / off
  codegen-fields     the 100-field limit (if data exist)
  offheap-gc         on-heap vs off-heap execution memory (if data exist)
"""
import json
import os

import matplotlib.pyplot as plt

from bookplot import C, save, use_book_style

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, "data")
t = json.load(open(os.path.join(D, "tungsten_results.json")))

# --- whole-stage codegen on/off ---------------------------------------------------------------------------------------------------------------
use_book_style(2.7)
fig, ax = plt.subplots(figsize=(6.3, 2.7))
ws = t["wholestage"]
w = 0.36
xs = range(len(ws))
on = [r["codegen_true"] for r in ws]
off = [r["codegen_false"] for r in ws]
ax.bar([x - w / 2 for x in xs], on, w, color=C["green_fill"], edgecolor=C["green"], linewidth=1.2, label="whole-stage codegen on")
ax.bar([x + w / 2 for x in xs], off, w, color=C["rose_fill"], edgecolor=C["rose"], linewidth=1.2, label="off")
for x, a_, b_ in zip(xs, on, off):
    ax.text(x - w / 2, a_ + 0.12, f"{a_:g} s", ha="center", fontsize=8.5, color=C["gray_ink"])
    ax.text(x + w / 2, b_ + 0.12, f"{b_:g} s", ha="center", fontsize=8.5, color=C["gray_ink"])
    ax.text(x, max(a_, b_) + 0.75, f"{b_ / a_:.2f}×", ha="center", fontsize=9, color=C["annot"], fontweight="bold")
ax.set_xticks(list(xs)); ax.set_xticklabels(["filter +\naggregate", "arithmetic\nchain", "group by\n(shuffle-bound)"], fontsize=8.5)
ax.set_ylabel("seconds"); ax.set_ylim(0, 9.4); ax.legend(loc="upper left"); ax.grid(axis="x", visible=False)
fig.tight_layout()
save(fig, "wholestage-onoff")

# --- Python UDF ---------------------------------------------------------------------------------------------------------------------------------
u = t["udf"]
p2 = os.path.join(D, "tungsten2_results.json")
t2 = json.load(open(p2)) if os.path.exists(p2) else {}
labels = ["built-in\nexpression", "row-at-a-time\nPython UDF"]
vals = [u["builtin_s"], u["python_udf_s"]]
cols = [C["green"], C["rose"]]
fills = [C["green_fill"], C["rose_fill"]]
if isinstance(t2.get("pandas_udf_s"), (int, float)):
    labels.insert(1, "pandas UDF\n(Arrow batches)")
    vals.insert(1, t2["pandas_udf_s"]); cols.insert(1, C["blue"]); fills.insert(1, C["blue_fill"])
use_book_style(2.7)
fig, ax = plt.subplots(figsize=(6.3, 2.7))
ax.bar(range(len(vals)), vals, color=fills, edgecolor=cols, linewidth=1.2)
ax.set_yscale("log"); ax.set_ylim(0.1, 40)
for i, v in enumerate(vals):
    ax.text(i, v * 1.15, f"{v:g} s" + ("" if i == 0 else f"  ({v / vals[0]:.0f}×)"), ha="center", fontsize=9, color=C["gray_ink"])
ax.set_xticks(range(len(vals))); ax.set_xticklabels(labels, fontsize=8.5)
ax.set_ylabel("seconds, log scale"); ax.grid(axis="x", visible=False)
fig.tight_layout()
save(fig, "udf-cost")

# --- radix sort -----------------------------------------------------------------------------------------------------------------------------------
r = t["radix"]
use_book_style(2.4)
fig, ax = plt.subplots(figsize=(6.3, 2.4))
ax.barh([1, 0], [r["true"], r["false"]], color=[C["green_fill"], C["rose_fill"]], edgecolor=[C["green"], C["rose"]], linewidth=1.2, height=0.55)
for y, v in ((1, r["true"]), (0, r["false"])):
    ax.text(v + 0.1, y, f"{v:g} s", va="center", fontsize=9, color=C["gray_ink"])
ax.set_yticks([1, 0]); ax.set_yticklabels(["enableRadixSort = true (default)", "enableRadixSort = false"], fontsize=9)
ax.set_xlim(0, 9); ax.set_xlabel("seconds to sort 9 days of orders by order_ts (window)"); ax.grid(axis="y", visible=False)
fig.tight_layout()
save(fig, "radix-sort")

# --- 100-field limit ------------------------------------------------------------------------------------------------------------------------------
if t2.get("wide"):
    wd = t2["wide"]
    use_book_style(2.7)
    fig, ax = plt.subplots(figsize=(6.3, 2.7))
    xs = range(len(wd))
    cols = [C["green"] if x["wholestage_in_project"] else C["rose"] for x in wd]
    fills = [C["green_fill"] if x["wholestage_in_project"] else C["rose_fill"] for x in wd]
    ax.bar(xs, [x["seconds"] for x in wd], color=fills, edgecolor=cols, linewidth=1.2)
    ax.set_yscale("log"); ax.set_ylim(1, 150)
    for i, x in enumerate(wd):
        ax.text(i, x["seconds"] * 1.12, f"{x['seconds']:g} s", ha="center", fontsize=8.5, color=C["gray_ink"])
    ax.set_xticks(list(xs)); ax.set_xticklabels([str(x["columns"]) for x in wd]); ax.set_xlabel("columns produced by one SELECT")
    ax.set_ylabel("seconds, log scale"); ax.grid(axis="x", visible=False)
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(facecolor=C["green_fill"], edgecolor=C["green"], label="Project inside whole-stage codegen"),
                       Patch(facecolor=C["rose_fill"], edgecolor=C["rose"], label="Project interpreted")], loc="upper right", fontsize=8.5)
    fig.tight_layout()
    save(fig, "codegen-fields")

# --- off-heap -------------------------------------------------------------------------------------------------------------------------------------
grid = {}
for k in ("tune_h2c4", "tune_h1c4", "tune_oh2g1g_c4", "tune_oh1g1g_c4"):
    pth = os.path.join(D, k + ".json")
    if os.path.exists(pth):
        grid[k] = json.load(open(pth))
if len(grid) == 4:
    names = [("tune_h1c4", "1 GB heap"), ("tune_oh1g1g_c4", "1 GB heap\n+ 1 GB off-heap"), ("tune_h2c4", "2 GB heap"), ("tune_oh2g1g_c4", "2 GB heap\n+ 1 GB off-heap")]
    use_book_style(2.7)
    fig, (a, b) = plt.subplots(1, 2, figsize=(6.3, 2.7))
    cols = [C["rose"], C["green"], C["rose"], C["green"]]
    fills = [C["rose_fill"], C["green_fill"], C["rose_fill"], C["green_fill"]]
    a.bar(range(4), [grid[k]["gc_ms"] / 1000 for k, _ in names], color=fills, edgecolor=cols, linewidth=1.2)
    b.bar(range(4), [grid[k]["seconds"] for k, _ in names], color=fills, edgecolor=cols, linewidth=1.2)
    for ax_, key, fmt in ((a, "gc_ms", "{:.2f}"), (b, "seconds", "{:g}")):
        for i, (k, _) in enumerate(names):
            v = grid[k][key] / (1000 if key == "gc_ms" else 1)
            ax_.text(i, v * 1.02, fmt.format(v), ha="center", va="bottom", fontsize=8.5, color=C["gray_ink"])
        ax_.set_xticks(range(4)); ax_.set_xticklabels([n for _, n in names], fontsize=7)
        ax_.grid(axis="x", visible=False)
    a.set_title("GC time (s), all tasks", fontsize=9.5); b.set_title("wall clock (s)", fontsize=9.5)
    a.set_ylim(0, max(grid[k]["gc_ms"] for k in grid) / 1000 * 1.2); b.set_ylim(0, max(grid[k]["seconds"] for k in grid) * 1.2)
    fig.tight_layout()
    save(fig, "offheap-gc")
