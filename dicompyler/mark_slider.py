#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import wx
from typing import List, Dict

def fraction_to_value(fraction, min_value, max_value):
    return (max_value - min_value) * fraction + min_value


def value_to_fraction(value, min_value, max_value):
    return float(value - min_value) / (max_value - min_value)


class SliderThumb:
    def __init__(self, parent, value: int, shape: str="circle"):
        self.parent = parent
        self.dragged = False
        self.mouse_over = False

        track_height = self.parent.track_height
        
        if shape == "arrow":
            self.shape = "arrow"
        else:
            self.shape = "circle"

        if self.shape == "arrow":
            # arrow thumb
            self.thumb_poly = ((0, 0), (0, 13), (5, 18), (10, 13), (10, 0))
            self.thumb_shadow_poly = ((0, 14), (4, 18), (6, 18), (10, 14))
            min_coords = [float("Inf"), float("Inf")]
            max_coords = [-float("Inf"), -float("Inf")]
            for pt in list(self.thumb_poly) + list(self.thumb_shadow_poly):
                for i_coord, coord in enumerate(pt):
                    if coord > max_coords[i_coord]:
                        max_coords[i_coord] = coord
                    if coord < min_coords[i_coord]:
                        min_coords[i_coord] = coord
            self.size = (max_coords[0] - min_coords[0], max_coords[1] - min_coords[1])
        elif self.shape == "circle":
            # circle thumb
            self.thumb_circle_radius = int(track_height/2)
            self.thumb_shadow_circle_radius = int(track_height/2) + 1
            self.size = (track_height + 1, track_height + 1)
        else:
            print("unknown shape")
        
        
        self.value = value

        # thumb colour
        self.normal_color = wx.Colour((0, 120, 215))
        self.normal_shadow_color = wx.Colour((120, 180, 228))
        self.dragged_color = wx.Colour((204, 204, 204))
        self.dragged_shadow_color = wx.Colour((222, 222, 222))
        self.mouse_over_color = wx.Colour((23, 23, 23))
        self.mouse_over_shadow_color = wx.Colour((132, 132, 132))

        if self.parent.style == wx.SL_HORIZONTAL:
            self.h = True
            self.v = False
        else:
            self.v = True
            self.h = False

    def GetPosition(self):
        min_x = self.GetMin()
        max_x = self.GetMax()
        parent_size = self.parent.GetSize()
        min_value = self.parent.GetMin()
        max_value = self.parent.GetMax()
        fraction = value_to_fraction(self.value, min_value, max_value)
        if self.h:
            pos = (fraction_to_value(fraction, min_x, max_x), parent_size[1] / 2 + 1)
        else:
            pos = (parent_size[0] / 2, fraction_to_value(fraction, min_x, max_x))
        return pos

    def SetPosition(self, pos):
        if self.h:
            pos_x = pos[0]

            # Limit movement by slider boundaries
            min_x = self.GetMin()
            max_x = self.GetMax()
            pos_x = min(max(pos_x, min_x), max_x)

            fraction = value_to_fraction(pos_x, min_x, max_x)
            value = fraction_to_value(
                fraction, self.parent.GetMin(), self.parent.GetMax()
            )
            # Post event notifying that position changed
            self.SetValue(value)
        else:
            pos_y = pos[1]
            
            # Limit movement by slider boundaries
            min_x = self.GetMin()
            max_x = self.GetMax()
            pos_y = min(max(pos_y, min_x), max_x)

            fraction = value_to_fraction(pos_y, min_x, max_x)
            value = fraction_to_value(
                fraction, self.parent.GetMin(), self.parent.GetMax()
            )
            self.SetValue(value)


    def GetValue(self):
        return self.value

    def SetValue(self, value):
        value = int(value)
        if self.value != value:
            self.value = value
            # Post event notifying that value changed
            self.PostEvent()

    def PostEvent(self):
        event = wx.PyCommandEvent(wx.EVT_SLIDER.typeId, self.parent.GetId())
        event.SetEventObject(self.parent)
        wx.PostEvent(self.parent.GetEventHandler(), event)
        
        print(f"PostEvent {self.parent.GetValue()}")

    def GetMin(self):
        if self.h:
            min_x = self.parent.border_width + self.size[0] / 2
        else:
            min_x = self.parent.border_width + self.size[1] / 2

        return min_x

    def GetMax(self):
        parent_size = self.parent.GetSize()
        if self.h:
            max_x = parent_size[0] - self.parent.border_width - self.size[0] / 2
        else:
            max_x = parent_size[1] - self.parent.border_width - self.size[1] / 2
        return max_x

    def IsMouseOver(self, mouse_pos):
        in_hitbox = True
        my_pos = self.GetPosition()
        for i_coord, mouse_coord in enumerate(mouse_pos):
            boundary_low = my_pos[i_coord] - self.size[i_coord] / 2
            boundary_high = my_pos[i_coord] + self.size[i_coord] / 2
            in_hitbox = in_hitbox and (boundary_low <= mouse_coord <= boundary_high)
        return in_hitbox

    def OnPaint(self, dc):
        if self.dragged or not self.parent.IsEnabled():
            thumb_color = self.dragged_color
            thumb_shadow_color = self.dragged_shadow_color
        elif self.mouse_over:
            thumb_color = self.mouse_over_color
            thumb_shadow_color = self.mouse_over_shadow_color
        else:
            thumb_color = self.normal_color
            thumb_shadow_color = self.normal_shadow_color
        my_pos = self.GetPosition()

        # Draw thumb shadow (or anti-aliasing effect)
        dc.SetBrush(wx.Brush(thumb_shadow_color, style=wx.BRUSHSTYLE_SOLID))
        dc.SetPen(wx.Pen(thumb_shadow_color, width=1, style=wx.PENSTYLE_SOLID))
        if self.shape == "arrow":
            dc.DrawPolygon(
                points=self.thumb_shadow_poly,
                xoffset=int(my_pos[0] - self.size[0] / 2),
                yoffset=int(my_pos[1] - self.size[1] / 2),
            )
        elif self.shape == "circle":
            dc.DrawCircle(
                x=int(my_pos[0]),
                y=int(my_pos[1]),
                radius=self.thumb_shadow_circle_radius,
            )

        # Draw thumb itself
        dc.SetBrush(wx.Brush(thumb_color, style=wx.BRUSHSTYLE_SOLID))
        dc.SetPen(wx.Pen(thumb_color, width=1, style=wx.PENSTYLE_SOLID))
        if self.shape == "arrow":
            dc.DrawPolygon(
                points=self.thumb_poly,
                xoffset=int(my_pos[0] - self.size[0] / 2),
                yoffset=int(my_pos[1] - self.size[1] / 2),
            )
        elif self.shape == "circle":
            dc.DrawCircle(
                x=int(my_pos[0]),
                y=int(my_pos[1]),
                radius=self.thumb_circle_radius,
            )

