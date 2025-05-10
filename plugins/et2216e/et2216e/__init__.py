# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/et2216e/src/et2216e/__init__.py
# Compiled at: 2005-01-13 01:21:46
import time, string, kernel.plugin, et2216e.et2216etype, et2216e.images as images, et2216e.messages as messages, et2216e.drivers, et2216e.participant, et2216e.drivers.rs485driver, et2216e.drivers.ser, et2216e.drivers.simulation, hardware, core.deviceregistry
from hardware import ResponseTimeoutException
import hardware.hardwaremanager, executionengine, logging, threading, ui
from hardware.utils.threads import BackgroundProcessThread, PurgeThread
import furnacezone.hw
logger = logging.getLogger('et2216e')

class et2216ePlugin(kernel.plugin.Plugin):
    __module__ = __name__

    def __init__(self):
        kernel.plugin.Plugin.__init__(self)
        self.contextBundle = None
        ui.getDefault().setSplashText('Loading Eurotherm 2216e plugin ...')
        return

    def getContextBundle(self):
        return self.contextBundle

    def startup(self, contextBundle):
        self.contextBundle = contextBundle
        logger.debug('2216e Plugin startup sequence')
        images.init(contextBundle)
        messages.init(contextBundle)
        hwtype = et2216etype.et2216eHardwareType()
        hardware.hardwaremanager.registerHardwareType(hwtype)
        executionengine.getDefault().registerRecipeParticipantFactory(hwtype.getType(), et2216e.participant.RecipeParticipantFactory())


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
                except Exception, msg:
                    self.paused = True
                    logger.exception(msg)

            self.lock.release()

    def askHardware(self):
        inst = self.hwinst
        if inst.getStatus() == hardware.hardwaremanager.STATUS_RUNNING or inst.getStatus() == hardware.hardwaremanager.STATUS_PURGING:
            pass
        else:
            return
        inst.getTemperature()


class et2216ePurgeThread(PurgeThread):
    __module__ = __name__

    def __init__(self, hwinst):
        PurgeThread.__init__(self, hwinst)
        self.starttime = 0
        self.setpoint = 0
        self.duration = 0

    def getDescription(self):
        return self.hwinst.getDescription().getName()

    def purgestart(self):
        self.starttime = time.time()
        try:
            logger.debug('Setting purge setpoint %d for %d seconds' % (self.setpoint, self.duration))
            self.hwinst.setSetpoint(self.setpoint)
        except Exception, msg:
            logger.exception(msg)
            logger.debug('Unable to start purging: %s' % msg)
            self.stop()

    def setPurgeSetpoint(self, setpoint, duration):
        self.setpoint = setpoint
        self.duration = duration

    def purgestop(self):
        try:
            self.hwinst.setSetpoint(0)
            self.setpoint = 0
            self.duration = 0
            self.done = True
        except Exception, msg:
            logger.exception(msg)

    def tick(self):
        now = time.time()
        delta = now - self.starttime
        self.hwinst.getTemperature()
        if delta > self.duration:
            try:
                self.hwinst.setSetpoint(0)
            except Exception, msg:
                logger.exception(msg)
            else:
                self.purgestop()
                return


