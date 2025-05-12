# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/rs485/src/rs485/__init__.py
# Compiled at: 2005-03-09 18:51:42
import logging, lib.kernel.plugin, plugins.hardware.hardware.hardwaremanager
import plugins.rs485.rs485.rs485type, plugins.rs485.rs485.drivers, plugins.rs485.rs485.drivers.ser
import plugins.poi.poi.actions, plugins.ui.ui, threading, plugins.executionengine.executionengine
import plugins.rs485.rs485.rs485type, plugins.hardware.hardware as hardware, plugins.rs485.rs485 as rs485
instance = None
logger = logging.getLogger('rs485')

def getDefault():
    global instance
    return instance


class RS485Plugin(lib.kernel.plugin.Plugin):
    __module__ = __name__

    def __init__(self):
        global instance
        self.logger = logging.getLogger('RS485Plugin')
        lib.kernel.plugin.Plugin.__init__(self)
        instance = self
        self.contextBundle = None
        plugins.ui.ui.getDefault().setSplashText('Loading RS 485 plugin ...')
        return

    def getContextBundle(self):
        return self.contextBundle

    def startup(self, contextBundle):
        self.contextBundle = contextBundle
        hwType = plugins.rs485.rs485.rs485type.RS485HardwareType()
        plugins.hardware.hardware.hardwaremanager.registerHardwareType(hwType)
        hw = plugins.hardware.hardware.hardwaremanager.getHardwareByType(hwType.getType())

    def beginInstantiation(self, descriptions):
        for description in descriptions:

            class InstancingThread(threading.Thread):
                __module__ = __name__

                def run(innerself):
                    hardware = plugins.rs485.rs485.RS485Hardware(description)
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
        self.hardwareNodes = self.hwinst.getLinkToNodes()
        self.nodeData = {}

    def done(self):
        self.hwinst.interruptOperation()
        self.isDone = True

    def run(self):
        while not self.isDone:
            for address in list(self.hardwareNodes.keys()):
                try:
                    self.nodeData[address] = self.hwinst.getData(address)
                except Exception as msg:
                    self.isDone = True
                    return

            time.sleep(0.25)


