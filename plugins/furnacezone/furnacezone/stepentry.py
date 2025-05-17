# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/furnacezone/src/furnacezone/stepentry.py
# Compiled at: 2004-08-23 08:14:46
import plugins.core.core.stepentry, logging, plugins.core.core as core
SETPOINT_SINGLE = 0
SETPOINT_LINEAR_RAMP = 1
RAMP_FROM_LAST = 0
RAMP_FROM_SETPOINT = 1
logger = logging.getLogger('furnacezone')

def parseFromNode(node):
    stepentry = FurnaceZoneStepEntry()
    setpointNode = node.getChildNamed('setpoint')
    setpointval = int(setpointNode.getValue())
    spm = SETPOINT_SINGLE
    try:
        stmstr = setpointNode.getAttribute('mode')
        stepentry.setpointMode = tagsTosetpointModes[stmstr]
        if tagsTosetpointModes[stmstr] == SETPOINT_LINEAR_RAMP:
            frm = tagsToRampTypes[setpointNode.getAttribute('from')]
            stepentry.rampStart = frm
    except Exception as msg:
        logger.exception(msg)
        logger.warning('Unable to parse setpoint mode')

    stepentry.setSetpoint(setpointval)
    return stepentry


spmtags = (
 (
  SETPOINT_SINGLE, 'single'), (SETPOINT_LINEAR_RAMP, 'linear-ramp'))
ramptags = (
 (
  RAMP_FROM_LAST, 'temperature'), (RAMP_FROM_SETPOINT, 'setpoint'))
setpointModeToTags = {}
list(map((lambda x: setpointModeToTags.__setitem__(x[0], x[1])), spmtags))
tagsTosetpointModes = {}
list(map((lambda x: tagsTosetpointModes.__setitem__(x[1], x[0])), spmtags))
rampTypesToTags = {}
list(map((lambda x: rampTypesToTags.__setitem__(x[0], x[1])), ramptags))
tagsToRampTypes = {}
list(map((lambda x: tagsToRampTypes.__setitem__(x[1], x[0])), ramptags))

class FurnaceZoneStepEntry(core.stepentry.StepEntry):
    __module__ = __name__

    def __init__(self):
        core.stepentry.StepEntry.__init__(self)
        self.setpoint = 0
        self.setpointMode = SETPOINT_SINGLE
        self.rampStart = RAMP_FROM_LAST

    def setSetpoint(self, setpoint):
        self.setpoint = setpoint

    def getSetpoint(self):
        return self.setpoint

    def getSetpointMode(self):
        return self.setpointMode

    def setSetpointMode(self, mode):
        """define the type of setpoint ramp mode"""
        self.setpointMode = mode

    def isSingleSetpoint(self):
        if self.setpointMode == SETPOINT_SINGLE:
            return True
        return False

    def isLinearRamp(self):
        if self.setpointMode == SETPOINT_LINEAR_RAMP:
            return True
        return False

    def setRampStart(self, start):
        """define the starting temperature of the ramp"""
        self.rampStart = start

    def isRampFromLast(self):
        if self.rampStart == RAMP_FROM_LAST:
            return True
        return False

    def isRampFromSetpoint(self):
        if self.rampStart == RAMP_FROM_SETPOINT:
            return True
        return False

    def getType(self):
        return 'furnace_zone'

    def getValueForCut(self):
        return str(self.getSetpoint())

    def convertToNode(self, root):
        setpointNode = root.createChild('setpoint')
        setpointNode.setValue(str(self.getSetpoint()))
        try:
            setpointNode.setAttribute('mode', setpointModeToTags[self.getSetpointMode()])
            if self.getSetpointMode() == SETPOINT_LINEAR_RAMP:
                setpointNode.setAttribute('from', rampTypesToTags[self.rampStart])
        except Exception as msg:
            logger.exception(msg)
            logger.warning('Unable to convert recipe to node.  Using default values')
            setpointNode.setAttribute('mode', setpointModeToTags[SETPOINT_SINGLE])

    def clone(self):
        stepentry = FurnaceZoneStepEntry()
        stepentry.setpoint = self.setpoint
        stepentry.setpointMode = self.setpointMode
        stepentry.rampStart = self.rampStart
        return stepentry

    def __repr__(self):
        return "[FurnaceZoneStepEntry: type='%s', setopint='%s']" % (self.getType(), self.getSetpoint())
