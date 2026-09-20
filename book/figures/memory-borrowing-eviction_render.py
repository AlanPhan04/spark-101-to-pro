#!/usr/bin/env python3
"""Render memory-borrowing-eviction.drawio -> ../images/memory-borrowing-eviction.pdf."""
import os
from _drawio import render

HERE = os.path.dirname(os.path.abspath(__file__))
render(os.path.join(HERE, "memory-borrowing-eviction.drawio"),
       os.path.join(HERE, os.pardir, "images", "memory-borrowing-eviction.pdf"))
