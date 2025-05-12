# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/adr2100/src/adr2100/__init__.py
# Compiled at: 2004-12-09 00:49:28
import os, py_compile, plugins.core.core as core
import lib.kernel.pluginmanager as PluginManager
import logging, lib.kernel.plugin
from plugins.hardware.hardware import ResponseTimeoutException
import plugins.adr2100.adr2100.adr2100type as adr2100type
import plugins.adr2100.adr2100.images as images
import plugins
import threading
import plugins.adr2100.adr2100.messages as messages
import plugins.ui as ui
from plugins.hardware.hardware.utils.threads import BackgroundProcessThread

instance = None
logger = logging.getLogger('adr2100')

def getDefault():
    global instance
    return instance


class ADR2100Plugin(lib.kernel.plugin.Plugin):
    __module__ = __name__

    def __init__(self):
        global instance
        self.logger = logging.getLogger('adr2100Plugin')
        lib.kernel.plugin.Plugin.__init__(self)
        instance = self
        self.contextBundle = None
        plugins.ui.ui.getDefault().setSplashText('Loading ADR 2100 plugin ...')
        return

    def getContextBundle(self):
        return self.contextBundle

    def startup(self, contextBundle):
        self.contextBundle = contextBundle
        images.init(contextBundle)
        messages.init(contextBundle)
        hwType = adr2100type.ADR2100HardwareType()
        plugins.hardware.hardware.hardwaremanager.registerHardwareType(hwType)
        hw = plugins.hardware.hardware.hardwaremanager.getHardwareByType(hwType.getType())

    def beginInstantiation(self, descriptions):
        for description in descriptions:

            class InstancingThread(threading.Thread):
                __module__ = __name__

                def run(innerself):
                    hardware = ADR2100Hardware(description)
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

            time.sleep(0.25)


class InitializeScriptThread(threading.Thread):
    __module__ = __name__

    def __init__(self, inst):
        threading.Thread.__init__(self)
        self.inst = inst
        self.setDaemon(True)

    def readScript(self):
        dirname = getDefault().getContextBundle().dirname
        DEFAULT_SCRIPT_FILENAME = 'startupscript.txt'
        script = []
        try:
            f = open(os.path.join(dirname, DEFAULT_SCRIPT_FILENAME), 'rt')
            lines = f.readlines()
            lines = list(map((lambda moo: moo.strip()), lines))
            f.close()
            for line in lines:
                (tt, sg) = line.split(':')
                tt = float(tt)
                segs = list(map((lambda moo: moo.strip()), sg.split(',')))
                entry = []
                for seg in segs:
                    ports = list(map((lambda moo: int(moo)), seg.split(' ')))
                    entry.append(ports)

                script.append([tt, entry])

        except Exception as msg:
            logger.exception(msg)

        return script

    def doSequence(self):
        script = self.readScript()
        portNames = [
         'A', 'B', 'C', 'D']
        for port in portNames:
            self.inst.configureDigitalPorts(port, (0, 0, 0, 0, 0, 0, 0, 0))

        for entry in script:
            waitTime = entry[0]
            ports = entry[1]
            i = 0
            for port in ports:
                portName = chr(ord('A') + i)
                self.inst.outputBinaryData(portName, port)
                i += 1

            time.sleep(waitTime)

    def run(self):
        try:
            self.inst.stopStatusThread()
            self.doSequence()
        except Exception as msg:
            logger.exception(msg)

        self.inst.resumeStatusThread()


class StatusThread(BackgroundProcessThread):
    __module__ = __name__

    def __init__(self, hwinst):
        BackgroundProcessThread.__init__(self, hwinst)
        self.throttle = DEFAULT_CHECK_THROTTLE
        self.channels = []
        self.participant = plugins.adr2100.adr2100.safetyparticipant.ADR2100InterlockParticipant()
        self.participant.setHardware(hwinst)

    def run(self):
        while not self.done:
            self.lock.acquire()
            self.lock.wait(0.02)
            if not self.paused:
                try:
                    self.askHardware()
                except Exception as msg:
                    logger.exception(msg)

            self.lock.release()
            time.sleep(self.throttle)

    def setThrottle(self, newThrottle):
        self.throttle = newThrottle

    def askHardware(self):
        inst = self.hwinst
        if inst.getStatus() == plugins.hardware.hardware.hardwaremanager.STATUS_RUNNING or inst.getStatus() == plugins.hardware.hardware.hardwaremanager.STATUS_PURGING:
            self.participant.fireUpdate()
        else:
            return
        inst.executeRequestCode()
        self.participant.touch(inst)


