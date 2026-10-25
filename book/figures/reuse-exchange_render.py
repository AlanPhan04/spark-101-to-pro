#!/usr/bin/env python3
"""Render reuse-exchange.drawio -> ../images/reuse-exchange.pdf."""
import os
from _drawio import render

HERE = os.path.dirname(os.path.abspath(__file__))
render(os.path.join(HERE, "reuse-exchange.drawio"),
       os.path.join(HERE, os.pardir, "images", "reuse-exchange.pdf"))
