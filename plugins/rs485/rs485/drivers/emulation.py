# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/rs485/src/rs485/drivers/emulation.py
# Compiled at: 2004-11-19 02:47:58
import wx, rs485.drivers, ui

class UserInterface(object):
    __module__ = __name__

    def __init__(self, owner):
        self.owner = owner
        self.window = None
        self.addressSliders = []
        self.addressSetpoints = []
        self.addressLabels = []
        self.numAddresses = 3
        self.respond = True
        return

    def createControl(self):
        wx.CallAfter(self.internalCreateControl)

    def OnRespondToggle(self, event):
        self.respond = not event.IsChecked()
        self.owner.setRespond(self.respond)
        event.Skip()

    def createInterface(self):
        """Creates vertical sliders for each channel.  How many depend on setting of 4 or 8 channels"""
        slidersizer = wx.BoxSizer(wx.HORIZONTAL)
        self.respondToggle = wx.ToggleButton(self.window, -1, 'Do Not Respond To Requests')
        self.window.Bind(wx.EVT_TOGGLEBUTTON, self.OnRespondToggle, self.respondToggle)
        for i in range(self.numAddresses):
            slider = wx.Slider(self.window, -1, 100, 0, 100, style=wx.SL_VERTICAL)
            label = wx.StaticText(self.window, -1, 'Address 0%i:       ' % (i + 1))
            setpoint = wx.StaticText(self.window, -1, 'Set Point:       ')
            vsizer = wx.BoxSizer(wx.VERTICAL)
            vsizer.Add(setpoint, 0, wx.GROW | wx.ALL | wx.ALIGN_CENTRE_HORIZONTAL, 5)
            vsizer.Add(slider, 1, wx.ALL | wx.ALIGN_CENTRE_HORIZONTAL, 5)
            vsizer.Add(label, 0, wx.GROW | wx.ALL | wx.ALIGN_CENTRE_HORIZONTAL, 5)
            slidersizer.Add(vsizer, 0, wx.ALL, 5)
            self.addressSliders.append(slider)
            self.addressSetpoints.append(setpoint)
            self.addressLabels.append(label)

            def onScroll(event, y=i):
                event.Skip()
                self.UpdateUI(y)
                sizer = self.window.GetSizer()
                sizer.Layout()

            self.UpdateUI(i)
            self.window.Bind(wx.EVT_SCROLL, onScroll, id=slider.GetId())

        mainsizer = wx.BoxSizer(wx.VERTICAL)
        mainsizer.Add(self.respondToggle, 0, wx.GROW | wx.ALL, 10)
        mainsizer.Add(slidersizer, 1, wx.GROW | wx.ALL, 10)
        mainsizer.Fit(self.window)
        mainsizer.Layout()
        self.window.SetSizer(mainsizer)
        self.window.SetAutoLayout(True)

    def UpdateUI(self, y):
        value = self.addressSliders[y].GetValue()
        self.addressLabels[y].SetLabel('Address 0%i: %i' % (y + 1, 100 - value))
        self.owner.setAddressValue(y, 100 - value)

    def internalCreateControl(self):
        mainframe = ui.getDefault().getMainFrame().getControl()
        self.window = wx.MiniFrame(ui.getDefault().getMainFrame().getControl(), -1, 'MKS647 Emulation', size=(300, 300), pos=(0, 0))
        self.createInterface()
        self.window.Show()

    def dispose(self):
        self.window.Destroy()
        del self.window
        self.window = None
        return


class EmulationConfigurationSegment(object):
    __module__ = __name__

    def __init__(self):
        self.complete = True

    def getControl(self):
        return self.control

    def setOwner(self, owner):
        self.owner = owner

    def createControl(self, composite):
        self.control = wx.Panel(composite, -1)
        return self.control

    def setData(self, data):
        pass

    def getData(self, data):
        pass

    def isComplete(self):
        return True

    def isConfigChanged(self):
        return False

    def setDirty(self, dirty):
        pass


class EmulationDeviceDriver(rs485.drivers.DeviceDriver):
    __module__ = __name__

    def __init__(self):
        rs485.drivers.DeviceDriver.__init__(self)
        self.wnd = None
        self.addressValues = {'01': 0, '02': 0, '03': 0}
        self.respond = True
        return

    def setRespond(self, respond):
        self.respond = respond

    def setAddressValue(self, address, value):
        self.addressValues[address] = value

    def checkRespond(self):
        if self.respond:
            return
        self.cv.acquire()
        self.cv.wait()
        if self.ir:
            self.cv.notify()
            self.ir = False
            self.respond = True
            self.cv.release()
            raise Exception('Interrupted')
        self.cv.release()

    def getTemperature(self, address):
        if self.checkInterrupt():
            return
        self.checkRespond()
        return self.addressValues[address]

    def checkInterrupt(self):
        if self.ir:
            self.cv.acquire()
            self.ir = False
            self.cv.notify()
            self.cv.release()
            return True
        return False

    def getID(self):
        if self.checkInterrupt():
            return
        return -1

    def displayUI(self):
        if self.getStatus() != rs485.drivers.STATUS_INITIALIZED:
            return
        self.wnd.createControl()

    def getConfigurationSegment(self):
        return EmulationConfigurationSegment()

    def initialize(self):
        if self.checkInterrupt():
            return
        self.wnd = UserInterface(self)
        self.status = rs485.drivers.STATUS_INITIALIZED
        self.displayUI()

    def shutdown(self):
        if self.checkInterrupt():
            return
        self.status = rs485.drivers.STATUS_UNINITIALIZED
        self.wnd.dispose()
        del self.wnd
        self.wnd = None
        return


rs485.drivers.registerDriver('emulation', EmulationDeviceDriver, EmulationConfigurationSegment, 'Emulation')
