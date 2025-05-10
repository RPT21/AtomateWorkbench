# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/pressure_gauge/src/pressure_gauge/panelviewitem.py
# Compiled at: 2004-11-23 01:09:00
import wx, pressure_gauge.hardwarestatusprovider, wx.gizmos, hardware.hardwaremanager, panelview.devicemediator, logging, poi.utils.LEDdisplay, ui.widgets.led
logger = logging.getLogger('pressure_gauge.panelview')

class PressureGaugePanelViewItem(panelview.devicemediator.DevicePanelViewContribution):
    __module__ = __name__

    def __init__(self):
        panelview.devicemediator.DevicePanelViewContribution.__init__(self)
        self.hwinst = None
        return

    def createControl(self, parent, horizontal=False):
        self.control = wx.Panel(parent, -1, size=(100, 100))
        self.deviceLabel = wx.StaticText(self.control, -1, '[no label]')
        font = self.control.GetFont()
        font.SetWeight(wx.BOLD)
        self.deviceLabel.SetFont(font)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(wx.StaticLine(self.control, -1), 0, wx.GROW)
        sizer.Add(self.deviceLabel, 0, wx.GROW | wx.ALL, 0)
        fsizer = wx.FlexGridSizer(2, 2, 2, 2)
        fsizer.AddGrowableCol(0)
        fsizer.AddGrowableCol(1)
        fsizer.AddGrowableRow(1)
        fsizer.Add(wx.StaticText(self.control, -1, 'Gauge 1', size=(50, -1)), 0, wx.GROW | wx.ALL)
        fsizer.Add(wx.StaticText(self.control, -1, 'Gauge 2', size=(50, -1)), 0, wx.GROW | wx.ALL)
        self.gauge1 = poi.utils.LEDdisplay.LEDDisplay(self.control, -1)
        self.gauge2 = poi.utils.LEDdisplay.LEDDisplay(self.control, -1)
        fsizer.Add(self.gauge1, 1, wx.GROW | wx.ALL)
        fsizer.Add(self.gauge2, 1, wx.GROW | wx.ALL)
        sizer.Add(fsizer, 1, wx.GROW | wx.ALL)
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
        except Exception, msg:
            logger.exception(msg)

    def getConfiguredHardware(self):
        try:
            hwid = self.device.hardwarehints.getChildNamed('id').getValue()
            desc = hardware.hardwaremanager.getHardwareByName(hwid)
            inst = desc.getInstance()
            return inst
        except Exception, msg:
            logger.exception(msg)

        return None
        return

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
        return

    def internalHardwareUpdate(self, event):
        try:
            if event.etype == pressure_gauge.hardwarestatusprovider.PRESSURE:
                pressure = event.data
            elif event.etype == pressure_gauge.hardwarestatusprovider.STOPPED:
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
        except Exception, msg:
            logger.exception(msg)
