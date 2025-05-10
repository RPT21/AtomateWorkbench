# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/mfc/src/mfc/device.py
# Compiled at: 2004-11-19 02:41:21
import wx, wx.lib.masked.timectrl as timectrl, wx.lib.colourselect as colourselect, traceback, threading, mfc, mfc.stepentry, mfc.widgets, hardware.hardwaremanager, core.device, poi.utils.scrolledpanel, logging, ui.context, mfc.messages as messages
logger = logging.getLogger('mfc.userinterface')
DEVICE_ID = 'mfc'

def parseColor(colorStr):
    return apply(wx.Color, map(int, colorStr.split(',')))


class MFCDeviceEditor(core.device.DeviceEditor):
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
                if dtype == 'mfc':
                    choices.append(item)

        return choices

    def createHardwareBox(self):
        sbox = wx.StaticBox(self.control, -1, messages.get('device.config.hardwarebox.label'), size=(-1, 200))
        ssizer = wx.StaticBoxSizer(sbox, wx.VERTICAL)
        fsizer = wx.FlexGridSizer(0, 2, 5, 5)
        fsizer.AddGrowableCol(1)
        label = wx.StaticText(self.control, -1, messages.get('device.config.gcf.label'))
        self.gcfText = wx.TextCtrl(self.control, -1)
        fsizer.Add(label, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
        fsizer.Add(self.gcfText, 0, wx.ALIGN_CENTRE_VERTICAL)
        self.purgeCheckbox = wx.CheckBox(self.control, -1, messages.get('device.config.purge.checkbox.label'))
        self.control.Bind(wx.EVT_CHECKBOX, self.OnPurgeCheck, self.purgeCheckbox)
        fsizer.Add(wx.Panel(self.control, -1))
        fsizer.Add(self.purgeCheckbox, 0, wx.ALL)
        self.purgeSetpointText = mfc.widgets.PurgetSetpointCtrl(self.control)
        self.purgeSetpointText.Enable(False)
        fsizer.Add(wx.StaticText(self.control, -1, messages.get('device.config.purge.setpoint.label')), 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
        fsizer.Add(self.purgeSetpointText, 1, wx.GROW | wx.ALL)
        self.purgeDuration = timectrl.TimeCtrl(self.control, -1, fmt24hr=True)
        self.purgeDuration.Enable(False)
        fsizer.Add(wx.StaticText(self.control, -1, messages.get('device.config.purge.duration.label')), 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
        fsizer.Add(self.purgeDuration, 0, wx.ALL)
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
        self.gcfText.Bind(wx.EVT_KILL_FOCUS, self.OnLeaveGCF)
        return ssizer

    def OnPurgeCheck(self, event):
        event.Skip()
        checked = self.purgeCheckbox.IsChecked()
        self.purgeSetpointText.Enable(checked)
        self.purgeDuration.Enable(checked)

    def OnLeaveGCF(self, event):
        """Conforms the value to a percentage with 2 precision"""
        event.Skip()
        value = self.gcfText.GetValue()
        try:
            value = float(value)
        except Exception, msg:
            logger.warn('Invalid value for gcf. Setting to 1.00')
            value = 1

        self.gcfText.SetValue(str(value))

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
        checked = self.purgeCheckbox.IsChecked()
        self.purgeSetpointText.Enable(checked)
        self.purgeDuration.Enable(checked)

    def createUIBox(self):
        sbox = wx.StaticBox(self.control, -1, ' User Interface ')
        ssizer = wx.StaticBoxSizer(sbox, wx.VERTICAL)
        fsizer = wx.FlexGridSizer(0, 2, 5, 5)
        fsizer.AddGrowableCol(1)
        label = wx.StaticText(self.control, -1, 'Label:')
        self.labelField = wx.TextCtrl(self.control, -1, '')
        fsizer.Add(label, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
        fsizer.Add(self.labelField, 1, wx.GROW | wx.ALIGN_CENTRE_VERTICAL)
        fsizer.Add(wx.StaticText(self.control, -1, 'Grid Editor Field:'), 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.columnActualFlowRadio = wx.RadioButton(self.control, wx.NewId(), 'GCF Converted Setpoint', style=wx.RB_GROUP)
        self.columnSetpointRadio = wx.RadioButton(self.control, wx.NewId(), 'Raw Setpoint')
        hsizer.Add(self.columnSetpointRadio, 0, wx.ALIGN_CENTRE_VERTICAL | wx.RIGHT, 5)
        hsizer.Add(self.columnActualFlowRadio, 0, wx.ALIGN_CENTRE_VERTICAL)
        fsizer.Add(hsizer, 1, wx.GROW | wx.ALIGN_CENTRE_VERTICAL)
        self.plotColor = colourselect.ColourSelect(self.control, -1, size=(60, 20))
        fsizer.Add(wx.StaticText(self.control, -1, 'Plot Color:'), 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
        fsizer.Add(self.plotColor, 0, wx.ALIGN_CENTRE_VERTICAL)
        ssizer.Add(fsizer, 0, wx.GROW | wx.TOP, 10)
        return ssizer

    def float2str(self, value):
        frmt = '%%0.%df' % 2
        return frmt % value

    def setData(self, data):
        """Put data from node into widgets"""
        self.device = data
        uihints = data.getUIHints()
        hwhints = data.getHardwareHints()
        try:
            gcf = int(hwhints.getChildNamed('conversion-factor').getValue()) / 100.0
        except Exception, msg:
            logger.warn("Unable to get value for gas conversion factor from recipe. Defaulting to 100%%: '%s'" % msg)
            gcf = 1.0

        self.gcfText.SetValue(self.float2str(gcf))
        try:
            hwid = hwhints.getChildNamed('id').getValue()
            self.selectHardware(hwid)
        except Exception, msg:
            logger.exception(msg)
            logger.warn('Cannot set hardware: %s' % msg)

        try:
            colors = uihints.getChildNamed('colors')
            self.plotColor.SetValue(parseColor(colors.getChildNamed('plot').getValue()))
        except Exception, msg:
            logger.exception(msg)
            logger.warn('Cannot set color: %s' % msg)

        try:
            label = uihints.getChildNamed('label').getValue()
            self.labelField.SetValue(label)
        except Exception, msg:
            logger.exception(msg)
            logger.warn('Cannot set hardware: %s' % msg)

        usegcf = True
        try:
            usegcf = uihints.getChildNamed('column-use-gcf').getValue().lower() == 'true'
        except Exception, msg:
            logger.exception(msg)
            logger.warn('Cannot set choice for column: %s' % msg)

        purgeSetpoint = '0.0'
        purgeDuration = 0
        purgeActive = False
        try:
            purgeNode = hwhints.getChildNamed('purge')
            purgeActive = purgeNode.getAttribute('active').lower() == 'true'
            purgeSetpoint = purgeNode.getAttribute('setpoint')
            purgeDuration = int(purgeNode.getAttribute('duration'))
        except Exception, msg:
            logger.exception(msg)
            logger.warn('Cannot set purge setpoint')

        self.purgeCheckbox.SetValue(purgeActive)
        self.columnActualFlowRadio.SetValue(usegcf)
        self.columnSetpointRadio.SetValue(not usegcf)
        self.purgeDuration.SetValue(wx.TimeSpan.Seconds(purgeDuration))
        self.purgeSetpointText.SetValue(purgeSetpoint)
        self.update()
        if self.currentHardwareEditor is not None:
            self.currentHardwareEditor.setData(None, hwhints)
        return

    def channelSelected(self, channel):
        hwid = self.getSelectedHardwareInstance()
        recipe = ui.context.getProperty('recipe')
        valid = True
        if channel == 0:
            return True
        for device in recipe.getDevices():
            if device.getType() != self.device.getType():
                continue
            if device == self.device:
                continue
            if hwid != device.getHardwareHints().getChildNamed('id').getValue():
                continue
            if device.getChannelNumber() == channel:
                valid = False
                break

        self.owner.setCanFinish(valid)
        return valid

    def getHardwareChoicesName(self):
        choices = self.getHardwareChoices()
        return map((lambda p: p.getName()), choices)

    def selectHardware(self, hwid):
        try:
            idx = self.getHardwareChoicesName().index(hwid)
            self.hardwareChoice.SetSelection(idx)
        except Exception, msg:
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
        self.purgeSetpointText.setMax(self.max)

    def setHardwareEditor(self, editor):
        self.removeHardwareEditor()
        editor.setInstance(self.description.getInstance())
        editor.setOwner(self)
        editor.createControl(self.hardwarePanel)
        sizer = self.hardwarePanel.GetSizer()
        sizer.Add(editor.getControl(), 1, wx.GROW | wx.TOP | wx.BOTTOM, 0)
        editor.getControl().GetSizer().Fit(editor.getControl())
        size = editor.getControl().GetSize()
        self.currentHardwareEditor = editor
        mainsizer = self.control.GetSizer()
        self.hardwarePanel.SetSize(size)
        mainsizer.SetItemMinSize(self.hardwarePanel, size)
        s = self.control.GetContainingSizer()
        (w, h) = self.control.GetSize()
        s.SetItemMinSize(self.control, (w, h))
        self.control.GetParent().Layout()

    def getGCFValue(self):
        val = self.gcfText.GetValue()
        try:
            return int(float(val) * 100)
        except Exception, msg:
            logger.warn("Invalid value for gas conversion factor '%s', setting to 100" % val)
            return 100

    def getData(self, data):
        """put data into the node"""
        try:
            hwhints = data.getHardwareHints()
            uihints = data.getUIHints()
            vname = self.getHardwareChoices()[self.hardwareChoice.GetSelection()].getName()
            label = self.labelField.GetValue()
            gcf = self.getGCFValue()
            usegcf = self.columnActualFlowRadio.GetValue()
            logger.debug('Setting conversion factor to: %s' % str(gcf))
            hwhints.createChildIfNotExists('conversion-factor').setValue(str(gcf))
            hwhints.createChildIfNotExists('id').setValue(vname)
            uihints.createChildIfNotExists('label').setValue(label)
            colors = uihints.createChildIfNotExists('colors')

            def convertColor(value):
                return '%s,%s,%s' % (value.Red(), value.Green(), value.Blue())

            colors.createChildIfNotExists('plot').setValue(convertColor(self.plotColor.GetValue()))
            purgeNode = hwhints.createChildIfNotExists('purge')
            purgeSetpoint = self.purgeSetpointText.GetValue()
            try:
                purgeSetpoint = str(float(purgeSetpoint))
            except Exception, msg:
                logger.exception(msg)
                purgeSetpoint = '0.0'

            purgeNode.setAttribute('active', str(self.purgeCheckbox.IsChecked()))
            purgeNode.setAttribute('setpoint', purgeSetpoint)
            purgeDuration = self.purgeDuration.GetValue(as_wxTimeSpan=True)
            try:
                purgeDuration = str(purgeDuration.GetSeconds())
            except Exception, msg:
                logger.exception(msg)
                purgeDuration = 0

            purgeNode.setAttribute('duration', purgeDuration)
            logger.debug('setting ui hints: %s' % str(usegcf))
            uihints.createChildIfNotExists('column-use-gcf').setValue(str(usegcf))
            if self.currentHardwareEditor is not None:
                self.currentHardwareEditor.getData(hwhints)
        except Exception, msg:
            logger.exception(msg)
            logger.error("Unable to save device data to recipe: '%s'" % msg)

        return


class MFCDevice(core.device.Device):
    __module__ = __name__

    def __init__(self):
        global DEVICE_ID
        core.device.Device.__init__(self, DEVICE_ID)
        self.haspurge = False
        self.channelNum = -1
        self.colors = {'plot': (wx.Color(0, 0, 0))}

    def hasPurge(self):
        try:
            hwhints = self.getHardwareHints()
            purgeNode = hwhints.getChildNamed('purge')
            return purgeNode.getAttribute('active').lower() == 'true'
        except:
            pass

        return False

    def getPurgeSetpoint(self):
        setpoint = 0
        try:
            hwhints = self.getHardwareHints()
            purgeNode = hwhints.getChildNamed('purge')
            setpoint = float(purgeNode.getAttribute('setpoint'))
        except Exception, msg:
            return 1

        return setpoint

    def getPurgeLength(self):
        length = 0
        try:
            hwhints = self.getHardwareHints()
            purgeNode = hwhints.getChildNamed('purge')
            length = int(purgeNode.getAttribute('duration'))
        except Exception, msg:
            logger.exception(msg)
            return 20

        return length

    def getChannelNumber(self):
        return self.channelNum

    def getDeviceStr(self):
        try:
            hwhints = self.getHardwareHints()
            hardwareName = hwhints.getChildNamed('id').getValue()
            hardwareChannel = int(hwhints.getChildNamed('channel').getValue())
            description = hardware.hardwaremanager.getHardwareByName(hardwareName)
            hwtype = description.getHardwareType()
            hwtype = hardware.hardwaremanager.getHardwareType(hwtype)
            description = hwtype.getDescription()
            return '%s (%s) - Channel %s' % (hardwareName, description, str(hardwareChannel))
        except Exception, msg:
            print '* WARNING:', msg

        return '*NOT CONFIGURED*'

    def parseColor(self, val):
        return apply(wx.Color, map(int, val.split(',')))

    def getPlotColor(self):
        """
        uihints = self.getUIHints()
        
        try:
            colors = uihints.getChildNamed('colors')
            
            return self.parseColor(colors.getChildNamed('plot').getValue())
        except Exception, msg:
            logger.exception(msg)
            
        return wx.Color(0, 0, 0)
        """
        return self.colors['plot']

    def configurationUpdated(self):
        core.device.Device.configurationUpdated(self)
        hwhints = self.getHardwareHints()
        try:
            self.channelNum = int(hwhints.getChildNamed('channel').getValue())
        except Exception, msg:
            logger.exception(msg)

    def getRange(self):
        try:
            return float(self.getHardwareHints().getChildNamed('range').getValue())
        except Exception, msg:
            return 1

    def getUnits(self):
        try:
            return self.getHardwareHints().getChildNamed('units').getValue()
        except Exception, msg:
            return 1

    def getGCF(self):
        try:
            return int(self.getHardwareHints().getChildNamed('conversion-factor').getValue())
        except Exception, msg:
            return 100

    def updateUIHints(self):
        core.device.Device.updateUIHints(self)
        uihints = self.getUIHints()
        try:
            colors = uihints.getChildNamed('colors')
            self.colors['plot'] = self.parseColor(colors.getChildNamed('plot').getValue())
        except Exception, msg:
            logger.exception(msg)
            self.colors['plot'] = wx.Color(0, 0, 0)

    def parseFromNode(self, node):
        result = mfc.stepentry.parseFromNode(node)
        self.configurationUpdated()
        return result

    def convertToNode(self, root):
        core.device.Device.convertToNode(self, root)

    def createNewStepEntry(self, fromExisting=None):
        if fromExisting is not None:
            return fromExisting.clone()
        return mfc.stepentry.MFCStepEntry()
        return

    def getDeviceEditor(self):
        return MFCDeviceEditor()
