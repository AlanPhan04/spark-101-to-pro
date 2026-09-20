#!/usr/bin/env python3
"""Render partition-evolution.drawio -> ../images/partition-evolution.pdf."""
import os
from _drawio import render

HERE = os.path.dirname(os.path.abspath(__file__))
render(os.path.join(HERE, "partition-evolution.drawio"),
       os.path.join(HERE, os.pardir, "images", "partition-evolution.pdf"))
