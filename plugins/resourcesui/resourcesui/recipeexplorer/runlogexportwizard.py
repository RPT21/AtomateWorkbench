# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/resourcesui/src/resourcesui/recipeexplorer/runlogexportwizard.py
# Compiled at: 2004-11-04 02:42:23
import re, wx, sys, os, plugins.ui.ui, threading, plugins.poi.poi.wizards, plugins.poi.poi.operation, plugins.poi.poi.dialogs
import plugins.poi.poi.dialogs.progress, plugins.poi.poi.views.viewers, plugins.poi.poi.views, plugins.resources.resources
import plugins.resourcesui.resourcesui.messages as messages, plugins.resourcesui.resourcesui.actions, logging, shutil
logger = logging.getLogger('resourcesui.exportrunlogwizard')

class ExportRunlogWizard(plugins.poi.poi.wizards.Wizard):
    __module__ = __name__

    def __init__(self):
        plugins.poi.poi.wizards.Wizard.__init__(self)
        self.runlog = None
        return

    def setRunlog(self, runlog):
        self.runlog = runlog

    def setResource(self, resource):
        pass

    def addPages(self):
        firstPage = FirstRecipeWizardPage()
        self.addPage(firstPage)
        self.setStartingPage(firstPage)

    def createControl(self, parent):
        plugins.poi.poi.wizards.Wizard.createControl(self, parent)
        self.control.SetSize((600, 600))
        self.control.CentreOnScreen()

    def createBody(self, parent):
        pass


class FirstRecipeWizardPage(plugins.poi.poi.wizards.WizardPage):
    __module__ = __name__

    def __init__(self):
        plugins.poi.poi.wizards.WizardPage.__init__(self, 'first', 'Export Recipe')
        self.setMessage('Select Destination')
        self.setDescription('Click browse to select a destination for the runlog')
        self.runlog = None
        return

    def performFinish(self):
        fname = self.fixName(self.getFullName())
        srcfilename = self.runlog.getLocation()
        try:
            shutil.copy2(srcfilename, fname)
        except Exception as msg:
            dlg = plugins.poi.poi.dialogs.MessageDialog(plugins.ui.ui.getDefault().getMainFrame().getControl(), str(msg), 'Error exporting log', wx.ICON_ERROR | wx.OK)
            dlg.ShowModal()
            dlg.Destroy()

    def createControl(self, composite):
        self.control = wx.Panel(composite, -1, size=wx.Size(100, 100))
        self.destinationDirField = wx.TextCtrl(self.control, -1)
        self.destinationDirField.SetBackgroundColour(wx.WHITE)
        browseButton = wx.Button(self.control, -1, 'B&rowse')
        sizer = wx.BoxSizer(wx.VERTICAL)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(wx.StaticText(self.control, -1, 'To dir:'), 0, wx.RIGHT | wx.ALIGN_CENTRE_VERTICAL, 5)
        hsizer.Add(self.destinationDirField, 1, wx.ALL | wx.EXPAND | wx.ALIGN_CENTRE_VERTICAL)
        hsizer.Add(browseButton, 0, wx.LEFT | wx.ALIGN_CENTRE_VERTICAL, 5)
        sizer.Add(hsizer, 0, wx.ALL | wx.EXPAND, 5)
        self.control.SetSizer(sizer)
        self.control.SetAutoLayout(True)
        self.control.Bind(wx.EVT_TEXT, self.OnUpdateText, self.destinationDirField)
        self.control.Bind(wx.EVT_BUTTON, self.OnBrowseButton, browseButton)
        self.updateControls()
        return self.control

    def OnBrowseButton(self, event):
        self.runlog = self.wizard.runlog
        dlg = wx.FileDialog(self.control, defaultFile='runlog_%s.log' % self.runlog.getParent().getProject().getName())
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
        filename = os.path.basename(rp)
        cmp = re.compile(validchars)
        m = cmp.match(filename)
        if m is not None:
            return False
        return True

    def getFullName(self):
        name = self.destinationDirField.GetValue().strip()
        name = name.strip()
        if len(name) == 0:
            return False
        rp = os.path.expanduser(name)
        return rp

    def fixName(self, name):
        filename = self.getFullName()
        name = os.path.basename(filename)
        dirname = os.path.dirname(filename)
        (prefix, ext) = os.path.splitext(name)
        ext = ext.lower()
        return filename

    def fileExists(self, name):
        filename = self.getFullName()
        return os.path.exists(filename)

    def updateValidControls(self, valid):
        self.setFinished(valid)
        self.setPageComplete(valid)

    def updateControls(self):
        name = self.destinationDirField.GetValue().strip()
        if len(name) == 0:
            self.updateValidControls(False)
            self.setErrorMessage(None)
            return
        if self.fileExists(name):
            self.updateValidControls(False)
            self.setErrorMessage('The file already exists.  Select a different name')
            return
        self.updateValidControls(True)
        self.setErrorMessage(None)
        return
