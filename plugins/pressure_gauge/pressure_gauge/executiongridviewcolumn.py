# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/mfc/src/mfc/executiongridviewcolumn.py
# Compiled at: 2004-09-15 00:23:52
import grideditor.executiongridviewer, logging
logger = logging.getLogger('mfc.execgridview')

def factoryFunc(device, recipe):
    return ExecutionGridColumnContribution(device, recipe)


class ExecutionGridColumnContribution(grideditor.executiongridviewer.ExecutionGridColumnContribution):
    __module__ = __name__

    def __init__(self, device, recipe):
        grideditor.executiongridviewer.ExecutionGridColumnContribution.__init__(self, device, recipe)
        self.configureDevice()

    def configureDevice(self):
        uihints = self.device.getUIHints()
        hwhints = self.device.getHardwareHints()
        gcf = 100.0
        try:
            gcf = float(hwhints.getChildNamed('conversion-factor').getValue())
        except Exception, msg:
            logger.exception(msg)

        range = 65500
        try:
            range = float(hwhints.getChildNamed('range').getValue())
        except Exception, msg:
            logger.exception(msg)

        usegcf = True
        try:
            usegcf = uihints.getChildNamed('column-use-gcf').getValue().lower() == 'true'
        except Exception, msg:
            logger.exception(msg)

        self.GCF = gcf
        self.useGCF = usegcf

    def getHeaderLabel(self):
        return self.device.getLabel()

    def getValueAt(self, row):
        deviceIndex = self.recipe.getDeviceIndex(self.device)
        step = self.recipe.getStep(row)
        entry = step.getEntry(deviceIndex)
        if self.useGCF:
            return entry.getFlow() * (self.GCF / 100.0)
        return entry.getFlow()


grideditor.executiongridviewer.addExecutionGridColumnContributionFactory('mfc', factoryFunc)
