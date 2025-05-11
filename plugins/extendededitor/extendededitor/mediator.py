# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/extendededitor/src/extendededitor/mediator.py
# Compiled at: 2004-11-19 02:20:58
import ui.context, extendededitor

class Mediator(object):
    __module__ = __name__

    def __init__(self, editor):
        self.model = None
        self.editor = editor
        self.devices = {}
        return

    def setRecipeModel(self, model):
        self.model = model
        if model is None:
            self.unloadEditors()
            return
        self.model.addModifyListener(self)
        self.loadContributions()
        return

    def unloadEditors(self):
        for (device, item) in list(self.devices.items()):
            self.editor.removeEditorItem(item)

        self.devices = {}

    def deviceRemoved(self, device):
        if device not in self.devices:
            return
        item = self.devices[device]
        self.editor.removeEditorItem(item)

    def recipeModelChanged(self, event):
        if event.getEventType() == event.REMOVE_DEVICE:
            self.deviceRemoved(event.getDevice())
        elif event.getEventType() == event.ADD_DEVICE:
            self.deviceAdded(event.getDevice())

    def deviceAdded(self, device):
        factory = extendededitor.getContributionFactory(device.getType())
        if factory is None:
            return
        self.addContribution(factory, device)
        return

    def loadContributions(self):
        for device in self.model.getDevices():
            factory = extendededitor.getContributionFactory(device.getType())
            if factory is None:
                return
            self.addContribution(factory, device)

        return

    def addContribution(self, factory, device):
        item = factory.getInstance(device.getType())
        item.setDevice(device)
        self.editor.addEditorItem(item)
        if item.hasConditionalContributions():
            pass
        item.setContainerPanel(self.editor)
        item.setRecipeModel(self.model)
        self.devices[device] = item
