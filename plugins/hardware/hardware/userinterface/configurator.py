# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/hardware/src/hardware/userinterface/configurator.py
# Compiled at: 2005-06-10 18:51:17
import wx, os, sys, string, ConfigParser, kernel, hardware, hardware.hardwaremanager, logging, poi.dialogs, poi.views, hardware.images as images
DIALOG_PREFS_FILE = 'hwconfig.prefs'
import poi.views.contentprovider, hardware.newhardwarewizard
logger = logging.getLogger('hardware.configuration')

class ConfiguredHardwareLabelProvider(poi.views.contentprovider.LabelProvider):
    __module__ = __name__

    def __init__(self):
        poi.views.contentprovider.LabelProvider.__init__(self)

    def getImage(self, element):
        return None
        return

    def getText(self, element):
        instance = element.getInstance()
        if instance is not None:
            status = instance.getStatusText()
        else:
            status = 'not initialized'
        htype = hardware.hardwaremanager.getHardwareType(element.getHardwareType())
        return string.join([element.getName(), status, htype.getDescription()], ' - ')
        return


class ConfiguredHardwareContentProvider(poi.views.contentprovider.ContentProvider):
    __module__ = __name__

    def __init__(self):
        poi.views.contentprovider.ContentProvider.__init__(self)
        self.tinput = None
        return

    def inputChanged(self, viewer, oldInput, newInput):
        if self.tinput != newInput and newInput != None:
            self.tinput = newInput
        if viewer != None:
            viewer.refresh()
        return

    def getElements(self, inputElement):
        return self.tinput.getHardware()


class ConfigurationPage(object):
    __module__ = __name__

    def __init__(self):
        self.control = None
        self.description = None
        self.dirty = False
        self.owner = None
        return

    def setOwner(self, owner):
        self.owner = owner

    def setDirty(self, dirty):
        self.dirty = dirty
        if self.owner is not None:
            self.owner.updateButtons()
        return

    def isDirty(self):
        return self.dirty

    def createControl(self, parent):
        pass

    def getControl(self):
        return self.control

    def setDescription(self, description):
        self.description = description
        inst = self.description.getInstance()
        if inst is not None:
            inst.addHardwareStatusListener(self)
            inst.addHardwareEventListener(self)
        return

    def hardwareStatusChanged(self, hardware):
        """Update all hardwares"""
        wx.CallAfter(self.OnHardwareStatusChanged, hardware)

    def hardwareEvent(self, event):
        pass

    def OnHardwareStatusChanged(self, hardware):
        pass

    def getDescription(self):
        return self.description

    def setData(self, config):
        pass

    def getData(self, config):
        pass

    def closing(self):
        pass

    def applied(self):
        """Called by the configurator when either the Apply or OK button were pressed"""
        pass

    def dispose(self):
        logger.debug('removing self as status listener: %s' % self)
        inst = self.description.getInstance()
        if inst is not None:
            inst.removeHardwareStatusListener(self)
            inst.removeHardwareEventListener(self)
        return


class NoConfigurationPage(ConfigurationPage):
    __module__ = __name__

    def createControl(self, parent):
        self.control = wx.Panel(parent, -1)
        return self.control

    def dispose(self):
        ConfigurationPage.dispose(self)
        self.control.Destroy()


