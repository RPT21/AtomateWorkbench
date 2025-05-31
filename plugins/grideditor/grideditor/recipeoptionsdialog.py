# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/grideditor/src/grideditor/recipeoptionsdialog.py
# Compiled at: 2004-12-08 05:05:12
import wx, plugins.poi.poi.dialogs
import plugins.grideditor.grideditor.messages as messages
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin
import plugins.ui.ui as ui
import plugins.poi.poi as poi
import plugins.grideditor.grideditor as grideditor
import plugins.grideditor.grideditor.adddevicedialog as grideditor_adddevicedialog

DIALOG_PREFS_FILE = 'recipeoptions.prefs'

class MixedInListCtrl(wx.ListCtrl, ListCtrlAutoWidthMixin):
    __module__ = __name__

    def __init__(self, parent, id, style):
        wx.ListCtrl.__init__(self, parent, id, style=style | wx.SUNKEN_BORDER)
        ListCtrlAutoWidthMixin.__init__(self)


class DeviceEditorDialog(poi.dialogs.MessageHeaderDialog):
    __module__ = __name__

    def __init__(self, device):
        poi.dialogs.MessageHeaderDialog.__init__(self, title='Device Editor')
        self.setStyle(wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.device = device

    def fitMe(self):
        size = self.body.GetSize()
        sizer = self.control.GetSizer()
        sizer.SetItemMinSize(self.body, size)
        mysize = self.control.GetSize()
        size = (
         size[0], size[1])
        mysize = (mysize[0], mysize[1])
        if mysize < size:
            self.control.SetSize(size)
            self.control.CentreOnScreen()

    def createButtons(self, parent):
        self.cancelButton = wx.Button(parent, wx.ID_CANCEL, 'Cancel')
        self.okButton = wx.Button(parent, wx.ID_OK, 'OK')
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.cancelButton, 0)
        sizer.Add(self.okButton, 0, wx.LEFT, 5)
        parent.Bind(wx.EVT_BUTTON, self.OnCancelButton, self.cancelButton)
        parent.Bind(wx.EVT_BUTTON, self.OnOKButton, self.okButton)
        return sizer

    def createControl(self, parent):
        poi.dialogs.MessageHeaderDialog.createControl(self, parent)
        self.control.SetSize((500, 500))
        self.control.CentreOnScreen()

    def OnCancelButton(self, event):
        self.endModal(wx.ID_CANCEL)

    def OnOKButton(self, event):
        self.endModal(wx.ID_OK)

    def OnScrollerSize(self, event):
        event.Skip()
        size = self.scroller.GetClientSize()
        self.scroller.SetScrollbars(20, 20, size[0] / 20, size[1] / 20)
        sizer = self.stage.GetSizer()
        if sizer is not None:
            sizer.Fit(self.stage)
            size = self.stage.GetSize()
            self.stage.SetSize(self.scroller.GetClientSize())
        return

    def setCanFinish(self, canit):
        self.okButton.Enable(canit)

    def createBody(self, parent):
        self.body = wx.Panel(parent, -1)
        self.editor = self.device.getDeviceEditor()
        self.editor.setOwner(self)
        self.editor.createControl(self.body)
        self.buttonSizer = self.createButtons(self.body)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.editor.getControl(), 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(wx.StaticLine(self.body, -1), 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(self.buttonSizer, 0, wx.ALIGN_RIGHT | wx.ALL, 5)
        self.body.SetSizer(sizer)
        self.body.SetAutoLayout(True)
        return self.body

    def showModal(self):
        self.editor.setData(self.device)
        return poi.dialogs.MessageHeaderDialog.showModal(self)

    def handleClosing(self, id):
        if id == wx.ID_OK:
            self.editor.getData(self.device)
            self.device.configurationUpdated()

    def endModal(self, id):
        poi.dialogs.MessageHeaderDialog.endModal(self, id)


class RecipeOptionsDialog(poi.dialogs.MessageHeaderDialog):
    __module__ = __name__

    def __init__(self, editor):
        poi.dialogs.MessageHeaderDialog.__init__(self, title=messages.get('dialog.recipeoptions.title'))
        self.control = None
        self.id2objects = {}
        self.setSaveLayout(True)
        self.editor = editor
        self.startingDevice = None
        self.setStyle(wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.NO_FULL_REPAINT_ON_RESIZE | wx.CLIP_CHILDREN)
        self.wasActivated = 0
        return

    def createControl(self, parent):
        poi.dialogs.MessageHeaderDialog.createControl(self, parent)
        self.control.Bind(wx.EVT_ACTIVATE, self.activated)

    def activated(self, event):
        event.Skip()
        if not event.GetActive():
            return
        self.wasActivated += 1
        if self.wasActivated != 1:
            return
        if self.startingDevice is None:
            return
        self.editDevice([self.startingDevice])
        return

    def setShowDevice(self, device):
        self.startingDevice = device

    def createBody(self, parent):
        self.stage = wx.Panel(parent, -1)
        self.listctrl = self.createList()
        self.actionsButtonSizer = self.createActionButtons()
        self.dialogButtonsSizer = self.createDialogButtons()
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(self.listctrl, 1, wx.EXPAND | wx.ALL, 5)
        hsizer.Add(self.actionsButtonSizer, 0, wx.ALIGN_TOP | wx.ALL, 5)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(hsizer, 1, wx.EXPAND)
        sizer.Add(wx.StaticLine(self.stage, -1), 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(self.dialogButtonsSizer, 0, wx.ALIGN_RIGHT)
        self.stage.SetSizer(sizer)
        self.stage.SetAutoLayout(True)
        self.setMessage(messages.get('recipeoptions.messages.start'))
        self.updateInfo()
        self.restoreLayout()

    def showModal(self):
        self.fillRecipeData()
        return poi.dialogs.MessageHeaderDialog.showModal(self)

    def clearEntries(self):
        self.listctrl.DeleteAllItems()

    def fillRecipeData(self):
        self.clearEntries()
        recipe = self.getRecipe()
        for device in recipe.getDevices():
            self.insertDeviceEntry(device)

    def getEditor(self):
        return grideditor.getDefault().getEditor()

    def getRecipe(self):
        recipe = ui.context.getProperty('recipe')
        return recipe

    def insertDeviceEntry(self, device):
        idx = self.listctrl.GetItemCount()
        self.listctrl.InsertStringItem(idx, device.getType())
        label = device.getLabel()
        self.listctrl.SetStringItem(idx, 1, label)
        self.listctrl.SetStringItem(idx, 2, device.getDeviceStr())
        self.listctrl.SetItemData(idx, idx)
        self.id2objects[idx] = device

    def createDialogButtons(self):
        self.okButton = wx.Button(self.stage, wx.ID_OK, 'OK')
        self.stage.Bind(wx.EVT_BUTTON, self.OnOKButton, self.okButton)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.okButton, 0, wx.ALL, 5)
        return sizer

    def OnOKButton(self, event):
        self.endModal(wx.ID_OK)

    def createActionButtons(self):
        self.addButton = wx.Button(self.stage, -1, '&Add ...')
        self.removeButton = wx.Button(self.stage, -1, '&Delete')
        self.removeButton.Enable(False)
        self.editButton = wx.Button(self.stage, -1, '&Edit ...')
        self.editButton.Enable(False)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.addButton, 0, wx.EXPAND)
        sizer.Add(self.removeButton, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 5)
        sizer.Add(self.editButton, 0, wx.EXPAND | wx.TOP, 10)
        self.stage.Bind(wx.EVT_BUTTON, self.OnEditButton, self.editButton)
        self.stage.Bind(wx.EVT_BUTTON, self.OnRemoveButton, self.removeButton)
        self.stage.Bind(wx.EVT_BUTTON, self.OnAddButton, self.addButton)
        return sizer

    def OnRemoveButton(self, event):
        selection = self.getItemSelected()
        if len(selection) == 0:
            return
        device = selection[0]
        self.getEditor().removeDevice(device)
        self.fillRecipeData()
        self.updateInfo()

    def updateInfo(self):
        if len(self.getRecipe().getDevices()) == 0:
            self.setInfo(messages.get('recipeoptions.messages.empty'))
            return
        if len(self.getItemSelected()) == 0:
            self.setInfo(messages.get('recipeoptions.messages.info'))
            return
        self.setInfo(messages.get('recipeoptions.messages.selected'))

    def OnAddButton(self, event):
        dlg = grideditor_adddevicedialog.AddDeviceDialog()
        dlg.createControl(self.control)
        if dlg.showModal() == wx.ID_OK:
            factory = dlg.getDeviceFactory()
            editor = self.getEditor()
            editor.addDevice(factory.getInstance())
            self.fillRecipeData()
        dlg.dispose()
        del dlg
        self.updateInfo()

    def createList(self):
        listctrl = MixedInListCtrl(self.stage, -1, style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_VRULES)
        info = wx.ListItem()
        info.SetColumn(0)
        info.SetAlign(wx.LIST_FORMAT_LEFT)
        info.SetText('Type')
        listctrl.InsertColumnInfo(0, info)
        listctrl.SetColumnWidth(0, 80)
        info = wx.ListItem()
        info.SetColumn(1)
        info.SetAlign(wx.LIST_FORMAT_LEFT)
        info.SetText('Label')
        listctrl.InsertColumnInfo(1, info)
        info = wx.ListItem()
        info.SetColumn(2)
        info.SetAlign(wx.LIST_FORMAT_LEFT)
        info.SetText('Hardware')
        listctrl.InsertColumnInfo(2, info)
        self.stage.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected, listctrl)
        self.stage.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected, listctrl)
        self.stage.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemDoubleClick, listctrl)
        return listctrl

    def OnItemDeselected(self, event):
        self.editButton.Enable(False)
        self.removeButton.Enable(False)
        self.setInfo(messages.get('recipeoptions.messages.info'))

    def OnItemSelected(self, event):
        self.editButton.Enable(True)
        self.removeButton.Enable(True)
        self.setInfo(messages.get('recipeoptions.messages.selected'))

    def OnEditButton(self, event):
        self.OnEditSelectedDevice()

    def OnItemDoubleClick(self, event):
        event.Skip()
        self.OnEditSelectedDevice()

    def OnEditSelectedDevice(self):
        self.editDevice(self.getItemSelected())

    def editDevice(self, selection):
        """Passes the selection, which is a device, to the editor dialog"""
        dlg = DeviceEditorDialog(selection[0])
        dlg.createControl(self.control)
        if dlg.showModal() == wx.ID_OK:
            recipeModel = self.editor.getRecipeModel()
            recipeModel.tagDeviceModified(selection[0])
        dlg.dispose()
        self.fillRecipeData()

    def getItemSelected(self):
        selection = []
        itemIndex = -1
        while True:
            itemIndex = self.listctrl.GetNextItem(itemIndex, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
            if itemIndex == -1:
                break
            item = self.listctrl.GetItem(itemIndex)
            selection.append(self.id2objects[item.GetData()])

        return selection

    def getMementoID(self):
        global DIALOG_PREFS_FILE
        return DIALOG_PREFS_FILE

    def fillLayoutMemento(self, memento):
        size = self.control.GetSize()
        memento.set('layout', 'size', '%s,%s' % (size[0], size[1]))

    def createDefaultLayout(self):
        self.control.SetSize((500, 600))
        self.control.CentreOnScreen()

    def restoreLayoutFromMemento(self, memento):
        size = list(map(int, tuple(memento.get('layout', 'size').split(','))))
        self.control.SetSize(size)
        self.control.CentreOnScreen()
