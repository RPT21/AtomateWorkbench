# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/grideditor/src/grideditor/durationcolumn.py
# Compiled at: 2004-09-21 02:56:07
import wx.lib.masked.timectrl as timectrl
from wx import *
import wx
import plugins.grideditor.grideditor as grideditor
import plugins.grideditor.grideditor.tablecolumn as grideditor_tablecolumn

class DurationChangeHandler(wx.EvtHandler):
    __module__ = __name__

    def __init__(self, owner):
        wx.EvtHandler.__init__(self)
        self.owner = owner
        self.Bind(timectrl.EVT_TIMEUPDATE, self.OnTimeUpdate)

    def OnTimeUpdate(self, event):
        event.Skip()
        self.owner.controlUpdate()


class DurationCellEditor(grideditor_tablecolumn.CellEditor):
    __module__ = __name__

    def __init__(self, column):
        grideditor_tablecolumn.CellEditor.__init__(self, column)
        self.oldValue = None
        self.acceptedStartKeys = [wx.WXK_SPACE, ord('1'), ord('2'), ord('3'), ord('4'), ord('5'), ord('6'), ord('7'), ord('8'), ord('9'), ord('0')]
        return

    def validate(self):
        """
        print self.getValue().GetSeconds()
        if self.getValue().GetSeconds() < 1:
            print "so ... :)"
            self.control.SetBackgroundColour(wx.GREEN)
        else:
            self.control.SetBackgroundColour(wx.WHITE)
        self.control.Refresh()     
        """
        pass

    def controlUpdate(self):
        try:
            value = self.getValue().GetSeconds()
        except Exception as msg:
            return

        self.validate()
        self.column.cellValueChanged(self.getStepIndex(), value)

    def isStartingKey(self, keycode):
        return keycode in self.acceptedStartKeys

    def createControl(self, parent):
        self.control = timectrl.TimeCtrl(parent, -1, fmt24hr=True)
        self.control.PushEventHandler(DurationChangeHandler(self))
        return self.control

    def setValue(self, value):
        self.oldValue = value
        ts = wx.TimeSpan.Seconds(int(value))
        self.control.SetValue(ts)
        self.validate()

    def getValue(self):
        return self.control.GetValue(as_wxTimeSpan=True)

    def isSameValue(self, newValue, oldValue):
        if oldValue is None:
            oldValue = wx.TimeSpan()
            oldValue.Seconds(0)
        if not isinstance(oldValue, wx.TimeSpan):
            ov = wx.TimeSpan()
            ov.Seconds(oldValue)
            oldValue = ov
        return newValue != oldValue


class DurationCellRenderer(grideditor_tablecolumn.StringCellRenderer):
    __module__ = __name__

    def __init__(self):
        grideditor_tablecolumn.StringCellRenderer.__init__(self)

    def getBackgroundColor(self, value):
        if value > self.range:
            return self.invalidColor
        else:
            return wx.WHITE

    def setRange(self, range):
        self.range = range

    def getSelectedRowColor(self, grid):
        return grideditor.getDefault().getHighlightStepColor()

    def getNormalRowColor(self, grid):
        return grid.GetDefaultCellBackgroundColour()

    def drawBackground(self, grid, dc, rect, isSelected, isColSelected, isRowSelected, value):
        if value < 1:
            color = grideditor.getDefault().getInvalidCellColor()
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
        ts = wx.TimeSpan.Seconds(value)
        text = ts.Format('%H:%M:%S')
        dc.SetFont(self.font)
        (w, h) = dc.GetTextExtent(text)
        x = self.inset
        y = (rect.height - h) * 0.5
        self.drawBackground(grid, dc, rect, isSelected, isColSelected, isRowSelected, value)
        dc.DrawText(text, rect.x + x, rect.y + y)


class DurationColumn(grideditor_tablecolumn.TableColumn):
    __module__ = __name__

    def __init__(self, recipeModel):
        grideditor_tablecolumn.TableColumn.__init__(self)
        self.recipeModel = recipeModel
        self.durationCellEditor = DurationCellEditor(self)
        self.durationCellRenderer = DurationCellRenderer()
        self.cellEditorWrapper = grideditor_tablecolumn.CellEditorWrapper(self.durationCellEditor, self)
        self.cellRendererWrapper = grideditor_tablecolumn.CellRendererWrapper(self.durationCellRenderer, self)
        self.hookToRecipeModel()

    def hookToRecipeModel(self):
        if self.recipeModel is not None:
            self.recipeModel.addModifyListener(self)
        return

    def cellValueChanged(self, index, value):
        step = self.recipeModel.getStepAt(index)
        step.setDuration(value)
        self.contentProvider.suppressContentUpdates(True)
        self.recipeModel.updateStepEntry(step)
        self.contentProvider.suppressContentUpdates(False)

    def recipeModelChanged(self, event):
        pass

    def unhookRecipeModel(self):
        if self.recipeModel is not None:
            self.recipeModel.removeModifyListener(self)
        return

    def getCellEditor(self):
        return self.cellEditorWrapper

    def getCellRenderer(self):
        return self.cellRendererWrapper

    def getHeaderLabel(self):
        return 'Duration'

    def getValueAt(self, stepIndex):
        return self.recipeModel.getStepAt(stepIndex).getDuration()

    def setValueAt(self, stepIndex, value):
        if isinstance(value, wx.TimeSpan):
            self.recipeModel.getStepAt(stepIndex).setDuration(value.GetSeconds())
        if isinstance(value, int):
            self.recipeModel.getStepAt(stepIndex).setDuration(value)

    def dispose(self):
        self.durationCellEditor.dispose()
        self.unhookRecipeModel()
