import wx
import wx.lib.mixins.listctrl
from pubsub import pub

from typing import List
from random import randint
import json

from dicompyler import util


import logging, logging.handlers

logger = logging.getLogger("dicompyler.lesion_panel")


mock_data = [
    {
        "id": 1,
        "pattern": "GGO",
        "location": "left",
        "volume": 3.28,
        "percentage": 0.06,
        "density": -700,
        "start_slice": 90,
        "end_slice": 96,
        "representative_slice": 93,
    },
    {
        "id": 2,
        "pattern": "GGO",
        "location": "left",
        "volume": 1.97,
        "percentage": 0.04,
        "density": -730,
        "start_slice": 90,
        "end_slice": 96,
        "representative_slice": 93,
    },
]

mock_data1 = [
    {
        "id": 3,
        "pattern": "consolidation",
        "location": "right",
        "volume": 32.73,
        "percentage": 0.6,
        "density": -300,
        "start_slice": 100,
        "end_slice": 120,
        "representative_slice": 107,
    }
]

COLUMN = [
    {"label": "No.", "key": "id"},
    {"label": "Pattern", "key": "pattern"},
    {"label": "Slices", "key": "slices"},
    {"label": "Volume(%)", "key": "volume"},
    {"label": "Density(HU)", "key": "density"},
    {"label": "Location", "key": "location"},
]


def pre_process_data(data: List):
    result = []
    for item in data:
        row = {}
        # combine `start_slice` and `end_slice` to `slice`
        row["slices"] = "-".join(
            [
                str(item["start_slice"]),
                str(item["representative_slice"]),
                str(item["end_slice"]),
            ]
        )

        # copy
        row["id"] = item["id"]
        row["pattern"] = item["pattern"]
        row["location"] = item["location"]
        row["volume"] = item["volume"]
        row["density"] = item["density"]
        row["start_slice"] = item["start_slice"]
        row["end_slice"] = item["end_slice"]
        row["representative_slice"] = item["representative_slice"]
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


class LesionStatisticsPanel(wx.Panel):
    def __init__(self, parent, *args, **kwargs):
        wx.Panel.__init__(self, parent, *args, **kwargs)

        print("Initialize Lesion Statistics Panel")
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        # TODO: Initialize data visulization view(does it need?)

        # Initialize data list control view
        self.list = SortedListCtrl(self)

        for i, col in enumerate(COLUMN):
            self.list.InsertColumn(i, col["label"])

        # Font size
        # self.list.SetFont(wx.Font(wx.FontInfo(10)))

        # sizer
        hbox.Add(self.list, 1, wx.EXPAND)
        self.SetSizer(hbox)

        # Bind interface events to the proper methods
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated, self.list)

        # Set up pubsub
        pub.subscribe(self.OnUpdateLesion, "lesion.loaded.analysis")

    def OnDestroy(self, evt):
        """Unbind to all events before the plugin is destroyed."""
        print("Destroy Lesion Statistics Panel")

        pub.unsubscribe(self.OnUpdateLesion, "lesion.loaded.analysis")

    def update_lesion_list(self, data):

        self.list.DeleteAllItems()

        self.items = pre_process_data(data)

        for i, item in enumerate(self.items):
            index = self.list.InsertItem(i, str(item["id"]))
            self.list.SetItem(index, 1, str(item["pattern"]))
            self.list.SetItem(index, 2, str(item["slices"]))
            self.list.SetItem(index, 3, str(item["volume"]))
            self.list.SetItem(index, 4, str(item["density"]))
            self.list.SetItem(index, 5, str(item["location"]))

    def OnItemActivated(self, msg):
        print("List Item Activated")
        # print(msg.GetIndex())
        print(self.items[msg.GetIndex()])
        item = self.items[msg.GetIndex()]

        pub.sendMessage(
            "2dview.goto_slice", msg={"slice": item["representative_slice"]}
        )

    def OnUpdateLesion(self, msg):
        print("Update Patient Lesion Statistics Panel")

        # TODO: real data instead of mock data

        # data = [mock_data, mock_data1][randint(0, 1)]
        with open(util.GetResourcePath("PA373_ST1_SE2.json")) as f:
            data = json.load(f)["lesion_list"]

        self.update_lesion_list(data)


def run_LesionPanel():
    app = wx.App()
    frame = wx.Frame(None, -1, "run LesionPanel", size=(300, 200))

    sizer = wx.BoxSizer(wx.VERTICAL)

    """code"""
    lesionPanel = LesionStatisticsPanel(frame)
    lesionPanel.update_lesion_list(mock_data)

    sizer.Add(lesionPanel, 1, wx.ALL | wx.EXPAND)
    frame.SetSizer(sizer)

    frame.Show()
    app.MainLoop()


def run_and_update_LesionPanel():
    app = wx.App()
    frame = wx.Frame(None, -1, "run LesionPanel", size=(300, 200))

    sizer = wx.BoxSizer(wx.VERTICAL)

    """code"""
    lesionPanel = LesionStatisticsPanel(frame)

    # first
    lesionPanel.update_lesion_list(mock_data)
    # second
    wx.CallLater(
        3000, lesionPanel.update_lesion_list, mock_data1,
    )

    sizer.Add(lesionPanel, 1, wx.ALL | wx.EXPAND)
    frame.SetSizer(sizer)

    frame.Show()
    app.MainLoop()


if __name__ == "__main__":
    """Create the main window and insert the custom frame."""
    # run_LesionPanel()
    run_and_update_LesionPanel()
