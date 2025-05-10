# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/grideditor/src/grideditor/tablecolumn.py
# Compiled at: 2004-10-14 00:26:32
from wx.grid import *
from wx import *
import wx
import wx.grid as gridlib

class TableColumn(object):
    __module__ = __name__

    def __init__(self):
        self.celleditor = None
        self.cellrenderer = None
        self.headerRenderer = StringHeaderCellRenderer(self)
        self.width = 80
        self.contentProvider = None
        return

    def setContentProvider(self, provider):
        self.contentProvider = provider

    def getValueAt(self, stepIndex):
        return ''

    def setValueAt(self, stepIndex, value):
        pass

    def cellValueChanged(self, stepIndex, value):
        """Used mostly cell editor to tag the cell as having been modified"""
        pass

    def getCellEditor(self):
        return self.celleditor

    def getCellRenderer(self):
        return self.cellrenderer

    def getHeaderImage(self):
        return None

    def getHeaderRenderer(self):
        return self.headerRenderer

    def getHeaderLabel(self):
        return None

    def setWidth(self, width):
        self.width = width

    def getWidth(self):
        return self.width

    def handleDoubleClick(self):
        pass

    def dispose(self):
        pass


class ColumnContributorTableColumnAdapter(TableColumn):
    __module__ = __name__

    def __init__(self, contribution, device, recipeModel):
        TableColumn.__init__(self)
        self.contribution = contribution
        self.contribution.setInput(recipeModel, device)

    def setContentProvider(self, provider):
        self.contribution.contentProvider = provider

    def getContribution(self):
        return self.contribution

    def getValueAt(self, stepIndex):
        return self.contribution.getValueAt(stepIndex)

    def setValueAt(self, stepIndex, value):
        self.contribution.setValueAt(stepIndex, value)

    def getCellEditor(self):
        return self.contribution.getCellEditorWrapper()

    def getCellRenderer(self):
        return self.contribution.getCellRendererWrapper()

    def getHeaderRenderer(self):
        return self.contribution.getHeaderRenderer()

    def getHeaderLabel(self):
        return self.contribution.getHeaderLabel()

    def handleDoubleClick(self):
        self.contribution.handleDoubleClick()

    def dispose(self):
        self.contribution.dispose()


class CellEditor(object):
    __module__ = __name__

    def __init__(self, column):
        self.control = None
        self.column = column
        self.stepIndex = -1
        self.oldValue = None
        return

    def setStepIndex(self, index):
        self.stepIndex = index

    def getStepIndex(self):
        return self.stepIndex

    def isSameValue(self, newValue, oldValue):
        """Used when values must have pointers to compare"""
        return newValue != oldValue

    def getControl(self):
        return self.control

    def createControl(self, parent):
        raise Exception('Not implemented')

    def isStartingKey(self, keycode):
        return True

    def setStartingKey(self, keycode):
        """Passed in when the control is about to be edited"""
        pass

    def setStartingClick(self):
        pass

    def setValue(self, value):
        pass

    def getValue(self):
        return None

    def setSize(self, rect):
        self.control.SetPosition((rect[0], rect[1]))
        self.control.SetSize((rect[2], rect[3]))

    def beginEdit(self):
        pass

    def endEdit(self):
        pass

    def dispose(self):
        pass


class TextCellEditor(CellEditor):
    __module__ = __name__

    def TextCellEditor(self, column):
        CellEditor.__init__(self, column)
        self.oldValue = None
        return

    def createControl(self, parent):
        self.control = wx.TextCtrl(parent, -1)
        return self.control

    def setValue(self, value):
        self.control.SetValue(value)

    def getValue(self):
        return self.control.GetValue()


class HeaderCellRenderer(object):
    __module__ = __name__

    def __init__(self):
        self.size = (30, 30)

    def draw(self, dc, rect):
        pass

    def setSize(self, size):
        self.size = size

    def getBestSize(self):
        return self.size


