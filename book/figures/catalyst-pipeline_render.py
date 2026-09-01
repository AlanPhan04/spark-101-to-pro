#!/usr/bin/env python3
"""Render catalyst-pipeline.drawio -> ../images/catalyst-pipeline.pdf."""
import os
from _drawio import render

HERE = os.path.dirname(os.path.abspath(__file__))
render(os.path.join(HERE, "catalyst-pipeline.drawio"),
       os.path.join(HERE, os.pardir, "images", "catalyst-pipeline.pdf"))
