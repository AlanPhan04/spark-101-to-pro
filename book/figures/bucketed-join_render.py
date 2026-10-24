#!/usr/bin/env python3
"""Render bucketed-join.drawio -> ../images/bucketed-join.pdf."""
import os
from _drawio import render

HERE = os.path.dirname(os.path.abspath(__file__))
render(os.path.join(HERE, "bucketed-join.drawio"),
       os.path.join(HERE, os.pardir, "images", "bucketed-join.pdf"))
