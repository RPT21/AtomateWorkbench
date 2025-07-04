# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/grideditor/src/grideditor/actions.py
# Compiled at: 2004-12-01 23:27:38
import logging, plugins.poi.poi.actions, plugins.poi.poi.views, plugins.resources.resources, plugins.core.core.recipe
import wx, plugins.ui.ui.clipboard, plugins.ui.ui.undomanager, plugins.grideditor.grideditor
import plugins.grideditor.grideditor.utils, plugins.grideditor.grideditor.images as images
import plugins.hardware.hardware.hardwaremanager
import plugins.ui.ui as ui
import plugins.poi.poi as poi
import plugins.core.core as core
import plugins.grideditor.grideditor as grideditor


logger = logging.getLogger('grideditor')
import plugins.grideditor.grideditor.recipeoptionsdialog
recipeOptionsAction = None
saveRecipeAction = None
visibilityStateActions = []

class UndoableRemoveStepsAction(ui.undomanager.UndoableAction):
    __module__ = __name__

    def __init__(self, description, undodesc, offset, steps, editor):
        ui.undomanager.UndoableAction.__init__(self, description, undodesc)
        self.offset = offset
        self.steps = steps
        self.editor = editor

    def undo(self):
        self.editor.insertStepsAfterIndex(self.offset, self.steps)

    def redo(self):
        self.editor.removeSteps(self.offset, len(self.steps))

    def __repr__(self):
        return '%s: offset=%d/len=%d' % (self.getDescription(), self.offset, len(self.steps))


class UndoableDeleteStepsAction(UndoableRemoveStepsAction):
    __module__ = __name__

    def __init__(self, offset, steps, editor):
        UndoableRemoveStepsAction.__init__(self, 'Undo Delete Steps', 'Redo Delete Steps', offset, steps, editor)


class UndoableCutStepsAction(UndoableRemoveStepsAction):
    __module__ = __name__

    def __init__(self, offset, steps, editor):
        UndoableRemoveStepsAction.__init__(self, 'Undo Cut Steps', 'Redo Cut Steps', offset, steps, editor)


class UndoablePasteStepAction(ui.undomanager.UndoableAction):
    __module__ = __name__

    def __init__(self, offset, steps, editor):
        """
        steps are cloned!
        """
        ui.undomanager.UndoableAction.__init__(self, 'Undo Paste Step', 'Redo Paste Step')
        self.steps = steps
        self.offset = offset
        self.editor = editor

    def undo(self):
        self.editor.removeSteps(self.offset, len(self.steps))

    def redo(self):
        self.editor.insertStepsAfterIndex(self.offset, self.steps)

    def __repr__(self):
        return "Undo/Redo Paste: offset='%d',len='%d'" % (self.offset, len(self.steps))


class UndoableInsertStepAction(ui.undomanager.UndoableAction):
    __module__ = __name__

    def __init__(self, offset, editor):
        """
        Step is completele created. NOT CLONED!!!!
        """
        ui.undomanager.UndoableAction.__init__(self, 'Undo Insert Step', 'Redo Insert Step')
        self.offset = offset
        self.editor = editor

    def undo(self):
        self.editor.removeSteps(self.offset, 1)

    def redo(self):
        self.editor.createNewStepAtIndex(self.offset)

    def __repr__(self):
        return "Undo/Redo Insert: offset='%d'" % self.offset


def convertStepsToTabbed(selection):
    buff = ''
    linesep = ''
    for step in selection:
        valsep = ''
        buff += linesep + str(step.getDuration())
        for entry in step.getEntries():
            buff += valsep + entry.getValueForCut()
            valsep = '\t'

        linesep = '\n'

    return buff


class SelectionDispatchAction(poi.actions.Action):
    __module__ = __name__

    def __init__(self, name, image=None):
        poi.actions.Action.__init__(self, name, image)
        self.selection = []

    def handleSelectionChanged(self, event):
        self.selection = event
        self.selectionChanged(self.selection)

    def selectionChanged(self, selection):
        pass

    def run(self):
        self.runWithSelection(self.selection)

    def runWithSelection(self, selection):
        pass


def handleActionContextChange(newValue, oldValue):
    global logger
    logger.debug("Context Changed '%s'" % newValue)
    if newValue is None:
        removeActions()
        return
    if oldValue is None:
        addActions()
    return


