# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/mkspdr2000/src/mkspdr2000/userinterface/__init__.py
# Compiled at: 2004-11-23 21:55:51
import validator, wx, ui, time, core.utils, string, logging, poi.views, poi.dialogs, hardware.userinterface.configurator, hardware.hardwaremanager, mkspdr2000.drivers, mkspdr2000.userinterface.initdialog, threading, poi.operation, poi.dialogs.progress
logger = logging.getLogger('mkspdr2000.ui')

class DeviceHardwareEditor(hardware.userinterface.DeviceHardwareEditor):
    __module__ = __name__

    def __init__(self):
        hardware.userinterface.DeviceHardwareEditor.__init__(self)
        self.control = None
        return

    def createControl(self, parent):
        self.control = wx.Panel(parent, -1)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.control.SetSizer(sizer)
        self.control.SetAutoLayout(True)
        return self.control

    def setData(self, recipe, data):
        global logger
        try:
            pass
        except Exception as msg:
            logger.warning("Unable to set data for device entry: '%s'" % msg)
            logger.exception(msg)

    def getData(self, data):
        pass


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
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.driverConfigPanel.SetSizer(sizer)
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

    def OnRestart(self, event):
        self.shutdownHardware()
        self.initializeHardware()

    def OnDriverChoice(self, event):
        self.setDirty(True)
        choice = event.GetString()
        page = mkspdr2000.drivers.getDriverPageByName(choice)
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
        keys = mkspdr2000.drivers.getRegisteredDeviceKeys()
        names = []
        for key in keys:
            names.append(mkspdr2000.drivers.getDriverName(key))

        return names

    def createControl(self, parent):
        self.control = self.createConfigPanel(parent)
        return self.control

    def setData(self, config):
        inst = self.getDescription().getInstance()
        try:
            self.setDriverConfig(config)
            self.startupInitCheckbox.SetValue(config.get('main', 'startupinit').lower() == 'true')
        except Exception as msg:
            self.setDefaultConfig()

        self.setHardwareInfo(config)
        self.updateStatus()

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
        driverName = mkspdr2000.drivers.getDriverName(driverType)
        options = self.getDriverOptions()
        idx = options.index(driverName)
        self.driverCombo.SetSelection(idx)
        page = mkspdr2000.drivers.getDriverConfigurationPage(driverType)
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
        if not config.has_section('driver'):
            config.add_section('driver')
        driverType = mkspdr2000.drivers.getDriverTypeByName(self.driverCombo.GetStringSelection())
        if driverType is not None:
            config.set('driver', 'type', driverType)
        self.driverSegment.getData(config)
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
            (e, v, t) = invocation.getWrapped()
            poi.dialogs.ExceptionDialog(f, v, 'Error Initializing Hardware').ShowModal()

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
