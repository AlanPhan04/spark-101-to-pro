#!/usr/bin/env python3
"""Render join-selection-flow.drawio -> ../images/join-selection-flow.pdf."""
import os
from _drawio import render

HERE = os.path.dirname(os.path.abspath(__file__))
render(os.path.join(HERE, "join-selection-flow.drawio"),
       os.path.join(HERE, os.pardir, "images", "join-selection-flow.pdf"))
