# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/grideditor/src/grideditor/utils/validation.py
# Compiled at: 2004-11-12 19:14:23
import logging, copy, hardware.hardwaremanager
from plugins.validator.validator.participant import ValidationParticipant, ValidationError
import plugins.validator.validator.participant as participant
import plugins.validator.validator as validator
logger = logging.getLogger('grideditor.validation')
KEY_DURATION = 'duration'
KEY_LOOPING = 'looping'
KEY_DEVICE_CONFIGURATION = 'device-configuration'

class InvalidDurationError(ValidationError):
    __module__ = __name__

    def __init__(self, step, description):
        ValidationError.__init__(self, [
         participant.KEY_STEP, KEY_DURATION], 'Invalid Duration: %s' % description, step, None)
        self.setSeverity(participant.SEVERITY_ERROR)
        return


class InvalidLoopingError(participant.ValidationError):
    __module__ = __name__

    def __init__(self, step, description):
        participant.ValidationError.__init__(self, [
         participant.KEY_STEP, KEY_LOOPING], 'Invalid looping parameter: %s' % description, step, None)
        self.setSeverity(participant.SEVERITY_ERROR)
        return


class DeviceNotConfiguredError(participant.ValidationError):
    __module__ = __name__

    def __init__(self, device, description):
        participant.ValidationError.__init__(self, [
         participant.KEY_CONFIGURATION, KEY_DEVICE_CONFIGURATION], "Device not configured for device '%s' (%s): %s" % (device.getLabel(), device.getType(), description), None, device)
        self.setSeverity(participant.SEVERITY_ERROR)
        return


def validateEnclosingLoops(owner, recipe):
    """Validates looping per step
    * Checks that if it loops then it loops at least once
    * that the number of enclosing steps does not exceed the number of steps
    * that the number of enclosing steps does not intercept the beginning of another loop
    """
    valid = True
    stack = []
    stepIdx = -1
    for step in recipe.getSteps():
        stepIdx += 1
        if len(stack) > 0:
            ns = copy.copy(stack)
            stack = []
            for e in ns:
                if stepIdx > e:
                    break
                stack.append(e)

        if not step.doesRepeat():
            continue
        lastStep = stepIdx + step.getRepeatEnclosingSteps()
        if lastStep >= recipe.getStepsCount():
            valid = False
            owner.addError(InvalidLoopingError(step, 'The step cannot loop past the end of a recipe'))
        if step.getRepeatCount() == 0:
            valid = False
            owner.addError(InvalidLoopingError(step, 'The step has a loop but the number of repetitions is set to zero'))
        if step.getRepeatEnclosingSteps() < 0:
            valid = False
            owner.addError(InvalidLoopingError(step, 'The number of enclosing steps must be greater than zero'))
        if len(stack) > 0:
            last = stack[-1]
            if last == stepIdx and lastStep > stepIdx:
                valid = False
                owner.addError(InvalidLoopingError(step, 'A previous loop has marked this as a last step.  This step cannot loop more than 0 enclosing steps'))
            elif lastStep > last:
                valid = False
                owner.addError(InvalidLoopingError(step, 'The enclosing steps are invalid.  Valid enclosing steps is less than or equal to %d' % (last - stepIdx)))
        stack.append(lastStep)

    return valid


def validateDuration(owner, recipe):
    """Return True if valid, false otherwise."""
    valid = True
    for step in recipe.getSteps():
        if step.getDuration() < 1:
            valid = False
            owner.addError(InvalidDurationError(step, 'The step must last more than 1 second'))

    return valid


def validateGeneral(owner, recipe):
    return recipe.getStepsCount() > 0


def validateDevices(owner, recipe):
    devices = recipe.getDevices()
    valid = True
    for device in devices:
        hwhints = device.getHardwareHints()
        try:
            id = hwhints.getChildNamed('id').getValue()
        except Exception as msg:
            owner.addError(DeviceNotConfiguredError(device, 'No hardware configured'))
            valid = False
            continue

        desc = hardware.hardwaremanager.getHardwareByName(id)
        if desc is None:
            owner.addError(DeviceNotConfiguredError(device, 'The associated hardware in the hardware manager is missing'))
            valid = False
            continue
        inst = desc.getInstance()
        if not inst.isConfigured():
            owner.addError(DeviceNotConfiguredError(device, 'The associated hardware is not properly configured'))
            valid = False

    return valid
    return


class CompositeValidationParticipant(ValidationParticipant):
    __module__ = __name__

    def __init__(self):
        ValidationParticipant.__init__(self)
        self.validators = [validateDuration, validateEnclosingLoops, validateGeneral, validateDevices]

    def validate(self, recipe):
        """Return True if valid, false otherwise."""
        ValidationParticipant.validate(self, recipe)
        valid = True
        for func in self.validators:
            if not func(self, recipe):
                valid = False

        return valid


def init():
    validator.getDefault().addValidationParticipant(CompositeValidationParticipant())
