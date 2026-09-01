#!/usr/bin/env python3
"""Shared draw.io -> vector-PDF renderer for the book's figures.

draw.io desktop is not installed here, so instead of "open -> Export as -> PDF"
each figure is a hand-authored .drawio (mxfile XML) plus a one-line script that
calls render() below. This reads the .drawio and redraws it with matplotlib, so
the PDF always follows the source. Editing the diagram in the draw.io app and
re-running the script both work; the .drawio stays authoritative.

Supported subset (extend as figures need it):
  - vertices: rounded / plain rectangles, fillColor / strokeColor / fontColor,
    strokeWidth, dashed, opacity; labels with <b>, <br>, and per-span font-size;
    align=left|center, verticalAlign=top|middle, spacingLeft, spacingTop.
  - edges: straight connectors between two vertices (source/target ids) or
    between explicit sourcePoint/targetPoint; dashed; endArrow=none for a plain
    line; optional midpoint label; exitX/exitY/entryX/entryY fractional anchors.
"""
import html
import os
import re
import xml.etree.ElementTree as ET

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

# draw.io renders Helvetica; Arial is the closest face on Windows.
plt.rcParams["font.family"] = ["Arial", "DejaVu Sans"]
plt.rcParams["pdf.fonttype"] = 42  # embed as TrueType, not Type 3

LINE_H = 17.5   # px per rendered text line at the base font size
FONT_SCALE = 1.18  # bump every label so text stays legible when the PDF is
                   # scaled to \linewidth in the book
CANVAS_DPI = 66.0  # < 72 shrinks the canvas in inches, enlarging text relative
                   # to the page once LaTeX scales the figure to the text width


def _style(s):
    d = {}
    for part in (s or "").split(";"):
        if "=" in part:
            k, v = part.split("=", 1)
            d[k] = v
        elif part:
            d[part] = "1"
    return d


def _label_lines(value, base=12):
    """One draw.io HTML label -> [(text, size, bold), ...].

    A font-size set inside a <span> persists across the <br>s it wraps and
    reverts to `base` after </span>.
    """
    if not value:
        return []
    value = value.replace("&#10;", "<br>")
    out = []
    cur = base
    for chunk in re.split(r"<br\s*/?>", value):
        bold = "<b>" in chunk or "<b " in chunk
        m = re.search(r"font-size:\s*(\d+)px", chunk)
        if m:
            cur = int(m.group(1))
        text = html.unescape(re.sub(r"<[^>]+>", "", chunk)).strip()
        out.append((text, cur, bold))
        if "</span>" in chunk:
            cur = base
    return out


def _draw_label(ax, x, y, w, h, value, st, z=5):
    lines = _label_lines(value)
    if not lines:
        return
    steps = [LINE_H * (1.18 if b else 1.0) for _, _, b in lines]
    total = sum(steps)
    left = st.get("align") == "left"
    top = st.get("verticalAlign") == "top"
    tx = x + float(st.get("spacingLeft", 12)) if left else x + w / 2.0
    ha = "left" if left else "center"
    if top:
        cy = y + float(st.get("spacingTop", 8)) + steps[0] / 2.0
    else:
        cy = y + h / 2.0 - total / 2.0 + steps[0] / 2.0
    color = _norm_color(st.get("fontColor"), "#1a1a1a")
    for (text, size, bold), step in zip(lines, steps):
        if text:
            ax.text(tx, cy, text, fontsize=size * 0.82 * FONT_SCALE, ha=ha, va="center",
                    zorder=z, color=color,
                    fontweight="bold" if bold else "normal")
        cy += step


def _norm_color(v, default):
    if not v or v.lower() == "none":
        return "none" if v and v.lower() == "none" else default
    return v if v.startswith("#") else "#" + v


def _anchor(box, frac):
    x, y, w, h = box
    fx, fy = frac
    return x + fx * w, y + fy * h


def _draw_vertex(ax, box, cell, z=4):
    from matplotlib.patches import FancyBboxPatch
    x, y, w, h = box
    st = _style(cell.get("style"))
    if "text" in st and st.get("fillColor", "none").lower() in ("none", ""):
        _draw_label(ax, x, y, w, h, cell.get("value"), st, z=z + 1)
        return
    rounded = st.get("rounded", "0") == "1" or "ellipse" in st
    boxstyle = "round,pad=0,rounding_size=8" if rounded else "square,pad=0"
    alpha = float(st.get("opacity", 100)) / 100.0
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h, boxstyle=boxstyle,
        linewidth=float(st.get("strokeWidth", 1.4)),
        edgecolor=_norm_color(st.get("strokeColor"), "#333333"),
        facecolor=_norm_color(st.get("fillColor"), "#ffffff"),
        alpha=alpha,
        linestyle=(0, (5, 3)) if st.get("dashed") == "1" else "solid",
        mutation_aspect=1, zorder=z))
    _draw_label(ax, x, y, w, h, cell.get("value"), st, z=z + 1)


