# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/core/src/core/utils/__init__.py
# Compiled at: 2004-11-23 21:27:01
import threading, traceback, sys, os
if sys.platform.find('linux') >= 0:
    import grp, pwd

class WrappedException(Exception):
    __module__ = __name__

    def __init__(self):
        Exception.__init__(self, 'Wrapped Exception')
        self.exception = sys.exc_info()[0]
        self.value = sys.exc_info()[1]
        self.stack = apply(traceback.format_exception, sys.exc_info())

    def getException(self):
        return self.exception

    def getValue(self):
        return self.value

    def getStack(self):
        return self.stack


class InterruptibleTimer(threading.Thread):
    __module__ = __name__

    def __init__(self, caller, interval):
        threading.Thread.__init__(self)
        self.interval = interval
        self.lock = threading.Condition()
        self.caller = caller
        self.interrupted = False
        self.running = False

    def isRunning(self):
        return self.running

    def setInterval(self, newInterval):
        self.interval = newInterval

    def prepare(self):
        self.interrupted = True

    def stop(self):
        if not self.running:
            return
        self.lock.acquire()
        self.interrupted = True
        self.lock.notify()
        self.lock.wait()
        self.interrupted = False
        self.running = False
        self.lock.release()

    def run(self):
        self.running = True
        while True:
            self.lock.acquire()
            self.lock.wait(self.interval / 1000.0)
            if self.interrupted:
                self.lock.notify()
                self.lock.release()
                return
            self.caller.perform()
            self.lock.release()
