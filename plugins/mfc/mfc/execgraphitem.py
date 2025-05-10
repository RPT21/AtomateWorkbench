# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/mfc/src/mfc/execgraphitem.py
# Compiled at: 2004-11-19 02:30:59
import wx, os, plugins.graphview.graphview, math, random, plugins.executionengine.executionengine
import plugins.executionengine.executionengine.engine, plugins.core.core.utils.caching, plugins.poi.poi.utils.bufferedwindow
import logging
logger = logging.getLogger('mfc')

def graphViewFactory(plugin, perspective):
    return GraphView(plugin, perspective)


class GraphItem(object):
    __module__ = __name__

    def __init__(self, owner, device):
        self.cache = plugins.core.core.utils.caching.Cache(plugins.core.core.utils.caching.MEGABYTE, type(float))
        (self.width, self.height) = owner.GetSize()
        self.extensionLength = 10
        self.ly = -9999
        self.device = device
        self.owner = owner
        self.scalex = 1.0
        self.scaley = 1.0
        DEFAULT_WIDTH = 200
        self.range = self.device.getRange()
        MAX = self.owner.getMaxRange()
        self.defaultValues = (DEFAULT_WIDTH, MAX, 1.0, 1.0, 10)
        self.bestSize = (DEFAULT_WIDTH, MAX)
        self.spp = 1.0
        self.tpp = 1.0
        self.lastTime = 0
        self.timeRange = self.bestSize[0] * self.spp
        self.expandedTime = self.calcExpansion()
        self.setupOptions()
        self.calcTimePerPixel()

    def resize(self):
        (self.width, self.height) = self.owner.GetSize()
        self.calcTimePerPixel()

    def clear(self):
        self.cache.clear()
        self.spp = 1.0
        self.tpp = 1.0
        self.ly = -9999
        self.timeRange = self.bestSize[0] * self.spp
        self.scalex = self.defaultValues[2]
        self.scaley = self.defaultValues[3]
        self.extensionLength = self.defaultValues[4]
        self.range = self.device.getRange()
        self.gcf = self.device.getGCF()
        self.calcTimePerPixel()
        self.calcExpansion()
        wx.CallAfter(self.refresh)

    def setupOptions(self):
        self.linePen = wx.Pen(self.device.getPlotColor())

    def refresh(self):
        self.owner.refresh()

    def xdrawPoints(self, dc):
        pass

    def xdrawLatestPoint(self, dc):
        pass

    def calcExpansion(self):
        """Calculates the required expansion of the time scale based on the last available time and 
        expands it to self.extensionLength"""
        x = self.spp / self.extensionLength
        if self.timeRange < self.lastTime:
            self.timeRange = self.lastTime + self.extensionLength / self.spp
            self.calcTimePerPixel()

    def OnSize(self, event):
        plugins.poi.poi.utils.bufferedwindow.BufferedWindow.OnSize(self, event)
        (self.width, self.height) = self.GetSize()
        self.calcTimePerPixel()

    def GetSize(self):
        return self.owner.GetSize()

    def calcTimePerPixel(self):
        (w, h) = self.GetSize()
        self.tpp = h / float(self.device.getRange())
        self.spp = w / self.timeRange

    def drawPoints(self, dc):
        (px, py) = (
         -1, -1)
        dc.SetPen(self.linePen)
        for (time, temp) in self.cache.cache:
            y = self.owner.getY(self.compensate(temp))
            x = self.owner.getX(time)
            if px == -1:
                (px, py) = (
                 x, y)
            (nx, ny) = (x, y)
            dc.DrawLine(px, py, nx, y)
            (px, py) = (nx, ny)

        dc.SetPen(wx.NullPen)

    def drawLatestPoint(self, dc):
        li = len(self.cache.cache)
        if li < 2:
            return
        pen = self.cache.cache[li - 2]
        last = self.cache.cache[li - 1]
        dc.SetPen(self.linePen)
        dc.DrawLine(self.owner.getX(pen[0]), self.owner.getY(self.compensate(pen[1])), self.owner.getX(last[0]), self.owner.getY(self.compensate(last[1])))
        dc.SetPen(wx.NullPen)

    def compensate(self, flow):
        """Returns 0 if the value is less than 0.2%"""
        min = self.range * 0.02
        if flow <= min:
            return 0
        return flow

    def stabilize(self, y):
        factor = self.range * 0.02
        fy = y * factor
        if self.ly == -9999:
            self.ly = y
        if factor > abs(y - self.ly):
            return self.ly
        self.ly = y
        return y

    def update(self):
        self.setupOptions()
        wx.CallAfter(self.refresh)

    def addflow(self, time, flow):
        convflow = float(flow * self.range / 1000) * (self.gcf / 100.0)
        self.cache.addvalue(time, convflow)
        p = self.cache.getvalueindex(time)
        self.lastTime = time
        self.calcExpansion()
        self.update()


