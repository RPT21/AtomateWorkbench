# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/furnacezone/src/furnacezone/__init__.py
# Compiled at: 2004-10-08 00:47:25
DEVICE_ID = 'furnacezone'
import plugins.ui.ui, lib.kernel.plugin, plugins.core.core.deviceregistry, plugins.executionengine.executionengine
import plugins.furnacezone.furnacezone.execgraphitem, plugins.furnacezone.furnacezone.device
import plugins.furnacezone.furnacezone.column, plugins.furnacezone.furnacezone.graphitem, plugins.furnacezone.furnacezone.extendededitoritem
import plugins.furnacezone.furnacezone.participant, plugins.extendededitor.extendededitor, plugins.grideditor.grideditor
import plugins.labbooks.labbooks, plugins.grapheditor.grapheditor, plugins.graphview.graphview, plugins.furnacezone.furnacezone.images as images
import plugins.furnacezone.furnacezone.messages as messages, plugins.furnacezone.furnacezone.panelviewitem
import plugins.panelview.panelview.devicemediator, logging, plugins.furnacezone.furnacezone.validation, plugins.furnacezone.furnacezone.executiongridviewcolumn
logger = logging.getLogger('furnacezone')

class FurnaceZoneDevicePlugin(lib.kernel.plugin.Plugin):
    __module__ = __name__

    def __init__(self):
        lib.kernel.plugin.Plugin.__init__(self)
        plugins.ui.ui.getDefault().setSplashText('Loading Furnace Zone plugin ...')

    def startup(self, contextBundle):
        logger.debug("Registering '%s' as device" % plugins.furnacezone.furnacezone.device.DEVICE_ID)
        images.init(contextBundle)
        messages.init(contextBundle)
        plugins.panelview.panelview.devicemediator.registerItemContributionFactory(plugins.furnacezone.furnacezone.device.DEVICE_ID, FurnacePanelViewContributionFactory())
        plugins.core.core.deviceregistry.addDeviceFactory(plugins.furnacezone.furnacezone.device.DEVICE_ID, FurnaceZoneDeviceFactory())
        plugins.grideditor.grideditor.addColumnContributionFactory(plugins.furnacezone.furnacezone.device.DEVICE_ID, FurnaceZoneColumnContributionFactory())
        plugins.grapheditor.grapheditor.addGraphContributionFactory(plugins.furnacezone.furnacezone.device.DEVICE_ID, FurnaceZoneGraphEditorContributionFactory())
        plugins.extendededitor.extendededitor.addContributionFactory(plugins.furnacezone.furnacezone.device.DEVICE_ID, FurnaceZoneExtendedEditorContributionFactory())
        plugins.labbooks.labbooks.getDefault().registerDeviceParticipant(plugins.furnacezone.furnacezone.participant.FurnaceZoneRunLogParticipant())
        plugins.graphview.graphview.getDefault().registerViewFactory(plugins.furnacezone.furnacezone.device.DEVICE_ID, plugins.furnacezone.furnacezone.execgraphitem.graphViewFactory)
        plugins.furnacezone.furnacezone.validation.init()


class FurnacePanelViewContributionFactory(object):
    __module__ = __name__

    def getInstance(self, deviceType):
        return plugins.furnacezone.furnacezone.panelviewitem.FurnaceZonePanelViewItem()


class FurnaceZoneExtendedEditorContributionFactory(object):
    __module__ = __name__

    def getInstance(self, deviceType):
        return plugins.furnacezone.furnacezone.extendededitoritem.FurnaceZoneExtendedEditorItem()


class FurnaceZoneGraphEditorContributionFactory(object):
    __module__ = __name__

    def getInstance(self, deviceType):
        return plugins.furnacezone.furnacezone.graphitem.FurnaceZoneGraphItem()


class FurnaceZoneColumnContributionFactory(object):
    __module__ = __name__

    def getInstance(self, deviceType):
        return plugins.furnacezone.furnacezone.column.FurnaceZoneColumn()


class FurnaceZoneDeviceFactory(object):
    __module__ = __name__

    def __init__(self):
        pass

    def getInstance(self):
        return plugins.furnacezone.furnacezone.device.FurnaceZoneDevice()

    def getTypeString(self):
        global DEVICE_ID
        return DEVICE_ID

    def getDescription(self):
        return 'Furnace Zone'

    def getImage(self):
        return None

    def getSmallImage(self):
        return images.getImage(images.SMALL_ICON)