def render(src, out):
    """Render mxfile at `src` to a vector PDF at `out`."""
    model = ET.parse(src).getroot().find("diagram").find("mxGraphModel")
    W, H = int(model.get("pageWidth")), int(model.get("pageHeight"))
    cells = model.find("root").findall("mxCell")

    geo = {}
    for c in cells:
        g = c.find("mxGeometry")
        if c.get("vertex") == "1" and g is not None:
            geo[c.get("id")] = tuple(float(g.get(k, 0)) for k in ("x", "y", "width", "height"))

    fig, ax = plt.subplots(figsize=(W / CANVAS_DPI, H / CANVAS_DPI))
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)  # draw.io y grows downward
    ax.axis("off")
    fig.subplots_adjust(0, 0, 1, 1)

    def is_container(c):
        return "container=1" in (c.get("style") or "")

    # background pass: container vertices, so edges can sit on top of their fill
    for c in cells:
        if c.get("vertex") == "1" and is_container(c):
            _draw_vertex(ax, geo[c.get("id")], c, z=1)

    # edges next, so leaf boxes sit on top of connector ends
    for c in cells:
        if c.get("edge") != "1":
            continue
        st = _style(c.get("style"))
        g = c.find("mxGeometry")
        src_id, tgt_id = c.get("source"), c.get("target")
        p0 = p1 = None
        if src_id in geo and tgt_id in geo:
            b0, b1 = geo[src_id], geo[tgt_id]
            if "exitX" in st:
                p0 = _anchor(b0, (float(st["exitX"]), float(st.get("exitY", 0.5))))
            if "entryX" in st:
                p1 = _anchor(b1, (float(st["entryX"]), float(st.get("entryY", 0.5))))
            c0 = (b0[0] + b0[2] / 2, b0[1] + b0[3] / 2)
            c1 = (b1[0] + b1[2] / 2, b1[1] + b1[3] / 2)
            if p0 is None:
                p0 = _clip(c0, c1, b0)
            if p1 is None:
                p1 = _clip(c1, c0, b1)
        elif g is not None:
            sp, tp = g.find("mxPoint[@as='sourcePoint']"), g.find("mxPoint[@as='targetPoint']")
            if sp is not None and tp is not None:
                p0 = (float(sp.get("x")), float(sp.get("y")))
                p1 = (float(tp.get("x")), float(tp.get("y")))
        if p0 is None or p1 is None:
            continue
        head = "" if st.get("endArrow") == "none" else "|>"
        tail = "<|" if st.get("startArrow") not in (None, "none") else ""
        arrow = f"{tail}-{head}" if (tail or head) else "-"
        ax.add_patch(FancyArrowPatch(
            p0, p1, arrowstyle=arrow, mutation_scale=13,
            linewidth=float(st.get("strokeWidth", 1.4)),
            color=_norm_color(st.get("strokeColor"), "#555555"),
            linestyle=(0, (5, 3)) if st.get("dashed") == "1" else "solid",
            shrinkA=0, shrinkB=0, zorder=3, joinstyle="round"))
        if c.get("value"):
            mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
            ax.text(mx, my - 6, html.unescape(re.sub(r"<[^>]+>", "", c.get("value"))),
                    fontsize=10, ha="center", va="center", zorder=6,
                    color="#333333",
                    bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none"))

    # foreground pass: every non-container vertex
    for c in cells:
        if c.get("vertex") == "1" and not is_container(c):
            _draw_vertex(ax, geo[c.get("id")], c)

    os.makedirs(os.path.dirname(out), exist_ok=True)
    fig.savefig(out, format="pdf", bbox_inches="tight", pad_inches=0.05,
                metadata={"CreationDate": None})
    plt.close(fig)
    print("wrote", os.path.relpath(out, os.path.dirname(src)))


def _clip(inside, toward, box):
    """Point on `box`'s border on the segment from its centre toward `toward`."""
    x, y, w, h = box
    cx, cy = inside
    dx, dy = toward[0] - cx, toward[1] - cy
    if dx == 0 and dy == 0:
        return inside
    tx = float("inf") if dx == 0 else (w / 2) / abs(dx)
    ty = float("inf") if dy == 0 else (h / 2) / abs(dy)
    t = min(tx, ty)
    return cx + dx * t, cy + dy * t
