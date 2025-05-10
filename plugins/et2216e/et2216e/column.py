# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: /home/maldoror/apps/eclipse/workspace/com.atomate.workbench/plugins/up150/src/up150/column.py
# Compiled at: 2004-08-12 02:18:21
from wxPython.grid import *
from wxPython.wx import *
import wx, up150.images as images, grideditor.tablecolumn, grideditor.utils.numericcelleditor, grideditor.utils

class UP150Column(grideditor.tablecolumn.ColumnContribution):
    __module__ = __name__

    def __init__(self):
        grideditor.tablecolumn.ColumnContribution.__init__(self)
        self.recipeModel = None
        self.deviceIndex = -1
        self.renderer = wxGridCellStringRenderer
        return

    def getHeaderImage(self):
        return images.getImage(images.SMALL_ICON)

    def createCellEditor(self):
        return grideditor.utils.numericcelleditor.NumericCellEditor()

    def getCellRenderer(self):
        return self.renderer()

    def getCellEditor(self):
        return self.editor()

    def getValueAt(self, stepIndex):
        entry = self.recipeModel.getEntryAt(stepIndex, self.device)
        return entry.getTemperature()

    def setValueAt(self, stepIndex, value):
        entry = self.recipeModel.getEntryAt(stepIndex, self.device)
        entry.setTemperature(int(value))

    def handleDoubleClick(self):
        grideditor.utils.showRecipeOptions(self.getDevice())
