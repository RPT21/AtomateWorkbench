# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/mks146/src/mks146/userinterface/__init__.py
# Compiled at: 2004-11-23 21:58:29
import traceback, wx, logging, core.utils, poi.views, poi.dialogs, hardware.userinterface.configurator, hardware.hardwaremanager, mks146.drivers, mks146.userinterface.initdialog, threading, ui, poi.operation, time, poi.dialogs.progress, mfc.messages as messages, ui.images as uiimages
RANGES = [
 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
CHANNEL_CHOICES = [
 '4', '8']
logger = logging.getLogger('mks146.ui')

def getUnitChoices():
    return UNITS


def getRangeChoices():
    global RANGES
    return RANGES


class DeviceHardwareEditor(hardware.userinterface.DeviceHardwareEditor):
    __module__ = __name__

    def __init__(self):
        hardware.userinterface.DeviceHardwareEditor.__init__(self)
        self.control = None
        return

    def getChannelChoices(self):

        def modapp(i):
            return str(i + 1)

        lst = [
         'None']
        lst.extend(map((lambda i: str(i + 1)), range(4)))
        return lst

    def createControl(self, parent):
        self.control = wx.Panel(parent, -1, style=0)
        label = wx.StaticText(self.control, -1, 'Channel:')
        self.channelChoice = wx.ComboBox(self.control, -1, choices=self.getChannelChoices(), style=wx.CB_READONLY)
        fsizer = wx.FlexGridSizer(0, 3, 5, 5)
        self.channelErrorMsg = wx.Panel(self.control)
        self.channelErrorMsg.Show(False)
        ceSizer = wx.BoxSizer()
        ceSizer.Add(wx.StaticBitmap(self.channelErrorMsg, -1, uiimages.getImage(uiimages.ERROR_ICON)), 0, wx.GROW)
        ceSizer.Add(wx.StaticText(self.channelErrorMsg, -1, messages.get('device.conflictingchannels.message')), 1, wx.GROW)
        self.channelErrorMsg.SetSizer(ceSizer)
        self.channelErrorMsg.SetAutoLayout(True)
        fsizer.Add(label, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
        fsizer.Add(self.channelChoice, 0, wx.ALIGN_CENTRE_VERTICAL)
        fsizer.Add(self.channelErrorMsg, 0, wx.ALIGN_CENTRE_VERTICAL | wx.LEFT, 5)
        label = wx.StaticText(self.control, -1, 'Range:')
        self.rangeChoice = wx.ComboBox(self.control, -1, style=wx.CB_READONLY, choices=map(str, getRangeChoices()))
        fsizer.Add(label, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
        fsizer.Add(self.rangeChoice, 0, wx.ALIGN_CENTRE_VERTICAL)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(fsizer, 1, wx.GROW | wx.ALL)
        self.control.SetSizer(sizer)
        self.control.SetAutoLayout(True)
        self.control.Bind(wx.EVT_COMBOBOX, self.OnChannelSelected, self.channelChoice)
        self.control.Bind(wx.EVT_COMBOBOX, self.OnRangeSelected, self.rangeChoice)
        return self.control

    def OnChannelSelected(self, event):
        valid = self.owner.channelSelected(self.channelChoice.GetSelection())
        self.channelErrorMsg.Show(not valid)

    def OnUnitSelected(self, event):
        event.Skip()
        self.selectUnit(self.unitsChoice.GetSelection())
        self.rangeChoice.SetSelection(0)

    def selectUnit(self, unitIdx):
        self.rangeChoice.Clear()
        ranges = getRangeChoices()
        for value in ranges:
            self.rangeChoice.Append(str(value))

    def selectChannel(self, channelNumStr):
        self.channelChoice.SetSelection(channelNumStr)

    def selectRange(self, rangeStr):
        self.rangeChoice.SetSelection(rangeStr)
        self.owner.setMax(int(getRangeChoices()[self.rangeChoice.GetSelection()]))

    def OnRangeSelected(self, event):
        event.Skip()
        self.owner.setMax(int(getRangeChoices()[self.rangeChoice.GetSelection()]))

    def setData(self, recipe, data):
        global logger
        try:
            channelNum = int(data.getChildNamed('channel').getValue())
            gcf = data.getChildNamed('conversion-factor').getValue()
            rangeValue = data.getChildNamed('range').getValue()
            self.selectRange(getRangeChoices().index(int(rangeValue)))
            self.selectChannel(self.getChannelChoices().index(str(channelNum)))
        except Exception, msg:
            logger.warning("Unable to set data for device entry: '%s'" % msg)
            logger.exception(msg)

    def getData(self, data):
        channelNum = self.getChannelChoices()[self.channelChoice.GetSelection()]
        rangeValue = getRangeChoices()[self.rangeChoice.GetSelection()]
        if channelNum == 'None':
            channelNum = ''
        data.createChildIfNotExists('channel').setValue(str(channelNum))
        data.createChildIfNotExists('units').setValue('sccm')
        data.createChildIfNotExists('range').setValue(str(rangeValue))


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
        panel = poi.utils.scrolledpanel.ScrolledPanel(parent)
        mainsizer = wx.BoxSizer(wx.VERTICAL)
        infoBox = wx.StaticBox(panel, -1, ' Hardware Information ', style=0)
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
        infoBox = wx.StaticBox(panel, -1, ' Hardware ')
        boxSizer = wx.StaticBoxSizer(infoBox, wx.VERTICAL)
        fsizer = wx.FlexGridSizer(0, 2, 5, 5)
        label = wx.StaticText(panel, -1, 'Number of Channels:')
        self.channelsChoice = wx.ComboBox(panel, -1, choices=CHANNEL_CHOICES, style=wx.CB_READONLY)
        panel.Bind(wx.EVT_COMBOBOX, self.markDirty, self.channelsChoice)
        fsizer.Add(label, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
        fsizer.Add(self.channelsChoice, 0, wx.ALIGN_CENTRE_VERTICAL)
        boxSizer.Add(fsizer, 1, wx.GROW | wx.ALL, 5)
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
        self.driverConfigPanel = wx.Panel(panel, -1)
        boxSizer.Add(sizer, 0, wx.GROW | wx.ALL, 5)
        boxSizer.Add(wx.StaticLine(panel, -1), 0, wx.GROW | wx.ALL, 5)
        boxSizer.Add(self.driverConfigPanel, 1, wx.GROW | wx.ALL, 5)
        mainsizer.Add(boxSizer, 0, wx.GROW | wx.ALL, 5)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.driverConfigPanel.SetSizer(sizer)
        infoBox = wx.StaticBox(panel, -1, ' General Options ')
        boxSizer = wx.StaticBoxSizer(infoBox, wx.VERTICAL)
        self.startupInitCheckbox = wx.CheckBox(panel, -1, 'Initialize hardware on Startup')
        panel.Bind(wx.EVT_CHECKBOX, self.markDirty, self.startupInitCheckbox)
        boxSizer.Add(self.startupInitCheckbox, 0, wx.GROW | wx.ALL, 5)
        mainsizer.Add(boxSizer, 0, wx.GROW | wx.ALL, 5)
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
        panel.SetupScrolling()
        return panel

    def OnStart(self, event):
        self.initializeHardware()

    def OnStop(self, event):
        self.shutdownHardware()

    def OnRestart(self, event):
        self.shutdownHardware()
        self.initializeHardware()

    def OnDriverChoice(self, event):
        self.setDirty(True)
        choice = event.GetString()
        page = mks146.drivers.getDriverPageByName(choice)
        wx.CallAfter(self.updateDriverSegment, page)

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
        s = page.getControl().GetSizer()
        if sizer is not None:
            sizer.Add(page.getControl(), 1, wx.GROW | wx.ALL, 0)
            s = self.driverConfigPanel.GetSizer()
            s.SetItemMinSize(page.getControl(), page.getControl().GetSize())
            self.driverConfigPanel.SetSize(page.getControl().GetSize())
            s.RecalcSizes()
            size = self.driverConfigPanel.GetSize()
            sizer.SetItemMinSize(page.getControl(), size)
            self.control.SetupScrolling()
        return page
        return

    def getDriverOptions(self):
        keys = mks146.drivers.getRegisteredDeviceKeys()
        names = []
        for key in keys:
            names.append(mks146.drivers.getDriverName(key))

        return names

    def createControl(self, parent):
        self.control = self.createConfigPanel(parent)
        return self.control

    def setData(self, config):
        try:
            self.setDriverConfig(config)
            self.startupInitCheckbox.SetValue(config.get('main', 'startupinit').lower() == 'true')
        except Exception, msg:
            logger.exception(msg)
            self.setDefaultConfig()

        self.setHardwareInfo(config)
        self.updateStatus()
        try:
            numChannels = config.get('main', 'channels')
            self.channelsChoice.SetSelection(CHANNEL_CHOICES.index(numChannels))
        except Exception, msg:
            print '* WARNING: Exception while setting channel numbers:', msg
            self.channelsChoice.SetSelection(0)

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
        driverName = mks146.drivers.getDriverName(driverType)
        options = self.getDriverOptions()
        idx = options.index(driverName)
        self.driverCombo.SetSelection(idx)
        page = mks146.drivers.getDriverConfigurationPage(driverType)
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
        driverType = mks146.drivers.getDriverTypeByName(self.driverCombo.GetStringSelection())
        if driverType is not None:
            config.set('driver', 'type', driverType)
        self.driverSegment.getData(config)
        numChannels = self.channelsChoice.GetStringSelection()
        config.set('main', 'channels', numChannels)
        return

    def initializeHardware(self):
        instance = self.getDescription().getInstance()

        class InitializeWithProgressRunner(poi.operation.RunnableWithProgress):
            __module__ = __name__

            def run(self, monitor):
                done = False

                class Canceller(threading.Thread):
                    __module__ = __name__

                    def run(innerself):
                        while not done:
                            if monitor.isCanceled():
                                instance.interruptOperation()
                                return
                            time.sleep(0.25)

                canceller = Canceller()
                canceller.start()
                exc = None
                monitor.beginTask('Initializing ...', 1)
                try:
                    instance.initialize()
                except Exception, msg:
                    logger.exception(msg)
                    canceller.done = True
                    exc = core.util.WrappedException()

                monitor.worked(1)
                monitor.endTask()
                done = True
                canceller.join()
                if exc:
                    raise exc
                return

        f = ui.invisibleFrame
        dlg = poi.dialogs.progress.ProgressDialog(f)
        dlg.setCancelable(True)
        runner = InitializeWithProgressRunner()
        try:
            dlg.run(runner, fork=False)
        except Exception, invocation:
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
                monitor.beginTask('Shutting down dff...', 1)
                try:
                    instance.shutdown()
                except Exception, msg:
                    logger.exception(msg)

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
        except Exception, msg:
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
                    return
            instance.setupDriver(self.getDescription())
            if wasOn:
                instance.initialize()

    def dispose(self):
        hardware.userinterface.configurator.ConfigurationPage.dispose(self)
        self.control.Destroy()
