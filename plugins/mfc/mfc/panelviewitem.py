# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/mfc/src/mfc/panelviewitem.py
# Compiled at: 2004-12-09 00:49:30
import wx, plugins.mfc.mfc.hardwarestatusprovider, wx.gizmos, plugins.hardware.hardware.hardwaremanager
import plugins.panelview.panelview.devicemediator, logging, plugins.ui.ui.widgets.led, plugins.ui.ui.widgets
import plugins.panelview.panelview as panelview
logger = logging.getLogger('mfc.panelview')


def _isDestroyed(window):
    if window is None:
        return True
    if hasattr(wx, 'IsDestroyed'):
        try:
            return wx.IsDestroyed(window)
        except Exception:
            return True
    return False


def _safeCallAfter(func, *args, **kwargs):
    def wrapper():
        try:
            return func(*args, **kwargs)
        except RuntimeError:
            return
        except Exception as msg:
            try:
                logger.debug(f'Callback exception: {msg}')
            except Exception:
                pass
    return wx.CallAfter(wrapper)

class MFCPanelViewItem(panelview.devicemediator.DevicePanelViewContribution):
    __module__ = __name__

    def __init__(self):
        panelview.devicemediator.DevicePanelViewContribution.__init__(self)
        self.hwinst = None
        self.range = 1
        self.gcf = 100
        self.deviceLabel = None
        return

    def createControl(self, parent, horizontal=False):
        self.control = wx.Panel(parent, -1, size=wx.Size(-1, 80))
        self.deviceLabel = plugins.ui.ui.widgets.GradientLabel(self.control, wx.GREEN)
        self.ledCtrl = plugins.ui.ui.widgets.led.LEDSetpointDisplay(self.control, bgcolor=(145, 145, 96), fgcolor=(0, 0, 0), showSetpoint=not horizontal)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(wx.StaticLine(self.control, -1), 0, wx.EXPAND)
        sizer.Add(self.deviceLabel, 0, wx.EXPAND | wx.ALL, 0)
        sizer.Add(self.ledCtrl, 1, wx.EXPAND | wx.ALL)
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
        if self.deviceLabel is None:
            return
        try:
            self.deviceLabel.SetLabel(self.device.getLabel())
        except Exception as msg:
            logger.exception(msg)

        self.deviceLabel.setColor(self.device.getPlotColor())
        return

    def getConfiguredHardware(self):
        try:
            hwid = self.device.hardwarehints.getChildNamed('id').getValue()
            desc = plugins.hardware.hardware.hardwaremanager.getHardwareByName(hwid)
            if desc is None:
                logger.warning("Configured hardware '%s' not found", hwid)
                return None
            try:
                inst = desc.getInstance()
            except Exception:
                logger.exception('Error getting instance for hardware %s', hwid)
                return None
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
        try:
            self.range = self.device.getRange()
            self.gcf = self.device.getGCF()
        except Exception as msg:
            logger.exception(msg)

        return

    def hardwareStatusChanged(self, event):
        if event.etype == plugins.mfc.mfc.hardwarestatusprovider.FLOW:
            if not event.channel == self.device.getChannelNumber():
                return
        if _isDestroyed(self.control):
            return
        _safeCallAfter(self.internalHardwareUpdate, event)

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
            if _isDestroyed(self.control):
                return
            flowval = 0
            if event.etype == plugins.mfc.mfc.hardwarestatusprovider.FLOW:
                flowval = event.data
                if flowval is None:
                    flowval = ''
            elif event.etype == plugins.mfc.mfc.hardwarestatusprovider.STOPPED:
                flowval = ''
            if flowval == '':
                flow = None
            else:
                flow = float(flowval * self.range / 1000) * (self.gcf / 100.0)
            self.ledCtrl.setValue(self.formatFlow(flow))
            inst = self.getConfiguredHardware()
            try:
                if inst is None:
                    setpoint = ''
                else:
                    setpoint = inst.getSetpoint(self.device.getChannelNumber())
                    if setpoint is None:
                        setpoint = ''
            except Exception:
                logger.exception('Error obtaining setpoint from hardware instance')
                setpoint = ''
            self.ledCtrl.setSetpointValue(str(setpoint))
        except Exception as msg:
            logger.exception(msg)

        return
