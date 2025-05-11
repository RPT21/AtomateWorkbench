# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/grideditor/src/grideditor/recipemodel.py
# Compiled at: 2004-11-02 21:50:14
import threading, wx, plugins.grideditor.grideditor.events, copy, logging
from plugins.grideditor.grideditor.events import EventObject
logger = logging.getLogger('recipemodel')

class RecipeModelEventListener:
    __module__ = __name__

    def recipeModelAboutToChange(self, event):
        pass

    def recipeModelChanged(self, event):
        pass


ALL = -1
ADD = 2
REMOVE = 3
CHANGE = 4
ADD_DEVICE = 5
REMOVE_DEVICE = 6
CHANGE_DEVICE = 7

class RecipeModelEvent(EventObject):
    __module__ = __name__

    def __init__(self, source, eventType, rowOffset=ALL, numRows=ALL, colOffset=ALL, numCols=ALL, device=None):
        self.ALL = ALL
        self.ADD = ADD
        self.REMOVE = REMOVE
        self.CHANGE = CHANGE
        self.ADD_DEVICE = ADD_DEVICE
        self.REMOVE_DEVICE = REMOVE_DEVICE
        self.CHANGE_DEVICE = CHANGE_DEVICE
        EventObject.__init__(self, source)
        self.eventType = eventType
        self.rowOffset = rowOffset
        self.numRows = numRows
        self.colOffset = colOffset
        self.numCols = numCols
        self.device = device

    def getDevice(self):
        return self.device

    def getEventType(self):
        return self.eventType

    def getModel(self):
        return self.getSource()

    def getRowOffset(self):
        return self.rowOffset

    def getNumRows(self):
        return self.numRows

    def getColOffset(self):
        return self.colOffset

    def getNumCols(self):
        return self.numCols

    def __repr__(self):
        typeDict = {ADD: 'ADD', CHANGE: 'CHANGE', REMOVE: 'REMOVE', ADD_DEVICE: 'ADD_DEVICE', REMOVE_DEVICE: 'REMOVE_DEVICE', CHANGE_DEVICE: 'CHANGE_DEVICE'}
        return '[RecipeModelEvent: Type=%s, rowOffset=%i, numRows=%i, colOffset=%i, numCols=%i]' % (typeDict[self.eventType], self.rowOffset, self.numRows, self.colOffset, self.numCols)


