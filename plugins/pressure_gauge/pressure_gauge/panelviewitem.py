# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/pressure_gauge/src/pressure_gauge/panelviewitem.py
# Compiled at: 2004-11-23 01:09:00
import wx, wx.gizmos
import plugins.pressure_gauge.pressure_gauge.hardwarestatusprovider as pressure_gauge_hardwarestatusprovider
import plugins.hardware.hardware.hardwaremanager, plugins.panelview.panelview.devicemediator, logging
import plugins.poi.poi.utils.LEDdisplay
import plugins.poi.poi as poi
import plugins.hardware.hardware as hardware
import plugins.panelview.panelview as panelview

logger = logging.getLogger('pressure_gauge.panelview')

class PressureGaugePanelViewItem(panelview.devicemediator.DevicePanelViewContribution):
    __module__ = __name__

    def __init__(self):
        panelview.devicemediator.DevicePanelViewContribution.__init__(self)
        self.hwinst = None
        return

    def createControl(self, parent, horizontal=False):
        self.control = wx.Panel(parent, -1, size=wx.Size(100, 100))
        self.deviceLabel = wx.StaticText(self.control, -1, '[no label]')
        font = self.control.GetFont()
        font.SetWeight(wx.BOLD)
        self.deviceLabel.SetFont(font)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(wx.StaticLine(self.control, -1), 0, wx.EXPAND)
        sizer.Add(self.deviceLabel, 0, wx.EXPAND | wx.ALL, 0)
        fsizer = wx.FlexGridSizer(2, 2, 2, 2)
        fsizer.AddGrowableCol(0)
        fsizer.AddGrowableCol(1)
        fsizer.AddGrowableRow(1)
        fsizer.Add(wx.StaticText(self.control, -1, 'Gauge 1', size=wx.Size(50, -1)), 0, wx.EXPAND | wx.ALL)
        fsizer.Add(wx.StaticText(self.control, -1, 'Gauge 2', size=wx.Size(50, -1)), 0, wx.EXPAND | wx.ALL)
        self.gauge1 = poi.utils.LEDdisplay.LEDDisplay(self.control, -1)
        self.gauge2 = poi.utils.LEDdisplay.LEDDisplay(self.control, -1)
        fsizer.Add(self.gauge1, 1, wx.EXPAND | wx.ALL)
        fsizer.Add(self.gauge2, 1, wx.EXPAND | wx.ALL)
        sizer.Add(fsizer, 1, wx.EXPAND | wx.ALL)
        self.control.SetSizer(sizer)
        self.control.SetAutoLayout(True)
        self.updateDeviceUI()
        return self.control

    def setDevice(self, device):
        panelview.devicemediator.DevicePanelViewContribution.setDevice(self, device)
        self.deviceChanged()

    def deviceChanged(self):
        self.unhookDeviceFromHardware()
        self.hookDeviceToHardware()
        self.updateDeviceUI()

    def updateDeviceUI(self):
        try:
            self.deviceLabel.SetLabel(self.device.getLabel())
        except Exception as msg:
            logger.exception(msg)

    def getConfiguredHardware(self):
        try:
            hwid = self.device.hardwarehints.getChildNamed('id').getValue()
            desc = hardware.hardwaremanager.getHardwareByName(hwid)
            inst = desc.getInstance()
            return inst
        except Exception as msg:
            logger.exception(msg)

        return None

    def dispose(self):
        panelview.devicemediator.DevicePanelViewContribution.dispose(self)
        self.unhookDeviceFromHardware()

    def unhookDeviceFromHardware(self):
        if self.hwinst is not None:
            self.hwinst.removeHardwareStatusProviderListener(self)
        return

    def hookDeviceToHardware(self):
        self.unhookDeviceFromHardware()
        inst = self.getConfiguredHardware()
        if inst is None:
            return
        inst.addHardwareStatusProviderListener(self)
        self.hwinst = inst
        return

    def hardwareStatusChanged(self, event):
        wx.CallAfter(self.internalHardwareUpdate, event)

    def formatFlow(self, flow):
        if flow is None:
            return ''
        ir = len(str(int(self.range)))
        leftover = 4 - ir
        if leftover < 0:
            leftover = 0
        frmt = '%%0.0%df' % leftover
        return frmt % flow

    def internalHardwareUpdate(self, event):
        try:
            if event.etype == pressure_gauge_hardwarestatusprovider.PRESSURE:
                pressure = event.data
            elif event.etype == pressure_gauge_hardwarestatusprovider.STOPPED:
                pressure = (
                 '', '')
            else:
                return
            (pressure1, pressure2) = pressure
            if pressure1.lower() == 'low':
                pressure1 = 'lo'
            if pressure2.lower() == 'low':
                pressure2 = 'lo'
            self.gauge1.setValue(pressure1)
            self.gauge2.setValue(pressure2)
        except Exception as msg:
            logger.exception(msg)
