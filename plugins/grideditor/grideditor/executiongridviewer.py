# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/grideditor/src/grideditor/executiongridviewer.py
# Compiled at: 2004-09-23 02:40:57
from wx.grid import *
from wx import *
import wx.grid as gridlib
import logging, poi.views.viewers, threading, wx, ui, poi.actions.menumanager, poi.actions, ui.undomanager, grideditor.recipegridviewercontentprovider, grideditor.recipegrideditortable, grideditor.recipemodel, grideditor.selections, grideditor.images as images, grideditor.messages as messages, grideditor.actions, grideditor.gutter, grideditor.tablecolumn, executionengine, executionengine.engine, resourcesui.utils
DEBUG = False
logger = logging.getLogger('grideditor')
executionGridColumnContributionsFactories = {}

def addExecutionGridColumnContributionFactory(strType, factory):
    global executionGridColumnContributionsFactories
    executionGridColumnContributionsFactories[strType] = factory


def removeExecutionGridColumnContributionFactory(strType, factory):
    if executionGridColumnContributionsFactories.has_key(strType):
        del executionGridColumnContributionsFactories[strType]


def getExecutionGridColumnContributionFactory(strType):
    if not executionGridColumnContributionsFactories.has_key(strType):
        return None
    return executionGridColumnContributionsFactories[strType]


class ExecutionGridViewer(object):
    __module__ = __name__

    def __init__(self):
        executionengine.getDefault().addEngineInitListener(self)
        self.showing = False
        self.initialStep = 0

    def engineInit(self, engine):
        engine.addEngineListener(self)
        self.engine = engine
        wx.CallAfter(self.prepareStart)

    def prepareStart(self):
        try:
            grideditor.getDefault().getView().showGridEditorView(False)
        except Exception as msg:
            logger.exception(msg)

    def engineEvent(self, event):
        if event.getType() == executionengine.engine.TYPE_ENDING:
            self.engine.removeEngineListener(self)
            self.updateEnded()
        if event.getType() == executionengine.engine.TYPE_ENTERING_STEP:
            self.mediator.setCurrentStep(self.engine.getCurrentStepIndex())
            self.grid.ForceRefresh()

    def dispose(self):
        logger.debug('Removing execution grid viewer')
        executionengine.getDefault().removeEngineInitListener(self)

    def updateEnded(self):
        self.closeViewButton.Enable()

    def createControl(self, composite):
        view = poi.views.StackedView()
        view.createControl(composite)
        view.setTitle(messages.get('executionview.title'))
        self.view = view
        panel = wx.Panel(view.getContent(), -1)
        self.grid = gridlib.wxGrid(panel, -1)
        self.mediator = ExecutionGridMediator()
        self.table = ExecutionGridTable(self.mediator)
        self.mediator.setManagedTable(self.table)
        self.grid.SetTable(self.table)
        self.grid.SetScrollRate(10, 10)
        self.grid.SetDefaultRowSize(20, True)
        self.grid.SetGridLineColour(gridlib.wxSystemSettings_GetColour(gridlib.wxSYS_COLOUR_3DDKSHADOW))
        self.grid.EnableDragRowSize(False)
        self.grid.SetColLabelSize(10)
        self.grid.EnableEditing(False)
        self.grid.SetCellHighlightPenWidth(0)
        self.closeViewButton = wx.Button(panel, -1, messages.get('executionview.close.label'))
        self.closeViewButton.Disable()
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.grid, 1, wx.GROW)
        sizer.Add(wx.StaticLine(panel, -1), 0, wx.GROW | wx.TOP | wx.BOTTOM, 5)
        sizer.Add(self.closeViewButton, 0, wx.ALIGN_RIGHT | wx.RIGHT | wx.BOTTOM, 5)
        panel.SetSizer(sizer)
        panel.SetAutoLayout(True)

        def ignore(event):
            pass

        self.grid.Bind(EVT_GRID_CELL_LEFT_CLICK, ignore, self.grid)
        self.grid.Bind(EVT_GRID_LABEL_LEFT_CLICK, ignore, self.grid)
        wnd = self.grid.GetGridColLabelWindow()
        wx.EVT_PAINT(wnd, self.OnHeaderLabelPaint)
        self.closeViewButton.Bind(wx.EVT_BUTTON, self.OnCloseView)
        self.panel = panel
        return self.view.getControl()

    def OnHeaderLabelPaint(self, event):
        self.headerLabelPaint(self.grid.GetGridColLabelWindow())

    def headerLabelPaint(self, window):
        dc = wx.PaintDC(window)
        currHeight = self.grid.GetColLabelSize()
        totColSize = -self.grid.GetViewStart()[0] * self.grid.GetScrollPixelsPerUnit()[0]
        for col in range(self.grid.GetNumberCols()):
            renderer = self.mediator.getHeaderRenderer(col)
            if renderer is None:
                continue
            (w, h) = (
             self.grid.GetColSize(col), self.grid.GetColLabelSize())
            bestsize = renderer.getBestSize()
            if bestsize[1] > h:
                self.grid.SetColLabelSize(bestsize[1])
                for c in range(self.grid.GetNumberCols()):
                    r = self.mediator.getHeaderRenderer(c)
                    if r is None:
                        continue
                    bs = r.getBestSize()
                    r.setSize((bs[0], bestsize[1]))

                h = bestsize[1]
            rect = ((totColSize, 0), (w, h))
            renderer.draw(dc, rect)
            totColSize += w

        return

    def OnCloseView(self, event):
        event.Skip()
        self.hide()
        grideditor.getDefault().getView().showGridEditorView(True)

    def removeColumns(self):
        self.mediator.removeColumns()

    def createColumns(self):
        self.mediator.createColumns()
        self.fixRowLabelWidth()

    def show(self):
        self.closeViewButton.Disable()
        self.removeColumns()
        self.createColumns()

    def hide(self):
        self.closeViewButton.Disable()

    def getControl(self):
        return self.view.getControl()

    def strLen(self, len):
        buff = ''
        for i in range(len):
            buff += 'H'

        return buff

    def fixRowLabelWidth(self):
        """
        Fixes the width of the rows if necessary.  It takes the last row
        and then figures out the width of the text extent.  It adds
        4 to the insets on either side and then sets the width 
        of the table
        """
        defaultValue = 30
        insets = 4
        numRows = self.mediator.getRowCount()
        width = defaultValue
        if numRows > 0:
            label = self.mediator.getRowLabel(numRows - 1)
            dc = wx.ClientDC(self.grid)
            hashStr = self.strLen(len(label))
            (w, h) = dc.GetTextExtent(hashStr)
            width = w + insets * 2
        rw = self.grid.GetRowLabelSize()
        if width < defaultValue:
            width = defaultValue
        if width != rw:
            self.grid.SetRowLabelSize(width)


