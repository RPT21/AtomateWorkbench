# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/pressure_gauge/src/pressure_gauge/response.py
# Compiled at: 2004-11-11 22:39:47
import plugins.executionengine.executionengine.engine
import plugins.executionengine.executionengine as executionengine


class PressureGaugeDeviceResponse(executionengine.engine.DeviceResponse):
    __module__ = __name__

    def __init__(self, device, pressure):
        executionengine.engine.DeviceResponse.__init__(self, device)
        self.pressure = pressure

    def getPressure(self):
        return self.pressure
