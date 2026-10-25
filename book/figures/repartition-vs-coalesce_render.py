#!/usr/bin/env python3
"""Render repartition-vs-coalesce.drawio -> ../images/repartition-vs-coalesce.pdf."""
import os
from _drawio import render

HERE = os.path.dirname(os.path.abspath(__file__))
render(os.path.join(HERE, "repartition-vs-coalesce.drawio"),
       os.path.join(HERE, os.pardir, "images", "repartition-vs-coalesce.pdf"))
