# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/hardware/src/hardware/userinterface/__init__.py
# Compiled at: 2005-06-10 18:51:17
import poi.views.contentprovider

class DeviceHardwareEditor(object):
    __module__ = __name__

    def __init__(self):
        self.control = None
        self.instance = None
        self.owner = None
        return

    def setInstance(self, instance):
        self.instance = instance

    def getControl(self):
        return self.control

    def createControl(self, parent):
        pass

    def setData(self, recipe, data):
        pass

    def getData(self, data):
        pass

    def setOwner(self, owner):
        self.owner = owner


class HardwareTypesLabelProvider(poi.views.contentprovider.LabelProvider):
    __module__ = __name__

    def __init__(self):
        poi.views.contentprovider.LabelProvider.__init__(self)

    def getImage(self, element):
        return None
        return

    def getText(self, element):
        return str(element)


class HardwareTypesContentProvider(poi.views.contentprovider.ContentProvider):
    __module__ = __name__

    def __init__(self):
        poi.views.contentprovider.ContentProvider.__init__(self)
        self.tinput = None
        return

    def inputChanged(self, viewer, oldInput, newInput):
        if self.tinput != newInput and newInput != None:
            self.tinput = newInput
        if viewer != None:
            viewer.refresh()
        return

    def getElements(self, inputElement):
        return self.tinput.getHardwareTypes()
