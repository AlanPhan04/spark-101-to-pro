#!/usr/bin/env python3
"""Chapter 19 measured figures (lab/exp_dsv2.py, exp_dsv2b.py).

  pushdown-rows-by-predicate  rows that leave the scan per WHERE shape; colour = does Spark keep a Filter above
  aggregate-pushdown          seconds and plan root for COUNT/MIN/MAX/SUM
"""
import json
import os

import matplotlib.pyplot as plt

from bookplot import C, save, use_book_style

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, "data")
a = json.load(open(os.path.join(D, "dsv2_results.json")))
b = json.load(open(os.path.join(D, "dsv2b_results.json")))
by = {r["predicate"]: r for r in a["pushdown"]}
by.update({r["predicate"]: r for r in b})
order = [
    ("one whole day (aligned)", "one whole day, aligned to the partition"),
    ("date(order_ts) = day", "date(order_ts) = a day"),
    ("one hour inside a day", "one hour inside a day"),
    ("partition AND data column", "that day AND order_total > 200"),
    ("partition OR data column", "that day OR product = hot"),
    ("range on data column", "order_total > 900 (above the maximum)"),
    ("equality on data column", "product_id = hot product"),
    ("IN list on data column", "customer_id IN (3 values)"),
    ("LIKE prefix", "product_id LIKE 'p00000%'"),
    ("CAST ts AS STRING", "CAST(order_ts AS STRING) range"),
    ("function on data column", "lower(product_id) = ..."),
    ("arithmetic on data column", "order_total * 2 > ..."),
    ("two columns compared", "promised_days < delivery_days"),
]
use_book_style(4.2)
fig, ax = plt.subplots(figsize=(6.3, 4.2))
ys = list(range(len(order)))[::-1]
for y, (key, label) in zip(ys, order):
    r = by[key]
    rows = (r["rows_out_of_scan"] or 0) / 1e6
    keep = r["filter_above_scan"]
    ax.barh(y, rows, color=C["rose_fill"] if keep else C["green_fill"], edgecolor=C["rose"] if keep else C["green"], linewidth=1.2)
    ax.text(rows + 0.5, y, f"{rows:.2f} M" if rows < 10 else f"{rows:.0f} M", va="center", fontsize=8.5, color=C["gray_ink"])
ax.set_yticks(ys); ax.set_yticklabels([l for _, l in order], fontsize=8.5)
ax.set_xlim(0, 36); ax.set_xlabel("rows produced by the scan (of 30 M)")
ax.grid(axis="y", visible=False)
from matplotlib.patches import Patch
ax.legend(handles=[Patch(facecolor=C["green_fill"], edgecolor=C["green"], label="no Filter above the scan"),
                   Patch(facecolor=C["rose_fill"], edgecolor=C["rose"], label="Spark keeps a Filter")], loc="upper center", bbox_to_anchor=(0.4, -0.13), ncol=2, fontsize=8.5)
fig.tight_layout()
save(fig, "pushdown-rows-by-predicate")

ag = a["aggregates"]
use_book_style(2.7)
fig, ax = plt.subplots(figsize=(6.3, 2.7))
labels = [r["query"] for r in ag]
secs = [r["seconds"] for r in ag]
local = [r["root_leaf"] == "LocalTableScan" for r in ag]
xs = range(len(ag))
ax.bar(xs, secs, color=[C["green_fill"] if l else C["blue_fill"] for l in local], edgecolor=[C["green"] if l else C["blue"] for l in local], linewidth=1.2)
for x, s in zip(xs, secs):
    ax.text(x, s + 0.03, f"{s:g} s", ha="center", fontsize=8.5, color=C["gray_ink"])
ax.set_xticks(list(xs)); ax.set_xticklabels([l.replace(" ", "\n", 1) if len(l) > 14 else l for l in labels], fontsize=7.5)
ax.set_ylabel("seconds"); ax.set_ylim(0, 1.15); ax.grid(axis="x", visible=False)
ax.legend(handles=[Patch(facecolor=C["green_fill"], edgecolor=C["green"], label="answered from metadata (LocalTableScan)"),
                   Patch(facecolor=C["blue_fill"], edgecolor=C["blue"], label="data files scanned (BatchScan)")], loc="upper left", fontsize=8.5)
fig.tight_layout()
save(fig, "aggregate-pushdown")
