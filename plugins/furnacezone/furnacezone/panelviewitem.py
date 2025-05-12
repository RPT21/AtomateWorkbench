# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/furnacezone/src/furnacezone/panelviewitem.py
# Compiled at: 2004-11-19 01:37:48
import wx, threading, wx.gizmos, hardware.hardwaremanager, panelview.devicemediator, logging, furnacezone.hw, ui.widgets.led, ui.widgets
logger = logging.getLogger('furnacezone.ui.panelview')

class FurnaceZonePanelViewItem(panelview.devicemediator.DevicePanelViewContribution):
    __module__ = __name__

    def __init__(self):
        panelview.devicemediator.DevicePanelViewContribution.__init__(self)
        self.hwinst = None
        self.deviceLabel = None
        self.horizontal = False
        return

    def createControl(self, parent, horizontal=False):
        self.control = wx.Panel(parent, -1, size=wx.Size(-1, 80))
        font = self.control.GetFont()
        self.deviceLabel = ui.widgets.GradientLabel(self.control, wx.RED)
        width = -1
        self.horizontal = horizontal
        if not horizontal:
            width = 200
        self.temperatureLED = ui.widgets.led.LEDSetpointDisplay(self.control, bgcolor=(0, 0, 0), fgcolor=(255, 0, 0), spfgcolor=(0, 255, 0), size=(width, -1), showSetpoint=not horizontal)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(wx.StaticLine(self.control, -1), 0, wx.EXPAND)
        sizer.Add(self.deviceLabel, 0, wx.EXPAND | wx.ALL, 0)
        sizer.Add(self.temperatureLED, 1, wx.EXPAND | wx.ALL, 0)
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
        logger.debug('Update device ui in thread %s' % threading.currentThread())
        try:
            self.deviceLabel.SetLabel(self.device.getLabel())
        except Exception as msg:
            pass

        if self.deviceLabel:
            self.deviceLabel.setColor(self.device.getPlotColor())

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

    def internalHardwareUpdate(self, event):
        logger.debug('Internal hardware update %s' % threading.currentThread())
        try:
            tempval = 0
            if event.etype == furnacezone.hw.TEMPERATURE:
                tempval = event.data
            elif event.etype == furnacezone.hw.STOPPED:
                tempval = ''
            self.temperatureLED.setValue(str(tempval))
            setpoint = self.getConfiguredHardware().getSetpoint()
            if setpoint is None:
                setpoint = ''
            self.temperatureLED.setSetpointValue(str(setpoint))
        except Exception as msg:
            logger.exception(msg)

        return
