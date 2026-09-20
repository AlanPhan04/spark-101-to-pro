#!/usr/bin/env python3
"""Render pruning-layers-funnel.drawio -> ../images/pruning-layers-funnel.pdf."""
import os
from _drawio import render

HERE = os.path.dirname(os.path.abspath(__file__))
render(os.path.join(HERE, "pruning-layers-funnel.drawio"),
       os.path.join(HERE, os.pardir, "images", "pruning-layers-funnel.pdf"))
