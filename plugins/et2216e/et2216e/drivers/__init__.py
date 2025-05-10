# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/et2216e/src/et2216e/drivers/__init__.py
# Compiled at: 2004-10-26 03:23:44
import logging, threading, traceback
STATUS_INITIALIZED = 0
STATUS_UNINITIALIZED = 1
MODE_LOCAL = 1
MODE_RESET = 0
DRIVERS = {}
logger = logging.getLogger('et2216e')

def registerDriver(driverID, clazz, configPageClazz, name):
    global DRIVERS
    logger.debug('Registering driver %s/%s/%s' % (clazz, configPageClazz, name))
    if driverID in DRIVERS:
        logger.warning("Attempt to register driver with same id '%s'" % driverID)
        return
    DRIVERS[driverID] = {'driver': clazz, 'configpage': configPageClazz, 'name': name}


def getDriverClassByName(driverName):
    for (key, value) in DRIVERS.items():
        if value['name'] == driverName:
            return value['driver']

    return None


def getDriverTypeByName(driverName):
    for (key, value) in DRIVERS.items():
        if value['name'] == driverName:
            return key

    return None


def getDriverPageByName(driverName):
    for (key, value) in DRIVERS.items():
        if value['name'] == driverName:
            return getDriverConfigurationPage(key)

    return None


def getRegisteredDeviceKeys():
    return DRIVERS.keys()


def getDriverName(driverID):
    if not driverID in DRIVERS:
        return None
    return DRIVERS[driverID]['name']


def getDriver(driverID):
    if not driverID in DRIVERS:
        return None
    return DRIVERS[driverID]['driver']


def getDriverConfigurationPage(driverID):
    if not driverID in DRIVERS:
        return None
    return DRIVERS[driverID]['configpage']()


class DeviceDriver(object):
    __module__ = __name__

    def __init__(self, hwinst):
        global STATUS_INITIALIZED
        self.status = STATUS_INITIALIZED
        self.configuration = None
        self.cv = threading.Condition()
        self.ir = False
        self.busy = False
        self.hwinst = hwinst
        return

    def deactivate(self):
        pass

    def isConfigured(self):
        return False

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

    def setConfiguration(self, configuration):
        self.configuration = configuration

    def getConfiguration(self):
        return self.configuration()

    def getStatus(self):
        return self.status

    def initialize(self):
        pass

    def shutdown(self):
        pass

    def sendAndWait(self, command, timeout=None):
        pass

    def discardAllInput(self):
        """
        Read all available data from the channel and discard it. 
        Used to flush prior to sending a critical command requiring a 
        response
        """
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
