#!/usr/bin/env python3
"""Render aqe-feedback-loop.drawio -> ../images/aqe-feedback-loop.pdf."""
import os
from _drawio import render

HERE = os.path.dirname(os.path.abspath(__file__))
render(os.path.join(HERE, "aqe-feedback-loop.drawio"),
       os.path.join(HERE, os.pardir, "images", "aqe-feedback-loop.pdf"))
