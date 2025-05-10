# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/mfc/src/mfc/stepentry.py
# Compiled at: 2004-09-17 02:44:24
import core.stepentry, logging
logger = logging.getLogger('mfc')

def parseFromNode(node):
    stepentry = MFCStepEntry()
    flowval = float(node.getChildNamed('flow').getValue())
    stepentry.setFlow(flowval)
    return stepentry


class MFCStepEntry(core.stepentry.StepEntry):
    __module__ = __name__

    def __init__(self):
        core.stepentry.StepEntry.__init__(self)
        self.flow = 0

    def setFlow(self, flow):
        logger.debug('sert flow: %f' % flow)
        self.flow = flow

    def getFlow(self):
        return self.flow

    def getType(self):
        return 'mfc'

    def getValueForCut(self):
        return str(self.getFlow())

    def convertToNode(self, root):
        flowNode = root.createChild('flow')
        flowNode.setValue(str(self.getFlow()))

    def clone(self):
        stepentry = MFCStepEntry()
        stepentry.flow = self.flow
        return stepentry

    def __repr__(self):
        return "[MFCStepEntry: type='%s', flow='%s']" % (self.getType(), self.getFlow())
