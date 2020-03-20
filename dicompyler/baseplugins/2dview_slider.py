import logging

logger = logging.getLogger("dicompyler.2dview")
import wx
from wx.xrc import XmlResource, XRCCTRL, XRCID
from pubsub import pub
from dicompyler import guiutil, util
from dicompyler.baseplugins.view2d import View2D
from dicompyler.mark_slider import MarkSlider

"""
Later, it will be renamed to "2dview.py" when it's steady
"""


def pluginProperties():
    """Properties of the plugin."""

    props = {}
    props["name"] = "2D View"
    props["description"] = "Display image, structure and dose data in 2D"
    props["author"] = "Aditya Panchal"
    props["version"] = "0.5.0"
    props["plugin_type"] = "main"
    props["plugin_version"] = 1
    props["min_dicom"] = ["images"]
    props["recommended_dicom"] = ["images", "rtss", "rtdose"]

    return props


def pluginLoader(parent):
    """Function to load the plugin."""

    panel2DView = Plugin2DViewSlider(parent)

    return panel2DView


class Plugin2DViewSlider(wx.Panel):
    """Plugin to display DICOM image, RT Structure, RT Dose in 2D."""

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        # Load the XRC file for our gui resources
        self.res = XmlResource(util.GetBasePluginsPath("2dviewslider.xrc"))
        self.res.LoadPanel(self, parent, "plugin2DViewSlider")

        self.Init()

    def Init(self):
        """Method called after the panel has been initialized."""

        # Initialize the panel controls
        self.view2d = View2D(self)
        self.res.AttachUnknownControl("2dviewPanel", self.view2d, self)
        self.slider = MarkSlider(self, style=wx.SL_VERTICAL)
        self.res.AttachUnknownControl("sliderPanel", self.slider, self)

        # Bind interface events to the proper methods
        self.slider.Bind(wx.EVT_SLIDER, self.OnMarkSliderScroll)

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
        self.slider.SetValue(msg["number"])

    def OnUpdateLesion(self, msg):
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

    def OnMarkSliderScroll(self, event):
        obj = event.GetEventObject()
        value = obj.GetValue()
        pub.sendMessage("2dview.goto_slice", msg={"slice": value})
