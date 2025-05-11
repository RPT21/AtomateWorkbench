# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/adr2100/src/adr2100/drivers/simulation.py
# Compiled at: 2004-12-07 23:11:58
import wx, ui, adr2100.drivers, poi, poi.actions

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
        self.control.SetBackgroundColour(wx.RED)
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
        poi.actions.Action.__init__(self, 'ADR 2100 Simulation Panel', 'Show the ADR 2100 Simulation Panel', 'Show the ADR 2100 Simulation Panel')
        self.driver = driver
        self.setEnabled(True)

    def run(self):
        self.driver.toggleDialog()


OUTPUT = adr2100.drivers.OUTPUT
INPUT = adr2100.drivers.INPUT
import traceback

class SimulationDeviceDriver(adr2100.drivers.DeviceDriver):
    __module__ = __name__

    def __init__(self, hwinst):
        adr2100.drivers.DeviceDriver.__init__(self, hwinst)
        self.digitalPorts = {}
        self.analogPorts = []
        self.digitalConfig = {}
        for c in ['A', 'B', 'C', 'D']:
            self.digitalConfig[c] = [
             INPUT, INPUT, INPUT, INPUT, INPUT, INPUT, 
             INPUT, INPUT]

        self.action = poi.actions.ActionContributionItem(ShowPanelAction(self))
        mng = ui.getDefault().getMenuManager().findByPath('atm.views')
        mng.appendToGroup('views-additions-end', self.action)
        mng.update()
        self.createDialog()

    def checkInterrupt(self):
        pass

    def createDialog(self):
        self.dlg = wx.Dialog(None, -1, 'ADR 2100 Simulation Panel', size=(400, 400), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        mainsizer = wx.BoxSizer(wx.VERTICAL)
        sb = wx.StaticBox(self.dlg, -1, 'Digital Ports')
        sbsizer = wx.StaticBoxSizer(sb, wx.VERTICAL)
        for c in ['A', 'B', 'C', 'D']:
            self.digitalPorts[c] = []
            hsizer = wx.BoxSizer(wx.HORIZONTAL)
            hsizer.Add(wx.StaticText(self.dlg, -1, '%s:' % c), 0, wx.ALL, 5)
            for i in range(8):
                ctrl = wx.CheckBox(self.dlg, -1, str(i))
                hsizer.Add(ctrl, 0, wx.ALL, 5)
                self.digitalPorts[c].append(ctrl)

            sbsizer.Add(hsizer, 0, wx.GROW | wx.ALL, 5)

        mainsizer.Add(sbsizer, 0, wx.GROW | wx.ALL, 5)
        sb = wx.StaticBox(self.dlg, -1, 'Analog Inputs')
        sbsizer = wx.StaticBoxSizer(sb, wx.HORIZONTAL)
        for i in range(4):
            ctrl = wx.CheckBox(self.dlg, -1, str(i))
            sbsizer.Add(ctrl, 0, wx.ALL, 5)
            self.analogPorts.append(ctrl)

        mainsizer.Add(sbsizer, 0, wx.GROW | wx.ALL, 5)
        self.dlg.SetSizer(mainsizer)
        self.dlg.Bind(wx.EVT_CLOSE, self.OnDlgClose)
        ui.getDefault().addCloseListener(self)
        return

    def OnDlgClose(self, event):
        event.Skip()
        event.Veto()

    def closing(self):
        if self.dlg is not None:
            self.dlg.Destroy()
            self.dlg = None
        return True
        return

    def toggleDialog(self):
        self.dlg.Show(not self.dlg.IsShown())

    def getConfigurationSegment(self):
        return SerialConfigurationSegment()

    def setConfiguration(self, configuration):
        adr2100.drivers.DeviceDriver.setConfiguration(self, configuration)

    def initialize(self):
        pass

    def configureDigitalPorts(self, port, config):
        port = port.upper()
        self.digitalConfig[port] = config

    def outputBinaryData(self, port, data):

        def doit(port, data):
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

    def readAnalogPort(self, port):
        val = self.analogPorts[int(port)].GetValue()
        if val:
            return 0.85
        return 0

    def readAnalogPorts(self):
        results = []
        for port in self.analogPorts:
            if port.GetValue():
                results.append(0.85)
            else:
                results.append(0)

        return results

    def shutdown(self):
        if not self.status == adr2100.drivers.STATUS_INITIALIZED:
            return
        self.status = adr2100.drivers.STATUS_UNINITIALIZED

    def dispose(self):

        def doit():
            if self.dlg is not None:
                self.dlg.Destroy()
            self.dlg = None
            mng = ui.getDefault().getMenuManager().findByPath('atm.views')
            mng.remove(self.action)
            mng.update()
            return

        wx.CallAfter(doit)

    def __del__(self):
        self.dispose()


adr2100.drivers.registerDriver('simulation', SimulationDeviceDriver, SimConfigurationSegment, 'Simulation')
