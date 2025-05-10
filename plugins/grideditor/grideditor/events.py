# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/grideditor/src/grideditor/events.py
# Compiled at: 2004-07-28 01:20:37
import time

class EventObject(object):
    """Generic event object class"""
    __module__ = __name__

    def __init__(self, source):
        self.source = source
        self.time = time.time()

    def getSource(self):
        return self.source

    def getTime(self):
        return self.time
