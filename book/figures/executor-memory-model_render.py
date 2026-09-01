#!/usr/bin/env python3
"""Render executor-memory-model.drawio to a vector PDF.

draw.io desktop is not installed here, so the usual "open -> Export as -> PDF"
route is unavailable. This reads the .drawio and redraws it with matplotlib, so
the PDF always follows whatever the .drawio currently says. Editing the diagram
in the draw.io app and re-running this script (or exporting from the app) both
work; the .drawio stays authoritative.

Understands the subset the figure uses: rounded/plain rectangles with an HTML
label, fill/stroke/dashed styles, per-span font sizes, and <b>/<br> in labels.
"""
import html
import os
import re
import xml.etree.ElementTree as ET

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "executor-memory-model.drawio")
OUT = os.path.join(HERE, os.pardir, "images", "executor-memory-model.pdf")

# draw.io renders Helvetica; Arial is the closest face on Windows.
plt.rcParams["font.family"] = ["Arial", "DejaVu Sans"]
plt.rcParams["pdf.fonttype"] = 42  # embed as TrueType, not Type 3

LINE_H = 15.5  # px per rendered text line at the base font size


def style_of(s):
    d = {}
    for part in (s or "").split(";"):
        if "=" in part:
            k, v = part.split("=", 1)
            d[k] = v
        elif part:
            d[part] = "1"
    return d


def parse_label(value):
    """One draw.io HTML label -> [(text, size, bold), ...] lines."""
    if not value:
        return []
    value = value.replace("&#10;", "<br>")
    out = []
    for chunk in re.split(r"<br\s*/?>", value):
        bold = "<b>" in chunk
        m = re.search(r"font-size:\s*(\d+)px", chunk)
        size = int(m.group(1)) if m else 11
        text = html.unescape(re.sub(r"<[^>]+>", "", chunk)).strip()
        out.append((text, size, bold))
    return out


def main():
    model = ET.parse(SRC).getroot().find("diagram").find("mxGraphModel")
    W, H = int(model.get("pageWidth")), int(model.get("pageHeight"))
    cells = model.find("root").findall("mxCell")

    fig, ax = plt.subplots(figsize=(W / 72.0, H / 72.0))
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)  # draw.io y grows downward
    ax.axis("off")
    fig.subplots_adjust(0, 0, 1, 1)

    for c in cells:
        if c.get("vertex") != "1":
            continue
        g = c.find("mxGeometry")
        if g is None:
            continue
        x, y, w, h = (float(g.get(k)) for k in ("x", "y", "width", "height"))
        st = style_of(c.get("style"))

        rounded = st.get("rounded", "0") == "1"
        boxstyle = "round,pad=0,rounding_size=6" if rounded else "square,pad=0"
        ax.add_patch(FancyBboxPatch(
            (x, y), w, h, boxstyle=boxstyle,
            linewidth=float(st.get("strokeWidth", 1)),
            edgecolor=st.get("strokeColor", "#000000"),
            facecolor=st.get("fillColor", "#ffffff"),
            linestyle=(0, (4, 3)) if st.get("dashed") == "1" else "solid",
            mutation_aspect=1, zorder=2))

        lines = parse_label(c.get("value"))
        if not lines:
            continue
        total = sum(LINE_H * (1.15 if b else 1.0) for _, _, b in lines)
        top_align = st.get("verticalAlign") == "top"
        if top_align:
            cy = y + float(st.get("spacingTop", 6)) + LINE_H * 0.4
        else:
            cy = y + h / 2.0 - total / 2.0 + LINE_H * 0.4
        for text, size, bold in lines:
            step = LINE_H * (1.15 if bold else 1.0)
            if text:
                ax.text(x + w / 2.0, cy, text, fontsize=size * 0.92,
                        ha="center", va="center", zorder=3,
                        color=st.get("fontColor", "#000000"),
                        fontweight="bold" if bold else "normal")
            cy += step

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    fig.savefig(OUT, format="pdf", bbox_inches="tight", pad_inches=0.04)
    plt.close(fig)
    print("wrote", os.path.relpath(OUT, HERE))


if __name__ == "__main__":
    main()
