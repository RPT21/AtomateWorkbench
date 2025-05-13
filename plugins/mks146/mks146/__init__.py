# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/mks146/src/mks146/__init__.py
# Compiled at: 2004-11-19 22:12:40
import os, shutil, core.error, core.deviceregistry, configparser, logging, kernel.plugin, kernel.pluginmanager as PluginManager, hardware.hardwaremanager
from hardware import ResponseTimeoutException
import mks146.mks146type, mks146.drivers, mks146.drivers.ser, mks146.participant, mfc.hardwarestatusprovider, poi.actions, threading
import plugins.ui.ui as ui
from . import mks146type, mks647bctype
from hardware.utils.threads import BackgroundProcessThread, PurgeThread
import plugins.executionengine.executionengine as executionengine
logger = logging.getLogger('mks146')

def getDefault():
    global instance
    return instance


class MKS146Plugin(kernel.plugin.Plugin):
    __module__ = __name__

    def __init__(self):
        global instance
        self.logger = logging.getLogger('MKS146Plugin')
        kernel.plugin.Plugin.__init__(self)
        instance = self
        self.contextBundle = None
        ui.getDefault().setSplashText('Loading MKS 146 plugin ...')
        return

    def getContextBundle(self):
        return self.contextBundle

    def startup(self, contextBundle):
        self.contextBundle = contextBundle
        hwType = mks146type.MKS146HardwareType()
        hardware.hardwaremanager.registerHardwareType(hwType)
        executionengine.getDefault().registerRecipeParticipantFactory(hwType.getType(), mks146.participant.RecipeParticipantFactory())
        hw = hardware.hardwaremanager.getHardwareByType(hwType.getType())

    def beginInstantiation(self, descriptions):
        for description in descriptions:

            class InstancingThread(threading.Thread):
                __module__ = __name__

                def run(innerself):
                    hardware = MKS146Hardware(description)
                    initialize = False
                    try:
                        initialize = description.getConfiguration().get('main', 'startupinit').lower() == 'true'
                    except Exception as msg:
                        pass

                    if initialize:
                        hardware.initialize()

            t = InstancingThread()
            t.start()


import time

class StateCaller(threading.Thread):
    __module__ = __name__

    def __init__(self, hwinst):
        threading.Thread.__init__(self)
        self.hwinst = hwinst
        self.isDone = False
        self.channels = [0, 0, 0, 0]

    def done(self):
        self.hwinst.interruptOperation()
        self.isDone = True

    def run(self):
        while not self.isDone:
            for i in range(len(self.channels)):
                try:
                    self.channels[i] = self.hwinst.getChannelFlow(i)
                except Exception as msg:
                    self.isDone = True
                    return

            time.sleep(0.03)


class StatusThread(BackgroundProcessThread):
    __module__ = __name__

    def __init__(self, hwinst):
        BackgroundProcessThread.__init__(self, hwinst)
        self.throttle = 0.5
        self.channels = []

    def run(self):
        while not self.done:
            self.lock.acquire()
            self.lock.wait(self.throttle)
            if not self.paused:
                try:
                    self.askHardware()
                except Exception as msg:
                    logger.exception(msg)

            self.lock.release()

    def askHardware(self):
        inst = self.hwinst
        if inst.getStatus() == hardware.hardwaremanager.STATUS_RUNNING or inst.getStatus() == hardware.hardwaremanager.STATUS_PURGING:
            pass
        else:
            return
        numc = inst.getChannelCount()
        if numc != len(self.channels):
            self.channels = list(map((lambda x: 0), list(range(numc))))
        for i in range(numc):
            try:
                self.channels[i] = inst.getChannelCondition(i + 1)
            except Exception as msg:
                self.paused = True
                logger.exception(msg)

        logger.debug('Look at all my channels: %s' % self.channels)


