# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/mks647bc/src/mks647bc/drivers/emulation.py
# Compiled at: 2004-08-18 03:37:00
import wx, poi, poi.actions, mks647bc.drivers, ui, logging
logger = logging.getLogger('mks647bc.drivers.emulation')

class UserInterface(object):
    __module__ = __name__

    def __init__(self, owner):
        self.owner = owner
        self.window = None
        self.channelSliders = []
        self.channelSetpoints = []
        self.channelLabels = []
        self.numChannels = 4
        self.respond = True
        self.shuttingdown = False
        return

    def createControl(self):
        wx.CallAfter(self.internalCreateControl)

    def OnRespondToggle(self, event):
        self.respond = not event.IsChecked()
        self.owner.setRespond(self.respond)
        event.Skip()

    def createInterface(self):
        """Creates vertical sliders for each channel.  How many depend on setting of 4 or 8 channels"""
        self.numChannels = int(self.owner.configuration.get('main', 'channels'))
        slidersizer = wx.BoxSizer(wx.HORIZONTAL)
        self.respondToggle = wx.ToggleButton(self.window, -1, 'Do Not Respond To Requests')
        self.window.Bind(wx.EVT_TOGGLEBUTTON, self.OnRespondToggle, self.respondToggle)
        for i in range(self.numChannels):
            slider = wx.Slider(self.window, -1, 100, 0, 100, style=wx.SL_VERTICAL)
            label = wx.StaticText(self.window, -1, 'Channel %i:       ' % (i + 1))
            setpoint = wx.StaticText(self.window, -1, 'Set Point:       ')
            vsizer = wx.BoxSizer(wx.VERTICAL)
            vsizer.Add(setpoint, 0, wx.GROW | wx.ALL | wx.ALIGN_CENTRE_HORIZONTAL, 5)
            vsizer.Add(slider, 1, wx.ALL | wx.ALIGN_CENTRE_HORIZONTAL, 5)
            vsizer.Add(label, 0, wx.GROW | wx.ALL | wx.ALIGN_CENTRE_HORIZONTAL, 5)
            slidersizer.AddSizer(vsizer, 0, wx.ALL, 5)
            self.channelSliders.append(slider)
            self.channelSetpoints.append(setpoint)
            self.channelLabels.append(label)

            def onScroll(event, y=i):
                event.Skip()
                self.UpdateUI(y)
                sizer = self.window.GetSizer()
                sizer.Layout()

            self.UpdateUI(i)
            self.window.Bind(wx.EVT_SCROLL, onScroll, id=slider.GetId())

        mainsizer = wx.BoxSizer(wx.VERTICAL)
        mainsizer.Add(self.respondToggle, 0, wx.GROW | wx.ALL, 10)
        mainsizer.AddSizer(slidersizer, 1, wx.GROW | wx.ALL, 10)
        mainsizer.Fit(self.window)
        mainsizer.Layout()
        self.window.SetSizer(mainsizer)
        self.window.SetAutoLayout(True)
        self.window.Bind(wx.EVT_CLOSE, self.OnClose)

    def OnClose(self, event):
        print('close called')
        if not self.shuttingdown:
            print('\thiding')
            self.window.Hide()
            event.Veto()
        else:
            event.Skip()

    def UpdateUI(self, y):
        value = self.channelSliders[y].GetValue()
        self.channelLabels[y].SetLabel('Channel %i: %i' % (y + 1, 100 - value))
        self.owner.setChannelValue(y, 100 - value)

    def restore(self):
        self.window.Show()

    def internalCreateControl(self):
        mainframe = ui.getDefault().getMainFrame().getControl()
        self.window = wx.MiniFrame(ui.getDefault().getMainFrame().getControl(), -1, 'MKS647 Emulation', size=wx.Size(300, 300), pos=(0, 0))
        self.createInterface()
        self.window.Show()

    def dispose(self):
        self.shuttingdown = True
        self.window.Close()
        self.window.Destroy()
        del self.window
        del self.channelSliders[0:]
        del self.channelLabels[0:]
        self.window = None
        return

    def isDisposed(self):
        return self.window is None
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


class ShowEmulationControl(poi.actions.Action):
    __module__ = __name__

    def __init__(self, name, owner):
        poi.actions.Action.__init__(self, name)
        self.owner = owner

    def run(self):
        self.owner.toggleDisplay()


class EmulationDeviceDriver(mks647bc.drivers.DeviceDriver):
    __module__ = __name__

    def __init__(self):
        mks647bc.drivers.DeviceDriver.__init__(self)
        self.wnd = UserInterface(self)
        self.channelValues = [0, 0, 0, 0]
        self.respond = True
        self.wnd = UserInterface(self)
        self.createMenuItem()

    def createMenuItem(self):
        mng = ui.getDefault().getMenuManager().findByPath('atm.views')
        action = ShowEmulationControl('MKS647bc', self)
        mng.addItem(poi.actions.ActionContributionItem(action, 'insert%s' % id(self)))
        mng.update()

    def setRespond(self, respond):
        self.respond = respond

    def setChannelValue(self, number, value):
        self.channelValues[number] = value

    def checkRespond(self):
        if self.respond:
            return
        print(self, 'checkRespond - acquire')
        self.cv.acquire()
        print(self, 'checkRespond - wait')
        self.cv.wait()
        if self.ir:
            print(self, 'checkrespond - notify')
            self.cv.notify()
            self.ir = False
            self.respond = True
            print(self, 'checkrespond release')
            self.cv.release()
            raise Exception('Interrupted')
        print(self, 'checkrespond - release')
        self.cv.release()

    def getFlow(self, channelNum):
        if self.checkInterrupt():
            return
        self.checkRespond()
        if channelNum >= len(self.channelValues):
            return 0
        return self.channelValues[channelNum]

    def checkInterrupt(self):
        if self.ir:
            print(self, 'checkInterrupt - Acquire')
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
        logger.debug('Display UI')
        if self.getStatus() != mks647bc.drivers.STATUS_INITIALIZED:
            logger.debug('Not initialized')
            return
        logger.debug('Asking to create control')
        self.wnd.createControl()

    def getConfigurationSegment(self):
        return EmulationConfigurationSegment()

    def toggleDisplay(self):
        if not self.wnd.isDisposed():
            self.wnd.restore()
        else:
            self.displayUI()

    def initialize(self):
        logger.debug('Initialize')
        print('is window disposed?', self.wnd.isDisposed())
        if not self.wnd.isDisposed():
            self.wnd.restore()
        if self.status == mks647bc.drivers.STATUS_INITIALIZED:
            logger.debug('Driver already initialized')
            return
        self.channelValues = list(map((lambda x: 0), list(range(int(self.configuration.get('main', 'channels'))))))
        if self.checkInterrupt():
            logger.debug('Interrupted')
            return
        self.status = mks647bc.drivers.STATUS_INITIALIZED
        if self.wnd.isDisposed():
            self.displayUI()

    def shutdown(self):
        if self.checkInterrupt():
            return
        self.status = mks647bc.drivers.STATUS_UNINITIALIZED
        if not self.wnd.isDisposed():
            self.wnd.dispose()


mks647bc.drivers.registerDriver('emulation', EmulationDeviceDriver, EmulationConfigurationSegment, 'Emulation')