"""
Custom Widget
"""

class MarkSlider(wx.Panel):
    def __init__(
        self,
        parent,
        id=wx.ID_ANY,
        value=None,
        minValue=0,
        maxValue=100,
        border_width=0,
        pos=wx.DefaultPosition,
        size=wx.DefaultSize,
        style=wx.SL_HORIZONTAL,
        validator=wx.DefaultValidator,
        name="markSlider",
    ):
        super().__init__(parent=parent, id=id, pos=pos, size=(-1, -1), name=name)

        # Intialize properties
        # orientation: horizontal or vertical
        self.style = None
        if style == wx.SL_HORIZONTAL:
            self.style = wx.SL_HORIZONTAL
        elif style == wx.SL_VERTICAL:
            self.style = wx.SL_VERTICAL
        else:
            raise NotImplementedError("Styles not implemented")
        
        if validator != wx.DefaultValidator:
            raise NotImplementedError("Validator not implemented")
        
        # track height
        self.track_height = 12

        # min size
        if style == wx.SL_HORIZONTAL:
            self.SetMinSize(size=(max(50, size[0]), max(self.track_height+4, size[1])))
        else:
            self.SetMinSize(size=(max(self.track_height+4, size[0]), max(50, size[1])))

        # min/max value
        if minValue > maxValue:
            minValue, maxValue = maxValue, minValue
        self.min_value = minValue
        self.max_value = maxValue

        # value
        if value is None:
            value = self.min_value
        self.value = value

        # border width
        self.border_width = border_width
        
        # ranges
        self.ranges = []

        # Thumb
        self.thumb = SliderThumb(parent=self, value=value)

        # Aesthetic definitions
        self.slider_background_color = wx.Colour((231, 234, 234))
        self.slider_outline_color = wx.Colour((214, 214, 214))
        self.range_color = wx.Colour((220, 20, 60))
        self.range_outline_color = wx.Colour((220, 20, 60))

        # Bind events
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnMouseUp)
        self.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.Bind(wx.EVT_MOUSE_CAPTURE_LOST, self.OnMouseLost)
        self.Bind(wx.EVT_ENTER_WINDOW, self.OnMouseEnter)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouseLeave)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        self.Bind(wx.EVT_SIZE, self.OnResize)
        
    def Enable(self, enable=True):
        super().Enable(enable)
        self.Refresh()

    def Disable(self):
        super().Disable()
        self.Refresh()

    def SetValueFromMousePosition(self, click_pos):
        #if self.thumb.dragged:
        self.thumb.SetPosition(click_pos)

    def OnMouseDown(self, event):
        #print(f"OnMouseDown {event}")
        if not self.IsEnabled():
            return
        click_pos = event.GetPosition()
        if self.thumb.IsMouseOver(click_pos):
            self.thumb.dragged = True
            self.thumb.mouse_over = False
        self.SetValueFromMousePosition(click_pos)
        self.CaptureMouse()
        self.Refresh()

    def OnMouseUp(self, event):
        #print(f"OnMouseUp {event}")
        if not self.IsEnabled():
            return
        self.SetValueFromMousePosition(event.GetPosition())
        self.thumb.dragged = False
        if self.HasCapture():
            self.ReleaseMouse()
        self.Refresh()

    def OnMouseLost(self, event):
        #print(f"OnMouseLost {event}")
        self.thumb.dragged = False
        self.thumb.mouse_over = False
        self.Refresh()

    def OnMouseMotion(self, event):
        #print(f"OnMouseMotion {event.GetPosition()}")
        if not self.IsEnabled():
            return
        refresh_needed = False
        mouse_pos = event.GetPosition()
        if event.Dragging() and event.LeftIsDown():
            self.SetValueFromMousePosition(mouse_pos)
            refresh_needed = True
        else:
            old_mouse_over = self.thumb.mouse_over
            self.thumb.mouse_over = self.thumb.IsMouseOver(mouse_pos)
            if old_mouse_over != self.thumb.mouse_over:
                refresh_needed = True
        if refresh_needed:
            self.Refresh()

    def OnMouseEnter(self, event):
        #print(f"OnMouseEnter {event}")
        if not self.IsEnabled():
            return
        mouse_pos = event.GetPosition()
        if self.thumb.IsMouseOver(mouse_pos):
            self.thumb.mouse_over = True
            self.Refresh()

    def OnMouseLeave(self, event):
        #print(f"OnMouseLeave {event}")
        if not self.IsEnabled():
            return
        self.thumb.mouse_over = False
        self.Refresh()

    def OnResize(self, event):
        self.Refresh()

    def OnPaint(self, event):
        w, h = self.GetSize()
        #print(f"size: {w}*{h}")
        # BufferedPaintDC should reduce flickering
        dc = wx.BufferedPaintDC(self)
        background_brush = wx.Brush(self.GetBackgroundColour(), wx.SOLID)
        dc.SetBackground(background_brush)
        dc.Clear()

        # 1. Draw slider
        track_height = self.track_height

        dc.SetPen(wx.Pen(self.slider_outline_color, width=1, style=wx.PENSTYLE_SOLID))
        dc.SetBrush(wx.Brush(self.slider_background_color, style=wx.BRUSHSTYLE_SOLID))
        #print(f"w,h {w},{h}")

        if self.style == wx.SL_HORIZONTAL:
            slider_x = self.border_width
            slider_y = int(h / 2 - track_height / 2)
            slider_w = int(w - 2 * self.border_width)
            slider_h = track_height
        else:
            slider_x = int(w / 2 - track_height / 2)
            slider_y = self.border_width
            slider_w = track_height
            slider_h = int(h - 2 * self.border_width)

        dc.DrawRectangle(slider_x, slider_y, slider_w, slider_h)
        
        # 2. Draw ranges
        if self.IsEnabled():
            dc.SetPen(
                wx.Pen(
                    self.range_outline_color, width=1, style=wx.PENSTYLE_SOLID
                )
            )
            dc.SetBrush(wx.Brush(self.range_color, style=wx.BRUSHSTYLE_SOLID))
        else:
            dc.SetPen(
                wx.Pen(self.slider_outline_color, width=1, style=wx.PENSTYLE_SOLID)
            )
            dc.SetBrush(wx.Brush(self.slider_outline_color, style=wx.BRUSHSTYLE_SOLID))


        min_value = self.GetMin()
        max_value = self.GetMax()

        if self.style == wx.SL_HORIZONTAL:
            min_pos = self.border_width
            max_pos = w -self.border_width
        else:
            min_pos = self.border_width
            max_pos = h -self.border_width

        for r in self.ranges:
            start_value = r["start_value"]
            end_value = r["end_value"]
            start_pos = fraction_to_value(value_to_fraction(start_value, min_value, max_value), min_pos, max_pos)
            end_pos = fraction_to_value(value_to_fraction(end_value, min_value, max_value), min_pos, max_pos)
            
            if self.style == wx.SL_HORIZONTAL:
                r_x = int(start_pos)
                r_y = int(h / 2 - track_height / 4)
                r_w = int(end_pos - start_pos)
                r_h = int(track_height / 2)
            else:
                r_x = int(w / 2 - track_height / 4)
                r_y = int(start_pos)
                r_w = int(track_height / 2)
                r_h = int(end_pos - start_pos)
            
            dc.DrawRectangle(r_x, r_y, r_w, r_h)

        # 3. Draw thumb
        self.thumb.OnPaint(dc)

        event.Skip()

    def OnEraseBackground(self, event):
        # This should reduce flickering
        pass

    def GetValue(self):
        return self.thumb.value

    def SetValue(self, value):
        # Limit value
        value = min(max(value, self.min_value), self.max_value)
        self.thumb.SetValue(value)
        self.Refresh()

    def GetMax(self):
        return self.max_value

    def GetMin(self):
        return self.min_value

    def SetMax(self, maxValue):
        if maxValue < self.min_value:
            maxValue = self.min_value
        self.max_value = maxValue
        value = self.GetValue()
        self.SetValue(value)
        self.Refresh()

    def SetMin(self, minValue):
        if minValue > self.max_value:
            minValue = self.max_value
        self.min_value = minValue
        value = self.GetValue()
        self.SetValue(value)
        self.Refresh()

    def SetRange(self, startValue, endValue=None):
        if (endValue is None) or (startValue > endValue):
            endValue = startValue
        self.ranges.append({"start_value": startValue, "end_value": endValue})
        self.Refresh()

    def SetRanges(self, ranges: List):
        """[summary]
        
        Arguments:
            ranges {List} -- [[100,120], [200,210]...]
        """

        for v in ranges:
            if len(v) == 1:
                v[1] = v[0]
            elif len(v) == 2:
                if v[1] < v[0]:
                    v[1] = v[0]
            else:
                continue

            v[0] = min(max(v[0], self.min_value), self.max_value)
            v[1] = min(max(v[1], self.min_value), self.max_value)

            self.ranges.append({"start_value": v[0], "end_value": v[1]})

        self.Refresh()


