#!/usr/bin/env python3
"""Render aqe-broadcast-promotion.drawio -> ../images/aqe-broadcast-promotion.pdf."""
import os
from _drawio import render

HERE = os.path.dirname(os.path.abspath(__file__))
render(os.path.join(HERE, "aqe-broadcast-promotion.drawio"),
       os.path.join(HERE, os.pardir, "images", "aqe-broadcast-promotion.pdf"))
