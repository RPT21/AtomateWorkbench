# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/extendededitor/src/extendededitor/conditionals/testeditor.py
# Compiled at: 2005-06-28 18:45:53
import plugins.core.core as core, wx, copy, plugins.poi.poi.utils.scrolledpanel as scrolledpanel
import plugins.poi.poi.utils.staticwraptext, plugins.poi.poi as poi
import plugins.extendededitor.extendededitor.messages as messages
import plugins.extendededitor.extendededitor.conditionals as extendededitor_conditionals, logging

logger = logging.getLogger('extendededitor')

class ActionRowItem(object):
    __module__ = __name__

    def __init__(self, contribution):
        self.contribution = contribution
        self.control = None
        self.focused = False
        self.normalcolor = wx.WHITE
        self.highlightcolor = wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT)
        self.actionControl = None
        self.action = None
        return

    def handles(self, action):
        return self.contribution.handles(action)

    def setConditionalAction(self, action):
        self.action = action
        self.populateFromAction()

    def populateFromAction(self):
        self.actionControl.populateFromAction(self.action, self.actionControl)

    def createActionControl(self, parent):
        ctrl = self.contribution.createActionRowControl(parent)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(ctrl.getControl(), 1, wx.EXPAND | wx.ALL | 3)
        parent.SetSizer(sizer)
        parent.SetAutoLayout(True)
        return ctrl

    def createControl(self, parent):
        self.control = wx.Panel(parent, -1, size=wx.Size(-1, 10), style=wx.TAB_TRAVERSAL)
        self.control.SetBackgroundColour(wx.WHITE)
        self.actionControlPanel = wx.Panel(self.control, -1, size=wx.Size(-1, 20))
        self.actionControlPanel.SetBackgroundColour(self.control.GetBackgroundColour())
        self.actionControl = self.createActionControl(self.actionControlPanel)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.actionControlPanel, 1, wx.ALIGN_CENTRE_VERTICAL | wx.RIGHT, 5)
        self.control.SetSizer(sizer)
        self.control.SetAutoLayout(True)
        sizer.Fit(self.control)
        return self.control

    def setFocused(self, focused):
        changed = self.focused != focused
        self.focused = focused
        if changed:
            self.updateFocusView()

    def updateFocusView(self):
        if self.focused:
            color = self.highlightcolor
        else:
            color = self.normalcolor
        self.control.SetBackgroundColour(color)
        self.control.Refresh()

    def isFocused(self):
        return self.focused

    def getControl(self):
        return self.control

    def dispose(self):
        self.control.Destroy()

    def createAction(self):
        return self.contribution.createAction(self.actionControl)


