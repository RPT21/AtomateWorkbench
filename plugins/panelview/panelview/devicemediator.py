# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/panelview/src/panelview/devicemediator.py
# Compiled at: 2004-10-28 00:15:40
import wx, plugins.panelview.panelview.item, logging
from plugins.panelview.panelview.item import *

logger = logging.getLogger('panelview')
itemFactories = {}
devices = {}
recipeModel = None
view = None
views = []

def addViews(newview):
    global views
    if not newview in views:
        views.append(newview)


def removeView(view):
    global devices
    views.remove(view)
    for (key, value) in list(devices.items()):
        if view in value:
            del value[view]


def setView(newview):
    addViews(newview)


class EventProxy(object):
    __module__ = __name__

    def recipeModelChanged(self, event):
        if event.getEventType() == event.REMOVE_DEVICE:
            deviceRemoved(event.getDevice())
        elif event.getEventType() == event.ADD_DEVICE:
            deviceAdded(event.getDevice())


proxy = EventProxy()

def registerItemContributionFactory(deviceType, factory):
    global itemFactories
    if not deviceType in itemFactories:
        itemFactories[deviceType] = factory


def setRecipeModel(model):
    global recipeModel
    recipeModel = model
    if model is None:
        return
    recipeModel.addModifyListener(proxy)
    loadContributions()
    return


def deviceAdded(device):
    factory = getContributionFactory(device.getType())
    if factory is None:
        return
    wx.CallAfter(addContribution, factory, device)
    return


def addContribution(factory, device):
    global view
    logger.debug('Adding panel view contribution: %s/%s' % (factory, device))
    if not device in devices:
        devices[device] = {}
        for view in views:
            inst = factory.getInstance(device.getType())
            devices[device][view] = inst
            inst.setDevice(device)
            inst.setRecipeModel(recipeModel)
            view.addItem(inst)


def deviceRemoved(device):
    global view
    if not device in devices:
        return
    for (view, item) in list(devices[device].items()):
        wx.CallAfter(view.removeItem, item)

    del devices[device]


def getContributionFactory(typestr):
    if not typestr in itemFactories:
        return None
    return itemFactories[typestr]


def loadContributions():
    for device in recipeModel.getDevices():
        factory = getContributionFactory(device.getType())
        if factory is None:
            continue
        addContribution(factory, device)

    return


class DevicePanelViewContribution(PanelViewItem):
    __module__ = __name__

    def __init__(self):
        plugins.panelview.panelview.item.PanelViewItem.__init__(self)
        self.device = None
        self.recipeModel = None
        return

    def setDevice(self, device):
        self.device = device

    def setRecipeModel(self, recipeModel):
        oldModel = self.recipeModel
        self.recipeModel = recipeModel
        if oldModel is not None:
            self.recipeModel.removeModifyListener(self)
        if self.recipeModel is not None:
            self.recipeModel.addModifyListener(self)
        return

    def dispose(self):
        plugins.panelview.panelview.item.PanelViewItem.dispose(self)
        if self.recipeModel is not None:
            self.recipeModel.removeModifyListener(self)
        return

    def recipeModelChanged(self, event):
        if event.getEventType() == event.CHANGE_DEVICE:
            device = event.getDevice()
            if device == self.device:
                self.deviceChanged()

    def deviceChanged(self):
        pass
