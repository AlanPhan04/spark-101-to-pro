#!/usr/bin/env python3
"""Render aqe-skew-split.drawio -> ../images/aqe-skew-split.pdf."""
import os
from _drawio import render

HERE = os.path.dirname(os.path.abspath(__file__))
render(os.path.join(HERE, "aqe-skew-split.drawio"),
       os.path.join(HERE, os.pardir, "images", "aqe-skew-split.pdf"))
