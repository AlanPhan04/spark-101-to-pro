#!/usr/bin/env python3
"""Render ui-diagnostic-funnel.drawio -> ../images/ui-diagnostic-funnel.pdf."""
import os
from _drawio import render

HERE = os.path.dirname(os.path.abspath(__file__))
render(os.path.join(HERE, "ui-diagnostic-funnel.drawio"),
       os.path.join(HERE, os.pardir, "images", "ui-diagnostic-funnel.pdf"))
