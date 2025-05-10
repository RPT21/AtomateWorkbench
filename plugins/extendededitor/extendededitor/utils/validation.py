# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/extendededitor/src/extendededitor/utils/validation.py
# Compiled at: 2004-11-12 19:06:17
import logging
logger = logging.getLogger('grideditor.validation')

def validateDuration(step):
    logger.debug("Validating duration: '%s'" % step)
    duration = step.getDuration()
    return duration >= 1


def validateRepeats(step, recipe):
    stepsCount = recipe.getStepsCount()
    stepIndex = recipe.getStepIndex(step)
    enclosingSteps = step.getRepeatEnclosingSteps()
    valid = False
    valid = stepIndex + enclosingSteps < stepsCount
    return valid


def validateValidNumberRepeats(step, recipe):
    enclosingSteps = step.getRepeatEnclosingSteps()
    if not step.doesRepeat():
        return True
    return enclosingSteps > 0
