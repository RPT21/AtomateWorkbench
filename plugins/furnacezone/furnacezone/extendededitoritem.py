# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/furnacezone/src/furnacezone/extendededitoritem.py
# Compiled at: 2004-11-19 02:46:08
import wx, plugins.extendededitor.extendededitor.item, plugins.grideditor.grideditor.recipemodel
import plugins.furnacezone.furnacezone.messages as messages
import plugins.furnacezone.furnacezone.stepentry as furnacezone_stepentry
import plugins.ui.ui.widgets.contentassist, logging
import plugins.ui.ui as ui
import plugins.extendededitor.extendededitor as extendededitor
import plugins.grideditor.grideditor as grideditor

logger = logging.getLogger('furnacezone.extendededitor')

class FurnaceZoneExtendedEditorItem(extendededitor.item.ExtendedEditorItem):
    __module__ = __name__

    def __init__(self):
        extendededitor.item.ExtendedEditorItem.__init__(self)
        self.device = None
        self.model = None
        self.suppress = False
        self.currentStep = None
        return

    def createBody(self, parent):
        self.body = wx.Panel(parent, -1)
        self.body.SetBackgroundColour(parent.GetBackgroundColour())
        self.inctrl = None
        self.contentassist = ui.widgets.contentassist.ContentAssistant(self.body)
        label = wx.StaticText(self.body, -1, messages.get('exted.setpoint.label'))
        self.setpoint = wx.TextCtrl(self.body, -1)
        sizer = wx.BoxSizer(wx.VERTICAL)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(self.contentassist.getControl(), 0, wx.ALL | wx.ALIGN_CENTRE_VERTICAL, 0)
        hsizer.Add(label, 0, wx.ALIGN_CENTRE_VERTICAL | wx.RIGHT, 5)
        hsizer.Add(self.setpoint, 0, wx.ALL | wx.ALIGN_CENTRE_VERTICAL, 0)
        sizer.Add(hsizer, 1, wx.EXPAND | wx.ALL)
        self.linearRampCheckbox = wx.CheckBox(self.body, -1, messages.get('exted.linearramp.label'))
        self.rampOriginSetpoint = wx.RadioButton(self.body, -1, messages.get('exted.linearramp_prevsetpoint.label'), style=wx.RB_GROUP)
        self.rampOriginSetpoint.Disable()
        self.rampOriginTemp = wx.RadioButton(self.body, -1, messages.get('exted.linearramp_lasttemp.label'))
        self.rampOriginTemp.Disable()
        sizer.Add(self.linearRampCheckbox, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 5)
        sizer.Add(self.rampOriginSetpoint, 0, wx.EXPAND | wx.LEFT, 15)
        empty = wx.Window(self.body, -1, size=wx.Size(1, 1))
        empty.SetBackgroundColour(self.body.GetBackgroundColour())
        sizer.Add(empty, 0, wx.EXPAND | wx.TOP, 5)
        sizer.Add(self.rampOriginTemp, 0, wx.EXPAND | wx.LEFT, 15)
        self.body.Bind(wx.EVT_TEXT, self.OnSetpointText, self.setpoint)
        self.setpoint.Bind(wx.EVT_KILL_FOCUS, (lambda evt: self.OnKillFocusText(evt, self.setpoint)))
        self.setpoint.Bind(wx.EVT_SET_FOCUS, (lambda evt: self.OnSetFocusText(evt, self.setpoint)))
        self.linearRampCheckbox.Bind(wx.EVT_CHECKBOX, self.OnLinearRampCheck)

        def mo(event):
            event.Skip()
            self.updateStepData()

        self.rampOriginTemp.Bind(wx.EVT_RADIOBUTTON, mo)
        self.rampOriginSetpoint.Bind(wx.EVT_RADIOBUTTON, mo)
        self.body.SetSizer(sizer)
        self.body.SetAutoLayout(True)
        sizer.Fit(self.body)
        self.addStateManagedControl(self.setpoint)
        self.addStateManagedControl(self.linearRampCheckbox)
        self.addStateManagedControl(self.rampOriginSetpoint)
        self.addStateManagedControl(self.rampOriginTemp)
        self.updateDeviceInfo()
        return self.body
        return

    def OnLinearRampCheck(self, event):
        event.Skip()
        checked = self.linearRampCheckbox.IsChecked()
        self.rampOriginSetpoint.Enable(checked)
        self.rampOriginTemp.Enable(checked)
        self.updateStepData()

    def OnSetpointText(self, event):
        event.Skip()
        self.updateStepData()

    def OnSetFocusText(self, event, ctrl):
        event.Skip()
        self.inctrl = ctrl

    def OnKillFocusText(self, event, ctrl):
        """Changes the existing value to conform to one expected"""
        logger.debug('Conforming ...')
        self.suppress = True
        val = ctrl.GetValue()
        try:
            val = int(val)
        except Exception as msg:
            logger.warning("Unable to conform value '%s' to int. Setting to 0" % val)
            val = 0

        logger.debug('Conformed: %d' % val)
        ctrl.SetValue(str(val))
        self.suppress = False

    def getSetpointValue(self):
        val = self.setpoint.GetValue()
        try:
            return int(val)
        except Exception as msg:
            logger.debug("Unable to convert value '%s' to int. Using 0" % val)
            return 0

    def setDevice(self, device):
        self.device = device
        self.updateDeviceInfo()

    def updateDeviceInfo(self):
        self.setTitle(self.device.getLabel())
        if self.control is None:
            return
        self.update()
        return

    def emptyStepSelected(self):
        self.disable()

    def stepSelectionChanged(self, step):
        logger.debug("**Step selection changed: '%s'" % step)
        oldStep = self.currentStep
        self.currentStep = step
        if step is None:
            self.emptyStepSelected()
            return
        self.updateControlData()
        self.validateStep()
        return

    def updateControlData(self):
        logger.debug('update control data %s/%s' % (self.currentStep, self.suppress))
        if self.currentStep is None:
            return
        if self.suppress:
            return
        self.suppress = True
        step = self.currentStep
        entry = self.model.getEntryAtStep(step, self.device)
        logger.debug("setting setpoint: '%d'" % entry.getSetpoint())
        self.setpoint.SetValue(str(entry.getSetpoint()))
        if entry.getSetpointMode() == furnacezone_stepentry.SETPOINT_LINEAR_RAMP:
            self.linearRampCheckbox.SetValue(True)
            self.rampOriginSetpoint.Enable(True)
            self.rampOriginTemp.Enable(True)
            print((entry.isRampFromSetpoint(), entry.isRampFromLast()))
            self.rampOriginSetpoint.SetValue(entry.isRampFromSetpoint())
            self.rampOriginTemp.SetValue(entry.isRampFromLast())
        else:
            self.linearRampCheckbox.SetValue(False)
            self.rampOriginSetpoint.Disable()
            self.rampOriginTemp.Disable()
        self.suppress = False
        return

    def updateStepData(self):
        if self.suppress:
            return
        if self.currentStep is None:
            return
        step = self.currentStep
        entry = self.model.getEntryAtStep(step, self.device)
        try:
            value = int(self.setpoint.GetValue())
            entry.setSetpoint(value)
        except Exception as msg:
            logger.debug("Unable to parse value for setpoint: '%s'" % msg)
            entry.setSetpoint(0)

        checked = self.linearRampCheckbox.IsChecked()
        if checked:
            entry.setSetpointMode(furnacezone_stepentry.SETPOINT_LINEAR_RAMP)
            if self.rampOriginSetpoint.GetValue():
                entry.setRampStart(furnacezone_stepentry.RAMP_FROM_SETPOINT)
            else:
                entry.setRampStart(furnacezone_stepentry.RAMP_FROM_LAST)
        else:
            entry.setSetpointMode(furnacezone_stepentry.SETPOINT_SINGLE)
        self.validateStep()
        self.model.updateStepEntry(self.currentStep)
        return

    def validateStep(self):
        pass

    def recipeModelChanged(self, event):
        if event.getEventType() == grideditor.recipemodel.CHANGE_DEVICE:
            if event.getDevice() != self.device:
                return
            self.updateDeviceInfo()
        elif event.getEventType() == event.CHANGE and self.device == event.getDevice():
            step = self.model.getStepAt(event.getRowOffset())
            if step != self.currentStep:
                return
            self.updateControlData()
        enable = self.model.getStepCount() > 0
        if self.isEnabled() == enable:
            return
        if enable:
            self.enable()
        else:
            self.disable()

    def dispose(self):
        extendededitor.item.ExtendedEditorItem.dispose(self)
        if self.model is not None:
            self.model.removeModifyListener(self)
        return
