#!/usr/bin/env python3
"""Render iceberg-metadata-tree.drawio -> ../images/iceberg-metadata-tree.pdf."""
import os
from _drawio import render

HERE = os.path.dirname(os.path.abspath(__file__))
render(os.path.join(HERE, "iceberg-metadata-tree.drawio"),
       os.path.join(HERE, os.pardir, "images", "iceberg-metadata-tree.pdf"))