def removeActions():
    global saveRecipeAction
    global visibilityStateActions
    tbm = ui.getDefault().getToolBarManager()
    visibilityStateActions = []
    menumanager = ui.getDefault().getMenuManager()
    editManager = menumanager.findByPath('atm.edit')
    tbm.remove(tbm.findByPath('recipe-options'))
    runManager = menumanager.findByPath('atm.run')
    runManager.remove(menumanager.findByPath('atm.run/recipe-options'))
    editManager.remove(menumanager.findByPath('atm.edit/recipe-edit-sep1'))
    editManager.remove(menumanager.findByPath('atm.edit/recipe-edit-sep2'))
    editManager.remove(menumanager.findByPath('atm.edit/recipe-insert-step'))
    editManager.remove(menumanager.findByPath('atm.edit/recipe-delete-step'))
    poi.actions.removeGlobalActionHandler('global.edit.cut')
    poi.actions.removeGlobalActionHandler('global.edit.copy')
    poi.actions.removeGlobalActionHandler('global.edit.paste')
    fileManager = menumanager.findByPath('atm.file')
    fileManager.remove(menumanager.findByPath('atm.file/recipe-save'))
    fileManager.update()
    tbm.update(True)
    editManager.update()
    if saveRecipeAction is not None:
        saveRecipeAction.dispose()
    return


def addActions():
    global recipeOptionsAction
    global saveRecipeAction
    editor = grideditor.getDefault().getEditor()
    tbm = ui.getDefault().getToolBarManager()
    editManager = ui.getDefault().getMenuManager().findByPath('atm.edit')
    runManager = ui.getDefault().getMenuManager().findByPath('atm.run')
    saveRecipeAction = SaveRecipeAction()
    recipeOptionsAction = RecipeOptionsAction()
    deleteStepAction = DeleteStepAction(editor)
    cutStepAction = CutStepAction(editor)
    copyStepAction = CopyStepAction(editor)
    insertStepAction = InsertStepAction(editor)
    pasteStepAction = PasteStepAction(editor)
    visibilityStateActions.append(deleteStepAction)
    visibilityStateActions.append(cutStepAction)
    visibilityStateActions.append(copyStepAction)
    visibilityStateActions.append(insertStepAction)
    tbm.appendToGroup('edit-actions-begin', poi.actions.ActionContributionItem(recipeOptionsAction, 'recipe-options'))
    runManager.appendToGroup('run-additions-begin', poi.actions.ActionContributionItem(recipeOptionsAction, 'recipe-options'))
    editManager.appendToGroup('edit-additions-begin', poi.actions.Separator('recipe-edit-sep1'))
    editManager.appendToGroup('edit-additions-begin', poi.actions.ActionContributionItem(deleteStepAction, 'recipe-delete-step'))
    editManager.appendToGroup('edit-additions-begin', poi.actions.ActionContributionItem(insertStepAction, 'recipe-insert-step'))
    editManager.appendToGroup('edit-additions-begin', poi.actions.Separator('recipe-edit-sep2'))
    poi.actions.setGlobalActionHandler('global.edit.cut', cutStepAction)
    poi.actions.setGlobalActionHandler('global.edit.copy', copyStepAction)
    poi.actions.setGlobalActionHandler('global.edit.paste', pasteStepAction)
    editManager.update()
    fileManager = ui.getDefault().getMenuManager().findByPath('atm.file')
    fileManager.insertAfter('close-group-end', poi.actions.ActionContributionItem(saveRecipeAction, 'recipe-save'))
    fileManager.update()
    tbm.update(True)


class CreateDefaultDevicesAction(poi.actions.Action):
    __module__ = __name__

    def __init__(self):
        poi.actions.Action.__init__(self, 'Create Default Devices', '', '')

    def run(self):
        lst = plugins.hardware.hardware.hardwaremanager.createDevicesForConfiguredHardware()
        editor = grideditor.getDefault().getEditor()
        for device in lst:
            editor.addDevice(device)


