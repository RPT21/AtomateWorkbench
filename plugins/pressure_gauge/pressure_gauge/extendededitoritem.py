# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/mfc/src/mfc/extendededitoritem.py
# Compiled at: 2004-10-13 02:10:16
"""
Extended editor item for mfc device.

Two values: setpoint and actualflow setpoint.
            Actual Flow Setpoint is the value after the setpoint is multiplied by 
            the GCF
"""
import wx, mfc.utils, extendededitor.item, grideditor.recipemodel, mfc.messages as messages, ui.widgets.contentassist, logging
logger = logging.getLogger('mfc.extendededitor')

class MFCExtendedEditorItem(extendededitor.item.ExtendedEditorItem):
    __module__ = __name__

    def __init__(self):
        extendededitor.item.ExtendedEditorItem.__init__(self)
        self.device = None
        self.model = None
        self.suppress = False
        self.currentStep = None
        self.precision = 4
        self.gcf = 100.0
        return

    def createBody(self, parent):
        self.body = wx.Panel(parent, -1)
        self.body.SetBackgroundColour(parent.GetBackgroundColour())
        self.inctrl = None
        self.contentassist = ui.widgets.contentassist.ContentAssistant(self.body)
        label = wx.StaticText(self.body, -1, messages.get('exted.setpoint.label'))
        self.setpoint = wx.TextCtrl(self.body, -1)
        self.gcfLabel = wx.StaticText(self.body, -1, ' x 00.00')
        self.actualFlow = wx.TextCtrl(self.body, -1)
        self.unitsLabel = wx.StaticText(self.body, -1, '')
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.contentassist.getControl(), 0, wx.ALL | wx.ALIGN_CENTRE_VERTICAL, 0)
        sizer.Add(label, 0, wx.ALIGN_CENTRE_VERTICAL | wx.RIGHT, 5)
        sizer.Add(self.setpoint, 0, wx.ALL | wx.ALIGN_CENTRE_VERTICAL, 0)
        sizer.Add(self.gcfLabel, 0, wx.ALIGN_CENTRE_VERTICAL | wx.LEFT | wx.RIGHT, 5)
        sizer.Add(self.actualFlow, 0, wx.ALIGN_CENTRE_VERTICAL, 0)
        sizer.Add(self.unitsLabel, 0, wx.ALIGN_CENTRE_VERTICAL | wx.LEFT, 5)
        self.body.Bind(wx.EVT_TEXT, self.OnSetpointText, self.setpoint)
        self.body.Bind(wx.EVT_TEXT, self.OnActualFlowText, self.actualFlow)
        self.setpoint.Bind(wx.EVT_KILL_FOCUS, (lambda evt: self.OnKillFocusText(evt, self.setpoint)))
        self.actualFlow.Bind(wx.EVT_KILL_FOCUS, (lambda evt: self.OnKillFocusText(evt, self.actualFlow)))
        self.setpoint.Bind(wx.EVT_SET_FOCUS, (lambda evt: self.OnSetFocusText(evt, self.setpoint)))
        self.actualFlow.Bind(wx.EVT_SET_FOCUS, (lambda evt: self.OnSetFocusText(evt, self.actualFlow)))
        self.body.SetSizer(sizer)
        self.body.SetAutoLayout(True)
        sizer.Fit(self.body)
        self.addStateManagedControl(self.setpoint)
        self.addStateManagedControl(self.actualFlow)
        self.updateDeviceInfo()
        return self.body
        return

    def OnSetFocusText(self, event, ctrl):
        event.Skip()
        self.inctrl = ctrl

    def OnKillFocusText(self, event, ctrl):
        """Changes the existing value to conform to one expected"""
        logger.debug('Conforming ...')
        self.suppress = True
        val = ctrl.GetValue()
        try:
            val = float(val)
        except Exception as msg:
            logger.warning("Unable to conform value '%s' to float. Setting to 0" % val)
            val = 0.0

        logger.debug('Conformed: %f' % val)
        ctrl.SetValue(self.float2str(val))
        self.suppress = False

    def getSetpointValue(self):
        val = self.setpoint.GetValue()
        try:
            return float(val)
        except Exception as msg:
            logger.debug("Unable to convert value '%s' to float. Using 0.0" % val)
            return 0.0

    def getActualFlowValue(self):
        val = self.actualFlow.GetValue()
        try:
            return float(val)
        except Exception as msg:
            logger.debug("Unable to convert value '%s' to float. Using 0.0" % val)
            return 0.0

    def getGCF(self):
        return self.gcf

    def float2str(self, val):
        """Returns floating point value to a configured precision"""
        frmt = '%%0.%df' % self.precision
        return frmt % val

    def setpoint2actual(self):
        val = self.getSetpointValue()
        gcf = self.getGCF()
        afv = gcf / 100.0 * val
        self.actualFlow.SetValue(self.float2str(afv))

    def actual2setpoint(self):
        val = self.getActualFlowValue()
        gcf = self.getGCF()
        spv = val / (gcf / 100.0)
        self.setpoint.SetValue(self.float2str(spv))

    def OnActualFlowText(self, event):
        event.Skip()
        if self.inctrl != self.actualFlow:
            return
        self.actual2setpoint()
        self.updateStepData()

    def OnSetpointText(self, event):
        event.Skip()
        if self.inctrl != self.setpoint:
            return
        self.setpoint2actual()
        self.updateStepData()

    def resizeToFit(self):
        sizer = self.body.GetSizer()
        sizer.SetItemMinSize(self.gcfLabel, self.gcfLabel.GetSize())
        sizer.SetItemMinSize(self.unitsLabel, self.unitsLabel.GetSize())
        sizer.Layout()
        sizer.Fit(self.body)
        self.update()

    def setDevice(self, device):
        self.device = device
        self.updateDeviceInfo()

    def setGCFLabel(self, gcf):
        self.gcfLabel.SetLabel('x %0.2f=' % (gcf / 100.0))

    def setUnitsLabel(self, units):
        self.unitsLabel.SetLabel(units)

    def updateDeviceInfo(self):
        self.setTitle(self.device.getLabel())
        if self.control is None:
            return
        hwhints = self.device.getHardwareHints()
        try:
            gcf = float(hwhints.getChildNamed('conversion-factor').getValue())
        except Exception as msg:
            logger.warning("Unable to get gas conversion factor for '%s':%s" % (self.device.getLabel(), msg))
            gcf = 100.0

        try:
            units = hwhints.getChildNamed('units').getValue()
        except Exception as msg:
            logger.warning("Unable to get gas units '%s':'%s'" % (self.device.getLabel(), msg))
            units = 'N/A'

        self.gcf = gcf
        self.units = units
        self.setGCFLabel(self.gcf)
        self.setUnitsLabel(self.units)
        self.resizeToFit()
        self.setpoint2actual()
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
        if self.currentStep is None:
            return
        if self.suppress:
            return
        self.suppress = True
        step = self.currentStep
        entry = self.model.getEntryAtStep(step, self.device)
        self.setpoint.SetValue(self.float2str(entry.getFlow()))
        self.setpoint2actual()
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
            value = float(self.setpoint.GetValue())
            entry.setFlow(value)
        except Exception as msg:
            logger.debug("Unable to parse value for setpoint: '%s'" % msg)
            entry.setFlow(0.0)

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
