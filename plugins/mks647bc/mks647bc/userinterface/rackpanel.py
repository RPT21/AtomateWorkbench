# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/mks647bc/src/mks647bc/userinterface/rackpanel.py
# Compiled at: 2004-07-24 10:26:33
import wx, wx.gizmos

class MKS647RackPanel(object):
    __module__ = __name__

    def __init__(self, hwinst):
        self.hwinst = hwinst
        self.control = None
        return

    def createControl(self, parent):
        self.control = wx.Panel(parent, -1)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.channelNums = []
        for i in range(4):
            led = wx.gizmos.LEDNumberCtrl(self.control, -1, size=(200, 40))
            led.SetDrawFaded(True)
            led.SetAlignment(wx.gizmos.LED_ALIGN_RIGHT)
            led.SetValue('12345')
            self.channelNums.append(led)
            sizer.Add(led, 0, wx.GROW | wx.ALL, 5)

        sizer.Fit(control)
        self.control.SetSizer(sizer)
        self.control.SetAutoLayout(True)
        return self.control