class ToggleEditorViewAction(poi.actions.Action):
    __module__ = __name__

    def __init__(self):
        poi.actions.Action.__init__(self, 'DEBUG-TOGGLE EDITOR VIEW\tt', '', '')
        self.showing = True

    def run(self):
        grideditor.getDefault().getView().showGridEditorView(not self.showing)
        self.showing = not self.showing


class DebugDumpRecipe(poi.actions.Action):
    __module__ = __name__

    def __init__(self):
        poi.actions.Action.__init__(self, 'DEBUG-DUMP RECIPE CONSOLE\td', '', '')

    def run(self):
        editor = grideditor.getActiveEditor().getEditor()
        recipe = editor.getInput().getRecipe()


class RecipeOptionsAction(poi.actions.Action):
    __module__ = __name__

    def __init__(self):
        poi.actions.Action.__init__(self, 'Recipe Options ...', '', '')
        self.setImage(images.getImage(images.RECIPE_OPTIONS))

    def run(self):
        grideditor.utils.showRecipeOptions(None)
        return


class CutStepAction(SelectionDispatchAction):
    __module__ = __name__

    def __init__(self, editor):
        SelectionDispatchAction.__init__(self, 'Cut')
        editor.addSelectionChangedListener(self)
        editor.addInputChangedListener(self)
        self.editor = editor
        self.setEnabled(False)
        self.inputChanged(None, editor.getInput())
        return

    def inputChanged(self, oldInput, newInput):
        if oldInput is not None:
            oldInput.removeModifyListener(self)
        if newInput is not None:
            newInput.addModifyListener(self)
        return

    def recipeModelChanged(self, event):
        pass

    def selectionChanged(self, selection):
        self.setEnabled(len(selection) > 0)

    def runWithSelection(self, selection):
        ui.clipboard.createObject()
        ui.clipboard.setObject(selection)
        ui.clipboard.setText(convertStepsToTabbed(selection))
        if not ui.clipboard.commit():
            return
        offset = self.editor.getIndexOfSelection()
        self.editor.deleteSelectedSteps()
        undoaction = UndoableCutStepsAction(offset, selection, self.editor)
        ui.undomanager.addUndoableAction(undoaction)


class CopyStepAction(SelectionDispatchAction):
    __module__ = __name__

    def __init__(self, editor):
        SelectionDispatchAction.__init__(self, 'Copy')
        editor.addSelectionChangedListener(self)
        editor.addInputChangedListener(self)
        self.setEnabled(False)

    def inputChanged(self, oldInput, newInput):
        pass

    def selectionChanged(self, selection):
        self.setEnabled(len(selection) > 0)

    def runWithSelection(self, selection):
        ui.clipboard.createObject()
        ui.clipboard.setObject(selection)
        ui.clipboard.setText(convertStepsToTabbed(selection))
        if not ui.clipboard.commit():
            pass


class PasteStepAction(poi.actions.Action):
    __module__ = __name__

    def __init__(self, editor):
        poi.actions.Action.__init__(self, 'Paste', '', '')
        self.editor = editor

    def isDataSteps(self, data):
        if not isinstance(data, list):
            return False
        for item in data:
            if not isinstance(item, core.recipestep.RecipeStep):
                return False

        return True

    def isEnabled(self):
        """    
        if not ui.clipboard.hasPyObject():
            if not ui.clipboard.hasText():
                return False
            # it does have text
            return True
        
        return self.isDataSteps(ui.clipboard.getObject())
        """
        return grideditor.getDefault().getView().getViewer().isShowing()

    def run(self):
        if ui.clipboard.hasPyObject():
            steps = ui.clipboard.getObject()
            if not self.isDataSteps(steps):
                return
            offset = self.editor.insertStepsAfterSelection(steps)
            undoaction = UndoablePasteStepAction(offset, steps, self.editor)
            ui.undomanager.addUndoableAction(undoaction)
        elif ui.clipboard.hasText():
            text = ui.clipboard.getText()


class InsertStepAction(poi.actions.Action):
    __module__ = __name__

    def __init__(self, editor):
        poi.actions.Action.__init__(self, 'Insert Step\tCtrl+I', 'Insert a step after the selection', 'Insert ')
        self.editor = editor

    def run(self):
        offset = self.editor.createNewStepAfterSelection()
        undoaction = UndoableInsertStepAction(offset, self.editor)
        ui.undomanager.addUndoableAction(undoaction)


