# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/goosemonitor/src/goosemonitor/goosedevicetype.py
# Compiled at: 2005-06-10 18:51:02
import plugins.hardware.hardware.hardwaretype
import plugins.hardware.hardware as hardware
import plugins.goosemonitor.goosemonitor.hw as goosehardware
import plugins.goosemonitor.goosemonitor as goosemonitor
import plugins.goosemonitor.goosemonitor.userinterface
GOOSE_TYPE = 'goose'

class GooseDeviceType(hardware.hardwaretype.HardwareType):
    __module__ = __name__

    def __init__(self):
        hardware.hardwaretype.HardwareType.__init__(self)

    def getType(self):
        return GOOSE_TYPE

    def getDeviceTypes(self):
        return []

    def getInstance(self):
        return goosehardware.GooseMonitorHardware()

    def getConfigurationPage(self):
        return goosemonitor.userinterface.ConfigurationPage()

    def getDeviceHardwareEditor(self):
        return goosemonitor.userinterface.DeviceHardwareEditor()

    def getDescription(self):
        return 'wxGoose Monitor'
