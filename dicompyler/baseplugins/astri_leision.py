import logging

logger = logging.getLogger("dicompyler.astri_leision")

import wx
from wx.lib.pubsub import pub
import pprint


def pluginProperties():
    """Properties of the plugin."""

    props = {}
    props["name"] = "Leision Analysis"
    props["description"] = "Leision Analysis"
    props["author"] = "ASTRI"
    props["version"] = 0.1
    props["plugin_type"] = "main"
    props["plugin_version"] = 1
    props["min_dicom"] = ["images"]
    props["recommended_dicom"] = []

    return props


def pluginLoader(parent):
    """Function to load the plugin."""
    print("Leision Analysis Loaded")
    panelTest = pluginTest(parent)
    return panelTest


class pluginTest(wx.Panel):
    """Test plugin to demonstrate dicompyler plugin system."""

    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)

        # Initialize the panel controls
        # self.patname = wx.StaticText(self, -1, "N/A", style=wx.ALIGN_CENTRE)
        self.patname = wx.TextCtrl(self, -1, "", style=wx.TE_MULTILINE)

        # Set up sizer for control placement
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.patname, 1, flag=wx.EXPAND | wx.ALL | wx.ALIGN_CENTRE, border=4)
        self.SetSizer(sizer)
        self.Layout()

        # Set up pubsub
        pub.subscribe(self.OnUpdatePatient, "patient.updated.raw_data")
        # pub.subscribe(self.OnUpdatePatient, "patient.updated.parsed_data")

    def OnUpdatePatient(self, msg):
        """Update and load the patient data."""

        logger.debug("msg.keys(%s), class(%s)", list(msg.keys()), type(msg).__name__)
        self.patname.AppendText(str(msg.keys()) + "\n")
        if "images" in msg:
            # raw_data
            image = msg["images"][0]
            logger.debug("class(%s)", type(image).__name__)
            logger.debug("class(%s)", type(image).__name__)
            self.patname.AppendText(pprint.pformat(image) + "\n")

        # Get the RT Structure Set DICOM dataset
        # rtss = msg.data["rtss"]
        # self.patname.SetLabel(rtss.PatientName)
