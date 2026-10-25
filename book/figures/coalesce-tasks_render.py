#!/usr/bin/env python3
"""coalesce-tasks.pdf: reduce-stage task counts, formula prediction against the lab's measurement.

Prediction: target = max(min(shuffle_bytes / 40, advisory), 1 MB); tasks ~ shuffle_bytes / target.
Observed: stage task counts from the Spark event log (lab/exp_aqe.py, exp_aqe2.py).
"""
import matplotlib.pyplot as plt
import numpy as np

from bookplot import C, save, use_book_style

LABELS = ["AQE off", "baseline", "pF off", "512 MB\nshuffle", "512 MB\nadvisory 16", "512 MB\nadvisory 4", "512 MB\npF off"]
PRED = [2000, 40, 2, 40, 40, 128, 8]
OBS = [2000, 40, 2, 41, 41, 134, 9]

use_book_style(3.0)
fig, ax = plt.subplots()
x = np.arange(len(LABELS))
w = 0.38
ax.bar(x - w / 2, PRED, w, color=C["blue_fill"], edgecolor=C["blue"], linewidth=1.0, label="formula")
ax.bar(x + w / 2, OBS, w, color=C["green_fill"], edgecolor=C["green"], linewidth=1.0, label="measured")
ax.set_yscale("log")
ax.set_ylim(1, 5000)
ax.set_xticks(x)
ax.set_xticklabels(LABELS, fontsize=8.5)
ax.set_ylabel("reduce-stage tasks (log scale)")
for xi, (p, o) in enumerate(zip(PRED, OBS)):
    ax.text(xi + w / 2, o * 1.15, str(o), ha="center", fontsize=8.5, color=C["green_ink"])
ax.legend(loc="upper right")
ax.grid(axis="x", visible=False)
fig.tight_layout()
save(fig, "coalesce-tasks")
