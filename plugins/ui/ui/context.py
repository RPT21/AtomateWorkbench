# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/ui/src/ui/context.py
# Compiled at: 2004-09-22 08:18:49
import plugins.ui.ui as ui, wx, logging
logger = logging.getLogger('ui.context')
contextChangeListeners = []
properties = {'state': None}
EVT_CONTEXT_CHANGE_ID = wx.NewId()

def EVT_CONTEXT_CHANGE(win, func):
    win.Connect(-1, -1, EVT_CONTEXT_CHANGE_ID, func)


class InternalContextChangeEvent(wx.PyEvent):
    __module__ = __name__

    def __init__(self, key, oldvalue, newvalue):
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_CONTEXT_CHANGE_ID)
        self.key = key
        self.oldvalue = oldvalue
        self.newvalue = newvalue


class EndTaskEvent(wx.PyEvent):
    __module__ = __name__

    def __init__(self):
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_TASK_END_ID)  # No he trobat què és


def OnContextChange(event):
    fireContextChanged(event.key, event.oldvalue, event.newvalue)


def init():
    EVT_CONTEXT_CHANGE(ui.invisibleFrame, OnContextChange)


class ContextChangeEvent(object):
    __module__ = __name__

    def __init__(self, key, oldValue, newValue):
        self.key = key
        self.oldValue = oldValue
        self.newValue = newValue

    def getKey(self):
        return self.key

    def getOldValue(self):
        return self.oldValue

    def getNewValue(self):
        return self.newValue


def getProperty(key):
    global properties
    if key in properties:
        return properties[key]
    return None


def hasProperty(key):
    return key in properties


def getProperties():
    return list(properties.items())


def dumpProperties():
    for (key, value) in list(properties.items()):
        logger.debug('%s\t=>%s' % (key, value))


def setProperty(key, value):
    oldValue = None
    if key in properties:
        oldValue = properties[key]
    properties[key] = value
    wx.PostEvent(ui.invisibleFrame, InternalContextChangeEvent(key, oldValue, value))
    return


def addContextChangeListener(listener):
    global contextChangeListeners
    if listener not in contextChangeListeners:
        contextChangeListeners.append(listener)


def removeContextChangeListener(listener):
    if listener in contextChangeListeners:
        contextChangeListeners.remove(listener)


def fireContextChanged(key, oldValue, newValue):
    event = ContextChangeEvent(key, oldValue, newValue)
    if False:
        logger.debug('*** List of listeners ***')

        def p(t):
            print(t)

        list(map(p, contextChangeListeners))
        logger.debug('*** END ***')

    def firer(listener):
        listener.contextChanged(event)

    list(map(firer, contextChangeListeners))
