#!/usr/bin/env python3
"""Render microbatch-commit-loop.drawio -> ../images/microbatch-commit-loop.pdf."""
import os
from _drawio import render

HERE = os.path.dirname(os.path.abspath(__file__))
render(os.path.join(HERE, "microbatch-commit-loop.drawio"),
       os.path.join(HERE, os.pardir, "images", "microbatch-commit-loop.pdf"))
