# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/pressure_gauge/src/pressure_gauge/stepentry.py
# Compiled at: 2004-11-11 02:31:52
import core.stepentry, logging
logger = logging.getLogger('pressure_gauge')

def parseFromNode(node):
    stepentry = PressureGaugeStepEntry()
    return stepentry


class PressureGaugeStepEntry(core.stepentry.StepEntry):
    __module__ = __name__

    def __init__(self):
        core.stepentry.StepEntry.__init__(self)

    def getType(self):
        return 'pressure_gauge'

    def getValueForCut(self):
        return ''

    def convertToNode(self, root):
        pass

    def clone(self):
        stepentry = PressureGaugeStepEntry()
        return stepentry

    def __repr__(self):
        return "[PressureGaugeStepEntry: type='%s']" % self.getType()
