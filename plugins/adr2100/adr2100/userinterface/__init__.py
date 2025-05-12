# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/adr2100/src/adr2100/userinterface/__init__.py
# Compiled at: 2004-12-09 00:49:29
import os, traceback, wx, string, logging, plugins.core.core.utils, plugins.poi.poi.views, plugins.poi.poi.dialogs
import plugins.hardware.hardware.userinterface.configurator, plugins.hardware.hardware.hardwaremanager, plugins.adr2100.adr2100.drivers
import threading, plugins.ui.ui, plugins.poi.poi.operation, time
import plugins.poi.poi.dialogs.progress, plugins.ui.ui.images as uiimages
import plugins.poi.poi.utils.staticwraptext as staticwraptext, py_compile
import plugins.poi.poi.utils.scrolledpanel
logger = logging.getLogger('adr2100.ui')

class ConfigurationPage(plugins.hardware.hardware.userinterface.configurator.ConfigurationPage):
    __module__ = __name__

    def __init__(self):
        plugins.hardware.hardware.userinterface.configurator.ConfigurationPage.__init__(self)
        self.changedDriverSegment = False
        self.requestTimer = None
        self.validateTimer = None
        return

    def getDriverSegmentChanged(self):
        return self.changedDriverSegment

    def setDriverSegmentChanged(self, changed):
        self.changedDriverSegment = changed

    def doCompile(self):
        pass

    def createConfigPanel(self, parent):
        panel = plugins.poi.poi.utils.scrolledpanel.ScrolledPanel(parent)
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
        sizer.Add(nameField, 1, wx.EXPAND)
        sizer.Add(statusLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
        sizer.Add(self.statusLabel, 1, wx.EXPAND)
        boxSizer.Add(sizer, 1, wx.EXPAND | wx.ALL, 5)
        mainsizer.Add(boxSizer, 0, wx.EXPAND | wx.ALL, 5)
        checkBox = wx.StaticBox(panel, -1, ' Safety Check Settings ')
        boxSizer = wx.StaticBoxSizer(checkBox, wx.VERTICAL)
        h2sizer = wx.BoxSizer(wx.HORIZONTAL)
        h2sizer.Add(wx.StaticText(panel, -1, 'Check Interval:'), 0, wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL, 2)
        self.checkInterval = wx.TextCtrl(panel, -1)
        h2sizer.Add(self.checkInterval, 0, wx.ALL | wx.ALIGN_CENTRE_VERTICAL, 2)
        h2sizer.Add(wx.StaticText(panel, -1, ' seconds'), 0, wx.ALIGN_LEFT | wx.ALIGN_CENTRE_VERTICAL | wx.ALL, 2)
        boxSizer.Add(h2sizer, 0, wx.EXPAND | wx.ALL, 2)
        panel.Bind(wx.EVT_TEXT, self.OnCheckInterval, self.checkInterval)
        inbox = wx.Panel(panel, -1, style=wx.SIMPLE_BORDER)
        inbox.SetBackgroundColour(wx.Colour(246, 232, 175))
        msg = 'The code below will be executed periodically.'
        helpText = staticwraptext.StaticWrapText(inbox, -1, msg)
        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(helpText, 1, wx.EXPAND | wx.ALL, 5)
        inbox.SetSizer(s)
        self.requestCodeText = wx.TextCtrl(panel, -1, style=wx.SUNKEN_BORDER | wx.TE_MULTILINE | wx.TE_PROCESS_TAB)
        panel.Bind(wx.EVT_TEXT, self.OnRequestCodeChanged, self.requestCodeText)
        self.requestCodeErrorIcon = wx.StaticBitmap(panel, -1, uiimages.getImage(uiimages.ERROR_ICON))
        self.requestCodeErrorText = wx.StaticText(panel, -1)
        boxSizer.Add(inbox, 0, wx.EXPAND | wx.ALL, 2)
        boxSizer.Add(self.requestCodeText, 1, wx.EXPAND | wx.ALL, 5)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(self.requestCodeErrorIcon, 0, wx.ALL | wx.ALIGN_CENTRE_VERTICAL, 1)
        hsizer.Add(self.requestCodeErrorText, 1, wx.ALL | wx.EXPAND, 1)
        boxSizer.Add(hsizer, 0, wx.EXPAND | wx.ALL, 2)
        inbox = wx.Panel(panel, -1, style=wx.SIMPLE_BORDER)
        inbox.SetBackgroundColour(wx.Colour(246, 232, 175))
        msg = 'The code below is used to validate the state of this node in the interlock mechanism.\n\r' + "Set the variable 'valid' to the proper value. It is set to True at the entrance of this code."
        helpText = staticwraptext.StaticWrapText(inbox, -1, msg)
        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(helpText, 1, wx.EXPAND | wx.ALL, 5)
        inbox.SetSizer(s)
        self.validationCodeText = wx.TextCtrl(panel, -1, style=wx.SUNKEN_BORDER | wx.TE_MULTILINE | wx.TE_PROCESS_TAB)
        panel.Bind(wx.EVT_TEXT, self.OnValidationCodeChanged, self.validationCodeText)
        self.validationCodeErrorIcon = wx.StaticBitmap(panel, -1, uiimages.getImage(uiimages.ERROR_ICON))
        self.validationCodeErrorText = wx.StaticText(panel, -1)
        boxSizer.Add(inbox, 0, wx.EXPAND | wx.ALL, 2)
        boxSizer.Add(self.validationCodeText, 1, wx.EXPAND | wx.ALL, 5)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(self.validationCodeErrorIcon, 0, wx.ALL | wx.ALIGN_CENTRE_VERTICAL, 1)
        hsizer.Add(self.validationCodeErrorText, 1, wx.ALL | wx.EXPAND, 1)
        boxSizer.Add(hsizer, 0, wx.EXPAND | wx.ALL, 2)
        self.setCodeError(None)
        self.setValidationError(None)
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
        self.driverConfigPanel = wx.Panel(panel, -1)
        boxSizer.Add(sizer, 0, wx.EXPAND | wx.ALL, 5)
        boxSizer.Add(wx.StaticLine(panel, -1), 0, wx.EXPAND | wx.ALL, 5)
        boxSizer.Add(self.driverConfigPanel, 1, wx.EXPAND | wx.ALL, 5)
        mainsizer.Add(boxSizer, 0, wx.EXPAND | wx.ALL, 5)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.driverConfigPanel.SetSizer(sizer)
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
        panel.SetupScrolling()
        return panel

    def OnCheckInterval(self, event):
        event.Skip()
        self.setDirty(True)

    def OnRequestCodeChanged(self, event):
        event.Skip()
        if self.requestTimer is not None and self.requestTimer.isAlive():
            self.requestTimer.cancel()
        self.requestTimer = threading.Timer(1, self.compileRequest)
        self.requestTimer.start()
        self.setDirty(True)
        return

    def OnValidationCodeChanged(self, event):
        event.Skip()
        if self.validateTimer is not None and self.validateTimer.isAlive():
            self.validateTimer.cancel()
        self.validateTimer = threading.Timer(1, self.compileValidation)
        self.validateTimer.start()
        self.setDirty(True)
        return

    def compileString(self, codeStr, name):
        try:
            code = py_compile.compile(codeStr, name, 'exec')
            return (True, code)
        except Exception as msg:
            logger.exception(msg)
            return (
             False, str(msg))

    def getCompileRequestValue(self):
        s = self.requestCodeText.GetValue()
        s += '\n\r'
        return s

    def getValidateRequestValue(self):
        s = self.validationCodeText.GetValue()
        s += '\n\r'
        return s

    def compileRequest(self):
        self.requestTimer = None
        str = self.getCompileRequestValue()
        (valid, codeOrMsg) = self.compileString(str, '__request__')
        if not valid:
            self.setCodeError(codeOrMsg)
        else:
            self.setCodeError(None)
        return

    def compileValidation(self):
        self.validateTimer = None
        str = self.getValidateRequestValue()
        (valid, codeOrMsg) = self.compileString(str, '__validation__')
        if not valid:
            self.setValidationError(codeOrMsg)
        else:
            self.setValidationError(None)
        return

    def setCodeError(self, text):

        def doit():
            if text is None:
                self.requestCodeErrorText.SetLabel('Code OK')
            else:
                self.requestCodeErrorText.SetLabel(text)
            self.requestCodeErrorIcon.Show(text is not None)
            return

        wx.CallAfter(doit)

    def setValidationError(self, text):

        def doit():
            if text is None:
                self.validationCodeErrorText.SetLabel('Code OK')
            else:
                self.validationCodeErrorText.SetLabel(text)
            self.validationCodeErrorIcon.Show(text is not None)
            return

        wx.CallAfter(doit)

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
        page = plugins.adr2100.adr2100.drivers.getDriverPageByName(choice)
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
            sizer.Add(page.getControl(), 1, wx.EXPAND | wx.ALL, 0)
            s = self.driverConfigPanel.GetSizer()
            s.SetItemMinSize(page.getControl(), page.getControl().GetSize())
            self.driverConfigPanel.SetSize(page.getControl().GetSize())
            s.RecalcSizes()
            size = self.driverConfigPanel.GetSize()
            sizer.SetItemMinSize(page.getControl(), size)
            self.control.SetupScrolling()
        return page

    def getDriverOptions(self):
        keys = plugins.adr2100.adr2100.drivers.getRegisteredDeviceKeys()
        names = []
        for key in keys:
            names.append(plugins.adr2100.adr2100.drivers.getDriverName(key))

        return names

    def createControl(self, parent):
        self.control = self.createConfigPanel(parent)
        return self.control

    def setData(self, config):
        inst = self.getDescription().getInstance()
        try:
            self.setDriverConfig(config)
        except Exception as msg:
            logger.exception(msg)
            self.setDefaultConfig()

        self.setHardwareInfo(config)
        self.updateStatus()
        self.requestCodeText.SetValue(inst.loadRequestCode())
        self.validationCodeText.SetValue(inst.loadValidationCode())
        self.checkInterval.SetValue(str(inst.getValidationInterval()))

    def createName(self, prefix):
        inst = self.getDescription().getInstance()
        return inst.createCodeFileName(prefix)

    def setHardwareInfo(self, config):
        self.nameField.SetValue(config.get('main', 'name'))

    def updateStatus(self):
        inst = self.description.getInstance()

    def OnHardwareStatusChanged(self, hardware):
        self.updateStatus()

    def setDriverConfig(self, config):
        driverType = config.get('driver', 'type')
        driverName = plugins.adr2100.adr2100.drivers.getDriverName(driverType)
        options = self.getDriverOptions()
        idx = options.index(driverName)
        self.driverCombo.SetSelection(idx)
        page = plugins.adr2100.adr2100.drivers.getDriverConfigurationPage(driverType)
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
        return

    def getData(self, config):
        if not config.has_section('driver'):
            config.add_section('driver')
        driverType = plugins.adr2100.adr2100.drivers.getDriverTypeByName(self.driverCombo.GetStringSelection())
        config.set('main', 'startupinit', 'true')
        if driverType is not None:
            config.set('driver', 'type', driverType)
        self.driverSegment.getData(config)
        inst = self.getDescription().getInstance()
        inst.writeRequestCode(self.getCompileRequestValue())
        inst.writeValidateCode(self.getValidateRequestValue())
        val = 0.5
        try:
            val = float(self.checkInterval.GetValue())
        except Exception as msg:
            logger.exception(msg)

        config.set('main', 'checkInterval', str(val))
        inst.setValidationInterval(val)
        return

    def initializeHardware(self):
        instance = self.getDescription().getInstance()

        class InitializeWithProgressRunner(plugins.poi.poi.operation.RunnableWithProgress):
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
                except Exception as msg:
                    logger.exception(msg)
                    canceller.done = True
                    exc = plugins.core.core.utils.WrappedException()

                monitor.worked(1)
                monitor.endTask()
                done = True
                canceller.join()
                if exc:
                    raise exc
                return

        f = plugins.ui.ui.invisibleFrame
        dlg = plugins.poi.poi.dialogs.progress.ProgressDialog(f)
        dlg.setCancelable(True)
        runner = InitializeWithProgressRunner()
        try:
            dlg.run(runner, fork=False)
        except Exception as invocation:
            logger.exception(invocation)
            plugins.poi.poi.dialogs.ExceptionDialog(f, invocation, 'Error Initializing Hardware').ShowModal()

    def shutdownHardware(self):
        """Attempt to shutdown hardware"""
        instance = self.getDescription().getInstance()

        class ShutdownWithProgressRunner(plugins.poi.poi.operation.RunnableWithProgress):
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
                except Exception as msg:
                    logger.exception(msg)

                monitor.worked(1)
                monitor.endTask()
                done = True
                cancelator.join()

        f = plugins.ui.ui.invisibleFrame
        dlg = plugins.poi.poi.dialogs.progress.ProgressDialog(f)
        dlg.setCancelable(True)
        runner = ShutdownWithProgressRunner()
        try:
            dlg.run(runner, fork=False)
        except Exception as msg:
            logger.exception(msg)
            plugins.poi.poi.dialogs.ExceptionDialog(f, str(msg), 'Error Shutting Down Hardware').ShowModal()

    def applied(self):
        if not self.isDirty():
            return
        if self.driverSegment.isConfigChanged() or self.getDriverSegmentChanged():
            self.setDriverSegmentChanged(False)
            self.driverSegment.setDirty(False)
            instance = self.getDescription().getInstance()
            wasOn = instance.getStatus() == plugins.hardware.hardware.hardwaremanager.STATUS_RUNNING
            if wasOn:
                errors = self.shutdownHardware()
                if errors:
                    return
            instance.setupDriver(self.getDescription())
            if wasOn:
                instance.initialize()

    def dispose(self):
        plugins.hardware.hardware.userinterface.configurator.ConfigurationPage.dispose(self)
        self.control.Destroy()
