# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/up150/src/up150/drivers/simulation.py
# Compiled at: 2004-11-13 00:03:05
import up150.drivers, wx, ui, poi, poi.actions

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
        poi.actions.Action.__init__(self, 'UP150 Sim Panel %s' % driver.hwinst.getDescription().getName(), '', '')
        self.driver = driver

    def run(self):
        self.driver.toggleDialog()


class SimulationDeviceDriver(up150.drivers.DeviceDriver):
    __module__ = __name__

    def __init__(self, hwinst):
        up150.drivers.DeviceDriver.__init__(self, hwinst)
        self.temperature = 0
        self.action = poi.actions.ActionContributionItem(ShowPanelAction(self))
        mng = ui.getDefault().getMenuManager().findByPath('atm.views')
        mng.appendToGroup('views-additions-end', self.action)
        mng.update()
        self.createDialog()

    def createDialog(self):
        self.dlg = wx.Dialog(None, -1, 'UP150 Simulation Driver %s' % self.hwinst.getDescription().getName(), size=wx.Size(400, 200))
        tempSlider = wx.Slider(self.dlg, -1, 0, 0, 1000)
        tempSlider.Bind(wx.EVT_SCROLL, self.OnSlide)
        self.tempCtrl = tempSlider
        self.lockoutPanel = wx.CheckBox(self.dlg, -1, 'Panel Locked Out')
        self.lockoutPanel.Disable()
        self.setpointText = wx.TextCtrl(self.dlg, -1, '')
        self.setpointText.Disable()
        sizer = wx.BoxSizer(wx.VERTICAL)
        s = wx.BoxSizer(wx.HORIZONTAL)
        s.Add(wx.StaticText(self.dlg, -1, 'Temperature:'), 0, wx.ALIGN_CENTRE_VERTICAL | wx.RIGHT, 5)
        s.Add(tempSlider, 1, wx.EXPAND | wx.ALIGN_CENTRE_VERTICAL)
        sizer.Add(s, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(self.lockoutPanel, 0, wx.EXPAND | wx.ALL, 5)
        s = wx.BoxSizer(wx.HORIZONTAL)
        s.Add(wx.StaticText(self.dlg, -1, 'Setpoint:'), 0, wx.ALIGN_CENTRE_VERTICAL | wx.RIGHT, 5)
        s.Add(self.setpointText, 1, wx.ALIGN_CENTRE_VERTICAL | wx.ALL)
        sizer.Add(s, 0, wx.EXPAND | wx.ALL, 5)
        self.dlg.SetSizer(sizer)
        self.dlg.SetAutoLayout(True)
        ui.getDefault().addCloseListener(self)
        return

    def closing(self):
        self.dlg.Destroy()
        self.dlg = None
        return True
        return

    def OnSlide(self, event):
        event.Skip()
        self.temperature = self.tempCtrl.GetValue()

    def toggleDialog(self):
        self.dlg.Show(not self.dlg.IsShown())

    def getConfigurationSegment(self):
        return SimConfigurationSegment()

    def getTemperature(self, timeout=1):
        return self.temperature

    def setSetpoint(self, setpoint, timeout=1):
        wx.CallAfter(self.setpointText.SetValue, str(setpoint))

    def lockPanel(self):
        wx.CallAfter(self.lockoutPanel.SetValue, True)

    def unlockPanel(self):
        wx.CallAfter(self.lockoutPanel.SetValue, False)

    def activate(self):
        pass

    def deactivate(self):
        pass

    def setMinimumTemperature(self, mt):
        pass

    def setMaximumTemperature(self, mt):
        pass

    def isConfigured(self):
        return True

    def getID(self):
        return 'UP150 Simulation Driver'

    def setConfiguration(self, configuration):
        self.configuration = configuration

    def getConfiguration(self):
        return self.configuration()

    def getStatus(self):
        return self.status

    def getDescription(self):
        return ''

    def initialize(self):
        self.status = up150.drivers.STATUS_INITIALIZED

    def shutdown(self):
        self.status = up150.drivers.STATUS_UNINITIALIZED

    def __del__(self):
        if self.dlg is not None:
            self.dlg.Destroy()
        mng = ui.getDefault().getMenuManager().findByPath('atm.views')
        mng.remove(self.action)
        mng.update()
        return


up150.drivers.registerDriver('simulation', SimulationDeviceDriver, SimConfigurationSegment, 'Simulation')
