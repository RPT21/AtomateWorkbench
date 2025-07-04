# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/et2216e/src/et2216e/et2216etype.py
# Compiled at: 2004-10-18 23:17:37
import plugins.hardware.hardware.hardwaretype, plugins.et2216e.et2216e as et2216e
import plugins.hardware.hardware as hardware, plugins.et2216e.et2216e.userinterface

class et2216eHardwareType(hardware.hardwaretype.HardwareType):
    __module__ = __name__

    def __init__(self):
        hardware.hardwaretype.HardwareType.__init__(self)

    def getType(self):
        return 'et2216e'

    def getDeviceTypes(self):
        return [
         'furnace_zone']

    def getInstance(self):
        return et2216e.et2216eHardware()

    def getConfigurationPage(self):
        return et2216e.userinterface.ConfigurationPage()

    def getDescription(self):
        return 'et2216e Controller'
