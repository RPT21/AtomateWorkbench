# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/furnacezone/src/furnacezone/participant.py
# Compiled at: 2004-10-29 23:08:52
import labbooks, furnacezone.device

class FurnaceZoneRunLogParticipant(labbooks.RunLogParticipant):
    __module__ = __name__

    def __init__(self):
        labbooks.RunLogParticipant.__init__(self)

    def getType(self):
        return 'furnacezone'

    def getRunLogHeaders(self, devices):
        headers = []
        for device in devices:
            if device.getType() == 'furnacezone':
                headers.append(device.getLabel())

        if len(headers) == 0:
            return None
        else:
            return headers
        return

    def writeToRunLog(self, envelope, runlog):
        responses = envelope.getResponseByType('furnacezone')
        for response in responses:
            runlog.appendBuffer('\t' + str(response.getTemperature()))
