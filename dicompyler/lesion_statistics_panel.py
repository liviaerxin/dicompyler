import wx
import wx.lib.mixins.listctrl
from pubsub import pub

from random import randint

import logging, logging.handlers

logger = logging.getLogger("dicompyler.lesion_panel")


mock_data = [
    ("左肺上叶", "7%", "53%"),
    ("左肺下叶", "13%", "27%"),
    ("右肺上叶", "4%", "26%"),
    ("右肺中叶", "2%", "25%"),
    ("右肺下叶", "12%", "30%"),
]

mock_data1 = [
    ("左肺上叶", "17%", "13%"),
    ("左肺下叶", "23%", "47%"),
    ("右肺上叶", "14%", "56%"),
    ("右肺中叶", "20%", "95%"),
    ("右肺下叶", "22%", "60%"),
]

COLUMN = [
    ("位置", 100),
    ("实性密度影", 20),
    ("磨玻璃密度", 20),
]


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

        hbox = wx.BoxSizer(wx.HORIZONTAL)

        # TODO: Initialize data visulization view(does it need?)

        # Initialize data list control view
        self.list = SortedListCtrl(self)
        self.list.InsertColumn(0, COLUMN[0][0], width=COLUMN[0][1])
        self.list.InsertColumn(1, COLUMN[1][0])
        self.list.InsertColumn(2, COLUMN[2][0])
        self.list.SetFont(wx.Font(wx.FontInfo(14)))

        # sizer
        hbox.Add(self.list, 1, wx.EXPAND)
        self.SetSizer(hbox)

        # Set up pubsub
        pub.subscribe(self.OnUpdateLesion, "patient.updated.lesion_analysis")

    def update_lesion_list(self, data):

        self.list.DeleteAllItems()

        idx = 0

        for item in data:

            index = self.list.InsertItem(idx, item[0])
            self.list.SetItem(index, 1, item[1])
            self.list.SetItem(index, 2, item[2])
            self.list.SetItemData(index, idx)
            idx += 1

    def OnUpdateLesion(self, msg):
        print("Update Patient Lesion Statistics Panel")
        # TODO: real data instead of mock data

        data = [mock_data, mock_data1][randint(0, 1)]
        self.update_lesion_list(data)


def run_LesionPanel():
    app = wx.App()
    frame = wx.Frame(None, -1, "run LesionPanel", size=(300, 200))

    sizer = wx.BoxSizer(wx.VERTICAL)

    """code"""
    lesionPanel = LesionPanel(frame)
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
    lesionPanel = LesionPanel(frame)

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
