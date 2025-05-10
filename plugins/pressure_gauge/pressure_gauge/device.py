# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/pressure_gauge/src/pressure_gauge/device.py
# Compiled at: 2004-11-11 02:37:26
import wx, wx.lib.masked.timectrl as timectrl, wx.lib.colourselect as colourselect, traceback, threading, pressure_gauge, pressure_gauge.stepentry, hardware.hardwaremanager, core.device, poi.utils.scrolledpanel, logging, ui.context, pressure_gauge.messages as messages
logger = logging.getLogger('pressure_gauge.userinterface')
DEVICE_ID = 'pressure_gauge'

def parseColor(colorStr):
    return apply(wx.Color, map(int, colorStr.split(',')))


class PressureGaugeDeviceEditor(core.device.DeviceEditor):
    __module__ = __name__

    def __init__(self):
        self.device = None
        core.device.DeviceEditor.__init__(self)
        self.currentHardwareEditor = None
        return

    def createControl(self, parent):
        self.control = poi.utils.scrolledpanel.ScrolledPanel(parent, -1)
        uibox = self.createUIBox()
        hwbox = self.createHardwareBox()
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(uibox, 0, wx.GROW | wx.ALL, 5)
        sizer.Add(hwbox, 0, wx.GROW | wx.ALL, 5)
        self.control.SetSizer(sizer)
        self.control.SetAutoLayout(True)
        self.control.SetupScrolling()
        return self.control

    def getHardwareChoices(self):
        choices = []
        hw = hardware.hardwaremanager.getHardware()
        for item in hw:
            hwtype = hardware.hardwaremanager.getHardwareType(item.getHardwareType())
            deviceTypes = hwtype.getDeviceTypes()
            for dtype in deviceTypes:
                if dtype == 'pressure_gauge':
                    choices.append(item)

        return choices

    def createHardwareBox(self):
        sbox = wx.StaticBox(self.control, -1, messages.get('device.config.hardwarebox.label'), size=(-1, 200))
        ssizer = wx.StaticBoxSizer(sbox, wx.VERTICAL)
        fsizer = wx.FlexGridSizer(0, 2, 5, 5)
        fsizer.AddGrowableCol(1)
        label = wx.StaticText(self.control, -1, messages.get('device.config.hardware.label'))
        hwchoices = self.getHardwareChoices()
        choices = []
        for choice in hwchoices:
            choices.append(choice.getName())

        self.hardwareChoice = wx.ComboBox(self.control, -1, choices=choices, style=wx.CB_READONLY)
        fsizer.Add(label, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL, 5)
        fsizer.Add(self.hardwareChoice, 1, wx.ALIGN_CENTRE_VERTICAL)
        self.control.Bind(wx.EVT_COMBOBOX, self.OnHardwareChoice, self.hardwareChoice)
        ssizer.Add(fsizer, 0, wx.GROW | wx.TOP, 10)
        ssizer.Add(wx.StaticLine(self.control, -1), 0, wx.GROW | wx.ALL, 5)
        self.hardwarePanel = wx.Panel(self.control, -1)
        self.hardwarePanel.SetSizer(wx.BoxSizer(wx.VERTICAL))
        self.hardwarePanel.SetAutoLayout(True)
        ssizer.Add(self.hardwarePanel, 1, wx.GROW | wx.ALL, 5)
        return ssizer

    def OnHardwareChoice(self, event):
        """
        When a selection is made from the drop down then
        get the name of the hardware and set the editor for that 
        device
        """
        choices = self.getHardwareChoices()
        choiceIdx = self.hardwareChoice.GetSelection()
        choice = choices[choiceIdx]
        self.description = choice
        self.selectHardware(choice.getName())

    def update(self):
        pass

    def createUIBox(self):
        sbox = wx.StaticBox(self.control, -1, ' User Interface ')
        ssizer = wx.StaticBoxSizer(sbox, wx.VERTICAL)
        fsizer = wx.FlexGridSizer(0, 2, 5, 5)
        fsizer.AddGrowableCol(1)
        label = wx.StaticText(self.control, -1, 'Label:')
        self.labelField = wx.TextCtrl(self.control, -1, '')
        fsizer.Add(label, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
        fsizer.Add(self.labelField, 1, wx.GROW | wx.ALIGN_CENTRE_VERTICAL)
        ssizer.Add(fsizer, 0, wx.GROW | wx.TOP, 10)
        return ssizer

    def setData(self, data):
        """Put data from node into widgets"""
        self.device = data
        uihints = data.getUIHints()
        hwhints = data.getHardwareHints()
        try:
            hwid = hwhints.getChildNamed('id').getValue()
            self.selectHardware(hwid)
        except Exception as msg:
            logger.exception(msg)
            logger.warning('Cannot set hardware: %s' % msg)

        try:
            label = uihints.getChildNamed('label').getValue()
            self.labelField.SetValue(label)
        except Exception as msg:
            logger.exception(msg)
            logger.warning('Cannot set hardware: %s' % msg)

        self.update()
        if self.currentHardwareEditor is not None:
            self.currentHardwareEditor.setData(None, hwhints)
        return

    def getHardwareChoicesName(self):
        choices = self.getHardwareChoices()
        return map((lambda p: p.getName()), choices)

    def selectHardware(self, hwid):
        try:
            idx = self.getHardwareChoicesName().index(hwid)
            self.hardwareChoice.SetSelection(idx)
        except Exception as msg:
            logger.exception(msg)

        description = hardware.hardwaremanager.getHardwareByName(hwid)
        hwtype = hardware.hardwaremanager.getHardwareType(description.getHardwareType())
        self.description = description
        self.setHardwareEditor(hwtype.getDeviceHardwareEditor())

    def getSelectedHardwareInstance(self):
        s = self.getHardwareChoicesName()[self.hardwareChoice.GetSelection()]
        return s

    def removeHardwareEditor(self):
        sizer = self.hardwarePanel.GetSizer()
        for child in self.hardwarePanel.GetChildren():
            self.hardwarePanel.RemoveChild(child)
            sizer.Remove(child)
            child.Destroy()

    def modified(self):
        pass

    def setHardwareEditor(self, editor):
        self.removeHardwareEditor()

    def getData(self, data):
        """put data into the node"""
        try:
            hwhints = data.getHardwareHints()
            uihints = data.getUIHints()
            vname = self.getHardwareChoices()[self.hardwareChoice.GetSelection()].getName()
            label = self.labelField.GetValue()
            hwhints.createChildIfNotExists('id').setValue(vname)
            uihints.createChildIfNotExists('label').setValue(label)
            if self.currentHardwareEditor is not None:
                self.currentHardwareEditor.getData(hwhints)
        except Exception as msg:
            logger.exception(msg)
            logger.error("Unable to save device data to recipe: '%s'" % msg)

        return


class PressureGaugeDevice(core.device.Device):
    __module__ = __name__

    def __init__(self):
        global DEVICE_ID
        core.device.Device.__init__(self, DEVICE_ID)

    def getDeviceStr(self):
        try:
            hwhints = self.getHardwareHints()
            hardwareName = hwhints.getChildNamed('id').getValue()
            description = hardware.hardwaremanager.getHardwareByName(hardwareName)
            hwtype = description.getHardwareType()
            hwtype = hardware.hardwaremanager.getHardwareType(hwtype)
            description = hwtype.getDescription()
            return '%s (%s)' % (hardwareName, description)
        except Exception as msg:
            print('* WARNING:', msg)

        return '*NOT CONFIGURED*'

    def configurationUpdated(self):
        core.device.Device.configurationUpdated(self)
        hwhints = self.getHardwareHints()

    def updateUIHints(self):
        core.device.Device.updateUIHints(self)
        uihints = self.getUIHints()

    def parseFromNode(self, node):
        result = pressure_gauge.stepentry.parseFromNode(node)
        self.configurationUpdated()
        return result

    def convertToNode(self, root):
        core.device.Device.convertToNode(self, root)

    def createNewStepEntry(self, fromExisting=None):
        if fromExisting is not None:
            return fromExisting.clone()
        return pressure_gauge.stepentry.PressureGaugeStepEntry()
        return

    def getDeviceEditor(self):
        return PressureGaugeDeviceEditor()
