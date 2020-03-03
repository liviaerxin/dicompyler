import os
import wx
import wx.xrc as xrc

dir = os.path.dirname(os.path.abspath(__file__))
resources_dir = os.path.join(dir, "resources")

main_xrc_file = os.path.join(resources_dir, "main.xrc")


class PanelGeneral(wx.Panel):
    def __init__(self, parent, *args, **kw):
        wx.Panel.__init__(self, parent)

        res = xrc.XmlResource(main_xrc_file)
        res.LoadPanel(self, parent, "panelGeneral")


class PanelWelcome(wx.Panel):
    def __init__(self, parent, *args, **kw):
        wx.Panel.__init__(self, parent)
        res = xrc.XmlResource(main_xrc_file)
        res.LoadPanel(self, parent, "panelWelcome")


class PanelTest(wx.Panel):
    def __init__(self, parent, *args, **kw):
        wx.Panel.__init__(self, parent)
        res = xrc.XmlResource(main_xrc_file)
        res.LoadPanel(self, parent, "MyPanel9")
        self.panel1 = xrc.XRCCTRL(self, "m_panel2")
        self.notebook: wx.Notebook = xrc.XRCCTRL(self, "m_notebook5")
        # self.notebook.DeletePage(0)


class TestFrame(wx.Frame):
    def __init__(self, parent, *args, **kw):
        wx.Frame.__init__(self, parent, *args, **kw)


"""
Test Show
"""


def show_PanelGeneral():
    frame = wx.Frame(None)

    panelGeneral = PanelGeneral(frame)

    frame.Show()


def show_PanelWelcome():
    frame = wx.Frame(None)

    # panelWelcome = xrc.XmlResource(main_xrc_file).LoadPanel(frame, 'panelWelcome')
    panelWelcome = PanelWelcome(frame)

    frame.Show()


if __name__ == "__main__":
    app = wx.App()
    # show_PanelGeneral()
    # show_PanelWelcome()

    frame = wx.Frame(None)

    PanelTest = PanelTest(frame)

    frame.Show()

    app.MainLoop()
