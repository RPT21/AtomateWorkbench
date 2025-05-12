# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/adr2100/src/adr2100/drivers/ser.py
# Compiled at: 2004-11-19 02:08:30
import wx, adr2100.drivers, socket, time, threading, select, adr2100.drivers, serial, logging
from hardware import ResponseTimeoutException
logger = logging.getLogger('adr2100.drivers.serial')
CHOICES_BAUDRATE = [
 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
CHOICES_PARITY = ['none', 'odd', 'even']
CHOICES_PARITY_TEXT = ['None', 'Odd', 'Even']
CHOICES_BITS = [7, 8]
CHOICES_STOPBITS = [1, 2]
CHOICES_PORTS = list(map((lambda p: p), list(range(9))))
ERROR_CODE_STRINGS = {111: {'short': 'Unrecognized command', 'long': 'The command transmitted is not recognized'}, 112: {'short': 'Syntax Error', 'long': 'The command sent is inproperly fomatted'}, 122: {'short': 'Invalid Data Field', 'long': 'The command parameter does not have a decimal form, or invalid characters were found within the parameter'}}
SERIAL_PARITY = {'none': (serial.PARITY_NONE), 'even': (serial.PARITY_EVEN), 'odd': (serial.PARITY_ODD)}

class PortEnumerator(threading.Thread):
    __module__ = __name__

    def run(self):
        global CHOICES_PORTS
        for i in range(32):
            ser = serial.Serial()
            ser.port = i
            try:
                ser.open()
                CHOICES_PORTS.append(i)
                ser.close()
            except Exception as msg:
                continue


def enumeratePorts():
    pe = PortEnumerator()
    pe.start()


class SerialConfigurationSegment(object):
    __module__ = __name__

    def __init__(self):
        self.complete = True
        self.fireText = True
        self.configChanged = False

    def getControl(self):
        return self.control

    def setOwner(self, owner):
        self.owner = owner

    def createControl(self, composite):
        global CHOICES_BAUDRATE
        global CHOICES_BITS
        global CHOICES_PARITY_TEXT
        global CHOICES_STOPBITS
        self.control = wx.Panel(composite, -1)
        try:
            sizer = wx.FlexGridSizer(0, 2, 10, 10)
            sizer.AddGrowableCol(1)

            def add(num):
                return num + 1

            portLabel = wx.StaticText(self.control, -1, 'Port:')
            self.portChoice = wx.ComboBox(self.control, -1, choices=list(map(add, CHOICES_PORTS)), style=wx.CB_READONLY)
            baudLabel = wx.StaticText(self.control, -1, 'Baud Rate:')
            self.baudChoice = wx.ComboBox(self.control, -1, choices=CHOICES_BAUDRATE, style=wx.CB_READONLY)
            parityLabel = wx.StaticText(self.control, -1, 'Parity:')
            self.parityChoice = wx.ComboBox(self.control, -1, choices=CHOICES_PARITY_TEXT, style=wx.CB_READONLY)
            stopbitsLabel = wx.StaticText(self.control, -1, 'Stop Bits:')
            self.stopbitsChoice = wx.ComboBox(self.control, -1, choices=CHOICES_STOPBITS, style=wx.CB_READONLY)
            wordSizeLabel = wx.StaticText(self.control, -1, 'Word Size:')
            self.wordSizeChoice = wx.ComboBox(self.control, -1, choices=CHOICES_BITS, style=wx.CB_READONLY)
            self.lockoutPanel = wx.CheckBox(self.control, -1, 'Lock out panel on initialization')
            sizer.Add(portLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
            sizer.Add(self.portChoice, 1, wx.ALIGN_CENTRE_VERTICAL)
            sizer.Add(baudLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
            sizer.Add(self.baudChoice, 0, wx.ALIGN_CENTRE_VERTICAL)
            sizer.Add(parityLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
            sizer.Add(self.parityChoice, 0, wx.ALIGN_CENTRE_VERTICAL)
            sizer.Add(stopbitsLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
            sizer.Add(self.stopbitsChoice, 0, wx.ALIGN_CENTRE_VERTICAL)
            sizer.Add(wordSizeLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
            sizer.Add(self.wordSizeChoice, 0, wx.ALIGN_CENTRE_VERTICAL)

            def onChoice(event):
                event.Skip()
                self.markDirty()

            self.control.Bind(wx.EVT_COMBOBOX, onChoice, self.portChoice)
            self.control.Bind(wx.EVT_COMBOBOX, onChoice, self.baudChoice)
            self.control.Bind(wx.EVT_COMBOBOX, onChoice, self.parityChoice)
            self.control.Bind(wx.EVT_COMBOBOX, onChoice, self.stopbitsChoice)
            self.control.Bind(wx.EVT_COMBOBOX, onChoice, self.wordSizeChoice)
            self.control.Bind(wx.EVT_CHECKBOX, onChoice, self.lockoutPanel)
            mainsizer = wx.BoxSizer(wx.VERTICAL)
            mainsizer.Add(sizer, 1, wx.EXPAND | wx.ALL, 10)
            mainsizer.Add(self.lockoutPanel, 0, wx.EXPAND | wx.ALL, 10)
            self.control.SetSizer(mainsizer)
            self.control.SetAutoLayout(True)
            mainsizer.Fit(self.control)
        except Exception as msg:
            logger.exception(msg)

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
        self.owner.setDirty(True)
        return

    def setData(self, data):
        global CHOICES_PARITY
        try:
            self.portChoice.SetSelection(CHOICES_PORTS.index(int(data.get('driver', 'port'))))
            self.baudChoice.SetSelection(CHOICES_BAUDRATE.index(int(data.get('driver', 'baudrate'))))
            self.parityChoice.SetSelection(CHOICES_PARITY.index(data.get('driver', 'parity')))
            self.stopbitsChoice.SetSelection(CHOICES_STOPBITS.index(int(data.get('driver', 'stopbits'))))
            self.lockoutPanel.SetValue(data.get('driver', 'panellockout').lower() == 'true')
            self.wordSizeChoice.SetSelection(CHOICES_BITS.index(int(data.get('driver', 'wordsize'))))
        except Exception as msg:
            logger.exception(msg)
            logger.warning('Cannot set proper values for driver segment: %s' % msg)
            self.setDefaultData()

    def setDefaultData(self):
        self.portChoice.SetSelection(0)
        self.baudChoice.SetSelection(0)
        self.parityChoice.SetSelection(0)
        self.stopbitsChoice.SetSelection(0)
        self.wordSizeChoice.SetSelection(0)

    def getData(self, data):
        if not data.has_section('driver'):
            data.add_section('driver')
        data.set('driver', 'port', str(CHOICES_PORTS[self.portChoice.GetSelection()]))
        data.set('driver', 'baudrate', str(CHOICES_BAUDRATE[self.baudChoice.GetSelection()]))
        data.set('driver', 'parity', str(CHOICES_PARITY[self.parityChoice.GetSelection()]))
        data.set('driver', 'stopbits', str(CHOICES_STOPBITS[self.stopbitsChoice.GetSelection()]))
        data.set('driver', 'panellockout', str(self.lockoutPanel.IsChecked()))
        data.set('driver', 'wordsize', str(CHOICES_BITS[self.wordSizeChoice.GetSelection()]))

    def setComplete(self, complete):
        self.complete = complete

    def isComplete(self):
        return self.complete


DEFAULT_TIMEOUT = 1000
CONDITION_DICT = {'A': 'on', 'B': 'low-power-degas', 'C': 'underranged', 'D': 'overranged', 'E': 'manually-off', 'F': 'auto-off', 'G': 'high-power-degas', 'H': 'initializing', 'I': 'zeroing', 'J': 'bad-sensor', 'K': 'disconnected', 'L': 'not-installed'}

class SerialDeviceDriver(adr2100.drivers.DeviceDriver):
    __module__ = __name__

    def __init__(self):
        adr2100.drivers.DeviceDriver.__init__(self)
        self.softwareVersion = None
        self.port = None
        self.portnum = None
        self.baudrate = None
        self.parity = None
        self.stopbits = None
        self.lockoutPanel = False
        self.range = list(map((lambda s: 1), list(range(4))))
        self.bits = 1
        self.wordsize = 7
        self.buff = ''
        self.delimeter = '\r'
        self.timeout = DEFAULT_TIMEOUT
        return

    def clearBuffer(self):
        self.buff = ''

    def getConfigurationSegment(self):
        return SerialConfigurationSegment()

    def scanBufferForCommand(self):
        cmd = ''
        idx = self.buff.find(self.delimeter)
        if idx >= 0:
            cmd = self.buff[:idx]
            self.buff = self.buff[idx + len(self.delimeter):]
            return cmd
        return None
        return

    def setConfiguration(self, configuration):
        global SERIAL_PARITY
        adr2100.drivers.DeviceDriver.setConfiguration(self, configuration)
        try:
            self.portnum = int(configuration.get('driver', 'port'))
            self.baudrate = int(configuration.get('driver', 'baudrate'))
            self.parity = SERIAL_PARITY[configuration.get('driver', 'parity')]
            self.stopbits = int(configuration.get('driver', 'stopbits'))
            self.lockoutPanel = configuration.get('driver', 'panellockout').lower() == 'true'
            self.wordsize = int(configuration.get('driver', 'wordsize'))
        except Exception as msg:
            logger.exception(msg)
            logger.error('Cannot configure network device driver: %s' % msg)
            raise Exception('* ERROR: Cannot configure network device driver: %s' % msg)

    def initialize(self):
        try:
            self.port = serial.Serial(port=self.portnum, baudrate=self.baudrate, parity=self.parity, stopbits=self.stopbits, bytesize=self.wordsize)
            self.port.open()
            self.checkInterrupt()
            self.status = adr2100.drivers.STATUS_INITIALIZED
            self.checkInterrupt()
            self.softwareVersion = self.getSoftwareVersion()
            logger.debug('Software version %s' % self.softwareVersion)
            if self.lockoutPanel:
                logger.debug('Locking panel')
                self.lockPanel()
        except Exception as msg:
            try:
                self.port.close()
            except:
                pass
            else:
                raise Exception(msg)

    def checkInterrupt(self):
        if self.ir:
            self.ir = False
            self.cv.acquire()
            self.cv.notify()
            self.cv.release()
            raise Exception('Block serial call was interrupted')

    def checkError(self, retval):
        global ERROR_CODE_STRINGS
        if len(retval) == 0:
            return retval
        if retval[0] == 'E':
            errorcode = int(retval[1:])
            raise Exception("Device Error['%s']: '%s'-'%s'" % (retval, ERROR_CODE_STRINGS[errorcode]['short'], ERROR_CODE_STRINGS[errorcode]['long']))
        else:
            return retval

    def enableChannel(self, channelNum, timeout=None):
        t = timeout
        if t == None:
            t = self.timeout
        ret = self.sendAndWait('@081%i:ON\r' % channelNum, t)
        self.checkError(ret)
        return

    def disableChannel(self, channelNum, timeout=None):
        t = timeout
        if t == None:
            t = self.timeout
        logger.debug('disableChannel: @081%i:OFF' % channelNum)
        ret = self.sendAndWait('@081%i:OFF\r' % channelNum, t)
        self.checkError(ret)
        return

    def lockPanel(self):
        ret = self.sendAndWait('@502 :L\r')
        self.checkError(ret)

    def unlockPanel(self):
        ret = self.sendAndWait('@502 :U\r')
        self.checkError(ret)

    def getChannelCondition(self, channelNum, timeout=None):
        t = timeout
        if t == None:
            t = self.timeout
        prefix = '@608%i' % channelNum
        ret = self.sendAndWait('%s?\r' % prefix, t)
        resp = ret[len(prefix) + 1:]
        code = CONDITION_DICT[resp[0]]
        data = None
        if resp[0] in ['A', 'B']:
            data = float(resp[1:]) * 1000 / self.range[channelNum - 1]
        return (
         code, data)
        return

    def getFlow(self, channelNum, timeout=None):
        t = timeout
        if t == None:
            t = self.timeout
        ret = self.sendAndWait('@608%i?\r' % channelNum, t)
        self.checkError(ret)
        return ret
        return

    def setRange(self, channel, r):
        self.range[channel - 1] = r
        return self.checkError(self.sendAndWait('@061%d:%d\r' % (channel, int(r)), self.timeout))

    def getSoftwareVersion(self):
        sid = self.sendAndWait('@701 ?\r', self.timeout)
        self.checkError(sid)
        return sid

    def setSetpoint(self, channel, flow):
        result = self.sendAndWait('@102%d:%d\r' % (channel, flow), self.timeout)
        self.checkError(result)
        return result

    def setSetpointMode(self, channel, mode):
        result = self.sendAndWait('@101%d:%s\r' % (channel, mode), self.timeout)
        self.checkError(result)
        return result

    def setUnits(self, channelNum, unitIndex):
        result = self.sendAndWait('PU %d\r' % unitIndex, self.timeout)
        self.checkError(result)
        return result

    def shutdown(self):
        if not self.status == adr2100.drivers.STATUS_INITIALIZED:
            return
        try:
            if self.lockoutPanel:
                self.unlockPanel()
        except Exception as msg:
            logger.exception(msg)
            logger.error('* ERROR: Cannot unlock panel')

        self.port.close()
        self.status = adr2100.drivers.STATUS_UNINITIALIZED

    def sendCommand(self, command):
        if not self.status == adr2100.drivers.STATUS_INITIALIZED:
            raise Exception('Driver is not initialized')
        self.port.write(command)
        self.port.flushOutput()

    def discardAllInput(self):
        adr2100.drivers.DeviceDriver.discardAllInput(self)
        self.ir = False
        self.buff = ''
        self.clearBuffer()
        try:
            self.port.flushOutput()
            self.port.flushInput()
            while self.port.inWaiting() > 0:
                self.port.read(self.port.inWaiting())

        except Exception as msg:
            logger.exception(msg)

    def sendAndWait(self, command, timeout=0):
        self.sendCommand(command)
        then = time.time()
        while True:
            data = None
            while data is None:
                avail = self.port.inWaiting()
                if avail:
                    numToRead = self.port.inWaiting()
                    data = self.port.read(numToRead)
                    self.buff += data
                    cmd = self.scanBufferForCommand()
                    if cmd is None:
                        data = None
                    else:
                        return cmd
                data = None
                self.markBusy()
                self.cv.wait(0.1)
                self.markFree()
                if self.ir:
                    self.ir = False
                    self.cv.acquire()
                    self.cv.notify()
                    self.cv.release()
                    raise Exception('Blocking serial call was interrupted')
                now = time.time()
                if not timeout is 0:
                    if (now - then) * 1000.0 > timeout:
                        logger.debug('Raising exception')
                        raise ResponseTimeoutException('Timeout while waiting for reply from port')

            rcpt = data
            return rcpt

        return None
        return


adr2100.drivers.registerDriver('serial', SerialDeviceDriver, SerialConfigurationSegment, 'Serial')
