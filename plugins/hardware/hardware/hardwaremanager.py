# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/hardware/src/hardware/hardwaremanager.py
# Compiled at: 2005-06-10 18:53:52
import copy, os, lib.kernel, string, configparser, plugins.hardware.hardware as hardware, logging

logger = logging.getLogger('hardwaremanager')
HARDWARE_CONFIG_DIRNAME = 'configs'
HARDWARE_CONFIG_FILE_SUFFIX = '.cfg'
hardwareTypes = []
hardwareList = []
hardwareManagerListeners = []
STATUS_STOPPED = 0
STATUS_STARTING = 1
STATUS_STOPPING = 2
STATUS_RUNNING = 3
STATUS_PURGING = 4
EVENT_ERROR = 0

class HardwareEvent(object):
    __module__ = __name__

    def __init__(self, source, etype, data):
        self.source = source
        self.etype = etype
        self.data = data

    def getType(self):
        return self.etype

    def getTypeString(self):
        global EVENT_ERROR
        strs = {EVENT_ERROR: 'ERROR'}

    def getData(self):
        return self.data

    def getHardware(self):
        return self.source

    def __repr__(self):
        return "[HardwareEvent - Type:%s,Data:'%s',Hardware:'%s']" % (self.getTypeString(), self.getData(), self.source)


class Hardware(object):
    """Contains information for describing a device configured and managed by the manager"""
    __module__ = __name__

    def __init__(self):
        global STATUS_STOPPED
        self.description = None
        self.hardwareStatusListeners = []
        self.hardwareEventListeners = []
        self.status = STATUS_STOPPED
        self.addHardwareEventListener(hardware.hardwaremanager)
        return

    def prepareDelete(self):
        pass

    def readDefaultDeviceProperties(self):
        props = configparser.RawConfigParser()
        try:
            p = os.path.join(os.path.dirname(self.description.getConfigurationPath()), self.description.getName() + '.default.props')
        except Exception as msg:
            logger.exception(msg)
            return None

        if not os.path.exists(p):
            self.createDefaultDeviceProperties(p)
        if not os.path.exists(p):
            return
        props.read_file(open(p, 'r'), p)
        return props

    def createDefaultDeviceProperties(self, path):
        pass

    def createDefaultDevices(self):
        return []

    def cleanup(self, status=STATUS_STOPPED):
        """This is called by drivers or other operations to reset the hardware back"""
        self.status = status
        self.fireHardwareStatusChanged()
        self.fireStatusIsStopped()

    def finishedPurge(self):
        pass

    def interruptOperation(self):
        """Interrupt whatever wait operation might be in progress"""
        pass

    def addHardwareEventListener(self, listener):
        if not listener in self.hardwareEventListeners:
            self.hardwareEventListeners.append(listener)

    def removeHardwareEventListener(self, listener):
        if listener in self.hardwareEventListeners:
            self.hardwareEventListeners.remove(listener)

    def fireHardwareEvent(self, event):
        list(map((lambda listener: listener.hardwareEvent(event)), self.hardwareEventListeners))

    def addHardwareStatusListener(self, listener):
        if not listener in self.hardwareStatusListeners:
            self.hardwareStatusListeners.append(listener)

    def removeHardwareStatusListener(self, listener):
        if listener in self.hardwareStatusListeners:
            self.hardwareStatusListeners.remove(listener)

    def fireHardwareStatusChanged(self):
        list(map((lambda p: p.hardwareStatusChanged(self)), self.hardwareStatusListeners))

    def setDescription(self, description):
        self.description = description
        self.setupDriver(description)
        description.setInstance(self)

    def getDescription(self):
        return self.description

    def initialize(self):
        pass

    def getStatus(self):
        return self.status

    def getStatusText(self):
        global STATUS_PURGING
        global STATUS_RUNNING
        global STATUS_STARTING
        global STATUS_STOPPING
        strtxt = {STATUS_STOPPED: 'stopped', STATUS_STOPPING: 'stopping', STATUS_STARTING: 'starting', STATUS_RUNNING: 'running', STATUS_PURGING: 'purging'}
        return strtxt[self.status]

    def dispose(self):
        self.removeHardwareEventListener(hardware.hardwaremanager)

    def isConfigured(self):
        """Return true if the configuration is complete but not necesseraly valid"""
        return True


class HardwareDescription(object):
    __module__ = __name__

    def __init__(self, config, configPath):
        self.config = config
        self.configPath = configPath
        self.instance = None
        return

    def getConfiguration(self):
        return self.config

    def getConfigurationPath(self):
        return self.configPath

    def getHandledDeviceTypes(self):
        if not self.config.has_option('main', 'devices'):
            return []
        return self.config.get('main', 'devices').split(',')

    def getHardwareType(self):
        return self.config.get('main', 'hardwareType')

    def getName(self):
        return self.config.get('main', 'name')

    def setInstance(self, instance):
        self.instance = instance

    def getInstance(self):
        return self.instance


def addHardwareManagerListener(listener):
    global hardwareManagerListeners
    if listener not in hardwareManagerListeners:
        hardwareManagerListeners.append(listener)


def removeHardwareManagerListener(listener):
    if listener in hardwareManagerListeners:
        hardwareManagerListeners.remove(listener)


