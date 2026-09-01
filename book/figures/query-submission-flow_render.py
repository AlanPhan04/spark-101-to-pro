#!/usr/bin/env python3
"""Render query-submission-flow.drawio -> ../images/query-submission-flow.pdf."""
import os
from _drawio import render

HERE = os.path.dirname(os.path.abspath(__file__))
render(os.path.join(HERE, "query-submission-flow.drawio"),
       os.path.join(HERE, os.pardir, "images", "query-submission-flow.pdf"))
