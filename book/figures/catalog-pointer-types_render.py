#!/usr/bin/env python3
"""Render catalog-pointer-types.drawio -> ../images/catalog-pointer-types.pdf."""
import os
from _drawio import render

HERE = os.path.dirname(os.path.abspath(__file__))
render(os.path.join(HERE, "catalog-pointer-types.drawio"),
       os.path.join(HERE, os.pardir, "images", "catalog-pointer-types.pdf"))
