#!/usr/bin/env python3
"""Render dpp-flow.drawio -> ../images/dpp-flow.pdf."""
import os
from _drawio import render

HERE = os.path.dirname(os.path.abspath(__file__))
render(os.path.join(HERE, "dpp-flow.drawio"),
       os.path.join(HERE, os.pardir, "images", "dpp-flow.pdf"))
