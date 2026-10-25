#!/usr/bin/env python3
"""Chapter 3 measured figures (lab/exp_jvm.py, exp_memory.py, ser2.scala, exp_gc.sh)."""
import json
import os

import matplotlib.pyplot as plt

from bookplot import C, save, use_book_style

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
w = json.load(open(os.path.join(D, "jvm_warmup.json")))
use_book_style(2.6)
fig, ax = plt.subplots(figsize=(6.3, 2.6))
ax.bar(range(len(w)), w, color=[C["rose_fill"]] + [C["green_fill"]] * (len(w) - 1), edgecolor=[C["rose"]] + [C["green"]] * (len(w) - 1), linewidth=1.2)
for i, v in enumerate(w):
    ax.text(i, v + 0.1, f"{v:g}", ha="center", fontsize=8.5, color=C["gray_ink"])
ax.set_xticks(range(len(w))); ax.set_xticklabels([str(i + 1) for i in range(len(w))])
ax.set_xlabel("run number of the same query in one fresh JVM"); ax.set_ylabel("seconds"); ax.grid(axis="x", visible=False)
fig.tight_layout(); save(fig, "jit-warmup")

o = json.load(open(os.path.join(D, "jvm_objects.json")))
use_book_style(2.7)
fig, (a, b) = plt.subplots(1, 2, figsize=(6.3, 2.7))
a.bar([0, 1], [o["int_array"] / 1e6, o["boxed_list"] / 1e6], color=[C["green_fill"], C["rose_fill"]], edgecolor=[C["green"], C["rose"]], linewidth=1.2)
for i, v in enumerate([o["int_array"] / 1e6, o["boxed_list"] / 1e6]):
    a.text(i, v + 0.4, f"{v:.1f} MB", ha="center", fontsize=8.5, color=C["gray_ink"])
a.set_xticks([0, 1]); a.set_xticklabels(["int[1M]", "List<Integer>\n(1M)"], fontsize=8.5); a.set_title("heap size of 1M integers (5.2×)", fontsize=9)
a.set_ylim(0, 24); a.grid(axis="x", visible=False)
vals = [o["java_each"] / o["n"], o["kryo_each"] / o["n"], o["java_array"] / o["n"], o["kryo_array"] / o["n"]]
b.bar(range(4), vals, color=[C["rose_fill"], C["green_fill"]] * 2, edgecolor=[C["rose"], C["green"]] * 2, linewidth=1.2)
for i, v in enumerate(vals):
    b.text(i, v + 5, f"{v:.0f}", ha="center", fontsize=8.5, color=C["gray_ink"])
b.set_xticks(range(4)); b.set_xticklabels(["Java\nper object", "Kryo\nper object", "Java\none array", "Kryo\none array"], fontsize=8)
b.set_title("bytes per 5-field record", fontsize=9); b.set_ylim(0, 340); b.grid(axis="x", visible=False)
fig.tight_layout(); save(fig, "serialization-size")

g = json.load(open(os.path.join(D, "jvm_gc.json")))
names = list(g)
use_book_style(2.7)
fig, axes = plt.subplots(1, 3, figsize=(6.3, 2.7))
cols = [C["blue"], C["orange"], C["purple"]]
fills = [C["blue_fill"], C["orange_fill"], C["purple_fill"]]
for ax, key, title, fmt in ((axes[0], "wall", "wall clock (s)", "{:g}"), (axes[1], "ui_gc_s", "GC time in task metrics (s)", "{:.1f}"), (axes[2], "pause_max_ms", "longest pause (ms)", "{:g}")):
    vals = [g[n][key] if g[n][key] is not None else 0 for n in names]
    ax.bar(range(3), vals, color=fills, edgecolor=cols, linewidth=1.2)
    for i, n in enumerate(names):
        ax.text(i, vals[i] + max(vals) * 0.03, fmt.format(vals[i]) if g[n][key] is not None else "n/a", ha="center", fontsize=8.5, color=C["gray_ink"])
    ax.set_xticks(range(3)); ax.set_xticklabels(names, fontsize=8); ax.set_title(title, fontsize=8.5); ax.set_ylim(0, max(vals) * 1.2); ax.grid(axis="x", visible=False)
fig.tight_layout(); save(fig, "gc-collectors-measured")
