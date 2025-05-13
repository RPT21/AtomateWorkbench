# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/core/src/core/error.py
# Compiled at: 2004-09-24 01:07:52
import sys, traceback
from functools import reduce
LEVEL_ERROR = 1
LEVEL_WARNING = 2

class WorkbenchException(Exception):
    __module__ = __name__

    def __init__(self, message, level=LEVEL_ERROR, description='', original=None):
        Exception.__init__(self, message)
        if original is None:
            (exctype, value, tb) = sys.exc_info()
            if exctype == WorkbenchException:
                self.original = value.original
                self.description = value.description
                self.level = value.level
            else:
                msglist = reduce((lambda x, y: ' '.join((x, y))), traceback.format_tb(tb))
                del tb
                self.original = (exctype, value, msglist)
        else:
            self.original = original
        self.level = level
        self.description = description
        self.message = message
        return

    def getLevel(self):
        return self.level

    def getMessage(self):
        return self.message

    def getOriginal(self):
        return self.original

    def getDescription(self):
        return self.description