class TestRowItem(object):
    __module__ = __name__

    def __init__(self, owner):
        self.owner = owner
        self.control = None
        self.focused = False
        self.normalcolor = wx.WHITE
        self.highlightcolor = wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT)
        self.conditionalTest = None
        self.leftOperands = []
        self.currentCtrl = None
        return

    def createTest(self):
        """Based on the left operand selection, create a conditional test"""
        contribution = self.leftOperands[self.leftOperandDropDown.GetSelection()]
        operatorIndex = self.operatorDropDown.GetSelection()
        ctrl = self.currentCtrl
        test = contribution.createTest(operatorIndex, ctrl)
        return test

    def setConditionalTest(self, test):
        self.conditionalTest = test
        self.populateFromTest(test)

    def populateFromTest(self, test):
        finalcontrib = None
        self.populateNew()
        for contribution in self.leftOperands:
            if contribution.handles(test):
                contribution.populateFromTest(test)
                finalcontrib = contribution
                break

        if finalcontrib is None:
            return
        contribution = finalcontrib
        idx = self.leftOperands.index(contribution)
        self.leftOperandDropDown.SetSelection(idx)
        self.operatorDropDown.SetSelection(contribution.getOperatorIndex())
        contribution.setRightOperandValue(self.currentCtrl)
        return

    def setFocused(self, focused):
        changed = self.focused != focused
        self.focused = focused
        if changed:
            self.updateFocusView()

    def updateFocusView(self):
        if self.focused:
            color = self.highlightcolor
        else:
            color = self.normalcolor
        self.control.SetBackgroundColour(color)
        self.control.Refresh()

    def isFocused(self):
        return self.focused

    def populateNew(self):
        self.populateLeftOperandDropDown()
        if self.leftOperandDropDown.GetCount() > 0:
            self.leftOperandDropDown.SetSelection(0)
            self.populateFromLeftOperand(0)

    def populateFromLeftOperand(self, loIndex):
        """Left operand index loIndex"""
        contribution = self.leftOperands[loIndex]
        operators = contribution.getOperators()
        self.operatorDropDown.Clear()
        for operator in operators:
            self.operatorDropDown.Append(operator)

        if self.operatorDropDown.GetCount() > 0:
            self.operatorDropDown.SetSelection(0)
        self.clearRightOperandPanel()
        ctrl = contribution.getRightOperandControl(self.rightOperatorPanel)
        self.currentCtrl = ctrl
        sizer = self.rightOperatorPanel.GetSizer()
        sizer.Add(ctrl.getControl(), 1, wx.EXPAND)
        wx.CallAfter(sizer.Layout)

    def clearRightOperandPanel(self):
        sizer = self.rightOperatorPanel.GetSizer()

        def killit(child):
            sizer.Remove(child)
            self.rightOperatorPanel.RemoveChild(child)
            child.Destroy()

        list(map(killit, self.rightOperatorPanel.GetChildren()))
        if self.currentCtrl is not None:
            self.currentCtrl.dispose()
        self.currentCtrl = None
        return

    def populateLeftOperandDropDown(self):
        del self.leftOperands[0:]
        self.leftOperandDropDown.Clear()
        for contributions in self.owner.getConditionalContributions():
            print(('slow ride:', contributions))
            if len(contributions) == 0:
                continue
            for testContribution in contributions:
                print(('Going to call test Contribution:', testContribution))
                for contribution in testContribution.getTestEditorContributions():
                    self.leftOperands.append(contribution)
                    name = contribution.getLeftOperandString()
                    self.leftOperandDropDown.Append(name)

    def createControl(self, parent):
        self.control = wx.Panel(parent, -1, size=wx.Size(-1, 10), style=wx.TAB_TRAVERSAL)
        self.control.SetBackgroundColour(wx.WHITE)
        self.leftOperandDropDown = wx.Choice(self.control, -1)
        self.operatorDropDown = wx.Choice(self.control, -1)
        self.rightOperatorPanel = wx.Panel(self.control, -1)
        self.rightOperatorPanel.SetBackgroundColour(self.control.GetBackgroundColour())
        self.rightOperatorPanel.SetSizer(wx.BoxSizer(wx.HORIZONTAL))
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.leftOperandDropDown, 1, wx.ALIGN_CENTRE_VERTICAL | wx.ALL, 3)
        sizer.Add(self.operatorDropDown, 1, wx.ALIGN_CENTRE_VERTICAL | wx.RIGHT, 5)
        sizer.Add(self.rightOperatorPanel, 1, wx.ALIGN_CENTRE_VERTICAL | wx.RIGHT, 5)
        self.control.SetSizer(sizer)
        self.control.SetAutoLayout(True)
        sizer.Fit(self.control)
        self.leftOperandDropDown.Bind(wx.EVT_CHOICE, self.OnLeftOperandDropDown)
        return self.control

    def OnLeftOperandDropDown(self, event):
        event.Skip()
        idx = self.leftOperandDropDown.GetSelection()
        contribution = self.leftOperands[idx]
        self.populateFromLeftOperand(idx)

    def getControl(self):
        return self.control

    def dispose(self):
        self.control.Destroy()


class ConditionalActionContribution(object):
    __module__ = __name__

    def __init__(self):
        pass

    def populateFromAction(self, action):
        pass

    def createActionRowControl(self, parent):
        pass

    def createAction(self, control):
        pass


