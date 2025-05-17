# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/furnacezone/src/furnacezone/__init__.py
# Compiled at: 2004-10-08 00:47:25
DEVICE_ID = 'furnacezone'
import plugins.ui.ui as ui, lib.kernel.plugin , plugins.core.core.deviceregistry, lib.kernel as kernel
import plugins.furnacezone.furnacezone.execgraphitem as furnacezone_execgraphitem
import plugins.furnacezone.furnacezone.device as furnacezone_device
import plugins.furnacezone.furnacezone.column as furnacezone_column
import plugins.furnacezone.furnacezone.graphitem as furnacezone_graphitem
import plugins.furnacezone.furnacezone.extendededitoritem as furnacezone_extendededitoritem
import plugins.furnacezone.furnacezone.participant as furnacezone_participant
import plugins.furnacezone.furnacezone.images as images
import plugins.furnacezone.furnacezone.messages as messages
import plugins.furnacezone.furnacezone.panelviewitem as furnacezone_panelviewitem
import plugins.panelview.panelview.devicemediator, logging
import plugins.furnacezone.furnacezone.validation as furnacezone_validation
import plugins.furnacezone.furnacezone.executiongridviewcolumn
import plugins.core.core as core
import plugins.grideditor.grideditor as grideditor
import plugins.panelview.panelview as panelview
import plugins.grapheditor.grapheditor as grapheditor
import plugins.extendededitor.extendededitor as extendededitor
import plugins.labbooks.labbooks as labbooks
import plugins.graphview.graphview as graphview

logger = logging.getLogger('furnacezone')

class FurnaceZoneDevicePlugin(kernel.plugin.Plugin):
    __module__ = __name__

    def __init__(self):
        lib.kernel.plugin.Plugin.__init__(self)
        ui.getDefault().setSplashText('Loading Furnace Zone plugin ...')

    def startup(self, contextBundle):
        logger.debug("Registering '%s' as device" % furnacezone_device.DEVICE_ID)
        images.init(contextBundle)
        messages.init(contextBundle)
        panelview.devicemediator.registerItemContributionFactory(furnacezone_device.DEVICE_ID, FurnacePanelViewContributionFactory())
        core.deviceregistry.addDeviceFactory(furnacezone_device.DEVICE_ID, FurnaceZoneDeviceFactory())
        grideditor.addColumnContributionFactory(furnacezone_device.DEVICE_ID, FurnaceZoneColumnContributionFactory())
        grapheditor.addGraphContributionFactory(furnacezone_device.DEVICE_ID, FurnaceZoneGraphEditorContributionFactory())
        extendededitor.addContributionFactory(furnacezone_device.DEVICE_ID, FurnaceZoneExtendedEditorContributionFactory())
        labbooks.getDefault().registerDeviceParticipant(furnacezone_participant.FurnaceZoneRunLogParticipant())
        graphview.getDefault().registerViewFactory(furnacezone_device.DEVICE_ID, furnacezone_execgraphitem.graphViewFactory)
        furnacezone_validation.init()


class FurnacePanelViewContributionFactory(object):
    __module__ = __name__

    def getInstance(self, deviceType):
        return furnacezone_panelviewitem.FurnaceZonePanelViewItem()


class FurnaceZoneExtendedEditorContributionFactory(object):
    __module__ = __name__

    def getInstance(self, deviceType):
        return furnacezone_extendededitoritem.FurnaceZoneExtendedEditorItem()


class FurnaceZoneGraphEditorContributionFactory(object):
    __module__ = __name__

    def getInstance(self, deviceType):
        return furnacezone_graphitem.FurnaceZoneGraphItem()


class FurnaceZoneColumnContributionFactory(object):
    __module__ = __name__

    def getInstance(self, deviceType):
        return furnacezone_column.FurnaceZoneColumn()


class FurnaceZoneDeviceFactory(object):
    __module__ = __name__

    def __init__(self):
        pass

    def getInstance(self):
        return furnacezone_device.FurnaceZoneDevice()

    def getTypeString(self):
        global DEVICE_ID
        return DEVICE_ID

    def getDescription(self):
        return 'Furnace Zone'

    def getImage(self):
        return None

    def getSmallImage(self):
        return images.getImage(images.SMALL_ICON)
