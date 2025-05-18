# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/grideditor/src/grideditor/recipegrideditortable.py
# Compiled at: 2004-10-13 03:17:33
from wx import *
import wx
import wx.grid as gridlib

class RecipeGridEditorTable(gridlib.GridTableBase):
    __module__ = __name__

    def __init__(self, mediator):
        gridlib.GridTableBase.__init__(self)
        self.mediator = mediator

    def removeAllRows(self):
        if self.mediator.getRowCount() == 0:
            return
        grid = self.GetView()
        grid.BeginBatch()
        msg = gridlib.GridTableMessage(self, gridlib.GRIDTABLE_NOTIFY_ROWS_DELETED, 0, self.mediator.getRowCount())
        grid.ProcessTableMessage(msg)
        grid.EndBatch()

    def removeRows(self, pos, numRows):
        if numRows == 0:
            return
        grid = self.GetView()
        grid.BeginBatch()
        msg = wx.grid.GridTableMessage(self, gridlib.GRIDTABLE_NOTIFY_ROWS_DELETED, pos, numRows)
        grid.ProcessTableMessage(msg)
        grid.EndBatch()

    def insertRows(self, pos, numRows):
        if numRows == 0:
            return
        grid = self.GetView()
        grid.BeginBatch()
        msg = gridlib.GridTableMessage(self, gridlib.GRIDTABLE_NOTIFY_ROWS_INSERTED, pos, numRows)
        grid.ProcessTableMessage(msg)
        grid.EndBatch()
        grid.AdjustScrollbars()

    def showAllColumns(self):
        grid = self.GetView()
        grid.BeginBatch()
        msg = gridlib.GridTableMessage(self, gridlib.GRIDTABLE_NOTIFY_COLS_INSERTED, 0, self.mediator.getColumnCount())
        grid.ProcessTableMessage(msg)
        grid.EndBatch()
        grid.AdjustScrollbars()

    def hideAllColumns(self):
        if self.mediator.getColumnCount() == 0:
            return
        grid = self.GetView()
        grid.BeginBatch()
        msg = gridlib.GridTableMessage(self, gridlib.GRIDTABLE_NOTIFY_COLS_DELETED, 0, self.mediator.getColumnCount())
        grid.ProcessTableMessage(msg)
        grid.EndBatch()
        grid.AdjustScrollbars()

    def removeColumn(self, index):
        grid = self.GetView()
        grid.HideCellEditControl()
        grid.DisableCellEditControl()
        self.hideColumn(index)

    def hideColumn(self, index):
        grid = self.GetView()
        grid.BeginBatch()
        msg = gridlib.GridTableMessage(self, gridlib.GRIDTABLE_NOTIFY_COLS_DELETED, index, 1)
        grid.ProcessTableMessage(msg)
        grid.EndBatch()
        grid.AdjustScrollbars()

    def showColumn(self, index):
        grid = self.GetView()
        grid.BeginBatch()
        msg = gridlib.GridTableMessage(self, gridlib.GRIDTABLE_NOTIFY_COLS_INSERTED, index, 1)
        grid.ProcessTableMessage(msg)
        grid.EndBatch()
        grid.AdjustScrollbars()

    def updateAll(self):
        grid = self.GetView()
        grid.BeginBatch()
        msg = gridlib.GridTableMessage(self, gridlib.GRIDTABLE_REQUEST_VIEW_GET_VALUES)
        grid.ProcessTableMessage(msg)
        grid.EndBatch()
        grid.AdjustScrollbars()

    def updateRow(self, row):
        grid = self.GetView()
        grid.BeginBatch()
        cols = grid.GetNumberCols()
        msg = gridlib.GridTableMessage(self, gridlib.GRIDTABLE_REQUEST_VIEW_GET_VALUES, row, 1)
        grid.ProcessTableMessage(msg)
        grid.EndBatch()

    def GetAttr(self, row, col, extra):
        return self.mediator.getAttribute(row, col, extra)

    def GetValue(self, row, col):
        return self.mediator.getValueAt(row, col)

    def GetNumberRows(self):
        return self.mediator.getRowCount()

    def GetNumberCols(self):
        return self.mediator.getColumnCount()

    def GetRowLabelValue(self, row):
        return self.mediator.getRowLabel(row)

    def GetColLabelValue(self, col):
        return self.mediator.getColLabel(col)
