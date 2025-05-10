# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/et2216e/src/et2216e/crc.py
# Compiled at: 2004-10-24 00:23:20
import struct

def crc16(inmsg):
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


def format(self, deviceaddr, function, address, value):
    pass


if __name__ == '__main__':
    import struct
    print 'Computing the value of the proper filling'
    msg = struct.pack('BBBBBBBB', 2, 3, 0, 1, 0, 2, 149, 248)
    (crc, result) = crc16(msg)
    print 'YES?', crc
    print 'Testing CRC16 should output hex values 0x41,0x12 for input 0x02,0x07'
    msg = struct.pack('bb', 2, 7)
    (crc, result) = crc16(msg)
    print 'raw:', crc, result
    for x in result:
        print '%x' % x

    if result[0] != 65:
        print 'Invalid'
    if result[1] != 18:
        print 'Invalid'
    print 'Second test'
    msg = struct.pack('bbbbbb', 2, 3, 0, 1, 0, 2)
    print 'Should output 0x95, 0xF8'
    (crc, result) = crc16(msg)
    for x in result:
        print '%x' % x

    if result[0] != 149:
        print 'Invalid'
    if result[1] != 248:
        print 'Invalid'
    print 'Checking crc values'
    msg = struct.pack('bbbb', 2, 7, 65, 18)
    (crc, result) = crc16(msg)
    print 'Result?', crc
