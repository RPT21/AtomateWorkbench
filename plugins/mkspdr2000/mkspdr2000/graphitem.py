# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: /home/maldoror/apps/eclipse/workspace/com.atomate.workbench/plugins/up150/src/up150/graphitem.py
# Compiled at: 2004-08-12 02:18:21
import wx, plugins.grapheditor.grapheditor.contributor, plugins.grideditor.grideditor.recipemodel
import plugins.grapheditor.grapheditor as grapheditor
import plugins.grideditor.grideditor as grideditor


class UP150GraphItem(grapheditor.contributor.GraphContributor):
    __module__ = __name__

    def __init__(self):
        grapheditor.contributor.GraphContributor.__init__(self)
        self.facecolor = wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE)
        self.setTitle('')

    def setDevice(self, device):
        grapheditor.contributor.GraphContributor.setDevice(self, device)
        self.updateDeviceInfo()

    def prepareItem(self, owner, recipeModel):
        grapheditor.contributor.GraphContributor.prepareItem(self, owner, recipeModel)
        recipeModel.addModifyListener(self)

    def recipeModelChanged(self, event):
        if event.getEventType() == grideditor.recipemodel.CHANGE_DEVICE:
            if not self.device == event.getDevice():
                return
            self.updateDeviceInfo()

    def updateDeviceInfo(self):
        print('ME?')
        self.setTitle(self.device.getLabel())
        self.refresh(True)

    def update(self, dc, pos, interval, pixelInterval, cachedIntervalEvents, editor):
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.SetBrush(wx.Brush(self.facecolor))
        dc.DrawRectangle(pos, (1000, self.getHeight()))
        dc.SetPen(wx.NullPen)

    def getHeight(self):
        return 100
