# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/resourcesui/src/resourcesui/exportrecipewizard.py
# Compiled at: 2004-11-02 05:40:32
import re, wx, sys, os, plugins.ui.ui, threading, plugins.poi.poi.wizards, plugins.poi.poi.operation
import plugins.poi.poi.dialogs.progress, plugins.poi.poi.views.viewers, plugins.poi.poi.views
import plugins.resources.resources, plugins.resourcesui.resourcesui.messages as messages, plugins.resourcesui.resourcesui.actions, logging
logger = logging.getLogger('resourcesui.exportrecipewizard')

class ExportRecipeWizard(plugins.poi.poi.wizards.Wizard):
    __module__ = __name__

    def __init__(self):
        plugins.poi.poi.wizards.Wizard.__init__(self)

    def setResource(self, resource):
        pass

    def addPages(self):
        firstPage = FirstRecipeWizardPage()
        secondPage = SecondPage()
        self.addPage(firstPage)
        self.addPage(secondPage)
        firstPage.setNextPage(secondPage)
        secondPage.setPreviousPage(firstPage)
        self.setStartingPage(firstPage)

    def createControl(self, parent):
        plugins.poi.poi.wizards.Wizard.createControl(self, parent)
        self.control.SetSize((600, 600))
        self.control.CentreOnScreen()

    def createBody(self, parent):
        pass


class SecondPage(plugins.poi.poi.wizards.WizardPage):
    __module__ = __name__

    def __init__(self):
        plugins.poi.poi.wizards.WizardPage.__init__(self, 'second', 'Second Page')
        self.setMessage('Second Page Yeah')
        self.setDescription('This is the second page')

    def performFinish(self):
        pass

    def createControl(self, composite):
        self.control = wx.Panel(composite, -1, size=wx.Size(100, 100))
        self.setPageComplete(True)
        self.setFinished(False)
        return self.control


class FirstRecipeWizardPage(plugins.poi.poi.wizards.WizardPage):
    __module__ = __name__

    def __init__(self):
        plugins.poi.poi.wizards.WizardPage.__init__(self, 'first', 'Export Recipe')
        self.setMessage('Select Destination')
        self.setDescription('Click browse to select a destination for the project')

    def performFinish(self):
        pass

    def createControl(self, composite):
        self.control = wx.Panel(composite, -1, size=wx.Size(100, 100))
        self.destinationDirField = wx.TextCtrl(self.control, -1)
        self.destinationDirField.SetBackgroundColour(wx.WHITE)
        browseButton = wx.Button(self.control, -1, 'B&rowse')
        sizer = wx.BoxSizer(wx.VERTICAL)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(wx.StaticText(self.control, -1, 'To dir:'), 0, wx.RIGHT | wx.ALIGN_CENTRE_VERTICAL, 5)
        hsizer.Add(self.destinationDirField, 1, wx.ALL | wx.GROW | wx.ALIGN_CENTRE_VERTICAL)
        hsizer.Add(browseButton, 0, wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, 5)
        sizer.Add(hsizer, 0, wx.ALL | wx.GROW, 5)
        self.control.SetSizer(sizer)
        self.control.SetAutoLayout(True)
        self.control.Bind(wx.EVT_TEXT, self.OnUpdateText, self.destinationDirField)
        self.control.Bind(wx.EVT_BUTTON, self.OnBrowseButton, browseButton)
        self.updateControls()
        return self.control

    def OnBrowseButton(self, event):
        dlg = wx.DirDialog(self.control)
        if dlg.ShowModal() == wx.ID_OK:
            self.destinationDirField.SetValue(dlg.GetPath())
        del dlg

    def OnUpdateText(self, event):
        event.Skip()
        self.updateControls()

    def validName(self, name):
        name = name.strip()
        if len(name) == 0:
            return False
        rp = os.path.expanduser(name)
        return os.path.exists(rp) and os.path.isdir(rp)

    def projectExists(self, name):
        project = plugins.resources.resources.getDefault().getWorkspace().getProject(name)
        return project.exists()

    def updateValidControls(self, valid):
        self.setFinished(valid)
        self.setPageComplete(valid)

    def updateControls(self):
        name = self.destinationDirField.GetValue().strip()
        if len(name) == 0:
            self.updateValidControls(False)
            self.setErrorMessage(None)
            return
        if not self.validName(name):
            self.updateValidControls(False)
            self.setErrorMessage('Invalid name')
            return
        self.updateValidControls(True)
        self.setErrorMessage(None)
        return
