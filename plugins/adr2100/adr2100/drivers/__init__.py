# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/adr2100/src/adr2100/drivers/__init__.py
# Compiled at: 2004-12-07 22:46:58
import threading, traceback, logging
logger = logging.getLogger('adr2100.drivers')
STATUS_INITIALIZED = 0
STATUS_UNINITIALIZED = 1
DRIVERS = {}

def registerDriver(driverID, clazz, configPageClazz, name):
    global DRIVERS
    if driverID in DRIVERS:
        logger.warning("* WARNING: Attempt to register driver with same id '%s'" % driverID)
        return
    DRIVERS[driverID] = {'driver': clazz, 'configpage': configPageClazz, 'name': name}


def getDriverClassByName(driverName):
    for (key, value) in list(DRIVERS.items()):
        if value['name'] == driverName:
            return value['driver']

    return None


def getDriverTypeByName(driverName):
    for (key, value) in list(DRIVERS.items()):
        if value['name'] == driverName:
            return key

    return None


def getDriverPageByName(driverName):
    for (key, value) in list(DRIVERS.items()):
        if value['name'] == driverName:
            return getDriverConfigurationPage(key)

    return None


def getRegisteredDeviceKeys():
    return list(DRIVERS.keys())


def getDriverName(driverID):
    if driverID not in DRIVERS:
        return None
    return DRIVERS[driverID]['name']


def getDriver(driverID):
    if driverID not in DRIVERS:
        return None
    return DRIVERS[driverID]['driver']


def getDriverConfigurationPage(driverID):
    if driverID not in DRIVERS:
        return None
    return DRIVERS[driverID]['configpage']()


OUTPUT = 0
INPUT = 1

class DeviceDriver(object):
    __module__ = __name__

    def __init__(self, hwinst):
        global STATUS_UNINITIALIZED
        self.status = STATUS_UNINITIALIZED
        self.configuration = None
        self.cv = threading.Condition()
        self.ir = False
        self.busy = False
        return

    def markBusy(self):
        self.cv.acquire()
        self.busy = True

    def markFree(self):
        self.busy = False
        self.cv.release()

    def isBusy(self):
        self.cv.acquire()
        return self.busy

    def getID(self):
        raise Exception('Not Implemented')

    def configureDigitalPorts(self, port, config):
        raise Exception('Not Implemented')

    def outputBinaryData(self, port, data):
        raise Exception('Not Implemented')

    def readAnalogPorts(self):
        raise Exception('Not implemented')

    def readAnalogPort(self, port):
        raise Exception('Not implemented')

    def readDigitalPorts(self, port):
        raise Exception('Not Implemented')

    def setConfiguration(self, configuration):
        self.configuration = configuration

    def getConfiguration(self):
        return self.configuration

    def initialize(self):
        pass

    def shutdown(self):
        pass

    def getStatus(self):
        return self.status

    def sendCommand(self, command):
        pass

    def sendAndWait(self, command, timeout=500):
        pass

    def discardAllInput(self):
        """Read all available data from the channel and discard it. 
        Used to flush prior to sending a critical command requiring a 
        response"""
        pass

    def interrupt(self):
        """Interrupt the device even if it was waiting for input."""
        self.cv.acquire()
        self.ir = True
        self.cv.notify()
        self.cv.release()
        if self.isBusy():
            self.cv.wait()
        self.cv.release()
        self.discardAllInput()

    def dispose(self):
        pass
