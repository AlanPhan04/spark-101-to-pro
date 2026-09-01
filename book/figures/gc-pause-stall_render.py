#!/usr/bin/env python3
"""Render gc-pause-stall.drawio -> ../images/gc-pause-stall.pdf."""
import os
from _drawio import render

HERE = os.path.dirname(os.path.abspath(__file__))
render(os.path.join(HERE, "gc-pause-stall.drawio"),
       os.path.join(HERE, os.pardir, "images", "gc-pause-stall.pdf"))
