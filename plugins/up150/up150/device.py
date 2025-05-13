# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: /home/maldoror/apps/eclipse/workspace/com.atomate.workbench/plugins/up150/src/up150/device.py
# Compiled at: 2004-08-12 02:18:21
import traceback, wx, up150, up150.stepentry, hardware.hardwaremanager, core.device
DEVICE_ID = 'up150'

class UP150DeviceEditor(core.device.DeviceEditor):
    __module__ = __name__

    def __init__(self):
        core.device.DeviceEditor.__init__(self)
        self.currentHardwareEditor = None
        return

    def createControl(self, parent):
        self.control = wx.Panel(parent, -1)
        uibox = self.createUIBox()
        hwbox = self.createHardwareBox()
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddSizer(uibox, 0, wx.EXPAND | wx.ALL, 5)
        sizer.AddSizer(hwbox, 0, wx.EXPAND | wx.ALL, 5)
        self.control.SetSizer(sizer)
        return self.control

    def getHardwareChoices(self):
        global DEVICE_ID
        choices = []
        hw = hardware.hardwaremanager.getHardware()
        for item in hw:
            hwtype = hardware.hardwaremanager.getHardwareType(item.getHardwareType())
            deviceTypes = hwtype.getDeviceTypes()
            if deviceTypes.count(DEVICE_ID) > 0:
                choices.append(item)

        return choices

    def createHardwareBox(self):
        sbox = wx.StaticBox(self.control, -1, ' Hardware ')
        ssizer = wx.StaticBoxSizer(sbox, wx.VERTICAL)
        fsizer = wx.FlexGridSizer(0, 2, 5, 5)
        fsizer.AddGrowableCol(1)
        label = wx.StaticText(self.control, -1, 'Hardware')
        hwchoices = self.getHardwareChoices()
        choices = []
        for choice in hwchoices:
            choices.append(choice.getName())

        self.hardwareChoice = wx.Choice(self.control, -1, choices=choices)
        fsizer.Add(label, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL | wx.RIGHT, 5)
        fsizer.Add(self.hardwareChoice, 1, wx.ALIGN_CENTRE_VERTICAL)
        self.control.Bind(wx.EVT_CHOICE, self.OnHardwareChoice, self.hardwareChoice)
        ssizer.Add(fsizer, 0, wx.EXPAND | wx.TOP, 10)
        ssizer.Add(wx.StaticLine(self.control, -1), 0, wx.EXPAND | wx.ALL, 5)
        self.hardwarePanel = wx.Panel(self.control, -1, size=wx.Size(300, 300))
        self.hardwarePanel.SetSizer(wx.BoxSizer(wx.VERTICAL))
        ssizer.Add(self.hardwarePanel, 1, wx.EXPAND | wx.ALL, 5)
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

    def createUIBox(self):
        sbox = wx.StaticBox(self.control, -1, ' User Interface ')
        ssizer = wx.StaticBoxSizer(sbox, wx.VERTICAL)
        fsizer = wx.FlexGridSizer(0, 2, 5, 5)
        fsizer.AddGrowableCol(1)
        label = wx.StaticText(self.control, -1, 'Label:')
        self.labelField = wx.TextCtrl(self.control, -1, '')
        fsizer.Add(label, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
        fsizer.Add(self.labelField, 1, wx.ALIGN_CENTRE_VERTICAL)
        ssizer.Add(fsizer, 1, wx.EXPAND | wx.TOP, 10)
        return ssizer

    def setData(self, data):
        uihints = data.getUIHints()
        hwhints = data.getHardwareHints()
        try:
            hwid = hwhints.getChildNamed('id').getValue()
            self.selectHardware(hwid)
        except Exception as msg:
            traceback.print_exc()
            print(('* WARNING: Cannot set hardware:', msg))

        try:
            label = uihints.getChildNamed('label').getValue()
            self.labelField.SetValue(label)
        except Exception as msg:
            traceback.print_exc()
            print(('* WARNING: Cannot set hardware:', msg))

        if self.currentHardwareEditor is not None:
            self.currentHardwareEditor.setData(None, hwhints)
        return

    def selectHardware(self, hwid):
        self.hardwareChoice.SetStringSelection(hwid)
        description = hardware.hardwaremanager.getHardwareByName(hwid)
        hwtype = hardware.hardwaremanager.getHardwareType(description.getHardwareType())
        self.description = description
        self.setHardwareEditor(hwtype.getDeviceHardwareEditor())

    def removeHardwareEditor(self):
        sizer = self.hardwarePanel.GetSizer()
        for child in self.hardwarePanel.GetChildren():
            self.hardwarePanel.Remove(child)
            sizer.Remove(child)
            child.Destroy()

    def setHardwareEditor(self, editor):
        print(('set hardare editor', editor))
        self.removeHardwareEditor()
        editor.setInstance(self.description.getInstance())
        editor.createControl(self.hardwarePanel)
        sizer = self.hardwarePanel.GetSizer()
        sizer.Add(editor.getControl(), 1, wx.EXPAND | wx.ALL, 0)
        sizer.Layout()
        self.currentHardwareEditor = editor

    def getData(self, data):
        try:
            hwhints = data.getHardwareHints()
            uihints = data.getUIHints()
            vname = self.hardwareChoice.GetStringSelection()
            label = self.labelField.GetValue()
            hwhints.createChildIfNotExists('id').setValue(vname)
            uihints.createChildIfNotExists('label').setValue(label)
            if self.currentHardwareEditor is not None:
                self.currentHardwareEditor.getData(hwhints)
        except Exception as msg:
            print(('* ERROR:', msg))

        return


class UP150Device(core.device.Device):
    __module__ = __name__

    def __init__(self):
        core.device.Device.__init__(self, DEVICE_ID)

    def getDeviceStr(self):
        try:
            hwhints = self.getHardwareHints()
            hardwareName = hwhints.getChildNamed('id').getValue()
            hardwareAddress = hwhints.getChildNamed('address').getValue()
            description = hardware.hardwaremanager.getHardwareByName(hardwareName)
            hwtype = description.getHardwareType()
            hwtype = hardware.hardwaremanager.getHardwareType(hwtype)
            description = hwtype.getDescription()
            return '%s (%s) - address %s' % (hardwareName, description, hardwareAddress)
        except Exception as msg:
            print(('* WARNING:', msg))

        return '*NOT CONFIGURED*'

    def configurationUpdated(self):
        core.device.Device.configurationUpdated(self)

    def parseFromNode(self, node):
        return up150.stepentry.parseFromNode(node)

    def convertToNode(self, root):
        core.device.Device.convertToNode(self, root)

    def createNewStepEntry(self, fromExisting=None):
        if fromExisting is not None:
            return fromExisting.clone()
        return up150.stepentry.UP150StepEntry()
        return

    def getDeviceEditor(self):
        return UP150DeviceEditor()