class MKSPurgeThread(PurgeThread):
    __module__ = __name__

    def __init__(self, hwinst):
        PurgeThread.__init__(self, hwinst)
        self.setpoints = []
        self.starttime = 0
        self.completed = []

    def getDescription(self):
        return self.hwinst.getDescription().getName()

    def purgestart(self):
        self.starttime = time.time()
        try:
            for (channel, setpoint, length) in self.setpoints:
                logger.debug('Setting %d %f %s' % (channel, setpoint, str(length)))
                self.hwinst.setChannelSetpoint(channel, setpoint)

        except Exception as msg:
            logger.exception(msg)
            logger.debug('Unable to start purging: %s' % msg)
            self.stop()

    def setPurgeSetpoints(self, setpoints):
        self.setpoints = setpoints

    def purgestop(self):
        try:
            for (channel, ignored, ignored2) in self.setpoints:
                try:
                    self.hwinst.disableChannel(channel)
                except Exception as msg:
                    logger.exception(msg)

                time.sleep(0.2)

            self.completed = []
            self.setpoints = []
            self.done = True
        except Exception as msg:
            logger.exception(msg)

    def tick(self):
        now = time.time()
        delta = now - self.starttime
        for (channel, sepoint, length) in self.setpoints:
            try:
                self.hwinst.getChannelCondition(channel)
            except Exception as msg:
                logger.exception(msg)
                self.purgestop()

            if delta > length and not channel in self.completed:
                logger.debug('Purge end disabling channel: %s' % channel)
                self.hwinst.disableChannel(channel)
                self.completed.append(channel)
            logger.debug('Completed: %s' % self.completed)

        if len(self.completed) == len(self.setpoints):
            self.purgestop()


DEFAULT_PROPS_FILENAME = 'default.devices.props'

