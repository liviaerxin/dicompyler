import wx
import wx.lib.mixins.listctrl
from pubsub import pub

from typing import List
from random import randint
import json

from dicompyler import util


import logging, logging.handlers

logger = logging.getLogger("dicompyler.lesion_panel")


COLUMN = [
    {"label": "", "key": "type", "width": 150,},
    {"label": "Whole Lung", "key": "whole", "width": 120,},
    {"label": "Right Lung", "key": "right", "width": 120,},
    {"label": "Left Lung", "key": "left", "width": 120,},
]

TYPE_LABLES = {
    "volume": "Volume (cm3)",
    "density": "Density (HU)",
    "infection_volume": "Infection Volume",
    "infection_percentage": "Infection Percentage",
}


def pre_process_data(data: List):
    result = []

    # copy data
    for item in data:
        row = {}
        row["type"] = item["type"] if "type" in item else None
        row["whole"] = item["whole"] if "whole" in item else None
        row["left"] = item["left"] if "left" in item else None
        row["right"] = item["right"] if "right" in item else None

        result.append(row)

    return result


class SortedListCtrl(
    wx.ListCtrl, wx.lib.mixins.listctrl.ListCtrlAutoWidthMixin,
):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, wx.ID_ANY, style=wx.LC_REPORT)
        wx.lib.mixins.listctrl.ListCtrlAutoWidthMixin.__init__(self)

    def GetListCtrl(self):
        return self


class LungStatisticsPanel(wx.Panel):
    def __init__(self, parent, *args, **kwargs):
        wx.Panel.__init__(self, parent, *args, **kwargs)

        hbox = wx.BoxSizer(wx.HORIZONTAL)

        # TODO: Initialize data visulization view(does it need?)

        # Initialize data list control view
        self.list = SortedListCtrl(self)

        for i, col in enumerate(COLUMN):
            self.list.InsertColumn(i, col["label"], width=col["width"])

        # Font size
        # self.list.SetFont(wx.Font(wx.FontInfo(10)))

        # sizer
        hbox.Add(self.list, 1, wx.EXPAND)
        self.SetSizer(hbox)

        # Set up pubsub
        pub.subscribe(self.OnUpdateLesion, "lesion.loaded.analysis")

    def update_list(self, data):

        self.list.DeleteAllItems()

        self.items = pre_process_data(data)

        for i, item in enumerate(self.items):
            if item["type"] in TYPE_LABLES:
                label = TYPE_LABLES[item["type"]]
            else:
                label = item["type"]
            index = self.list.InsertItem(i, str(label))
            self.list.SetItem(index, 1, str(item["whole"]))
            self.list.SetItem(index, 2, str(item["right"]))
            self.list.SetItem(index, 3, str(item["left"]))

    def OnUpdateLesion(self, msg):
        print("Update Lung Lesion Statistics Panel")

        # Mock Data
        # data = [mock_data, mock_data1][randint(0, 1)]
        # with open(util.GetResourcePath("PA373_ST1_SE2.json")) as f:
        #     data = json.load(f)
        # self.update_list(data)

        if ("analysis" in msg) and ("whole_lung" in msg["analysis"]):
            data = msg["analysis"]["whole_lung"]
            self.update_list(data)
        else:
            print("no whole_lung data")
