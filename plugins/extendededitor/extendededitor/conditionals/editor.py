# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/extendededitor/src/extendededitor/conditionals/editor.py
# Compiled at: 2004-12-08 05:11:50
import wx, ui, copy, core.conditional, extendededitor.messages as messages, extendededitor.conditionals.testeditor, poi.utils.listctrl

class ConditionalEditor(object):
    __module__ = __name__

    def __init__(self):
        self.control = None
        self.recipe = None
        self.step = None
        return

    def setStep(self, step):
        self.step = step

    def setRecipe(self, recipe):
        self.recipe = recipe

    def createControl(self, parent):
        self.control = wx.Dialog(parent, -1, messages.get('dialog.conditionals.title'), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.testsList = self.createTestsList(self.control)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(self.testsList, 1, wx.GROW | wx.RIGHT, 10)
        self.editButton = wx.Button(self.control, -1, messages.get('dialog.conditionals.edit.label'))
        self.editButton.Disable()
        self.addButton = wx.Button(self.control, -1, messages.get('dialog.conditionals.add.label'))
        self.deleteButton = wx.Button(self.control, -1, messages.get('dialog.conditionals.delete.label'))
        self.deleteButton.Disable()
        self.moveUpButton = wx.Button(self.control, -1, messages.get('dialog.conditionals.moveup.label'))
        self.moveUpButton.Disable()
        self.moveDownButton = wx.Button(self.control, -1, messages.get('dialog.conditionals.movedown.label'))
        self.moveDownButton.Disable()
        rbsizer = wx.BoxSizer(wx.VERTICAL)
        rbsizer.Add(self.addButton, 0, wx.GROW)
        rbsizer.Add(self.editButton, 0, wx.GROW)
        rbsizer.Add(self.deleteButton, 0, wx.GROW | wx.TOP, 5)
        rbsizer.Add(self.moveUpButton, 0, wx.GROW | wx.TOP, 30)
        rbsizer.Add(self.moveDownButton, 0, wx.GROW | wx.BOTTOM, 10)
        hsizer.Add(rbsizer, 0, wx.GROW | wx.ALIGN_RIGHT)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(hsizer, 1, wx.GROW | wx.LEFT | wx.TOP | wx.BOTTOM, 5)
        sizer.Add(wx.StaticLine(self.control, -1), 0, wx.GROW)
        self.okButton = wx.Button(self.control, wx.ID_OK, 'OK')
        self.cancelButton = wx.Button(self.control, wx.ID_CANCEL, 'Cancel')
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(self.okButton, 0, wx.ALIGN_CENTRE_VERTICAL)
        hsizer.Add(self.cancelButton, 0, wx.ALIGN_CENTRE_VERTICAL)
        sizer.Add(hsizer, 0, wx.ALIGN_RIGHT | wx.TOP | wx.BOTTOM | wx.RIGHT, 10)
        self.control.SetSizer(sizer)
        self.control.SetAutoLayout(True)
        self.control.SetSize((400, 500))
        self.control.CentreOnScreen()
        self.addButton.Bind(wx.EVT_BUTTON, self.OnAddButton)
        self.editButton.Bind(wx.EVT_BUTTON, self.OnEdit)
        self.deleteButton.Bind(wx.EVT_BUTTON, self.OnDelete)
        self.moveUpButton.Bind(wx.EVT_BUTTON, self.OnMoveUp)
        self.moveDownButton.Bind(wx.EVT_BUTTON, self.OnMoveDown)
        self.testsList.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnTestSelected)
        self.testsList.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnEdit)

    def OnMoveUp(self, event):
        selection = self.getSelection()
        conditionals = self.step.getConditionals()
        curridx = conditionals.index(selection)
        newidx = curridx - 1
        conditionals.remove(selection)
        conditionals.insert(newidx, selection)
        self.populateTestsList()
        wx.CallAfter(self.setSelected, newidx)

    def setSelected(self, index):
        self.testsList.SetItemState(index, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)
        self.testsList.Layout()

    def OnMoveDown(self, event):
        selection = self.getSelection()
        conditionals = self.step.getConditionals()
        curridx = conditionals.index(selection)
        newidx = curridx + 1
        conditionals.remove(selection)
        conditionals.insert(newidx, selection)
        self.populateTestsList()
        wx.CallAfter(self.setSelected, newidx)

    def OnDelete(self, event):
        selection = self.getSelection()
        index = self.step.getConditionals().index(selection)
        self.step.getConditionals().remove(selection)
        self.populateTestsList()
        if index > 0:
            index -= 1
        if len(self.step.getConditionals()) > 0:
            wx.CallAfter(self.setSelected, index)

    def getSelection(self):
        itemIndex = -1
        conditionals = self.step.getConditionals()
        while True:
            itemIndex = self.testsList.GetNextItem(itemIndex, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
            if itemIndex == -1:
                break
            return conditionals[itemIndex]

        self.setSelection(selection)

    def OnTestSelected(self, event):
        event.Skip()
        conditionals = self.step.getConditionals()
        selection = self.getSelection()
        self.editButton.Enable()
        self.deleteButton.Enable()
        self.moveDownButton.Enable(conditionals.index(selection) < len(conditionals) - 1)
        self.moveUpButton.Enable(conditionals.index(selection) > 0)

    def OnEdit(self, event):
        dlg = extendededitor.conditionals.testeditor.TestEditor()
        dlg.setRecipe(self.recipe)
        dlg.createControl(ui.getDefault().getMainFrame().getControl())
        selection = self.getSelection()
        dlg.setConditionalTests(selection)
        if dlg.showModal() == wx.ID_OK:
            tests = dlg.getConditionalTests()
            selection.clear()
            selection.setTests(copy.copy(tests))
            selection.clearActions()
            selection.setActions(copy.copy(dlg.getActions()))
            selection.setUseConnectiveAnd(dlg.isConnectiveAnd())
            selection.setName(dlg.getTestName())
            self.populateTestsList()
        dlg.dispose()

    def OnAddButton(self, event):
        dlg = extendededitor.conditionals.testeditor.TestEditor()
        dlg.setRecipe(self.recipe)
        dlg.createControl(ui.getDefault().getMainFrame().getControl())
        if dlg.showModal() == wx.ID_OK:
            tests = dlg.getConditionalTests()
            suite = core.conditional.ConditionalTests()
            suite.setTests(copy.copy(tests))
            suite.setName(dlg.getTestName())
            suite.setActions(copy.copy(dlg.getActions()))
            suite.setUseConnectiveAnd(dlg.isConnectiveAnd())
            self.step.addConditional(suite)
            self.populateTestsList()
            index = len(self.step.getConditionals()) - 1
            self.setSelected(index)
        dlg.dispose()

    def populateTestsList(self):
        self.clearTestsList()
        for conditional in self.step.getConditionals():
            self.appendConditional(conditional)

    def appendConditional(self, conditional):
        item = self.createListItem(conditional)
        idx = self.testsList.GetItemCount()
        item.SetId(idx)
        self.testsList.InsertItem(item)

    def createListItem(self, conditional):
        item = wx.ListItem()
        item.SetText(conditional.getName())
        return item

    def clearTestsList(self):
        self.testsList.DeleteAllItems()

    def createTestsList(self, parent):
        lst = poi.utils.listctrl.ListCtrl(parent, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER, size=wx.Size(100, 100))
        lst.InsertColumn(0, 'Test Name', width=200)
        return lst

    def getControl(self):
        return self.control

    def showModal(self):
        self.populateTestsList()
        result = self.control.ShowModal()
        return result

    def dispose(self):
        self.control.Destroy()
        del self.control
