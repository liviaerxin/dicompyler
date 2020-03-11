import wx
import wx.lib.mixins.inspection as wit
from pubsub import pub

import matplotlib as mpl

import matplotlib.image as mpimg
from matplotlib.backends.backend_wxagg import (
    FigureCanvasWxAgg as FigureCanvas,
    NavigationToolbar2WxAgg as NavigationToolbar,
)
from matplotlib.figure import Figure
from matplotlib import font_manager


import numpy as np
from dicompyler import util

from PIL import Image
from typing import List
import json
import logging

logger = logging.getLogger("dicompyler.hist_panel")


# label_size = 8
# mpl.rcParams['xtick.labelsize'] = label_size

hist_params = {
    # "bins": 15,
    "density": True,
    "histtype": "bar",
    "color": "b",
    "edgecolor": "k",
    "alpha": 0.5,
}

Ref_Lung = None
with open(util.GetResourcePath("ref_lung_hist.json")) as f:
    Ref_Lung_Hist = json.load(f)["hist"]


def pyramid_plot(
    figure: Figure,
    ylabels: List,
    xticks: List,
    data_left: List,
    title_left: str,
    data_right: List,
    title_right: str = "",
    **kwargs,
):
    if figure is None:
        return None

    y_pos = np.arange(len(ylabels))
    # empty_ticks = tuple('' for n in ylabels)

    # set yticks by slice
    yticks = y_pos[::5]
    yticklabels = ylabels[::5]

    # space between bars
    height = 1

    # left
    axes_left = figure.add_subplot(121)
    axes_left.barh(y_pos, data_left, height=height, **kwargs)
    axes_left.invert_xaxis()
    axes_left.set_yticks(yticks)
    # axes_left.set_yticklabels(yticklabels, fontsize=8)
    axes_left.set_yticklabels(yticklabels)
    axes_left.yaxis.set_tick_params(labelsize=7)
    axes_left.yaxis.tick_right()
    axes_left.set_title(title_left)

    # right
    axes_right = figure.add_subplot(122)
    axes_right.barh(y_pos, data_right, height=height, **kwargs)
    axes_right.set_yticks(yticks)
    axes_right.set_yticklabels([])
    axes_right.yaxis.set_tick_params(labelsize=7)
    axes_right.set_title(title_right)

    # line
    axes_left.plot(Ref_Lung_Hist["left"], y_pos, "r")
    axes_right.plot(Ref_Lung_Hist["right"], y_pos, "r")

    # ...
    if xticks is not None:
        axes_left.set(xticks=xticks)
        axes_right.set(xticks=xticks)

    figure.tight_layout()
    # set the left and right plot space
    figure.subplots_adjust(wspace=0.3)

    return figure


def hist_plot(figure: Figure, data: List, title: str = ""):
    if figure is None:
        return None

    axes = figure.add_subplot(111)
    # set tick size,...etc
    axes.yaxis.set_tick_params(labelsize=5)
    axes.xaxis.set_tick_params(labelsize=7)
    axes.set_title(title)

    counts, bins = np.histogram(data, bins=15)
    axes.hist(bins[:-1], bins=bins, weights=counts, **hist_params)

    return figure


