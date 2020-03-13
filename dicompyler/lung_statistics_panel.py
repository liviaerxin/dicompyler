import wx
import wx.lib.mixins.listctrl
from pubsub import pub

from typing import Dict
from random import randint
import json

from dicompyler import util


import logging, logging.handlers

logger = logging.getLogger("dicompyler.lesion_panel")


mock_data = {
    "density": {"whole": -817.98, "left": -817.08, "right": -818.75},
    "infection_volume": {"whole": 13.66, "left": 13.66, "right": 0},
}

mock_data1 = {
    "density": {"whole": -817.98, "left": -817.08, "right": -818.75},
    "infection_volume": {"whole": 13.66, "left": 13.66, "right": 0},
    "volume": {"whole": 5356.45, "left": 2457.46, "right": 2898.98},
    "infection_volume": {"whole": 0.255, "left": 0.5559, "right": 0.0},
}

COLUMN = [
    {
        "label": "",
        "key": "item",
        "width": 150,
        "items": [
            {"label": "Volume (cm3)", "key": "volume"},
            {"label": "Density (HU)", "key": "density"},
            {"label": "Infection Volume", "key": "infection_volume"},
            {"label": "Infection Percentage", "key": "infection_volume"},
        ],
    },
    {"label": "Whole Lung", "key": "whole", "width": 120,},
    {"label": "Right Lung", "key": "right", "width": 120,},
    {"label": "Left Lung", "key": "left", "width": 120,},
]


def pre_process_data(data: Dict):
    result = []
    for item in COLUMN[0]["items"]:
        key = item["key"]
        label = item["label"]
        if key in data:
            row = {}
            v = data[key]
            row["label"] = label
            row["whole"] = str(v["whole"]) if "whole" in v else "None"
            row["left"] = str(v["left"]) if "left" in v else "None"
            row["right"] = str(v["right"]) if "right" in v else "None"
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

        idx = 0
        items = pre_process_data(data)

        for item in items:
            index = self.list.InsertItem(idx, item["label"])
            self.list.SetItem(index, 1, item["whole"])
            self.list.SetItem(index, 2, item["right"])
            self.list.SetItem(index, 3, item["left"])
            self.list.SetItemData(index, idx)
            idx += 1


    def OnUpdateLesion(self, msg):
        print("Update Patient Lesion Statistics Panel")

        # TODO: real data instead of mock data

        # data = [mock_data, mock_data1][randint(0, 1)]
        with open(util.GetResourcePath("PA373_ST1_SE2.json")) as f:
            data = json.load(f)

        self.update_list(data)
