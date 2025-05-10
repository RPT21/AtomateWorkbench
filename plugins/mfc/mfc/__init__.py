# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/mfc/src/mfc/__init__.py
# Compiled at: 2004-10-29 21:12:52
import ui, kernel.plugin, core.deviceregistry, panelview, executionengine, mfc.device, mfc.column, mfc.graphitem, mfc.extendededitoritem, mfc.panelviewitem, mfc.participant, extendededitor, grideditor, grapheditor, mfc.images as images, mfc.messages as messages, mfc.validation, mfc.hardwarestatusprovider, mfc.executiongridviewcolumn, mfc.execgraphitem, graphview, labbooks, logging
logger = logging.getLogger('mfc')

class MFCDevicePlugin(kernel.plugin.Plugin):
    __module__ = __name__

    def __init__(self):
        kernel.plugin.Plugin.__init__(self)
        ui.getDefault().setSplashText('Loading Mass Flow Controller plugin ...')

    def startup(self, contextBundle):
        logger.debug("Registering '%s' as device" % mfc.device.DEVICE_ID)
        images.init(contextBundle)
        messages.init(contextBundle)
        panelview.devicemediator.registerItemContributionFactory(mfc.device.DEVICE_ID, MFCPanelViewContributionFactory())
        core.deviceregistry.addDeviceFactory(mfc.device.DEVICE_ID, MFCDeviceFactory())
        grideditor.addColumnContributionFactory(mfc.device.DEVICE_ID, MFCColumnContributionFactory())
        grapheditor.addGraphContributionFactory(mfc.device.DEVICE_ID, MFCGraphEditorContributionFactory())
        extendededitor.addContributionFactory(mfc.device.DEVICE_ID, MFCExtendedEditorContributionFactory())

    mfc.validation.init()
    graphview.getDefault().registerViewFactory(mfc.device.DEVICE_ID, mfc.execgraphitem.graphViewFactory)
    labbooks.getDefault().registerDeviceParticipant(mfc.participant.MFCRunLogParticipant())


class MFCPanelViewContributionFactory(object):
    __module__ = __name__

    def getInstance(self, deviceType):
        return mfc.panelviewitem.MFCPanelViewItem()


class MFCExtendedEditorContributionFactory(object):
    __module__ = __name__

    def getInstance(self, deviceType):
        return mfc.extendededitoritem.MFCExtendedEditorItem()


class MFCGraphEditorContributionFactory(object):
    __module__ = __name__

    def getInstance(self, deviceType):
        return mfc.graphitem.MFCGraphItem()


class MFCColumnContributionFactory(object):
    __module__ = __name__

    def getInstance(self, deviceType):
        return mfc.column.MFCColumn()


class MFCDeviceFactory(object):
    __module__ = __name__

    def __init__(self):
        pass

    def getInstance(self):
        return mfc.device.MFCDevice()

    def getTypeString(self):
        return 'mfc'

    def getDescription(self):
        return 'Mass Flow Controller'

    def getImage(self):
        return None
        return

    def getSmallImage(self):
        return images.getImage(images.SMALL_ICON)
