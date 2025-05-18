# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/grideditor/src/grideditor/adddevicedialog.py
# Compiled at: 2004-12-08 05:09:27
import wx
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin
import plugins.grideditor.grideditor.messages as messages
import plugins.core.core as core
import plugins.poi.poi as poi
import plugins.poi.poi.dialogs
import plugins.core.core.deviceregistry

class MixedInListCtrl(wx.ListCtrl, ListCtrlAutoWidthMixin):
    __module__ = __name__

    def __init__(self, parent, id, style):
        wx.ListCtrl.__init__(self, parent, id, style=style)
        ListCtrlAutoWidthMixin.__init__(self)


class AddDeviceDialog(poi.dialogs.MessageHeaderDialog):
    __module__ = __name__

    def __init__(self):
        poi.dialogs.MessageHeaderDialog.__init__(self, title=messages.get('dialog.adddevice.title'))
        self.setStyle(wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.NO_FULL_REPAINT_ON_RESIZE | wx.CLIP_CHILDREN)
        self.id2objects = {}
        self.imageList = wx.ImageList(16, 16)

    def createBody(self, parent):
        self.body = wx.Panel(parent, -1)
        buttonsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.okButton = wx.Button(self.body, -1, 'OK')
        self.okButton.Disable()
        self.cancelButton = wx.Button(self.body, -1, 'Cancel')
        buttonsizer.Add(self.cancelButton, 0, wx.RIGHT | wx.ALIGN_CENTRE_VERTICAL, 5)
        buttonsizer.Add(self.okButton, 0, wx.ALIGN_CENTRE_VERTICAL)
        self.listctrl = self.createList()
        mainsizer = wx.BoxSizer(wx.VERTICAL)
        mainsizer.Add(self.listctrl, 1, wx.EXPAND | wx.ALL, 5)
        mainsizer.Add(wx.StaticLine(self.body, -1), 0, wx.EXPAND)
        mainsizer.Add(buttonsizer, 0, wx.ALIGN_RIGHT | wx.TOP | wx.BOTTOM | wx.RIGHT, 10)
        self.body.SetSizer(mainsizer)
        self.body.SetAutoLayout(True)
        self.body.Bind(wx.EVT_BUTTON, self.OnOKButton, self.okButton)
        self.body.Bind(wx.EVT_BUTTON, self.OnCancelButton, self.cancelButton)
        self.control.SetSize((400, 450))
        self.control.CentreOnScreen()
        self.populateDevices()
        self.setMessage('Add Device')
        self.updateInfo()
        return self.body

    def updateInfo(self):
        if len(self.getItemSelected()) > 0:
            self.setInfo('Click OK to add the device to the recipe')
        else:
            self.setInfo('Select the device you want to add')

    def populateDevices(self):
        deviceFactories = core.deviceregistry.getDeviceFactories()
        for factory in deviceFactories:
            self.addEntry(factory)

    def addEntry(self, factory):
        idx = self.listctrl.GetItemCount()
        label = factory.getTypeString()
        description = factory.getDescription()
        image = factory.getSmallImage()
        if image is None:
            self.listctrl.InsertStringItem(idx, label)
        else:
            imgidx = self.imageList.Add(image)
            self.listctrl.InsertImageStringItem(idx, label, imgidx)
        self.listctrl.SetStringItem(idx, 1, description)
        self.listctrl.SetItemData(idx, idx)
        self.id2objects[idx] = factory
        return

    def createList(self):
        listctrl = MixedInListCtrl(self.body, -1, style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.SUNKEN_BORDER)
        listctrl.SetImageList(self.imageList, wx.IMAGE_LIST_SMALL)
        info = wx.ListItem()
        info.m_mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
        info.m_format = 0
        info.m_image = -1
        info.m_text = 'Type'
        listctrl.InsertColumnInfo(0, info)
        listctrl.SetColumnWidth(0, 80)
        info.m_format = wx.LIST_FORMAT_LEFT
        info.m_text = 'Description'
        listctrl.InsertColumnInfo(1, info)
        self.body.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected, listctrl)
        self.body.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected, listctrl)
        self.body.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemDoubleClick, listctrl)
        return listctrl

    def OnItemSelected(self, event):
        event.Skip()
        self.okButton.Enable()
        self.updateInfo()

    def OnItemDeselected(self, event):
        event.Skip()
        self.okButton.Disable()
        self.updateInfo()

    def OnItemDoubleClick(self, event):
        event.Skip()
        self.onDeviceSelected(self.getItemSelected()[0])

    def onDeviceSelected(self, deviceFactory):
        self.factory = deviceFactory
        self.endModal(wx.ID_OK)

    def getDeviceFactory(self):
        return self.factory

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

    def OnOKButton(self, event):
        event.Skip()
        self.onDeviceSelected(self.getItemSelected()[0])

    def OnCancelButton(self, event):
        event.Skip()
        self.endModal(wx.ID_CANCEL)

    def xshowModal(self):
        return poi.dialogs.MessageHeaderDialog.showModal(self)

    def handleClosing(self, id):
        pass

    def xendModal(self, id):
        poi.dialogs.MessageHeaderDialog.endModal(self, id)
