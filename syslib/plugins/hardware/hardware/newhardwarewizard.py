# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/hardware/src/hardware/newhardwarewizard.py
# Compiled at: 2005-06-10 18:51:17
import wx, sys, os, poi.wizards, poi.views.viewers, poi.views, logging, poi.views.contentprovider, hardware.hardwaremanager
logger = logging.getLogger('hardware.ui')

class NewHardwareWizard(poi.wizards.Wizard):
    __module__ = __name__

    def __init__(self):
        poi.wizards.Wizard.__init__(self)
        self.hardware = None
        return

    def addPages(self):
        pageOne = HardwareTypeSelectionPage()
        pageTwo = NameHardwarePage()
        self.addPage(pageOne)
        self.setStartingPage(pageOne)

    def createControl(self, parent):
        poi.wizards.Wizard.createControl(self, parent)
        self.control.SetSize((600, 600))
        self.control.CentreOnScreen()

    def createBody(self, parent):
        pass

    def setHardware(self, hardware):
        self.hardware = hardware

    def getHardware(self):
        return self.hardware


class LabelProvider(poi.views.contentprovider.LabelProvider):
    __module__ = __name__

    def __init__(self):
        poi.views.contentprovider.LabelProvider.__init__(self)

    def getImage(self, element):
        return None
        return

    def getText(self, element):
        """
        instance = element.getInstance()
        if instance is not None:
            status = instance.getStatusText()
        else:
            status = "not initialized"
        
        htype = hardware.hardwaremanager.getHardwareType(element.getHardwareType())

        return string.join( [element.getName(), status, htype.getDescription()], " - " ) 
        """
        return '%s - %s' % (element.getType(), element.getDescription())


class NameHardwarePage(poi.wizards.WizardPage):
    __module__ = __name__

    def __init__(self):
        poi.wizards.WizardPage.__init__(self, 'name', 'Hardware Name')
        self.setMessage('Hardware Identification')
        self.setInfo('Enter a name to uniquely identify the hardware device')

    def createControl(self, composite):
        self.control = wx.Panel(composite, -1, size=(100, 100))
        self.setPageComplete(True)
        return self.control


class HardwareTypeSelectionPage(poi.wizards.WizardPage):
    __module__ = __name__

    def __init__(self):
        poi.wizards.WizardPage.__init__(self, 'typeselection', 'Hardware Selection')
        self.setMessage('Hardware Selection')
        self.setInfo('Please select the type of hardware to install')
        self.canFlip = False

    def createControl(self, composite):
        self.control = wx.Panel(composite, -1, size=(100, 100))
        self.infopane = wx.Panel(self.control, -1)
        nameGroup = wx.Panel(self.control, -1)
        label = wx.StaticText(nameGroup, -1, 'Name:')
        self.nameField = wx.TextCtrl(nameGroup, -1, '')
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(label, 0, wx.GROW | wx.RIGHT | wx.ALIGN_CENTRE_VERTICAL, 5)
        sizer.Add(self.nameField, 1, wx.GROW | wx.ALIGN_CENTRE_VERTICAL, 0)
        nameGroup.SetSizer(sizer)
        nameGroup.SetAutoLayout(True)
        self.nameField.Enable(False)
        wx.EVT_TEXT(composite, self.nameField.GetId(), self.OnNameFieldChange)
        self.viewer = poi.views.viewers.TableViewer(self.control)
        self.viewer.setContentProvider(hardware.userinterface.HardwareTypesContentProvider())
        self.viewer.setLabelProvider(hardware.userinterface.HardwareTypesLabelProvider())
        listcontrol = self.viewer.getControl()
        listcontrol.InsertColumn(0, 'Available Hardware')
        self.viewer.setLabelProvider(LabelProvider())
        self.viewer.setInput(hardware.hardwaremanager)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(nameGroup, 0, wx.GROW | wx.ALL, 5)
        sizer.Add(listcontrol, 1, wx.GROW | wx.ALL, 5)
        sizer.Add(self.infopane, 1, wx.GROW | wx.ALL, 5)
        self.control.SetSizer(sizer)

        class HardwareListEventHandler(object):
            __module__ = __name__

            def handleSelectionChanged(innerself, selection):
                self.handleHardwareTypeSelectionChanged(selection)

        eventHandler = HardwareListEventHandler()
        self.viewer.addSelectionChangedListener(eventHandler)
        self.setPageComplete(False)
        return self.control

    def OnNameFieldChange(self, event):
        self.validateName()

    def handleHardwareTypeSelectionChanged(self, selection):
        self.nameField.Enable(len(selection) > 0)
        self.validateName()

    def getConfiguredNames(self):
        hw = hardware.hardwaremanager.getHardware()
        hn = []
        for item in hw:
            hn.append(item.getName())

        return hn

    def validateName(self):
        name = self.nameField.GetValue()
        if len(name) == 0:
            self.canFlip = False
            self.setPageComplete(self.canFlip)
            self.getWizard().update()
            return
        if name in self.getConfiguredNames():
            self.canFlip = False
            self.setPageComplete(self.canFlip)
            self.getWizard().update()
            return
        notallowed = '*/.-\\!@#$%^&*()<>?;:\'"[]{}'
        for char in notallowed:
            if name.find(char) >= 0:
                self.canFlip = False
                self.setPageComplete(self.canFlip)
                self.getWizard().update()
                return

        self.canFlip = len(self.viewer.getSelection()) != 0
        self.setPageComplete(self.canFlip)

    def canFlipToNextPage(self):
        return False

    def performFinish(self):
        """Creates the configuration as specified"""
        global logger
        name = self.nameField.GetValue()
        hardwareType = self.viewer.getSelection()[0]
        logger.debug("Creating hardware of type '%s'" % hardwareType)
        try:
            hw = hardware.hardwaremanager.create(name, hardwareType)
            self.getWizard().setHardware(hw)
        except Exception, msg:
            logger.exception(msg)
            logger.error("Cannot create hardware configuration for '%s'/'%s':'%s'" % (name, str(hardwareType), msg))
            return
