# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/et2216e/src/et2216e/drivers/rs485driver.py
# Compiled at: 2005-01-24 14:58:20
import wx, time, threading, select, et2216e.drivers, serial, rs485, logging, hardware, hardware.hardwaremanager
from string import zfill
import et2216e.messages as messages, modbus

def hextoint(hexnum):
    return eval('0x' + hexnum)


def inttohex(intnum):
    return hex(int(intnum))[2:].upper()


logger = logging.getLogger('rs485driver')
MODE_NORMAL = 0
MODE_STANDBY = 1
MODE_CONFIGURATION = 2
MODES = [
 MODE_NORMAL, MODE_STANDBY, MODE_CONFIGURATION]
DISABLE_KEYS_REGISTER = 279

class SerialConfigurationSegment(object):
    __module__ = __name__

    def __init__(self):
        self.complete = False
        self.fireText = True
        self.configChanged = False
        self.configured = True

    def getControl(self):
        return self.control

    def setOwner(self, owner):
        self.owner = owner

    def createControl(self, composite):
        self.control = wx.Panel(composite, -1)
        try:
            sizer = wx.FlexGridSizer(0, 3, 5, 5)
            sizer.AddGrowableCol(1)

            def add(num):
                return num + 1

            hardwareLabel = wx.StaticText(self.control, -1, messages.get('dialog.rs485driver.hardwareids.label'))
            self.hardwareChoice = wx.ComboBox(self.control, -1, choices=self.getNetworkChoices(), style=wx.CB_READONLY)
            addressLabel = wx.StaticText(self.control, -1, messages.get('dialog.rs485driver.address.label'))
            self.addressText = wx.TextCtrl(self.control, -1)
            self.lockoutPanel = wx.CheckBox(self.control, -1, messages.get('dialog.rs485driver.lockout.label'))
            sizer.Add(hardwareLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
            sizer.Add(self.hardwareChoice, 1, wx.ALIGN_CENTRE_VERTICAL)
            sizer.Add(wx.Panel(self.control, -1, style=0, size=(1, 1)), 0)
            sizer.Add(addressLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL)
            sizer.Add(self.addressText, 1, wx.ALIGN_CENTRE_VERTICAL)

            def onChoice(event):
                event.Skip()
                idx = self.hardwareChoice.GetSelection()
                choice = self.getNetworkChoices()[idx]
                if choice != '':
                    self.addressText.Enable()
                else:
                    self.addressText.Disable()
                self.markDirty()

            def onLockout(event):
                event.Skip()
                self.markDirty()

            self.control.Bind(wx.EVT_COMBOBOX, onChoice, self.hardwareChoice)
            self.control.Bind(wx.EVT_TEXT, self.OnAddressText, self.addressText)
            self.control.Bind(wx.EVT_CHECKBOX, onLockout, self.lockoutPanel)
            self.control.Bind(wx.EVT_KILL_FOCUS, self.OnAddressFocusText, self.addressText)
            mainsizer = wx.BoxSizer(wx.VERTICAL)
            mainsizer.Add(sizer, 0, wx.GROW | wx.ALL, 10)
            mainsizer.Add(self.lockoutPanel, 0, wx.LEFT, 10)
            self.control.SetSizer(mainsizer)
            self.control.SetAutoLayout(True)
            mainsizer.Fit(self.control)
        except Exception, msg:
            logger.exception(msg)

        return self.control

    def getNetworkChoices(self):
        choices = []
        hwlist = hardware.hardwaremanager.getHardware()
        for description in hwlist:
            if description.getHardwareType() == 'rs485':
                choices.append(description.getName())

        return choices

    def OnAddressText(self, event):
        event.Skip()
        if not self.fireText:
            return
        self.markDirty()
        addr = self.addressText.GetValue()
        self.configured = False
        if not self.validateAddress(addr):
            pass
        self.configured = True

    def OnAddressFocusText(self, event):
        event.Skip()
        self.fireText = False
        addr = self.addressText.GetValue()
        try:
            self.addressText.SetValue(self.convertAddressValue(addr))
        except Exception, msg:
            logger.exception(msg)

        self.fireText = True

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

    def validateHardwareChoice(self, choiceName):
        description = hardware.hardwaremanager.getHardwareByName(choiceName)
        logger.debug("Got: '%s'" % description)
        if description is None:
            raise Exception("Network with '%s' id is not available" % choiceName)
        return

    def getSelectedNetworkInstance(self):
        logger.debug('Get selected network instance')
        choice = self.hardwareChoice.GetStringSelection()
        description = hardware.hardwaremanager.getHardwareByName(choice)
        if description is None:
            return None
        return description.getInstance()
        return

    def convertAddressValue(self, address):
        try:
            address = str(address)
            logger.debug('\tType: %s' % type(address))
            numericaddr = int(address)
            address = '%02d' % numericaddr
        except Exception, msg:
            raise Exception("'%s' is an invalid address. It must be a number." % address)

        return address

    def validateAddress(self, address):
        inst = self.getSelectedNetworkInstance()
        logger.debug("validating address '%s' for '%s'" % (address, inst))
        if len(address) == 0:
            return False
        address = self.convertAddressValue(address)
        try:
            numericaddr = int(address)
            if numericaddr > 99:
                raise Exception('Address cannot be greater than 99')
        except Exception, msg:
            raise Exception("'%s' is an invalid address. It must be a number." % address)

        logger.debug("Final address set to '%s'" % address)
        if not inst.hasAddress(address):
            return True
        node = inst.getNodeAtAddress(address)
        if node != self.owner.description.getInstance():
            return False
        return True

    def setData(self, data):
        self.fireText = False
        try:
            self.addressText.SetValue(data.get('driver', 'address'))
            choice = data.get('driver', 'networkid')
            self.validateHardwareChoice(choice)
            self.hardwareChoice.SetSelection(self.getNetworkChoices().index(choice))
        except Exception, msg:
            logger.exception(msg)
            logger.error("Cannot set proper values for driver segment: '%s'" % msg)
            self.setDefaultData()

        self.fireText = True
        try:
            self.lockoutPanel.SetValue(data.get('driver', 'lockout').lower() == 'true')
        except Exception, msg:
            logger.exception(msg)
            self.lockoutPanel.SetValue(False)

    def setDefaultData(self):
        self.hardwareChoice.SetSelection(0)
        self.lockoutPanel.SetValue(False)

    def getData(self, data):
        if not data.has_section('driver'):
            data.add_section('driver')
        data.set('driver', 'networkid', self.hardwareChoice.GetStringSelection())
        data.set('driver', 'address', self.convertAddressValue(self.addressText.GetValue()))
        chk = 'false'
        if self.lockoutPanel.GetValue():
            chk = 'true'
        data.set('driver', 'lockout', chk)

    def isConfigured(self):
        return self.configured

    def setComplete(self, complete):
        self.complete = complete

    def isComplete(self):
        return self.complete


DEFAULT_TIMEOUT = 1.0

class RS485Driver(et2216e.drivers.DeviceDriver, rs485.RS485SerialNetworkNode):
    __module__ = __name__

    def __init__(self, hwinst):
        et2216e.drivers.DeviceDriver.__init__(self, hwinst)
        rs485.RS485SerialNetworkNode.__init__(self, None)
        self.timeout = DEFAULT_TIMEOUT
        self.networkid = None
        self.network = None
        self.address = None
        self.configured = False
        self.runningMode = et2216e.drivers.MODE_RESET
        self.startOut = -1
        self.modbusChannel = modbus.ModbusRTUChannel()
        return

    def cleanUp(self):
        if self.hwinst.getStatus() != hardware.hardwaremanager.STATUS_STOPPED:
            self.hwinst.shutdown()

    def clearBuffer(self):
        self.buffer = ''

    def getConfigurationSegment(self):
        return SerialConfigurationSegment()

    def scanBufferForCommand(self):
        """
        Nothing needed here because modbus runs on ETX of silence and not chars
        """
        return None
        return

    def isConfigured(self):
        return self.configured

    def setConfiguration(self, configuration):
        et2216e.drivers.DeviceDriver.setConfiguration(self, configuration)
        logger.debug('Setting configuration for driver')
        try:
            self.address = configuration.get('driver', 'address')
            self.networkid = configuration.get('driver', 'networkid')
            self.lockout = configuration.get('driver', 'lockout').lower() == 'true'
            self.configured = True
        except Exception, msg:
            logger.exception(msg)
            self.configured = False
            raise Exception('* ERROR: Cannot configure network device driver: %s' % msg)

    def getRS485Network(self, networkid):
        nw = hardware.hardwaremanager.getHardwareByName(networkid)
        if nw is None:
            raise Exception("No rs485 network configured with name: '%s'" % networkid)
        return nw.getInstance()
        return

    def write(self, msg):
        self.network.sendNoWait(self, msg)

    def flush(self, msg):
        self.network.flush()

    def initialize(self):
        logger.debug('Initializing')
        logger.debug("\tAddress: '%s'" % self.address)
        logger.debug("\tRS485 Network: '%s'" % self.networkid)
        self.network = self.getRS485Network(self.networkid)
        if self.network.getStatus() != hardware.hardwaremanager.STATUS_RUNNING:
            logger.debug('Network is not started, starting')
            self.network.initialize()
        logger.debug('Checking if registered with network %d' % int(self.address))
        if not self.network.hasAddress(self.address):
            logger.debug('No. Adding to network')
            self.network.addNode(self)
        else:
            logger.debug("Yes, checking if i'm it")
            node = self.network.getNodeAtAddress(self.address)
            if node != self:
                logger.error("Node taken up by someone else: '%s' and i am %s" % (node, self))
                raise Exception("Node taken up by someone else: '%s' and i am %s" % (node, self))
            logger.debug('I am already part of the network. No need to add')
        try:
            self.modbusChannel.configure(self, int(self.address))
            self.softwareVersion = self.getSoftwareVersion()
            logger.debug('Software version %s' % self.softwareVersion)
            logger.debug('Turning Off Manual Mode')
            self.setManual(False)
            if self.lockout:
                self.lockPanel()
        except Exception, msg:
            logger.exception(msg)
            self.network.removeNode(self)
            raise

        self.status = et2216e.drivers.STATUS_INITIALIZED

    def readWords(self, startAddress, numWords):
        msg = self.modbusChannel.formatReadWords(startAddress, numWords)
        msg = self.modbusChannel.formatRawMessage(3, msg)
        result = self.sendAndWait(msg)
        self.resetTime()
        return self.modbusChannel.parseReadWordsMsg(result)

    def writeBit(self, address, on):
        msg = self.modbusChannel.formatWriteBit(address, on)
        result = self.sendAndWait(msg)
        self.resetTime()
        return self.modbusChannel.parseWriteBit(result)

    def setManual(self, manual):
        self.writeBit(2, manual)

    def writeWord(self, address, value):
        msg = self.modbusChannel.formatWriteWord(address, value)
        self.sendAndWait(msg)
        self.resetTime()

    def getSoftwareVersion(self):
        return '%0.4x' % self.readWords(107, 1)

    def resetTime(self):
        self.startOut = -1

    def frameEnded(self):
        if self.startOut == -1:
            return False
        return time.time() - self.startOut > self.modbusChannel.delay

    def incomingData(self):
        self.startOut = time.time()

    def checkNetwork(self):
        if self.network == None:
            raise Exception('No network configured for this hardware')
        return

    def shutdown(self):
        logger.debug('Shutdown')
        if not self.status == et2216e.drivers.STATUS_INITIALIZED:
            logger.debug('returning not intialized')
            return
        if self.runningMode:
            self.deactivate()
        logger.debug("Removing existing node '%s'" % self.address)
        self.network.removeNode(self)
        self.status = rs485.drivers.STATUS_UNINITIALIZED

    def sendCommand(self, command):
        self.checkNetwork()
        self.network.sendCommand(self, command)

    def sendAndWait(self, command, timeout=1):
        self.checkNetwork()
        self.clearBuffer()
        diff = time.time() - self.startOut
        if self.startOut != -1 and diff < self.modbusChannel.delay:
            logger.debug('Not paused for next send ... %f' % (self.modbusChannel.delay - diff))
            time.sleep(self.modbusChannel.delay - diff)
        return self.modbusChannel.parseMessage(self.network.sendAndWait(self, command, timeout))

    def interrupt(self):
        self.checkNetwork()
        logger.debug('Telling network to interrupt: %s' % self.network)
        self.network.interrupt(self)

    def getTemperature(self, timeout=1):
        self.checkNetwork()
        return self.readWords(1, 1)[0]

    def setSetpoint(self, setpoint, timeout=1):
        self.checkNetwork()
        if not self.runningMode:
            self.activate()
        self.writeWord(24, setpoint)

    def checkError(self, data):
        if True:
            return
        if data.count('OK') > 0:
            if data[:2] == self.address:
                return data
            else:
                raise Exception('Device Error: Address Error-request and reponse addresses are mismatched')
        elif data.count('ER') > 0:
            errorIndex = data.find('ER') + len('ER')
            errorcode = data[errorIndex:errorIndex + 2]
            raise Exception("Device Error['%s']: '%s'-'%s'" % (data, ERROR_CODE_STRINGS[errorcode]['short'], ERROR_CODE_STRINGS[errorcode]['long']))
        else:
            raise Exception('Device Error: Unknown Error')
        return data

    def translateData(self, data):
        """checks data, only valid for data acquisition commands"""
        return int(hextoint(data[data.index('OK') + len('OK'):]))

    def stripDelimiters(self, data):
        return data[data.index('\x02') + len('\x02'):data.index('\x03\r')]

    def lockPanel(self):
        self.checkNetwork()
        self.writeWord(DISABLE_KEYS_REGISTER, 1)

    def unlockPanel(self):
        self.checkNetwork()
        self.writeWord(DISABLE_KEYS_REGISTER, 0)

    def activate(self):
        self.checkNetwork()
        self.runStatus = et2216e.drivers.MODE_LOCAL

    def deactivate(self):
        self.checkNetwork()
        if self.lockout:
            self.unlockPanel()
        self.runStatus = et2216e.drivers.MODE_RESET

    def setMinimumTemperature(self, mt):
        self.checkNetwork()
        self.checkError(self.sendAndWait('\x02' + self.address + '010WWRD0306 01 ' + zfill(inttohex(mt), 4) + '\x03\r'))

    def setMaximumTemperature(self, mt):
        self.checkNetwork()
        self.checkError(self.sendAndWait('\x02' + self.address + '010WWRD0305 01 ' + zfill(inttohex(mt), 4) + '\x03\r'))


et2216e.drivers.registerDriver('rs485', RS485Driver, SerialConfigurationSegment, 'RS485')
