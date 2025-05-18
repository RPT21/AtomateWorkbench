# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/mkspdr2000/src/mkspdr2000/drivers/simulation.py
# Compiled at: 2004-11-23 21:54:18
import wx, plugins.mkspdr2000.mkspdr2000.drivers as mkspdr2000_drivers
import plugins.poi.poi as poi, plugins.poi.poi.actions
import plugins.ui.ui as ui

OUTPUT = 0
INPUT = 1


class SimConfigurationSegment(object):
    __module__ = __name__

    def __init__(self):
        self.complete = True
        self.dirty = False

    def setDirty(self, dirty):
        self.dirty = dirty

    def getControl(self):
        return self.control

    def setOwner(self, owner):
        self.owner = owner

    def createControl(self, composite):
        self.control = wx.Panel(composite, -1)
        sizer = wx.BoxSizer(wx.VERTICAL)
        label = wx.StaticText(self.control, -1, 'Simulation driver')
        label.Enable(False)
        sizer.Add(label, 1, wx.EXPAND | wx.ALL, 5)
        self.control.SetSizer(sizer)
        return self.control

    def isConfigChanged(self):
        return False

    def setData(self, data):
        pass

    def getData(self, data):
        pass

    def setComplete(self, complete):
        self.complete = complete

    def isComplete(self):
        return self.complete


class ShowPanelAction(poi.actions.Action):
    __module__ = __name__

    def __init__(self, driver):
        poi.actions.Action.__init__(self, 'MKS PDR 2000 Simulation Panel', 'Show the MKS PDR 2000 Simulation Panel', 'Show the MKS PDR 2000 Simulation Panel')
        self.driver = driver
        self.setEnabled(True)

    def run(self):
        self.driver.toggleDialog()


