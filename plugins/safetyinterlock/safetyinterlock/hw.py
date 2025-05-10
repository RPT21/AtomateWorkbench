# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/safetyinterlock/src/safetyinterlock/hw.py
# Compiled at: 2004-10-19 02:46:39
import hardware.hardwaremanager

class SafetyInterlockHardware(hardware.hardwaremanager.Hardware):
    __module__ = __name__

    def __init__(self):
        hardware.hardwaremanager.Hardware.__init__(self)

    def dispose(self):
        hardware.hardwaremanager.Hardware.dispose(self)

    def initialize(self):
        pass

    def shutdown(self):
        pass
