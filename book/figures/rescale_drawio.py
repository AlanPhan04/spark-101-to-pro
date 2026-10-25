#!/usr/bin/env python3
"""Rescale a legacy .drawio figure to the book's legibility rule (pageWidth 640, fontSize >= 13).

    python rescale_drawio.py <slug> [ky]

Geometry is scaled by s = 640 / pageWidth horizontally and by s * ky vertically (default ky 1.45) so that the
larger text, which wraps in narrower boxes, still fits. Fonts are raised to 13. Review the render afterwards:
nodes whose text still overflows need their label shortened by hand.
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
slug = sys.argv[1]
ky = float(sys.argv[2]) if len(sys.argv) > 2 else 1.45
path = os.path.join(HERE, slug + ".drawio")
tree = ET.parse(path)
model = tree.getroot().find(".//mxGraphModel")
pw = float(model.get("pageWidth"))
ph = float(model.get("pageHeight"))
s = 640.0 / pw
sx, sy = s, s * ky
model.set("pageWidth", "640")
model.set("pageHeight", str(int(ph * sy)))
for g in model.iter("mxGeometry"):
    for k, f in (("x", sx), ("width", sx), ("y", sy), ("height", sy)):
        if g.get(k) is not None:
            g.set(k, str(round(float(g.get(k)) * f, 1)))
for p in model.iter("mxPoint"):
    for k, f in (("x", sx), ("y", sy)):
        if p.get(k) is not None:
            p.set(k, str(round(float(p.get(k)) * f, 1)))
for c in model.iter("mxCell"):
    st = c.get("style")
    if st is None:
        continue
    if "fontSize=" in st:
        st = re.sub(r"fontSize=\d+", "fontSize=13", st)
    elif c.get("vertex") == "1":
        st += "fontSize=13;"
    c.set("style", st)
tree.write(path, encoding="utf-8", xml_declaration=False)
print(f"{slug}: scale {s:.3f}, ky {ky}, page 640 x {int(ph * sy)}")
