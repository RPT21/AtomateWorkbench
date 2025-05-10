# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/hardware/src/hardware/actions.py
# Compiled at: 2005-06-10 18:51:17
import ui, poi.actions, hardware.userinterface.configurator

def openHardwareEditor():
    configurator = hardware.userinterface.configurator.HardwareConfigurator()
    configurator.createControl(ui.getDefault().getMainFrame().getControl())
    configurator.showModal()
    configurator.dispose()


class OpenHardwareManagerAction(poi.actions.Action):
    __module__ = __name__

    def __init__(self):
        poi.actions.Action.__init__(self, 'Hardware Manager ...', '', '')

    def run(self):
        openHardwareEditor()
