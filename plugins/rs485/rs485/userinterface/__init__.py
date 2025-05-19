# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/rs485/src/rs485/userinterface/__init__.py
# Compiled at: 2004-11-23 21:59:58
import wx, logging, plugins.poi.poi.dialogs, plugins.hardware.hardware.userinterface.configurator
import plugins.hardware.hardware.hardwaremanager, plugins.rs485.rs485.drivers as rs485_drivers
import plugins.rs485.rs485.userinterface.initdialog
import plugins.poi.poi.operation, plugins.poi.poi.dialogs.progress
import plugins.poi.poi as poi
import plugins.hardware.hardware as hardware
import plugins.ui.ui as ui

SCCM = 'sccm'
SLM = 'slm'
SCMM = 'scmm'
SCFH = 'scfh'
SCFM = 'scfm'
UNITS = [SCCM, SLM, SCMM, SCFH, SCFM]
RANGES = {SCCM: {0: 1, 1: 2, 2: 5, 3: 10, 4: 20, 5: 50, 6: 100, 7: 200, 8: 500},
          SLM: {9: 1, 10: 2, 11: 5, 12: 10, 13: 20, 38: 30, 14: 50, 15: 100, 16: 200, 39: 300, 17: 400, 18: 500},
          SCMM: {19: 1}, SCFH: {20: 1, 21: 2, 22: 5, 23: 10, 24: 20, 25: 50, 26: 100, 27: 200, 28: 500},
          SCFM: {29: 1, 30: 2, 31: 5, 32: 10, 33: 20, 34: 50, 35: 100, 36: 200, 37: 500}}
logger = logging.getLogger('rs485.ui')

def getUnitChoices():
    global UNITS
    return UNITS


def getRangeChoices(unitKey):
    global RANGES
    values = list(RANGES[unitKey].values())
    values.sort()
    return values


