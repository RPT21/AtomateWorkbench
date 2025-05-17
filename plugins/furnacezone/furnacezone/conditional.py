# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/furnacezone/src/furnacezone/conditional.py
# Compiled at: 2004-09-22 20:17:39
import wx, plugins.core.core.conditional, logging
import plugins.core.core as core
logger = logging.getLogger('furnacezone')

def equals(x, y):
    return x == y


def lessThan(x, y):
    return x < y


def lessThanOrEqual(x, y):
    return x <= y


def greaterThan(x, y):
    return x > y


def greaterThanOrEqual(x, y):
    return x >= y


OPERATOR_METHODS = {'==': equals, '<': lessThan, '<=': lessThanOrEqual, '>': greaterThan, '>=': greaterThanOrEqual}

class RightOperandControl(object):
    __module__ = __name__

    def __init__(self):
        self.control = None
        return

    def getControl(self):
        return self.control

    def createControl(self, parent):
        ctrl = wx.TextCtrl(parent, -1)
        ctrl.SetFont(parent.GetFont())
        ctrl.SetBackgroundColour(parent.GetBackgroundColour())
        self.control = ctrl
        return ctrl

    def dispose(self):
        pass


class FurnaceZoneConditionalTest(core.conditional.ConditionalTest):
    __module__ = __name__

    def __init__(self, device, operator, temperature):
        super().__init__()
        self.device = device
        self.operator = operator
        self.comparator = OPERATOR_METHODS[operator]
        self.temperature = temperature

    def getDevice(self):
        return self.device

    def getTemperature(self):
        return self.temperature

    def getOperator(self):
        return self.operator

    def evaluate(self, replyEnvelope):
        """A context object makes accessible to the test the things needed to evaluate itself"""
        response = replyEnvelope.getReply(self.device)
        return self.comparator(int(response.getTemperature()), int(self.temperature))

    def getType(self):
        return 'furnacezone_temperature'

    def convertToNode(self, node):
        core.conditional.ConditionalTest.convertToNode(self, node)
        node.setAttribute('device-index', str(self.device.getIndex()))
        node.setAttribute('operator', self.getOperator())
        node.setAttribute('temperature', str(self.getTemperature()))
        node.setAttribute('id', str(self.device.getID()))

    def __repr__(self):
        return '[Furnace Zone Conditional Test: %s %s %s]' % (self.device.getLabel(), self.operator, self.temperature)


OPERATORS = [
 8, 9, 7, 10, 11]

class FurnaceZoneTestEditorContribution(core.conditional.ConditionalTestEditorContribution):
    __module__ = __name__

    def getLeftOperandString(self):
        return '%s - Temperature' % self.device.getLabel()

    def handles(self, test):
        return isinstance(test, FurnaceZoneConditionalTest) and test.device == self.device

    def getOperators(self):
        return OPERATORS

    def getRightOperandControl(self, parent):
        ctrl = RightOperandControl()
        ctrl.createControl(parent)
        return ctrl

    def createTest(self, operatorIdx, control):
        temperature = control.getControl().GetValue()
        try:
            temperature = int(temperature)
        except Exception as msg:
            logger.exception(msg)
            logger.warning("Unable to set proper temperature for test '%s'" % msg)

        operator = self.getOperators()[operatorIdx]
        test = FurnaceZoneConditionalTest(self.device, operator, temperature)
        return test

    def setRightOperandValue(self, control):
        control.getControl().SetValue(str(self.test.getTemperature()))

    def getOperatorIndex(self):
        op = self.test.getOperator()
        return OPERATORS.index(op)


class FurnaceZoneConditionalContribution(core.conditional.ConditionalContribution):
    __module__ = __name__

    def handles(self, test):
        return isinstance(test, FurnaceZoneConditionalTest) and test.device == self.device

    def handlesByType(self, strType):
        return strType in ['furnacezone_temperature']

    def createFromNode(self, node):
        return None

    def getTestEditorContributions(self):
        return [FurnaceZoneTestEditorContribution(self.device)]


def furnaceTempCreator(node, recipe):
    idx = int(node.getAttribute('device-index'))
    deviceID = node.getAttribute('id')
    if id is None:
        raise Exception('No device with id specified for conditional node %s' % node)
    device = recipe.getDeviceByID(deviceID)
    if device is None:
        raise Exception('No device with id %s is in the recipe' % deviceID)
    operator = node.getAttribute('operator')
    temp = int(node.getAttribute('temperature'))
    test = FurnaceZoneConditionalTest(device, operator, temp)
    return test


core.conditional.addConditionalTestFactory('furnacezone_temperature', furnaceTempCreator)
