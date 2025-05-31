# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/rs485/src/rs485/rs485type.py
# Compiled at: 2004-08-12 08:30:21
import plugins.hardware.hardware.hardwaretype
import plugins.rs485.rs485.userinterface as rs485_userinterface
import plugins.hardware.hardware as hardware
import plugins.rs485.rs485 as rs485

class RS485HardwareType(hardware.hardwaretype.HardwareType):
    __module__ = __name__

    def __init__(self):
        hardware.hardwaretype.HardwareType.__init__(self)

    def getType(self):
        return 'rs485'

    def getDeviceTypes(self):
        return ['up150', 'ut150']

    def getInstance(self):
        return rs485.RS485SerialNetwork()

    def getConfigurationPage(self):
        return rs485_userinterface.ConfigurationPage()

    def getDescription(self):
        return 'Addressable Serial Network'
