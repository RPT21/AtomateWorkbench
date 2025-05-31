# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/grideditor/src/grideditor/recipegridviewer.py
# Compiled at: 2004-12-07 12:28:55
from wx.grid import *
from wx import *
import logging, plugins.poi.poi.views.viewers, wx, plugins.poi.poi.actions.menumanager
import plugins.ui.ui.undomanager, plugins.grideditor.grideditor.constants as grideditor_constants
import plugins.grideditor.grideditor.recipegridviewercontentprovider as grideditor_recipegridviewercontentprovider
import plugins.grideditor.grideditor.recipegrideditortable as grideditor_recipegrideditortable
import plugins.grideditor.grideditor.images as images
import plugins.grideditor.grideditor.messages as messages
import plugins.grideditor.grideditor.actions as grideditor_actions
import plugins.grideditor.grideditor.gutter as grideditor_gutter
from plugins.grideditor.grideditor.actions import SelectionDispatchAction
from plugins.grideditor.grideditor.recipemodel import RecipeModelEventListener
from plugins.poi.poi.views.viewers import SelectionProvider
import plugins.poi.poi as poi
import plugins.ui.ui as ui
import plugins.grideditor.grideditor as grideditor

DEBUG = False
logger = logging.getLogger('grideditor')

class ActionGroup(poi.actions.ActionContributionItem):
    __module__ = __name__

    def fillMenu(self, parent):
        if not self.isEnabled():
            return
        poi.actions.ActionContributionItem.fillMenu(self, parent)


class DeleteSelectedAction(SelectionDispatchAction):
    __module__ = __name__

    def __init__(self, editor):
        SelectionDispatchAction.__init__(self, 'Remove Selected Step')
        self.editor = editor

    def runWithSelection(self, selection):
        if len(selection) == 0:
            return
        firstElement = selection[0]
        stepIndex = self.editor.getIndexOfStep(firstElement)
        self.editor.removeSteps(stepIndex, len(selection))


class InsertStepAfterSelectionAction(SelectionDispatchAction):
    __module__ = __name__

    def __init__(self, editor):
        SelectionDispatchAction.__init__(self, 'Insert After Selection')
        self.editor = editor

    def runWithSelection(self, selection):
        print(('Insert After Selection', selection, self.editor))