class TestFrame(wx.Frame):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

        self.InitUI()

    def InitUI(self):

        panel = wx.Panel(self)

        hbox = wx.BoxSizer(orient=wx.HORIZONTAL)

        # Regular Slider
        self.slider = wx.Slider(
            panel,
            value=200,
            minValue=150,
            maxValue=500,
            style=wx.SL_VERTICAL | wx.SL_INVERSE,
        )
        hbox.Add(self.slider, proportion=1, flag=wx.EXPAND | wx.ALL)

        # StaticText to show
        self.txt = wx.StaticText(panel, label="200")
        hbox.Add(self.txt, proportion=0, flag=wx.TOP | wx.RIGHT)

        # Custom Slider
        self.mark_slider = MarkSlider(
            panel, value=200, minValue=0, maxValue=500, size=(-1, 300), style = wx.SL_VERTICAL
        )
        self.mark_slider.SetRange(100, 110)
        self.mark_slider.SetRanges([[200, 240], [300, 340]])

        hbox.Add(self.mark_slider, proportion=0, flag=wx.EXPAND | wx.ALL)

        # StaticText to show Custom Slider Value
        self.mark_slider_txt = wx.StaticText(panel, label="200")
        hbox.Add(self.mark_slider_txt, proportion=0, flag=wx.TOP | wx.RIGHT)

        panel.SetSizer(hbox)

        self.SetTitle("wx.Slider")
        self.Centre()

        # Bind events
        self.slider.Bind(wx.EVT_SCROLL, self.OnSliderScroll)
        self.mark_slider.Bind(wx.EVT_SLIDER, self.OnMarkSliderScroll)


    def OnSliderScroll(self, e):

        obj = e.GetEventObject()
        val = obj.GetValue()

        self.txt.SetLabel(str(val))


    def OnMarkSliderScroll(self, e):
        print("OnMarkSliderScroll")
        obj = e.GetEventObject()
        val = obj.GetValue()

        self.mark_slider_txt.SetLabel(str(val))


def main():
    app = wx.App()
    frame = TestFrame(None)
    frame.Show()
    app.MainLoop()


if __name__ == "__main__":
    main()
