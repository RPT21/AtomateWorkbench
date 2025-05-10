# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/labbooks/src/labbooks/graphs.py
# Compiled at: 2004-09-30 21:45:55


class GraphItem(object):
    __module__ = __name__

    def __init__(self, owner):
        self.owner = owner

    def draw(self, timespan, dc):
        """timespan is tuple with (start, end)"""
        dc.DrawRectangle(0, 0, 30, 30)


class GraphPanel(wx.Window):
    __module__ = __name__

    def __init__(self, parent):
        wx.Window.__init__(self, parent, -1)
        self.SetBackgroundColour(wx.RED)
        self.items = []
        self.canvas = wx.Window(self, -1)
        self.canvasBuffer = None
        self.createBuffer()
        self.Bind(wx.EVT_SIZE, self.canvas.OnSize)
        self.Bind(wx.EVT_PAINT, self.canvas.OnPaint)
        return

    def OnPaint(self, event):
        dc = wx.BufferedPaintDC(self.canvas, self.canvasBuffer)

    def OnSize(self, event):
        event.Skip()
        self.createBuffer()
        self.updateDrawing()

    def createBuffer(self):
        (w, h) = self.canvas.GetSize()
        self.canvasBuffer = wx.EmptyBitmap(w, h)
        self.updateDrawing()

    def updateDrawing(self):
        dc = wx.BufferedPaintDC(wx.ClientDC(self.canvas), self.canvasBuffer)
        self.draw(dc)

    def draw(self, dc):
        dc.DrawRectangle(0, 0, 100, 100)

    def addItem(self, item):
        self.items.append(item)

    def removeItem(self, item):
        self.items.remove(item)


class GraphManager(object):
    __module__ = __name__

    def __init__(self):
        self.graphPanels = []
        self.hookToModel()
        self.hookToExecution()

    def hookToModel(self):
        pass

    def hookToExecution(self):
        pass
