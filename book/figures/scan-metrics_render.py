#!/usr/bin/env python3
"""Render scan-metrics.drawio -> ../images/scan-metrics.pdf."""
import os
from _drawio import render

HERE = os.path.dirname(os.path.abspath(__file__))
render(os.path.join(HERE, "scan-metrics.drawio"),
       os.path.join(HERE, os.pardir, "images", "scan-metrics.pdf"))