class DeviceHardwareEditor(hardware.userinterface.DeviceHardwareEditor):
    __module__ = __name__

    def __init__(self):
        hardware.userinterface.DeviceHardwareEditor.__init__(self)
        self.control = None
        return

    def createControl(self, parent):
        fsizer = wx.FlexGridSizer(0, 2, 5, 5)
        self.control = wx.Panel(parent, -1)
        label = wx.StaticText(self.control, -1, 'Channel:')

        def modapp(i):
            return str(i + 1)

        self.channelChoice = wx.Choice(self.control, -1, choices=list(map(modapp, list(range(self.instance.getChannelCount())))))
        fsizer.Add(label, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
        fsizer.Add(self.channelChoice, 0, wx.ALIGN_CENTRE_VERTICAL)
        label = wx.StaticText(self.control, -1, 'Units:')
        self.unitsChoice = wx.Choice(self.control, -1, choices=getUnitChoices())
        fsizer.Add(label, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
        fsizer.Add(self.unitsChoice, 0, wx.ALIGN_CENTRE_VERTICAL)
        label = wx.StaticText(self.control, -1, 'Range:')
        self.rangeChoice = wx.Choice(self.control, -1)
        fsizer.Add(label, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
        fsizer.Add(self.rangeChoice, 0, wx.ALIGN_CENTRE_VERTICAL)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(fsizer, 1, wx.EXPAND | wx.ALL)
        self.control.SetSizer(sizer)
        self.control.SetAutoLayout(True)
        self.control.Bind(wx.EVT_CHOICE, self.OnUnitSelected, self.unitsChoice)
        self.control.Bind(wx.EVT_CHOICE, self.OnRangeSelected, self.rangeChoice)
        return self.control

    def OnUnitSelected(self, event):
        event.Skip()
        self.selectUnit(self.unitsChoice.GetStringSelection())
        self.rangeChoice.SetSelection(0)

    def selectUnit(self, unitStr):
        self.unitsChoice.SetStringSelection(unitStr)
        self.rangeChoice.Clear()
        ranges = getRangeChoices(unitStr)
        for value in ranges:
            self.rangeChoice.Append(str(value))

    def selectChannel(self, channelNumStr):
        self.channelChoice.SetStringSelection(channelNumStr)

    def selectRange(self, rangeStr):
        self.rangeChoice.SetStringSelection(rangeStr)

    def OnRangeSelected(self, event):
        event.Skip()

    def setData(self, recipe, data):
        global logger
        try:
            channelNum = int(data.getChildNamed('channel').getValue())
            units = data.getChildNamed('units').getValue()
            gcf = data.getChildNamed('conversion-factor').getValue()
            rangeValue = data.getChildNamed('range').getValue()
            self.selectUnit(units)
            self.selectRange(str(rangeValue))
            self.selectChannel(str(channelNum + 1))
        except Exception as msg:
            logger.warning("Unable to set data for device entry: '%s'" % msg)
            logger.exception(msg)

    def getData(self, data):
        channelNum = int(self.channelChoice.GetStringSelection()) - 1
        units = self.unitsChoice.GetStringSelection()
        rangeValue = int(self.rangeChoice.GetStringSelection())
        gcf = 1.0
        data.createChildIfNotExists('channel').setValue(str(channelNum))
        data.createChildIfNotExists('units').setValue(units)
        data.createChildIfNotExists('range').setValue(str(rangeValue))
        data.createChildIfNotExists('conversion-factor').setValue(str(gcf))


class ConfigurationPage(hardware.userinterface.configurator.ConfigurationPage):
    __module__ = __name__

    def __init__(self):
        hardware.userinterface.configurator.ConfigurationPage.__init__(self)
        self.changedDriverSegment = False

    def getDriverSegmentChanged(self):
        return self.changedDriverSegment

    def setDriverSegmentChanged(self, changed):
        self.changedDriverSegment = changed

    def createConfigPanel(self, parent):
        panel = wx.Panel(parent, -1)
        mainsizer = wx.BoxSizer(wx.VERTICAL)
        banner = wx.Panel(panel, -1, style=wx.SIMPLE_BORDER)
        banner.SetBackgroundColour(wx.WHITE)
        self.hardwareLabel = wx.StaticText(banner, -1, '')
        font = parent.GetFont()
        font.SetWeight(wx.BOLD)
        self.hardwareLabel.SetFont(font)
        bsizer = wx.BoxSizer(wx.HORIZONTAL)
        bsizer.Add(self.hardwareLabel, 1, wx.ALL | wx.ALIGN_CENTRE_VERTICAL, 5)
        banner.SetSizer(bsizer)
        banner.SetAutoLayout(True)
        mainsizer.Add(banner, 0, wx.EXPAND | wx.ALL, 5)
        infoBox = wx.StaticBox(panel, -1, ' Hardware Information ')
        nameLabel = wx.StaticText(panel, -1, 'Name:')
        nameField = wx.TextCtrl(panel, -1, '')
        nameField.Enable(False)
        self.nameField = nameField
        statusLabel = wx.StaticText(panel, -1, 'Status:')
        self.statusLabel = wx.StaticText(panel, -1, '')
        boxSizer = wx.StaticBoxSizer(infoBox, wx.VERTICAL)
        sizer = wx.FlexGridSizer(0, 2, 5, 5)
        sizer.AddGrowableCol(1)
        sizer.Add(nameLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
        sizer.Add(nameField, 1, wx.EXPAND)
        sizer.Add(statusLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
        sizer.Add(self.statusLabel, 1, wx.EXPAND)
        boxSizer.Add(sizer, 1, wx.EXPAND | wx.ALL, 5)
        mainsizer.Add(boxSizer, 0, wx.EXPAND | wx.ALL, 5)
        infoBox = wx.StaticBox(panel, -1, ' Device Driver ')
        boxSizer = wx.StaticBoxSizer(infoBox, wx.VERTICAL)
        driverLabel = wx.StaticText(panel, -1, 'Driver Type:')
        self.driverCombo = wx.ComboBox(panel, -1, choices=self.getDriverOptions(), style=wx.CB_READONLY)
        panel.Bind(wx.EVT_COMBOBOX, self.OnDriverChoice, self.driverCombo)
        sizer = wx.FlexGridSizer(0, 2, 5, 5)
        sizer.AddGrowableCol(1)
        sizer.Add(driverLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
        sizer.Add(self.driverCombo, 1, wx.ALIGN_CENTRE_VERTICAL)
        self.driverConfigPanel = wx.Panel(panel, -1, size=wx.Size(300, 150))
        boxSizer.Add(sizer, 0, wx.EXPAND | wx.ALL, 5)
        boxSizer.Add(wx.StaticLine(panel, -1), 0, wx.EXPAND | wx.ALL, 5)
        boxSizer.Add(self.driverConfigPanel, 1, wx.EXPAND | wx.ALL, 5)
        mainsizer.Add(boxSizer, 0, wx.EXPAND | wx.ALL, 5)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.driverConfigPanel.SetSizer(sizer)
        infoBox = wx.StaticBox(panel, -1, ' General Options ')
        boxSizer = wx.StaticBoxSizer(infoBox, wx.VERTICAL)
        self.startupInitCheckbox = wx.CheckBox(panel, -1, 'Initialize hardware on Startup')
        panel.Bind(wx.EVT_CHECKBOX, self.markDirty, self.startupInitCheckbox)
        boxSizer.Add(self.startupInitCheckbox, 0, wx.EXPAND | wx.ALL, 5)
        mainsizer.Add(boxSizer, 0, wx.EXPAND | wx.ALL, 5)
        self.startButton = wx.Button(panel, -1, 'Start')
        panel.Bind(wx.EVT_BUTTON, self.OnStart, self.startButton)
        self.stopButton = wx.Button(panel, -1, 'Stop')
        panel.Bind(wx.EVT_BUTTON, self.OnStop, self.stopButton)
        self.restartButton = wx.Button(panel, -1, 'Restart')
        panel.Bind(wx.EVT_BUTTON, self.OnRestart, self.restartButton)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.startButton, 0, wx.RIGHT, 5)
        sizer.Add(self.stopButton, 0, wx.RIGHT, 5)
        sizer.Add(self.restartButton, 0, wx.RIGHT, 5)
        mainsizer.Add(sizer, 0, wx.EXPAND | wx.ALL, 5)
        panel.SetSizer(mainsizer)
        panel.SetAutoLayout(True)
        return panel

    def OnStart(self, event):
        errors = self.initializeHardware()

    def OnStop(self, event):
        errors = self.shutdownHardware()
        if errors:
            print(('Error shutting down', errors))

    def OnRestart(self, event):
        self.shutdownHardware()
        self.initializeHardware()

    def OnDriverChoice(self, event):
        self.setDirty(True)
        choice = event.GetString()
        page = rs485_drivers.getDriverPageByName(choice)
        self.updateDriverSegment(page)

    def markDirty(self, event=None):
        if event is not None:
            event.Skip()
        self.setDirty(True)
        return

    def updateDriverSegment(self, page):
        self.setDriverSegmentChanged(True)
        if page is None:
            return
        page.setOwner(self)
        self.driverSegment = page
        sizer = self.driverConfigPanel.GetSizer()
        for child in self.driverConfigPanel.GetChildren():
            self.driverConfigPanel.RemoveChild(child)
            if sizer is not None:
                sizer.Remove(child)
            child.Destroy()

        page.createControl(self.driverConfigPanel)
        if sizer is not None:
            sizer.Add(page.getControl(), 1, wx.EXPAND | wx.ALL, 0)
            s = self.driverConfigPanel.GetSizer()
            s.SetItemMinSize(page.getControl(), page.getControl().GetSize())
            self.driverConfigPanel.SetSize(page.getControl().GetSize())
            s.RecalcSizes()
            size = self.driverConfigPanel.GetSize()
            sizer.SetItemMinSize(page.getControl(), size)
        return page

    def getDriverOptions(self):
        keys = rs485_drivers.getRegisteredDeviceKeys()
        names = []
        for key in keys:
            names.append(rs485_drivers.getDriverName(key))

        return names

    def createControl(self, parent):
        self.control = self.createConfigPanel(parent)
        return self.control

    def setData(self, config):
        try:
            self.setDriverConfig(config)
            self.startupInitCheckbox.SetValue(config.get('main', 'startupinit').lower() == 'true')
        except Exception as msg:
            self.setDefaultConfig()

        self.setHardwareInfo(config)
        self.updateStatus()
        htype = hardware.hardwaremanager.getHardwareType(self.description.getHardwareType())
        self.hardwareLabel.SetLabel(htype.getDescription())

    def setHardwareInfo(self, config):
        self.nameField.SetValue(config.get('main', 'name'))

    def updateStatus(self):
        inst = self.description.getInstance()
        if inst is not None:
            self.statusLabel.SetLabel(inst.getStatusText())
            status = inst.getStatus()
            self.stopButton.Enable(status == hardware.hardwaremanager.STATUS_RUNNING)
            self.startButton.Enable(status == hardware.hardwaremanager.STATUS_STOPPED)
            self.restartButton.Enable(status == hardware.hardwaremanager.STATUS_RUNNING)
        return

    def OnHardwareStatusChanged(self, hardware):
        self.updateStatus()

    def setDriverConfig(self, config):
        driverType = config.get('driver', 'type')
        driverName = rs485_drivers.getDriverName(driverType)
        options = self.getDriverOptions()
        idx = options.index(driverName)
        self.driverCombo.SetSelection(idx)
        page = rs485_drivers.getDriverConfigurationPage(driverType)
        self.updateDriverSegment(page)
        page.setData(config)

    def hardwareEvent(self, event):
        if True:
            return
        if event.getType() == hardware.hardwaremanager.EVENT_ERROR:
            msg = "Error: '%s'" % str(event.getData())
            dlg = wx.MessageDialog(self.control, msg, 'Hardware Error', wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            del dlg

    def setDefaultConfig(self):
        self.updateDriverSegment(None)
        self.startupInitCheckbox.SetValue(True)
        return

    def getData(self, config):
        its = self.startupInitCheckbox.IsChecked()
        if its:
            its = 'true'
        else:
            its = 'false'
        config.set('main', 'startupinit', its)
        if not config.has_section('driver'):
            config.add_section('driver')
        driverType = rs485_drivers.getDriverTypeByName(self.driverCombo.GetStringSelection())
        if driverType is not None:
            config.set('driver', 'type', driverType)
        self.driverSegment.getData(config)
        return

    def initializeHardware(self):
        instance = self.getDescription().getInstance()

        class InitializeWithProgressRunner(poi.operation.RunnableWithProgress):
            __module__ = __name__

            def run(self, monitor):
                monitor.beginTask('Initializing ...', 1)
                instance.initialize()
                monitor.worked(1)
                monitor.endTask()

        f = ui.invisibleFrame
        dlg = poi.dialogs.progress.ProgressDialog(f)
        runner = InitializeWithProgressRunner()
        try:
            dlg.run(runner, fork=False)
        except Exception as msg:
            logger.exception(msg)
            poi.dialogs.ExceptionDialog(f, msg.getWrapped(), 'Error Initializing Hardware').ShowModal()

    def shutdownHardware(self):
        """Attempt to shutdown hardware"""
        instance = self.getDescription().getInstance()

        class ShutdownWithProgressRunner(poi.operation.RunnableWithProgress):
            __module__ = __name__

            def run(self, monitor):
                monitor.beginTask('Shutting down ...', 1)
                instance.shutdown()
                monitor.worked(1)
                monitor.endTask()

        f = ui.invisibleFrame
        dlg = poi.dialogs.progress.ProgressDialog(f)
        runner = ShutdownWithProgressRunner()
        try:
            dlg.run(runner, fork=False)
        except Exception as msg:
            logger.exception(msg)
            poi.dialogs.ExceptionDialog(f, msg.getWrapped(), 'Error Shutting Down Hardware').ShowModal()

    def applied(self):
        if not self.isDirty():
            return
        if self.driverSegment.isConfigChanged() or self.getDriverSegmentChanged():
            self.setDriverSegmentChanged(False)
            self.driverSegment.setDirty(False)
            instance = self.getDescription().getInstance()
            wasOn = instance.getStatus() == hardware.hardwaremanager.STATUS_RUNNING
            if wasOn:
                errors = self.shutdownHardware()
                if errors:
                    print(('* ERROR: Cannot shutdown:', errors))
                if errors:
                    return
            instance.setupDriver(self.getDescription())
            if wasOn:
                instance.initialize()

    def dispose(self):
        hardware.userinterface.configurator.ConfigurationPage.dispose(self)
        self.control.Destroy()