class HistPanel(wx.Panel):
    def __init__(self, parent, dpi=None, figsize=(4, 4), *args, **kwargs):
        wx.Panel.__init__(self, parent, *args, **kwargs)
        self.figure = Figure(figsize=figsize, dpi=dpi)

        self.canvas = FigureCanvas(self, -1, self.figure)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.EXPAND | wx.ALL)
        self.SetSizer(self.sizer)

        # self.add_toolbar()  # add as needed

        self.Bind(wx.EVT_PAINT, self.OnPaint)

        # Set up pubsub
        pub.subscribe(self.OnUpdateHistogram, "patient.updated.lesion_analysis")

    def plot_histogram_img(self, img: str):
        """Plot a histogram

        Arguments:
            img {str} -- image filepath string
        """
        print("plot_histogram_img")
        # t = np.arange(0.0, 3.0, 0.01)
        # s = np.sin(2 * np.pi * t)
        # self.axes.plot(t, s)

        img_data = mpimg.imread(img)

        self.plot_histogram(img_data.ravel())

    def plot_histogram(self, data_array: np.ndarray):
        """Plot a histogram

        Arguments:
            data_array {np.ndarray} -- 1-d array
        """
        print("plot_histogram")
        self.figure.clear()

        # Plot
        hist_plot(self.figure, data_array)

        self.canvas.draw()
        self.canvas.Refresh()

    def plot_histogram_back_to_back(
        self, ylabels: List, xticks: List, counts_left: List, counts_right: List
    ):
        self.figure.clear()

        # Plot

        pyramid_plot(
            self.figure,
            ylabels,
            xticks,
            counts_left,
            "Left Lung",
            counts_right,
            "Right Lung",
        )

        self.canvas.draw()
        self.canvas.Refresh()

    def plot_histogram_line_by_line(
        self, bins: List, counts_left: List, counts_right: List
    ):
        self.figure.clear()
        self.figure.subplots_adjust(hspace=0.3)

        # 1. Plot Right Lung
        ax_right_lung = self.figure.add_subplot(211)

        # 1.1. configure
        ax_right_lung.grid(True, linestyle="-.")
        ax_right_lung.tick_params(axis="x", labelsize=6, labelrotation=45)
        ax_right_lung.set_title(
            label="Right Lung", x=-0.05, y=1, fontdict={"fontsize": 8}
        )
        # ax_right_lung.set_ylabel("Right Lung")

        # 1.2. set xticks by slice
        xticks = bins[::10]
        ax_right_lung.set_xticks(xticks)
        ax_right_lung.set_yticklabels([])

        # 1.3 plot hist
        ax_right_lung.hist(bins[:-1], bins=bins, weights=counts_right, label="Present")

        # 1.4 plot ref hist line
        ax_right_lung.plot(
            Ref_Lung_Hist["HU"][:-1], Ref_Lung_Hist["right"], "r", label="Reference"
        )
        ax_right_lung.legend()

        # 2. Plot Left Lung
        ax_left_lung = self.figure.add_subplot(212)

        # 2.1. configure
        ax_left_lung.grid(True, linestyle="-.")
        ax_left_lung.tick_params(axis="x", labelsize=6, labelrotation=45)
        ax_left_lung.set_title(
            label="Left Lung", x=-0.05, y=1, fontdict={"fontsize": 8}
        )

        # 2.2. set xticks by slice
        xticks = bins[::10]
        ax_left_lung.set_xticks(xticks)
        ax_left_lung.set_yticklabels([])
        ax_left_lung.set_xlim(-750, 100)

        # 2.3 plot hist
        ax_left_lung.hist(bins[:-1], bins=bins, weights=counts_right, label="Present")

        # 2.4 plot ref hist line
        ax_left_lung.plot(
            Ref_Lung_Hist["HU"][:-1], Ref_Lung_Hist["left"], "r", label="Reference"
        )
        ax_left_lung.legend()

        ax_left_lung.set_xlabel("CT Value")

        # redraw
        self.canvas.draw()
        self.canvas.Refresh()

        # TODO: Test OnChangeCTRange
        # wx.CallLater(3000, self.OnChangeCTRange, -800, 100)

    def OnChangeCTRange(self, left, right):
        for ax in self.figure.axes:
            print(ax)

    def add_toolbar(self):
        self.toolbar = NavigationToolbar(self.canvas)
        self.toolbar.Realize()
        # By adding toolbar in sizer, we are able to put it at the bottom
        # of the frame - so appearance is closer to GTK version.
        self.sizer.Add(self.toolbar, 0, wx.LEFT | wx.EXPAND)
        # update the axes menu on the toolbar
        self.toolbar.update()

    def OnUpdateHistogram(self, msg):
        print(f"Update Patient Histogram Panel")
        """Update Histogram When Lesion Analysis Finish."""
        # logger.info(msg)

        try:
            hist_data = msg["result"]["hist"]

            """Plot Two back-to-back Histograms"""
            # print(hist_data["HU"])
            # print(hist_data["left"])
            # print(hist_data["right"])
            # TODO: process real data here, here is expected to get `counts` and `bins` directly by specific method provided by robin
            # self.plot_histogram_back_to_back(
            #     hist_data["HU"][:-1], None, hist_data["left"], hist_data["right"]
            # )
            self.plot_histogram_line_by_line(
                hist_data["HU"], hist_data["left"], hist_data["right"]
            )

        except KeyError:
            print("no valid data to plot histogram!")

        """Plot Single Histogram"""
        # Mock data
        # data_array = np.array(image)
        # flatten to 1-d array
        # self.plot_histogram(data_array.ravel())

    def OnPaint(self, e):
        # print(f"OnPaint: {e}")
        pass

    def OnSize(self, e):
        print(f"OnSize: {e}")


def run_HistPanel():
    app = wx.App()
    frame = wx.Frame(None, -1, "run HistPanel once", size=(550, 500))

    sizer = wx.BoxSizer(wx.VERTICAL)

    histPanel = HistPanel(frame)
    # first
    histPanel.plot_histogram(np.random.randint(0, 100, (500)))

    sizer.Add(histPanel, 1, wx.ALL | wx.EXPAND)
    frame.SetSizer(sizer)
    frame.Fit()

    frame.Show(True)
    app.MainLoop()


def run_and_update_HistPanel():
    app = wx.App()
    frame = wx.Frame(None, -1, "run and update HistPanel", size=(550, 500))

    sizer = wx.BoxSizer(wx.VERTICAL)

    histPanel = HistPanel(frame, figsize=(6, 6))

    # first
    histPanel.plot_histogram(np.random.randint(0, 100, (500)))
    # second
    wx.CallLater(
        3000, histPanel.plot_histogram_img, util.GetResourcePath("book.png"),
    )
    sizer.Add(histPanel, 1, wx.ALL | wx.EXPAND)
    frame.SetSizer(sizer)
    frame.Fit()

    frame.Show(True)
    app.MainLoop()


def run_two_HistPanel():
    app = wx.App()
    frame = wx.Frame(None, -1, "run HistPanel once", size=(550, 500))

    sizer = wx.BoxSizer(wx.VERTICAL)

    # first
    histPanel = HistPanel(frame)
    histPanel.plot_histogram_back_to_back(
        [0, 100, 200, 300, 400, 500],
        None,
        [20, 30, 40, 50, 89, 20],
        [40, 30, 60, 50, 70, 10],
    )

    sizer.Add(histPanel, 1, wx.ALL | wx.EXPAND)
    frame.SetSizer(sizer)
    frame.Fit()

    frame.Show(True)
    app.MainLoop()


if __name__ == "__main__":
    """Create the main window and insert the custom frame."""
    # run_HistPanel()
    # run_and_update_HistPanel()
    run_two_HistPanel()
