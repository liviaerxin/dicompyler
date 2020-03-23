import os
import wx
import wx.xrc as xrc

dir = os.path.dirname(os.path.abspath(__file__))
resources_dir = os.path.join(dir, "resources")

main_xrc_file = os.path.join(resources_dir, "main.xrc")


class PanelGeneral(wx.Panel):
    def __init__(self, parent, *args, **kw):
        super().__init__()

        res = xrc.XmlResource(main_xrc_file)
        res.LoadPanel(self, parent, "panelGeneral")


class PanelWelcome(wx.Panel):
    def __init__(self, parent, *args, **kw):
        super().__init__()

        res = xrc.XmlResource(main_xrc_file)
        res.LoadPanel(self, parent, "panelWelcome")


"""
Test Show
"""

class TestFrameGeneral(wx.Frame):
    def __init__(self, parent, *args, **kw):
        super().__init__(parent, *args, **kw)

        self.panel = PanelGeneral(self) #! it does not show when using `panel = PanelGeneral(self)`  (c++ variable destroy)


class TestFrameWelcome(wx.Frame):
    def __init__(self, parent, *args, **kw):
        super().__init__(parent, *args, **kw)

        self.panel = PanelWelcome(self) #! it does not show when using `panel = PanelWelcome(self)`  (c++ variable destroy)

if __name__ == "__main__":
    app = wx.App()

    #frame = TestFrameGeneral(None)
    frame = TestFrameWelcome(None)

    frame.Show()

    app.MainLoop()
