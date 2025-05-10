# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/pressure_gauge/src/pressure_gauge/hardwarestatusprovider.py
# Compiled at: 2004-11-11 03:22:29
import copy
RUNNING = 1
STOPPED = 2
PRESSURE = 3
TYPE2STR = {RUNNING: 'Running', STOPPED: 'Stopped', PRESSURE: 'Pressure'}

class HardwareStatusEvent(object):
    __module__ = __name__

    def __init__(self, source, etype, data=None):
        self.source = source
        self.etype = etype
        self.data = data

    def getTypeString(self):
        return TYPE2STR[self.etype]

    def __repr__(self):
        return "HardwareStatusEvent etype:%s/data:'%s'" % (self.getTypeString(), str(self.data))


class HardwareStatusProvider(object):
    __module__ = __name__

    def __init__(self):
        self.statusListeners = []

    def statusGetPressure(self, pressure):
        self.fireHardwareStatusProviderEvent(HardwareStatusEvent(self, PRESSURE, pressure))

    def fireHardwareStatusProviderEvent(self, event):
        listeners = copy.copy(self.statusListeners)
        for listener in listeners:
            listener.hardwareStatusChanged(event)

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


class HardwareStatusListener(object):
    __module__ = __name__

    def __init__(self):
        pass

    def hardwareStatusChanged(self, event):
        print 'Hardware status changed'