class GlobalConditionalActionContribution(ConditionalActionContribution):
    __module__ = __name__

    def createActionRowControl(self, parent):
        ctrl = GlobalActionRowControl()
        ctrl.createControl(parent)
        return ctrl

    def handles(self, action):
        return action.getType() in ['abort-recipe', 'hold-step', 'advance-step']

    def createAction(self, control):
        if control.abortRadio.GetValue():
            return extendededitor_conditionals.AbortRecipeAction()
        if control.holdRadio.GetValue():
            return extendededitor_conditionals.HoldStepAction()
        if control.advanceRadio.GetValue():
            return extendededitor_conditionals.AdvanceStepAction()
        raise Exception('Unknown action!')


class GlobalActionRowControl(object):
    __module__ = __name__

    def __init__(self):
        self.control = None
        return

    def populateFromAction(self, action, control):
        t = action.getType()
        control.abortRadio.SetValue(t == 'abort-recipe')
        control.holdRadio.SetValue(t == 'hold-step')
        control.advanceRadio.SetValue(t == 'advance-step')

    def createControl(self, parent):
        self.control = wx.Panel(parent, -1)
        self.control.SetBackgroundColour(parent.GetBackgroundColour())
        self.abortRadio = wx.RadioButton(self.control, -1, messages.get('global.action.abort'), style=wx.RB_GROUP)
        self.holdRadio = wx.RadioButton(self.control, -1, messages.get('global.action.hold'))
        self.advanceRadio = wx.RadioButton(self.control, -1, messages.get('global.action.advance'))
        self.abortRadio.SetValue(True)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.abortRadio, 0, wx.ALIGN_CENTRE_VERTICAL | wx.RIGHT, 5)
        sizer.Add(self.holdRadio, 0, wx.ALIGN_CENTRE_VERTICAL | wx.RIGHT, 5)
        sizer.Add(self.advanceRadio, 0, wx.ALIGN_CENTRE_VERTICAL | wx.RIGHT, 3)
        sizer.Add(poi.utils.staticwraptext.StaticWrapText(self.control, -1, messages.get('global.action.advance.help')), 0, wx.ALIGN_CENTRE_VERTICAL)
        self.control.SetSizer(sizer)
        self.control.SetAutoLayout(True)
        return self.control

    def getControl(self):
        return self.control

    def putData(self, action):
        pass

    def dispose(self):
        pass


