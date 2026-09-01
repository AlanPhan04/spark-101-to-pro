#!/usr/bin/env python3
"""Render application-topology.drawio -> ../images/application-topology.pdf."""
import os
from _drawio import render

HERE = os.path.dirname(os.path.abspath(__file__))
render(os.path.join(HERE, "application-topology.drawio"),
       os.path.join(HERE, os.pardir, "images", "application-topology.pdf"))
