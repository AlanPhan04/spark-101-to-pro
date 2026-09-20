#!/usr/bin/env python3
"""Render unsaferow-layout.drawio -> ../images/unsaferow-layout.pdf."""
import os
from _drawio import render

HERE = os.path.dirname(os.path.abspath(__file__))
render(os.path.join(HERE, "unsaferow-layout.drawio"),
       os.path.join(HERE, os.pardir, "images", "unsaferow-layout.pdf"))
