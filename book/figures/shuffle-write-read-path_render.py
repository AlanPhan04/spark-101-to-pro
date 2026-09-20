#!/usr/bin/env python3
"""Render shuffle-write-read-path.drawio -> ../images/shuffle-write-read-path.pdf."""
import os
from _drawio import render

HERE = os.path.dirname(os.path.abspath(__file__))
render(os.path.join(HERE, "shuffle-write-read-path.drawio"),
       os.path.join(HERE, os.pardir, "images", "shuffle-write-read-path.pdf"))
