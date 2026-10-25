#!/usr/bin/env python3
"""Render metadata-tree-lab.drawio -> ../images/metadata-tree-lab.pdf."""
import os
from _drawio import render

HERE = os.path.dirname(os.path.abspath(__file__))
render(os.path.join(HERE, "metadata-tree-lab.drawio"),
       os.path.join(HERE, os.pardir, "images", "metadata-tree-lab.pdf"))