class RecipeModel(object):
    __module__ = __name__

    def __init__(self):
        self.modifyListeners = []
        self.preModifyListeners = []
        self.recipe = None
        self.stopFiring = False
        return

    def clear(self):
        event = RecipeModelEvent(self, REMOVE)
        self.fireRecipeModelAboutToChange(event)
        self.fireRecipeModelChanged(event)

    def removeStep(self, step):
        index = self.recipe.getStepIndex(step)
        event = RecipeModelEvent(self, REMOVE, index, 1)
        self.fireRecipeModelAboutToChange(event)
        self.recipe.removeStepByPtr(step)
        self.recipe.setDirty(True)
        self.fireRecipeModelChanged(event)

    def insertStep(self, index):
        """Insert a step at index"""
        newStep = self.recipe.createNewStep()
        event = RecipeModelEvent(self, ADD, index, 1)
        self.fireRecipeModelAboutToChange(event)
        self.recipe.insertStep(index, newStep)
        self.recipe.setDirty(True)
        self.fireRecipeModelChanged(event)

    def getRecipe(self):
        return self.recipe

    def setRecipe(self, recipe):
        event = RecipeModelEvent(self, CHANGE)
        self.fireRecipeModelAboutToChange(event)
        self.recipe = recipe
        self.fireRecipeModelChanged(event)

    def getDevice(self, deviceIndex):
        return self.recipe.getDevice(deviceIndex)

    def touch(self):
        event = RecipeModelEvent(self, CHANGE)
        self.fireRecipeModelAboutToChange(event)
        self.fireRecipeModelChanged(event)

    def updateRecipeOptions(self):
        event = RecipeModelEvent(self, CHANGE)
        self.fireRecipeModelAboutToChange(event)
        self.recipe.setDirty(True)
        self.fireRecipeModelChanged(event)

    def tagDeviceModified(self, device):
        event = RecipeModelEvent(self, CHANGE_DEVICE, device=device)
        self.fireRecipeModelAboutToChange(event)
        self.recipe.setDirty()
        self.fireRecipeModelChanged(event)

    def getEntryAtStep(self, step, device):
        deviceIndex = self.recipe.getDeviceIndex(device)
        return step.getEntry(deviceIndex)

    def getEntryAt(self, row, device):
        deviceIndex = self.recipe.getDeviceIndex(device)
        step = self.recipe.getStep(row)
        entry = step.getEntry(deviceIndex)
        return entry

    def getStepAt(self, row):
        return self.recipe.getStep(row)

    def getEntryIndexFromDevice(self, device):
        return self.getDevices().index(device)

    def updateStepEntry(self, step, device=None):
        row = self.recipe.getStepIndex(step)
        entryIndex = ALL
        if device is not None:
            entryIndex = self.getEntryIndexFromDevice(device)
        self.recipe.setDirty()
        event = RecipeModelEvent(self, CHANGE, row, numRows=1, colOffset=entryIndex, numCols=1, device=device)
        self.fireRecipeModelChanged(event)
        return

    def tagEntryUpdateAt(self, row, deviceIndex):
        event = RecipeEvent(self, row, 1, deviceIndex, 1)
        self.fireRecipeModelAboutToChange(event)
        self.recipe.setDirty(True)

    def markEntryUpdatedAt(self, row, deviceIndex):
        self.recipe.setDirty(True)
        event = RecipeEvent(self, row, 1, deviceIndex, 1)
        self.fireRecipeModelChanged(event)

    def fireRecipeModelAboutToChange(self, event):
        """All handlers should catch their own exceptions and not prevent this loop from continuing"""
        if self.stopFiring:
            return
        if False:
            logger.debug('*** PRE MODIFY LISTENERS ***')
            for listener in self.preModifyListeners:
                print(listener)

            logger.debug('*** END PREMODIFY LISTENERS ***')
        list(map((lambda p: p.recipeModelAboutToChange(event)), self.preModifyListeners))

    def fireRecipeModelChanged(self, event):
        """All handlers should catch their exceptions and not prevent this loop from continuing"""
        wx.CallAfter(self.internalFireRecipeModelChanged, event)

    def internalFireRecipeModelChanged(self, event):
        if self.stopFiring:
            return
        if False:
            logger.debug('*** MODIFY LISTENERS ***')
            for listener in self.modifyListeners:
                print(listener)

            logger.debug('*** END MODIFY LISTENERS ***')
        listeners = copy.copy(self.modifyListeners)
        for listener in listeners:
            try:
                listener.recipeModelChanged(event)
            except Exception as msg:
                logger.exception(msg)

    def moveRow(self, fromRow, toRow):
        """prevent move?"""
        if 0 > fromRow > self.getNumRows():
            return
        if toRow >= self.getNumRows():
            return
        event = RecipeModelEvent(self, REMOVE, fromRow, 1)
        event2 = RecipeModelEvent(self, CHANGE, fromRow, self.getNumRows() - fromRow)
        self.fireRecipeModelAboutToChange(event)
        self.fireRecipeModelAboutToChange(event2)
        self.recipe.setDirty(True)
        self.fireRecipeModelChanged(event)
        self.fireRecipeModelChanged(event2)

    def getSteps(self):
        return self.recipe.getSteps()

    def removeSteps(self, rowIndex, numRows):
        if 0 > rowIndex > self.getStepCount():
            return
        event = RecipeModelEvent(self, REMOVE, rowIndex, numRows)
        self.fireRecipeModelAboutToChange(event)
        self.recipe.removeSteps(rowIndex, numRows)
        self.recipe.setDirty(True)
        self.fireRecipeModelChanged(event)

    def addPreModifyListener(self, listener):
        if listener not in self.preModifyListeners:
            self.preModifyListeners.append(listener)

    def removePreModifyListener(self, listener):
        if listener in self.preModifyListeners:
            del self.preModifyListeners[self.preModifyListeners.index(listener)]

    def addModifyListener(self, listener):
        if listener not in self.modifyListeners:
            self.modifyListeners.append(listener)

    def removeModifyListener(self, listener):
        if listener in self.modifyListeners:
            del self.modifyListeners[self.modifyListeners.index(listener)]

    def insertStepsAfterOffset(self, offset, steps):
        event = RecipeModelEvent(self, ADD, offset, len(steps))
        self.fireRecipeModelAboutToChange(event)
        self.recipe.insertStepsAtOffset(offset, steps)
        self.recipe.setDirty(True)
        self.fireRecipeModelChanged(event)

    def getStepCount(self):
        if self.recipe is None:
            return 0
        return self.recipe.getStepsCount()
        return

    def setStopFiring(self, stopFiring):
        """Prevent table from firing"""
        self.stopFiring = stopFiring

    def getNumDevices(self):
        if self.recipe is None:
            return 0
        return len(self.recipe.getDevices())
        return

    def addDevice(self, device):
        offset = self.getNumDevices()
        event = RecipeModelEvent(self, ADD_DEVICE, device=device)
        self.fireRecipeModelAboutToChange(event)
        self.recipe.addDevice(device)
        self.recipe.setDirty()
        index = self.recipe.getDeviceIndex(device)
        if index == -1:
            raise Exception('Unable to insert step for %s in new recipe' % str(device))
        for step in self.recipe.getSteps():
            entry = device.createNewStepEntry()
            step.insertEntry(index, entry)

        self.fireRecipeModelChanged(event)

    def removeDevice(self, device):
        index = self.recipe.getDeviceIndex(device)
        if index == -1:
            raise Exception('Unable to remove entries for %s in recipe' % str(device))
        event = RecipeModelEvent(self, REMOVE_DEVICE, numCols=1, device=device)
        self.fireRecipeModelAboutToChange(event)
        self.recipe.setDirty()
        self.recipe.removeDevice(device)
        list(map((lambda step: step.removeEntry(index)), self.recipe.getSteps()))
        self.fireRecipeModelChanged(event)

    def dispose(self):
        pass

    def getDevices(self):
        if self.recipe is None:
            return []
        return self.recipe.getDevices()
        return

    def __repr__(self):
        return '[RecipeModel: Rows=%i, Devices=%i, Firing=%i]' % (self.getStepCount(), self.getNumDevices(), not self.stopFiring)
