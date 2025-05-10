# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/grideditor/src/grideditor/gutter.py
# Compiled at: 2004-11-05 20:16:50
import wx, grideditor, validator, grideditor.utils.validation, ui.images, ui.widgets.contentassist, copy
_DEFAULT_WIDTH = 10
_DEBUG = True

class ScrollEvtHandler(wx.EvtHandler):
    __module__ = __name__

    def __init__(self, wnd, owner):
        wx.EvtHandler.__init__(self)
        self.Bind(wx.EVT_SCROLL_THUMBTRACK, self.OnScroll)
        self.owner = owner

    def OnScroll(self, event):
        event.Skip()
        self.owner.handleScrolled()


class GutterColumn(wx.Window):
    __module__ = __name__

    def __init__(self, parent):
        wx.Window.__init__(self, parent, -1)
        self.gutter = None
        self.grid = None
        self.gridviewer = None
        self.step = None
        self.editor = None
        self.model = None
        validator.getDefault().addValidationListener(self)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        return

    def validationEvent(self, valid, errors):
        self.Refresh()

    def setGutter(self, gutter):
        self.gutter = gutter
        if self.gutter is not None:
            self.grid = self.gutter.getGrid()
            self.gridviewer = self.gutter.getGridViewer()
        else:
            self.grid = None
            self.gridviewer = None
        if self.grid is not None:
            self.gridviewer.addSelectionChangedListener(self)
            self.handleSelectionChanged(self.gridviewer.getSelection())
            model = self.gridviewer.getInput()
            self.gridviewer.addInputChangedListener(self)
            self.inputChanged(model, None)
        return

    def handleSelectionChanged(self, selection):
        step = None
        if len(selection) > 0:
            step = selection[0]
        self.stepSelectionChanged(step)
        self.Refresh()
        return

    def stepSelectionChanged(self, step):
        self.step = step

    def getWidth(self):
        return 10

    def OnPaint(self, event):
        self.draw(wx.PaintDC(self), self.gutter)

    def draw(self, parentdc, gutter):
        pass

    def dispose(self):
        validator.getDefault().removeValidationListener(self)
        self.gridviewer.removeSelectionChangedListener(self)
        self.gridviewer.removeInputChangedListener(self)
        self.step = None
        if self.model is not None:
            self.model.removeModifyListener(self)
        return

    def recipeModelChanged(self, event):
        self.Refresh()

    def inputChanged(self, oldInput, newInput):
        model = newInput
        if self.model is not None and self.model != model:
            self.model.removeModifyListener(self)
        if model is not None:
            self.model = model
            self.model.addModifyListener(self)
        return