class et2216eHardware(hardware.hardwaremanager.Hardware, furnacezone.hw.HardwareStatusProvider):
    __module__ = __name__

    def __init__(self):
        hardware.hardwaremanager.Hardware.__init__(self)
        furnacezone.hw.HardwareStatusProvider.__init__(self)
        self.logger = logger
        self.setpoint = None
        self.statusThread = StatusThread(self)
        self.statusThread.start()
        return

    def createDefaultDevices(self):
        factory = core.deviceregistry.getDeviceFactory('furnacezone')
        device = factory.getInstance()
        hwhints = device.getHardwareHints()
        hwhints.createChildIfNotExists('id').setValue(self.getDescription().getName())
        uihints = device.getUIHints()
        uihints.createChildIfNotExists('label').setValue(self.getDescription().getName())
        try:
            conf = self.getDescription().getConfiguration()
            if conf.has_section('default.device.props'):
                uihints.createChildIfNotExists('plot-color').setValue(conf.get('default.device.props', 'plot.color'))
                hwhints.createChildIfNotExists('range').setValue(conf.get('default.device.props', 'range'))
        except Exception, msg:
            logger.exception(msg)

        return [
         device]

    def parsePIDString(self, val):
        return tuple(map(int, val.split(',')))

    def formatPIDSettings(self, pid):
        return string.join(map(str, pid), ',')

    def getPIDSettings(self):
        desc = self.getDescription()
        if self.getDescription() is None:
            return None
        conf = self.getDescription().getConfiguration()
        try:
            return map(int, conf.get('main', 'pid').split(','))
        except Exception, msg:
            logger.exception(msg)

        return None
        return

    def setPIDSettings(self, pid):
        if self.getDescription() is None:
            raise Exception('Not configured')
        conf = self.getDescription().getConfiguration()
        val = ''
        if pid is not None:
            val = self.formatPIDSettings(pid)
        try:
            conf.set('main', 'pid', val)
        except Exception, msg:
            logger.exception(msg)
            raise

        return

    def dispose(self):
        hardware.hardwaremanager.Hardware.dispose(self)
        self.statusThread.stop()

    def resumeStatusThread(self):
        logger.debug('resuming the dang status thread.  where is it at?')
        self.statusThread.resume()

    def stopStatusThread(self):
        logger.debug('pausing status thread.  dang.')
        self.statusThread.pause()

    def getID(self):
        self.checkDriver()
        try:
            return self.driver.getID()
        except ResponseTimeoutException, msg:
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

    def setSetpoint(self, setpoint):
        self.checkDriver()
        try:
            self.driver.setSetpoint(setpoint)
            self.setpoint = setpoint
        except ResponseTimeoutException, msg:
            self.cleanup()
            raise

    def getSetpoint(self):
        return self.setpoint

    def getTemperature(self, timeout=1):
        self.checkDriver()
        try:
            temperature = self.driver.getTemperature()
            self.statusGetTemperature(temperature)
        except ResponseTimeoutException, msg:
            self.cleanup()
            raise

        return temperature

    def isConfigured(self):
        if self.driver is None:
            return False
        if not self.driver.isConfigured():
            return False
        return True
        return

    def setupDriver(self, description):
        self.driver = None
        config = description.getConfiguration()
        try:
            driverType = config.get('driver', 'type')
            inst = et2216e.drivers.getDriver(driverType)(self)
            self.setDriver(inst)
            self.driver.setConfiguration(config)
        except Exception, msg:
            self.driver = None
            self.logger.exception(msg)
            self.logger.error("Cannot setup driver : '%s'" % msg)
            self.fireHardwareEvent(hardware.hardwaremanager.HardwareEvent(self, hardware.hardwaremanager.EVENT_ERROR, "Error, cannot setup driver:'%s'" % msg))
        except Error, msg:
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
        except Exception, msg:
            self.logger.exception(msg)
            self.logger.error("Cannot initialize '%s'" % msg)
            self.fireHardwareEvent(hardware.hardwaremanager.HardwareEvent(self, hardware.hardwaremanager.EVENT_ERROR, "Error cannot initialize'%s'" % msg))
            raise Exception(msg)

        self.status = hardware.hardwaremanager.STATUS_RUNNING
        self.fireHardwareStatusChanged()
        self.fireStatusIsRunning()

    def shutdown(self):
        if self.driver is None:
            return
        try:
            self.driver.shutdown()
        except Exception, msg:
            logger.error("Cannot initialize '%s'" % msg)
            self.fireHardwareEvent(hardware.hardwaremanager.HardwareEvent(self, hardware.hardwareevent.EVENT_ERROR, "Error cannot initialize'%s'" % msg))
            raise Exception(msg)

        self.status = hardware.hardwaremanager.STATUS_STOPPED
        self.fireHardwareStatusChanged()
        self.fireStatusIsStopped()
        return

    def startPurge(self, setpoint, duration):
        self.purgeThread = et2216ePurgeThread(self)
        self.purgeThread.setPurgeSetpoint(setpoint, duration)
        self.purgeThread.start()
        self.status = hardware.hardwaremanager.STATUS_PURGING
        self.fireHardwareStatusChanged()
        self.fireStatusIsPurging()

    def finishedPurge(self):
        try:
            self.driver.deactivate()
        except Exception, msg:
            logger.exception(msg)

        self.status = hardware.hardwaremanager.STATUS_RUNNING
        self.fireHardwareStatusChanged()
        self.fireStatusIsRunning()
        self.resumeStatusThread()

    def interruptPurge(self):
        self.purgeThread.stop()
        self.status = hardware.hardwaremanager.STATUS_RUNNING
        self.fireHardwareStatusChanged()
        self.fireStatusIsRunning()
