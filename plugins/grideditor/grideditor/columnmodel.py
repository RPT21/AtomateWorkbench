# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/grideditor/src/grideditor/columnmodel.py
# Compiled at: 2004-07-28 01:20:37
from wx import *
import wx

class TableColumn(object):
    __module__ = __name__

    def __init(self, headerLabel):
        self.headerLabel = headerLabel
        self.celleditor = wx.GridCellEditor()
        self.cellrenderer = None
        self.width = 80
        return

    def getWidth(self):
        return self.width

    def setWidth(self, width):
        self.width = width

    def getHeaderLabel(self):
        return self.headerLabel

    def getCellEditor(self):
        return self.celleditor

    def getCellRenderer(self):
        return self.cellrenderer
