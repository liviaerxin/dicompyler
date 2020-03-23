import logging

logger = logging.getLogger("dicompyler.2dview")
import wx
from wx.xrc import XmlResource, XRCCTRL, XRCID
from pubsub import pub
from dicompyler import guiutil, util
from dicompyler.baseplugins.view2d import View2d
from dicompyler.mark_slider import MarkSlider


"""
Use as a Custom Widget.
"""


class View2dSlider(wx.Panel):
    """Panel to display DICOM image in 2D with a slider."""

    def __init__(self, parent):
        super().__init__()

        # Load the XRC file for our gui resources
        self.res = XmlResource(util.GetBasePluginsPath("view2d_slider.xrc"))
        self.res.LoadPanel(self, parent, "view2dSliderPanel")

        self.Init()

    def Init(self):
        """Method called after the panel has been initialized."""

        # Initialize the panel controls
        self.view2d = View2d(self)
        self.res.AttachUnknownControl("viewPanel", self.view2d, self)
        self.slider = MarkSlider(self, style=wx.SL_VERTICAL)
        self.res.AttachUnknownControl("sliderPanel", self.slider, self)

        # Bind interface events to the proper methods
        self.slider.Bind(wx.EVT_SLIDER, self.OnSliderScroll)

        # Set up pubsub
        pub.subscribe(self.OnUpdatePatient, "patient.updated.parsed_data")
        pub.subscribe(self.OnUpdateImage, "2dview.updated.image")
        pub.subscribe(self.OnUpdateLesion, "lesion.loaded.analysis")

    def OnDestroy(self, event):
        """Unbind to all events before the plugin is dÃƒÅ¸estroyed."""

        print("Destroy plugin2DView")

        pub.unsubscribe(self.OnUpdatePatient, "patient.updated.parsed_data")
        pub.unsubscribe(self.OnUpdateImage, "2dview.updated.image")
        pub.unsubscribe(self.OnUpdateLesion, "lesion.loaded.analysis")

    def OnUpdatePatient(self, msg):
        """Update and load the patient data."""

        max = len(msg["images"])
        min = 1
        self.slider.SetMax(max)
        self.slider.SetMin(min)
        self.slider.SetValue(min)

    def OnUpdateImage(self, msg):
        """Update the slider when 2d view update to a new image."""

        self.slider.SetValue(msg["number"])

    def OnUpdateLesion(self, msg):
        """Update the slider range when 2d view update to a new image."""

        if ("analysis" in msg) and ("lesions" in msg["analysis"]):
            lesions = msg["analysis"]["lesions"]
            lesion_ranges = []
            for lesion in lesions:
                start_slice = lesion["start_slice"]
                end_slice = lesion["end_slice"]
                lesion_ranges.append([start_slice, end_slice])
            self.slider.SetRanges(lesion_ranges)
        else:
            print("no lesions data")

    def OnSliderScroll(self, event):
        """slider value changed"""

        obj = event.GetEventObject()
        value = obj.GetValue()
        pub.sendMessage("2dview.goto_slice", msg={"slice": value})


class TestFrame(wx.Frame):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

        self.InitUI()

    def InitUI(self):
        panel = wx.Panel(self)

        hbox = wx.BoxSizer(orient=wx.HORIZONTAL)

        self.view2d_slider = View2dSlider(panel)
        hbox.Add(self.view2d_slider, proportion=1, flag=wx.EXPAND | wx.ALL)

        panel.SetSizer(hbox)

        self.Centre()


def main():
    app = wx.App()
    frame = TestFrame(None)
    frame.Show()
    app.MainLoop()


if __name__ == "__main__":
    main()
