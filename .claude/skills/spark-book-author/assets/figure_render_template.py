#!/usr/bin/env python3
"""Render <slug>.drawio -> ../images/<slug>.pdf.

Copy to book/figures/<slug>_render.py and replace <slug> (same pattern as the
book's existing renderers; figures/build.ps1 picks it up automatically).
"""
import os
from _drawio import render

SLUG = "<slug>"
HERE = os.path.dirname(os.path.abspath(__file__))
render(os.path.join(HERE, f"{SLUG}.drawio"),
       os.path.join(HERE, os.pardir, "images", f"{SLUG}.pdf"))
