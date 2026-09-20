#!/usr/bin/env python3
"""Render catalog-commit-race.drawio -> ../images/catalog-commit-race.pdf."""
import os
from _drawio import render

HERE = os.path.dirname(os.path.abspath(__file__))
render(os.path.join(HERE, "catalog-commit-race.drawio"),
       os.path.join(HERE, os.pardir, "images", "catalog-commit-race.pdf"))