def fireHardwareManagerUpdated():
    list(map((lambda p: p.hardwareManagerUpdated()), hardwareManagerListeners))


def hardwareEvent(event):
    pass


def init():
    fullpath = getHardwareConfigPath()
    for filename in os.listdir(fullpath):
        if not filename.rfind('.cfg') >= 0:
            continue
        try:
            hw = loadHardware(os.path.join(fullpath, filename))
            addHardware(hw)
        except Exception as msg:
            logger.exception(msg)
            logger.error("* ERROR: Unable to load hardware configuration: '%s'" % msg)


def getHardwareType(typeStr):
    global hardwareTypes
    for hwt in hardwareTypes:
        if hwt.getType() == typeStr:
            return hwt

    return None


def loadHardware(fullpath):
    config = configparser.RawConfigParser()
    config.read([fullpath])
    hardwareTypeStr = config.get('main', 'hardwareType')
    hardwareDescription = HardwareDescription(config, fullpath)
    return hardwareDescription


def getHardwareByType(hardwareType):
    global hardwareList
    results = []
    for hw in hardwareList:
        if hw.getHardwareType() == hardwareType:
            results.append(hw)

    return results


def save(hardwareDescription):
    logger.debug('Saving Desc: %s' % hardwareDescription.getConfigurationPath())
    f = open(hardwareDescription.getConfigurationPath(), 'w')
    hardwareDescription.getConfiguration().write(f)
    f.close()


def shutdown():
    for desc in hardwareList:
        inst = desc.getInstance()
        if inst is not None:
            try:
                inst.dispose()
            except Exception as msg:
                logger.exception(msg)

    return


def delete(hardwareDescription):
    global hardwareList
    if not hardwareDescription in hardwareList:
        return
    inst = hardwareDescription.getInstance()
    if inst is not None:
        try:
            if inst.getStatus() is not STATUS_STOPPED:
                try:
                    inst.shutdown()
                except Exception as msg:
                    logger.exception(msg)

            inst.dispose()
        except Exception as msg:
            logger.exception(msg)

    hardwareList.remove(hardwareDescription)
    fullpath = hardwareDescription.getConfigurationPath()
    os.unlink(fullpath)
    fireHardwareRemoved(hardwareDescription)
    fireHardwareManagerUpdated()
    return


def registerHardwareType(hardwareType):
    global hardwareTypes
    hardwareTypes.append(hardwareType)
    fireHardwareManagerUpdated()


def getHardwareTypes():
    global hardwareTypes
    return hardwareTypes


def getHardware():
    global hardwareList
    return hardwareList


def getHardwareConfigPath():
    global HARDWARE_CONFIG_DIRNAME
    path = os.path.join(lib.kernel.getPluginWorkspacePath(hardware.PLUGIN_ID), HARDWARE_CONFIG_DIRNAME)
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def getFilenameFromName(name):
    newname = ''
    allowed = []
    allowed.extend(string.ascii_letters)
    allowed.extend(string.ascii_lowercase)
    for char in name:
        if char not in string.printable:
            continue
        newname += char

    return newname


def create(name, hardwareType):
    global HARDWARE_CONFIG_FILE_SUFFIX
    path = getHardwareConfigPath()
    config = configparser.RawConfigParser()
    config.add_section('main')
    config.set('main', 'name', name)
    config.set('main', 'hardwareType', hardwareType.getType())
    config.set('main', 'startupinit', 'true')  # Afegit per mi
    filename = name
    fullpath = os.path.join(path, filename + HARDWARE_CONFIG_FILE_SUFFIX)
    f = open(fullpath, 'w')
    config.write(f)
    f.close()
    hw = loadHardware(fullpath)
    hwType = getHardwareType(hw.getHardwareType())
    if hwType is not None:
        inst = hwType.getInstance()
        hw.setInstance(inst)
        inst.setDescription(hw)
    addHardware(hw)
    return hw


def fireHardwareAdded(hardware):
    myListeners = copy.copy(hardwareManagerListeners)
    print(('oh thos elisteners: ', myListeners))
    for listener in myListeners:
        print(('listener', listener, hasattr(listener, 'hardwareAdded')))
        if not hasattr(listener, 'hardwareAdded'):
            continue
        listener.hardwareAdded(hardware)

    del myListeners


def fireHardwareRemoved(hardware):
    myListeners = copy.copy(hardwareManagerListeners)
    print(('telling all listeners hardware removed', myListeners))
    for listener in myListeners:
        if not hasattr(listener, 'hardwareRemoved'):
            continue
        listener.hardwareRemoved(hardware)

    del myListeners


def addHardware(hardware):
    hardwareList.append(hardware)
    fireHardwareAdded(hardware)
    fireHardwareManagerUpdated()


def getHardwareByName(name):
    """Returns descriptions"""
    for description in hardwareList:
        if description.getName() == name:
            return description

    return None


def createDevicesForConfiguredHardware():
    """Runs through the list of configured hardware and creates devices
        for the recipe"""
    devices = []
    for hw in getHardware():
        devs = hw.getInstance().createDefaultDevices()
        for dev in devs:
            dev.configurationUpdated()

        devices.extend(devs)

    return devices
