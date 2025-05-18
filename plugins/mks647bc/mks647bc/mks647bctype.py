# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/mks647bc/src/mks647bc/mks647bctype.py
# Compiled at: 2004-10-14 01:59:52
import plugins.hardware.hardware.hardwaretype
import plugins.hardware.hardware as hardware
import plugins.mks647bc.mks647bc.userinterface as mks647bc_userinterface
import plugins.mks647bc.mks647bc.__init__ as mks647bc

class MKS647HardwareType(hardware.hardwaretype.HardwareType):
    __module__ = __name__

    def __init__(self):
        hardware.hardwaretype.HardwareType.__init__(self)

    def getType(self):
        return 'mks647bc'

    def getDeviceTypes(self):
        return [
         'mfc']

    def getInstance(self):
        return mks647bc.MKS647Hardware()

    def getConfigurationPage(self):
        return mks647bc_userinterface.ConfigurationPage()

    def getDeviceHardwareEditor(self):
        return mks647bc_userinterface.DeviceHardwareEditor()

    def getDescription(self):
        return 'MKS647BC Mass Flow Controller'
