# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/executionengine/src/executionengine/userinterface/hwiniterrorsdialog.py
# Compiled at: 2004-08-13 09:33:12
import wx, ui, poi.actions, poi.views, executionengine, executionengine.engine, wx.lib.mixins.listctrl as listmix, wx.lib.buttons as buttons

class RecipeInitializationDialog(poi.dialogs.Dialog):
    __module__ = __name__

    def __init__(self):
        poi.dialogs.Dialog.__init__(self)
        self.control = None
        return

    def createControl(self, parent):
        self.control = wx.Dialog(parent, -1, 'Hardware Initialization Errors')
        self.okButton = wx.Button(self.control, -1, 'OK')
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.okButton, 0, wx.ALIGN_CENTRE_HORIZONTAL)
        self.control.SetSizer(sizer)
        self.control.SetAutoLayout(True)
        self.control.SetSize((400, 200))
        self.control.CentreOnScreen()
        poi.dialogs.Dialog.createControl(self, parent)
        self.control.Bind(wx.EVT_BUTTON, self.OnOKPressed, self.okButton)

    def OnOKPressed(self, event):
        self.endModal(wx.ID_OK)
