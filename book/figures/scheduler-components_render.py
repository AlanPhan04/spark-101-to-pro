#!/usr/bin/env python3
"""Render scheduler-components.drawio -> ../images/scheduler-components.pdf."""
import os
from _drawio import render

HERE = os.path.dirname(os.path.abspath(__file__))
render(os.path.join(HERE, "scheduler-components.drawio"),
       os.path.join(HERE, os.pardir, "images", "scheduler-components.pdf"))
