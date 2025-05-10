# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/furnacezone/src/furnacezone/device.py
# Compiled at: 2004-11-19 02:40:49
import wx.lib.masked.timectrl as timectrl, traceback, wx, furnacezone, furnacezone.stepentry, furnacezone.conditional, hardware.hardwaremanager, core.device, ui, ui.images as uiimages, poi.utils.staticwraptext as staticwraptext, poi.images as poiimages, logging, furnacezone.messages as messages, wx.lib.colourselect as colourselect

def color2str(color):
    return '%d,%d,%d' % (color.Red(), color.Green(), color.Blue())


def parseColor(colorStr):
    return apply(wx.Color, map(int, colorStr.split(',')))


logger = logging.getLogger('furnacezone.userinterface')
DEVICE_ID = 'furnacezone'

def parseColor(colorStr):
    return apply(wx.Color, map(int, colorStr.split(',')))


class FurnaceZoneDeviceEditor(core.device.DeviceEditor):
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
        sizer.Add(uibox, 0, wx.GROW | wx.ALL, 5)
        sizer.Add(hwbox, 0, wx.GROW | wx.ALL, 5)
        self.control.SetSizer(sizer)
        self.control.SetAutoLayout(True)
        sizer.Layout()
        return self.control

    def getHardwareChoices(self):
        choices = []
        hw = hardware.hardwaremanager.getHardware()
        for item in hw:
            hwtype = hardware.hardwaremanager.getHardwareType(item.getHardwareType())
            deviceTypes = hwtype.getDeviceTypes()
            for dtype in deviceTypes:
                if dtype == 'furnace_zone':
                    choices.append(item)

        return choices

    def createHardwareBox(self):
        sbox = wx.StaticBox(self.control, -1, messages.get('device.config.hardwarebox.label'))
        ssizer = wx.StaticBoxSizer(sbox, wx.VERTICAL)
        fsizer = wx.FlexGridSizer(0, 2, 5, 5)
        fsizer.AddGrowableCol(1)
        label = wx.StaticText(self.control, -1, messages.get('device.config.range.label'))
        self.rangeText = wx.TextCtrl(self.control, -1)
        fsizer.Add(label, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
        fsizer.Add(self.rangeText, 0, wx.ALIGN_CENTRE_VERTICAL)
        self.purgeCheckbox = wx.CheckBox(self.control, -1, messages.get('device.config.purge.active'))
        fsizer.Add(wx.Panel(self.control, -1), 0, wx.ALIGN_RIGHT)
        fsizer.Add(self.purgeCheckbox, 1, wx.GROW | wx.ALL | wx.ALIGN_CENTRE_VERTICAL)
        self.purgeSetpointText = wx.TextCtrl(self.control, -1)
        panel = wx.Panel(self.control, -1, style=wx.SIMPLE_BORDER, size=(200, -1))
        panel.SetBackgroundColour(wx.Color(246, 232, 175))
        img = wx.StaticBitmap(panel, -1, poiimages.getImage(poiimages.WARNING_ICON_32))
        notice = wx.Panel(panel, -1)
        notice.SetBackgroundColour(panel.GetBackgroundColour())
        txt = staticwraptext.StaticWrapText(notice, -1, messages.get('device.config.purge.notice'), size=(-1, 40))
        s = wx.BoxSizer(wx.HORIZONTAL)
        s.Add(txt, 1, wx.GROW)
        notice.SetSizer(s)
        notice.SetAutoLayout(True)
        sb = wx.BoxSizer(wx.HORIZONTAL)
        sb.Add(img, 0, wx.GROW | wx.ALL | wx.ALIGN_CENTRE_VERTICAL, 5)
        sb.Add(notice, 1, wx.GROW | wx.ALL, 5)
        panel.SetSizer(sb)
        panel.SetAutoLayout(True)
        fsizer.Add(wx.Panel(self.control, -1), 0, wx.ALIGN_RIGHT)
        fsizer.Add(panel, 1, wx.GROW | wx.ALL | wx.ALIGN_CENTRE_VERTICAL, 0)
        fsizer.Add(wx.StaticText(self.control, -1, messages.get('device.config.purge.setpoint.label')), 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
        fsizer.Add(self.purgeSetpointText, 1, wx.GROW | wx.ALL)
        self.purgeDuration = timectrl.TimeCtrl(self.control, -1, fmt24hr=True)
        fsizer.Add(wx.StaticText(self.control, -1, messages.get('device.config.purge.duration.label')), 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
        fsizer.Add(self.purgeDuration, 0, wx.ALL)
        label = wx.StaticText(self.control, -1, messages.get('device.config.hardware.label'))
        hwchoices = self.getHardwareChoices()
        self.hardwareChoice = wx.ComboBox(self.control, -1, choices=self.getHardwareChoicesNames())
        fsizer.Add(label, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL, 5)
        self.channelErrorMsg = wx.Panel(self.control)
        self.channelErrorMsg.Show(False)
        ceSizer = wx.BoxSizer()
        ceSizer.Add(wx.StaticBitmap(self.channelErrorMsg, -1, uiimages.getImage(uiimages.ERROR_ICON)), 0, wx.GROW)
        ceSizer.Add(wx.StaticText(self.channelErrorMsg, -1, messages.get('conflictinghardware.message')), 1, wx.GROW)
        self.channelErrorMsg.SetSizer(ceSizer)
        self.channelErrorMsg.SetAutoLayout(True)
        hs = wx.BoxSizer(wx.HORIZONTAL)
        hs.Add(self.hardwareChoice, 0, wx.ALIGN_CENTRE_VERTICAL)
        hs.Add(self.channelErrorMsg, 1, wx.ALIGN_CENTRE_VERTICAL)
        fsizer.Add(hs, 1, wx.ALIGN_CENTRE_VERTICAL)
        self.control.Bind(wx.EVT_COMBOBOX, self.OnHardwareChoice, self.hardwareChoice)
        self.control.Bind(wx.EVT_TEXT, self.OnRangeText, self.rangeText)
        ssizer.Add(fsizer, 0, wx.GROW | wx.TOP, 10)
        ssizer.Add(wx.StaticLine(self.control, -1), 0, wx.GROW | wx.ALL, 5)
        self.hardwarePanel = wx.Panel(self.control, -1, size=(300, 300))
        self.hardwarePanel.SetSizer(wx.BoxSizer(wx.VERTICAL))
        ssizer.Add(self.hardwarePanel, 1, wx.GROW | wx.ALL, 5)
        self.purgeCheckbox.Bind(wx.EVT_CHECKBOX, self.OnPurgeCheckboxChecked)
        return ssizer

    def getHardwareChoicesNames(self):
        lst = [
         'None']
        lst.extend(map((lambda c: c.getName()), self.getHardwareChoices()))
        return lst

    def OnRangeText(self, event):
        event.Skip()

    def OnHardwareChoice(self, event):
        """
        When a selection is made from the drop down then
        get the name of the hardware and set the editor for that 
        device
        """
        choices = self.getHardwareChoices()
        choiceIdx = self.hardwareChoice.GetSelection()
        if choiceIdx > 0:
            choice = choices[choiceIdx - 1]
            choice = choice.getName()
        else:
            choice = 'None'
            self.description = None
        self.selectHardware(choice)
        return

    def OnPurgeCheckboxChecked(self, event):
        event.Skip()
        self.updateControls()

    def updateControls(self):
        purgeActive = self.purgeCheckbox.IsChecked()
        self.purgeSetpointText.Enable(purgeActive)
        self.purgeDuration.Enable(purgeActive)

    def createUIBox(self):
        sbox = wx.StaticBox(self.control, -1, ' User Interface ')
        ssizer = wx.StaticBoxSizer(sbox, wx.VERTICAL)
        fsizer = wx.FlexGridSizer(0, 2, 5, 5)
        fsizer.AddGrowableCol(1)
        label = wx.StaticText(self.control, -1, 'Label:')
        self.labelField = wx.TextCtrl(self.control, -1, '')
        fsizer.Add(label, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
        fsizer.Add(self.labelField, 1, wx.GROW | wx.ALIGN_CENTRE_VERTICAL)
        self.devicePlotColor = colourselect.ColourSelect(self.control, -1, size=(60, 20))
        fsizer.Add(wx.StaticText(self.control, -1, messages.get('device.plot.color.label')), 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
        fsizer.Add(self.devicePlotColor, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTRE_VERTICAL)
        ssizer.Add(fsizer, 1, wx.GROW | wx.TOP, 10)
        return ssizer

    def float2str(self, value):
        frmt = '%%0.%df' % 2
        return frmt % value

    def setData(self, data):
        self.device = data
        uihints = data.getUIHints()
        hwhints = data.getHardwareHints()
        try:
            rng = int(hwhints.getChildNamed('range').getValue())
        except Exception as msg:
            logger.warning("Unable to get range value: '%s'" % msg)
            rng = 1000

        self.rangeText.SetValue(str(rng))
        try:
            self.devicePlotColor.SetValue(parseColor(uihints.getChildNamed('plot-color').getValue()))
        except Exception as msg:
            logger.exception(msg)
            self.devicePlotColor.SetValue(wx.RED)

        try:
            hwid = hwhints.getChildNamed('id').getValue()
            self.selectHardware(hwid)
        except Exception as msg:
            logger.exception(msg)
            logger.warning("Cannot set hardware: '%s'" % msg)

        try:
            label = uihints.getChildNamed('label').getValue()
            self.labelField.SetValue(label)
        except Exception as msg:
            logger.exception(msg)
            logger.warning("Cannot set hardware: '%s'" % msg)

        purgeActive = False
        purgeSetpoint = '0'
        purgeDuration = 0
        try:
            purgeActive = hwhints.getChildNamed('purge').getAttribute('active').lower() == 'true'
        except Exception as msg:
            logger.exception(msg)

        self.purgeCheckbox.SetValue(purgeActive)
        try:
            purgeNode = hwhints.getChildNamed('purge')
            purgeSetpoint = purgeNode.getAttribute('setpoint')
            purgeDuration = int(purgeNode.getAttribute('duration'))
        except Exception as msg:
            logger.exception(msg)
            logger.warning('Cannot set purge setpoint')

        self.purgeDuration.SetValue(wx.TimeSpan.Seconds(purgeDuration))
        self.purgeSetpointText.SetValue(purgeSetpoint)
        if self.currentHardwareEditor is not None:
            self.currentHardwareEditor.setData(None, hwhints)
        self.updateControls()
        return

    def selectHardware(self, hwid):
        hwidx = self.getHardwareChoicesNames().index(hwid)
        self.hardwareChoice.SetSelection(hwidx)
        if hwidx > 0:
            description = hardware.hardwaremanager.getHardwareByName(hwid)
            hwtype = hardware.hardwaremanager.getHardwareType(description.getHardwareType())
            self.description = description
        else:
            self.description = None
        recipe = ui.context.getProperty('recipe')
        valid = True
        for device in recipe.getDevices():
            if device.getType() != self.device.getType():
                continue
            if device == self.device:
                continue
            if hwid != device.getHardwareHints().getChildNamed('id').getValue():
                continue
            valid = False

        self.owner.setCanFinish(valid)
        self.channelErrorMsg.Show(not valid)
        return

    def removeHardwareEditor(self):
        sizer = self.hardwarePanel.GetSizer()
        for child in self.hardwarePanel.GetChildren():
            self.hardwarePanel.Remove(child)
            sizer.Remove(child)
            child.Destroy()

    def setHardwareEditor(self, editor):
        self.removeHardwareEditor()
        editor.setInstance(self.description.getInstance())
        editor.createControl(self.hardwarePanel)
        sizer = self.hardwarePanel.GetSizer()
        sizer.Add(editor.getControl(), 1, wx.GROW | wx.ALL, 0)
        sizer.Layout()
        self.currentHardwareEditor = editor

    def getData(self, data):
        try:
            hwhints = data.getHardwareHints()
            uihints = data.getUIHints()
            vname = self.hardwareChoice.GetStringSelection()
            label = self.labelField.GetValue()
            rng = self.rangeText.GetValue()
            try:
                rng = int(rng)
            except Exception as msg:
                logger.warning("Unable to parse integer for range value: '%s'" % msg)
                rng = 1000

            hwhints.createChildIfNotExists('range').setValue(str(rng))
            hwhints.createChildIfNotExists('id').setValue(vname)
            uihints.createChildIfNotExists('label').setValue(label)
            uihints.createChildIfNotExists('plot-color').setValue(color2str(self.devicePlotColor.GetValue()))
            purgeNode = hwhints.createChildIfNotExists('purge')
            purgeSetpoint = self.purgeSetpointText.GetValue()
            try:
                purgeSetpoint = str(int(purgeSetpoint))
            except Exception as msg:
                logger.exception(msg)
                purgeSetpoint = '0'

            purgeActive = 'false'
            if self.purgeCheckbox.IsChecked():
                purgeActive = 'true'
            purgeNode.setAttribute('active', purgeActive)
            purgeNode.setAttribute('setpoint', purgeSetpoint)
            purgeDuration = self.purgeDuration.GetValue(as_wxTimeSpan=True)
            try:
                purgeDuration = str(purgeDuration.GetSeconds())
            except Exception as msg:
                logger.exception(msg)
                purgeDuration = 0

            purgeNode.setAttribute('duration', purgeDuration)
            if self.currentHardwareEditor is not None:
                self.currentHardwareEditor.getData(hwhints)
        except Exception as msg:
            logger.exception(msg)
            logger.error("Unable to save device data to recipe: '%s'" % msg)

        return


class FurnaceZoneDevice(core.device.Device):
    __module__ = __name__

    def __init__(self):
        global DEVICE_ID
        core.device.Device.__init__(self, DEVICE_ID)
        self.plotcolor = wx.RED
        mainframe = ui.getDefault().getMainFrame()
        mainframe.addViewLifecycleListener(self)

    def getPlotColor(self):
        return self.plotcolor

    def getHardwareID(self):
        try:
            hwhints = self.getHardwareHints()
            return hwhints.getChildNamed('id').getValue()
        except Exception as msg:
            pass

        return None

    def getPurgeActive(self):
        try:
            hwhints = self.getHardwareHints()
            return hwhints.getChildNamed('purge').getAttribute('active').lower() == 'true'
        except Exception as msg:
            pass

        return False

    def getPurgeSetpoint(self):
        setpoint = 0
        try:
            hwhints = self.getHardwareHints()
            purgeNode = hwhints.getChildNamed('purge')
            setpoint = int(purgeNode.getAttribute('setpoint'))
        except Exception as msg:
            logger.exception(msg)
            return 1

        return setpoint

    def getPurgeLength(self):
        length = 0
        try:
            hwhints = self.getHardwareHints()
            purgeNode = hwhints.getChildNamed('purge')
            length = int(purgeNode.getAttribute('duration'))
        except Exception as msg:
            logger.exception(msg)
            return 20

        return length

    def viewCreated(self, viewID, view):
        print('View Created:', viewID, self)

    def viewRemoved(self, viewID, view):
        print('View Removed:', viewID, self)

    def updateHardwareHints(self):
        pass

    def getRange(self):
        try:
            return int(self.getHardwareHints().getChildNamed('range').getValue())
        except Exception as msg:
            return 1000

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
            logger.exception(msg)

        return '*NOT CONFIGURED*'

    def updateUIHints(self):
        core.device.Device.updateUIHints(self)
        uihints = self.getUIHints()
        try:
            self.plotcolor = parseColor(uihints.getChildNamed('plot-color').getValue())
        except Exception as msg:
            logger.exception(msg)
            self.plotcolor = wx.RED

    def configurationUpdated(self):
        core.device.Device.configurationUpdated(self)
        uihints = self.getUIHints()

    def parseFromNode(self, node):
        return furnacezone.stepentry.parseFromNode(node)

    def convertToNode(self, root):
        core.device.Device.convertToNode(self, root)

    def createNewStepEntry(self, fromExisting=None):
        if fromExisting is not None:
            return fromExisting.clone()
        return furnacezone.stepentry.FurnaceZoneStepEntry()

    def getDeviceEditor(self):
        return FurnaceZoneDeviceEditor()

    def getConditionalContributions(self):
        return [
         furnacezone.conditional.FurnaceZoneConditionalContribution(self)]

    def dispose(self):
        mainframe = ui.getDefault().getMainFrame()
        mainframe.removeViewLifecycleListener(self)
