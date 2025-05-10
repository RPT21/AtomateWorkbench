# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/mks647bc/src/mks647bc/drivers/ser.py
# Compiled at: 2005-08-13 03:03:00
import wx, mks647bc.drivers, socket, time, threading, select, mks647bc.drivers, serial, logging
from hardware import ResponseTimeoutException
logger = logging.getLogger('mks647.drivers.serial')
CHOICES_BAUDRATE = [
 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
CHOICES_PARITY = ['none', 'odd', 'even']
CHOICES_PARITY_TEXT = ['None', 'Odd', 'Even']
CHOICES_BITS = [7, 8]
CHOICES_STOPBITS = [1, 2]
CHOICES_PORTS = map((lambda p: p), range(9))
ERROR_CODE_STRINGS = {0: {'short': 'Channel Error', 'long': 'An invalid channel number was specified or the channel is missing'}, 1: {'short': 'Unknown Command', 'long': 'The command transmitted is unknown'}, 2: {'short': 'Syntax Error', 'long': 'Only one character was sent instead of the expected 2 bytes'}, 3: {'short': 'Invalid Expression', 'long': 'The command parameter does not have a decimal form, or invalid characters were found within the parameter'}, 4: {'short': 'Invalid Value', 'long': 'Parameter specified is outside the range'}, 5: {'short': 'Autozero Error', 'long': 'The gas must be switched off before attempting to zero the channel'}}
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
        self.complete = False
        self.fireText = True
        self.configChanged = False

    def getControl(self):
        return self.control

    def setOwner(self, owner):
        self.owner = owner

    def createControl(self, composite):
        global CHOICES_BAUDRATE
        global CHOICES_PARITY_TEXT
        global CHOICES_STOPBITS
        self.control = wx.Panel(composite, -1)
        try:
            sizer = wx.FlexGridSizer(0, 2, 10, 10)
            sizer.AddGrowableCol(1)

            def add(num):
                return num + 1

            portLabel = wx.StaticText(self.control, -1, 'Port:')
            self.portChoice = wx.ComboBox(self.control, -1, choices=map(add, CHOICES_PORTS), style=wx.CB_READONLY)
            baudLabel = wx.StaticText(self.control, -1, 'Baud Rate:')
            self.baudChoice = wx.ComboBox(self.control, -1, choices=CHOICES_BAUDRATE, style=wx.CB_READONLY)
            parityLabel = wx.StaticText(self.control, -1, 'Parity:')
            self.parityChoice = wx.ComboBox(self.control, -1, choices=CHOICES_PARITY_TEXT, style=wx.CB_READONLY)
            stopbitsLabel = wx.StaticText(self.control, -1, 'Stop Bits:')
            self.stopbitsChoice = wx.ComboBox(self.control, -1, choices=CHOICES_STOPBITS, style=wx.CB_READONLY)
            self.lockoutPanel = wx.CheckBox(self.control, -1, 'Lock out panel on initialization')
            sizer.Add(portLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
            sizer.Add(self.portChoice, 1, wx.ALIGN_CENTRE_VERTICAL)
            sizer.Add(baudLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
            sizer.Add(self.baudChoice, 0, wx.ALIGN_CENTRE_VERTICAL)
            sizer.Add(parityLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
            sizer.Add(self.parityChoice, 0, wx.ALIGN_CENTRE_VERTICAL)
            sizer.Add(stopbitsLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
            sizer.Add(self.stopbitsChoice, 0, wx.ALIGN_CENTRE_VERTICAL)

            def onChoice(event):
                event.Skip()
                self.markDirty()

            self.control.Bind(wx.EVT_CHOICE, onChoice, self.portChoice)
            self.control.Bind(wx.EVT_CHOICE, onChoice, self.baudChoice)
            self.control.Bind(wx.EVT_CHOICE, onChoice, self.parityChoice)
            self.control.Bind(wx.EVT_CHOICE, onChoice, self.stopbitsChoice)
            self.control.Bind(wx.EVT_CHECKBOX, onChoice, self.lockoutPanel)
            mainsizer = wx.BoxSizer(wx.VERTICAL)
            mainsizer.Add(sizer, 1, wx.GROW | wx.ALL, 10)
            mainsizer.Add(self.lockoutPanel, 0, wx.GROW | wx.ALL, 10)
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
        self.owner.markDirty()
        return

    def setData(self, data):
        global CHOICES_PARITY
        try:
            self.portChoice.SetSelection(CHOICES_PORTS.index(int(data.get('driver', 'port'))))
            self.baudChoice.SetSelection(CHOICES_BAUDRATE.index(int(data.get('driver', 'baudrate'))))
            self.parityChoice.SetSelection(CHOICES_PARITY.index(data.get('driver', 'parity')))
            self.stopbitsChoice.SetSelection(CHOICES_STOPBITS.index(int(data.get('driver', 'stopbits'))))
            self.lockoutPanel.SetValue(data.get('driver', 'panellockout').lower() == 'true')
        except Exception as msg:
            logger.exception(msg)
            logger.warning('Cannot set proper values for driver segment: %s' % msg)
            self.setDefaultData()

    def setDefaultData(self):
        self.portChoice.SetSelection(0)
        self.baudChoice.SetSelection(0)
        self.parityChoice.SetSelection(0)
        self.stopbitsChoice.SetSelection(0)

    def getData(self, data):
        if not data.has_section('driver'):
            data.add_section('driver')
        data.set('driver', 'port', str(CHOICES_PORTS[self.portChoice.GetSelection()]))
        data.set('driver', 'baudrate', str(CHOICES_BAUDRATE[self.baudChoice.GetSelection()]))
        data.set('driver', 'parity', str(CHOICES_PARITY[self.parityChoice.GetSelection()]))
        data.set('driver', 'stopbits', str(CHOICES_STOPBITS[self.stopbitsChoice.GetSelection()]))
        data.set('driver', 'panellockout', str(self.lockoutPanel.IsChecked()))

    def setComplete(self, complete):
        self.complete = complete

    def isComplete(self):
        return self.complete


DEFAULT_TIMEOUT = 1000
THROTTLE = 0.002

class SerialDeviceDriver(mks647bc.drivers.DeviceDriver):
    __module__ = __name__

    def __init__(self):
        mks647bc.drivers.DeviceDriver.__init__(self)
        self.port = None
        self.portnum = None
        self.baudrate = None
        self.parity = None
        self.stopbits = None
        self.lockoutPanel = False
        self.bits = 1
        self.buff = ''
        self.delimeter = '\r\n'
        self.timeout = DEFAULT_TIMEOUT
        self.channelRanges = {}
        self.channelSwitch = map((lambda x: False), range(9))
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
        mks647bc.drivers.DeviceDriver.setConfiguration(self, configuration)
        try:
            self.portnum = int(configuration.get('driver', 'port'))
            self.baudrate = int(configuration.get('driver', 'baudrate'))
            self.parity = SERIAL_PARITY[configuration.get('driver', 'parity')]
            self.stopbits = int(configuration.get('driver', 'stopbits'))
            self.lockoutPanel = configuration.get('driver', 'panellockout').lower() == 'true'
        except Exception as msg:
            logger.exception(msg)
            logger.error('Cannot configure network device driver: %s' % msg)
            raise Exception('* ERROR: Cannot configure network device driver: %s' % msg)

    def initialize(self):
        try:
            self.port = serial.Serial(port=self.portnum, baudrate=self.baudrate, parity=self.parity, stopbits=self.stopbits)
            self.port.open()
            self.checkInterrupt()
            self.status = mks647bc.drivers.STATUS_INITIALIZED
            self.discardAllInput()
            self.checkInterrupt()
            logger.debug('Get ID')
            did = self.getID()
            logger.debug('Past GET ID')
            if did.find('647') < 0:
                raise Exception('An id was returned but the id was not compatible with this driver')
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
            return
        if retval[0] == 'E':
            errorcode = int(retval[1])
            raise Exception("Device Error['%s']: '%s'-'%s'" % (retval, ERROR_CODE_STRINGS[errorcode]['short'], ERROR_CODE_STRINGS[errorcode]['long']))
        else:
            return

    def lockPanel(self):
        ret = self.sendAndWait('KD\r', self.timeout)
        self.checkError(ret)

    def unlockPanel(self):
        ret = self.sendAndWait('KE\r', self.timeout)
        self.checkError(ret)

    def channelOn(self, channelNum):
        output = self.sendAndWait('ON %i\r' % channelNum, self.timeout)
        self.checkError(output)
        self.channelSwitch[channelNum] = True
        logger.debug('channel %i on' % channelNum)

    def channelOff(self, channelNum):
        output = self.sendAndWait('OF %i\r' % channelNum, self.timeout)
        self.checkError(output)
        self.channelSwitch[channelNum] = False
        logger.debug('channel %i off' % channelNum)

    def enableFlow(self):
        output = self.sendAndWait('ON 0\r')
        self.checkError(output)
        logger.debug('flow enabled')

    def disableFlow(self):
        output = self.sendAndWait('OF 0\r', self.timeout)
        self.checkError(output)
        logger.debug('flow disabled')

    def getFlow(self, channelNum, timeout=None):
        t = timeout
        if t == None:
            t = self.timeout
        if not self.channelSwitch[channelNum]:
            return None
        output = self.sendAndWait('FL %i\r' % channelNum, t)
        self.checkError(output)
        logger.debug("spork '%s'" % output)
        logger.debug('the flow is: %s' % str(output))
        return int(output)
        return

    def getID(self):
        sid = self.sendAndWait('ID\r', self.timeout)
        self.checkError(sid)
        return sid

    def setSetpoint(self, channel, flow):
        converted = int(1000.0 * flow / self.channelRanges[channel] + 0.5)
        logger.debug('Setting setpoint to %d' % converted)
        result = self.sendAndWait('FS %d %d\r' % (channel, converted), self.timeout)
        self.checkError(result)
        return result

    def setRange(self, channel, range):
        logger.debug('Setting range: RA %d %d\r' % (channel, range))
        result = self.sendAndWait('RA %d %d\r' % (channel, range))
        self.channelRanges[channel] = range
        self.checkError(result)
        return result

    def setRangeIndex(self, channelNum, rangeIndex, range):
        logger.debug('Range index RA %d %d (%d)' % (channelNum, rangeIndex, range))
        result = self.sendAndWait('RA %d %d\r' % (channelNum, rangeIndex))
        self.channelRanges[channelNum] = range
        self.checkError(result)
        return result

    def setGCF(self, channelNum, gcf):
        logger.debug('GC %d %d\r' % (channelNum, int(gcf)))
        self.sendCommand('GC %d %d\r' % (channelNum, gcf))
        result = self.sendAndWait('GC %d R\r' % channelNum, self.timeout)
        self.checkError(result)
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
            print('* ERROR: Cannot unlock panel', msg)

        self.port.close()
        self.status = mks647bc.drivers.STATUS_UNINITIALIZED

    def sendCommand(self, command):
        if not self.status == mks647bc.drivers.STATUS_INITIALIZED:
            raise Exception('Driver is not initialized')
        self.port.write(command)
        self.port.flushOutput()

    def discardAllInput(self):
        mks647bc.drivers.DeviceDriver.discardAllInput(self)
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

    def sendAndWait(self, command, timeout=1000):
        global THROTTLE
        logger.debug('sending command with %d' % timeout)
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
                self.cv.wait(THROTTLE)
                self.markFree()
                if self.ir:
                    self.ir = False
                    self.cv.acquire()
                    self.cv.notify()
                    self.cv.release()
                    raise Exception('Blocking serial call was interrupted')
                now = time.time()
                if (now - then) * 1000.0 > timeout:
                    logger.debug('Raising exception')
                    raise ResponseTimeoutException('Timeout while waiting for reply from port')

            rcpt = data
            return rcpt

        return None
        return


mks647bc.drivers.registerDriver('serial', SerialDeviceDriver, SerialConfigurationSegment, 'Serial')
# global CHOICES_BITS ## Warning: Unused global
