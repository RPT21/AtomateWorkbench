# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/validator/src/validator/participant.py
# Compiled at: 2004-08-25 21:37:16
SEVERITY_WARNING = 1
SEVERITY_ERROR = 2
KEY_STEP = 'step'
KEY_ENTRY = 'entry'
KEY_CONFIGURATION = 'configuration'

class ValidationError(object):
    __module__ = __name__

    def __init__(self, keys, description, step, device):
        self.description = description
        self.quickfixes = []
        self.severity = SEVERITY_WARNING
        self.step = step
        self.device = device
        self.keys = keys

    def getKeys(self):
        return self.keys

    def getDevice(self):
        return self.device

    def setDescription(self, description):
        self.description = description

    def getQuickFixes(self):
        return self.quickfixes

    def addQuickFix(self, quickfix):
        self.quickfixes.append(quickfix)

    def getDescription(self):
        return self.description

    def setSeverity(self, severity):
        self.severity = severity

    def getStep(self):
        return self.step


class QuickFix(object):
    __module__ = __name__

    def __init__(self):
        self.descrition = ''
        self.details = ''

    def setDescriptionse(self, description):
        self.description = description

    def setDetails(self):
        self.details = details

    def getDescription(self):
        return self.description

    def getDetails(self):
        return self.details

    def fix(self, recipe):
        pass


class ValidationParticipant(object):
    __module__ = __name__

    def __init__(self):
        self.owner = None
        self.errors = []
        return

    def clearErrors(self):
        del self.errors[0:]

    def addError(self, error):
        self.errors.append(error)

    def setOwner(self, owner):
        self.owner = owner

    def validate(self, recipe):
        """Return True if valid, false otherwise."""
        self.clearErrors()
        return True

    def getErrors(self):
        return self.errors

    def getQuickFixes(self):
        return []
