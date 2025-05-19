# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/up150/src/up150/up150node.py
# Compiled at: 2004-11-19 02:37:58
import plugins.rs485.rs485 as rs485

def hextoint(hexnum):
    return eval('0x' + hexnum)


def inttohex(intnum):
    return hex(int(intnum))[2:].upper()


DICTIONARY_UP150 = {'hours.minutes': ('WWRD0307 01 ', '0'), 'minutes.seconds': ('WWRD0307 01 ', '0'),
                    'panel lockout': ('WWRD0118 01 ', '2'), 'panel unlock': ('WWRD0118 01 ', '0'),
                    'reset': ('WWRD0121 01 ', '0'), 'run': ('WWRD0121 01 ', '1'), 'local': ('WWRD0121 01 ', '2'),
                    'setpoint': ('WWRD0114 01 ', ''), 'min temp': ('WWRD0306 01 ', ''), 'max temp': ('WWRD0305 01 ', ''),
                    'start temp': ('WWRD0228 01 ', ''), 'autotune on': ('WWRD0263 01 ', '1'),
                    'autotune off': ('WWRD0263 01 ', '0'), 'current setpoint': ('WRDD0010 01', ''),
                    'current temp': ('WRDD0002 01', ''), 'set pid': (['WRW03D0105 ', ' D0106 ', ' D0107 '], ['', '', '']),
                    'get pid': (['WRR03D0105 ', 'D0106 ', 'D0107'], ['', '', ''])}
CODE_TIME_UNITS = {'minutes.seconds': '0', 'hours.minutes': '1'}
ERROR_CODE_STRINGS = {'02': {'short': 'Unknown Command', 'long': 'The command transmitted is unknown'},
                      '03': {'short': 'Register Error', 'long': 'Specified register is unavailable for use'},
                      '04': {'short': 'Invalid Value', 'long': 'Parameter specified is outside the range'},
                      '05': {'short': 'Command Count Error', 'long': 'Invalid number of commands were specified'},
                      '06': {'short': 'Monitoring Error', 'long': 'Monitoring execution without monitor definition was attempted'},
                      '08': {'short': 'Parameter Error', 'long': 'Illegal parameter has been sent'},
                      '42': {'short': 'Checksum error', 'long': 'Expected value does not match the checksum'},
                      '43': {'short': 'Buffer Overflow', 'long': 'Received data is larger than the expected value'},
                      '44': {'short': 'EOT Timeout', 'long': 'End of data was not received before timeout'}}

class UP150DeviceNode(rs485.RS485SerialNetworkNode):
    __module__ = __name__

    def __init__(self, address):
        rs485.RS485SerialNetworkNode.__init__(self, address)
        self.configuration = None
        self.delimiters = ['\x02', '\x03\r']
        return

    def initialize(self):
        if self.configuration is None:
            raise Exception('UP150 [address: %s] is not configured' % self.address)
        timeUnits = CODE_TIME_UNITS[self.configuration.get('time units')]
        minTemp = self.configuration.get('min temp')
        maxTemp = self.configuration.get('max temp')
        idleTemp = self.configuration.get('idle temp')
        self.panelLockout = self.configuration.get('panel lockout')
        self.checkError(self.rs485network.sendData('\x02' + self.address + '010WWRD0307 01 ' + inttohex(timeUnits).zfill(4) + '\x03\r', self.delimiters))
        self.checkError(self.rs485network.sendData('\x02' + self.address + '010WWRD0306 01 ' + inttohex(minTemp).zfill(4) + '\x03\r', self.delimiters))
        self.checkError(self.rs485network.sendData('\x02' + self.address + '010WWRD0305 01 ' + inttohex(maxTemp).zfill(4) + '\x03\r', self.delimiters))
        self.checkError(self.rs485network.sendData('\x02' + self.address + '010WWRD0228 01 ' + inttohex(idleTemp).zfill(4) + '\x03\r', self.delimiters))
        if self.panelLockout:
            self.lockPanel()
        self.initStatus = rs485.STATUS_NODE_INITIALIZED
        self.runStatus = rs485.STATUS_NODE_IDLE
        return

    def getData(self):
        data = self.rs485network.sendData('\x02' + self.address + '010WRDD0002 01\x03\r', self.delimiters)
        self.checkError(data)
        return self.translateData(data)

    def hasSetpointCapability(self):
        return True

    def setSetpoint(self, setpoint):
        if self.runStatus == rs485.STATUS_NODE_IDLE:
            self.checkError(self.rs485network.sendData('\x02' + self.address + '010WWRD0121 01 0002\x03\r', self.delimiters))
            self.runStatus = rs485.STATUS_NODE_RUNNING
        self.checkError(self.rs485network.sendData('\x02' + self.address + '010WWRD0114 01 ' + inttohex(setpoint).zfill(4) + '\x03\r', self.delimiters))
        return

    def checkError(self, data):
        if data.count('OK') > 0:
            if data[:2] == self.address:
                return
            else:
                raise Exception('Device Error: Address Error-request and reponse addresses are mismatched')
        elif data.count('ER') > 0:
            errorIndex = data.find('ER') + len('ER')
            errorcode = data[errorIndex:errorIndex + 2]
            raise Exception("Device Error['%s']: '%s'-'%s'" % (data, ERROR_CODE_STRINGS[errorcode]['short'], ERROR_CODE_STRINGS[errorcode]['long']))
        else:
            raise Exception('Device Error: Unknown Error')

    def translateData(self, data):
        return float(hextoint(data[7:]))

    def cleanUp(self):
        self.deactivate()
        if self.panelLockout:
            self.unlockPanel()
        self.initStatus = rs485.STATUS_NODE_UNINITIALIZED

    def lockPanel(self):
        self.checkError(self.rs485network.sendData('\x02' + self.address + '010WWRD0118 01 0002\x03\r', self.delimiters))

    def unlockPanel(self):
        self.checkError(self.rs485network.sendData('\x02' + self.address + '010WWRD0118 01 0000\x03\r', self.delimiters))

    def activate(self):
        self.checkError(self.rs485network.sendData('\x02' + self.address + '010WWRD0121 01 0002\x03\r', self.delimiters))
        self.runStatus = rs485.STATUS_NODE_RUNNING

    def deactivate(self):
        self.checkError(self.rs485network.sendData('\x02' + self.address + '010WWRD0121 01 0000\x03\r', self.delimiters))
        self.runStatus = rs485.STATUS_NODE_IDLE
