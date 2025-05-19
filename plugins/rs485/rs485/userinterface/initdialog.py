# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/rs485/src/rs485/userinterface/initdialog.py
# Compiled at: 2004-08-10 09:09:48
import plugins.poi.poi.dialogs, wx
import plugins.poi.poi as poi


class ShutdownInitializeDialog(plugins.poi.poi.dialogs.Dialog):
    __module__ = __name__

    def __init__(self, title, msg):
        plugins.poi.poi.dialogs.Dialog.__init__(self)
        self.msg = msg
        self.title = title
        self.throbber = None
        return

    def createControl(self, parent):
        self.control = wx.Dialog(parent, -1, self.title, style=wx.CAPTION)
        messageImageGroup = self.createMessageImageGroup(self.control)
        self.buttons = self.createButtons(self.control)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(messageImageGroup, 1, wx.EXPAND | wx.ALIGN_CENTRE_VERTICAL | wx.ALL, 5)
        sizer.Add(self.buttons, 0, wx.ALIGN_CENTRE_HORIZONTAL | wx.ALL, 5)
        self.control.SetSizer(sizer)
        self.control.SetAutoLayout(True)
        sizer.Fit(self.control)
        self.control.SetSize(wx.Size(300, -1))
        poi.dialogs.Dialog.createControl(self, parent)
        return self.control

    def createMessageImageGroup(self, composite):
        panel = wx.Panel(composite, -1)
        self.messageLabel = wx.StaticText(panel, -1, self.msg)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.messageLabel, 1, wx.EXPAND | wx.ALL | wx.ALIGN_CENTRE_VERTICAL, 10)
        panel.SetSizer(sizer)
        panel.SetAutoLayout(True)
        sizer.Fit(panel)
        return panel

    def createButtons(self, composite):
        self.cancelButton = wx.Button(composite, -1, 'Cancel')
        composite.Bind(wx.EVT_BUTTON, self.OnCancelButton, self.cancelButton)
        return self.cancelButton

    def OnCancelButton(self, event):
        event.Skip()
        self.cancelButton.Enable(False)
        self.endModal(wx.ID_CANCEL)

    def showModal(self):
        self.control.CentreOnScreen()
        return self.control.ShowModal()

    def endModal(self, id):
        return self.control.EndModal(id)

    def dispose(self):
        self.control.Destroy()
        del self.control
        self.control = None
        return
