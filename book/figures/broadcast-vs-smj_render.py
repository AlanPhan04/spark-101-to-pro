#!/usr/bin/env python3
"""Render broadcast-vs-smj.drawio -> ../images/broadcast-vs-smj.pdf."""
import os
from _drawio import render

HERE = os.path.dirname(os.path.abspath(__file__))
render(os.path.join(HERE, "broadcast-vs-smj.drawio"),
       os.path.join(HERE, os.pardir, "images", "broadcast-vs-smj.pdf"))