class TestEditor(object):
    __module__ = __name__

    def __init__(self):
        self.control = None
        self.recipe = None
        self.step = None
        self.rows = []
        self.actionRows = []
        self.selectedTestRow = None
        self.actionContributions = []
        self.conditionalContributions = []
        self.conditionalTests = None
        return

    def setConditionalTests(self, conditionaltests):
        self.conditionalTests = conditionaltests

    def populateTests(self):
        """populate from existing tests"""
        if self.conditionalTests is None:
            return
        for test in self.conditionalTests.getTests():
            item = self.createRowItem()
            item.populateFromTest(test)
            self.addTestRowItem(item, refresh=False)

        self.testNameField.SetValue(self.conditionalTests.getName())
        self.andRadio.SetValue(self.conditionalTests.isConnectiveAnd())
        self.orRadio.SetValue(self.conditionalTests.isConnectiveOr())
        for action in self.conditionalTests.getActions():
            for item in self.actionRows:
                if item.handles(action):
                    item.setConditionalAction(action)

        wx.CallAfter(self.testsGridSizer.Layout)
        return

    def populateConditionalActionContributions(self):
        """simply adds the one action for now"""
        self.actionContributions = [
         GlobalConditionalActionContribution()]

    def populateConditionalActionsPanel(self):
        for contribution in self.actionContributions:
            item = self.createActionRowItem(contribution)
            self.addActionRowItem(item)

    def populateConditionalContributions(self):
        logger.debug('Populating conditional contributions with existing? %s' % self.conditionalContributions)
        self.conditionalContributions.extend(core.getConditionalContributions())
        logger.debug('Conditional contributions with core exiting ones: %s' % self.conditionalContributions)
        for device in self.recipe.getDevices():
            logger.debug("\tAsking device: '%s'" % device)
            self.conditionalContributions.append(device.getConditionalContributions())

    def getConditionalContributions(self):
        print((' i got asked:', self.conditionalContributions))
        return self.conditionalContributions

    def setRecipe(self, recipe):
        self.recipe = recipe
        self.populateConditionalContributions()
        self.populateConditionalActionContributions()

    def setStep(self, step):
        self.step = step

    def createControl(self, parent):
        self.control = wx.Dialog(parent, -1, messages.get('dialog.testeditor.title'), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.testNameField = wx.TextCtrl(self.control, -1)
        self.andRadio = wx.RadioButton(self.control, -1, messages.get('dialog.testeditor.and.label'), style=wx.RB_GROUP)
        self.orRadio = wx.RadioButton(self.control, -1, messages.get('dialog.testeditor.or.label'))
        self.testsGrid = scrolledpanel.ScrolledPanel(self.control, -1, style=wx.SIMPLE_BORDER)
        self.testsGridSizer = wx.BoxSizer(wx.VERTICAL)
        self.testsGrid.SetSizer(self.testsGridSizer)
        self.testsGrid.SetBackgroundColour(wx.WHITE)
        self.moreButton = wx.Button(self.control, -1, messages.get('dialog.testeditor.more.label'))
        self.fewerButton = wx.Button(self.control, -1, messages.get('dialog.testeditor.fewer.label'))
        self.fewerButton.Disable()
        self.actionsGrid = scrolledpanel.ScrolledPanel(self.control, -1, style=wx.SIMPLE_BORDER)
        self.actionsGridSizer = wx.BoxSizer(wx.VERTICAL)
        self.actionsGrid.SetSizer(self.actionsGridSizer)
        self.actionsGrid.SetBackgroundColour(wx.WHITE)
        self.okButton = wx.Button(self.control, wx.ID_OK, 'OK')
        self.cancelButton = wx.Button(self.control, wx.ID_CANCEL, 'Cancel')
        sizer = wx.BoxSizer(wx.VERTICAL)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(wx.StaticText(self.control, -1, messages.get('dialog.testeditor.name.label')), 0, wx.ALIGN_CENTRE_VERTICAL)
        hsizer.Add(self.testNameField, 1, wx.EXPAND | wx.ALIGN_CENTRE_VERTICAL)
        sizer.Add(hsizer, 0, wx.EXPAND | wx.LEFT | wx.TOP | wx.RIGHT, 10)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(wx.StaticText(self.control, -1, 'If ...'), 0, wx.LEFT | wx.TOP, 10)
        hsizer.Add(self.andRadio, 0, wx.RIGHT, 5)
        hsizer.Add(self.orRadio, 0)
        sizer.Add(hsizer, 0, wx.EXPAND | wx.ALIGN_LEFT | wx.BOTTOM | wx.LEFT, 10)
        sizer.Add(self.testsGrid, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(self.moreButton, 0, wx.RIGHT, 5)
        hsizer.Add(self.fewerButton, 0)
        sizer.Add(hsizer, 0, wx.EXPAND | wx.ALIGN_LEFT | wx.LEFT | wx.BOTTOM, 10)
        sizer.Add(wx.StaticText(self.control, -1, messages.get('dialog.testeditor.actiongrid.label')), 0, wx.LEFT | wx.TOP, 10)
        sizer.Add(self.actionsGrid, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        sizer.Add(wx.StaticLine(self.control, -1), 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 5)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(self.okButton, 0, wx.ALIGN_CENTRE_VERTICAL)
        hsizer.Add(self.cancelButton, 0, wx.ALIGN_CENTRE_VERTICAL)
        sizer.Add(hsizer, 0, wx.ALIGN_RIGHT | wx.TOP | wx.BOTTOM | wx.RIGHT, 10)
        self.control.SetSizer(sizer)
        self.control.SetAutoLayout(True)
        self.control.SetSize(wx.Size(600, 400))
        self.control.CentreOnScreen()
        self.moreButton.Bind(wx.EVT_BUTTON, self.OnMoreButton)
        self.fewerButton.Bind(wx.EVT_BUTTON, self.OnFewerButton)
        self.testsGrid.Bind(wx.EVT_CHILD_FOCUS, self.OnTestsGridFocus)
        self.testNameField.Bind(wx.EVT_TEXT, self.OnTestNameText)
        self.okButton.Disable()
        return self.control

    def validate(self):
        val = self.testNameField.GetValue()
        val = val.strip()
        if len(val) == 0:
            self.okButton.Disable()
            return
        if len(self.rows) == 0:
            self.okButton.Disable()
            return
        self.okButton.Enable()

    def OnTestNameText(self, event):
        event.Skip()
        self.validate()

    def OnDebugDumpTests(self, event):
        logger.debug('Conditional Tests Debug')
        for test in self.getConditionalTests():
            logger.debug('\t%s' % str(test))

        logger.debug('-done-')

    def OnTestsGridFocus(self, event):
        event.Skip()
        item = self.findTestRowForChild(event.GetEventObject())
        self.setRowFocus(item)
        self.selectedTestRow = item
        self.fewerButton.Enable(item is not None)
        return

    def findTestRowForChild(self, child):
        rows = copy.copy(self.rows)
        for row in rows:
            ctrl = row.getControl()
            parent = child
            while parent != self.control and parent != None:
                if parent == ctrl:
                    return row
                parent = parent.GetParent()

        return None
        return

    def setRowFocus(self, focused):
        for row in self.rows:
            row.setFocused(row == focused)

    def createRowItem(self):
        rowPanel = TestRowItem(self)
        rowPanel.createControl(self.testsGrid)
        return rowPanel

    def clearActionsGrid(self):
        sizer = self.actionsGrid.GetSizer()

        def killit(child):
            sizer.Remove(child)
            self.actionGrid.RemoveChild(child)

        list(map(killit, self.actionsGrid.GetChildren()))
        for actionRow in self.actionRows:
            actionRow.dispose()

    def createActionRowItem(self, contrib):
        actionRowPanel = ActionRowItem(contrib)
        actionRowPanel.createControl(self.actionsGrid)
        return actionRowPanel

    def OnFewerButton(self, event):
        if self.selectedTestRow is None:
            return
        idx = self.rows.index(self.selectedTestRow)
        self.removeTestRowItem(self.selectedTestRow)
        nextitem = None
        if len(self.rows) > 0:
            if idx > 0:
                idx -= 1
                nextitem = self.rows[idx]
        self.selectTestRow(nextitem)
        self.validate()
        return

    def selectTestRow(self, item):
        if item is None:
            self.fewerButton.Disable()
            return
        item.getControl().SetFocus()
        return

    def OnMoreButton(self, event):
        newitem = self.createRowItem()
        self.addTestRowItem(newitem)
        newitem.populateNew()
        self.validate()

    def addActionRowItem(self, item, refresh=True):
        self.actionRows.append(item)
        self.actionsGridSizer.Add(item.getControl(), 0, wx.EXPAND | wx.ALL, 3)
        self.actionsGrid.SetupScrolling()
        item.getControl().SetFocus()
        if refresh:
            wx.CallAfter(self.actionsGridSizer.Layout)

    def addTestRowItem(self, item, refresh=True):
        self.rows.append(item)
        self.testsGridSizer.Add(item.getControl(), 0, wx.EXPAND | wx.ALL, 0)
        self.testsGrid.SetupScrolling()
        item.getControl().SetFocus()
        if refresh:
            wx.CallAfter(self.testsGridSizer.Layout)

    def removeTestRowItem(self, item):
        if not item in self.rows:
            return
        self.rows.remove(item)
        self.testsGrid.RemoveChild(item.getControl())
        self.testsGridSizer.Remove(item.getControl())
        self.testsGridSizer.Layout()
        item.dispose()

    def isConnectiveAnd(self):
        return self.andRadio.GetValue()

    def getActions(self):
        actions = []
        for row in self.actionRows:
            actions.append(row.createAction())

        return actions

    def getConditionalTests(self):
        """Iterates thru all conditionals in the rows and creates a test for each of them"""
        tests = []
        for row in self.rows:
            tests.append(row.createTest())

        return tests

    def getTestName(self):
        return self.testNameField.GetValue().strip()

    def getConditionalTest(self):
        return self.conditionalTests

    def getControl(self):
        return self.control

    def showModal(self):
        self.populateConditionalActionsPanel()
        self.populateTests()
        return self.control.ShowModal()

    def dispose(self):
        self.control.Destroy()
