# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/mfc/src/mfc/validation.py
# Compiled at: 2004-10-27 04:33:50
import validator, validator.participant, mfc.device, logging
logger = logging.getLogger('mfc.validation')

class MFCInvalidRange(validator.participant.ValidationError):
    __module__ = __name__

    def __init__(self, step, device, description):
        validator.participant.ValidationError.__init__(self, [
         validator.participant.KEY_STEP, validator.participant.KEY_ENTRY], 'Invalid setpoint: %s' % description, step, device)
        self.setSeverity(validator.participant.SEVERITY_ERROR)


class MFCInvalidPurgeRange(validator.participant.ValidationError):
    __module__ = __name__

    def __init__(self, device, description):
        validator.participant.ValidationError.__init__(self, [
         validator.participant.KEY_ENTRY], 'Invalid purge setpoint: %s.  Device %s' % (description, device.getLabel()), None, device)
        self.setSeverity(validator.participant.SEVERITY_ERROR)
        return


def validatePurgeRange(owner, recipe):
    valid = True
    for device in recipe.getDevices():
        if device.getType() != 'mfc':
            continue
        print('Device has purge?', device.hasPurge())
        if not device.hasPurge():
            continue
        if device.getPurgeLength() == 0:
            valid = False
            owner.addError(MFCInvalidPurgeRange(device, 'Purge duration length cannot be 0'))
        range = device.getRange()
        gcf = device.getGCF() / 100.0
        if range is None:
            continue
        if int(device.getPurgeSetpoint() * 1000.0) > int(device.getRange() * 1000.0):
            owner.addError(MFCInvalidPurgeRange(device, 'Setpoint is outside the device range. Should be below %0.3f (%0.3f with %0.2f gcf)' % (range, range * gcf, gcf)))
            valid = False

    return valid
    return


def validateRange(owner, recipe):
    valid = True
    for step in recipe.getSteps():
        idx = 0
        for entry in step.getEntries():
            if not entry.getType() == mfc.device.DEVICE_ID:
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
            gcf = device.getGCF() / 100.0
            if range is None:
                continue
            modifier = 1000
            if int(modifier * entry.getFlow()) > int(modifier * range):
                valid = False
                owner.addError(MFCInvalidRange(step, device, 'Setpoint is outside the range. Should be below %0.3f (%0.3f with %0.2f gcf)' % (range, range * gcf, gcf)))

    return valid
    return


class CompositeValidationParticipant(validator.participant.ValidationParticipant):
    __module__ = __name__

    def __init__(self):
        validator.participant.ValidationParticipant.__init__(self)
        self.validators = [validateRange, validatePurgeRange]

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
