# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: /home/maldoror/apps/eclipse/workspace/com.atomate.workbench/plugins/up150/src/up150/extendededitoritem.py
# Compiled at: 2004-08-12 02:18:21
import wx, extendededitor.item, grideditor.recipemodel, up150.messages as messages, ui.widgets.contentassist

class UP150ExtendedEditorItem(extendededitor.item.ExtendedEditorItem):
    __module__ = __name__

    def __init__(self):
        extendededitor.item.ExtendedEditorItem.__init__(self)
        self.device = None
        self.model = None
        return

    def createBody(self, parent):
        self.body = wx.Panel(parent, -1)
        self.body.SetBackgroundColour(parent.GetBackgroundColour())
        self.contentassist = ui.widgets.contentassist.ContentAssistant(self.body)
        label = wx.StaticText(self.body, -1, messages.get('exted.setpoint.label'))
        self.setpoint = wx.TextCtrl(self.body, -1)
        self.gcfLabel = wx.StaticText(self.body, -1, ' x 00.00')
        self.actualFlow = wx.TextCtrl(self.body, -1)
        self.unitsLabel = wx.StaticText(self.body, -1, '[units]')
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.contentassist.getControl(), 0, wx.ALL | wx.ALIGN_CENTRE_VERTICAL, 0)
        sizer.Add(label, 0, wx.ALIGN_CENTRE_VERTICAL | wx.RIGHT, 5)
        sizer.Add(self.setpoint, 0, wx.ALL | wx.ALIGN_CENTRE_VERTICAL, 0)
        sizer.Add(self.gcfLabel, 0, wx.ALIGN_CENTRE_VERTICAL | wx.LEFT | wx.RIGHT, 5)
        sizer.Add(self.actualFlow, 0, wx.ALIGN_CENTRE_VERTICAL, 0)
        sizer.Add(self.unitsLabel, 0, wx.ALIGN_CENTRE_VERTICAL | wx.LEFT, 5)
        self.body.Bind(wx.EVT_TEXT, self.OnSetpointText, self.setpoint)
        self.body.SetSizer(sizer)
        self.body.SetAutoLayout(True)
        sizer.Fit(self.body)
        self.pussy = 0
        return self.body

    def OnSetpointText(self, event):
        event.Skip()
        self.pussy += 25
        txt = 'x %0.2f:' % self.pussy
        self.gcfLabel.SetLabel(txt)
        self.gcfLabel.Refresh()
        self.resizeToFit()

    def resizeToFit(self):
        sizer = self.body.GetSizer()
        sizer.SetItemMinSize(self.gcfLabel, self.gcfLabel.GetSize())
        sizer.Layout()
        sizer.Fit(self.body)
        self.update()

    def setDevice(self, device):
        self.device = device
        self.updateDeviceInfo()

    def updateDeviceInfo(self):
        self.setTitle(self.device.getLabel())
        self.update()

    def setRecipeModel(self, model):
        self.model = model
        self.model.addModifyListener(self)

    def recipeModelChanged(self, event):
        if event.getEventType() == grideditor.recipemodel.CHANGE_DEVICE:
            if event.getDevice() != self.device:
                return
            self.updateDeviceInfo()

    def dispose(self):
        extendededitor.item.ExtendedEditorItem.dispose(self)
        if self.model is not None:
            self.model.removeModifyListener(self)
        return
