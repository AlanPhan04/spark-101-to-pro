#!/usr/bin/env python3
"""Render sequence-number-rule.drawio -> ../images/sequence-number-rule.pdf."""
import os
from _drawio import render

HERE = os.path.dirname(os.path.abspath(__file__))
render(os.path.join(HERE, "sequence-number-rule.drawio"),
       os.path.join(HERE, os.pardir, "images", "sequence-number-rule.pdf"))
