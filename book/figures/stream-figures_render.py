#!/usr/bin/env python3
"""Chapter 16 measured figures (lab/exp_stream.py; data in figures/data/stream_*.json).

  stream-cadence     files, average file size and manifests per 100 s at three trigger intervals
  state-growth       streaming state rows over time with and without a watermark
  output-modes       rows emitted per micro-batch under append, update, complete
  kill-restart       records per snapshot across a killed and restarted query
"""
import json
import os

import matplotlib.pyplot as plt

from bookplot import C, save, use_book_style

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, "data")


def load(n):
    return json.load(open(os.path.join(D, n)))


# --- cadence ----------------------------------------------------------------------------------------------------------------------------------
runs = [load(f"stream_cad_{t}.json") for t in (2, 10, 30)]
use_book_style(2.8)
fig, axes = plt.subplots(1, 3, figsize=(6.3, 2.8))
labels = [f"{r['trigger_s']} s" for r in runs]
for ax, key, title, fmt in ((axes[0], "files", "data files in 100 s", "{:g}"), (axes[1], "avg_file_kb", "average file (KB)", "{:,.0f}"), (axes[2], "manifests", "manifests in 100 s", "{:g}")):
    vals = [float(r[key]) for r in runs]
    ax.bar(range(3), vals, color=[C["rose_fill"], C["blue_fill"], C["green_fill"]], edgecolor=[C["rose"], C["blue"], C["green"]], linewidth=1.2)
    for i, v in enumerate(vals):
        ax.text(i, v + max(vals) * 0.02, fmt.format(v), ha="center", fontsize=8.5, color=C["gray_ink"])
    ax.set_xticks(range(3)); ax.set_xticklabels(labels); ax.set_xlabel("trigger interval")
    ax.set_title(title, fontsize=9.5); ax.set_ylim(0, max(vals) * 1.18); ax.grid(axis="x", visible=False)
fig.tight_layout()
save(fig, "stream-cadence")

# --- state growth -----------------------------------------------------------------------------------------------------------------------------
use_book_style(2.7)
fig, ax = plt.subplots(figsize=(6.3, 2.7))
for key, label, color in (("none", "no watermark", C["rose"]), ("watermark", "watermark 10 s", C["green"])):
    s = load(f"stream_state_{key}.json")
    ax.plot([x["t"] for x in s], [x["state_rows"] for x in s], color=color, marker="o", markersize=3.5, label=label)
ax.set_xlabel("seconds since the query started"); ax.set_ylabel("state rows"); ax.legend(loc="upper left")
fig.tight_layout()
save(fig, "state-growth")

# --- output modes -----------------------------------------------------------------------------------------------------------------------------
m = load("stream_modes.json")
use_book_style(2.7)
fig, ax = plt.subplots(figsize=(6.3, 2.7))
for key, color in (("complete", C["rose"]), ("update", C["blue"]), ("append", C["green"])):
    ax.plot(range(len(m[key])), m[key], color=color, marker="o", markersize=3.5, label=key)
ax.set_xlabel("micro-batch"); ax.set_ylabel("rows emitted by the batch"); ax.legend(loc="upper left")
fig.tight_layout()
save(fig, "output-modes")

# --- kill and restart --------------------------------------------------------------------------------------------------------------------------
k = load("stream_kill_check.json")
use_book_style(2.7)
fig, ax = plt.subplots(figsize=(6.3, 2.7))
eps = [int(s["epoch"]) for s in k["snapshots"]]
recs = [int(s["records"] or 0) / 1000 for s in k["snapshots"]]
cols = [C["orange"] if e == 19 else C["blue"] for e in eps]
fills = [C["orange_fill"] if e == 19 else C["blue_fill"] for e in eps]
ax.bar(eps, recs, color=fills, edgecolor=cols, linewidth=1.0)
ax.annotate("first batch after the restart\ncatches up on the downtime", xy=(19, 20), xytext=(21, 16), fontsize=8.5, color=C["orange_ink"], arrowprops=dict(arrowstyle="->", color=C["orange_ink"], lw=1))
ax.set_ylim(0, 23); ax.set_xlabel("epoch (micro-batch) id, one Iceberg snapshot each"); ax.set_ylabel("records committed (thousands)")
ax.grid(axis="x", visible=False)
fig.tight_layout()
save(fig, "kill-restart")

# --- state providers -------------------------------------------------------------------------------------------------------------------------------
use_book_style(2.7)
fig, (a, b) = plt.subplots(1, 2, figsize=(6.3, 2.7))
for key, label, color in (("default", "default provider", C["rose"]), ("rocksdb", "RocksDB provider", C["green"])):
    s = load(f"stream_big_{key}.json")
    a.plot([x["state_rows"] / 1e3 for x in s], [x["state_bytes"] / 1e6 for x in s], color=color, marker="o", markersize=3, label=label)
    b.plot([x["t"] for x in s[2:]], [x["batch_ms"] for x in s[2:]], color=color, marker="o", markersize=3, label=label)
a.set_xlabel("state rows (thousands)"); a.set_ylabel("memory reported by the state store (MB)"); a.legend(loc="upper left", fontsize=8)
b.set_xlabel("seconds since the query started"); b.set_ylabel("micro-batch duration (ms)"); b.set_ylim(0, 1800)
fig.tight_layout(); save(fig, "state-providers")
