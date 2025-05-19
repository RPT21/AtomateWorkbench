# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/up150/src/up150/__init__.py
# Compiled at: 2004-11-19 01:56:28
import os, shutil, plugins.core.core.error, time, lib.kernel.plugin
import plugins.up150.up150.images as images, plugins.up150.up150.messages as messages
import plugins.up150.up150.drivers as up150_drivers
import plugins.up150.up150.participant as up150_participant
import plugins.up150.up150.drivers.rs485driver, plugins.up150.up150.drivers.simulation
import plugins.hardware.hardware as hardware
from plugins.hardware.hardware import ResponseTimeoutException
import plugins.hardware.hardware.hardwaremanager, logging
import plugins.up150.up150.up150type as up150type
import plugins.ui.ui as ui, lib.kernel as kernel
from plugins.hardware.hardware.utils.threads import BackgroundProcessThread, PurgeThread
import plugins.core.core.deviceregistry, plugins.furnacezone.furnacezone.hw
import plugins.executionengine.executionengine as executionengine
import plugins.up150.up150.up150node
import plugins.core.core as core
import plugins.furnacezone.furnacezone as furnacezone

logger = logging.getLogger('up150')

def getDefault():
    global instance
    return instance


class UP150Plugin(kernel.plugin.Plugin):
    __module__ = __name__

    def __init__(self):
        global instance
        kernel.plugin.Plugin.__init__(self)
        self.contextBundle = None
        ui.getDefault().setSplashText('Loading UP 150 plugin ...')
        instance = self
        return

    def getContextBundle(self):
        return self.contextBundle

    def startup(self, contextBundle):
        self.contextBundle = contextBundle
        logger.debug('UP150 Plugin startup sequence')
        images.init(contextBundle)
        messages.init(contextBundle)
        hwtype = up150type.UP150HardwareType()
        hardware.hardwaremanager.registerHardwareType(hwtype)
        executionengine.getDefault().registerRecipeParticipantFactory(hwtype.getType(), up150_participant.RecipeParticipantFactory())


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
        inst.getTemperature()


def createDefaultHardwareNode(root, num, units, range, gcf):
    root.createChildIfNotExists('channel').setValue(str(num))
    root.createChildIfNotExists('units').setValue(units)
    root.createChildIfNotExists('range').setValue(str(range))
    root.createChildIfNotExists('conversion-factor').setValue(str(gcf))


class UP150PurgeThread(PurgeThread):
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
        except Exception as msg:
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
        except Exception as msg:
            logger.exception(msg)

    def tick(self):
        now = time.time()
        delta = now - self.starttime
        self.hwinst.getTemperature()
        if delta > self.duration:
            try:
                self.hwinst.setSetpoint(0)
            except Exception as msg:
                logger.exception(msg)
            else:
                self.purgestop()
                return


DEFAULT_PROPS_FILENAME = 'default.devices.props'

class UP150Hardware(hardware.hardwaremanager.Hardware, furnacezone.hw.HardwareStatusProvider):
    __module__ = __name__

    def __init__(self):
        hardware.hardwaremanager.Hardware.__init__(self)
        furnacezone.hw.HardwareStatusProvider.__init__(self)
        self.logger = logger
        self.setpoint = None
        self.statusThread = StatusThread(self)
        self.statusThread.start()
        return

    def createDefaultDeviceProperties(self, path):
        dfp = os.path.join(getDefault().getContextBundle().dirname, DEFAULT_PROPS_FILENAME)
        self.logger.debug("Acquiring default device properties at '%s'" % dfp)
        if os.path.exists(dfp) and os.path.isfile(dfp):
            shutil.copyfile(dfp, path)
            return

    def createDefaultDevices(self):
        """Creates one furnace zone device"""
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
        except Exception as msg:
            logger.exception(msg)

        return [
         device]

    def parsePIDString(self, val):
        return tuple(map(int, val.split(',')))

    def formatPIDSettings(self, pid):
        return ','.join(map(str, pid))

    def getPIDSettings(self):
        desc = self.getDescription()
        if self.getDescription() is None:
            return None
        conf = self.getDescription().getConfiguration()
        try:
            return list(map(int, conf.get('main', 'pid').split(',')))
        except Exception as msg:
            logger.exception(msg)

        return None

    def setPIDSettings(self, pid):
        if self.getDescription() is None:
            raise Exception('Not configured')
        conf = self.getDescription().getConfiguration()
        val = ''
        if pid is not None:
            val = self.formatPIDSettings(pid)
        try:
            conf.set('main', 'pid', val)
        except Exception as msg:
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

    def setSetpoint(self, setpoint):
        self.checkDriver()
        try:
            self.driver.setSetpoint(setpoint)
            self.setpoint = setpoint
        except ResponseTimeoutException as msg:
            self.cleanup()
            raise

    def getSetpoint(self):
        return self.setpoint

    def getTemperature(self, timeout=1):
        self.checkDriver()
        try:
            temperature = self.driver.getTemperature(timeout)
            self.statusGetTemperature(temperature)
        except ResponseTimeoutException as msg:
            self.cleanup()
            raise

        return temperature

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
            inst = up150_drivers.getDriver(driverType)(self)
            self.setDriver(inst)
            self.driver.setConfiguration(config)
        except Exception as msg:
            self.driver = None
            self.logger.exception(msg)
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
            import traceback
            traceback.print_exc()
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

    def startPurge(self, setpoint, duration):
        self.purgeThread = UP150PurgeThread(self)
        self.purgeThread.setPurgeSetpoint(setpoint, duration)
        self.purgeThread.start()
        self.status = hardware.hardwaremanager.STATUS_PURGING
        self.fireHardwareStatusChanged()
        self.fireStatusIsPurging()

    def finishedPurge(self):
        try:
            self.driver.deactivate()
        except Exception as msg:
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
