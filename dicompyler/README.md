# Extended Dicompyler

## Feature

1. Panel to show the histogram graph of each image in 2D-View.
2. Panel to show the lesion list of each series

## TODO Works

- [x] replace `panelGeneral` with our algorithm output
  hide the left sizer is ok?
- add background thread to `astri_leision.py`
- `sendMessage()` from `astri_leision.py` for histogram
  better send from thread
- remove `dicompyler/baseplugins/{dvh,quickopen}.*`
- also check code of `https://github.com/dicompyler/dicompyler-core`  
  DICOM parsing (with `pydicom`) done here
- are we using [wxWidgets/Phoenix](https://github.com/wxWidgets/Phoenix/)? (Yes, after wxPython4.0.0a2 version, Phoenix is the improved next-generation wxPython)

- add overlay to `2dview`
- add WC/WW to `2dview` (toolbar button/right click drag/Control drag?)  
  https://www.radiantviewer.com/dicom-viewer-manual/change_brightness_contrast.html

## dicomplyer study

- `dicomgui.py::DirectorySearchThread()` scan dcm files
  show as tree
- `dicomgui.py::GetPatientData()`
  update `patient["images"]` sort order:

  ```py
  # dicomgui.py::GetPatientData()
  image = dicomgui.patient["images"][i]  # dp.ds, DicomParser.FileDataset
  image.ImagePositionPatient, image.InstanceNumber, image.AcquisitionNumber
  ```

- histogram
  - shown before opening series
  - larger bin to make it a bar chart
  - show 2 back to back

## Workarounds

1. wx.StaticText set `wrap` with -1 to disable wrapping
2. different derived class from `XRC` for wx.Frame and wx.Panel  
   wx.Panel,

   ```py
   class PanelWelcome(wx.Panel):
       def __init__(self, parent, *args, **kw):
           wx.Panel.__init__(self, parent, *args, **kw)
           res = xrc.XmlResource(main_xrc_file)
           res.LoadPanel(self, parent, "panelWelcome")
   ```

   wx.Frame,

   ```py
   class FrameWelcome(wx.Frame):
       def __init__(self, parent, *args, **kw):
           wx.Frame.__init__(self)
           res = xrc.XmlResource(main_xrc_file)
           res.LoadFrame(self, parent, "frameWelcome")
   ```

3. vscode stuck in `analyzing in background`  
   set "python.jediEnabled": true
4. embed matplotlib in wxPython  
   You have a few different options available to you for embedding
   matplotlib in a wxPython application

   1. Embed one of the wxPython backend widgets (which subclass wx.Panel)
      directly and draw plots on it using matplotlib's object-oriented
      API. This approach is demonstrated by some of the examples
      embedding_in_wx\*.py

   2. Embed the PlotPanel from Matt Newville's `MPlot' package and draw
      plots on it using its plot() and oplot() methods.  
      <http://cars9.uchicago.edu/~newville/Python/MPlot/>

   3. Embed the PlotPanel from Ken McIvor wxmpl module and draw plots on
      it using the matplotlib's object-oriented API.  
      <http://agni.phys.iit.edu/~kmcivor/wxmpl/>

   Each of these approaches has different benefits and drawbacks, so I
   encourage you to evaluate each of them and select the one that best
   meets your needs.

5. when debug python code, error `ImportError: attempted relative import with no known parent package`  
   run as module

   ```sh
   python -m dicompyler.guihist
   ```

   [ImportError: attempted relative import with no known parent package](https://napuzba.com/a/import-error-relative-no-parent/p4)

6. refresh/redraw a mathplotlib figure in a wxpython panel

   ```py
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
   ```

   before `plot`,

   ```py
   self.axes.cla()
   ```

   doing `plot`,

   ```py
   self.axes.plot(x, y)
   ...
   self.axes.hist(array)
   ```

   after `plot`,

   ```py
   self.canvas.draw()
   self.canvas.Refresh()
   ```

7. convert a PIL Image into a numpy array

   ```py
   from PIL import Image
   import numpy as np
   im = Image.open('1.jpg')
   im2arr = np.array(im) # im2arr.shape: height x width x channel
   arr2im = Image.fromarray(im2arr)
   ```