class HardwareConfigurator(poi.dialogs.MessageHeaderDialog):
    __module__ = __name__

    def __init__(self):
        poi.dialogs.MessageHeaderDialog.__init__(self, image=images.getImage(images.CONFIG_WIZARD))
        self.control = None
        self.setSaveLayout(True)
        self.counts = 0
        self.setStyle(wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.oldSelection = None
        self.currentPage = None
        hardware.hardwaremanager.addHardwareManagerListener(self)
        return

    def dispose(self):
        hardware.hardwaremanager.removeHardwareManagerListener(self)

    def hardwareManagerUpdated(self):
        self.updateInput()

    def hardwareStatusChanged(self, hardware):
        self.viewer.refresh()

    def updateInput(self):
        hw = hardware.hardwaremanager.getHardware()
        for item in hw:
            inst = item.getInstance()
            if inst is not None:
                inst.addHardwareStatusListener(self)

        self.viewer.setInput(hardware.hardwaremanager)
        return

    def createBody(self, parent):
        win = wx.Panel(parent, -1, style=0)
        self.stage = win
        left = wx.Panel(self.stage, -1)
        left.SetSize((200, 100))
        self.newButton = wx.Button(left, -1, '&New')
        self.deleteButton = wx.Button(left, -1, '&Delete')
        self.deleteButton.Enable(False)
        left.Bind(wx.EVT_BUTTON, self.OnNewButton, id=self.newButton.GetId())
        left.Bind(wx.EVT_BUTTON, self.OnDeleteButton, id=self.deleteButton.GetId())
        self.viewer = poi.views.viewers.TableViewer(left)
        control = self.viewer.getControl()
        control.InsertColumn(0, 'Hardware')
        self.viewer.setContentProvider(ConfiguredHardwareContentProvider())
        self.viewer.setLabelProvider(ConfiguredHardwareLabelProvider())
        self.viewer.setInput(hardware.hardwaremanager)
        self.updateInput()

        class HardwareListEventHandler(object):
            __module__ = __name__

            def handleSelectionChanged(innerself, selection):
                self.handleHardwareSelectionChanged(selection)

        eventHandler = HardwareListEventHandler()
        self.viewer.addSelectionChangedListener(eventHandler)
        self.configBody = wx.Panel(self.stage, -1, style=0)
        self.configBody.SetSizer(wx.BoxSizer(wx.VERTICAL))
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(control, 1, wx.GROW)
        hbsizer = wx.BoxSizer(wx.HORIZONTAL)
        hbsizer.Add(self.newButton, 0, wx.RIGHT, 5)
        hbsizer.Add(self.deleteButton, 0)
        sizer.Add(hbsizer, 0, wx.GROW | wx.ALIGN_CENTRE_HORIZONTAL | wx.ALL, 0)
        left.SetSizer(sizer)
        left.SetAutoLayout(True)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(left, 0, wx.GROW)
        sizer.Add(self.configBody, 1, wx.GROW)
        mainsizer = wx.BoxSizer(wx.VERTICAL)
        mainsizer.Add(sizer, 1, wx.GROW | wx.ALL, 0)
        mainsizer.Add(wx.StaticLine(self.stage, -1), 0, wx.GROW | wx.TOP | wx.BOTTOM, 5)
        self.applyButton = wx.Button(self.stage, -1, '&Apply')
        self.cancelButton = wx.Button(self.stage, wx.ID_CANCEL, '&Cancel')
        self.okButton = wx.Button(self.stage, -1, '&OK')
        self.applyButton.Enable(False)
        self.stage.Bind(wx.EVT_BUTTON, self.OnApplyButton, self.applyButton)
        self.stage.Bind(wx.EVT_BUTTON, self.OnCancelButton, self.cancelButton)
        self.stage.Bind(wx.EVT_BUTTON, self.OnOKButton, self.okButton)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(self.applyButton, 0, wx.RIGHT, 20)
        hsizer.Add(self.cancelButton, 0, wx.RIGHT, 5)
        hsizer.Add(self.okButton, 0, wx.RIGHT, 5)
        mainsizer.Add(hsizer, 0, wx.BOTTOM | wx.ALIGN_RIGHT, 10)
        self.stage.SetSizer(mainsizer)
        self.stage.SetAutoLayout(True)
        self.setTitle('Hardware Configuration')
        self.setMessage('Hardware Configuration')
        self.setInfo('Manage the hardware installed on your system')
        self.showNoConfigBody()
        self.restoreLayout()

    def OnApplyButton(self, event):
        self.saveCurrentPageData()
        self.updateButtons()

    def saveCurrentPageData(self):
        hw = self.oldSelection
        if hw is None:
            return
        if self.currentPage is None:
            return
        config = hw.getConfiguration()
        try:
            self.currentPage.getData(config)
            hardware.hardwaremanager.save(hw)
        except Exception, msg:
            print '* ERROR: Unable to save hardware configuration:', msg
            dlg = poi.dialogs.MessageDialog(self.control, 'Error:\n\n%s' % msg, 'Configuration Error', style=wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return

        print 'porkus, saying what: ', self.currentPage
        self.currentPage.applied()
        self.currentPage.setDirty(False)
        return

    def OnCancelButton(self, event):
        self.endModal(wx.ID_CANCEL)

    def OnOKButton(self, event):
        self.saveCurrentPageData()
        self.endModal(wx.ID_OK)

    def handleClosing(self, id):
        self.internalClose()

    def updateButtons(self):
        self.setCanApply(self.currentPage.isDirty())

    def setCanApply(self, canit):
        self.applyButton.Enable(canit)

    def OnDeleteButton(self, event):
        selected = self.viewer.getSelection()[0]
        dlg = wx.MessageDialog(self.control, "Are you sure you want to '%s'?" % selected.getName(), 'Delete Hardware', wx.YES_NO | wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.ID_NO:
            return
        hardware.hardwaremanager.delete(selected)
        self.removeCurrentConfigPage()
        self.showNoConfigBody()
        if len(hardware.hardwaremanager.getHardware()) == 0:
            self.removeCurrentConfigPage()

    def OnNewButton(self, event):
        dlg = hardware.newhardwarewizard.NewHardwareWizard()
        dlg.createControl(self.control)
        if dlg.showModal() == wx.ID_OK:
            description = dlg.getHardware()
            self.selectAndReveal(description)

    def selectAndReveal(self, description):
        self.viewer.selectAndReveal(description)

    def showNoConfigBody(self):
        page = NoConfigurationPage()
        self.showConfigPage(page)
        self.currentPage = None
        return

    def showConfigPage(self, configPage):
        self.removeCurrentConfigPage()
        selection = self.viewer.getSelection()
        config = None
        if len(selection) > 0:
            selection = selection[0]
            config = selection.getConfiguration()
            configPage.createControl(self.configBody)
            configPage.setDescription(selection)
            configPage.setData(config)
            configPage.setOwner(self)
            self.configBody.GetSizer().Add(configPage.getControl(), 1, wx.GROW | wx.ALL, 5)
            self.configBody.GetSizer().Layout()
        self.currentPage = configPage
        self.configBody.Show()
        self.setCanApply(False)
        return

    def removeCurrentConfigPage(self):
        self.configBody.Hide()
        for child in self.configBody.GetChildren():
            self.configBody.RemoveChild(child)
            self.configBody.GetSizer().Remove(child)
            if self.currentPage is not None:
                self.currentPage.dispose()
                self.currentPage = None

        self.configBody.Show()
        return

    def performPageChange(self, hw):
        if self.currentPage is None:
            return
        if not self.currentPage.isDirty():
            return
        self.saveCurrentPageData()
        return

    def handleHardwareSelectionChanged(self, selection):
        self.deleteButton.Enable(len(selection) != 0)
        if self.oldSelection is not None:
            self.performPageChange(self.oldSelection)
        if len(selection) == 0:
            self.oldSelection = None
            return
        selection = selection[0]
        self.oldSelection = selection
        hwtypestr = selection.getHardwareType()
        hwtype = hardware.hardwaremanager.getHardwareType(hwtypestr)
        configPage = hwtype.getConfigurationPage()
        if configPage == None:
            self.showNoConfigBody()
            return
        self.showConfigPage(configPage)
        return

    def getMementoID(self):
        global DIALOG_PREFS_FILE
        return DIALOG_PREFS_FILE

    def fillLayoutMemento(self, memento):
        size = self.control.GetSize()
        memento.set('layout', 'size', '%s,%s' % (size[0], size[1]))

    def createDefaultLayout(self):
        self.control.SetSize((600, 600))
        self.control.CentreOnScreen()

    def restoreLayoutFromMemento(self, memento):
        size = map(int, tuple(memento.get('layout', 'size').split(',')))
        self.control.SetSize(size)
        self.control.CentreOnScreen()

    def closing(self):
        self.internalClose()

    def internalClose(self):
        if self.currentPage is None:
            return
        if self.oldSelection is not None:
            self.performPageChange(self.oldSelection)
            self.removeCurrentConfigPage()
        hardwares = hardware.hardwaremanager.getHardware()
        for item in hardwares:
            inst = item.getInstance()
            if inst is not None:
                inst.removeHardwareStatusListener(self)

        return
