# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: /home/maldoror/apps/eclipse/workspace/com.atomate.workbench/plugins/up150/src/up150/stepentry.py
# Compiled at: 2004-08-12 02:18:21
import plugins.core.core.stepentry, plugins.core.core as core

def parseFromNode(node):
    stepentry = UP150StepEntry()
    temperature = int(node.getChildNamed('temperature').getValue())
    stepentry.setTemperature(temperature)
    return stepentry


class UP150StepEntry(core.stepentry.StepEntry):
    __module__ = __name__

    def __init__(self):
        core.stepentry.StepEntry.__init__(self)
        self.temperature = 0

    def setTemperature(self, temperature):
        self.temperature = temperature

    def getTemperature(self):
        return self.temperature

    def getType(self):
        return 'up150'

    def getValueForCut(self):
        return str(self.getTemperature())

    def convertToNode(self, root):
        temperatureNode = root.createChild('temperature')
        temperatureNode.setValue(str(self.getTemperature()))

    def clone(self):
        stepentry = UP150StepEntry()
        stepentry.temperature = self.temperature
        return stepentry

    def __repr__(self):
        return "[UP150StepEntry: type='%s', temperature='%s']" % (self.getType(), self.getTemperature())
