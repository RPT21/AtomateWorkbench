# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/hardware/src/hardware/hardwaretype.py
# Compiled at: 2005-06-10 18:51:17


class HardwareType(object):
    __module__ = __name__

    def __init__(self):
        pass

    def getType(self):
        raise Exception('Not Implemented')

    def getDeviceTypes(self):
        return []

    def getConfigurationPage(self):
        return None

    def getInstance(self):
        raise Exception('Not implemented')

    def getManufacturer(self):
        return None

    def getDescription(self):
        return None

    def getLargeImage(self):
        return None

    def getDeviceHardwareEditor(self):
        return None