class RecipeGridViewer(RecipeModelEventListener, SelectionProvider):
    __module__ = __name__

    def __init__(self):
        SelectionProvider.__init__(self)
        self.focus = False
        self.focusing = False
        self.hasFocus = False
        self.input = None
        self.reentrantSelectionEvent = False
        self.inputChangedListeners = []
        self.deleteSelectedAction = DeleteSelectedAction(self)
        self.addSelectionChangedListener(self.deleteSelectedAction)
        self.insertAfterAction = InsertStepAfterSelectionAction(self)
        self.currentGridCursorRow = 0
        self.lastRowSelected = -1
        self.addSelectionChangedListener(self.insertAfterAction)
        self.shown = True
        return

    def addInputChangedListener(self, listener):
        if not listener in self.inputChangedListeners:
            self.inputChangedListeners.append(listener)

    def removeInputChangedListener(self, listener):
        if listener in self.inputChangedListeners:
            self.inputChangedListeners.remove(listener)

    def fireInputChanged(self, oldInput, newInput):
        list(map((lambda p: p.inputChanged(oldInput, newInput)), self.inputChangedListeners))

    def recipeModelAboutToChange(self, event):
        pass

    def recipeModelChanged(self, event):
        global logger
        logger.debug("Recipe Model Changed: '%s'" % event)
        if event.getEventType() in [event.CHANGE_DEVICE, event.REMOVE_DEVICE, event.ADD_DEVICE, event.CHANGE, event.ADD, event.REMOVE]:
            self.updateGridView()

    def update(self):
        if self.grid is None:
            return
        self.updateGridView()
        return

    def updateGridView(self):
        self.updateTitleBar()
        self.fixRowLabelWidth()
        self.grid.ForceRefresh()

    def saveValue(self):
        self.grid.SaveEditControlValue()

    def updateTitleBar(self):
        if self.getInput() is None:
            text = None
        else:
            recipe = self.getInput().getRecipe()
            version = recipe.getUnderlyingResource()
            project = version.getProject()
            suffix = ''
            if recipe.isDirty():
                suffix = '*'
            text = '%s-%s %s' % (project.getName(), version.getNumber(), suffix)
        ui.getDefault().getMainFrame().setTitle(text)
        return

    def addDevice(self, device):
        self.getInput().addDevice(device)

    def removeDevice(self, device):
        self.getInput().removeDevice(device)

    def getInput(self):
        return self.input

    def setInput(self, input):
        oldInput = self.input
        if self.input is not None:
            self.input.removePreModifyListener(self)
            self.input.removeModifyListener(self)
        self.input = input
        if input is not None:
            self.input.addPreModifyListener(self)
            self.input.addModifyListener(self)
        try:
            self.contentprovider.setInput(input)
            self.fireInputChanged(oldInput, input)
        except Exception as msg:
            logger.exception(msg)
            logger.error("Unable to parse and display recipe: '%s'" % msg)

        self.updateGridView()
        self.fireStepSelected()
        return

    def bindFocus(self, control):
        for child in control.GetChildren():
            self.bindFocus(child)

    def isWindowContainer(self, window, root):
        for child in root.GetChildren():
            if window.GetId() == child.GetId():
                return True
            isit = self.isWindowContainer(window, child)
            if isit:
                return True

        return False

    def setFocus(self, focus):
        if self.focusing:
            return
        self.focusing = True
        changed = self.focus != focus
        self.focus = focus
        self.view.setFocus(focus)
        if focus is False and changed:
            if self.grid.IsCellEditControlShown():
                self.grid.SaveEditControlValue()
                self.grid.HideCellEditControl()
        self.focusing = False

    def OnSetFocus(self, event):
        event.Skip()
        if self.hasFocus:
            return
        self.hasFocus = True

    def OnKillFocus(self, event):
        event.Skip()
        if not self.hasFocus:
            return
        self.hasFocus = False

    def createControl(self, composite):
        view = poi.views.StackedView()
        view.createControl(composite)
        self.view = view
        self.control = wx.Panel(view.getContent(), -1)
        self.contentprovider = grideditor_recipegridviewercontentprovider.RecipeGridViewerContentProvider()
        self.wxtable = grideditor_recipegrideditortable.RecipeGridEditorTable(self.contentprovider)
        self.contentprovider.setManagedTable(self.wxtable)
        self.grid = wx.Grid(self.control, -1)
        self.grid.SetHelpText(grideditor_constants.HELP_GRIDEDITOR)
        self.grid.SetScrollRate(10, 10)
        self.grid.SetDefaultRowSize(20, True)
        self.grid.SetGridLineColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DDKSHADOW))
        self.grid.EnableDragRowSize(False)
        self.grid.SetTable(self.wxtable)
        self.grid.SetColLabelSize(10)
        self.grid.SetCellHighlightPenWidth(1)
        self.grid.SetCellHighlightColour(grideditor.getDefault().getHighlightStepColor())
        self.pork = False
        self.gutter = grideditor_gutter.Gutter()
        self.gutter.setGrid(self)
        gtrctrl = self.gutter.createControl(self.control)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(gtrctrl, 0, wx.EXPAND | wx.ALL, 0)
        sizer.Add(self.grid, 1, wx.EXPAND | wx.ALL, 0)
        if DEBUG:
            hsizer = wx.BoxSizer(wx.HORIZONTAL)
            deleteButton = grideditor_actions.ActionButton(self.deleteSelectedAction, self.control)
            insertAfterButton = grideditor_actions.ActionButton(self.insertAfterAction, self.control)
            hsizer.Add(deleteButton.getControl(), 0, wx.ALL, 5)
            hsizer.Add(insertAfterButton.getControl(), 0, wx.ALL, 5)
            sizer.Add(hsizer, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Fit(self.control)
        self.control.SetSizer(sizer)
        self.control.SetAutoLayout(True)
        self.control.Bind(wx.EVT_SIZE, self.OnSize, self.control)
        self.grid.Bind(EVT_GRID_RANGE_SELECT, self.OnGridRangeSelect, self.grid)
        self.grid.Bind(EVT_GRID_SELECT_CELL, self.OnGridCellSelect, self.grid)
        self.grid.Bind(EVT_GRID_CELL_RIGHT_CLICK, self.OnShowGridContextMenu)
        self.grid.Bind(EVT_GRID_LABEL_LEFT_CLICK, self.OnGridLabelLeftClick, self.grid)
        self.grid.Bind(EVT_GRID_LABEL_LEFT_DCLICK, self.OnGridLabelLeftDClick, self.grid)
        self.grid.Bind(EVT_GRID_LABEL_RIGHT_CLICK, self.OnShowColumnContextMenu, self.grid)
        self.grid.Bind(EVT_GRID_CELL_CHANGED, self.OnGridCellChange, self.grid)
        self.grid.SetRowLabelSize(30)
        wx.EVT_KEY_DOWN(self.grid, self.OnKeyDown)
        self.bindPaintEvents()
        self.createContextMenu()
        self.view.setTitle(messages.get('view.title'))
        self.view.setTitleImage(images.getImage(images.VIEW_ICON))
        self.control = view.getControl()
        self.createDefaultGutterColumns()

    def createDefaultGutterColumns(self):
        ctrl = self.gutter.getControl()
        looper = grideditor_gutter.LoopColumn(ctrl)
        errorer = grideditor_gutter.ErrorColumn(ctrl)
        self.gutter.addColumn(errorer)
        self.gutter.addColumn(looper)

    def OnGridCellChange(self, event):
        event.Skip()
        if False:
            print(('Grid Cell Change:', event.GetCol()))
            row = event.GetRow()
            column = self.contentprovider.getRealIndexOfCol(event.GetCol())
            print(('\tfor', col))

    def OnShowColumnContextMenu(self, event):
        logger.debug("Show Column Context Menu: '%s'" % event.GetCol())

    def OnGridLabelLeftClick(self, event):
        if event.GetCol() == -1:
            event.Skip()

    def OnGridLabelLeftDClick(self, event):
        if event.GetCol() == -1:
            event.Skip()
            return
        index = event.GetCol()
        column = self.contentprovider.getVisibleColumn(index)
        column.handleDoubleClick()

    def bindPaintEvents(self):
        wnd = self.grid.GetGridRowLabelWindow()
        wnd = self.grid.GetGridColLabelWindow()
        wx.EVT_PAINT(wnd, self.OnHeaderLabelPaint)

    def OnRowLabelPaint(self, event):
        self.rowLabelPaint(self.grid.GetGridRowLabelWindow())

    def OnHeaderLabelPaint(self, event):
        self.headerLabelPaint(self.grid.GetGridColLabelWindow())

    def headerLabelPaint(self, window):
        dc = wx.PaintDC(window)
        currHeight = self.grid.GetColLabelSize()
        totColSize = -self.grid.GetViewStart()[0] * self.grid.GetScrollPixelsPerUnit()[0]
        for col in range(self.grid.GetNumberCols()):
            renderer = self.contentprovider.getHeaderRenderer(col)
            (w, h) = (self.grid.GetColSize(col), self.grid.GetColLabelSize())
            bestsize = renderer.getBestSize()
            if bestsize[1] > h:
                self.grid.SetColLabelSize(bestsize[1])
                for c in range(self.grid.GetNumberCols()):
                    r = self.contentprovider.getHeaderRenderer(c)
                    bs = r.getBestSize()
                    r.setSize((bs[0], bestsize[1]))

                h = bestsize[1]
            rect = ((totColSize, 0), (w, h))
            renderer.draw(dc, rect)
            totColSize += w

    def getGrid(self):
        return self.grid

    def rowLabelPaint(self, window):
        """
        Draw the labels
        """
        dc = wx.PaintDC(window)
        dc.DrawRectangle(wx.Point(0, 0), wx.Size(10, 10))
        rect = window.GetClientRect()
        dc.DrawRectangle(wx.Point(rect[0], rect[1]), wx.Size(rect[2], rect[3]))

    def onInsertRow(self):
        self.fixRowLabelWidth()

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
        numRows = self.input.getStepCount()
        width = defaultValue
        if numRows > 0:
            label = self.contentprovider.getRowLabel(numRows - 1)
            dc = wx.ClientDC(self.grid)
            hashStr = self.strLen(len(label))
            (w, h) = dc.GetTextExtent(hashStr)
            width = w + insets * 2
        rw = self.grid.GetRowLabelSize()
        if width < defaultValue:
            width = defaultValue
        if width != rw:
            self.grid.SetRowLabelSize(width)

    def OnShowGridContextMenu(self, event):
        event.Skip()
        menu = self.contextMenuManager.createContextMenu(self.grid)
        self.grid.PopupMenu(menu, event.GetPosition())

    def createContextMenu(self):
        self.contextMenuManager = poi.actions.menumanager.MenuManager(None, '#POPUP')
        mng = self.contextMenuManager
        mng.addItem(poi.actions.ActionContributionItem(ui.undomanager.UNDO_ACTION))
        mng.addItem(ActionGroup(ui.undomanager.REDO_ACTION))
        return

    def isNavigationKey(self, keycode):
        numpad_navs = [
         wx.WXK_NUMPAD_RIGHT, wx.WXK_NUMPAD_LEFT, wx.WXK_NUMPAD_UP, wx.WXK_NUMPAD_DOWN, wx.WXK_RIGHT, wx.WXK_LEFT, wx.WXK_UP, wx.WXK_DOWN]
        return keycode in numpad_navs

    def handleNavigation(self, keycode):
        return True

    def OnKeyDown(self, event):
        keycode = event.GetKeyCode()
        if self.isNavigationKey(keycode):
            proceed = self.handleNavigation(keycode)
            if not proceed:
                event.Skip()
                return
        if keycode == wx.WXK_TAB:
            acquirePrev = True
            self.tabPressed()
            if event.m_shiftDown:
                self.moveToPrevCell()
            else:
                self.moveToNextCell()
            return
        elif keycode == wx.WXK_NUMPAD_ENTER:
            self.closeCellEditor()
            return
        elif keycode == wx.WXK_RETURN:
            self.saveReturn()
            return
        event.Skip()

    def saveReturn(self):
        self.closeCellEditor()
        self.moveToNextCell()

    def moveToPrevCell(self):
        (row, col) = (
         self.grid.GetGridCursorRow(), self.grid.GetGridCursorCol())
        (nrow, ncol) = (self.grid.GetNumberRows(), self.grid.GetNumberCols())
        (frow, fcol) = (
         row, col - 1)
        if frow - 1 < 0 and fcol < 0:
            return
        if fcol < 0:
            fcol = ncol - 1
            if frow > 0:
                frow = frow - 1
        self.grid.SetGridCursor(frow, fcol)

    def moveToNextCell(self):
        (row, col) = (
         self.grid.GetGridCursorRow(), self.grid.GetGridCursorCol())
        (nrow, ncol) = (self.grid.GetNumberRows(), self.grid.GetNumberCols())
        (frow, fcol) = (
         row, col + 1)
        if frow + 1 >= nrow and fcol >= ncol:
            return
        if fcol >= ncol:
            fcol = 0
            if frow < nrow - 1:
                frow = frow + 1
        self.grid.SetGridCursor(frow, fcol)

    def preferencesChanged(self):
        if self.grid is None:
            return
        self.grid.SetCellHighlightColour(grideditor.getDefault().getHighlightStepColor())
        return

    def closeCellEditor(self):
        if self.grid.IsCellEditControlEnabled():
            self.grid.SaveEditControlValue()
            self.grid.HideCellEditControl()

    def tabPressed(self):
        prefs = grideditor.getDefault().getPreferencesStore().getPreferences()
        try:
            acquire = prefs.get('tab-acquires-previous').tolower() == 'true'
        except Exception as msg:
            acquire = True

        if not acquire:
            return
        row = self.grid.GetGridCursorRow()
        col = self.grid.GetGridCursorCol()
        self.contentprovider.acquireValueFromPrev(row, col)

    def updateRowSelection(self, last, current):
        self.grid.BeginBatch()
        cols = self.grid.GetNumberCols()
        msg = wx.GridTableMessage(self.grid.GetTable(), wx.GRIDTABLE_REQUEST_VIEW_GET_VALUES, last, 1)
        self.grid.ProcessTableMessage(msg)
        msg = wx.GridTableMessage(self.grid.GetTable(), wx.GRIDTABLE_REQUEST_VIEW_GET_VALUES, current, 1)
        self.grid.ProcessTableMessage(msg)
        self.grid.EndBatch()

    def fireColumnCellSelected(self):
        pass

    def OnGridCellSelect(self, event):
        event.Skip()
        if event.GetCol() != self.grid.GetGridCursorCol():
            self.fireColumnCellSelected()
        newrow = event.GetRow()
        self.currentGridCursorRow = newrow
        self.updateRowSelection(self.lastRowSelected, newrow)
        self.lastRowSelected = newrow
        self.fireStepSelected()

    def fireStepSelected(self):
        event = self.getStepSelected()
        if event is None:
            event = []
        else:
            event = [
             event]
        logger.debug('Step selection event: %s' % event)
        self.fireSelectionChanged(event)
        return

    def getSelection(self):
        return self.getStepsSelected()

    def getStepsSelected(self):
        """Return the steps selected"""
        selection = []
        if self.grid.GetNumberRows() == 0:
            return []
        rows = []
        rows = self.grid.GetSelectedRows()
        if len(rows) == 0:
            rows = [
             self.grid.GetGridCursorRow()]
        for rowIndex in rows:
            selection.append(self.input.getStepAt(rowIndex))

        return selection

    def getStepSelected(self):
        selection = []
        if self.grid.GetNumberRows() == 0:
            return None
        row = self.currentGridCursorRow
        step = self.input.getStepAt(row)
        return step

    def OnGridRangeSelect(self, event):
        event.Skip()
        if not event.Selecting():
            return
        selection = []
        numrows = event.GetBottomRow() + 1 - event.GetTopRow()
        if numrows > 1:
            self.grid.ClearSelection()
            for row in range(event.GetTopRow(), event.GetBottomRow() + 1):
                self.grid.SelectRow(row, True)

        for stepsIndex in range(event.GetTopRow(), event.GetBottomRow() + 1):
            step = self.input.getStepAt(stepsIndex)
            selection.append(step)

        event = selection
        self.fireSelectionChanged(event)

    def OnVisibilityButton(self, event):
        if not self.pork:
            self.contentprovider.hideColumn(0)
            self.pork = True
        else:
            self.contentprovider.showColumn(0)
            self.pork = False

    def OnSize(self, event):
        self.grid.ForceRefresh()
        event.Skip()

    def getIndexOfSelection(self):
        step = self.getStepSelected()
        if step is None:
            if self.input.getStepCount() == 0:
                return -1
            return self.input.getStepCount()
        index = self.getIndexOfStep(step)
        return index

    def removeSteps(self, pos, number):
        self.input.removeSteps(pos, number)

    def getIndexOfStep(self, step):
        steps = self.input.getSteps()
        if step not in steps:
            return -1
        return steps.index(step)

    def createNewStepAfterSelection(self):
        stepIndex = self.getIndexOfSelection()
        if stepIndex < 0:
            stepIndex = 0
        else:
            stepIndex += 1
        return self.createNewStepAtIndex(stepIndex)

    def setStepSelected(self, stepIndex):
        self.grid.SetGridCursor(stepIndex, 0)
        self.grid.MakeCellVisible(stepIndex, 0)

    def createNewStepAtIndex(self, stepIndex):
        self.getInput().insertStep(stepIndex)
        self.grid.SetGridCursor(stepIndex, 0)
        return stepIndex

    def deleteSelectedSteps(self):
        steps = self.getStepsSelected()
        logger.debug("DELETE STEPS SELECTED: '%d'" % len(steps))
        for step in steps:
            logger.debug("\t'%s'" % str(step))
            self.getInput().removeStep(step)

    def insertStepsAfterIndex(self, offset, steps):
        newsteps = []
        for step in steps:
            newsteps.append(step.clone())

        self.getInput().insertStepsAfterOffset(offset, newsteps)

    def insertStepsAfterSelection(self, steps):
        offset = self.getIndexOfSelection()
        if offset < 0:
            offset = 0
        else:
            offset += 1
        self.insertStepsAfterIndex(offset, steps)
        return offset

    def getControl(self):
        return self.control

    def dispose(self):
        logger.debug("Disposing of grid view based on current input '%s'" % str(self.input))
        if self.input is not None:
            self.input.removePreModifyListener(self)
            self.input.removeModifyListener(self)
        self.contentprovider.dispose()
        self.gutter.dispose()
        self.grid = None
        return

    def show(self, show):
        self.shown = show
        self.control.Show(show)
        if show:
            self.fireStepSelected()

    def isShowing(self):
        return self.shown