class SimulationDeviceDriver(mkspdr2000_drivers.DeviceDriver):
    __module__ = __name__

    def __init__(self, hwinst):
        mkspdr2000_drivers.DeviceDriver.__init__(self, hwinst)
        self.gauges = [
         'Off', 'Off']
        self.action = poi.actions.ActionContributionItem(ShowPanelAction(self))
        mng = ui.getDefault().getMenuManager().findByPath('atm.views')
        mng.appendToGroup('views-additions-end', self.action)
        mng.update()
        self.createDialog()

    def isConfigured(self):
        return True

    def createDialog(self):
        self.dlg = wx.Dialog(None, -1, 'MKS PDR 2000 Simulation Panel', size=wx.Size(400, 400), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        mainsizer = wx.BoxSizer(wx.HORIZONTAL)
        vsizer = wx.BoxSizer(wx.VERTICAL)
        self.gaugeCtrl1 = wx.Slider(self.dlg, -1, 0, 0, 100, style=wx.SL_VERTICAL)
        self.low1 = wx.CheckBox(self.dlg, -1, 'Low')
        self.off1 = wx.CheckBox(self.dlg, -1, 'Off')
        vsizer.Add(wx.StaticText(self.dlg, -1, 'Gauge 1'), 0, wx.ALL, 5)
        vsizer.Add(self.gaugeCtrl1, 1, wx.EXPAND | wx.ALL, 5)
        vsizer.Add(self.low1, 0, wx.EXPAND | wx.ALL, 5)
        vsizer.Add(self.off1, 0, wx.EXPAND | wx.ALL, 5)
        mainsizer.Add(vsizer, 0, wx.EXPAND | wx.ALL, 10)
        vsizer = wx.BoxSizer(wx.VERTICAL)
        self.gaugeCtrl2 = wx.Slider(self.dlg, -1, 0, 0, 100, style=wx.SL_VERTICAL)
        self.low2 = wx.CheckBox(self.dlg, -1, 'Low')
        self.off2 = wx.CheckBox(self.dlg, -1, 'Off')
        vsizer.Add(wx.StaticText(self.dlg, -1, 'Gauge 2'), 0, wx.ALL, 5)
        vsizer.Add(self.gaugeCtrl2, 1, wx.EXPAND | wx.ALL, 5)
        vsizer.Add(self.low2, 0, wx.EXPAND | wx.ALL, 5)
        vsizer.Add(self.off2, 0, wx.EXPAND | wx.ALL, 5)
        mainsizer.Add(vsizer, 0, wx.EXPAND | wx.ALL, 10)
        self.dlg.SetSizer(mainsizer)
        self.dlg.Bind(wx.EVT_CLOSE, self.OnDlgClose)
        self.suppress = False
        self.dlg.Bind(wx.EVT_CHECKBOX, self.updateControls, self.low1)
        self.dlg.Bind(wx.EVT_CHECKBOX, self.updateControls, self.low2)
        self.dlg.Bind(wx.EVT_CHECKBOX, self.updateControls, self.off1)
        self.dlg.Bind(wx.EVT_CHECKBOX, self.updateControls, self.off2)
        ui.getDefault().addCloseListener(self)
        self.updateControls()
        return

    def updateControls(self, event=None):
        if event is not None:
            event.Skip()
        if self.suppress:
            return
        self.suppress = True
        self.gaugeCtrl1.Enable(not (self.low1.IsChecked() or self.off1.IsChecked()))
        if self.off1.IsChecked():
            self.low1.SetValue(False)
        elif self.low1.IsChecked():
            self.off1.SetValue(False)
        self.gaugeCtrl2.Enable(not (self.low1.IsChecked() or self.off1.IsChecked()))
        if self.off2.IsChecked():
            self.low2.SetValue(False)
        elif self.low2.IsChecked():
            self.off2.SetValue(False)
        self.suppress = False
        return

    def OnDlgClose(self, event):
        event.Skip()
        event.Veto()

    def closing(self):
        self.dlg.Destroy()
        self.dlg = None
        return True

    def toggleDialog(self):
        self.dlg.Show(not self.dlg.IsShown())

    def getConfigurationSegment(self):
        return SimConfigurationSegment()

    def setConfiguration(self, configuration):
        mkspdr2000_drivers.DeviceDriver.setConfiguration(self, configuration)

    def initialize(self):
        pass

    def getID(self):
        return 'Simulation Driver MKS PDR 2000'

    def getPressure(self):
        gauge1 = 'Off'
        if self.off1.IsChecked():
            gauge1 = 'Off'
        if self.low1.IsChecked():
            gauge1 = 'Low'
        if not (self.off1.IsChecked() or self.low1.IsChecked()):
            gauge1 = '%d+e2' % self.gaugeCtrl1.GetValue()
        gauge2 = 'Off'
        if self.off2.IsChecked():
            gauge2 = 'Off'
        if self.low2.IsChecked():
            gauge2 = 'Low'
        if not (self.off2.IsChecked() or self.low2.IsChecked()):
            gauge2 = '%d+e2' % self.gaugeCtrl2.GetValue()
        return (gauge1, gauge2)

    def outputBinaryData(self, port, data):

        def doit(port, data):
            global OUTPUT
            x = -1
            port = port.upper()
            for datum in data:
                x += 1
                if self.digitalConfig[port][x] != OUTPUT:
                    continue
                self.digitalPorts[port][x].SetValue(datum)

        wx.CallAfter(doit, port, data)

    def readDigitalPorts(self, port):
        port = port.upper()
        return list(map((lambda x: x.GetValue()), self.digitalPorts[port]))

    def shutdown(self):
        if not self.status == mkspdr2000_drivers.STATUS_INITIALIZED:
            return
        self.status = mkspdr2000_drivers.STATUS_UNINITIALIZED

    def __del__(self):
        if self.dlg is not None:
            self.dlg.Destroy()
        mng = ui.getDefault().getMenuManager().findByPath('atm.views')
        mng.remove(self.action)
        mng.update()
        return


mkspdr2000_drivers.registerDriver('simulation', SimulationDeviceDriver, SimConfigurationSegment, 'Simulation')