class ExecutionGridTable(gridlib.GridTableBase):
    __module__ = __name__

    def __init__(self, mediator):
        gridlib.GridTableBase.__init__(self)
        self.mediator = mediator

    def InsertCols(self, pos, num):
        grid = self.GetView()
        grid.BeginBatch()
        msg = gridlib.wxGridTableMessage(self, gridlib.wxGRIDTABLE_NOTIFY_COLS_INSERTED, pos, num)
        grid.ProcessTableMessage(msg)
        grid.EndBatch()
        grid.AdjustScrollbars()

    def DeleteRows(self, pos, num):
        if num == 0:
            return
        grid = self.GetView()
        grid.BeginBatch()
        msg = gridlib.wxGridTableMessage(self, gridlib.wxGRIDTABLE_NOTIFY_ROWS_DELETED, pos, num)
        grid.ProcessTableMessage(msg)
        grid.EndBatch()
        grid.AdjustScrollbars()

    def DeleteCols(self, pos, num):
        if num == 0:
            return
        grid = self.GetView()
        grid.BeginBatch()
        msg = gridlib.wxGridTableMessage(self, gridlib.wxGRIDTABLE_NOTIFY_COLS_DELETED, pos, num)
        grid.ProcessTableMessage(msg)
        grid.EndBatch()
        grid.AdjustScrollbars()

    def InsertRows(self, pos, num):
        grid = self.GetView()
        grid.BeginBatch()
        msg = gridlib.wxGridTableMessage(self, gridlib.wxGRIDTABLE_NOTIFY_ROWS_INSERTED, pos, num)
        grid.ProcessTableMessage(msg)
        grid.EndBatch()
        grid.AdjustScrollbars()
        grid.ForceRefresh()

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


class ExecutionGridColumn(object):
    __module__ = __name__

    def __init__(self, recipe):
        self.recipe = recipe
        self.headerRenderer = self.createHeaderRenderer()
        self.renderer = self.createRenderer()
        self.rendererWrapper = CellRendererWrapper(self.renderer, self)

    def createHeaderRenderer(self):
        return grideditor.tablecolumn.StringHeaderCellRenderer(self)

    def createRenderer(self):
        return StringCellRenderer()

    def getCellRenderer(self):
        return self.renderer

    def getHeaderRenderer(self):
        return self.headerRenderer

    def getHeaderImage(self):
        return None
        return

    def getHeaderLabel(self):
        return None
        return

    def getValueAt(self, row):
        return ''

    def getCellRendererWrapper(self):
        return self.rendererWrapper

    def dispose(self):
        pass


class ExecutionGridColumnContribution(ExecutionGridColumn):
    __module__ = __name__

    def __init__(self, device, recipe):
        ExecutionGridColumn.__init__(self, recipe)
        self.device = device


class DurationColumn(ExecutionGridColumn):
    __module__ = __name__

    def getHeaderLabel(self):
        return 'Duration'

    def createRenderer(self):
        return DurationCellRenderer()

    def getValueAt(self, row):
        return str(self.recipe.getStep(row).getDuration())


