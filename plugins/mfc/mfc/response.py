# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/mfc/src/mfc/response.py
# Compiled at: 2004-08-09 11:44:20
import executionengine.engine

class MFCDeviceResponse(executionengine.engine.DeviceResponse):
    __module__ = __name__

    def __init__(self, device, flow):
        executionengine.engine.DeviceResponse.__init__(self, device)
        self.flow = flow

    def getFlow(self):
        return self.flow
