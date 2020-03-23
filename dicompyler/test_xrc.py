import os
import wx
import wx.xrc as xrc

dir = os.path.dirname(os.path.abspath(__file__))
resources_dir = os.path.join(dir, "resources")

main_xrc_file = os.path.join(resources_dir, "main.xrc")


class PanelGeneral(wx.Panel):
    def __init__(self, parent):
        super().__init__()

        res = xrc.XmlResource(main_xrc_file)
        res.LoadPanel(self, parent, "panelGeneral")


class PanelWelcome(wx.Panel):
    def __init__(self, parent):
        super().__init__()
        res = xrc.XmlResource(main_xrc_file)
        print(parent)
        res.LoadPanel(self, parent, "panelWelcome")
        print(parent.GetChildren())

"""
Test Show
"""


class TestFramePanelGeneral(wx.Frame):
    def __init__(self, parent=None, *args, **kw):
        super().__init__(parent, *args, **kw)

        sizer = wx.BoxSizer()
        
        self.panelGeneral = PanelGeneral(self) # !it does not show when using `panelGeneral = PanelGeneral(self)`  (c++ variable destroy?)
        sizer.Add(panelGeneral)

        self.SetSizer(sizer)



class TestFramePanelWelcome(wx.Frame):
    def __init__(self, parent=None):
        super().__init__(parent=None, title="xxxx")

        self.panelWelcome = PanelWelcome(self) # !it does not show when using `panelWelcome = PanelWelcome(self)`


def main():
    app = wx.App()
    
    #frame = TestFramePanelGeneral(title="xxxx")
    
    
    frame = TestFramePanelWelcome(None)
    
    #frame = wx.Frame(None)
    #panelWelcome = PanelWelcome(frame) # !it does not show when using `PanelWelcome(frame)`
    
    
    frame.Show()

    app.MainLoop()

if __name__ == "__main__":
    main()