class CellRenderer(object):
    __module__ = __name__

    def __init__(self):
        pass

    def draw(self, grid, value, dc, isSelected, rect, row, isCurrentStep):
        pass

    def getBestSize(self, value):
        return (
         0, 0)


class StringCellRenderer(CellRenderer):
    __module__ = __name__

    def __init__(self):
        self.font = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
        self.inset = 5

    def draw(self, grid, value, dc, isSelected, rect, row, isCurrentStep):
        text = str(value)
        dc.SetFont(self.font)
        (w, h) = dc.GetTextExtent(text)
        x = self.inset
        y = (rect.height - h) * 0.5
        self.drawBackground(grid, dc, rect, isSelected, isCurrentStep)
        dc.DrawText(text, rect.x + x, rect.y + y)

    def getSelectedRowColor(self, grid):
        return wx.RED

    def getNormalRowColor(self, grid):
        return wx.WHITE

    def drawBackground(self, grid, dc, rect, isSelected, isCurrentStep):
        if isCurrentStep:
            color = self.getSelectedRowColor(grid)
        else:
            color = self.getNormalRowColor(grid)
        dc.SetPen(wx.Pen(color))
        dc.SetBrush(wx.Brush(color))
        dc.DrawRectangle(rect.x, rect.y, rect.width, rect.height)
        dc.SetBrush(wx.NullBrush)
        dc.SetPen(wx.NullPen)

    def getBestSize(self, value):
        text = str(value)
        (w, h) = dc.GetTextExtent(text)
        return (
         w, h)


class DurationCellRenderer(StringCellRenderer):
    __module__ = __name__

    def draw(self, grid, value, dc, isSelected, rect, row, isCurrentStep):
        ts = wx.TimeSpan.Seconds(int(value))
        text = ts.Format('%H:%M:%S')
        (w, h) = dc.GetTextExtent(text)
        x = self.inset
        y = (rect.height - h) * 0.5
        self.drawBackground(grid, dc, rect, isSelected, isCurrentStep)
        dc.DrawText(text, rect.x + x, rect.y + y)


class CellRendererWrapper(gridlib.GridCellRenderer):
    __module__ = __name__

    def __init__(self, renderer, column):
        gridlib.GridCellRenderer.__init__(self)
        self.renderer = renderer
        self.column = column
        self.currentStep = -1

    def setCurrentStep(self, stepIndex):
        self.currentStep = stepIndex

    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
        value = self.column.getValueAt(row)
        self.renderer.draw(grid, value, dc, isSelected, rect, row, self.currentStep == row)

    def GetBestSize(self):
        value = self.column.getValueAt(row)
        return self.renderer.getBestSize(value)

    def Clone(self):
        return CellRendererWrapper(self.renderer, self.column)


class ExecutionGridMediator(object):
    __module__ = __name__

    def __init__(self):
        self.columns = []
        self.recipe = None
        self.table = None
        self.colattrs = {}
        return

    def setCurrentStep(self, stepIndex):
        for column in self.columns:
            column.getCellRendererWrapper().setCurrentStep(stepIndex)

    def setManagedTable(self, table):
        self.table = table
        self.oldRowLength = 0

    def createColumns(self):
        recipe = ui.context.getProperty('recipe')
        if recipe is None:
            logger.warn('Attempt to create columns but no recipe is available')
            return
        self.columns.append(DurationColumn(recipe))
        for device in recipe.getDevices():
            factory = getExecutionGridColumnContributionFactory(device.getType())
            if factory is None:
                continue
            column = factory(device, recipe)
            self.columns.append(column)

        self.recipe = recipe
        self.oldRowLength = self.getRowCount()
        self.table.InsertCols(0, self.getColumnCount())
        self.table.InsertRows(0, self.getRowCount())
        return

    def removeColumns(self):
        self.table.DeleteCols(0, self.getColumnCount())
        self.table.DeleteRows(0, self.oldRowLength)
        del self.columns[0:]
        self.columns = []

    def getHeaderRenderer(self, col):
        return self.columns[col].getHeaderRenderer()

    def drawColumnHeader(self, col, dc):
        pass

    def getColLabel(self, col):
        return self.columns[col].getHeaderLabel()

    def getRowLabel(self, row):
        return '%d' % (row + 1)

    def getColumnCount(self):
        return len(self.columns)

    def getRowCount(self):
        if self.recipe is None:
            return 0
        return self.recipe.getStepsCount()
        return

    def getValueAt(self, row, col):
        return self.columns[col].getValueAt(row, col)

    def getAttribute(self, row, col, extra):
        if len(self.columns) == 0:
            return None
        column = self.columns[col]
        if not self.colattrs.has_key(column):
            attr = wxGridCellAttr()
            self.colattrs[column] = attr
            attr.SetRenderer(column.getCellRendererWrapper())
        else:
            attr = self.colattrs[column]
        if attr == None:
            attr = wxGridCellAttr()
            self.colattrs[column] = attr
            attr.SetRenderer(column.getCellRendererWrapper())
        return attr.Clone()
        return
