# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/hardware/src/hardware/utils/threads.py
# Compiled at: 2005-06-10 18:51:17
import threading, logging, executionengine.purgemanager as purgemanager
logger = logging.getLogger('hardware.utils.threads')

class BackgroundProcessThread(threading.Thread):
    __module__ = __name__

    def __init__(self, hwinst):
        threading.Thread.__init__(self)
        self.hwinst = hwinst
        self.paused = None
        self.lock = threading.Condition()
        self.done = False
        self.running = False
        return

    def run(self):
        pass

    def pause(self):
        self.lock.acquire()
        self.paused = True
        self.hwinst.interruptOperation()
        self.lock.notify()
        self.lock.release()

    def resume(self):
        self.lock.acquire()
        self.paused = False
        self.lock.notify()
        self.lock.release()

    def stop(self):
        self.lock.acquire()
        self.done = True
        try:
            self.hwinst.interruptOperation()
        except Exception, msg:
            logger.exception(msg)

        self.lock.notify()
        self.lock.release()


class PurgeThread(BackgroundProcessThread):
    __module__ = __name__

    def __init__(self, hwinst):
        BackgroundProcessThread.__init__(self, hwinst)
        self.throttle = 0.5
        self.listeners = []
        purgemanager.addPurgeWorker(self)

    def getDescription(self):
        return 'Generic Purge Thread'

    def getStatusText(self):
        if self.paused:
            return 'Paused'
        if self.done:
            return 'Done'
        if self.running:
            return 'Purging'
        return 'Idle'

    def pause(self):
        BackgroundProcessThread.pause(self)
        self.firePurgePause()

    def purgestart(self):
        pass

    def purgestop(self):
        pass

    def tick(self):
        pass

    def run(self):
        self.running = True
        self.firePurgeStart()
        self.purgestart()
        while not self.done:
            self.lock.acquire()
            self.lock.wait(self.throttle)
            if not self.paused:
                try:
                    self.tick()
                except Exception, msg:
                    logger.exception(msg)
                    break

            self.lock.release()

        try:
            self.purgestop()
        except Exception, msg:
            logger.exception(msg)

        self.firePurgeEnd()
        self.hwinst.finishedPurge()
        purgemanager.removePurgeWorker(self)

    def deactivateHardware(self):
        self.hwinst.deactivate()
        self.done = True

    def addPurgeListener(self, listener):
        if not listener in self.listeners:
            self.listeners.append(listener)

    def removePurgeListener(self, listener):
        if listener in self.listeners:
            self.listeners.remove(listener)

    def firePurgeEnd(self):
        map((lambda listener: listener.purgeEnd(self)), self.listeners)

    def firePurgeStart(self):
        map((lambda listener: listener.purgeStart(self)), self.listeners)

    def firePurgePause(self):
        map((lambda listener: listener.purgePause(self)), self.listeners)
