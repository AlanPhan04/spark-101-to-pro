#!/usr/bin/env python3
"""Render dsv2-write-protocol.drawio -> ../images/dsv2-write-protocol.pdf."""
import os
from _drawio import render

HERE = os.path.dirname(os.path.abspath(__file__))
render(os.path.join(HERE, "dsv2-write-protocol.drawio"),
       os.path.join(HERE, os.pardir, "images", "dsv2-write-protocol.pdf"))
