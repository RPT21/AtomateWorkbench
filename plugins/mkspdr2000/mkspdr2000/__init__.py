# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/mkspdr2000/src/mkspdr2000/__init__.py
# Compiled at: 2004-12-09 00:49:30
import core.error, time, string, kernel.plugin, mkspdr2000.mkspdr2000type, mkspdr2000.images as images, mkspdr2000.messages as messages, mkspdr2000.drivers, mkspdr2000.participant, mkspdr2000.drivers.ser, mkspdr2000.drivers.simulation, hardware
from hardware import ResponseTimeoutException
import hardware.hardwaremanager, executionengine, logging, threading
from hardware.utils.threads import BackgroundProcessThread, PurgeThread
from . import mkspdr2000type, mkspdr2000node
import core.deviceregistry, pressure_gauge.hardwarestatusprovider
import plugins.ui.ui as ui
import plugins.executionengine.executionengine as executionengine
logger = logging.getLogger('mkspdr2000')

class MKSPDR2000Plugin(kernel.plugin.Plugin):
    __module__ = __name__

    def __init__(self):
        kernel.plugin.Plugin.__init__(self)
        self.contextBundle = None
        ui.getDefault().setSplashText('Loading MKS PDR 2000 plugin ...')
        return

    def getContextBundle(self):
        return self.contextBundle

    def startup(self, contextBundle):
        self.contextBundle = contextBundle
        logger.debug('mkspdr2000 Plugin startup sequence')
        images.init(contextBundle)
        messages.init(contextBundle)
        hwtype = mkspdr2000type.mkspdr2000HardwareType()
        hardware.hardwaremanager.registerHardwareType(hwtype)
        executionengine.getDefault().registerRecipeParticipantFactory(hwtype.getType(), mkspdr2000.participant.RecipeParticipantFactory())


class StatusThread(BackgroundProcessThread):
    __module__ = __name__

    def __init__(self, hwinst):
        BackgroundProcessThread.__init__(self, hwinst)
        self.throttle = 0.5

    def run(self):
        while not self.done:
            self.lock.acquire()
            self.lock.wait(self.throttle)
            if not self.paused:
                try:
                    self.askHardware()
                except Exception as msg:
                    self.paused = True
                    logger.exception(msg)

            self.lock.release()

    def askHardware(self):
        inst = self.hwinst
        if inst.getStatus() == hardware.hardwaremanager.STATUS_RUNNING or inst.getStatus() == hardware.hardwaremanager.STATUS_PURGING:
            pass
        else:
            return
        inst.getPressure()


def createDefaultHardwareNode(root, num, units, range, gcf):
    pass


class mkspdr2000Hardware(hardware.hardwaremanager.Hardware, pressure_gauge.hardwarestatusprovider.HardwareStatusProvider):
    __module__ = __name__

    def __init__(self):
        hardware.hardwaremanager.Hardware.__init__(self)
        pressure_gauge.hardwarestatusprovider.HardwareStatusProvider.__init__(self)
        self.logger = logger
        self.setpoint = None
        self.statusThread = StatusThread(self)
        self.statusThread.start()
        return

    def createDefaultDevices(self):
        factory = core.deviceregistry.getDeviceFactory('pressure_gauge')
        device = factory.getInstance()
        hwhints = device.getHardwareHints()
        hwhints.createChildIfNotExists('id').setValue(self.getDescription().getName())
        uihints = device.getUIHints()
        uihints.createChildIfNotExists('label').setValue(self.getDescription().getName())
        return [
         device]

    def dispose(self):
        hardware.hardwaremanager.Hardware.dispose(self)
        self.statusThread.stop()

    def resumeStatusThread(self):
        self.statusThread.resume()

    def stopStatusThread(self):
        self.statusThread.pause()

    def getID(self):
        self.checkDriver()
        try:
            return self.driver.getID()
        except ResponseTimeoutException as msg:
            self.cleanup()
            raise

    def interruptOperation(self):
        if self.driver is None:
            return
        self.driver.interrupt()
        return

    def checkDriver(self):
        if self.driver is None:
            raise Exception('No driver set')
        return

    def activate(self):
        self.checkDriver()
        self.driver.activate()

    def deactivate(self):
        self.checkDriver()
        self.driver.deactivate()

    def getPressure(self, timeout=1):
        self.checkDriver()
        try:
            pressure = self.driver.getPressure()
            self.statusGetPressure(pressure)
        except ResponseTimeoutException as msg:
            self.cleanup()
            raise

        return pressure

    def isConfigured(self):
        if self.driver is None:
            return False
        if not self.driver.isConfigured():
            return False
        return True

    def getExtraData(self):
        if self.driver is None:
            return ''
        return self.driver.getDescription()

    def setupDriver(self, description):
        self.driver = None
        config = description.getConfiguration()
        try:
            driverType = config.get('driver', 'type')
            inst = mkspdr2000.drivers.getDriver(driverType)(self)
            self.setDriver(inst)
            self.driver.setConfiguration(config)
        except Exception as msg:
            self.driver = None
            self.logger.exception(msg)
            self.logger.error("Cannot setup driver : '%s'" % msg)
            self.fireHardwareEvent(hardware.hardwaremanager.HardwareEvent(self, hardware.hardwaremanager.EVENT_ERROR, "Error, cannot setup driver:'%s'" % msg))
        except Error as msg:
            self.driver = None
            self.logger.error("Cannot setup driver : '%s'" % msg)
            self.fireHardwareEvent(hardware.hardwaremanager.HardwareEvent(self, hardware.hardwaremanager.EVENT_ERROR, "Error, cannot setup driver:'%s'" % msg))

        return

    def setDriver(self, driver):
        self.driver = driver

    def initialize(self):
        logger.debug('Initialize')
        self.checkDriver()
        self.resumeStatusThread()
        try:
            self.driver.initialize()
        except Exception as msg:
            self.logger.exception(msg)
            self.logger.error("Cannot initialize '%s'" % msg)
            self.fireHardwareEvent(hardware.hardwaremanager.HardwareEvent(self, hardware.hardwaremanager.EVENT_ERROR, "Error cannot initialize'%s'" % msg))
            raise core.error.WorkbenchException('Unable to initialize %s - %s' % (self.getDescription().getName(), msg))

        self.status = hardware.hardwaremanager.STATUS_RUNNING
        self.fireHardwareStatusChanged()
        self.fireStatusIsRunning()

    def shutdown(self):
        if self.driver is None:
            return
        try:
            self.driver.shutdown()
        except Exception as msg:
            logger.error("Cannot initialize '%s'" % msg)
            self.fireHardwareEvent(hardware.hardwaremanager.HardwareEvent(self, hardware.hardwaremanager.EVENT_ERROR, "Error cannot initialize'%s'" % msg))
            raise Exception(msg)

        self.status = hardware.hardwaremanager.STATUS_STOPPED
        self.fireHardwareStatusChanged()
        self.fireStatusIsStopped()
        return