class StringHeaderCellRenderer(HeaderCellRenderer):
    __module__ = __name__

    def __init__(self, column):
        HeaderCellRenderer.__init__(self)
        self.column = column
        self.cachedBestSize = (0, 0)
        self.lastLabel = ''
        self.image = None
        self.insets = (4, 2, 4, 4)
        self.font = wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        return

    def getFont(self):
        return self.font

    def draw(self, dc, rect):
        bkgcolor = wx.SystemSettings_GetColour(wx.SYS_COLOUR_BTNFACE)
        x = rect[0][0]
        y = rect[0][1]
        width = rect[1][0]
        height = rect[1][1]
        dc.SetClippingRegion(x, y, width, height)
        dc.SetBrush(wx.Brush(bkgcolor))
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.DrawRectangle(rect[0][0], rect[0][1], rect[1][0], rect[1][1])
        dc.SetPen(wx.NullPen)
        self.drawImage(dc, x, y, width, height)
        self.drawText(dc, x, y, width, height, self.column.getHeaderLabel())
        shadowcolor = wx.SystemSettings_GetColour(wx.SYS_COLOUR_3DDKSHADOW)
        hlcolor = wx.SystemSettings_GetColour(wx.SYS_COLOUR_BTNHIGHLIGHT)
        dc.SetPen(wx.Pen(shadowcolor))
        dc.DrawLine(x + width - 1, y, x + width - 1, y + height)
        dc.DrawLine(x, y + height - 1, x + width, y + height - 1)
        dc.DrawLine(x, y, x + width, y)
        dc.DestroyClippingRegion()

    def drawImage(self, dc, x, y, width, height):
        image = self.column.getHeaderImage()
        if image is None:
            return
        dc.DrawBitmap(image, x + self.insets[0], y + self.insets[1], True)
        return

    def getTextLeftPos(self):
        image = self.column.getHeaderImage()
        if image is None:
            return 0
        return image.GetWidth() + self.insets[0]

    def drawText(self, dc, x, y, width, height, text):
        indent = self.getTextLeftPos()
        dc.SetFont(self.getFont())
        top = y + self.insets[1]
        x = indent + x + self.insets[0]
        dc.DrawText(text, x, top)
        dc.DestroyClippingRegion()
        dc.SetPen(wx.NullPen)

    def cacheBestSize(self):
        self.lastLabel = self.column.getHeaderLabel()
        mdc = wx.MemoryDC()
        mdc.SelectObject(wx.EmptyBitmap(100, 100))
        mdc.SetFont(self.getFont())
        (w, h) = mdc.GetTextExtent(self.lastLabel)
        self.cachedBestSize = (w + self.insets[0] + self.insets[2], h + self.insets[1] + self.insets[3])

    def getBestSize(self):
        if self.lastLabel != self.column.getHeaderLabel():
            self.cacheBestSize()
        return self.cachedBestSize


class CellRenderer(object):
    __module__ = __name__

    def draw(self, value, dc, isSelected, rect, row=-1, col=-1, isColSelected=False, isRowSelected=False):
        pass

    def getBestSize(self, value):
        return None


class StringCellRenderer(CellRenderer):
    __module__ = __name__

    def __init__(self):
        self.font = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
        self.inset = 5

    def draw(self, grid, value, dc, isSelected, rect, row=-1, col=-1, isColSelected=False, isRowSelected=False):
        text = str(value)
        dc.SetFont(self.font)
        (w, h) = dc.GetTextExtent(text)
        x = self.inset
        y = (rect.height - h) * 0.5
        self.drawBackground(grid, dc, rect, isSelected, isColSelected, isRowSelected)
        dc.DrawText(text, (rect.x + x, rect.y + y))

    def getSelectedRowColor(self, grid):
        return wx.RED

    def getNormalRowColor(self, grid):
        return grid.GetDefaultCellBackgroundColour()

    def drawBackground(self, grid, dc, rect, isSelected, isColSelected, isRowSelected):
        if isRowSelected and not isColSelected:
            color = self.getSelectedRowColor(grid)
        else:
            color = self.getNormalRowColor(grid)
        dc.SetPen(wx.Pen(color))
        dc.SetBrush(wx.Brush(color))
        dc.DrawRectangle((rect.x, rect.y), (rect.width, rect.height))
        dc.SetBrush(wx.NullBrush)
        dc.SetPen(wx.NullPen)

    def getBestSize(self, value):
        text = str(value)
        (w, h) = dc.GetTextExtent(text)
        return (
         w, h)


