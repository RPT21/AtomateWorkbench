# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/mks146/src/mks146/mks146type.py
# Compiled at: 2004-10-14 01:59:48
import plugins.hardware.hardware.hardwaretype
import plugins.mks146.mks146.userinterface as mks146_userinterface
import plugins.hardware.hardware as hardware
import plugins.mks146.mks146.__init__ as mks146

class MKS146HardwareType(hardware.hardwaretype.HardwareType):
    __module__ = __name__

    def __init__(self):
        hardware.hardwaretype.HardwareType.__init__(self)

    def getType(self):
        return 'mks146'

    def getDeviceTypes(self):
        return ['mfc']

    def getInstance(self):
        return mks146.MKS146Hardware()

    def getConfigurationPage(self):
        return mks146_userinterface.ConfigurationPage()

    def getDeviceHardwareEditor(self):
        return mks146_userinterface.DeviceHardwareEditor()

    def getDescription(self):
        return 'MKS146 Mass Flow Controller'
