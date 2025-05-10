# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/poi/src/poi/utils/bufferedwindow.py
# Compiled at: 2005-06-10 18:51:25
import wx

class BufferedWindow(wx.Window):
    __module__ = __name__

    def __init__(self, parent, useBufferedDC=True):
        wx.Window.__init__(self, parent, -1)
        self.useBufferedDC = useBufferedDC
        self.Bind(wx.EVT_PAINT, self.OnPaint)

        class SizeHandler(wx.EvtHandler):
            __module__ = __name__

            def __init__(innerself):
                wx.EvtHandler.__init__(innerself)
                innerself.Bind(wx.EVT_SIZE, self.OnSize, self)

        self.PushEventHandler(SizeHandler())
        (self.width, self.height) = (0, 0)
        self.createBuffer()

    def handleResize(self):
        pass

    def createBuffer(self):
        (self.width, self.height) = self.GetClientSizeTuple()
        self._buffer = wx.EmptyBitmap(self.width, self.height)
        self.updateDrawing()

    def updateDrawing(self):
        if self.useBufferedDC:
            dc = wx.BufferedDC(wx.ClientDC(self), self._buffer)
            self.Draw(dc)
        else:
            dc = wx.MemoryDC()
            dc.SelectObject(self._buffer)
            self.Draw(dc)
            wx.ClientDC(self).Blit(0, 0, self.width, self.height, dc, 0, 0)

    def OnSize(self, event):
        event.Skip()
        self.createBuffer()
        self.handleResize()

    def OnPaint(self, event):
        event.Skip()
        if self.useBufferedDC:
            dc = wx.BufferedPaintDC(self, self._buffer)
        else:
            dc = wx.PaintDC(self)
            dc.DrawBitmap(self._buffer, 0, 0)
        self.Draw(dc)

    def Draw(self, dc):
        pass
