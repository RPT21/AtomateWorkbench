# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/adr2100/src/adr2100/adr2100type.py
# Compiled at: 2004-11-09 18:19:39
import plugins.adr2100.adr2100, plugins.hardware.hardware.hardwaretype
import plugins.adr2100.adr2100.userinterface as userinterface
import plugins.adr2100.adr2100.userinterface

class ADR2100HardwareType(plugins.hardware.hardware.hardwaretype.HardwareType):
    __module__ = __name__

    def __init__(self):
        plugins.hardware.hardware.hardwaretype.HardwareType.__init__(self)

    def getType(self):
        return 'adr2100'

    def getDeviceTypes(self):
        return []

    def getInstance(self):
        return plugins.adr2100.adr2100.ADR2100Hardware()

    def getConfigurationPage(self):
        return plugins.adr2100.adr2100.userinterface.ConfigurationPage()

    def getDeviceHardwareEditor(self):
        return plugins.adr2100.adr2100.userinterface.DeviceHardwareEditor()

    def getDescription(self):
        return 'ADR 2100 I/O Board'