class Gutter(object):
    __module__ = __name__

    def __init__(self):
        self.control = None
        self.gridviewer = None
        self.grid = None
        self.old = (0, 0)
        self.ypos = 0
        self.sizing = False
        self.columns = []
        return

    def getGridViewer(self):
        return self.gridviewer

    def getGrid(self):
        return self.grid

    def addColumn(self, column):
        if column in self.columns:
            raise Exception('Column already exists! %s' % column)
        column.setGutter(self)
        self.columns.append(column)
        self.updateWidth()

    def removeColumns(self, column):
        if column in self.columns:
            column.setGutter(None)
            self.columns.remove(column)
            self.control.RemoveChild(column)
        self.updateWidth()
        return

    def updateWidth(self):
        wx.CallAfter(self.internalUpdateWidth)

    def internalUpdateWidth(self):
        width = 0
        for column in self.columns:
            width += column.getWidth()

        (x, y) = self.grid.GetVirtualSize()
        if width == 0:
            width = _DEFAULT_WIDTH
        self.control.SetVirtualSize((width, y))

    def setGrid(self, gridviewer):
        self.gridviewer = gridviewer
        self.grid = gridviewer.getGrid()
        wnd = self.grid.GetGridWindow()

    def OnScroll(self, event):
        event.Skip()
        self.handleScrolled(event)

    def createControl(self, parent):
        self.control = wx.Window(parent, -1, size=(_DEFAULT_WIDTH, -1), style=0)
        (ppx, ppy) = self.grid.GetScrollPixelsPerUnit()
        (x, y) = self.grid.GetVirtualSize()
        self.old = (x, y)
        self.y = 0
        self.control.SetVirtualSize((_DEFAULT_WIDTH, y))
        wnd = self.grid
        wnd.Bind(wx.EVT_SCROLLWIN, self.OnScroll)
        self.control.Bind(wx.EVT_SIZE, self.OnSize)
        return self.control

    def OnSize(self, event):
        event.Skip()
        if self.sizing:
            return
        self.sizing = True
        (width, height) = self.control.GetVirtualSize()
        lastx = 0
        for column in self.columns:
            column.SetPosition((lastx, 0))
            column.SetSize((column.getWidth(), height))
            lastx += column.getWidth()

        self.control.SetVirtualSize((lastx, -1))
        self.control.SetSize((lastx, -1))
        sizer = self.control.GetParent().GetSizer()
        if sizer is not None:
            (w, h) = self.control.GetSize()
            sizer.SetItemMinSize(self.control, lastx, h)
            sizer.Layout()
        self.sizing = False
        return

    def getStepY(self, step=None, index=None):
        """Get the Y position from the top of the window for the start of the
        step specified by step or index on the grid"""
        if step is None and index is None:
            return 0
        if step is not None:
            index = self.getStepIndex(step)
        headerHeight = self.grid.GetColLabelSize()
        rowHeight = self.grid.GetDefaultRowSize()
        return headerHeight + rowHeight * index
        return

    def getHeaderHeight(self):
        return self.grid.GetColLabelSize()

    def getStepIndex(self, step):
        return self.gridviewer.getIndexOfStep(step)

    def getRowHeight(self):
        return self.grid.GetDefaultRowSize()

    def DoDraw(self, event):
        dc = wx.PaintDC(self.control)
        dc.SetDeviceOrigin(0, self.ypos)

    def getControl(self):
        return self.control

    def handleScrolled(self, event):
        eventType = event.GetEventType()
        if event.GetOrientation() == wx.HORIZONTAL:
            return
        if eventType == wx.EVT_SCROLLWIN_LINEUP:
            self.y -= 1
        elif eventType == wx.EVT_SCROLLWIN_LINEDOWN:
            self.y += 1
        elif eventType == wx.EVT_SCROLLWIN_PAGEUP:
            self.y -= 10
        elif eventType == wx.EVT_SCROLLWIN_PAGEDOWN:
            self.y += 10
        elif eventType == wx.EVT_SCROLLWIN_TOP:
            self.y = self.cy = 0
        elif eventType == wx.EVT_SCROLLWIN_BOTTOM:
            self.y = 50
        elif eventType == wx.EVT_SCROLLWIN_THUMBTRACK:
            pass
        elif eventType == wx.EVT_SCROLLWIN_THUMBRELEASE:
            pass
        elif eventType == 10068:
            self.y += 1
        elif eventType == 10067:
            self.y -= 1
        else:
            self.y = event.GetPosition()
        self.scroll(self.y)
        self.control.Refresh()

    def updateDimensions(self):
        (ppx, ppy) = self.grid.GetScrollPixelsPerUnit()
        (x, y) = self.grid.GetVirtualSize()
        self.control.SetVirtualSize((_DEFAULT_WIDTH, y))
        self.old = (x, y)

    def scroll(self, pos):
        (ppx, ppy) = self.grid.GetScrollPixelsPerUnit()
        (x, y) = self.grid.GetVirtualSize()
        if (x, y) != self.old:
            self.updateDimensions()
        hh = self.getHeaderHeight()
        self.ypos = 0 - pos * ppy
        self.control.ScrollWindow(0, self.ypos)
        map((lambda column: column.SetPosition((column.GetPosition()[0], self.ypos))), self.columns)

    def dispose(self):
        map((lambda column: column.dispose()), self.columns)


