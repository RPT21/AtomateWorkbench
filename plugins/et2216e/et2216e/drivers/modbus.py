# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/et2216e/src/et2216e/drivers/modbus.py
# Compiled at: 2005-02-16 22:01:03
import struct, time, logging
logger = logging.getLogger('modbus')
DEBUG = True

def crc16(inmsg):
    """
    Calculates crc value of message and correctness of message
    Returns ( result, (crcl, crch))

    Returns CRC Low and CRC High of message.

    If the incoming message contains the CRC values on the last two bytes then
    it returns 0 if the crc is correct for the message.

    """
    CRC = 65535
    next = 0
    carry = 0
    n = 0
    crch = 0
    crcl = 0
    msg = list(inmsg)
    for next in map((lambda c: ord(c)), msg):
        CRC ^= next
        for n in range(8):
            carry = CRC & 1
            CRC >>= 1
            if carry:
                CRC ^= 40961

    crch = CRC / 256
    crcl = CRC % 256
    return (
     CRC, (crcl, crch))


def fmtHex(msg):
    buff = ''
    sep = ''
    for c in msg:
        buff += '%s0x%x' % (sep, ord(c))
        sep = ' '

    return buff


def formatRTUMessage(deviceaddr, function, msg):
    msg = struct.pack('BB', deviceaddr, function) + msg
    (result, (crcl, crch)) = crc16(msg)
    result = msg + struct.pack('BB', crcl, crch)
    if DEBUG:
        logger.debug("FormatRTUMessage '%s'" % fmtHex(result))
    return result


