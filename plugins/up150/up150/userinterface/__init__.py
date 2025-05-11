# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/up150/src/up150/userinterface/__init__.py
# Compiled at: 2004-11-23 22:00:44
import validator, wx, ui, time, string, logging, core.utils, poi.views, poi.dialogs, hardware.userinterface.configurator, hardware.hardwaremanager, up150.drivers, up150.userinterface.initdialog, up150.messages as messages, threading, poi.operation, poi.dialogs.progress, wx.lib.colourselect as colourselect
logger = logging.getLogger('up150.ui')

def color2str(color):
    return '%d,%d,%d' % (color.Red(), color.Green(), color.Blue())


def parseColor(colorStr):
    return wx.Color(*list(map(int, colorStr.split(','))))


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

        self.channelChoice = wx.ComboBox(self.control, -1, choices=list(map(modapp, list(range(self.instance.getChannelCount())))), style=wx.CB_READONL)
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
        label = wx.StaticText(self.control, -1, 'PID:')
        self.pidProportional = wx.TextCtrl(self.control, -1, '')
        self.pidIntegral = wx.TextCtrl(self.control, -1, '')
        self.pidDerivated = wx.TextCtrl(self.control, -1, '')
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        h2sizer.Add(pidProportional, 1, wx.LEFT, 5)
        h2sizer.Add(pidIntegral, 1, wx.LEFT, 5)
        h2sizer.Add(pidDerivative, 1, wx.LEFT, 5)
        fsizer.Add(label, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
        fsizer.Add(h2sizer, 1, wx.ALIGN_CENTRE_VERTICAL)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(fsizer, 1, wx.GROW | wx.ALL)
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
        sizer.Add(nameField, 1, wx.GROW | wx.ALIGN_CENTRE_VERTICAL)
        sizer.Add(statusLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
        sizer.Add(self.statusLabel, 1, wx.GROW | wx.ALIGN_CENTRE_VERTICAL)
        boxSizer.Add(sizer, 1, wx.GROW | wx.ALL, 5)
        mainsizer.Add(boxSizer, 0, wx.GROW | wx.ALL, 5)
        infoBox = wx.StaticBox(panel, -1, ' Device Driver ')
        boxSizer = wx.StaticBoxSizer(infoBox, wx.VERTICAL)
        driverLabel = wx.StaticText(panel, -1, 'Driver Type:')
        self.driverCombo = wx.ComboBox(panel, -1, choices=self.getDriverOptions(), style=wx.CB_READONLY)
        panel.Bind(wx.EVT_COMBOBOX, self.OnDriverChoice, self.driverCombo)
        sizer = wx.FlexGridSizer(0, 2, 5, 5)
        sizer.AddGrowableCol(1)
        sizer.Add(driverLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
        sizer.Add(self.driverCombo, 1, wx.ALIGN_CENTRE_VERTICAL)
        self.driverConfigPanel = wx.Panel(panel, -1, size=(300, 150))
        boxSizer.Add(sizer, 0, wx.GROW | wx.ALL, 5)
        boxSizer.Add(wx.StaticLine(panel, -1), 0, wx.GROW | wx.ALL, 5)
        boxSizer.Add(self.driverConfigPanel, 1, wx.GROW | wx.ALL, 5)
        mainsizer.Add(boxSizer, 0, wx.GROW | wx.ALL, 5)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.driverConfigPanel.SetSizer(sizer)
        infoBox = wx.StaticBox(panel, -1, ' General Options ')
        boxSizer = wx.StaticBoxSizer(infoBox, wx.VERTICAL)
        self.pidControls = {}
        self.pidControls['p'] = wx.TextCtrl(panel, -1, '')
        self.pidControls['i'] = wx.TextCtrl(panel, -1, '')
        self.pidControls['d'] = wx.TextCtrl(panel, -1, '')
        h2sizer = wx.BoxSizer(wx.HORIZONTAL)
        h2sizer.Add(wx.StaticText(panel, -1, 'PID Settings:'), 0, wx.ALIGN_RIGHT | wx.RIGHT | wx.ALIGN_CENTRE_VERTICAL, 5)
        h2sizer.Add(self.pidControls['p'], 1, wx.RIGHT | wx.ALIGN_CENTRE_VERTICAL, 5)
        h2sizer.Add(self.pidControls['i'], 1, wx.RIGHT | wx.ALIGN_CENTRE_VERTICAL, 5)
        h2sizer.Add(self.pidControls['d'], 1, wx.ALIGN_CENTRE_VERTICAL)
        self.startupInitCheckbox = wx.CheckBox(panel, -1, 'Initialize hardware on Startup')
        panel.Bind(wx.EVT_CHECKBOX, self.markDirty, self.startupInitCheckbox)
        list(map((lambda c: panel.Bind(wx.EVT_TEXT, self.markDirty, c)), list(self.pidControls.values())))
        boxSizer.Add(h2sizer, 0, wx.GROW | wx.ALL, 5)
        boxSizer.Add(self.startupInitCheckbox, 0, wx.GROW | wx.ALL, 5)
        sb = wx.StaticBox(panel, -1, ' Default Recipe Device Options ')
        sbsizer = wx.StaticBoxSizer(sb, wx.VERTICAL)
        fsizer = wx.FlexGridSizer(1, 2, 5, 5)
        fsizer.AddGrowableCol(1)
        fsizer.Add(wx.StaticText(panel, -1, messages.get('dialog.hwconfig.default.device.color.label')), 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
        self.devicePlotColor = colourselect.ColourSelect(panel, -1, size=(60, 20))
        fsizer.Add(self.devicePlotColor, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTRE_VERTICAL)
        sbsizer.Add(fsizer, 1, wx.GROW | wx.ALL, 5)
        mainsizer.Add(boxSizer, 0, wx.GROW | wx.ALL, 5)
        mainsizer.Add(sbsizer, 0, wx.GROW | wx.ALL, 5)
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
        mainsizer.Add(sizer, 0, wx.GROW | wx.ALL, 5)
        panel.SetSizer(mainsizer)
        panel.SetAutoLayout(True)
        return panel

    def OnStart(self, event):
        errors = self.initializeHardware()

    def OnStop(self, event):
        errors = self.shutdownHardware()

    def OnRestart(self, event):
        self.shutdownHardware()
        self.initializeHardware()

    def OnDriverChoice(self, event):
        self.setDirty(True)
        choice = event.GetString()
        page = up150.drivers.getDriverPageByName(choice)
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
            sizer.Add(page.getControl(), 1, wx.GROW | wx.ALL, 0)
            s = page.getControl().GetSizer()
            s.SetItemMinSize(page.getControl(), page.getControl().GetSize())
            self.driverConfigPanel.SetSize(page.getControl().GetSize())
            s.RecalcSizes()
            size = self.driverConfigPanel.GetSize()
            sizer.SetItemMinSize(page.getControl(), size)
            self.control.Layout()
        self.control.Refresh()
        return page
        return

    def getDriverOptions(self):
        keys = up150.drivers.getRegisteredDeviceKeys()
        names = []
        for key in keys:
            names.append(up150.drivers.getDriverName(key))

        return names

    def createControl(self, parent):
        self.control = self.createConfigPanel(parent)
        return self.control

    def setData(self, config):
        inst = self.getDescription().getInstance()
        try:
            self.setDriverConfig(config)
            self.startupInitCheckbox.SetValue(config.get('main', 'startupinit').lower() == 'true')
            pid = inst.getPIDSettings()
            if pid is not None:
                list(map((lambda c, s: c.SetValue(str(s))), list(self.pidControls.values()), pid))
        except Exception as msg:
            self.setDefaultConfig()

        self.setHardwareInfo(config)
        self.updateStatus()
        if config.has_section('default.device.props'):
            try:
                self.devicePlotColor.SetValue(parseColor(config.get('default.device.props', 'plot.color')))
            except Exception as msg:
                logger.exception(msg)

        return

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
        driverName = up150.drivers.getDriverName(driverType)
        options = self.getDriverOptions()
        idx = options.index(driverName)
        self.driverCombo.SetSelection(idx)
        page = up150.drivers.getDriverConfigurationPage(driverType)
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
        inst = self.getDescription().getInstance()
        its = self.startupInitCheckbox.IsChecked()
        if its:
            its = 'true'
        else:
            its = 'false'
        config.set('main', 'startupinit', its)
        (p, i, d) = list(map((lambda s: s.strip()), list(map((lambda c: c.GetValue()), list(self.pidControls.values())))))
        if not 0 in list(map((lambda i: len(i)), (p, i, d))):
            inst.setPIDSettings((p, i, d))
        else:
            inst.setPIDSettings(None)
        if not config.has_section('driver'):
            config.add_section('driver')
        driverType = up150.drivers.getDriverTypeByName(self.driverCombo.GetStringSelection())
        if driverType is not None:
            config.set('driver', 'type', driverType)
        self.driverSegment.getData(config)
        if not config.has_section('default.device.props'):
            config.add_section('default.device.props')
        config.set('default.device.props', 'plot.color', color2str(self.devicePlotColor.GetValue()))
        return

    def initializeHardware(self):
        instance = self.getDescription().getInstance()

        class InitializeWithProgressRunner(poi.operation.RunnableWithProgress):
            __module__ = __name__

            def run(self, monitor):
                done = False

                class Cancelator(threading.Thread):
                    __module__ = __name__

                    def run(innerself):
                        while not done:
                            if monitor.isCanceled():
                                instance.interruptOperation()
                                return
                            time.sleep(0.25)

                cancelator = Cancelator()
                cancelator.start()
                monitor.beginTask('Initializing ...', 1)
                exc = None
                try:
                    instance.initialize()
                except Exception as msg:
                    logger.exception(msg)
                    done = True
                    exc = core.utils.WrappedException()

                monitor.worked(1)
                monitor.endTask()
                done = True
                cancelator.join()
                if exc is not None:
                    raise exc
                return

        f = ui.invisibleFrame
        dlg = poi.dialogs.progress.ProgressDialog(f)
        dlg.setCancelable(True)
        runner = InitializeWithProgressRunner()
        try:
            dlg.run(runner, fork=False)
        except Exception as invocation:
            logger.exception(invocation)
            poi.dialogs.ExceptionDialog(f, msg.getWrapped()[1], 'Error Initializing Hardware').ShowModal()

    def shutdownHardware(self):
        """Attempt to shutdown hardware"""
        instance = self.getDescription().getInstance()

        class ShutdownWithProgressRunner(poi.operation.RunnableWithProgress):
            __module__ = __name__

            def run(self, monitor):
                done = False

                class Cancelator(threading.Thread):
                    __module__ = __name__

                    def run(innerself):
                        while not done:
                            if monitor.isCanceled():
                                instance.interruptOperation()
                                return
                            time.sleep(0.25)

                cancelator = Cancelator()
                cancelator.start()
                monitor.beginTask('Shutting down ...', 1)
                instance.shutdown()
                monitor.worked(1)
                monitor.endTask()
                done = True
                cancelator.join()

        f = ui.invisibleFrame
        dlg = poi.dialogs.progress.ProgressDialog(f)
        dlg.setCancelable(True)
        runner = ShutdownWithProgressRunner()
        try:
            dlg.run(runner, fork=False)
        except Exception as msg:
            logger.exception(msg)
            poi.dialogs.ExceptionDialog(f, msg.getWrapped(), 'Error Shutting Down Hardware').ShowModal()

    def applied(self):
        if not self.isDirty():
            return
        validator.getDefault().nudge()
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
        del self.control
