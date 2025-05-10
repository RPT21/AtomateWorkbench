# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/graphview/src/graphview/devicemediator.py
# Compiled at: 2004-11-19 02:22:36
import wx, panelview.item, logging
logger = logging.getLogger('panelview')
itemFactories = {}
devices = {}
recipeModel = None
view = None

def setView(newview):
    global view
    view = newview


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
    if not itemFactories.has_key(deviceType):
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
    global devices
    logger.debug('Adding panel view contribution: %s/%s' % (factory, device))
    if not device in devices:
        inst = factory.getInstance(device.getType())
        devices[device] = inst
        inst.setDevice(device)
        inst.setRecipeModel(recipeModel)
        view.addItem(inst)


def deviceRemoved(device):
    if not devices.has_key(device):
        return
    item = devices[device]
    del devices[device]
    wx.CallAfter(view.removeItem, item)


def getContributionFactory(typestr):
    if not itemFactories.has_key(typestr):
        return None
    return itemFactories[typestr]
    return


def loadContributions():
    for device in recipeModel.getDevices():
        factory = getContributionFactory(device.getType())
        if factory is None:
            continue
        addContribution(factory, device)

    return


class DevicePanelViewContribution(panelview.item.PanelViewItem):
    __module__ = __name__

    def __init__(self):
        panelview.item.PanelViewItem.__init__(self)
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
        panelview.item.PanelViewItem.dispose(self)
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
