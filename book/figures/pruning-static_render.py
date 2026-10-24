#!/usr/bin/env python3
"""Render pruning-static.drawio -> ../images/pruning-static.pdf."""
import os
from _drawio import render

HERE = os.path.dirname(os.path.abspath(__file__))
render(os.path.join(HERE, "pruning-static.drawio"),
       os.path.join(HERE, os.pardir, "images", "pruning-static.pdf"))
