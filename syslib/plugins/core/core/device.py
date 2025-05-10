# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/core/src/core/device.py
# Compiled at: 2004-11-19 02:06:28
""" Another factory object that keeps track of devices """
import configurationelement, time, random
random.seed()

def createDeviceID():
    return str(time.time() * random.random())


class DeviceEditor(object):
    __module__ = __name__

    def __init__(self):
        self.control = None
        self.owner = None
        self.max = 1000.0
        return

    def setOwner(self, owner):
        self.owner = owner

    def updateOwner(self):
        if self.owner is not None:
            self.owner.fitMe()
        return

    def createControl(self, parent):
        return self.control

    def getControl(self):
        return self.control

    def setData(self, data):
        pass

    def getData(self, data):
        pass

    def setMax(self, max):
        self.max = max
        self.modified()

    def modified(self):
        pass


class PropertyChangeEvent(object):
    __module__ = __name__

    def __init__(self, source, key, oldValue, newValue):
        self.source = source
        self.key = key
        self.oldValue = oldValue
        self.newValue = newValue

    def getSource(self):
        return self.source

    def getPropertyName(self):
        return self.key

    def getOldValue(self):
        return self.oldValue

    def getNewValue(self):
        return self.newValue

    def __repr__(self):
        return "[PropertyChangeEvent: name='%s'/oldValue='%s'/newValue='%s'/source='%s'" % (self.key, self.oldValue, self.newValue, self.source)


class Device(object):
    __module__ = __name__

    def __init__(self, deviceType):
        self.deviceType = deviceType
        self.label = '[no label]'
        self.recipe = None
        self.createEmptyRootElement()
        self.propertyChangeListeners = []
        self.devID = createDeviceID()
        return

    def getID(self):
        return self.devID

    def setID(self, devID):
        self.devID = devID

    def setLabel(self, label):
        self.label = label

    def createEmptyRootElement(self):
        self.uihints = configurationelement.new('ui-hint')
        self.hardwarehints = configurationelement.new('hardware-hint')
        self.uihints.createChild('label').setValue(self.label)
        columnhints = self.uihints.createChild('column')
        columnhints.setAttribute('order', '0')
        columnhints.setAttribute('visible', 'true')
        columnhints.setAttribute('width', '100')

    def setRecipe(self, recipe):
        self.recipe = recipe

    def getIndex(self):
        return self.recipe.getDeviceIndex(self)

    def addPropertyChangeListener(self, listener):
        if not listener in self.propertyChangeListeners:
            self.propertyChangeListeners.append(listener)

    def removePropertyChangeListener(self, listener):
        if listener in self.propertyChangeListeners:
            self.propertyChangeListeners.remove(listener)

    def firePropertyChangedEvent(self, event):
        for listener in self.propertyChangeListeners:
            listener.propertyChanged(event)

    def getType(self):
        return self.deviceType

    def getUIHints(self):
        return self.uihints

    def getDeviceEditor(self):
        return None
        return

    def getHardwareHints(self):
        return self.hardwarehints

    def setHardwareHints(self, node):
        self.hardwarehints = node
        self.updateHardwareHints()

    def updateHardwareHints(self):
        pass

    def getDeviceStr(self):
        return '--invalid--'

    def setUIHints(self, node):
        self.uihints = node
        self.updateUIHints()

    def updateUIHints(self):
        self.label = self.uihints.getChildren('label')[0].getValue()

    def configurationUpdated(self):
        event = PropertyChangeEvent(self, 'ALL', None, None)
        self.updateUIHints()
        self.firePropertyChangedEvent(event)
        return

    def getLabel(self):
        return self.label

    def createNewStepEntry(self, fromExisting=None):
        """Create from with default values"""
        raise Exception('Not implemented for this device')

    def getConditionalContributions(self):
        return []

    def parseFromNode(self, node):
        raise Exception('Not implemented for this device!')

    def convertToNode(self, root):
        root.setAttribute('type', self.getType())
        root.setAttribute('id', self.getID())
        newUIHint = root.createChild('ui-hint')
        newHardwareHint = root.createChild('hardware-hint')
        newUIHint.clone(self.uihints)
        newHardwareHint.clone(self.hardwarehints)
        self.configurationUpdated()

    def clone(self):
        raise Exception('Not implemented exception')

    def dispose(self):
        pass
