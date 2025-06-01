# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/extendededitor/src/extendededitor/mainitem.py
# Compiled at: 2004-11-19 02:39:40
import wx, wx.lib.masked.timectrl as timectrl, wx.lib.intctrl, plugins.ui.ui.widgets.contentassist
import plugins.extendededitor.extendededitor.item as extendededitor_item
import plugins.extendededitor.extendededitor.messages as messages
import plugins.extendededitor.extendededitor.images as images
import plugins.extendededitor.extendededitor.conditionals.itemlist as conditionals_itemlist
import plugins.extendededitor.extendededitor.utils.validation as validation, plugins.validator.validator.participant
import plugins.validator.validator as validator, logging
import plugins.ui.ui as ui

logger = logging.getLogger('extendededitor.mainitem')

class MainEditorItem(extendededitor_item.ExtendedEditorItem):
    __module__ = __name__

    def __init__(self):
        extendededitor_item.ExtendedEditorItem.__init__(self)
        self.setTitle(messages.get('exted.title'))
        self.setImage(images.getImage(images.MAIN_ITEM))
        self.suppress = False
        self.currentStep = None
        self.ready = False
        return

    def dispose(self):
        extendededitor_item.ExtendedEditorItem.dispose(self)
        validator.getDefault().removeValidationListener(self)

    def setFocus(self, focused):
        extendededitor_item.ExtendedEditorItem.setFocus(self, focused)
        self.supress = not self.isFocused()

    def recipeModelChanged(self, event):
        if event.getEventType() == event.CHANGE:
            step = self.model.getStepAt(event.getRowOffset())
            if step != self.currentStep:
                return
            if not self.isFocused():
                self.updateControlData()
        enable = self.model.getStepCount() > 0
        if self.isEnabled() == enable:
            return
        if enable:
            self.enable()
        else:
            self.disable()

    def createBody(self, parent):
        self.body = wx.Panel(parent, -1)
        self.body.SetBackgroundColour(parent.GetBackgroundColour())
        sizer = wx.FlexGridSizer(0, 1, 3, 3)
        fsizer = wx.FlexGridSizer(0, 3, 3, 3)
        fsizer.AddGrowableCol(2)
        label = wx.StaticText(self.body, -1, messages.get('exted.duration.label'))
        self.duration = timectrl.TimeCtrl(self.body, -1, fmt24hr=True)
        self.duration.SetHelpText('extendededitor:mainitem')
        self.duration.Enable()
        self.durationca = ui.widgets.contentassist.ContentAssistant(self.body)
        fsizer.Add(self.durationca.getControl(), 0, wx.ALIGN_CENTRE_VERTICAL)
        fsizer.Add(label, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
        fsizer.Add(self.duration, 0, wx.ALIGN_CENTRE_VERTICAL)
        sizer.Add(fsizer, 0, wx.EXPAND)
        fsizer = wx.FlexGridSizer(0, 2, 3, 3)
        fsizer.AddGrowableCol(1)
        self.repeatCheck = wx.CheckBox(self.body, -1, messages.get('exted.repeats.label'))
        p = wx.Panel(self.body, -1, size=wx.Size(2, 2))
        p.SetBackgroundColour(self.body.GetBackgroundColour())
        fsizer.Add(p, 0, wx.ALIGN_CENTRE_VERTICAL)
        fsizer.Add(self.repeatCheck, 0, wx.EXPAND | wx.ALIGN_CENTRE_VERTICAL)
        sizer.Add(fsizer, 0, wx.EXPAND | wx.ALL, 0)
        label = wx.StaticText(self.body, -1, messages.get('exted.enclosingsteps.label'))
        self.enclosingStepsText = wx.lib.intctrl.IntCtrl(self.body, value=1, min=1, max=9999)
        self.enclosingStepsText.Enable()
        self.enclosingstepsca = ui.widgets.contentassist.ContentAssistant(self.body)
        fsizer = wx.FlexGridSizer(0, 3, 3, 3)
        fsizer.AddGrowableCol(2)
        fsizer.Add(self.enclosingstepsca.getControl(), 0, wx.ALIGN_CENTRE_VERTICAL)
        fsizer.Add(label, 0, wx.ALIGN_CENTRE_VERTICAL)
        fsizer.Add(self.enclosingStepsText, 0, wx.ALIGN_CENTRE_VERTICAL)
        label = wx.StaticText(self.body, -1, messages.get('exted.repeatcount.label'))
        self.numberRepsText = wx.lib.intctrl.IntCtrl(self.body, value=1, limited=True, min=0, max=9999)
        p = wx.Panel(self.body, -1)
        p.SetBackgroundColour(self.body.GetBackgroundColour())
        fsizer.Add(p, 0, wx.ALIGN_CENTRE_VERTICAL)
        fsizer.Add(label, 0, wx.ALIGN_CENTRE_VERTICAL)
        fsizer.Add(self.numberRepsText, 0, wx.ALIGN_CENTRE_VERTICAL)
        sizer.Add(fsizer, 0, wx.EXPAND | wx.LEFT, 15)
        self.conditionalList = self.createConditionalList(self.body)
        sizer.Add(self.conditionalList.getControl(), 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 5)
        self.body.SetSizer(sizer)
        self.body.SetAutoLayout(True)
        sizer.Fit(self.body)
        self.control.Bind(timectrl.EVT_TIMEUPDATE, self.OnTimeUpdate, self.duration)
        self.control.Bind(wx.EVT_CHECKBOX, self.OnRepeatCheck, self.repeatCheck)
        self.control.Bind(wx.lib.intctrl.EVT_INT, self.OnEnclosingUpdate, self.enclosingStepsText)
        self.control.Bind(wx.lib.intctrl.EVT_INT, self.OnNumberRepsUpdate, self.numberRepsText)
        self.addStateManagedControl(self.enclosingStepsText)
        self.addStateManagedControl(self.numberRepsText)
        self.addStateManagedControl(self.repeatCheck)
        self.addStateManagedControl(self.duration)
        self.addStateManagedControl(self.conditionalList.getControl())
        self.prepareContentAssistants()
        self.updateCheckDeps()
        self.ready = True
        return self.body

    def createConditionalList(self, body):
        ctrl = conditionals_itemlist.ConditionalListItem()
        ctrl.createControl(body)
        return ctrl

    def prepareContentAssistants(self):
        validator.getDefault().addValidationListener(self)

    def validationEvent(self, valid, errors):
        if not self.ready:
            return
        self.durationca.clear()
        self.enclosingstepsca.clear()
        for error in errors:
            if self.currentStep != error.getStep():
                continue
            keys = error.getKeys()
            if 'duration' in keys:
                self.durationca.setWarning(error.getDescription())
                self.durationca.warn()
            elif 'looping' in keys:
                self.enclosingstepsca.setWarning(error.getDescription())
                self.enclosingstepsca.warn()

    def OnKillFocus(self, event):
        event.Skip()

    def OnChildFocus(self, event):
        event.Skip()

    def OnEnclosingStepsChar(self, event):
        event.Skip()
        keycode = event.GetKeyCode()
        self.upDownIntCtrl(keycode, self.enclosingStepsText)

    def OnNumberRepsChar(self, event):
        event.Skip()
        keycode = event.GetKeyCode()
        self.upDownIntCtrl(keycode, self.numberRepsText)

    def emptyStepSelected(self):
        self.duration.SetValue(wx.TimeSpan.Seconds(0))
        self.conditionalList.clearTests()
        self.conditionalList.setStep(None)
        self.disable()
        return

    def stepSelectionChanged(self, step):
        logger.debug("**Step selection changed: '%s'" % step)
        oldStep = self.currentStep
        self.currentStep = step
        if step is None:
            self.emptyStepSelected()
            return
        self.conditionalList.setRecipe(self.model)
        self.conditionalList.setStep(self.currentStep)
        self.updateControlData()
        self.validateStep()
        return

    def updateControlData(self):
        """Updates the control data from the current step."""
        if self.suppress:
            return
        logger.debug("Update Control Data '%s'" % self.currentStep)
        self.suppress = True
        if self.currentStep is None:
            self.suppress = False
            return
        step = self.currentStep
        self.duration.SetValue(wx.TimeSpan.Seconds(int(step.getDuration())))
        self.repeatCheck.SetValue(step.doesRepeat())
        self.enclosingStepsText.SetValue(step.getRepeatEnclosingSteps() + 1)
        self.numberRepsText.SetValue(step.getRepeatCount())
        self.conditionalList.setStep(step)
        self.updateCheckDeps()
        self.suppress = False
        return

    def validateStep(self):
        valid = validation.validateRepeats(self.currentStep, self.model.getRecipe())
        if not valid:
            self.enclosingstepsca.setWarning('The enclosing steps go past the end of the recipe')
            self.enclosingstepsca.warn()
        else:
            self.enclosingstepsca.clear()
        if valid:
            valid = validation.validateValidNumberRepeats(self.currentStep, self.model.getRecipe())
            if not valid:
                self.enclosingstepsca.setWarning('The number of enclosing steps must be greater than zero')
                self.enclosingstepsca.warn()
        valid = validation.validateDuration(self.currentStep)
        if not valid:
            self.durationca.setWarning('The step duration cannot be less than 1 second')
            self.durationca.warn()
        else:
            self.durationca.clear()
        if not validator.getDefault().isValid():
            self.validationEvent(False, validator.getDefault().getErrors())

    def updateStepData(self, timevalue=None):
        """Updates the current step with data from the controls"""
        if self.suppress:
            return
        if self.currentStep is None:
            return
        self.suppress = True
        step = self.currentStep
        if timevalue is not None:
            value = timevalue
        else:
            value = self.duration.GetValue(as_wxTimeSpan=True).GetSeconds()
        step.setDuration(value)
        step.setDoesRepeat(self.repeatCheck.IsChecked())
        step.setRepeatEnclosingSteps(self.enclosingStepsText.GetValue() - 1)
        step.setRepeatCount(self.numberRepsText.GetValue())
        self.model.updateStepEntry(self.currentStep)
        self.suppress = False
        return

    def OnEnclosingUpdate(self, event):
        event.Skip()
        self.updateStepData()

    def OnNumberRepsUpdate(self, event):
        event.Skip()
        self.updateStepData()

    def OnTimeUpdate(self, event):
        event.Skip()
        try:
            val = event.GetValue()
            if len(val) == 0:
                return
            self.updateStepData()
        finally:
            pass

    def updateCheckDeps(self):
        checked = self.repeatCheck.IsChecked()
        self.enclosingStepsText.Enable(checked)
        self.numberRepsText.Enable(checked)

    def OnRepeatCheck(self, event):
        event.Skip()
        self.updateCheckDeps()
        self.updateStepData()

    def OnShutIt(self, event):
        event.Skip()
        self.hide()
