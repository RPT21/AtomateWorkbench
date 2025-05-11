# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/executionengine/src/executionengine/userinterface/engineiniterrordialog.py
# Compiled at: 2004-10-28 21:04:39
import wx, plugins.ui.ui, wx.lib.mixins.listctrl as listmix, plugins.executionengine.executionengine.messages as messages, plugins.core.core.error

class AutoSizingListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
    __module__ = __name__

    def __init__(self, parent, ID, pos=wx.DefaultPosition, size=wx.DefaultSize, style=0):
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
        listmix.ListCtrlAutoWidthMixin.__init__(self)


class EngineInitErrorDialog(wx.Dialog):
    __module__ = __name__

    def __init__(self, errors):
        parent = ui.getDefault().getMainFrame().getControl()
        style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        wx.Dialog.__init__(self, parent, -1, size=wx.Size(350, 450), style=style)
        self.SetTitle(messages.get('engine.init.error.title'))
        self.list = AutoSizingListCtrl(self, -1, style=wx.LC_REPORT | wx.LC_NO_HEADER)
        self.list.InsertColumn(0, 'Error')
        self.message = wx.TextCtrl(self, -1, style=wx.TE_MULTILINE)
        self.closeButton = wx.Button(self, -1, '&Close')
        self.closeButton.SetDefault()
        vsizer = wx.BoxSizer(wx.VERTICAL)
        vsizer.Add(self.list, 1, wx.GROW | wx.ALL, 5)
        vsizer.Add(self.message, 1, wx.GROW | wx.ALL, 5)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(self.closeButton, 0, wx.ALIGN_RIGHT)
        vsizer.Add(hsizer, 0, wx.ALIGN_RIGHT | wx.ALL, 5)
        self.SetSizer(vsizer)
        self.Bind(wx.EVT_BUTTON, self.OnClose, self.closeButton)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnSelected, self.list)
        self.CentreOnScreen()
        self.errors = []
        self.populateErrors(errors)

    def OnClose(self, event):
        self.EndModal(wx.ID_OK)

    def OnSelected(self, event):
        idx = self.getItemSelected()
        if idx == -1:
            self.message.SetValue('')
            return
        error = self.errors[idx]
        msg = str(error)
        if isinstance(error, core.error.WorkbenchException):
            msg = '%s\n%s' % (error.getMessage(), error.getDescription())
        self.message.SetValue(msg)

    def getItemSelected(self):
        itemIndex = -1
        while True:
            itemIndex = self.list.GetNextItem(itemIndex, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
            if itemIndex == -1:
                break
            return itemIndex

        return -1

    def populateErrors(self, errors):
        i = 0
        for error in errors:
            msg = str(error)
            level = core.error.LEVEL_ERROR
            ne = (
             str(error), str(error))
            if isinstance(error, core.error.WorkbenchException):
                ne = error
                msg = error.getMessage()
                level = error.getMessage()
            self.errors.append(ne)
            self.list.InsertStringItem(i, msg)
            i += 1

        self.list.Refresh()
