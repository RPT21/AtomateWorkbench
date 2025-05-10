# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/mfc/src/mfc/__init__.py
# Compiled at: 2004-10-29 21:12:52
import plugins.ui.ui as ui, lib.kernel.plugin, plugins.core.core.deviceregistry
import plugins.extendededitor.extendededitor, plugins.panelview.panelview.devicemediator, plugins.executionengine.executionengine
import plugins.grideditor.grideditor, plugins.grapheditor.grapheditor, plugins.mfc.mfc.images as images
import logging

import plugins.panelview.panelview as panelview
import plugins.core.core as core
import plugins.grideditor.grideditor as grideditor
import plugins.grapheditor.grapheditor as grapheditor
import plugins.extendededitor.extendededitor as extendededitor
import plugins.labbooks.labbooks as labbooks
import plugins.graphview.graphview as graphview
from . import device, panelviewitem, participant, validation, hardwarestatusprovider, images, column, graphitem, extendededitoritem

from  plugins.mfc.mfc.execgraphitem import graphViewFactory
logger = logging.getLogger('mfc')

class MFCDevicePlugin(lib.kernel.plugin.Plugin):
    __module__ = __name__

    def __init__(self):
        lib.kernel.plugin.Plugin.__init__(self)
        plugins.ui.ui.getDefault().setSplashText('Loading Mass Flow Controller plugin ...')

    def startup(self, contextBundle):
        logger.debug("Registering '%s' as device" % device.DEVICE_ID)
        images.init(contextBundle)
        messages.init(contextBundle)
        panelview.devicemediator.registerItemContributionFactory(plugins.mfc.mfc.device.DEVICE_ID, MFCPanelViewContributionFactory())
        core.deviceregistry.addDeviceFactory(plugins.mfc.mfc.device.DEVICE_ID, MFCDeviceFactory())
        grideditor.addColumnContributionFactory(plugins.mfc.mfc.device.DEVICE_ID, MFCColumnContributionFactory())
        grapheditor.addGraphContributionFactory(plugins.mfc.mfc.device.DEVICE_ID, MFCGraphEditorContributionFactory())
        extendededitor.addContributionFactory(plugins.mfc.mfc.device.DEVICE_ID, MFCExtendedEditorContributionFactory())

    validation.init()
    graphview.getDefault().registerViewFactory(device.DEVICE_ID, graphViewFactory)
    plugins.labbooks.labbooks.getDefault().registerDeviceParticipant(participant.MFCRunLogParticipant())


class MFCPanelViewContributionFactory(object):
    __module__ = __name__

    def getInstance(self, deviceType):
        return plugins.mfc.mfc.panelviewitem.MFCPanelViewItem()


class MFCExtendedEditorContributionFactory(object):
    __module__ = __name__

    def getInstance(self, deviceType):
        return plugins.mfc.mfc.extendededitoritem.MFCExtendedEditorItem()


class MFCGraphEditorContributionFactory(object):
    __module__ = __name__

    def getInstance(self, deviceType):
        return plugins.mfc.mfc.graphitem.MFCGraphItem()


class MFCColumnContributionFactory(object):
    __module__ = __name__

    def getInstance(self, deviceType):
        return plugins.mfc.mfc.column.MFCColumn()


class MFCDeviceFactory(object):
    __module__ = __name__

    def __init__(self):
        pass

    def getInstance(self):
        return plugins.mfc.mfc.device.MFCDevice()

    def getTypeString(self):
        return 'mfc'

    def getDescription(self):
        return 'Mass Flow Controller'

    def getImage(self):
        return None

    def getSmallImage(self):
        return images.getImage(images.SMALL_ICON)
