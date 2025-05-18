# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/mfc/src/mfc/column.py
# Compiled at: 2004-10-29 20:49:59
from wx import *
import wx, logging, plugins.mfc.mfc.images as images
from plugins.mfc.mfc.utils import *
import plugins.grideditor.grideditor.tablecolumn
import plugins.grideditor.grideditor.utils.numericcelleditor
import plugins.grideditor.grideditor as grideditor

logger = logging.getLogger('mfc')

class MFCCellEditor(grideditor.utils.numericcelleditor.NumericCellEditor):
    __module__ = __name__

    def __init__(self, column):
        grideditor.utils.numericcelleditor.NumericCellEditor.__init__(self, column, float)
        self.range = 0.0
        self.usegcf = True
        self.gcf = 100

    def setUseGCF(self, use, gcf):
        self.usegcf = use
        self.gcf = gcf

    def formatValue(self, value):
        return formatValue(value)

    def setRange(self, range):
        self.range = range
        self.valideIfNeeded()

    def valideIfNeeded(self):
        if self.control is not None:
            self.validate()
        return

    def getInvalidCellColor(self):
        return grideditor.getDefault().getInvalidCellColor()

    def getHighlightStepColor(self):
        return grideditor.getDefault().getHighlightStepColor()

    def validate(self):
        value = self.getValue()
        compval = value
        if self.usegcf:
            compval = value / self.gcf * 100
        if compval > self.range:
            self.control.SetBackgroundColour(self.getInvalidCellColor())
        else:
            self.control.SetBackgroundColour(wx.WHITE)
        self.control.Refresh()

    def controlUpdate(self):
        grideditor.utils.numericcelleditor.NumericCellEditor.controlUpdate(self)
        self.validate()


class MFCCellRenderer(grideditor.tablecolumn.StringCellRenderer):
    __module__ = __name__

    def __init__(self):
        grideditor.tablecolumn.StringCellRenderer.__init__(self)
        self.range = 0
        self.gcf = 100
        self.usegcf = False

    def setUseGCF(self, use, gcf):
        self.usegcf = use
        self.gcf = gcf

    def validate(self, value):
        compval = value
        if self.usegcf:
            compval = value / self.gcf * 100
        return compval <= self.range

    def getInvalidCellColor(self):
        return grideditor.getDefault().getInvalidCellColor()

    def getHighlightStepColor(self):
        return grideditor.getDefault().getHighlightStepColor()

    def setRange(self, range):
        self.range = range

    def getSelectedRowColor(self, grid):
        return self.getHighlightStepColor()

    def getNormalRowColor(self, grid):
        return grid.GetDefaultCellBackgroundColour()

    def drawBackground(self, grid, dc, rect, isSelected, isColSelected, isRowSelected, value):
        if not self.validate(value):
            color = self.getInvalidCellColor()
        elif isRowSelected and not isColSelected:
            color = self.getSelectedRowColor(grid)
        else:
            color = self.getNormalRowColor(grid)
        dc.SetPen(wx.Pen(color))
        dc.SetBrush(wx.Brush(color))
        dc.DrawRectangle(rect.x, rect.y, rect.width, rect.height)
        dc.SetBrush(wx.NullBrush)
        dc.SetPen(wx.NullPen)

    def draw(self, grid, value, dc, isSelected, rect, row=-1, col=-1, isColSelected=False, isRowSelected=False):
        text = formatValue(value)
        dc.SetFont(self.font)
        (w, h) = dc.GetTextExtent(text)
        x = self.inset
        y = (rect.height - h) * 0.5
        self.drawBackground(grid, dc, rect, isSelected, isColSelected, isRowSelected, value)
        dc.DrawText(text, rect.x + x, rect.y + y)


class MFCColumn(grideditor.tablecolumn.ColumnContribution):
    __module__ = __name__

    def __init__(self):
        grideditor.tablecolumn.ColumnContribution.__init__(self)  # Demana una columna, que no sé quin tipus de variable és, podria ser que column sigui una variable eliminable
        self.recipeModel = None
        self.useGCF = True
        self.GCF = 100.0
        return

    def hookToRecipeModel(self):
        if self.recipeModel is not None:
            self.recipeModel.addModifyListener(self)
        self.updateDeviceConfiguration()
        return

    def setInput(self, recipeModel, device):
        self.unhookRecipeModel()
        grideditor.tablecolumn.ColumnContribution.setInput(self, recipeModel, device)
        self.hookToRecipeModel()

    def recipeModelChanged(self, event):
        if not event.getEventType() == event.CHANGE_DEVICE:
            return
        if not self.device == event.getDevice():
            return
        self.updateDeviceConfiguration()

    def updateDeviceConfiguration(self):
        uihints = self.device.getUIHints()
        hwhints = self.device.getHardwareHints()
        gcf = 100.0
        try:
            gcf = float(hwhints.getChildNamed('conversion-factor').getValue())
        except Exception as msg:
            logger.exception(msg)

        range = 65500
        try:
            range = float(hwhints.getChildNamed('range').getValue())
        except Exception as msg:
            logger.exception(msg)

        usegcf = True
        try:
            usegcf = uihints.getChildNamed('column-use-gcf').getValue().lower() == 'true'
        except Exception as msg:
            logger.exception(msg)

        self.GCF = gcf
        self.useGCF = usegcf
        self.getCellEditor().setUseGCF(usegcf, gcf)
        self.getCellEditor().setRange(range)
        self.getCellRenderer().setUseGCF(usegcf, gcf)
        self.getCellRenderer().setRange(range)

    def unhookRecipeModel(self):
        if self.recipeModel is not None:
            self.recipeModel.removeModifyListener(self)
        return

    def getHeaderImage(self):
        return images.getImage(images.SMALL_ICON)

    def createCellEditor(self):
        return MFCCellEditor(self)

    def createCellRenderer(self):
        return MFCCellRenderer()

    def getValueAt(self, stepIndex):
        entry = self.recipeModel.getEntryAt(stepIndex, self.device)
        if self.useGCF:
            return entry.getFlow() * (self.GCF / 100.0)
        return entry.getFlow()

    def setValueAt(self, stepIndex, value):
        entry = self.recipeModel.getEntryAt(stepIndex, self.device)
        realvalue = value
        if self.useGCF and value is not 0:
            realvalue = value / (self.GCF / 100.0)
        entry.setFlow(float(realvalue))

    def handleDoubleClick(self):
        grideditor.utils.showRecipeOptions(self.getDevice())

    def cellValueChanged(self, index, value):
        """
        step = self.recipeModel.getStepAt(index)
        entry = self.recipeModel.getEntryAt(index, self.device)
        entry.setFlow( float(value) )
        """
        self.setValueAt(index, value)
        step = self.recipeModel.getStepAt(index)
        self.contentProvider.suppressContentUpdates(True)
        self.recipeModel.updateStepEntry(step, self.device)
        self.contentProvider.suppressContentUpdates(False)

    def dispose(self):
        self.getCellEditor().dispose()
        self.unhookRecipeModel()

    def createHeaderRenderer(self):
        return MFCHeaderCellRenderer(self)


class MFCHeaderCellRenderer(grideditor.tablecolumn.StringHeaderCellRenderer):
    __module__ = __name__

    def draw(self, dc, rect):
        grideditor.tablecolumn.StringHeaderCellRenderer.draw(self, dc, rect)
        dc.SetBrush(wx.Brush(self.column.device.getPlotColor(), wx.SOLID))
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.DrawRectangle(rect[0][0], rect[0][1] + rect[1][1] - 3, rect[1][0], 3)
