# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/goosemonitor/src/goosemonitor/conditional.py
# Compiled at: 2005-06-29 22:15:15
import wx, copy, core, core.conditional, logging, goosemonitor, hardware.hardwaremanager, goosemonitor.goosedevicetype
logger = logging.getLogger('goosemonitor')

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

class GooseMonitorConditionalTest(core.conditional.ConditionalTest):
    __module__ = __name__

    def __init__(self, fieldKey, device, parentID, operator, value):
        print('creating test for device:', device, fieldKey)
        self.device = device
        self.fieldKey = fieldKey
        self.operator = operator
        self.parentID = parentID
        self.comparator = OPERATOR_METHODS[operator]
        self.value = value

    def getType(self):
        return 'goosemonitor'

    def convertToNode(self, node):
        core.conditional.ConditionalTest.convertToNode(self, node)
        print('gwan convert', self.parentID, self.fieldKey, self.getOperator(), str(self.getValue()))
        node.setAttribute('id', self.parentID)
        node.setAttribute('field', self.fieldKey)
        node.setAttribute('operator', self.getOperator())
        node.setAttribute('value', str(self.getValue()))


class RangeConditionalTest(GooseMonitorConditionalTest):
    __module__ = __name__

    def getValue(self):
        return self.value

    def getOperator(self):
        return self.operator

    def evaluate(self, replyEnvelope):
        print('Told to evaluate!', replyEnvelope)
        return False

    def __repr__(self):
        return '[RangeConditionalTest: %s %s %s]' % ('not chet', self.operator, self.value)


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


RANGE_OPERATORS = [
 8, 9, 7, 10, 11]

class GooseMonitorTestEditorContribution(core.conditional.ConditionalTestEditorContribution):
    __module__ = __name__

    def __init__(self, parentID, fieldKey, field):
        core.conditional.ConditionalTestEditorContribution.__init__(self, field)
        self.parentID = parentID
        self.fieldKey = fieldKey

    def handles(self, test):
        print('GooseMonitorTestEditorContribution.handles')
        print('\t', self.parentID, test.parentID, self.fieldKey, test.fieldKey, type(test))
        return isinstance(test, GooseMonitorConditionalTest) and self.parentID == test.parentID and self.fieldKey == test.fieldKey

    def getLeftOperandString(self):
        return '%s' % self.device['name']

    def getOperators(self):
        global RANGE_OPERATORS
        return RANGE_OPERATORS

    def getRightOperandControl(self, parent):
        ctrl = RightOperandControl()
        ctrl.createControl(parent)
        return ctrl

    def createTest(self, operatorIdx, control):
        value = control.getControl().GetValue()
        try:
            value = int(value)
        except Exception as msg:
            logger.exception(msg)

        operator = self.getOperators()[operatorIdx]
        print('**** creating the shits of the shots, betcho', operator, type(operator))
        test = RangeConditionalTest(self.fieldKey, self.device, self.parentID, operator, value)
        return test

    def setRightOperandValue(self, control):
        print('setRightOperandValue', control, self.test)
        control.getControl().SetValue(str(self.test.getValue()))

    def getOperatorIndex(self):
        op = self.test.getOperator()
        return RANGE_OPERATORS.index(op)


class DeviceHandler(object):
    __module__ = __name__

    def __init__(self, deviceData):
        self.deviceData = copy.copy(deviceData)

    def createEditorContributions(self):
        return []


class AirFlowSensorHandler(DeviceHandler):
    __module__ = __name__

    def __init__(self, data):
        DeviceHandler.__init__(self, data)

    def createEditorContributions(self, parentID):
        return [
         GooseMonitorTestEditorContribution(parentID, 'AirFlow', self.deviceData['fields']['AirFlow'])]


class WeatherDuckHandler(DeviceHandler):
    __module__ = __name__

    def __init__(self, data):
        DeviceHandler.__init__(self, data)
        self.items = {}

    def createEditorContributions(self, parentID):
        fields = self.deviceData['fields']
        contribs = []
        print('asked to create contribs weather duck', fields)
        for field in fields.keys():
            field = str(field)
            if field == 'TempC':
                contribs.append(GooseMonitorTestEditorContribution(parentID, field, fields[field]))

        return contribs


HANDLERS = {'AirFlowSensor': AirFlowSensorHandler, 'WeatherDuck': WeatherDuckHandler}

class GooseMonitorConditionalContribution(core.conditional.ConditionalContribution):
    __module__ = __name__

    def handles(self, test):
        logger.debug('I was asked if i could handle: %s, %s' % (test, dir(test)))
        return isinstance(test, GooseMonitorConditionalTest)

    def handlesByType(self, strType):
        return strType in ['goosemonitor']

    def createFromNode(self, node):
        return None

    def getTestEditorContributions(self):
        global HANDLERS
        print('asked to create editor contrib with device:', self.device)
        contribs = []
        devices = self.device.getInstance().getDevices()
        keys = devices.keys()
        try:
            for did in keys:
                print('Looking for device id:', did)
                device = devices[did]
                print('I got a device', device)
                if not device['type'] in HANDLERS:
                    print("I couldnt' find a type for '%s'" % device['type'])
                    continue
                handler = HANDLERS[device['type']](device)
                print(' I just created a handler:', handler)
                contribs.extend(handler.createEditorContributions(did))

        except Exception as msg:
            logger.exception(msg)

        print(' I got a bunch of contributions:', contribs)
        return contribs


TEST_MAKERS = {'AirFlow': RangeConditionalTest, 'TempC': RangeConditionalTest}

def monitorCondCreator(node, recipe):
    devID = node.getAttribute('id')
    field = node.getAttribute('field')
    logger.debug("monitor conditional creation: '%s' - fuck: %s, val %s" % (devID, field, node.getAttribute('value')))
    operator = node.getAttribute('operator')
    value = int(node.getAttribute('value'))
    types = hardware.hardwaremanager.getHardwareByType(goosemonitor.goosedevicetype.GOOSE_TYPE)
    if not field in TEST_MAKERS:
        return None
    test = TEST_MAKERS[field](field, {}, devID, operator, value)
    print('created test: ', test)
    return test
    return


core.conditional.addConditionalTestFactory('goosemonitor', monitorCondCreator)
