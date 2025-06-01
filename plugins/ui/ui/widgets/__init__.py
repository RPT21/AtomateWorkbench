# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/ui/src/ui/widgets/__init__.py
# Compiled at: 2004-11-19 01:53:56
import wx

class GradientLabel(wx.Window):
    __module__ = __name__

    def __init__(self, parent, color):
        wx.Window.__init__(self, parent, -1, size=wx.Size(-1, 10))
        self.label = ''
        self.cachedBackground = None
        self.color = color
        self.textColor = wx.BLACK
        self.font = self.GetFont()
        self.font.SetWeight(wx.BOLD)
        self.SetFont(self.font)
        self.cacheSize()
        self.createGradient()
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        return

    def cacheSize(self):
        self.size = self.GetTextExtent('H')
        self.SetSize(wx.Size(-1, self.size[1] + 4))

    def setColor(self, color):
        self.color = color
        cs = (
         color.Red(), color.Green(), color.Blue())
        if min(cs) < 100:
            self.textColor = wx.WHITE
        else:
            self.textColor = wx.BLACK
        self.createGradient()
        wx.CallAfter(self.Refresh)

    def createGradient(self):
        (w, h) = self.GetSize()
        self.cachedBackground = wx.Bitmap(w, h)
        dc = wx.MemoryDC()
        dc.SelectObject(self.cachedBackground)
        dc.SetBrush(wx.Brush(self.color))
        color = self.color
        startColour = [color.Red(), color.Green(), color.Blue()]
        start = color.Red()
        jump = 2
        height = h
        for i in range(0, height):
            dc.SetPen(wx.Pen(wx.Colour(startColour[0], startColour[1], startColour[2])))
            dc.DrawLine(0, i, w, i)
            if startColour[0] + jump < 255:
                startColour[0] += jump
            if startColour[1] + jump < 255:
                startColour[1] += jump
            if startColour[2] + jump < 255:
                startColour[2] += jump

        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.SetBrush(wx.Brush(wx.Colour(startColour[0], startColour[1], startColour[2])))

    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        dc.DrawBitmap(self.cachedBackground, 0, 0, False)
        dc.SetTextForeground(self.textColor)
        dc.SetFont(self.font)
        y = 2
        dc.DrawText(self.label, 2, y)

    def OnSize(self, event):
        self.createGradient()
        event.Skip()

    def SetLabel(self, label):
        self.label = label
