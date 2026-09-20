#!/usr/bin/env python3
"""Render join-strategies.drawio -> ../images/join-strategies.pdf."""
import os
from _drawio import render

HERE = os.path.dirname(os.path.abspath(__file__))
render(os.path.join(HERE, "join-strategies.drawio"),
       os.path.join(HERE, os.pardir, "images", "join-strategies.pdf"))