class MKS146Hardware(hardware.hardwaremanager.Hardware, mfc.hardwarestatusprovider.HardwareStatusProvider):
    __module__ = __name__

    def __init__(self):
        mfc.hardwarestatusprovider.HardwareStatusProvider.__init__(self)
        self.logger = logging.getLogger('MKS146Hardware')
        hardware.hardwaremanager.Hardware.__init__(self)
        self.channelNum = 4
        self.setpoints = list(map((lambda x: None), list(range(self.channelNum))))
        self.statusThread = StatusThread(self)
        self.statusThread.start()

    def createDefaultDeviceProperties(self, path):
        dfp = os.path.join(getDefault().getContextBundle().dirname, DEFAULT_PROPS_FILENAME)
        self.logger.debug("Acquiring default device properties at '%s'" % dfp)
        if os.path.exists(dfp) and os.path.isfile(dfp):
            shutil.copyfile(dfp, path)
            return

    def createDefaultDevices(self):
        """Creates one furnace zone device"""
        factory = core.deviceregistry.getDeviceFactory('mfc')
        props = self.readDefaultDeviceProperties()
        if props is None:
            return []
        devices = []
        section = ''
        for i in range(4):
            section = 'channel.%d' % (i + 1)
            if not props.has_section(section):
                continue
            device = factory.getInstance()
            hwhints = device.getHardwareHints()
            hwhints.createChildIfNotExists('id').setValue(self.getDescription().getName())
            hwhints.createChildIfNotExists('channel').setValue(str(i + 1))
            hwhints.createChildIfNotExists('units').setValue(props.get(section, 'units'))
            hwhints.createChildIfNotExists('range').setValue(props.get(section, 'range'))
            hwhints.createChildIfNotExists('conversion-factor').setValue(props.get(section, 'conversion-factor'))
            purgeNode = hwhints.createChildIfNotExists('purge')
            purgeNode.setAttribute('active', props.get(section, 'purge'))
            purgeNode.setAttribute('setpoint', props.get(section, 'purge.setpoint'))
            purgeNode.setAttribute('duration', props.get(section, 'purge.duration'))
            uihints = device.getUIHints()
            uihints.createChildIfNotExists('label').setValue(props.get(section, 'label'))
            uihints.createChildIfNotExists('column-use-gcf').setValue(props.get(section, 'column-use-gcf'))
            colors = uihints.createChildIfNotExists('colors')
            colors.createChildIfNotExists('plot').setValue(props.get(section, 'colors.plot'))
            device.updateUIHints()
            devices.append(device)

        return devices
        return

    def finishedPurge(self):
        self.resumeStatusThread()

    def startPurge(self, setpoints):
        self.purgeWorker = MKSPurgeThread(self)
        self.purgeWorker.setPurgeSetpoints(setpoints)
        self.purgeWorker.start()

    def checkChannel(self, channelNum):
        if channelNum > self.channelNum:
            raise Exception('Invalid channel number %d' % channelNum)

    def enableChannel(self, channelNum):
        self.checkDriver()
        self.driver.enableChannel(channelNum)

    def disableChannel(self, channelNum):
        self.checkDriver()
        self.driver.disableChannel(channelNum)
        self.setpoints[channelNum - 1] = None
        return

    def setRange(self, channelNum, r):
        self.checkDriver()
        self.checkChannel(channelNum)
        self.driver.setRange(channelNum, r)

    def getSetpoint(self, channelNum):
        return self.setpoints[channelNum - 1]

    def setChannelSetpoint(self, channelNum, flow):
        self.checkDriver()
        self.checkChannel(channelNum)
        try:
            self.driver.setSetpoint(channelNum, flow)
            self.setpoints[channelNum - 1] = flow
        except Exception as msg:
            self.logger.exception(msg)
            raise

    def setSetpointMode(self, channel, mode):
        self.checkDriver()
        self.checkChannel(channel)
        self.driver.setSetpointMode(channel, mode)

    def setUnits(self, channel, unitsIndex):
        self.checkDriver()
        self.checkChannel(channel)
        self.driver.setUnits(channel, unitsIndex)

    def stopPurge(self):
        self.purgeWorker.pause()

    def dispose(self):
        hardware.hardwaremanager.Hardware.dispose(self)
        try:
            self.purgeWorker.stop()
        except Exception as msg:
            self.logger.exception(msg)

        try:
            self.statusThread.stop()
        except Exception as msg:
            self.logger.exception(msg)

    def resumeStatusThread(self):
        logger.debug('Resulting status thread')
        self.statusThread.resume()

    def stopStatusThread(self):
        logger.debug('Pausing status thread.')
        self.statusThread.pause()

    def getChannelCount(self):
        return self.channelNum

    def getID(self):
        self.checkDriver()
        try:
            return self.driver.getID()
        except ResponseTimeoutException as msg:
            self.cleanup()
            raise

    def getChannelCondition(self, channel):
        self.checkDriver()
        self.checkChannel(channel)
        try:
            resp = self.driver.getChannelCondition(channel)
            self.statusGetFlow(channel, resp[1])
            return resp
        except ResponseTimeoutException as msg:
            self.cleanup()
            raise

    def getChannelFlow(self, channelNum):
        raise Exception('USE getChannelCondition instead')
        self.checkDriver()
        try:
            flow = self.driver.getFlow(channelNum)
            self.statusGetFlow(channelNum, flow)
            return flow
        except ResponseTimeoutException as msg:
            self.cleanup()
            raise

    def checkDriver(self):
        if self.driver is None:
            raise Exception('No driver set')
        return

    def interruptOperation(self):
        if self.driver is None:
            return
        self.driver.interrupt()
        return

    def setupDriver(self, description):
        self.driver = None
        config = description.getConfiguration()
        try:
            driverType = config.get('driver', 'type')
            inst = mks146.drivers.getDriver(driverType)()
            self.setDriver(inst)
            self.driver.setConfiguration(config)
        except Exception as msg:
            self.driver = None
            self.logger.exception(msg)
            self.logger.error("Cannot initialize driver: '%s'" % msg)
            self.fireHardwareEvent(hardware.hardwaremanager.HardwareEvent(self, hardware.hardwaremanager.EVENT_ERROR, "* ERROR: Cannot initialize driver: '%s'" % msg))

        try:
            self.channelNum = int(config.get('main', 'channels'))
        except Exception as msg:
            self.channelNum = 4

        return

    def setDriver(self, driver):
        self.driver = driver

    def initialize(self):
        self.checkDriver()
        try:
            self.logger.debug('Initializing driver %s' % str(self.driver))
            self.driver.initialize()
            self.logger.debug('Resuming status thread')
            self.resumeStatusThread()
            self.logger.debug('Done')
        except Exception as msg:
            self.logger.exception(msg)
            self.logger.error("Cannot initialize: '%s'" % msg)
            self.fireHardwareEvent(hardware.hardwaremanager.HardwareEvent(self, hardware.hardwaremanager.EVENT_ERROR, "* ERROR: Cannot initialize: '%s'" % msg))
            raise core.error.WorkbenchException('Unable to initialize %s - %s' % (self.getDescription().getName(), msg))

        self.status = hardware.hardwaremanager.STATUS_RUNNING
        self.logger.debug('Going to fire hardware status changed')
        self.fireHardwareStatusChanged()
        self.logger.debug('Goind to fire status is running')
        self.fireStatusIsRunning()

    def shutdown(self):
        if self.driver is None:
            return
        try:
            self.driver.shutdown()
        except Exception as msg:
            self.logger.error("Unable to shutdown '%s'" % msg)
            self.fireHardwareEvent(hardware.hardwaremanager.HardwareEvent(self, hardware.hardwaremanager.EVENT_ERROR, "* ERROR: Cannot shutdown: '%s'" % msg))
            raise Exception(msg)

        self.status = hardware.hardwaremanager.STATUS_STOPPED
        self.fireHardwareStatusChanged()
        self.fireStatusIsStopped()
        return
