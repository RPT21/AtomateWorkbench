# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/grideditor/src/grideditor/recipegridviewercontentprovider.py
# Compiled at: 2004-11-19 02:29:39
from wx.grid import *
from wx import *
import wx, logging
import plugins.grideditor.grideditor.durationcolumn as grideditor_durationcolumn
import plugins.grideditor.grideditor.recipemodel as grideditor_recipemodel
import plugins.grideditor.grideditor.tablecolumn as grideditor_tablecolumn
import plugins.grideditor.grideditor.__init__ as grideditor

logger = logging.getLogger('grideditor.contentprovider')


class RecipeGridViewerContentProvider(grideditor_recipemodel.RecipeModelEventListener):
    __module__ = __name__

    def __init__(self):
        self.input = None
        self.columns = []
        self.visibleColumns = []
        self.managedTable = None
        self.colattrs = {}
        self.contributions = []
        self.suppress = False
        return

    def suppressContentUpdates(self, suppress):
        self.suppress = suppress

    def recipeModelAboutToChange(self, event):
        pass

    def dispose(self):
        if self.input is not None:
            self.input.removePreModifyListener(self)
            self.input.removeModifyListener(self)
        for column in self.columns:
            column.dispose()

        return

    def recipeModelChanged(self, event):
        if self.suppress:
            return
        etype = event.getEventType()
        if etype == grideditor_recipemodel.ADD:
            if event.getRowOffset() != grideditor_recipemodel.ALL:
                self.managedTable.insertRows(event.getRowOffset(), event.getNumRows())
            elif event.getColOffset() != grideditor_recipemodel.ALL:
                pass
        elif etype == grideditor_recipemodel.ADD_DEVICE:
            self.addDeviceColumnContribution(event.getDevice())
        elif etype == grideditor_recipemodel.REMOVE_DEVICE:
            self.removeDeviceColumnContribution(event.getDevice())
        elif etype == grideditor_recipemodel.REMOVE:
            if event.getRowOffset() != grideditor_recipemodel.ALL:
                self.managedTable.removeRows(event.getRowOffset(), event.getNumRows())
        elif etype == grideditor_recipemodel.CHANGE:
            if event.getRowOffset() != grideditor_recipemodel.ALL:
                pass
            else:
                self.managedTable.updateAll()

    def setManagedTable(self, table):
        self.managedTable = table

    def getAttribute(self, row, col, extra):
        realIndex = self.getRealIndexOfCol(col)
        column = self.visibleColumns[col]
        if not column in self.colattrs:
            attr = wx.GridCellAttr()
            self.colattrs[column] = attr
            attr.SetEditor(column.getCellEditor())
            attr.SetRenderer(column.getCellRenderer())
        else:
            attr = self.colattrs[column]
        if attr == None:
            attr = wx.GridCellAttr()
            self.colattrs[column] = attr
            attr.SetEditor(column.getCellEditor())
            attr.SetRenderer(column.getCellRenderer())
        return attr.Clone()

    def hideColumn(self, columnIndex):
        pass

    def showColumn(self, columnIndex):
        if True:
            return
        if columnIndex not in self.visibleColumns:
            i = 0
            for visIndex in list(self.visibleColumns.keys()):
                if visIndex > columnIndex:
                    break
                i += 1

            self.visibleColumns[i] = columnIndex
            self.managedTable.showColumn(i)

    def addColumn(self, column):
        column.setContentProvider(self)
        self.columns.append(column)
        idx = self.columns.index(column)
        self.visibleColumns.append(column)
        self.managedTable.showColumn(self.visibleColumns.index(column))

    def getRealIndexOfCol(self, col):
        return self.visibleColumns[col]

    def getRowCount(self):
        if self.input is not None:
            return self.input.getStepCount()
        return 0

    def getColumnCount(self):
        return len(self.visibleColumns)

    def getHeaderRenderer(self, col):
        return self.visibleColumns[col].getHeaderRenderer()

    def getRowLabel(self, row):
        return '%i' % (row + 1)

    def getColLabel(self, col):
        """Gets the column label for the col ON THE SCREEN"""
        column = self.visibleColumns[col]
        return column.getHeaderLabel()

    def acquireValueFromPrev(self, row, col):
        if row <= 0:
            return
        prevval = self.getValueAt(row - 1, col)
        self.visibleColumns[col].setValueAt(row, prevval)
        self.managedTable.updateRow(row)

    def getValueAt(self, row, col):
        return self.visibleColumns[col].getValueAt(row)

    def setInput(self, input):
        """Set the Recipe Model"""
        if self.input is not None:
            self.input.removePreModifyListener(self)
            self.input.removeModifyListener(self)
        self.managedTableRemoveAllRows()
        self.removeAllColumns()
        self.input = input
        if input is not None:
            self.input.addPreModifyListener(self)
            self.input.addModifyListener(self)
        self.createDurationColumn()
        self.loadColumnContributions()
        self.manageTableInsertedRows(0, self.getRowCount())
        return

    def manageTableInsertedRows(self, pos, numRows):
        self.managedTable.insertRows(pos, numRows)

    def managedTableRemoveAllRows(self):
        self.managedTable.removeAllRows()

    def addDeviceColumnContribution(self, device):
        offset = len(self.columns)
        params = self.setupDeviceColumnContribution(device)
        if params is None:
            return
        self.addColumn(params[3])
        params[3].setWidth(params[2])
        return

    def removeDeviceColumnContribution(self, device):
        """
        Remove the device and column contribution. Not the same as hiding!
        The contribution is disposed
        """
        result = None
        for contribution in self.contributions:
            if contribution.getContribution().getDevice() == device:
                result = contribution
                break

        if not result:
            return
        index = self.columns.index(result)
        visindex = self.visibleColumns.index(result)
        self.managedTable.removeColumn(visindex)
        self.contributions.remove(result)
        self.columns.remove(result)
        self.visibleColumns.remove(result)
        for con in self.contributions:
            pass

        result.dispose()
        return

    def getVisibleColumn(self, index):
        return self.visibleColumns[index]

    def setupDeviceColumnContribution(self, device):
        deviceType = device.getType()
        contribution = None
        factory = grideditor.getColumnContributionFactory(deviceType)
        if factory is None:
            return None
        contribution = factory.getInstance(deviceType)
        column = grideditor_tablecolumn.ColumnContributorTableColumnAdapter(contribution, device, self.input)
        self.contributions.append(column)
        uihints = device.getUIHints()
        columnhints = uihints.getChildNamed('column')
        try:
            order = int(columnhints.getAttribute('order'))
            visible = columnhints.getAttribute('visible') == 'true'
            width = int(columnhints.getAttribute('width'))
        except Exception as msg:
            print(('* WARNING: Missing column node in uihints for', device))
            order = 0
            visible = True
            width = 100

        return (
         order, visible, width, column)

    def loadColumnContributions(self):
        contributions = {}
        deviceIndex = 0
        ordering = []
        idx = 0
        for device in self.input.getDevices():
            params = self.setupDeviceColumnContribution(device)
            if params is None:
                deviceIndex += 1
                continue
            ordering.append(params)
            deviceIndex += 1

        def sortit(x, y):
            if x[0] < y[0]:
                return -1
            elif x[0] > y[0]:
                return 1
            return 0

        ordering.sort(sortit)
        index = 0
        for item in ordering:
            if item[1]:
                self.addColumn(item[3])
            item[3].setWidth(item[2])
            index += 1

        return

    def removeAllColumns(self):
        self.managedTable.hideAllColumns()
        del self.contributions[0:]
        del self.columns[0:]
        del self.visibleColumns[0:]

    def createDurationColumn(self):
        self.addColumn(grideditor_durationcolumn.DurationColumn(self.input))
