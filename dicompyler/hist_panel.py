import wx
import wx.lib.mixins.inspection as wit
from pubsub import pub

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

import logging

logger = logging.getLogger("dicompyler.hist_panel")

hist_params = {
    # "bins": 15,
    "density": True,
    "histtype": "bar",
    "color": "b",
    "edgecolor": "k",
    "alpha": 0.5,
}


def pyramid_plot(figure:Figure, ylabels: List, xticks: List, data_left: List, title_left: str, data_right: List, title_right: str="", **kwargs):
    if(figure is None):
        return None

    y_pos = np.arange(len(ylabels))
    #empty_ticks = tuple('' for n in ylabels)
    
    height = 1
    axes_left = figure.add_subplot(121)
    axes_left.barh(y_pos, data_left, height=height, **kwargs)
    axes_left.invert_xaxis()
    axes_left.set(yticks=y_pos, yticklabels=ylabels)
    axes_left.yaxis.tick_right()
    axes_left.set_title(title_left)
    
    axes_right = figure.add_subplot(122)
    axes_right.barh(y_pos, data_right, height=height, **kwargs)
    axes_right.set(yticks=y_pos, yticklabels=[])
    axes_right.set_title(title_right)


    #...
    if xticks is not None:
        axes_left.set(xticks=xticks)
        axes_right.set(xticks=xticks)

    figure.tight_layout()
    figure.subplots_adjust(wspace=0.3)

    return figure

def hist_plot(figure:Figure, data: List, title: str=""):
    if(figure is None):
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
        pub.subscribe(self.OnUpdateHistogram, "2dview.updated.image")


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

    def plot_histogram_back_to_back(self, ylabels: List, xticks: List, counts_left: List, counts_right: List):
        self.figure.clear()

        # Plot

        pyramid_plot(self.figure, ylabels, xticks, counts_left, u"left", counts_right, u"right")

        self.canvas.draw()
        self.canvas.Refresh()

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
        """Update Histogram When 2D View Image Updated."""
        # logger.info(msg)
        image: Image.Image = msg["image_pil"]

        """Plot Single Histogram"""
        # Mock data
        #data_array = np.array(image)
        # flatten to 1-d array
        #self.plot_histogram(data_array.ravel())

        """Plot Two back-to-back Histograms"""
        # Mock data
        data_array = np.array(image)
        # flatten to 1-d array
        data_left = data_array.ravel()
        data_right = data_left + np.random.random(len(data_left))

        # Mock counts, bins calculation
        data_sets = [data_left, data_right]
        hist_range = (np.min(data_sets), np.max(data_sets))
        if np.max(data_sets) > 1:
            hist_range = (0, 250)
        number_of_bins = 10
        counts_left, bins = np.histogram(data_left, range=hist_range, bins=number_of_bins)
        counts_right, bins = np.histogram(data_right, range=hist_range, bins=number_of_bins)
        xticks = None #np.arange(0, np.max([counts_left, counts_right]))
        #print(bins)
        #print(xticks)
        #print(counts_left)
        #print(counts_right)
        bins = bins.astype(int)
        self.plot_histogram_back_to_back(bins[:-1], xticks, counts_left, counts_right)
        
        #self.plot_histogram_back_to_back([0, 100, 200, 300, 400, 500], None, [20, 30, 40, 50, 89, 20], [40, 30, 60, 50, 70, 10])
        # TODO: process real data here, here is expected to get `counts` and `bins` directly by specific method provided by robin


    def OnPaint(self, e):
        print(f"OnPaint: {e}")

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
        3000,
        histPanel.plot_histogram_img,
        util.GetResourcePath("book.png"),
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
    histPanel.plot_histogram_back_to_back([0, 100, 200, 300, 400, 500], None, [20, 30, 40, 50, 89, 20], [40, 30, 60, 50, 70, 10])

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