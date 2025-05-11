# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/core/src/core/deviceregistry.py
# Compiled at: 2004-08-23 08:14:42
__devicesTable = {}

def init():
    pass

def addDeviceFactory(name, deviceInstance):
    global __devicesTable
    if not name in __devicesTable:
        __devicesTable[name] = deviceInstance


def getDeviceFactory(deviceName):
    if deviceName in __devicesTable:
        return __devicesTable[deviceName]
    return None


def getDeviceFactories():
    return list(__devicesTable.values())


def getDeviceNames():
    return list(__devicesTable.keys())


def print_debug():
    print(('** Device Registry: ', len(__devicesTable)))
    for device in list(__devicesTable.values()):
        print(('\tDevice: ', device.getType(), '-', device))
