#!/usr/bin/env python3
"""Render aqe-coalesce.drawio -> ../images/aqe-coalesce.pdf."""
import os
from _drawio import render

HERE = os.path.dirname(os.path.abspath(__file__))
render(os.path.join(HERE, "aqe-coalesce.drawio"),
       os.path.join(HERE, os.pardir, "images", "aqe-coalesce.pdf"))
