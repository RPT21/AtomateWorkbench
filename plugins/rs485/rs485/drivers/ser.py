# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/rs485/src/rs485/drivers/ser.py
# Compiled at: 2004-12-07 10:31:20
import wx, socket, time, threading, select, plugins.rs485.rs485.drivers, logging, serial
from plugins.rs485.rs485.drivers import DeviceDriver, registerDriver
from plugins.hardware.hardware import ResponseTimeoutException
logger = logging.getLogger('rs485.drivers.serial')
CHOICES_BAUDRATE = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
CHOICES_PARITY = ['none', 'odd', 'even']
CHOICES_PARITY_TEXT = ['None', 'Odd', 'Even']
CHOICES_BITS = [7, 8]
CHOICES_STOPBITS = [1, 2]
CHOICES_PORTS = list(range(9))
SERIAL_PARITY = {'none': (serial.PARITY_NONE), 'even': (serial.PARITY_EVEN), 'odd': (serial.PARITY_ODD)}

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
        global CHOICES_PORTS
        global CHOICES_STOPBITS
        self.control = wx.Panel(composite, -1)
        try:
            sizer = wx.FlexGridSizer(0, 2, 5, 5)
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

            self.control.Bind(wx.EVT_COMBOBOX, onChoice, self.portChoice)
            self.control.Bind(wx.EVT_COMBOBOX, onChoice, self.baudChoice)
            self.control.Bind(wx.EVT_COMBOBOX, onChoice, self.parityChoice)
            self.control.Bind(wx.EVT_COMBOBOX, onChoice, self.stopbitsChoice)
            mainsizer = wx.BoxSizer(wx.VERTICAL)
            mainsizer.Add(sizer, 1, wx.GROW | wx.ALL, 10)
            self.control.SetSizer(mainsizer)
            self.control.SetAutoLayout(True)
            mainsizer.Fit(self.control)
        except Exception as msg:
            print(('**** ', Exception, msg))

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
        except Exception as msg:
            print(('*ERROR: Cannot set proper values for driver segment:', msg))
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

    def setComplete(self, complete):
        self.complete = complete

    def isComplete(self):
        return self.complete


DEFAULT_TIMEOUT = 1.0