class DeleteStepAction(SelectionDispatchAction):
    __module__ = __name__

    def __init__(self, editor):
        SelectionDispatchAction.__init__(self, 'Delete Step\tDel')
        editor.addSelectionChangedListener(self)
        editor.addInputChangedListener(self)
        self.editor = editor
        self.setEnabled(False)

    def inputChanged(self, oldInput, newInput):
        pass

    def selectionChanged(self, selection):
        if len(selection) > 1:
            self.setText('Delete Steps')
        if len(selection) == 1:
            self.setText('Delete Step')
        self.setEnabled(len(selection) > 0)

    def runWithSelection(self, selection):
        offset = self.editor.getIndexOfSelection()
        self.editor.deleteSelectedSteps()
        undoaction = UndoableDeleteStepsAction(offset, selection, self.editor)
        ui.undomanager.addUndoableAction(undoaction)


class ActionButtonEventHandler(wx.EvtHandler):
    __module__ = __name__

    def __init__(self, button, caller):
        wx.EvtHandler.__init__(self)
        self.caller = caller
        self.button = button
        wx.EVT_BUTTON(self, button.GetId(), self.OnButton)

    def OnButton(self, event):
        self.caller.onButtonClicked(self.button)


class ActionButton(object):
    __module__ = __name__

    def __init__(self, action, parent=None):
        self.action = action
        self.button = None
        if parent is not None:
            self.createControl(parent)
        return

    def createControl(self, parent):
        self.button = wx.Button(parent, -1, self.action.getText())
        self.button.PushEventHandler(ActionButtonEventHandler(self.button, self))
        self.update()

    def update(self):
        if self.button is not None:
            self.button.Enable(self.action.isEnabled())
        return

    def onButtonClicked(self, button):
        if self.action.isEnabled():
            self.action.run()

    def getControl(self):
        return self.button


class SaveRecipeAction(poi.actions.Action):
    __module__ = __name__

    def __init__(self):
        poi.actions.Action.__init__(self, 'Save\tCtrl+S', '', '')
        ui.context.addContextChangeListener(self)
        self.setEnabled(False)

    def contextChanged(self, event):
        key = event.getKey()
        value = event.getNewValue()
        if key != 'recipe':
            return
        self.setEnabled(value != None)
        return

    def run(self):
        grideditor.utils.saveCurrentRecipe()

    def dispose(self):
        ui.context.removeContextChangeListener(self)


class BundkDebugOpenRecipe(poi.actions.Action):
    __module__ = __name__

    def __init__(self):
        poi.actions.Action.__init__(self, 'Debug - Open Recipe ...', '', '')
        ui.context.addContextChangeListener(self)

    def contextChanged(self, event):
        key = event.getKey()
        if key == 'can-edit':
            self.setEnabled(event.getNewValue())

    def run(self):
        """Open a file dialog and finds a recipe to execute, prepares all user interfaces for debug session"""
        item = ui.context.getProperty('recipe')
        if item is None:
            dlg = wx.FileDialog(ui.getDefault().getMainFrame().getControl(), 'Select a recipe file', plugins.resources.resources.getDefault().getWorkspace().getSharedLocation(), wildcard='Recipe Files (*.recipe)|*.recipe', style=wx.OPEN)
            dlg.CentreOnScreen()
            loaded = False
            if dlg.ShowModal() == wx.ID_OK:
                path = dlg.GetPath()
                loaded = True
            dlg.Destroy()
            del dlg
            if loaded:
                try:
                    recipe = core.recipe.loadFromFile(path)
                except Exception as msg:
                    print(('* ERROR: Unable to parse recipe:', msg))
                    return
                else:
                    ui.context.setProperty('recipe', recipe)
                    ui.context.setProperty('recipe-path', path)
        else:
            ui.context.setProperty('recipe', None)
        return


def updateActions():
    """Update the enabled state of the actions based on the visibility of the
        Grid Editor"""
    logger.debug('UPDATE ACTIONS')
    for action in visibilityStateActions:
        logger.debug('\t %s - %s' % (action, grideditor.getDefault().getView().getViewer().isShowing()))
        action.setEnabled(grideditor.getDefault().getView().getViewer().isShowing())
