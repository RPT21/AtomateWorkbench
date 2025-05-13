# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/core/src/core/recipe.py
# Compiled at: 2004-11-19 02:10:54
import traceback, plugins.core.core.recipestep, copy, logging
import plugins.core.core.configurationelement as configurationelement
import plugins.core.core.device as device_lib
import plugins.core.core as core
logger = logging.getLogger('core')

def loadFromFile(filename):
    logger.debug("Loading recipe from '%s'" % filename)
    f = open(filename, 'rU')
    buff = f.read()
    f.close()
    try:
        return loadFromString(buff)
    except Exception as msg:
        logger.exception(msg)
        raise Exception(msg)


def loadFromString(buff):
    root = configurationelement.loadFromString(buff)
    if root is None:
        raise Exception('Unable to parse recipe')
    recipe = Recipe()
    devicesNode = root.getChildren('devices')
    if len(devicesNode) == 0:
        raise Exception('No devices node present in recipe')
    devicesNode = devicesNode[0]
    logger.debug('Parsing devices')
    for deviceNode in devicesNode.getChildren('device'):
        deviceType = deviceNode.getAttribute('type')
        deviceID = deviceNode.getAttribute('id')
        if not deviceID:
            deviceID = device_lib.createDeviceID()
            logger.warning('No device id specified, using new %s' % deviceID)
        logger.debug('Using device id: %s' % deviceID)
        inst = findDeviceInRegistry(deviceType)
        if inst is None:
            logger.warning("No devuce type found for name '%s'" % deviceType)
            continue
        uihints = deviceNode.getChildren('ui-hint')[0]
        hwhints = deviceNode.getChildren('hardware-hint')[0]
        inst.setUIHints(uihints)
        inst.setHardwareHints(hwhints)
        inst.setID(deviceID)
        recipe.addDevice(inst)

    logger.debug('Done loading devices')
    for device in recipe.getDevices():
        logger.debug("Device '%s'" % device.getLabel())

    logger.debug('Parsing steps ...')
    stepNodes = root.getChildren('steps')
    if len(stepNodes) == 0:
        raise Exception('No <steps> node present in recipe')
    stepNodes = stepNodes[0]
    for stepNode in stepNodes.getChildren('step'):
        try:
            step = plugins.core.core.recipestep.fromNode(stepNode, recipe)
            recipe.addStep(step)
        except Exception as msg:
            logger.exception(msg)
            logger.error("Unable to parse step '%s'" % stepNode)

    logger.debug('Done parsing steps. %d' % len(recipe.getSteps()))
    return recipe


def convertToNode(recipe):
    node = plugins.core.core.configurationelement.new('recipe')
    devicesNode = node.createChild('devices')
    stepsNode = node.createChild('steps')
    for device in recipe.getDevices():
        deviceNode = devicesNode.createChild('device')
        device.convertToNode(deviceNode)

    for step in recipe.getSteps():
        stepNode = stepsNode.createChild('step')
        step.convertToNode(stepNode)

    return node


def findDeviceInRegistry(deviceType):
    """
    extensions = ModuleRegistry.getExtensions('devices')
    
    for deviceExtensionNode in extensions:
        moduleDeviceType = deviceExtensionNode.getChildren('type')[0].getValue()
        clazzname = deviceExtensionNode.getChildren('class')[0].getValue()
        
        if deviceType == moduleDeviceType:
            return ModuleRegistry.createExecutableElement(clazzname)
    """
    factory = core.deviceregistry.getDeviceFactory(deviceType)
    if factory is not None:
        return factory.getInstance()
    logger.error("No device module found for '%s', creating empty default." % deviceType)
    return core.device.Device(deviceType)


class Recipe(object):
    __module__ = __name__

    def __init__(self):
        self.devices = []
        self.steps = []
        self.underlyingResource = None
        self.dirty = False
        return

    def debugOutput(self):
        logger.debug('------------ DEBUG OUTPUT --------------')
        logger.debug("Number of Steps: '%d'" % len(self.steps))
        for step in self.steps:
            logger.debug('\t%s' % str(step))

        logger.debug('------------ END DEBUG --------------')

    def isDirty(self):
        return self.dirty

    def setDirty(self, dirty=True):
        logger.debug('set dirty %s' % dirty)
        self.dirty = dirty

    def setUnderlyingResource(self, resource):
        self.underlyingResource = resource

    def getUnderlyingResource(self):
        return self.underlyingResource

    def addDevice(self, device):
        self.devices.append(device)
        device.setRecipe(self)

    def removeDevice(self, device):
        if device in self.devices:
            self.devices.remove(device)
            self.removeDeviceFromTests(device)
            device.dispose()

    def removeDeviceFromTests(self, device):
        for step in self.steps:
            for conditional in step.getConditionals():
                tests = copy.copy(conditional.getTests())
                for test in tests:
                    if test.getDevice().getID() == device.getID():
                        logger.debug('Removing test %s from %s' % (test, conditional.getTests()))
                        conditional.removeTest(test)

    def createNewStep(self):
        """Creates a new step based on the entries and sets all entries to default values"""
        step = core.recipestep.RecipeStep()
        for device in self.getDevices():
            step.addEntry(device.createNewStepEntry())

        return step

    def addStep(self, step):
        self.steps.append(step)

    def insertStep(self, index, step):
        self.steps.insert(index, step)

    def removeSteps(self, index, number):
        del self.steps[index:index + number]

    def insertStepsAtOffset(self, offset, steps):
        self.steps = self.steps[0:offset] + steps + self.steps[offset:]

    def getStepIndex(self, step):
        return self.steps.index(step)

    def removeStepByPtr(self, step):
        self.steps.remove(step)

    def removeStep(self, index):
        del self.steps[index]

    def getStepsCount(self):
        return len(self.steps)

    def getSteps(self):
        return self.steps

    def getStep(self, index):
        return self.steps[index]

    def getDevices(self):
        return self.devices

    def getDevice(self, index):
        if index > len(self.devices):
            return None
        return self.devices[index]

    def getDeviceByID(self, deviceID):
        for device in self.devices:
            if device.getID() == deviceID:
                return device

        return None

    def getDeviceIndex(self, device):
        if not device in self.devices:
            return -1
        return self.devices.index(device)

    def getRaw(self):
        return convertToNode(self).tostring()

    def dispose(self):
        for device in self.devices:
            device.dispose()

    def clone(self):
        return loadFromString(convertToNode(self).tostring())