class ModbusRTUChannel(object):
    __module__ = __name__

    def __init__(self):
        self.delay = 0.02
        self.messageEnd = 0
        self.errorCount = 0

    def configure(self, port, deviceAddr):
        self.port = port
        self.deviceAddress = deviceAddr

    def formatReadWords(self, startAddress, numWords):
        return struct.pack('>HH', int(startAddress), int(numWords))

    def parseReadWordsMsg(self, result):
        self.checkError(result)
        numwords = ord(result[0]) / 2
        words = struct.unpack('>%dH' % numwords, result[1:])
        if DEBUG:
            logger.debug('Read %d' % len(result))
            logger.debug('\tNum Words: %d' % numwords)
            logger.debug('\tWords:%d' % words)
        return words

    def readWords(self, startAddress, numWords):
        msg = struct.pack('>HH', int(startAddress), int(numWords))
        result = self.sendMessage(3, msg)
        self.checkError(result)
        numwords = ord(result[0]) / 2
        words = struct.unpack('>%dH' % numwords, result[1:])
        if DEBUG:
            logger.debug('Read %d' % len(result))
            logger.debug('\tNum Words: %d' % numwords)
            logger.debug('\tWords:%d' % words)
        return words

    def writeWords(self, wordAddress, values):
        msg = struct.pack('>HHb', wordAddress, len(values), 2 * len(values))
        woot = ['>%dH' % len(list(map((lambda x: int(x)), values)))]
        woot.extend(values)
        msg += struct.pack(*woot)
        result = self.sendMessage(16, msg)
        self.checkError(result)
        (addr, numwritten) = struct.unpack('>HH', result)
        if DEBUG:
            logger.debug('Wrote')
            logger.debug('\tNum: %d' % numwritten)
            logger.debug('\tAddr %x' % addr)

    def formatWriteWord(self, address, value):
        msg = struct.pack('>HH', int(address), int(value))
        msg = self.formatRawMessage(6, msg)
        return msg

    def parseWriteWord(self, msg):
        self.checkError(msg)
        (addr, val) = struct.unpack('>HH', result)
        return val

    def writeWord(self, address, value):
        msg = struct.pack('>HH', int(address), int(value))
        result = self.sendMessage(6, msg)
        self.checkError(result)
        (addr, val) = struct.unpack('>HH', result)
        return val

    def fastRead(self):
        result = self.sendMessage(7, '')
        return ()

    def formatWriteBit(self, address, on):
        von = 0
        if on:
            von = 256
        msg = struct.pack('>HH', int(address), int(von))
        return self.formatRawMessage(5, msg)

    def parseWriteBit(self, result):
        self.checkError(result)
        (addr, val) = struct.unpack('>HH', result)
        return val & 1 << 8

    def writeBit(self, address, on):
        von = 0
        if on:
            von = 256
        msg = struct.pack('>HH', int(address), int(von))
        result = self.sendMessage(5, msg)
        self.checkError(result)
        (addr, val) = struct.unpack('>HH', result)
        return val & 1 << 8

    def checkError(self, buff):
        if len(buff) > 1:
            return
        if ord(buff[0]) == 2:
            msg = 'Illegal Data Address'
        else:
            msg = 'Illegal Data Value'
        raise Exception(msg)

    def readBits(self, startAddress, numBits):
        msg = struct.pack('>HH', int(startAddress), int(numBits))
        result = self.sendMessage(1, msg)
        numbytes = ord(result[0])
        bytes = result[1:]
        lst = list(map((lambda x: 0), list(range(numBits))))
        for i in range(numbytes):
            byte = ord(bytes[i])
            for j in range(8):
                index = i * 8 + j
                if index == numBits:
                    return lst
                lst[index] = byte & 1 << j

        return lst

    def formatRawMessage(self, function, msg):
        return formatRTUMessage(self.deviceAddress, function, msg)

    def sendMessage(self, function, msg):
        msg = formatRTUMessage(self.deviceAddress, function, msg)
        self.delayForSend()
        self.port.write(msg)
        self.port.flush()
        start = time.time()
        buff = ''
        startIn = 0
        isStarted = False
        logger.debug("preparing to wait for response on modbus: '%s'" % self)
        delta = time.time() - start
        while delta < 1:
            logger.debug("\tin waiting? '%d' => '%s'" % (self.port.inWaiting(), self))
            if self.port.inWaiting() > 0:
                startIn = time.time()
                buff += self.port.read(self.port.inWaiting())
                isStarted = True
            if isStarted and time.time() - startIn > self.delay:
                self.messageEnd = time.time()
                return self.parseMessage(buff)
            delta = time.time() - start

        logger.debug("ended wait on modbus: '%s'" % self)
        self.messageEnd = time.time()
        raise Exception('Timeout while waiting for reply from port.  Bytes read so far: %d' % len(buff))

    def parseMessage(self, msg):
        omsg = msg
        (result, ignored) = crc16(msg)
        logger.debug("modbus: '%s'" % fmtHex(msg))
        if result != 0:
            raise Exception('Bad CRC')
        addr = ord(msg[0])
        func = ord(msg[1])
        rest = msg[2:len(msg) - 2]
        l = len(msg) - 2
        (crcl, crch) = (
         ord(msg[l]), ord(msg[l + 1]))
        if DEBUG:
            logger.debug('parsed message:')
            logger.debug('\tAddress: %x' % addr)
            logger.debug('\tFunction Code %x' % func)
            logger.debug('\tMsg: %s', fmtHex(rest))
            logger.debug('\tCRC: %d, %x,%x' % (result, crcl, crch))
        if not self.deviceAddress == addr:
            raise Exception('Incorrect address %x, this channel uses %x' % (addr, self.deviceAddress))
        return rest

    def delayForSend(self):
        """Waits a little bit to let the min time b/w messages pass"""
        minimum = self.delay
        time.sleep(minimum)


if __name__ == '__main__':
    import serial
    DEBUG = True
    port = serial.Serial(0)
    print('Opening port 1')
    channel = ModbusRTUChannel()
    channel.configure(port, 1)
    print(('Reading software version: %0.4x' % channel.readWords(107, 1)))
    time.sleep(2)
    port.flush()
    port.write('\n\r*IDN?\n\r')
    print('waiting ...')
    time.sleep(2)
    print(('what is what', port.inWaiting()))
    if port.inWaiting() > 0:
        print((':', port.read(port.inWaiting())))
    port.write('')
    time.sleep(0.1)
    print(('waiting?', port.inWaiting()))
    if port.inWaiting() > 0:
        print(('>', port.read(port.inWaiting())))
    port.close()
