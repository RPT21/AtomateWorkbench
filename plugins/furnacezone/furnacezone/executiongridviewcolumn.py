# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/furnacezone/src/furnacezone/executiongridviewcolumn.py
# Compiled at: 2004-09-01 03:00:19
import grideditor.executiongridviewer

def factoryFunc(device, recipe):
    return ExecutionGridColumnContribution(device, recipe)


class ExecutionGridColumnContribution(grideditor.executiongridviewer.ExecutionGridColumnContribution):
    __module__ = __name__

    def getHeaderLabel(self):
        return self.device.getLabel()

    def getValueAt(self, row):
        deviceIndex = self.recipe.getDeviceIndex(self.device)
        step = self.recipe.getStep(row)
        entry = step.getEntry(deviceIndex)
        return entry.getSetpoint()


grideditor.executiongridviewer.addExecutionGridColumnContributionFactory('furnacezone', factoryFunc)
