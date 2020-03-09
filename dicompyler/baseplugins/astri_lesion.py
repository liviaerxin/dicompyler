import logging

logger = logging.getLogger("dicompyler.plugins.astri_leision")

import wx
from pubsub import pub
import pprint
import os, threading
from dicompyler import guiutil, util
import pydicom
from typing import List
import time
import json


def pluginProperties():
    """Properties of the plugin."""

    props = {}
    props["name"] = "Lesion Analysis"
    props["description"] = "Lesion Analysis"
    props["author"] = "ASTRI"
    props["version"] = 0.1
    props["plugin_type"] = "main"
    props["plugin_version"] = 1
    props["min_dicom"] = ["images"]
    props["recommended_dicom"] = []

    return props


def pluginLoader(parent):
    """Function to load the plugin."""
    print("Lesion Analysis Plugin Loaded")
    panelTest = pluginTest(parent)
    return panelTest


class pluginTest(wx.Panel):
    """Test plugin to demonstrate dicompyler plugin system."""

    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)

        # Initialize variables

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
        # self.patname.AppendText(str(msg.keys()) + "\n")
        files: List[str] = []
        if "images" in msg:
            # raw_data
            images = msg["images"]
            for image in images:
                if isinstance(image, pydicom.dataset.FileDataset):
                    files.append(image.filename)
                else:
                    print(f"unable to process the image: {type(image)}")

        self.OnUpdateAnalysis(files)

        pub.unsubscribe(self.OnUpdatePatient, "patient.updated.raw_data")

    def OnUpdateAnalysis(self, files: List[str]):
        """Analyze the lesion with given DICOM files

        Arguments:
            files {List[str]} -- a list of DICOM files, each value is expected to be the filepath
        """

        # Initialize the progress dialog
        dlgProgress = guiutil.get_progress_dialog(
            wx.GetApp().GetTopWindow(), "Analyzing Lesion..."
        )
        # Set up the queue so that the thread knows which item was added
        # self.queue = queue.Queue()
        # Initialize and start the background analyzing thread
        self.t = threading.Thread(
            target=self.analyze_files_thread,
            args=(files, dlgProgress.OnUpdateProgress),
        )
        self.t.start()
        # Show the progress dialog
        dlgProgress.ShowModal()
        dlgProgress.Destroy()

    def OnDestroy(self, evt):
        """Unbind to all events before the plugin is destroyed."""

        pub.unsubscribe(self.OnUpdatePatient, "patient.updated.raw_data")

    def mock_analyze_file(self, file: str):
        """mock analyze algorithm, process one file

        Arguments:
            file {str} -- [description]
        """
        time.sleep(0.01)

    def analyze_files_thread(self, files: List[str], progressFunc):
        length = len(files)

        for i, file in enumerate(files):
            wx.CallAfter(progressFunc, i, length, "Analyzing Lesion...")

            # TODO: replace with real analyzing algorithm
            self.mock_analyze_file(file)

        wx.CallAfter(progressFunc, length, length, "Done")

        # Mock analysis result
        result = None
        with open(util.GetResourcePath("lung_stats.json")) as f:
            result = json.load(f)

        pub.sendMessage("patient.updated.lesion_analysis", msg={"result": result})
