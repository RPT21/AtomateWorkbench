# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/resourcesui/src/resourcesui/newrecipewizard.py
# Compiled at: 2004-11-19 02:47:44
import re, wx, sys, os, plugins.ui.ui, threading, plugins.poi.poi.wizards, plugins.poi.poi.operation, plugins.poi.poi.dialogs.progress
import plugins.poi.poi.views.viewers, plugins.poi.poi.views, plugins.hardware.hardware.hardwaremanager, plugins.resources.resources
import plugins.resourcesui.resourcesui.messages as messages, plugins.resourcesui.resourcesui.actions, plugins.resourcesui.resourcesui.utils, logging
logger = logging.getLogger('resourcesui.newrecipewizard')

class NewRecipeWizard(plugins.poi.poi.wizards.Wizard):
    __module__ = __name__

    def __init__(self):
        plugins.poi.poi.wizards.Wizard.__init__(self)

    def addPages(self):
        firstPage = FirstRecipeWizardPage()
        self.addPage(firstPage)
        self.setStartingPage(firstPage)

    def createControl(self, parent):
        poi.wizards.Wizard.createControl(self, parent)
        self.control.SetSize((600, 600))
        self.control.CentreOnScreen()

    def createBody(self, parent):
        pass


class FirstRecipeWizardPage(plugins.poi.poi.wizards.WizardPage):
    __module__ = __name__

    def __init__(self):
        plugins.poi.poi.wizards.WizardPage.__init__(self, 'first', 'New Recipe')
        self.setMessage('General Recipe Information')
        self.setDescription('Enter a name for the recipe')

    def performFinish(self):
        name = self.nameField.GetValue().strip()
        comment = self.commentCtrl.GetValue().strip()
        shared = self.sharedCheck.GetValue()
        defaultDevices = self.createDefaultDevicesCheck.GetValue()

        class NewRecipeRunner(plugins.poi.poi.operation.RunnableWithProgress):
            __module__ = __name__

            def run(self, monitor):
                numTasks = 3
                if defaultDevices:
                    numTasks += 1
                monitor.beginTask('Creating new recipe', numTasks)
                project = plugins.resources.resources.getDefault().getWorkspace().getProject(name, shared)
                desc = project.getDescription()
                desc.comment = comment
                monitor.subTask('Creating project')
                project.create()
                monitor.worked(1)
                monitor.subTask('Creating initial version')
                version = plugins.resourcesui.resourcesui.actions.createInitialVersionAction(project)
                monitor.worked(1)
                if defaultDevices:
                    monitor.subTask('Creating default devices')
                    lst = plugins.hardware.hardware.hardwaremanager.createDevicesForConfiguredHardware()
                    recipe = plugins.resourcesui.resourcesui.actions.getRecipeFromVersion(version)
                    for device in lst:
                        recipe.addDevice(device)

                    plugins.resourcesui.resourcesui.utils.writeRecipe(recipe, version)
                    monitor.worked(1)
                monitor.subTask('Opening new version in editor')
                plugins.resourcesui.resourcesui.actions.openRecipeVersion(version)
                monitor.worked(1)
                monitor.endTask()

        f = self.control
        dlg = plugins.poi.poi.dialogs.progress.ProgressDialog(f)
        try:
            dlg.run(NewRecipeRunner(), fork=True)
        except Exception as msg:
            logger.exception(msg)

    def createControl(self, composite):
        self.control = wx.Panel(composite, -1, size=wx.Size(100, 100))
        fsizer = wx.FlexGridSizer(0, 2, 5, 5)
        fsizer.AddGrowableCol(1)
        self.nameField = wx.TextCtrl(self.control, -1)
        label = wx.StaticText(self.control, -1, messages.get('newrecipewizard.name.label'))
        fsizer.Add(label, 0, wx.ALIGN_CENTRE_VERTICAL)
        fsizer.Add(self.nameField, 1, wx.ALIGN_CENTRE_VERTICAL | wx.GROW)
        label = wx.StaticText(self.control, -1, messages.get('newrecipewizard.comment.label'))
        self.commentCtrl = wx.TextCtrl(self.control, -1, size=wx.Size(-1, 200), style=wx.TE_MULTILINE)
        sizer2 = wx.BoxSizer(wx.VERTICAL)
        sizer2.Add(label, 0, wx.GROW | wx.LEFT | wx.RIGHT, 5)
        sizer2.Add(self.commentCtrl, 0, wx.GROW | wx.ALL, 5)
        self.sharedCheck = wx.CheckBox(self.control, -1, messages.get('newrecipewizard.sharedoption.label'))
        self.createDefaultDevicesCheck = wx.CheckBox(self.control, -1, messages.get('newrecipewizard.createdefaultdevices.label'))
        self.createDefaultDevicesCheck.SetValue(True)
        mainsizer = wx.BoxSizer(wx.VERTICAL)
        mainsizer.Add(fsizer, 0, wx.GROW | wx.ALL, 5)
        mainsizer.Add(sizer2, 0, wx.GROW)
        mainsizer.Add(self.sharedCheck, 0, wx.GROW | wx.LEFT | wx.RIGHT, 5)
        mainsizer.Add(self.createDefaultDevicesCheck, 0, wx.GROW | wx.LEFT | wx.RIGHT, 5)
        self.control.SetSizer(mainsizer)
        self.control.SetAutoLayout(True)
        self.control.Bind(wx.EVT_TEXT, self.OnUpdateText, self.nameField)
        self.updateControls()
        self.setPageComplete(False)
        return self.control

    def OnUpdateText(self, event):
        event.Skip()
        self.updateControls()

    def validName(self, name):
        name = name.strip()
        if len(name) == 0:
            return False
        validchars = '.*[^a-zA-Z0-9_\\ ].*'
        cmp = re.compile(validchars)
        m = cmp.match(name)
        if m is not None:
            return False
        return True

    def projectExists(self, name):
        project = plugins.resources.resources.getDefault().getWorkspace().getProject(name)
        return project.exists()

    def updateValidControls(self, valid):
        self.commentCtrl.Enable(valid)
        self.sharedCheck.Enable(valid)
        self.setPageComplete(valid)
        self.createDefaultDevicesCheck.Enable(valid)

    def updateControls(self):
        name = self.nameField.GetValue().strip()
        if len(name) == 0:
            self.updateValidControls(False)
            self.setErrorMessage(None)
            return
        if not self.validName(name):
            self.updateValidControls(False)
            self.setErrorMessage('Invalid name')
            return
        if self.projectExists(name):
            self.updateValidControls(False)
            self.setErrorMessage('A project by that name already exists')
            return
        self.updateValidControls(True)
        self.setErrorMessage(None)
        return