class GraphView(plugins.graphview.graphview.PanelView, plugins.poi.poi.utils.bufferedwindow.BufferedWindow):
    __module__ = __name__

    def __init__(self, owner, panel):
        self.devicePanels = {}
        self.maxRange = 500
        self.lastTime = 0
        self.spp = 1.0
        self.tpp = 1.0
        self.extensionLength = 10
        self.createUnitFont()
        self.devices = []
        (self.width, self.height) = (1, 1)
        self.createGraphBuffer()
        plugins.graphview.graphview.PanelView.__init__(self, owner, panel)
        plugins.poi.poi.utils.bufferedwindow.BufferedWindow.__init__(self, panel)
        self.createUI()
        self.engine = None
        self.SetSize(self.GetBestSize())
        plugins.executionengine.executionengine.getDefault().addEngineInitListener(self)

        class SizeHandler(wx.EvtHandler):
            __module__ = __name__

            def __init__(self, win):
                wx.EvtHandler.__init__(self)
                self.Bind(wx.EVT_SIZE, self.OnSize, win)

            def OnSize(self2, event):
                event.Skip()
                self.resizeChildren()

        self.PushEventHandler(SizeHandler(self))
        self.extensionLength = 10
        self.scalex = 1.0
        self.scaley = 1.0
        DEFAULT_WIDTH = 200
        MAX = 200
        self.defaultValues = (DEFAULT_WIDTH, MAX, 1.0, 1.0, 10)
        self.bestSize = (DEFAULT_WIDTH, MAX)
        self.lastTime = 0
        self.timeRange = self.bestSize[0] * self.spp
        self.expandedTime = self.calcExpansion()
        self.calcTimePerPixel()
        return

    def saveSnapshot(self, runlog):
        (ow, oh) = (self.width, self.height)
        self.height = 400
        self.width = 400
        self.createGraphBuffer()
        snapshot = wx.ImageFromBitmap(self.graphBuffer)
        (self.width, self.height) = (
         ow, oh)
        self.createGraphBuffer()
        name = os.path.join(runlog.getLocation(), '%s_mfc.jpg' % runlog.getName())
        snapshot.SaveFile(name, wx.BITMAP_TYPE_JPEG)

    def dispose(self):
        plugins.graphview.graphview.PanelView.dispose(self)
        for (device, panel) in self.devicePanels.items():
            self.removeDevice(device, False)

        plugins.executionengine.executionengine.getDefault().removeEngineInitListener(self)
        self.panel.removeGraphPanel(self)

    def createGraphBuffer(self):
        (w, h) = (
         self.width, self.height)
        if w == 0 or h == 0:
            (w, h) = (
             1, 1)
        self.graphBuffer = wx.EmptyBitmap(w, h)
        self.drawPoints()

    def drawBorder(self, dc):
        dc.SetPen(wx.LIGHT_GREY_PEN)
        dc.DrawRectangle(0, 0, self.width, self.height)
        dc.SetPen(wx.NullPen)

    def drawPoints(self):
        dc = wx.MemoryDC()
        dc.SelectObject(self.graphBuffer)
        dc.SetBackground(wx.Brush(wx.WHITE))
        dc.Clear()
        self.drawBorder(dc)
        self.drawRange(dc)
        map((lambda panel: panel.drawPoints(dc)), self.devicePanels.values())

    def drawLatestPoints(self):
        dc = wx.MemoryDC()
        dc.SelectObject(self.graphBuffer)
        map((lambda panel: panel.drawLatestPoint(dc)), self.devicePanels.values())

    def createUnitFont(self):
        self.unitFont = wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL)

    def resizeChildren(self):
        self.maxRange = self.calcMaxRange()
        (self.width, self.height) = self.GetSize()
        self.calcTimePerPixel()
        self.createGraphBuffer()
        map((lambda panel: panel.resize()), self.devicePanels.values())
        self.drawPoints()

    def calcMaxRange(self):
        max = 0
        for device in self.devices:
            if device.getRange() > max:
                max = device.getRange()

        if max is 0:
            max = 500
        self.maxRange = max
        self.calcTimePerPixel()
        return max

    def getMaxRange(self):
        return self.maxRange

    def calcTimePerPixel(self):
        (w, h) = self.GetSize()
        self.tpp = h / math.log(self.maxRange / 0.1)
        self.spp = w / self.timeRange

    def drawRange(self, dc):
        (w, h) = (
         self.width, self.height)
        dc.SetPen(wx.LIGHT_GREY_PEN)
        dc.SetFont(self.unitFont)
        dc.SetTextForeground(wx.LIGHT_GREY)
        if True:
            for device in self.devices:
                r = device.getRange()
                y = self.getY(r)
                dc.DrawLine(0, y, w, y)
                dc.DrawText(str(r), 0, y + 1)

        if False:
            dc.SetPen(wx.LIGHT_GREY_PEN)
            last = self.maxRange
            spiff = self.maxRange / 10
            i = spiff
            while i < last:
                y = self.getY(i)
                dc.DrawLine(0, y, w, y)
                i += spiff

            dc.SetPen(wx.NullPen)

    def getX(self, t):
        return int(t * self.spp)

    def getY(self, y1):
        (w, h) = self.GetSize()
        if y1 < 0.1:
            return h - 1
        out = int(h - (math.log(y1) * self.tpp - math.log(0.1) * self.tpp))
        if out >= h:
            return h - 1
        return out

    def Draw(self, dc):
        dc.BeginDrawing()
        dc.Clear()
        if False:
            dc.SetPen(wx.LIGHT_GREY_PEN)
            dc.DrawLine(self.width - self.extensionLength, 0, self.width - self.extensionLength, self.height)
        self.drawLatestPoints()
        dc.DrawBitmap(self.graphBuffer, 0, 0)
        dc.EndDrawing()

    def GetBestSize(self):
        return (
         200, 200)

    def engineInit(self, engine):
        self.engine = engine
        self.engine.addEngineListener(self)
        self.clearItems()

    def clearItems(self):
        for item in self.devicePanels.values():
            try:
                item.clear()
            except Exception as msg:
                logger.exception(msg)

        self.drawPoints()
        wx.CallAfter(self.Refresh)

    def engineEvent(self, event):
        eventType = event.getType()
        if eventType == plugins.executionengine.executionengine.engine.TYPE_ENDING:
            self.engine.removeEngineListener(self)
            return
        elif eventType == plugins.executionengine.executionengine.engine.TYPE_DEVICE_RESPONSE:
            replies = event.getData().getResponseByType('mfc')
            for reply in replies:
                self.lastTime = event.getData().getRecipeTime()
                self.calcExpansion()
                self.devicePanels[reply.getDevice()].addflow(self.lastTime, reply.getFlow())

    def refresh(self):
        self.Refresh()

    def createUI(self):
        self.panel.addGraphPanel(self)
        self.panel.refresh()

    def addDevice(self, device):
        plugins.graphview.graphview.PanelView.addDevice(self, device)
        self.calcMaxRange()
        p = GraphItem(self, device)
        self.devicePanels[device] = p
        self.resizeChildren()
        wx.CallAfter(self.Refresh)

    def removeDevice(self, device, refresh=True):
        plugins.graphview.graphview.PanelView.removeDevice(self, device)
        self.calcMaxRange()
        p = self.devicePanels[device]
        del self.devicePanels[device]
        if len(self.devicePanels.values()) == 0:
            plugins.graphview.graphview.getDefault().destroyDeviceGroup('mfc')
            plugins.executionengine.executionengine.getDefault().perspective.graphView.removeGraphPanel(self)
            plugins.executionengine.executionengine.getDefault().perspective.graphView.refresh()
            return
        self.resizeChildren()
        if refresh:
            wx.CallAfter(self.Refresh)

    def updateDevice(self, device):
        self.calcMaxRange()
        self.devicePanels[device].update()
        self.drawPoints()

    def clear(self):
        self.tpp = 1.0
        self.timeRange = self.bestSize[0] * self.spp
        self.scalex = self.defaultValues[2]
        self.scaley = self.defaultValues[3]
        self.extensionLength = self.defaultValues[4]
        self.calcTimePerPixel()
        self.calcExpansion()
        wx.CallAfter(self.Refresh)

    def calcExpansion(self):
        """Calculates the required expansion of the time scale based on the last available time and 
        expands it to self.extensionLength"""
        x = self.spp / self.extensionLength
        if self.timeRange < self.lastTime:
            self.timeRange = self.lastTime + self.extensionLength / self.spp
            self.calcTimePerPixel()
            self.drawPoints()
