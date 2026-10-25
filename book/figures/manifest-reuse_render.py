#!/usr/bin/env python3
"""Render manifest-reuse.drawio -> ../images/manifest-reuse.pdf."""
import os
from _drawio import render

HERE = os.path.dirname(os.path.abspath(__file__))
render(os.path.join(HERE, "manifest-reuse.drawio"),
       os.path.join(HERE, os.pardir, "images", "manifest-reuse.pdf"))
