# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/mkspdr2000/src/mkspdr2000/mkspdr2000type.py
# Compiled at: 2004-11-11 01:55:16
import plugins.mkspdr2000.mkspdr2000.userinterface
import plugins.hardware.hardware as hardware
import plugins.hardware.hardware.hardwaretype
import plugins.mkspdr2000.mkspdr2000 as mkspdr2000


class mkspdr2000HardwareType(hardware.hardwaretype.HardwareType):
    __module__ = __name__

    def __init__(self):
        hardware.hardwaretype.HardwareType.__init__(self)

    def getType(self):
        return 'mkspdr2000'

    def getDeviceTypes(self):
        return [
         'pressure_gauge']

    def getInstance(self):
        return mkspdr2000.mkspdr2000Hardware()

    def getConfigurationPage(self):
        return mkspdr2000.userinterface.ConfigurationPage()

    def getDescription(self):
        return 'MKS PDR 2000 Pressure Gauge Controller'
