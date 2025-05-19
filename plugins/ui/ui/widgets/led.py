# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/ui/src/ui/widgets/led.py
# Compiled at: 2004-11-04 21:38:28
import wx, plugins.poi.poi.utils.LEDdisplay
import plugins.poi.poi as poi

class LEDSetpointDisplay(wx.Panel):
    """LED Display with setpoint on top-right corner"""
    __module__ = __name__

    def __init__(self, *args, **kwargs):
        bgcolor = (
         0, 0, 0)
        fgcolor = (255, 255, 255)
        spfgcolor = (255, 255, 255)
        myargs = [
         'bgcolor', 'fgcolor']
        if 'bgcolor' in kwargs:
            bgcolor = kwargs['bgcolor']
            del kwargs['bgcolor']
        if 'fgcolor' in kwargs:
            fgcolor = kwargs['fgcolor']
            del kwargs['fgcolor']
        if 'spfgcolor' in kwargs:
            spfgcolor = kwargs['spfgcolor']
            del kwargs['spfgcolor']
        self.showSetpoint = False
        if 'showSetpoint' in kwargs:
            self.showSetpoint = kwargs['showSetpoint']
            del kwargs['showSetpoint']
        wx.Panel.__init__(self, *args, **kwargs)
        self.createUI()
        self.setBackgroundColor(bgcolor)
        self.setForegroundColor(fgcolor)
        self.setSetpointForegroundColor(spfgcolor)

    def createUI(self):
        self.valueCtrl = poi.utils.LEDdisplay.LEDDisplay(self, -1)
        if self.showSetpoint:
            self.setpointCtrl = poi.utils.LEDdisplay.LEDDisplay(self, -1, size=wx.Size(100, 25))
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.valueCtrl, 1, wx.EXPAND | wx.RIGHT | wx.ALIGN_RIGHT, 5)
        if self.showSetpoint:
            sizer.Add(wx.StaticLine(self, -1, style=wx.LI_VERTICAL), 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 1)
            hsizer = wx.BoxSizer(wx.VERTICAL)
            self.setpointLabel = wx.StaticText(self, -1, 'Setpoint')
            hsizer.Add(self.setpointLabel, 0, wx.EXPAND | wx.BOTTOM | wx.TOP, 2)
            hsizer.Add(self.setpointCtrl, 0, wx.ALL, 0)
            sizer.Add(hsizer, 0, wx.ALL | wx.EXPAND, 0)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)

    def setBackgroundColor(self, color):
        self.bgcolor = color
        self.SetBackgroundColour(wx.Color(*self.bgcolor))
        self.valueCtrl.setBackgroundColor(*color)
        if self.showSetpoint:
            self.setpointCtrl.setBackgroundColor(*color)
            if color[0] < 50 and color[1] < 50 and color[2] < 50:
                self.setpointLabel.SetForegroundColour(wx.WHITE)
            else:
                self.setpointLabel.SetForegroundColour(wx.BLACK)
        self.__internalUpdate()

    def setSetpointForegroundColor(self, color):
        if not self.showSetpoint:
            return
        self.spfgcolor = color
        self.setpointCtrl.setLEDColor(*color)
        self.__internalUpdate()

    def setForegroundColor(self, color):
        self.fgcolor = color
        self.valueCtrl.setLEDColor(*color)
        self.__internalUpdate()

    def setSetpointValue(self, value):
        if not self.showSetpoint:
            return
        self.setpointCtrl.SetValue(value)

    def setValue(self, value):
        self.valueCtrl.SetValue(value)

    def __internalUpdate(self):
        wx.CallAfter(self.Refresh)
