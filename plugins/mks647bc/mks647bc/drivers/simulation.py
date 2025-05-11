# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/mks647bc/src/mks647bc/drivers/simulation.py
# Compiled at: 2004-11-18 22:13:01
import wx, mks647bc.drivers, socket, time, threading, select, mks647bc.drivers, serial, logging, poi, ui
from hardware import ResponseTimeoutException
logger = logging.getLogger('mks647.drivers.simulation')

class SimulationConfigurationSegment(object):
    __module__ = __name__

    def __init__(self):
        self.complete = False
        self.fireText = True
        self.configChanged = False

    def getControl(self):
        return self.control

    def setOwner(self, owner):
        self.owner = owner

    def createControl(self, composite):
        self.control = wx.Panel(composite, -1)
        return self.control

    def setDirty(self, dirty):
        self.dirty = dirty
        self.configChanged = False

    def isConfigChanged(self):
        return self.configChanged

    def markDirty(self, event=None):
        if event is not None:
            event.Skip()
        if not self.fireText:
            return
        self.configChanged = True
        self.owner.markDirty()
        return

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
        poi.actions.Action.__init__(self, 'MKS647 Simulation Driver', '', '')
        self.driver = driver

    def run(self):
        self.driver.toggleDialog()


class SimulationDeviceDriver(mks647bc.drivers.DeviceDriver):
    __module__ = __name__

    def __init__(self):
        mks647bc.drivers.DeviceDriver.__init__(self)
        self.lockoutPanel = True
        self.channelRanges = {1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0, 5: 1.0, 6: 1.0, 7: 1.0, 8: 1.0}
        self.channels = []
        self.action = poi.actions.ActionContributionItem(ShowPanelAction(self))
        mng = ui.getDefault().getMenuManager().findByPath('atm.views')
        mng.appendToGroup('views-additions-end', self.action)
        mng.update()
        ui.getDefault().addCloseListener(self)
        self.createDialog()

    def createDialog(self):
        self.dlg = wx.Dialog(None, -1, 'MKS647 Simulation Dialog', size=(400, 400), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        sizer = wx.BoxSizer(wx.VERTICAL)
        for i in range(8):
            box = wx.StaticBox(self.dlg, -1, 'Channel %d' % (i + 1))
            sbsizer = wx.StaticBoxSizer(box, wx.HORIZONTAL)
            ctrls = {}
            ctrls['switch'] = wx.CheckBox(self.dlg, -1, 'Enabled')
            ctrls['switch'].Disable()
            ctrls['slider'] = wx.Slider(self.dlg, -1, 0, 0, 100)
            ctrls['setpoint'] = wx.TextCtrl(self.dlg, -1, '     ')
            ctrls['setpoint'].Disable()
            sbsizer.Add(ctrls['switch'], 0, wx.RIGHT | wx.ALIGN_CENTRE_VERTICAL, 5)
            sbsizer.Add(ctrls['slider'], 1, wx.ALIGN_CENTRE_VERTICAL)
            sbsizer.Add(ctrls['setpoint'], 0, wx.ALIGN_CENTRE_VERTICAL | wx.LEFT, 5)
            self.channels.append(ctrls)
            sizer.Add(sbsizer, 0, wx.GROW | wx.ALL, 5)

        self.dlg.SetSizer(sizer)
        s = sizer.CalcMin()
        self.dlg.SetSize((400, s[1]))
        self.dlg.SetAutoLayout(True)
        return

    def closing(self):
        self.dlg.Destroy()
        self.dlg = None
        return True
        return

    def toggleDialog(self):
        self.dlg.Show(not self.dlg.IsShown())

    def getConfigurationSegment(self):
        return SimulationConfigurationSegment()

    def setConfiguration(self, configuration):
        mks647bc.drivers.DeviceDriver.setConfiguration(self, configuration)

    def initialize(self):
        try:
            self.checkInterrupt()
            did = self.getID()
            if self.lockoutPanel:
                logger.debug('Locking panel')
                self.lockPanel()
        except Exception as msg:
            raise Exception(msg)

    def checkInterrupt(self):
        pass

    def lockPanel(self):
        pass

    def unlockPanel(self):
        pass

    def channelOn(self, channelNum):

        def doit(n):
            self.channels[n]['switch'].SetValue(True)

        wx.CallAfter(doit, channelNum - 1)
        logger.debug('channel %i on' % channelNum)

    def channelOff(self, channelNum):

        def doit(n):
            self.channels[n]['switch'].SetValue(False)

        wx.CallAfter(doit, channelNum - 1)
        logger.debug('channel %i off' % channelNum)

    def enableFlow(self):

        def doit(n):
            self.channels[n]['flow'].SetValue(True)

        logger.debug('flow enabled')

    def disableFlow(self):

        def doit(n):
            self.channels[n]['flow'].SetValue(False)

        logger.debug('flow disabled')

    def getFlow(self, channelNum, timeout=None):
        if not self.channels[channelNum - 1]['switch'].IsChecked():
            return None
        it = float(self.channels[channelNum - 1]['slider'].GetValue()) / 100.0
        time.sleep(1.0)
        return int(self.channelRanges[channelNum] * it)
        if output.find('-') >= 0:
            return self.channelRanges[channelNum] + 1
        return int(output)
        return

    def getID(self):
        sid = '647'
        return sid

    def setSetpoint(self, channel, flow):
        converted = int(1000.0 * flow / self.channelRanges[channel] + 0.5)
        logger.debug('Setting setpoint to %d' % converted)
        result = 0

        def doit(c, f):
            self.channels[c - 1]['setpoint'].SetValue(str(flow))

        wx.CallAfter(doit, channel, flow)
        return result

    def setRange(self, channel, range):
        logger.debug('Setting range: RA %d %d\r' % (channel, range))
        result = 0
        self.channelRanges[channel] = range
        return result

    def setRangeIndex(self, channelNum, rangeIndex, range):
        logger.debug('Range index RA %d %d (%d)' % (channelNum, rangeIndex, range))
        self.channelRanges[channelNum] = range

    def setGCF(self, channelNum, gcf):
        logger.debug('GC %d %d\r' % (channelNum, int(gcf)))
        result = 0.0
        return result

    def setUnits(self, channelNum, unitStr):
        pass

    def setSetpointConversion(self, channelNum, conversion):
        self.channelRanges[channelNum] = conversion

    def shutdown(self):
        if not self.status == mks647bc.drivers.STATUS_INITIALIZED:
            return
        try:
            if self.lockoutPanel:
                self.unlockPanel()
        except Exception as msg:
            print(('* ERROR: Cannot unlock panel', msg))

        self.status = mks647bc.drivers.STATUS_UNINITIALIZED

    def __del__(self):
        if self.dlg is not None:
            self.dlg.Destroy()
        mng = ui.getDefault().getMenuManager().findByPath('atm.views')
        mng.remove(self.action)
        mng.update()
        return


mks647bc.drivers.registerDriver('simulation', SimulationDeviceDriver, SimulationConfigurationSegment, 'Simulation')
