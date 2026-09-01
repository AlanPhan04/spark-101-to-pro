#!/usr/bin/env python3
"""Render executor-memory-model.drawio -> ../images/executor-memory-model.pdf."""
import os
from _drawio import render

HERE = os.path.dirname(os.path.abspath(__file__))
render(os.path.join(HERE, "executor-memory-model.drawio"),
       os.path.join(HERE, os.pardir, "images", "executor-memory-model.pdf"))
