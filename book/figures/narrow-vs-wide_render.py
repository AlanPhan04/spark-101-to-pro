#!/usr/bin/env python3
"""Render narrow-vs-wide.drawio -> ../images/narrow-vs-wide.pdf."""
import os
from _drawio import render

HERE = os.path.dirname(os.path.abspath(__file__))
render(os.path.join(HERE, "narrow-vs-wide.drawio"),
       os.path.join(HERE, os.pardir, "images", "narrow-vs-wide.pdf"))
