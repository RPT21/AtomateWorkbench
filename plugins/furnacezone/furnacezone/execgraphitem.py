# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/furnacezone/src/furnacezone/execgraphitem.py
# Compiled at: 2004-11-16 19:14:29
import wx, os, plugins.graphview.graphview, math, plugins.executionengine.executionengine, plugins.executionengine.executionengine.engine
import plugins.core.core.utils.caching, plugins.poi.poi.utils.bufferedwindow, time, logging
logger = logging.getLogger('furnacezone.graphview')

def graphViewFactory(plugin, perspective):
    return GraphView(plugin, perspective)


class GraphItem(wx.Panel):
    __module__ = __name__

    def __init__(self, parent, owner, device):
        wx.Panel.__init__(self, parent)
        self.SetBackgroundColour(wx.WHITE)
        self.cache = core.utils.caching.Cache(core.utils.caching.MEGABYTE, type(int))
        (self.width, self.height) = (0, 0)
        self.extensionLength = 10
        self.setpoint = 0
        self.setpointColor = wx.Color(200, 200, 240)
        self.setpointPen = wx.Pen(self.setpointColor, 1)
        self.createSetpointFont()
        self.spp = 1.0
        self.tpp = 1.0
        self.lastTemp = (-1, -1)
        self.lastSize = (-1, -1)
        self.device = device
        self.owner = owner
        self.ly = 0.0
        self.scalex = 1.0
        self.scaley = 1.0
        DEFAULT_WIDTH = 200
        self.defaultValues = (DEFAULT_WIDTH, 200, 1.0, 1.0, 10)
        self.bestSize = (DEFAULT_WIDTH, 200)
        self.lastTime = 0
        self.timeRange = self.bestSize[0] * self.spp
        self.expandedTime = self.calcExpansion()
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.calcTimePerPixel()
        self.createGraphBuffer()
        self.canvas = poi.utils.bufferedwindow.BufferedWindow(self)
        self.canvas.Draw = self.Draw
        self.canvas.handleResize = self.handleResize
        self.label = wx.StaticText(self, -1, device.getLabel())
        self.label.SetBackgroundColour(wx.LIGHT_GREY)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.label, 0, wx.GROW | wx.LEFT | wx.TOP, 5)
        sizer.Add(wx.StaticLine(self, -1), 0, wx.GROW, wx.ALL, 0)
        sizer.Add(self.canvas, 1, wx.GROW | wx.ALL, 0)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)

    def createGraphBuffer(self):
        (w, h) = (
         self.width, self.height)
        if self.width == 0 or self.height == 0:
            (w, h) = (
             1, 1)
        self.graphBuffer = wx.EmptyBitmap(w, h)
        self.recreateGraphBuffer()

    def saveSnapshot(self, width, height):
        (ow, oh) = (
         self.width, self.height)
        self.width = width
        self.height = height
        self.graphBuffer = wx.EmptyBitmap(self.width, self.height)
        self.recreateGraphBuffer()
        snapshot = wx.ImageFromBitmap(self.graphBuffer)
        (self.width, self.height) = (
         ow, oh)
        self.createGraphBuffer()
        return snapshot

    def recreateGraphBuffer(self):
        """Creates a dc to draw the graph onto"""
        dc = wx.MemoryDC()
        dc.SelectObject(self.graphBuffer)
        self.drawPoints(dc)

    def createSetpointFont(self):
        self.setpointFont = wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL)

    def clear(self):
        self.cache.clear()
        self.spp = 1.0
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
            self.recreateGraphBuffer()

    def handleResize(self):
        (self.width, self.height) = self.canvas.GetSize()
        self.calcTimePerPixel()
        self.createGraphBuffer()

    def OnSize(self, event):
        event.Skip()

    def calcTimePerPixel(self):
        (w, h) = (
         self.width, self.height)
        self.tpp = h / float(self.device.getRange() + 50)
        self.spp = w / self.timeRange

    def Draw(self, dc):
        dc.BeginDrawing()
        dc.Clear()
        dc.DrawBitmap(self.graphBuffer, 0, 0, False)

    def drawSetpoint(self, dc):
        sp = self.setpoint
        if sp == 0:
            sp = 1
        dc.SetPen(self.setpointPen)
        sp = self.height - sp * self.tpp
        dc.SetTextForeground(self.setpointColor)
        dc.SetFont(self.setpointFont)
        dc.DrawLine(0, sp, self.width, sp)
        s = 'Setpoint %d' % self.setpoint
        (w, h) = dc.GetTextExtent(s)
        where = sp + 1
        if sp + 1 + h > self.height:
            where = sp - 1 - h
        dc.DrawText(s, 10, where)
        if False:
            dc.SetPen(wx.LIGHT_GREY_PEN)
            dc.DrawLine(self.width - self.extensionLength, 0, self.width - self.extensionLength, self.height)
        dc.SetPen(wx.Pen(wx.LIGHT_GREY, style=wx.DOT))
        r = self.height - self.device.getRange() * self.tpp
        dc.DrawLine(0, r, self.width, r)
        dc.EndDrawing()

    def incrementPoint(self, dc):
        """Only draw the very last segment"""
        li = len(self.cache.cache)
        if li <= 2:
            return
        latest = self.cache.cache[li - 1]
        prev = self.cache.cache[li - 2]
        dc.SetPen(wx.RED_PEN)
        h = self.height
        dc.DrawLine(prev[0] * self.spp, h - prev[1] * self.tpp, latest[0] * self.spp, h - latest[1] * self.tpp)

    def drawPoints(self, dc):
        dc.SetBackground(wx.Brush(wx.WHITE))
        dc.Clear()
        self.drawSetpoint(dc)
        if len(self.cache.cache) < 2:
            return
        p = self.cache.cache[0]
        (px, py) = (p[0] * self.spp, p[1] * self.tpp)
        dc.SetPen(wx.RED_PEN)
        start = time.time()
        for (t, temp) in self.cache.cache:
            (nx, ny) = (t * self.spp, temp * self.tpp)
            dc.DrawLine(px, self.height - py, nx, self.height - ny)
            (px, py) = (nx, ny)

    def addLatestPoint(self):
        dc = wx.MemoryDC()
        dc.SelectObject(self.graphBuffer)
        self.incrementPoint(dc)

    def GetBestSize(self):
        return self.bestSize

    def updateDevice(self):
        self.label.SetLabel(self.device.getLabel())

    def update(self):
        wx.CallAfter(self.Refresh)

    def addtemperature(self, t, temperature):
        self.cache.addvalue(t, temperature)
        p = self.cache.getvalueindex(t)
        self.lastTime = t
        self.calcExpansion()
        self.addLatestPoint()
        self.update()

    def setSetpoint(self, entry):
        self.setpoint = entry.getSetpoint()
        self.recreateGraphBuffer()


