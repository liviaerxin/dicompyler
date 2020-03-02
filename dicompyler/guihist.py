import wx
import wx.lib.mixins.inspection as wit
from wx.lib.pubsub import pub

import matplotlib.image as mpimg
from matplotlib.backends.backend_wxagg import (
    FigureCanvasWxAgg as FigureCanvas,
    NavigationToolbar2WxAgg as NavigationToolbar)
from matplotlib.figure import Figure

import numpy as np
from dicompyler import util
 
from PIL import Image

import logging, logging.handlers
logger = logging.getLogger('dicompyler.guihist')

class HistPanel(wx.Panel):
    def __init__(self, parent, dpi=None, **kwargs):
        wx.Panel.__init__(self, parent, **kwargs)
        self.figure = Figure(figsize=(1, 4), dpi=dpi)
        #self.axes = self.figure.add_subplot(111)
        self.axes = self.figure.gca()
        self.canvas = FigureCanvas(self, -1, self.figure)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.EXPAND)
        self.SetSizer(self.sizer)

        self._init_plot()
        #self.add_toolbar()
        #self.plot_histogram()

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        #self.Bind(wx.EVT_SIZE, self.OnSize)

        # Set up pubsub
        pub.subscribe(self.OnUpdateHistogram, '2dview.updated.image')


    def _init_plot(self):
        # set title
        self.figure.suptitle('Histogram', fontsize=10)
        # set label
        self.axes.set_xlabel('xlabel', fontsize=6)
        self.axes.set_ylabel('ylabel', fontsize=6)
        # set ticks
        self.axes.xaxis.set_tick_params(labelsize=7)
        self.axes.yaxis.set_tick_params(labelsize=5)

    def plot_histogram_img(self, img: str):
        print("plot_histogram_img")
        self.axes.cla()
        # t = np.arange(0.0, 3.0, 0.01)
        # s = np.sin(2 * np.pi * t)
        #self.axes.plot(t, s)
        
        img_data = mpimg.imread(img)
        
        self.axes.hist(img_data.ravel(), bins=50)
        self.canvas.draw()
        self.canvas.Refresh()

    def plot_histogram(self, data_array: np.ndarray):
        print("plot_histogram")
        self.axes.cla()
        self.axes.hist(data_array, bins=100)
        self.canvas.draw()
        self.canvas.Refresh()

    def add_toolbar(self):
        self.toolbar = NavigationToolbar(self.canvas)
        self.toolbar.Realize()
        # By adding toolbar in sizer, we are able to put it at the bottom
        # of the frame - so appearance is closer to G   TK version.
        self.sizer.Add(self.toolbar, 0, wx.LEFT | wx.EXPAND)
        # update the axes menu on the toolbar
        self.toolbar.update()

    def OnUpdateHistogram(self, msg):
        """Update Histogram When 2D View Image Updated."""
        #logger.info(msg)
        image: Image.Image = msg['image_pil']

        data_array = np.array(image)
        #logger.info(data_array)

        # flatten to 1-d array
        self.plot_histogram(data_array.ravel())

    def OnPaint(self, e):
        print(f"OnPaint: {e}")

    def OnSize(self, e):
        print(f"OnSize: {e}")

class CanvasFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1,
                          'CanvasFrame', size=(550, 500))
        
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.histPanel = HistPanel(self)

        #self.histPanel.plot_histogram_img("/Users/siyao/Documents/dicom/dicompyler/dicompyler/resources/book.png")
        self.histPanel.plot_histogram(np.random.randint(0, 100, (500)))
        #wx.CallLater(5000, self.histPanel.plot_histogram, np.random.randint(0, 100, (500)))

        wx.CallLater(2000, self.histPanel.plot_histogram_img, "/Users/siyao/Documents/dicom/dicompyler/dicompyler/resources/book.png")

        self.sizer.Add(self.histPanel, 1, wx.TOP | wx.LEFT | wx.EXPAND)

        # update the axes menu on the toolbar
        self.SetSizer(self.sizer)
        self.Fit()



if __name__ == "__main__":
    """Create the main window and insert the custom frame."""
    app = wx.App()
    frame = CanvasFrame()
    frame.Show(True)
    app.MainLoop()