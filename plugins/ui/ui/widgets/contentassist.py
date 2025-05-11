# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/ui/src/ui/widgets/contentassist.py
# Compiled at: 2004-09-21 03:06:59
import wx, ui.images

class ContentAssistant(object):
    __module__ = __name__

    def __init__(self, parent=None):
        self.control = None
        self.warning = False
        self.warningText = None
        self.image = ui.images.getImage(ui.images.ERROR_ICON)
        if parent is not None:
            self.createControl(parent)
        return

    def createControl(self, parent):
        self.control = wx.Panel(parent, -1, style=0)
        self.control.SetSize((self.image.GetWidth(), self.image.GetHeight()))
        self.control.SetBackgroundColour(parent.GetBackgroundColour())
        self.control.Hide()
        self.control.Bind(wx.EVT_PAINT, self.OnPaint)
        self.control.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        return self.control

    def OnPaint(self, event):
        event.Skip()
        dc = wx.PaintDC(self.control)
        if self.warning:
            dc.DrawBitmap(self.image, 0, 0, True)

    def OnMouseMotion(self, event):
        event.Skip()
        if not self.warning:
            return
        (w, h) = self.control.GetSize()
        (x, y) = self.control.ClientToScreen((0, 0))
        self.tp = wx.TipWindow(self.control, self.warningText, rectBound=wx.Rect(x, y, w, h))

    def getControl(self):
        return self.control

    def warn(self):
        self.warning = True
        self.update()

    def clear(self):
        self.warning = False
        self.update()

    def setWarning(self, text):
        self.warningText = text

    def update(self):
        wx.CallAfter(self.internalUpdate)

    def internalUpdate(self):
        try:
            if not self.control.IsShown() and self.warning:
                self.control.Show(self.warning)
            if not self.warning:
                self.control.Hide()
        except wx.PyDeadObjectError as msg:
            print(('Dead Object Error:', msg))
