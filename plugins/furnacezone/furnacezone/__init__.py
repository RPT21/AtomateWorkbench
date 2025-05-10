# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/furnacezone/src/furnacezone/__init__.py
# Compiled at: 2004-10-08 00:47:25
DEVICE_ID = 'furnacezone'
import ui, kernel.plugin, core.deviceregistry, executionengine, furnacezone.execgraphitem, furnacezone.device, furnacezone.column, furnacezone.graphitem, furnacezone.extendededitoritem, furnacezone.participant, extendededitor, grideditor, labbooks, grapheditor, graphview, furnacezone.images as images, furnacezone.messages as messages, furnacezone.panelviewitem, panelview.devicemediator, logging, furnacezone.validation, furnacezone.executiongridviewcolumn
logger = logging.getLogger('furnacezone')

class FurnaceZoneDevicePlugin(kernel.plugin.Plugin):
    __module__ = __name__

    def __init__(self):
        kernel.plugin.Plugin.__init__(self)
        ui.getDefault().setSplashText('Loading Furnace Zone plugin ...')

    def startup(self, contextBundle):
        logger.debug("Registering '%s' as device" % furnacezone.device.DEVICE_ID)
        images.init(contextBundle)
        messages.init(contextBundle)
        panelview.devicemediator.registerItemContributionFactory(furnacezone.device.DEVICE_ID, FurnacePanelViewContributionFactory())
        core.deviceregistry.addDeviceFactory(furnacezone.device.DEVICE_ID, FurnaceZoneDeviceFactory())
        grideditor.addColumnContributionFactory(furnacezone.device.DEVICE_ID, FurnaceZoneColumnContributionFactory())
        grapheditor.addGraphContributionFactory(furnacezone.device.DEVICE_ID, FurnaceZoneGraphEditorContributionFactory())
        extendededitor.addContributionFactory(furnacezone.device.DEVICE_ID, FurnaceZoneExtendedEditorContributionFactory())
        labbooks.getDefault().registerDeviceParticipant(furnacezone.participant.FurnaceZoneRunLogParticipant())
        graphview.getDefault().registerViewFactory(furnacezone.device.DEVICE_ID, furnacezone.execgraphitem.graphViewFactory)
        furnacezone.validation.init()


class FurnacePanelViewContributionFactory(object):
    __module__ = __name__

    def getInstance(self, deviceType):
        return furnacezone.panelviewitem.FurnaceZonePanelViewItem()


class FurnaceZoneExtendedEditorContributionFactory(object):
    __module__ = __name__

    def getInstance(self, deviceType):
        return furnacezone.extendededitoritem.FurnaceZoneExtendedEditorItem()


class FurnaceZoneGraphEditorContributionFactory(object):
    __module__ = __name__

    def getInstance(self, deviceType):
        return furnacezone.graphitem.FurnaceZoneGraphItem()


class FurnaceZoneColumnContributionFactory(object):
    __module__ = __name__

    def getInstance(self, deviceType):
        return furnacezone.column.FurnaceZoneColumn()


class FurnaceZoneDeviceFactory(object):
    __module__ = __name__

    def __init__(self):
        pass

    def getInstance(self):
        return furnacezone.device.FurnaceZoneDevice()

    def getTypeString(self):
        global DEVICE_ID
        return DEVICE_ID

    def getDescription(self):
        return 'Furnace Zone'

    def getImage(self):
        return None
        return

    def getSmallImage(self):
        return images.getImage(images.SMALL_ICON)
