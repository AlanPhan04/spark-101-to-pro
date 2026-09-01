#!/usr/bin/env python3
"""Render job-stage-task.drawio -> ../images/job-stage-task.pdf."""
import os
from _drawio import render

HERE = os.path.dirname(os.path.abspath(__file__))
render(os.path.join(HERE, "job-stage-task.drawio"),
       os.path.join(HERE, os.pardir, "images", "job-stage-task.pdf"))
