#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 2dview.py
"""dicompyler plugin that displays images, structures and dose in 2D planes."""
# Copyright (c) 2009-2017 Aditya Panchal
# This file is part of dicompyler, released under a BSD license.
#    See the file license.txt included with this distribution, also
#    available at https://github.com/bastula/dicompyler/
#

import logging

logger = logging.getLogger("dicompyler.2dview")
import wx
from wx.xrc import XmlResource, XRCCTRL, XRCID
from pubsub import pub
from dicompyler.baseplugins.view2d import View2d
from dicompyler.baseplugins.view2d_slider import View2dSlider

"""
Later, it will be depricated and replaced by "2dview_slider.py"
"""


def pluginProperties():
    """Properties of the plugin."""

    props = {}
    props["name"] = "2D View"
    props["description"] = "Display image, structure and dose data in 2D"
    props["author"] = "Aditya Panchal"
    props["version"] = "0.5.0"
    props["plugin_type"] = "main"
    props["plugin_version"] = 1
    props["min_dicom"] = ["images"]
    props["recommended_dicom"] = ["images", "rtss", "rtdose"]

    return props


def pluginLoader(parent):
    """Function to load the plugin."""

    # previous view2d without slider
    # panelView2D = View2d(parent)

    # new view2d with a slider
    panelView2D = View2dSlider(parent)
    return panelView2D
