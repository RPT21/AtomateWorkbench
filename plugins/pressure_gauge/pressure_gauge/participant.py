# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/pressure_gauge/src/pressure_gauge/participant.py
# Compiled at: 2004-11-23 04:02:59
import labbooks, pressure_gauge.device, logging
logger = logging.getLogger('pressure_gauge.labbooks')

class PressureGaugeRunLogParticipant(labbooks.RunLogParticipant):
    __module__ = __name__

    def __init__(self):
        labbooks.RunLogParticipant.__init__(self)

    def getType(self):
        return 'pressure_gauge'

    def getRunLogHeaders(self, devices):
        headers = []
        for device in devices:
            if device.getType() == 'pressure_gauge':
                headers.append('%s-%s' % (device.getLabel(), 'Gauge 1'))
                headers.append('%s-%s' % (device.getLabel(), 'Gauge 2'))

        if len(headers) == 0:
            return None
        else:
            return headers
        return

    def writeToRunLog(self, envelope, runlog):
        responses = envelope.getResponseByType('pressure_gauge')
        try:
            for response in responses:
                pressure = response.getPressure()
                runlog.appendBuffer('\t%s\t%s' % tuple(pressure))

        except Exception, msg:
            logger.exception(msg)
