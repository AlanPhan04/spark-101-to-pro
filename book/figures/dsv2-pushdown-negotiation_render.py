#!/usr/bin/env python3
"""Render dsv2-pushdown-negotiation.drawio -> ../images/dsv2-pushdown-negotiation.pdf."""
import os
from _drawio import render

HERE = os.path.dirname(os.path.abspath(__file__))
render(os.path.join(HERE, "dsv2-pushdown-negotiation.drawio"),
       os.path.join(HERE, os.pardir, "images", "dsv2-pushdown-negotiation.pdf"))