class RS485SerialNetwork(plugins.hardware.hardware.hardwaremanager.Hardware):
    __module__ = __name__

    def __init__(self):
        hardware.hardwaremanager.Hardware.__init__(self)
        self.stcaller = None
        self.nodes = {}
        self.lock = threading.Lock()
        self.locked = False
        self.activeNode = None
        return

    def isLocked(self):
        return self.locked

    def getLock(self):
        self.lock.acquire()

    def releaseLock(self):
        self.lock.release()

    def hasAddress(self, addr):
        return addr in self.nodes

    def getID(self):
        self.checkDriver()
        return self.driver.getID()

    def checkDriver(self):
        if self.driver is None:
            raise Exception('No driver set')
        return

    def checkValidNode(self, node):
        if not self.hasAddress(node.getAddress()):
            raise Exception("Node '%s' not registered for this network" % node)

    def interrupt(self, node):
        if not node == self.currentNode:
            return
        self.interruptOperation()

    def sendNoWait(self, node, command):
        self.checkDriver()
        self.checkValidNode(node)
        self.getLock()
        self.currentNode = node
        try:
            self.driver.sendNoWait(node, command)
        finally:
            self.releaseLock()

    def sendAndWait(self, node, command, timeout):
        """Send a command using the node passed in"""
        self.checkDriver()
        self.checkValidNode(node)
        self.getLock()
        self.currentNode = node
        node.clearBuffer()
        try:
            reply = self.driver.sendAndWait(node, command, timeout)
            return reply
        finally:
            self.releaseLock()

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
            inst = rs485.drivers.getDriver(driverType)()
            self.setDriver(inst)
            self.driver.setConfiguration(config)
        except Exception as msg:
            self.fireHardwareEvent(hardware.hardwaremanager.HardwareEvent(self, hardware.hardwaremanager.EVENT_ERROR, "* ERROR: Cannot initialize driver: '%s'" % msg))

        return

    def setDriver(self, driver):
        self.driver = driver

    def initialize(self):
        self.checkDriver()
        try:
            self.driver.initialize()
        except Exception as msg:
            logger.exception(msg)
            self.fireHardwareEvent(hardware.hardwaremanager.HardwareEvent(self, hardware.hardwaremanager.EVENT_ERROR, "* ERROR: Cannot initialize: '%s'" % msg))
            raise Exception(msg)

        self.status = hardware.hardwaremanager.STATUS_RUNNING
        self.fireHardwareStatusChanged()

    def removeNode(self, node):
        address = node.getAddress()
        if not address in list(self.nodes.keys()):
            return
        del self.nodes[address]

    def addNode(self, node):
        """
        addition of an address node to the RS-485 network
        """
        address = node.getAddress()
        if not list(self.nodes.keys()).count(address) == 0:
            raise Exception('address in use')
        self.nodes[address] = node
        return

    def getNodeAtAddress(self, address):
        if not self.hasAddress(address):
            return None
        return self.nodes[address]

    def getLinkToNodes(self):
        """
        returns a pointer to the nodes
        """
        return self.nodes

    def shutdown(self):
        if self.driver is None:
            return
        try:
            if self.stcaller:
                self.stcaller.done()
                del self.stcaller
                self.stcaller = None
            for node in list(self.nodes.values()):
                node.cleanUp()
                node.removeFromNetwork(self)

            del self.nodes
            self.nodes = {}
            self.driver.shutdown()
        except Exception as msg:
            print(('* ERROR: Unable to shutdown', msg))
            self.fireHardwareEvent(hardware.hardwaremanager.HardwareEvent(self, hardware.hardwaremanager.EVENT_ERROR, "* ERROR: Cannot shutdown: '%s'" % msg))
            raise Exception(msg)

        self.status = hardware.hardwaremanager.STATUS_STOPPED
        self.fireHardwareStatusChanged()
        return


STATUS_NODE_UNINITIALIZED = 0
STATUS_NODE_INITIALIZED = 1
STATUS_NODE_IDLE = 2
STATUS_NODE_RUNNING = 3

class RS485SerialNetworkNode:
    """
    a node in the RS-485 network
    """
    __module__ = __name__

    def __init__(self, address):
        self.address = address
        self.configuration = None
        self.initStatus = STATUS_NODE_UNINITIALIZED
        self.runStatus = STATUS_NODE_IDLE
        self.rs485network = None
        self.buffer = ''
        return

    def __del__(self):
        self.rs485network = None
        return

    def appendToBuffer(self, data):
        self.buffer += data

    def clearBuffer(self):
        self.buffer = ''

    def frameEnded(self):
        """Checks that a frame of reply has ended, if so, it's the
            same as finding a buffer eof"""
        return False

    def incomingData(self):
        """Useful for tagging start of frame"""
        pass

    def resetTime(self):
        """reset junk here"""
        pass

    def getBuffer(self):
        return self.buffer

    def getAddress(self):
        return self.address

    def scanBufferForCommand(self):
        raise Exception('Required method not implemented')

    def removeFromNetwork(self, rs485network):
        if self.rs485network == rs485network:
            self.rs485network = None
        return

    def addToNetwork(self, rs485network):
        if self.rs485network is not None:
            raise Exception('already on an RS-485 network')
        self.rs485network = rs485network
        return

    def setConfiguration(self, configuration):
        self.configuration = configuration

    def initialize(self):
        """
        returns an ordered list of commands to send to the serial driver
          intended to turn set the device in an active state
        the results of each item's action should be error checked and translated
        """
        raise Exception('Not Implemented')

    def cleanUp(self):
        """
        cleans up data within the node, called before deletion
        """
        pass
