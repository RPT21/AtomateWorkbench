# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/furnacezone/src/furnacezone/response.py
# Compiled at: 2004-11-19 02:21:26
import plugins.executionengine.executionengine.engine as engine

class FurnaceZoneDeviceResponse(engine.DeviceResponse):
    __module__ = __name__

    def __init__(self, device, temperature):
        engine.DeviceResponse.__init__(self, device)
        self.temperature = temperature

    def setTemperature(self, temperature):
        self.temperature = temperature

    def getTemperature(self):
        return self.temperature

    def __repr__(self):
        return "[Furnace Zone Device Response '%s': Temperature: '%d']" % (self.device.getLabel(), self.getTemperature())
