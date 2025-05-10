# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/up150/src/up150/up150type.py
# Compiled at: 2004-08-13 22:51:37
import hardware.hardwaretype, up150, up150.userinterface

class UP150HardwareType(hardware.hardwaretype.HardwareType):
    __module__ = __name__

    def __init__(self):
        hardware.hardwaretype.HardwareType.__init__(self)

    def getType(self):
        return 'up150'

    def getDeviceTypes(self):
        return [
         'furnace_zone']

    def getInstance(self):
        return up150.UP150Hardware()

    def getConfigurationPage(self):
        return up150.userinterface.ConfigurationPage()

    def getDescription(self):
        return 'UP150 Controller'
