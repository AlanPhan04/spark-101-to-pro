#!/usr/bin/env python3
"""Render cow-vs-mor.drawio -> ../images/cow-vs-mor.pdf."""
import os
from _drawio import render

HERE = os.path.dirname(os.path.abspath(__file__))
render(os.path.join(HERE, "cow-vs-mor.drawio"),
       os.path.join(HERE, os.pardir, "images", "cow-vs-mor.pdf"))
