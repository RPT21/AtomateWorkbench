# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/executionengine/src/executionengine/purgemanager.py
# Compiled at: 2004-09-07 03:53:55
import logging, threading
logger = logging.getLogger('purgemanager')
purgeWorkers = []
purgeProxies = {}
listeners = []

class ProxyClass(object):
    __module__ = __name__

    def purgeEnd(self, worker):
        purgeEnd(worker)

    def purgeStart(self, worker):
        purgeStart(worker)

    def purgePause(self, worker):
        purgePause(worker)


def addListener(listener):
    if not listener in listeners:
        listeners.append(listener)


def removeListener(listener):
    if listener in listeners:
        listeners.remove(listener)


def addPurgeWorker(worker):
    global purgeWorkers
    logger.debug('Add Purge Worker: %s' % worker)
    proxy = ProxyClass()
    purgeProxies[worker] = proxy
    purgeWorkers.append(worker)
    worker.addPurgeListener(proxy)
    fireWorkerAdded(worker)


def fireWorkerAdded(worker):
    list(map((lambda listener: listener.workerAdded(worker)), listeners))


def removePurgeWorker(worker):
    logger.debug('Remove Purge Worker: %s' % worker)
    if worker in purgeWorkers:
        purgeWorkers.remove(worker)
        if worker in purgeProxies:
            worker.removePurgeListener(purgeProxies[worker])
            fireWorkerRemoved(worker)
            del purgeProxies[worker]


def fireWorkerRemoved(worker):
    list(map((lambda p: p.workerRemoved(worker)), listeners))


def getPurgeWorkers():
    return purgeWorkers


def cancelPurge():
    t = threading.Thread()
    t.run = internalCancelPurge
    t.start()


def internalCancelPurge():
    logger.debug('Internal cancel purge for %d workers' % len(purgeWorkers))
    for worker in purgeWorkers:
        logger.debug('Telling worker to cancel purge: %s' % worker)
        cancelWorker(worker)
        logger.debug('Done with worked %s' % worker)


def cancelWorker(worker):
    try:
        worker.stop()
    except Exception as msg:
        logger.exception(msg)


def purgeEnd(worker):
    logger.debug('Purge Ended: %s' % worker)
    fireWorkerPurgeEnd(worker)


def fireWorkerPurgeEnd(worker):
    list(map((lambda p: p.purgeEnd(worker)), listeners))


def purgeStart(worker):
    logger.debug('Purge Started: %s' % worker)
    fireWorkerPurgeStart(worker)


def fireWorkerPurgeStart(worker):
    list(map((lambda p: p.purgeStart(worker)), listeners))


def purgePause(worker):
    logger.debug('Purge Pause: %s' % worker)
    fireWorkerPurgePause(worker)


def fireWorkerPurgePause(worker):
    list(map((lambda p: p.purgePause(worker)), listeners))
