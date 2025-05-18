# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/mfc/src/mfc/__init__.py
# Compiled at: 2004-10-29 21:12:52
import plugins.ui.ui as ui, lib.kernel.plugin, plugins.core.core.deviceregistry, lib.kernel as kernel
import plugins.panelview.panelview.devicemediator
import plugins.panelview.panelview as panelview
import plugins.core.core as core
import plugins.grideditor.grideditor as grideditor
import plugins.grapheditor.grapheditor as grapheditor
import plugins.extendededitor.extendededitor as extendededitor
import plugins.graphview.graphview as graphview
import plugins.mfc.mfc.device as mfc_device
import plugins.mfc.mfc.panelviewitem as mfc_panelviewitem
import plugins.mfc.mfc.participant as mfc_participant
import plugins.mfc.mfc.validation as validation
import plugins.mfc.mfc.hardwarestatusprovider as mfc_hardwarestatusprovider
import plugins.mfc.mfc.images as images
import plugins.mfc.mfc.column as mfc_column
import plugins.mfc.mfc.graphitem as mfc_graphitem
import plugins.mfc.mfc.extendededitoritem as mfc_extendededitoritem
import plugins.mfc.mfc.messages as messages
import plugins.mfc.mfc.execgraphitem as mfc_execgraphitem
import plugins.labbooks.labbooks as labbooks
import logging

logger = logging.getLogger('mfc')

class MFCDevicePlugin(kernel.plugin.Plugin):
    __module__ = __name__

    def __init__(self):
        kernel.plugin.Plugin.__init__(self)
        ui.getDefault().setSplashText('Loading Mass Flow Controller plugin ...')

    def startup(self, contextBundle):
        logger.debug("Registering '%s' as device" % mfc_device.DEVICE_ID)
        images.init(contextBundle)
        messages.init(contextBundle)
        panelview.devicemediator.registerItemContributionFactory(mfc_device.DEVICE_ID, MFCPanelViewContributionFactory())
        core.deviceregistry.addDeviceFactory(mfc_device.DEVICE_ID, MFCDeviceFactory())
        grideditor.addColumnContributionFactory(mfc_device.DEVICE_ID, MFCColumnContributionFactory())
        grapheditor.addGraphContributionFactory(mfc_device.DEVICE_ID, MFCGraphEditorContributionFactory())
        extendededitor.addContributionFactory(mfc_device.DEVICE_ID, MFCExtendedEditorContributionFactory())

    validation.init()
    graphview.getDefault().registerViewFactory(mfc_device.DEVICE_ID, mfc_execgraphitem.graphViewFactory)
    labbooks.getDefault().registerDeviceParticipant(mfc_participant.MFCRunLogParticipant())


class MFCPanelViewContributionFactory(object):
    __module__ = __name__

    def getInstance(self, deviceType):
        return mfc_panelviewitem.MFCPanelViewItem()


class MFCExtendedEditorContributionFactory(object):
    __module__ = __name__

    def getInstance(self, deviceType):
        return mfc_extendededitoritem.MFCExtendedEditorItem()


class MFCGraphEditorContributionFactory(object):
    __module__ = __name__

    def getInstance(self, deviceType):
        return mfc_graphitem.MFCGraphItem()


class MFCColumnContributionFactory(object):
    __module__ = __name__

    def getInstance(self, deviceType):
        return mfc_column.MFCColumn()


class MFCDeviceFactory(object):
    __module__ = __name__

    def __init__(self):
        pass

    def getInstance(self):
        return mfc_device.MFCDevice()

    def getTypeString(self):
        return 'mfc'

    def getDescription(self):
        return 'Mass Flow Controller'

    def getImage(self):
        return None

    def getSmallImage(self):
        return images.getImage(images.SMALL_ICON)
