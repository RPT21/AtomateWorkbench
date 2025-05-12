# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/mks647bc/src/mks647bc/drivers/network.py
# Compiled at: 2004-11-19 02:32:36
import wx, mks647bc.drivers, socket, time, threading, select, mks647bc.drivers

class NetworkConfigurationSegment(object):
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
        sizer = wx.FlexGridSizer(0, 2, 5, 5)
        sizer.AddGrowableCol(1)
        hostLabel = wx.StaticText(self.control, -1, 'Host:')
        self.hostField = wx.TextCtrl(self.control, -1)
        portLabel = wx.StaticText(self.control, -1, 'Port:')
        self.portField = wx.TextCtrl(self.control, -1)
        self.control.Bind(wx.EVT_TEXT, self.markDirty, self.hostField)
        self.control.Bind(wx.EVT_TEXT, self.markDirty, self.portField)
        sizer.Add(hostLabel, 0, wx.EXPAND | wx.ALIGN_CENTRE_VERTICAL)
        sizer.Add(self.hostField, 1, wx.EXPAND | wx.ALIGN_CENTRE_VERTICAL)
        sizer.Add(portLabel, 0, wx.EXPAND | wx.ALIGN_CENTRE_VERTICAL)
        sizer.Add(self.portField, 1, wx.EXPAND | wx.ALIGN_CENTRE_VERTICAL)
        self.control.SetSizer(sizer)
        self.control.SetAutoLayout(True)
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
        self.fireText = False
        try:
            self.hostField.SetValue(data.get('driver', 'host'))
            self.portField.SetValue(data.get('driver', 'port'))
        except Exception as msg:
            print(('*ERROR: Cannot set proper values for driver segment:', msg))
            self.hostField.SetValue('127.0.0.1')
            self.portField.SetValue('8081')

        self.fireText = True

    def getData(self, data):
        if not data.has_section('driver'):
            data.add_section('driver')
        data.set('driver', 'host', self.hostField.GetValue())
        data.set('driver', 'port', self.portField.GetValue())

    def setComplete(self, complete):
        self.complete = complete

    def isComplete(self):
        return self.complete


class NetworkDeviceDriver(mks647bc.drivers.DeviceDriver):
    __module__ = __name__

    def __init__(self):
        mks647bc.drivers.DeviceDriver.__init__(self)
        self.socket = None
        self.host = None
        self.port = None
        self.buff = ''
        self.delimeter = 'oi'
        debug = False
        if debug:
            self.shutdown = self.debug_shutdown
            self.initialize = self.debug_initialize
        else:
            self.shutdown = self.real_shutdown
            self.initialize = self.real_initialize
        return

    def getConfigurationSegment(self):
        return NetworkConfigurationSegment()

    def scanBufferForCommand(self):
        cmd = ''
        idx = self.buff.find(self.delimeter)
        if idx >= 0:
            cmd = self.buff[:idx]
            cmd.strip()
            self.buff = self.buff[idx + len(self.delimeter):]
            return cmd
        return None

    def setConfiguration(self, configuration):
        mks647bc.drivers.DeviceDriver.setConfiguration(self, configuration)
        try:
            self.port = configuration.get('driver', 'port')
            self.host = configuration.get('driver', 'host')
        except Exception as msg:
            print(('* ERROR: Cannot configure network device driver:', msg))
            raise Exception('* ERROR: Cannot configure network device driver: %s' % msg)

    def debug_shutdown(self):
        timeout = 30
        then = time.time()
        self.cv.acquire()
        self.ir = False
        while True:
            self.cv.wait(0.5)
            if self.ir:
                self.ir = False
                self.cv.release()
                raise Exception('Interrupted when shutdown ...')
            now = time.time()
            if now - then > timeout:
                self.ir = False
                self.cv.release()
                raise Exception('Timeout!')

    def debug_initialize(self):
        timeout = 5
        then = time.time()
        self.cv.acquire()
        self.ir = False
        while True:
            self.cv.wait(0.5)
            if self.ir:
                self.ir = False
                self.cv.release()
                raise Exception('Interrupted ... :)')
            now = time.time()
            if now - then > timeout:
                self.ir = False
                self.cv.release()
                raise Exception('Timeout while waiting for connection')

    def real_initialize(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, int(self.port)))
        self.status = mks647bc.drivers.STATUS_INITIALIZED

    def real_shutdown(self):
        if not self.status == mks647bc.drivers.STATUS_INITIALIZED:
            return
        self.socket.close()
        self.status = mks647bc.drivers.STATUS_UNINITIALIZED

    def sendCommand(self, command):
        if not self.status == mks647bc.drivers.STATUS_INITIALIZED:
            raise Exception('Driver is not initialized')
        self.socket.send(command)

    def discardAllInput(self):
        mks647bc.drivers.DeviceDriver.discardAllInput(self)
        self.ir = False
        self.cv.acquire()
        self.buff = ''
        while self.hasWaiting():
            self.socket.recv(1024)
            self.cv.wait(0.1)

        self.cv.release()

    def hasWaiting(self):
        (r, w, e) = select.select([self.socket], [], [], 0.2)
        return len(r) != 0

    def sendAndWait(self, command, timeout=0):
        self.sendCommand(command)
        then = time.time()
        self.cv.acquire()
        while True:
            data = None
            while data is None:
                avail = self.hasWaiting()
                if avail:
                    data = self.socket.recv(1024)
                    self.buff += data
                    cmd = self.scanBufferForCommand()
                    if cmd is None:
                        data = None
                    else:
                        self.cv.release()
                        return cmd
                data = None
                self.cv.wait(0.5)
                if self.ir:
                    self.ir = False
                    self.cv.release()
                    raise Exception('Blocking network call was interrupted')
                now = time.time()
                if not timeout is 0:
                    if (now - then) * 1000.0 > timeout:
                        self.cv.release()
                        raise Exception('Timeout while waiting for reply from host')

            rcpt = data
            self.cv.release()
            return rcpt

        self.cv.release()
        return None
        return


mks647bc.drivers.registerDriver('network', NetworkDeviceDriver, NetworkConfigurationSegment, 'Network')
