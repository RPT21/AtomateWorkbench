# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/furnacezone/src/furnacezone/column.py
# Compiled at: 2004-09-21 20:05:48
from wx import *
import wx, plugins.furnacezone.furnacezone.images as images, plugins.grideditor.grideditor.tablecolumn
import plugins.grideditor.grideditor.utils.numericcelleditor, plugins.grideditor.grideditor as grideditor
import logging
logger = logging.getLogger('furnacezone')

class FurnaceZoneCellEditor(grideditor.utils.numericcelleditor.NumericCellEditor):
    __module__ = __name__

    def __init__(self, column):
        grideditor.utils.numericcelleditor.NumericCellEditor.__init__(self, column, int)
        self.range = -1

    def getInvalidCellColor(self):
        return grideditor.getDefault().getInvalidCellColor()

    def setRange(self, range):
        self.range = range
        self.valideIfNeeded()

    def valideIfNeeded(self):
        if self.control is not None:
            self.validate()
        return

    def validate(self):
        value = self.getValue()
        if value > self.range:
            self.control.SetBackgroundColour(self.getInvalidCellColor())
        else:
            self.control.SetBackgroundColour(wx.WHITE)
        self.control.Refresh()

    def controlUpdate(self):
        grideditor.utils.numericcelleditor.NumericCellEditor.controlUpdate(self)
        self.validate()


class FurnaceZoneCellRenderer(grideditor.tablecolumn.StringCellRenderer):
    __module__ = __name__

    def __init__(self):
        grideditor.tablecolumn.StringCellRenderer.__init__(self)
        self.range = 0

    def getInvalidCellColor(self):
        return grideditor.getDefault().getInvalidCellColor()

    def getHighlightStepColor(self):
        return grideditor.getDefault().getHighlightStepColor()

    def setRange(self, range):
        self.range = range

    def getNormalRowColor(self, grid):
        return grid.GetDefaultCellBackgroundColour()

    def drawBackground(self, grid, dc, rect, isSelected, isColSelected, isRowSelected, value):
        if value > self.range:
            color = self.getInvalidCellColor()
        elif isRowSelected and not isColSelected:
            color = self.getHighlightStepColor()
        else:
            color = self.getNormalRowColor(grid)
        dc.SetPen(wx.Pen(color))
        dc.SetBrush(wx.Brush(color))
        dc.DrawRectangle(rect.x, rect.y, rect.width, rect.height)
        dc.SetBrush(wx.NullBrush)
        dc.SetPen(wx.NullPen)

    def draw(self, grid, value, dc, isSelected, rect, row=-1, col=-1, isColSelected=False, isRowSelected=False):
        text = '%d' % value
        dc.SetFont(self.font)
        (w, h) = dc.GetTextExtent(text)
        x = self.inset
        y = (rect.height - h) * 0.5
        self.drawBackground(grid, dc, rect, isSelected, isColSelected, isRowSelected, value)
        dc.DrawText(text, rect.x + x, rect.y + y)


class FurnaceZoneColumn(grideditor.tablecolumn.ColumnContribution):
    __module__ = __name__

    def __init__(self):
        grideditor.tablecolumn.ColumnContribution.__init__(self)
        self.recipeModel = None
        return

    def hookToRecipeModel(self):
        if self.recipeModel is not None:
            self.recipeModel.addModifyListener(self)
        return

    def setInput(self, recipeModel, device):
        self.unhookRecipeModel()
        grideditor.tablecolumn.ColumnContribution.setInput(self, recipeModel, device)
        self.hookToRecipeModel()
        if device is not None:
            self.updateOptions()
        return

    def updateOptions(self):
        rng = 1000
        try:
            hints = self.device.getHardwareHints()
            rng = int(hints.getChildNamed('range').getValue())
        except Exception as msg:
            logger.exception(msg)
            rng = 1000

        self.getCellEditor().setRange(rng)
        self.getCellRenderer().setRange(rng)

    def recipeModelChanged(self, event):
        if not event.getEventType() == event.CHANGE_DEVICE:
            return
        if not self.device == event.getDevice():
            return
        self.updateOptions()

    def unhookRecipeModel(self):
        if self.recipeModel is not None:
            self.recipeModel.removeModifyListener(self)
        return

    def getHeaderImage(self):
        return images.getImage(images.SMALL_ICON)

    def createCellEditor(self):
        return FurnaceZoneCellEditor(self)

    def createCellRenderer(self):
        return FurnaceZoneCellRenderer()

    def xgetCellRenderer(self):
        return self.renderer()

    def getValueAt(self, stepIndex):
        entry = self.recipeModel.getEntryAt(stepIndex, self.device)
        return entry.getSetpoint()

    def setValueAt(self, stepIndex, value):
        entry = self.recipeModel.getEntryAt(stepIndex, self.device)
        entry.setSetpoint(int(value))

    def handleDoubleClick(self):
        grideditor.utils.showRecipeOptions(self.getDevice())

    def cellValueChanged(self, index, value):
        step = self.recipeModel.getStepAt(index)
        entry = self.recipeModel.getEntryAt(index, self.device)
        entry.setSetpoint(int(value))
        self.contentProvider.suppressContentUpdates(True)
        self.recipeModel.updateStepEntry(step, self.device)
        self.contentProvider.suppressContentUpdates(False)

    def dispose(self):
        self.getCellEditor().dispose()
        self.unhookRecipeModel()
