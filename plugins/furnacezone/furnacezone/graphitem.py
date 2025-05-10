# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/furnacezone/src/furnacezone/graphitem.py
# Compiled at: 2004-11-19 21:59:47
import wx, grapheditor.contributor, grideditor.recipemodel, executionengine, logging
logger = logging.getLogger('furnacezone.ui.graphitem')

class FurnaceZoneGraphItem(grapheditor.contributor.GraphContributor):
    __module__ = __name__

    def __init__(self):
        grapheditor.contributor.GraphContributor.__init__(self)
        self.facecolor = wx.SystemSettings_GetColour(wx.SYS_COLOUR_BTNFACE)
        self.setTitle('')
        self.engine = None
        self.events = []
        self.maxRange = 1000
        return

    def engineInit(self, engine):
        self.engine = engine
        self.engine.addEngineListener(self)

    def engineEvent(self, event):
        if event.getType() == executionengine.engine.TYPE_ENDING:
            self.engine.removeEngineListener(self)

    def setDevice(self, device):
        grapheditor.contributor.GraphContributor.setDevice(self, device)
        self.updateDeviceInfo()
        self.populateEvents()

    def prepareItem(self, owner, recipeModel):
        grapheditor.contributor.GraphContributor.prepareItem(self, owner, recipeModel)
        recipeModel.addModifyListener(self)

    def populateEvents(self):
        recipeModel = self.recipeModel
        steps = recipeModel.getSteps()
        if self.device is None:
            return
        for step in steps:
            entry = recipeModel.getEntryAtStep(step, self.device)
            self.events.append((entry.getSetpoint(), step.getDuration() * 1000))

        return

    def recipeModelChanged(self, event):
        if event.getEventType() == grideditor.recipemodel.CHANGE_DEVICE:
            if not self.device == event.getDevice():
                return
            self.updateDeviceInfo()
        if event.getRowOffset() == -1:
            return
        if event.getEventType() == event.ADD:
            self.addEvent(event)
        elif event.getEventType() == event.CHANGE:
            self.changeEvent(event)
        elif event.getEventType() == event.REMOVE:
            self.removeEvent(event)

    def removeEvent(self, event):
        index = event.getRowOffset()
        self.events.remove(self.events[index])

    def changeEvent(self, event):
        index = event.getRowOffset()
        step = event.getModel().getStepAt(index)
        entry = event.getModel().getEntryAt(index, self.device)
        if index > len(self.events):
            return
        self.events[index] = (
         entry.getSetpoint(), step.getDuration() * 1000)

    def addEvent(self, event):
        index = event.getRowOffset()
        step = event.getModel().getStepAt(index)
        entry = event.getModel().getEntryAt(index, self.device)
        self.events.insert(index, (entry.getSetpoint(), step.getDuration() * 1000))

    def updateDeviceInfo(self):
        self.maxRange = self.device.getRange()
        self.setTitle(self.device.getLabel())
        self.refresh(True)

    def getScale(self):
        return self.getHeight() / float(self.maxRange)

    def flowToPixel(self, flow):
        return self.getHeight() - int(flow * self.getScale())

    def update(self, dc, pos, interval, pixelInterval, cachedIntervalEvents, editor):
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.SetBrush(wx.Brush(self.facecolor))
        dc.DrawRectangle(pos[0], pos[1], 1000, self.getHeight())
        dc.SetPen(wx.NullPen)
        if self.device is None:
            return
        color = self.device.getPlotColor()
        dc.SetPen(wx.Pen(color, 1))
        dc.SetBrush(wx.Brush(self.reduceColor(color)))
        lastDuration = 0
        prevDuration = pos[0]
        font = wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        hicolor = wx.BLACK
        if color.Red() < 40 or color.Green() < 40 or color.Blue() < 40:
            hicolor = wx.WHITE
        dc.SetFont(font)
        prevSetpoint = pos[1] + self.getHeight()
        dc.SetTextForeground(wx.BLACK)
        next = -1
        idx = 1
        for (flow, duration) in self.events:
            lastDuration += duration
            next = -1
            if idx < len(self.events):
                next = self.owner.millisToPixels(self.events[idx][1])
            idx += 1
            h = self.flowToPixel(flow)
            x = pos[0] + self.owner.millisToPixels(lastDuration)
            y = pos[1] + h
            w = x - prevDuration
            if prevDuration == 0:
                prevDuration = pos[0]
            sep = 3000 / (self.owner.horizontalScale * self.owner.millisPerPixel)
            tip = 1
            if prevSetpoint < y:
                tip = -1
            if prevSetpoint == y:
                tip = 0
            if abs(sep) >= abs(w) / 2:
                sep = int(abs(w) / 4)
            dc.DrawSpline(((prevDuration, prevSetpoint), (prevDuration + sep, prevSetpoint + tip), (prevDuration + w - sep, y + tip), (prevDuration + w, y)))
            txt = '%d' % int(flow)
            (tw, th) = dc.GetTextExtent(txt)
            tx = prevDuration + w + 2
            ty = y
            if next != -1 and tw + 2 > next:
                prevSetpoint = y
                prevDuration = x
                continue
            hw = self.getHeight()
            if ty >= pos[1] + hw - th:
                ty = pos[1] + hw - th
            dc.DrawText(txt, tx, ty)
            prevSetpoint = y
            prevDuration = x

        dc.SetPen(wx.NullPen)
        return

    def reduceColor(self, color):
        scale = 0.6
        return wx.Color(self.normalize(color.Red()), self.normalize(color.Green()), self.normalize(color.Blue()))

    def normalize(self, color):
        scale = 0.6
        color = color + color * scale
        if color > 255:
            color = 255
        return color

    def getHeight(self):
        return 100