class ErrorColumn(GutterColumn):
    __module__ = __name__

    def __init__(self, parent):
        GutterColumn.__init__(self, parent)
        self.width = ui.images.getImage(ui.images.ERROR_ICON).GetWidth() + 1
        self.cachedErrorIndices = {}
        self.errorIcons = []
        self.Bind(wx.EVT_SIZE, self.OnSize)

    def OnSize(self, event):
        event.Skip()
        self.positionIcons()

    def positionIcons(self):
        (start, end) = self.getVisibleRowRange()
        for icon in self.errorIcons:
            if start <= icon[0] <= end:
                self.positionIcon(icon)

    def positionIcon(self, icontup):
        (index, error, icon) = icontup
        y = self.gutter.getStepY(index=index)
        icon.getControl().SetPosition((0, y))

    def setErrorIcon(self, error, index):
        icn = ui.widgets.contentassist.ContentAssistant(self)
        icn.setWarning(error.getDescription())
        icn.warn()
        icn.getControl().SetBackgroundColour(wx.WHITE)
        self.errorIcons.append((index, error, icn))

    def clearErrorIcons(self):
        icons = copy.copy(self.errorIcons)
        self.errorIcons = []
        for icon in icons:
            ctrl = icon[2].getControl()
            self.RemoveChild(ctrl)
            ctrl.Destroy()

    def validationEvent(self, valid, errors):
        GutterColumn.validationEvent(self, valid, errors)
        self.cacheInvalidSteps()
        self.positionIcons()

    def cacheInvalidSteps(self):
        v = validator.getDefault()
        self.cachedErrorIndices.clear()
        self.clearErrorIcons()
        if v.isValid():
            return
        for error in v.getErrors():
            if not validator.participant.KEY_STEP in error.getKeys():
                continue
            step = error.getStep()
            index = self.gutter.getStepIndex(step)
            if not self.cachedErrorIndices.has_key(index):
                self.cachedErrorIndices[index] = []
            self.cachedErrorIndices[index].append(error)
            self.setErrorIcon(error, index)

    def getVisibleRowRange(self):
        """Return the range of rows visible"""
        (start, end) = (
         -1, -1)
        for i in range(self.grid.GetNumberRows()):
            vis = self.grid.IsVisible(i, 0, False)
            if vis and start == -1:
                start = i
                continue
            if start == -1:
                continue
            end = i
            if not vis and start != -1:
                break

        return (
         start, end)

    def getWidth(self):
        return self.width

    def draw(self, dc, gutter):
        (w, h) = self.GetSize()
        dc.SetBrush(wx.WHITE_BRUSH)
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.DrawRectangle(0, 0, w, h)
        dc.SetPen(wx.LIGHT_GREY_PEN)
        dc.DrawLine(self.width - 1, 0, self.width - 1, h)


class LoopColumn(GutterColumn):
    __module__ = __name__

    def __init__(self, parent):
        GutterColumn.__init__(self, parent)
        self.SetSize((self.getWidth(), -1))
        self.invalidPen = wx.Pen(wx.RED, 2)
        self.normalPen = wx.Pen(wx.BLACK, 1)

    def getWidth(self):
        return 8

    def drawArrow(self, dc, x, y, x2):
        dc.DrawLine(x, y, x2, y)
        dc.DrawLine(x2 - 2, y - 2, x2, y)
        dc.DrawLine(x2 - 2, y + 2, x2, y)

    def isValidLoop(self, step):
        v = validator.getDefault()
        if v.isValid():
            return True
        for error in v.getErrors():
            if grideditor.utils.validation.KEY_LOOPING in error.getKeys():
                if error.getStep() == step:
                    return False

        return True

    def draw(self, dc, gutter):
        if self.step is None:
            return
        if not self.step.doesRepeat():
            return
        (w, h) = self.GetSize()
        gh = gutter.getHeaderHeight()
        dc.SetClippingRegion(0, gh, w, h - gh)
        valid = self.isValidLoop(self.step)
        stepIndex = gutter.getStepIndex(self.step)
        lastStepIndex = stepIndex + self.step.getRepeatEnclosingSteps()
        firstY = gutter.getStepY(index=stepIndex)
        lastY = gutter.getStepY(index=lastStepIndex)
        middleX = 1
        endWidth = self.getWidth()
        rowHeightY = gutter.getRowHeight()
        midRowHeight = rowHeightY / 2
        if not valid:
            dc.SetBrush(wx.RED_BRUSH)
            dc.SetPen(wx.TRANSPARENT_PEN)
            y = lastY - firstY + rowHeightY
            dc.DrawRectangle(0, firstY, endWidth, y)
            dc.SetPen(wx.NullPen)
        dc.SetPen(self.normalPen)
        if stepIndex != lastStepIndex:
            self.drawArrow(dc, middleX, firstY + midRowHeight, endWidth)
            self.drawArrow(dc, middleX, lastY + midRowHeight, endWidth)
            dc.DrawLine(middleX, firstY + midRowHeight, middleX, lastY + midRowHeight)
        else:
            y = firstY + midRowHeight
            self.drawArrow(dc, middleX, y - 2, endWidth)
            self.drawArrow(dc, middleX, y + 2, endWidth)
            dc.DrawLine(middleX, y - 2, middleX, y + 2)
        dc.DestroyClippingRegion()
        return