class SerialNetworkDriver(DeviceDriver):
    __module__ = __name__

    def __init__(self):
        DeviceDriver.__init__(self)
        self.port = None
        self.portnum = None
        self.baudrate = None
        self.parity = None
        self.stopbits = None
        self.bits = 1
        self.buffer = ''
        self.timeout = DEFAULT_TIMEOUT
        self.seriallock = threading.Lock()
        self.currentNode = None
        self.receiveComplete = True
        self.lastWait = 0.004
        return

    def checkWait(self):
        now = time.time()
        delay = 0.02
        time.sleep(delay)
        if now - self.lastWait < delay:
            logger.debug('Sleeping .. zzzz %f' % (now - self.lastWait))
            time.sleep(now - self.lastWait)
        self.lastWait = time.time()

    def debugDumpLockStatus(self):
        logger.debug('DUMPING LOCK STATUS')
        logger.debug('\tSerial Lock: %s' % self.seriallock.locked_lock())
        logger.debug('\tCV Lock: %s' % self.cv._is_owned())
        logger.debug('DONE DUMPING LOCK')

    def clearBuffer(self):
        self.buffer = ''

    def getConfigurationSegment(self):
        return SerialConfigurationSegment()

    def setConfiguration(self, configuration):
        global SERIAL_PARITY
        DeviceDriver.setConfiguration(self, configuration)
        try:
            self.portnum = int(configuration.get('driver', 'port'))
            self.baudrate = int(configuration.get('driver', 'baudrate'))
            self.parity = SERIAL_PARITY[configuration.get('driver', 'parity')]
            self.stopbits = int(configuration.get('driver', 'stopbits'))
        except Exception as msg:
            print(('* ERROR: Cannot configure network device driver:', msg))
            raise Exception('* ERROR: Cannot configure network device driver: %s' % msg)

    def initialize(self):
        try:
            print('Initializing with:')
            print(('\tPort Num:', self.portnum))
            print(('\tBaud Rate:', self.baudrate))
            print(('\tParity:', self.parity))
            print(('\tStop Bits:', self.stopbits))
            self.port = serial.Serial(port=self.portnum, baudrate=self.baudrate, parity=self.parity, stopbits=self.stopbits)
            self.port.open()
            self.status = rs485.drivers.STATUS_INITIALIZED
        except Exception as msg:
            import traceback
            traceback.print_exc()
            try:
                self.port.close()
            except:
                pass
            else:
                raise Exception(msg)

    def checkError(self, retval):
        """
        global ERROR_CODE_STRINGS
        if len(retval) == 0:
            return # alls good if it's empty
            
        if retval[:2] == 'ER':
            # some error, yes
            errorcode = retval[2:4]
            raise Exception( "Device Error['%s']: '%s'-'%s'" % (retval, ERROR_CODE_STRINGS[errorcode]['short'], ERROR_CODE_STRINGS[errorcode]['long']) )
        else:
            return
        """
        pass

    def shutdown(self):
        logger.debug('shutdown')
        if not self.status == plugins.rs485.rs485.drivers.STATUS_INITIALIZED:
            print('returning not intialized')
            return
        self.port.close()
        self.status = plugins.rs485.rs485.drivers.STATUS_UNINITIALIZED

    def sendCommand(self, command):
        if not self.status == plugins.rs485.rs485.drivers.STATUS_INITIALIZED:
            raise Exception('Driver is not initialized')
        self.port.write(command)
        self.port.flush()

    def discardAllInput(self):
        logger.debug('Discarding all input')
        self.debugDumpLockStatus()
        if self.receiveComplete:
            return
        if self.currentNode is None:
            logger.debug('Current node is none')
            return
        self.cv.acquire()
        self.port.flushOutput()
        startTime = time.time()
        logger.debug('Going to wait for port to discard all input for %f' % self.timeout)
        while time.time() - startTime <= 10:
            print('in here')
            self.currentNode.appendToBuffer(self.port.read(self.port.inWaiting()))
            if self.currentNode.scanBufferForCommand() is None:
                break
            time.sleep(0.02)

        self.currentNode.clearBuffer()
        self.port.flushInput()
        logger.debug('Discard all input complete')
        self.cv.release()
        self.debugDumpLockStatus()
        return

    def sendNoWait(self, node, command):
        self.checkInterrupt()
        self.checkWait()
        try:
            self.markBusy()
            self.seriallock.acquire()
            self.currentNode = node
            self.sendCommand(command)
        finally:
            if self.busy:
                self.markFree()
            self.seriallock.release()

    def sendAndWait(self, node, command, timeout=DEFAULT_TIMEOUT):
        self.checkInterrupt()
        self.checkWait()
        try:
            self.markBusy()
            logger.debug("Acquiring serial lock with '%s'" % node)
            self.seriallock.acquire()
            self.receiveComplete = False
            self.currentNode = node
            self.clearBuffer()
            self.sendCommand(command)
            self.markFree()
            startTime = time.time()
            while True:
                self.checkInterrupt()
                self.markBusy()
                if self.port.inWaiting():
                    node.appendToBuffer(self.port.read(self.port.inWaiting()))
                    command = node.scanBufferForCommand()
                    node.incomingData()
                    if not command == None:
                        self.receiveComplete = True
                        return command
                if node.frameEnded():
                    logger.debug('Frame ended!')
                    self.receiveComplete = True
                    return node.getBuffer()
                self.cv.wait(0.025)
                self.checkInterrupt()
                if time.time() - startTime > self.timeout:
                    self.receiveComplete = True
                    raise ResponseTimeoutException('Timeout while waiting for reply from port')
                self.markFree()

        finally:
            if self.busy:
                self.markFree()
            logger.debug('releasing serial lock')
            self.seriallock.release()

    def checkInterrupt(self):
        if self.ir:
            self.ir = False
            self.cv.acquire()
            self.cv.notify()
            self.cv.release()
            raise Exception('Block serial call was interrupted')
        return


registerDriver('serial', SerialNetworkDriver, SerialConfigurationSegment, 'Serial')
# global CHOICES_BITS ## Warning: Unused global