OUTPUT = 0
INPUT = 1
DEFAULT_CHECK_THROTTLE = 1.0

class ADR2100Hardware(plugins.hardware.hardware.hardwaremanager.Hardware):
    __module__ = __name__

    def __init__(self):
        self.driver = None
        self.logger = logging.getLogger('adr2100Hardware')
        plugins.hardware.hardware.hardwaremanager.Hardware.__init__(self)
        self.requestCode = None
        self.validationCode = None
        self.checkThrottle = DEFAULT_CHECK_THROTTLE
        self.statusThread = StatusThread(self)
        self.statusThread.start()
        self.cachedPorts = {'A': (0, 0, 0, 0, 0, 0, 0, 0), 'B': (0, 0, 0, 0, 0, 0, 0, 0), 'C': (0, 0, 0, 0, 0, 0, 0, 0), 'D': (0, 0, 0, 0, 0, 0, 0, 0), '0': 0, '1': 0, '2': 0}
        return

    def setValidationInterval(self, value):
        self.checkThrottle = value
        self.statusThread.setThrottle(self.checkThrottle)

    def getValidationInterval(self):
        return self.checkThrottle

    def getValidationCode(self):
        return self.validationCode

    def getRequestCode(self):
        return self.requestCode

    def executeRequestCode(self):
        if self.requestCode is None:
            return
        try:
            getAnalogPort = self.readAnalogPort
            getDigitalPort = self.readDigitalPorts
            setDigitalPort = self.outputBinaryData
            READ = 1
            WRITE = 0
            configureDigitalPort = self.configureDigitalPorts
            exec(self.requestCode)
        except Exception as msg:
            logger.exception(msg)

        return

    def executeValidationCode(self):
        if self.validationCode is None:
            return (
             True, [])
        try:
            errors = []
            valid = True
            getAnalogPort = self.getCachedPort
            getDigitalPort = self.getCachedPort
            exec(self.validationCode)
            return (valid, errors)
        except Exception as msg:
            logger.exception(msg)
            return (
             False, [msg])


    def getCachedPort(self, port):
        return self.cachedPorts[str(port)]

    def createCodeFileName(self, prefix):
        p = os.path.dirname(self.description.getConfigurationPath())
        name = self.description.getName()
        return os.path.join(p, '%s.%s.txt' % (name, prefix))

    def loadRequestCode(self):
        return self.loadCode('request')

    def loadValidationCode(self):
        return self.loadCode('validation')

    def compileCode(self, source, name):
        try:
            return py_compile.compile(source, name, 'exec')
        except Exception as msg:
            logger.exception(msg)

        return None

    def writeRequestCode(self, txt):
        """ will automatically recompile and replace the existing code with the new one or None if compilation error"""
        self.writeCode(txt, 'request')
        self.processRequestCode(txt)

    def processRequestCode(self, txt):
        self.requestCode = self.processCode(txt, 'request')

    def processValidationCode(self, txt):
        self.validationCode = self.processCode(txt, 'validation')

    def initRequestCode(self):
        txt = self.loadCode('request')
        self.processRequestCode(txt)

    def initValidationCode(self):
        txt = self.loadCode('validation')
        self.processValidationCode(txt)

    def processCode(self, txt, codeType):
        txt = txt.strip()
        if len(txt) == 0:
            return None
        else:
            return self.compileCode(txt, codeType)

    def writeValidateCode(self, txt):
        self.writeCode(txt, 'validation')
        self.processValidationCode(txt)

    def writeCode(self, value, prefix):
        fullpath = self.createCodeFileName(prefix)
        try:
            f = open(fullpath, 'wt')
            f.write(value)
            f.close()
        except Exception as msg:
            logger.exception(msg)

    def loadCode(self, prefix):
        fullpath = self.createCodeFileName(prefix)
        try:
            if not os.path.exists(fullpath):
                open(fullpath, 'wt').close()
            f = open(fullpath, 'rt')
            buff = ''.join(f.readlines())
            f.close()
            return buff
        except Exception as msg:
            logger.exception(msg)
            return None

    def configureDigitalPorts(self, port, config):
        self.checkDriver()
        self.driver.configureDigitalPorts(port, list(config))

    def outputBinaryData(self, port, data):
        self.checkDriver()
        self.driver.outputBinaryData(port, data)
        self.cachedPorts[port] = data

    def readDigitalPorts(self, port):
        self.checkDriver()
        val = self.driver.readDigitalPorts(port)
        self.cachedPorts[port] = val
        return val

    def readAnalogPort(self, port):
        self.checkDriver()
        val = self.driver.readAnalogPort(port)
        self.cachedPorts[str(port)] = val
        return val

    def readAnalogPorts(self):
        self.checkDriver()
        return self.driver.readAnalogPorts()

    def dispose(self):
        plugins.hardware.hardware.hardwaremanager.Hardware.dispose(self)
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

    def getID(self):
        self.checkDriver()
        try:
            return self.driver.getID()
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
        if self.driver is not None:
            self.driver.dispose()
            del self.driver
        self.driver = None
        config = description.getConfiguration()
        try:
            self.throttleCheck = config.get('main', 'checkInterval')
        except Exception as msg:
            logger.exception(msg)

        try:
            driverType = config.get('driver', 'type')
            inst = adr2100.drivers.getDriver(driverType)(self)
            self.setDriver(inst)
            self.driver.setConfiguration(config)
        except Exception as msg:
            self.driver = None
            self.logger.exception(msg)
            self.logger.error("Cannot initialize driver: '%s'" % msg)
            self.fireHardwareEvent(plugins.hardware.hardware.hardwaremanager.HardwareEvent(self, plugins.hardware.hardware.hardwaremanager.EVENT_ERROR, "* ERROR: Cannot initialize driver: '%s'" % msg))

        return

    def setDriver(self, driver):
        self.driver = driver

    def performInitScript(self):
        """
        t = threading.Thread()
        
        def doscriptinit():
            def tick():
                print "tick"
                
            #timer = threading.Timer(5, tick)
            #timer.start()
            time.sleep(5)
            print "YAWN!"
            
            self.resumeStatusThread()
            
        t.run = doscriptinit
        t.start()
        """
        t = InitializeScriptThread(self)
        t.start()

    def initialize(self):
        self.checkDriver()
        self.initRequestCode()
        self.initValidationCode()
        try:
            self.logger.debug('Initializing driver %s' % str(self.driver))
            self.driver.initialize()
            self.performInitScript()
            self.resumeStatusThread()
        except Exception as msg:
            self.resumeStatusThread()
            self.logger.exception(msg)
            self.logger.error("Cannot initialize: '%s'" % msg)
            self.fireHardwareEvent(plugins.hardware.hardware.hardwaremanager.HardwareEvent(self, plugins.hardware.hardware.hardwaremanager.EVENT_ERROR, "* ERROR: Cannot initialize: '%s'" % msg))
            raise plugins.core.core.error.WorkbenchException('Unable to initialize %s - %s' % (self.getDescription().getName(), msg))

        self.status = plugins.hardware.hardware.hardwaremanager.STATUS_RUNNING
        self.fireHardwareStatusChanged()

    def shutdown(self):
        if self.driver is None:
            return
        try:
            self.driver.shutdown()
        except Exception as msg:
            self.logger.error("Unable to shutdown '%s'" % msg)
            self.fireHardwareEvent(plugins.hardware.hardware.hardwaremanager.HardwareEvent(self, plugins.hardware.hardware.hardwaremanager.EVENT_ERROR, "* ERROR: Cannot shutdown: '%s'" % msg))
            self.driver.dispose()
            del self.driver
            self.driver = None
            raise Exception(msg)

        self.driver.dispose()
        del self.driver
        self.driver = None
        self.status = plugins.hardware.hardware.hardwaremanager.STATUS_STOPPED
        self.fireHardwareStatusChanged()
        return
