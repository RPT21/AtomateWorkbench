# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/mfc/src/mfc/graphitem.py
# Compiled at: 2004-10-27 04:37:26
import wx, grapheditor.contributor, grideditor.recipemodel, executionengine, logging
logger = logging.getLogger('mfc.ui.graphitem')

class MFCGraphItem(grapheditor.contributor.GraphContributor):
    __module__ = __name__

    def __init__(self):
        grapheditor.contributor.GraphContributor.__init__(self)
        self.facecolor = wx.WHITE
        self.setTitle('')
        self.engine = None
        self.events = []
        self.maxRange = 1
        return

    def flowToPixel(self, flow):
        return self.getHeight() - int(flow * (self.getHeight() / self.maxRange))

    def engineInit(self, engine):
        self.engine = engine
        self.engine.addEngineListener(self)

    def engineEvent(self, event):
        logger.debug('Engine event: %s' % event)
        if event.getType() == executionengine.engine.TYPE_ENDING:
            self.engine.removeEngineListener(self)

    def setDevice(self, device):
        grapheditor.contributor.GraphContributor.setDevice(self, device)
        self.updateDeviceInfo()
        self.maxRange = self.device.getRange()
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
            self.events.append((entry.getFlow(), step.getDuration() * 1000))

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
         entry.getFlow(), step.getDuration() * 1000)

    def addEvent(self, event):
        index = event.getRowOffset()
        step = event.getModel().getStepAt(index)
        entry = event.getModel().getEntryAt(index, self.device)
        self.events.insert(index, (entry.getFlow(), step.getDuration() * 1000))

    def updateDeviceInfo(self):
        self.maxRange = self.device.getRange()
        self.setTitle(self.device.getLabel())
        self.refresh(True)

    def update(self, dc, pos, interval, pixelInterval, cachedIntervalEvents, editor):
        y = pos[1]
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.SetBrush(wx.Brush(self.facecolor))
        dc.DrawRectangle(pos[0], pos[1], 1000, self.getHeight())
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
        for (flow, duration) in self.events:
            lastDuration += duration
            h = self.flowToPixel(flow)
            x = pos[0] + self.owner.millisToPixels(lastDuration)
            y = pos[1] + h
            w = x - prevDuration
            if prevDuration == 0:
                prevDuration = pos[0]
            dc.DrawRectangle(prevDuration, y, w, self.getHeight() - h)
            txt = '%0.04f' % flow
            (tw, th) = dc.GetTextExtent(txt)
            tx = prevDuration + (w - tw) / 2
            ty = y - (th + 2)
            if ty < pos[1]:
                ty = y + 2
                dc.SetTextForeground(hicolor)
            else:
                dc.SetTextForeground(wx.BLACK)
            dc.DrawText(txt, tx, ty)
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
