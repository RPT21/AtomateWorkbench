# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/furnacezone/src/furnacezone/hw.py
# Compiled at: 2004-11-19 02:21:21
import logging
logger = logging.getLogger('furnacezone.hw')
RUNNING = 1
STOPPED = 2
TEMPERATURE = 3
SET_SETPOINT = 4
GET_SETPOINT = 5
PURGING = 6
TYPE2STR = {RUNNING: 'Running', STOPPED: 'Stopped', TEMPERATURE: 'Temperature', SET_SETPOINT: 'Set Setpoint', GET_SETPOINT: 'Get Setpoint', PURGING: 'Purging'}

class HardwareStatusEvent(object):
    __module__ = __name__

    def __init__(self, source, etype, data=None):
        self.source = source
        self.etype = etype
        self.data = data

    def getTypeString(self):
        return TYPE2STR[self.etype]

    def __repr__(self):
        return "HardwareStatusEvent etype:%s/data:'%s'" % (self.getTypeString(), self.data)


class HardwareStatusProvider(object):
    __module__ = __name__

    def __init__(self):
        self.statusListeners = []

    def statusGetTemperature(self, temperature):
        self.fireHardwareStatusProviderEvent(HardwareStatusEvent(self, TEMPERATURE, temperature))

    def fireHardwareStatusProviderEvent(self, event):
        logger.debug('will fire for listeners %s' % self.statusListeners)
        list(map((lambda p: p.hardwareStatusChanged(event)), self.statusListeners))

    def removeHardwareStatusProviderListener(self, listener):
        if listener in self.statusListeners:
            self.statusListeners.remove(listener)

    def addHardwareStatusProviderListener(self, listener):
        if listener not in self.statusListeners:
            self.statusListeners.append(listener)

    def fireStatusIsRunning(self):
        self.fireHardwareStatusProviderEvent(HardwareStatusEvent(self, RUNNING))

    def fireStatusIsStopped(self):
        self.fireHardwareStatusProviderEvent(HardwareStatusEvent(self, STOPPED))

    def fireStatusIsPurging(self):
        self.fireHardwareStatusProviderEvent(HardwareStatusEvent(self, PURGING))


class HardwareStatusListener(object):
    __module__ = __name__

    def __init__(self):
        pass

    def hardwareStatusChanged(self, event):
        pass
