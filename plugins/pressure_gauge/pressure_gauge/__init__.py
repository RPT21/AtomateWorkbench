# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/pressure_gauge/src/pressure_gauge/__init__.py
# Compiled at: 2004-12-07 10:29:40
import lib.kernel.plugin, plugins.core.core.deviceregistry
import plugins.pressure_gauge.pressure_gauge.device as pressure_gauge_device
import plugins.pressure_gauge.pressure_gauge.panelviewitem as pressure_gauge_panelviewitem
import plugins.pressure_gauge.pressure_gauge.participant as pressure_gauge_participant
import plugins.pressure_gauge.pressure_gauge.images as images
import plugins.pressure_gauge.pressure_gauge.messages as messages
import plugins.pressure_gauge.pressure_gauge.hardwarestatusprovider
import plugins.pressure_gauge.pressure_gauge.execgraphitem, logging
import plugins.labbooks.labbooks as labbooks
import lib.kernel as kernel
import plugins.ui.ui as ui
import plugins.core.core as core
import plugins.panelview.panelview as panelview
import plugins.panelview.panelview.devicemediator

logger = logging.getLogger('pressure_gauge')

class PressureGaugeDevicePlugin(kernel.plugin.Plugin):
    __module__ = __name__

    def __init__(self):
        kernel.plugin.Plugin.__init__(self)
        ui.getDefault().setSplashText('Loading Pressure Gauge Controller plugin ...')

    def startup(self, contextBundle):
        logger.debug("Registering '%s' as device" % pressure_gauge_device.DEVICE_ID)
        images.init(contextBundle)
        messages.init(contextBundle)
        panelview.devicemediator.registerItemContributionFactory(pressure_gauge_device.DEVICE_ID, PressureGaugePanelViewContributionFactory())
        core.deviceregistry.addDeviceFactory(pressure_gauge_device.DEVICE_ID, PressureGaugeDeviceFactory())

    labbooks.getDefault().registerDeviceParticipant(pressure_gauge_participant.PressureGaugeRunLogParticipant())


class PressureGaugePanelViewContributionFactory(object):
    __module__ = __name__

    def getInstance(self, deviceType):
        return pressure_gauge_panelviewitem.PressureGaugePanelViewItem()


class PressureGaugeDeviceFactory(object):
    __module__ = __name__

    def __init__(self):
        pass

    def getInstance(self):
        return pressure_gauge_device.PressureGaugeDevice()

    def getTypeString(self):
        return 'pressure_gauge'

    def getDescription(self):
        return 'Pressure Gauge'

    def getImage(self):
        return None

    def getSmallImage(self):
        return images.getImage(images.SMALL_ICON)