class GraphView(plugins.graphview.graphview.PanelView):
    __module__ = __name__

    def __init__(self, owner, panel):
        plugins.graphview.graphview.PanelView.__init__(self, owner, panel)
        self.createUI(owner, panel)
        self.devicePanels = {}
        self.engine = None
        executionengine.getDefault().addEngineInitListener(self)
        return

    def engineInit(self, engine):
        self.engine = engine
        self.engine.addEngineListener(self)
        self.clearItems()

    def dispose(self):
        graphview.PanelView.dispose(self)
        for (device, panel) in self.devicePanels.items():
            self.removeDevice(device, False)

        self.panel.removeGraphPanel(self.p)
        executionengine.getDefault().removeEngineInitListener(self)

    def saveSnapshot(self, runlog):
        for (device, panel) in self.devicePanels.items():
            img = panel.saveSnapshot(400, 400)
            name = os.path.join(runlog.getLocation(), '%s_%s.jpg' % (runlog.getName(), panel.device.getID()))
            img.SaveFile(name, wx.BITMAP_TYPE_JPEG)

    def clearItems(self):
        map((lambda s: s.clear()), self.devicePanels.values())

    def engineEvent(self, event):
        eventType = event.getType()
        if eventType == executionengine.engine.TYPE_ENDING:
            self.engine.removeEngineListener(self)
            return
        elif eventType == executionengine.engine.TYPE_DEVICE_RESPONSE:
            replies = event.getData().getResponseByType('furnacezone')
            for reply in replies:
                self.devicePanels[reply.getDevice()].addtemperature(event.getData().getRecipeTime(), reply.getTemperature())

        elif eventType == executionengine.engine.TYPE_SETTING_STEP_GOALS:
            self.setStepGoals(event.getData())

    def setStepGoals(self, step):
        for (device, panel) in self.devicePanels.items():
            devIdx = self.engine.recipe.getDeviceIndex(device)
            devEntry = step.getEntry(devIdx)
            panel.setSetpoint(devEntry)

    def createUI(self, owner, panel):
        self.p = wx.Panel(panel, -1)
        self.p.SetBackgroundColour(wx.Color(60, 60, 60))
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.p.SetSizer(self.sizer)
        self.p.SetAutoLayout(True)
        self.panel.addGraphPanel(self.p)

    def addDevice(self, device):
        graphview.PanelView.addDevice(self, device)
        p = GraphItem(self.p, self, device)
        self.devicePanels[device] = p
        self.sizer.Add(p, 1, wx.GROW | wx.ALL, 1)
        self.p.GetSizer().SetItemMinSize(p, p.GetBestSize())
        self.p.GetContainingSizer().SetItemMinSize(p, p.GetSize())
        self.panel.refresh()

    def removeDevice(self, device, refresh=True):
        graphview.PanelView.removeDevice(self, device)
        p = self.devicePanels[device]
        self.sizer.Remove(p)
        self.p.RemoveChild(p)
        p.Destroy()
        del self.devicePanels[device]
        if len(self.devicePanels.values()) == 0:
            graphview.getDefault().destroyDeviceGroup('furnacezone')
            executionengine.getDefault().perspective.graphView.refresh()
            return
        if refresh:
            wx.CallAfter(self.p.Layout)
            self.panel.refresh()

    def updateDevice(self, device):
        self.devicePanels[device].updateDevice()
