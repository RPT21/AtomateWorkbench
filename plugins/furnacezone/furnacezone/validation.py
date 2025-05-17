# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/furnacezone/src/furnacezone/validation.py
# Compiled at: 2004-10-27 04:34:26
import plugins.validator.validator.participant, logging
import plugins.validator.validator as validator

logger = logging.getLogger('furnacezone.validation')

class FurnaceZoneInvalidRange(validator.participant.ValidationError):
    __module__ = __name__

    def __init__(self, step, device, description):
        validator.participant.ValidationError.__init__(self, [
         validator.participant.KEY_STEP, validator.participant.KEY_ENTRY], 'Invalid setpoint: %s' % description, step, device)
        self.setSeverity(validator.participant.SEVERITY_ERROR)


def validateRange(owner, recipe):
    valid = True
    for step in recipe.getSteps():
        idx = 0
        for entry in step.getEntries():
            if not entry.getType() == 'furnace_zone':
                idx += 1
                continue
            try:
                device = recipe.getDevice(idx)
            except Exception as msg:
                logger.exception(msg)
                idx += 1
                continue

            idx += 1
            range = device.getRange()
            if range is None:
                continue
            if entry.getSetpoint() > range:
                valid = False
                owner.addError(FurnaceZoneInvalidRange(step, device, 'Setpoint is outside the range. Should be below %f' % range))

    return valid


class CompositeValidationParticipant(validator.participant.ValidationParticipant):
    __module__ = __name__

    def __init__(self):
        validator.participant.ValidationParticipant.__init__(self)
        self.validators = [validateRange]

    def validate(self, recipe):
        """Return True if valid, false otherwise."""
        validator.participant.ValidationParticipant.validate(self, recipe)
        valid = True
        for func in self.validators:
            if not func(self, recipe):
                valid = False

        return valid


def init():
    validator.getDefault().addValidationParticipant(CompositeValidationParticipant())
