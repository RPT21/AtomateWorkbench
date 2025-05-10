# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/poi/src/poi/operation/__init__.py
# Compiled at: 2005-06-10 18:51:25
import traceback

class RunnableWithProgress(object):
    __module__ = __name__

    def run(self, monitor, fork=False):
        pass


class ProgressMonitor(object):
    __module__ = __name__

    def __init__(self):
        self.canceled = False

    def beginTask(self, name, totalWork):
        pass

    def endTask(self):
        pass

    def isCanceled(self):
        return self.canceled

    def setCanceled(self, canceled):
        self.canceled = canceled

    def subTask(self, name):
        pass

    def worked(self, amt):
        pass


class InvocationTargetException(Exception):
    __module__ = __name__

    def __init__(self, wrapped):
        self.wrapped = wrapped

    def getWrapped(self):
        return self.wrapped

    def __str__(self):
        f = traceback.format_exception(self.wrapped[0], self.wrapped[1], self.wrapped[2])
        buff = ''
        for e in f:
            buff += e

        return buff

    def __del__(self):
        del self.wrapped
