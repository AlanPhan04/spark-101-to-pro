#!/usr/bin/env python3
"""Render maintenance-order.drawio -> ../images/maintenance-order.pdf."""
import os
from _drawio import render

HERE = os.path.dirname(os.path.abspath(__file__))
render(os.path.join(HERE, "maintenance-order.drawio"),
       os.path.join(HERE, os.pardir, "images", "maintenance-order.pdf"))