class CellRendererWrapper(gridlib.GridCellRenderer):
    __module__ = __name__

    def __init__(self, renderer, column):
        gridlib.GridCellRenderer.__init__(self)
        self.renderer = renderer
        self.column = column

    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
        value = self.column.getValueAt(row)
        isRowSelected = grid.GetGridCursorRow() == row
        isColSelected = grid.GetGridCursorCol() == col
        self.renderer.draw(grid, value, dc, isSelected, rect, row, col, isColSelected=isColSelected, isRowSelected=isRowSelected)

    def GetBestSize(self):
        value = self.column.getValueAt(row)
        return self.renderer.getBestSize(value)

    def Clone(self):
        return CellRendererWrapper(self.renderer, self.column)


class CellEditorWrapper(gridlib.GridCellEditor):
    __module__ = __name__

    def __init__(self, control, column):
        """Create a wrapper around the control which is of type"""
        gridlib.GridCellEditor.__init__(self)
        self.oldValue = None
        self.control = control
        self.column = column
        self.recipeModel = None
        return

    def setInput(self, recipeModel):
        self.recipeModel = recipeModel

    def Create(self, parent, id, evtHandler):
        self.control.createControl(parent)
        self.SetControl(self.control.getControl())
        if evtHandler:
            self.control.getControl().PushEventHandler(evtHandler)

    def SetSize(self, rect):
        if rect[0] > 0:
            rect[0] += 1
        if rect[1] > 0:
            rect[1] += 1
        self.control.setSize(rect)

    def BeginEdit(self, row, col, attr):
        value = self.column.getValueAt(row)
        self.oldValue = value
        self.control.setStepIndex(row)
        self.control.setValue(value)
        self.control.beginEdit()
        self.control.getControl().SetFocus()

    def EndEdit(self, row, col, grid):
        self.control.endEdit()
        value = self.control.getValue()
        if self.control.isSameValue(value, self.oldValue):
            self.column.setValueAt(row, value)
            return True
        return False

    def Reset(self):
        self.control.setValue(self.oldValue)

    def IsAcceptedKey(self, event):
        key = event.GetKeyCode()
        return self.control.isStartingKey(key)

    def SetStartingKey(self, event):
        key = event.GetKeyCode()
        self.control.setStartingKey(key)

    def StartingClick(self):
        self.control.setStartingClick()

    def Clone(self):
        return CellEditorWrapper(self.control, self.column)

    def Show(self, show, attr):
        self.base_Show(show, attr)

    def Destroy(self):
        self.base_Destroy()
        self.control.dispose()


class ColumnContribution(object):
    __module__ = __name__

    def __init__(self):
        self.celleditor = self.createCellEditor()
        self.cellrenderer = self.createCellRenderer()
        self.cellEditorWrapper = CellEditorWrapper(self.celleditor, self)
        self.cellRendererWrapper = CellRendererWrapper(self.cellrenderer, self)
        self.headerRenderer = self.createHeaderRenderer()

    def getCellEditor(self):
        return self.celleditor

    def getCellRenderer(self):
        return self.cellrenderer

    def cellValueChanged(self, stepIndex, value):
        """Used mostly cell editor to tag the cell as having been modified"""
        pass

    def setInput(self, recipeModel, device):
        self.recipeModel = recipeModel
        self.device = device
        self.cellEditorWrapper.setInput(recipeModel)

    def handleDoubleClick(self):
        pass

    def createHeaderRenderer(self):
        return StringHeaderCellRenderer(self)

    def createCellRenderer(self):
        return StringCellRenderer()

    def createCellEditor(self):
        return TextCellEditor()

    def getDevice(self):
        return self.device

    def getCellRendererWrapper(self):
        return self.cellRendererWrapper

    def getCellEditorWrapper(self):
        return self.cellEditorWrapper

    def getHeaderImage(self):
        return None

    def getHeaderRenderer(self):
        return self.headerRenderer

    def getHeaderLabel(self):
        return self.device.getLabel()

    def getValueAt(self, stepIndex):
        raise Exception('Not implemented')

    def setValueAt(self, stepIndex, value):
        raise Exception('Not implemented')

    def dispose(self):
        pass
