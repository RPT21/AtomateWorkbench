# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/core/src/core/conditional.py
# Compiled at: 2004-09-22 20:51:00
import logging
logger = logging.getLogger('core.conditionals')
conditionalContributions = {}
actionContributions = {}

def addConditionalTestFactory(contribType, func):
    """Register a class of conditional contribution"""
    global conditionalContributions
    if not conditionalContributions.has_key(contribType):
        conditionalContributions[contribType] = func


def getConditionalTestFactoryFor(contribType):
    if conditionalContributions.has_key(contribType):
        return conditionalContributions[contribType]
    return None
    return


def addConditionalActionFactory(typestr, func):
    global actionContributions
    if not actionContributions.has_key(typestr):
        actionContributions[typestr] = func


def getConditionalActionFactoryFor(typestr):
    if actionContributions.has_key(typestr):
        return actionContributions[typestr]
    return None
    return


def parseFromNode(node, recipe):
    conditional = None
    testsNode = node.getChildNamed('tests')
    tests = []
    conditionalTests = ConditionalTests()
    name = node.getAttribute('name')
    conditionalTests.setName(name)
    connective = node.getAttribute('connective')
    conditionalTests.setUseConnectiveAnd(connective == CONNECTIVE_AND)
    for testNode in testsNode.getChildren('test'):
        condTypeStr = testNode.getAttribute('type')
        func = getConditionalTestFactoryFor(condTypeStr)
        if func is None:
            raise Exception("Unable to parse conditional '%s'" % testNode)
        test = func(testNode, recipe)
        conditionalTests.appendTest(test)

    actionsNode = node.getChildNamed('actions')
    for actionNode in actionsNode.getChildren('action'):
        typestr = actionNode.getAttribute('type')
        func = getConditionalActionFactoryFor(typestr)
        if func is None:
            raise Exception("Unable to parse action conditional '%s'" % actionNode)
        action = func(actionNode, recipe)
        conditionalTests.appendAction(action)

    return conditionalTests
    return


class ConditionalContribution(object):
    __module__ = __name__

    def __init__(self, device):
        self.device = device

    def handles(self, test):
        return False

    def handlesByType(self, strType):
        return False

    def createFromNode(self, node):
        raise NotImplementedMethod()

    def getTestEditorContributions(self):
        return []


class ConditionalTestEditorContribution(object):
    """Implemented by objects interested i populating the editor"""
    __module__ = __name__

    def __init__(self, device):
        self.device = device
        self.test = None
        return

    def getLeftOperandString(self):
        raise NotImplementedException()

    def getOperators(self):
        raise NotImplementedException()

    def getRightOperandControl(self, parent):
        raise NotImplementedException()

    def createTest(self, operatorIdx, control):
        raise NotImplementedException()

    def populateFromTest(self, test):
        self.test = test

    def setRightOperandValue(self, control):
        pass

    def getOperatorIndex(self):
        return 0


class ConditionalTest(object):
    __module__ = __name__

    def __init__(self):
        self.device = None
        self.operand = None
        self.operator = None
        return

    def getDevice(self):
        return self.device

    def getRightOperand(self):
        return self.operand

    def getOperator(self):
        return self.operator

    def evaluate(self, envelope):
        return False

    def getType(self):
        raise NotImplementedError()

    def convertToNode(self, node):
        node.setAttribute('type', self.getType())

    def clone(self):
        raise NotImplementedError()


CONNECTIVE_AND = 'and'
CONNECTIVE_OR = 'or'

def connectiveAnd(a, b):
    return a and b


def connectiveOr(a, b):
    return a or b


CONNECTIVE_METHODS = {CONNECTIVE_AND: connectiveAnd, CONNECTIVE_OR: connectiveOr}

class ConditionalTests(object):
    __module__ = __name__

    def __init__(self):
        self.conditionaltests = []
        self.name = ''
        self.connective = CONNECTIVE_AND
        self.connector = CONNECTIVE_METHODS[self.connective]
        self.actions = []

    def getTests(self):
        return self.conditionaltests

    def clear(self):
        """Clear all tests"""
        del self.conditionaltests[0:]

    def appendAction(self, action):
        self.actions.append(action)

    def setActions(self, actions):
        self.actions = actions

    def clearActions(self):
        del self.actions[0:]

    def appendTest(self, test):
        self.conditionaltests.append(test)

    def removeTest(self, test):
        self.conditionaltests.remove(test)

    def setTests(self, tests):
        self.conditionaltests = tests

    def getName(self):
        return self.name

    def setName(self, name):
        self.name = name

    def getConnective(self):
        return self.connective

    def setUseConnectiveAnd(self, useit):
        if useit:
            self.connective = CONNECTIVE_AND
        else:
            self.connective = CONNECTIVE_OR
        self.connector = CONNECTIVE_METHODS[self.connective]

    def isConnectiveAnd(self):
        return self.connective == CONNECTIVE_AND

    def isConnectiveOr(self):
        return self.connective == CONNECTIVE_OR

    def getConditionalTests(self):
        return self.conditionaltests

    def getActions(self):
        return self.actions

    def evaluate(self, replyEnvelope):
        answers = []
        for test in self.conditionaltests:
            logger.debug('\t\tTest: %s' % test)
            answers.append(test.evaluate(replyEnvelope))

        if len(answers) == 0:
            return False
        return reduce(self.connector, answers)

    def convertToNode(self, node):
        node.setAttribute('name', self.getName())
        node.setAttribute('connective', self.getConnective())
        testsNode = node.createChild('tests')
        for test in self.getTests():
            testNode = testsNode.createChild('test')
            test.convertToNode(testNode)

        actionsNode = node.createChild('actions')
        for action in self.actions:
            actionNode = actionsNode.createChild('action')
            action.convertToNode(actionNode)

    def clone(self):
        ct = ConditionalTests()
        for test in self.conditionaltests:
            ct.conditionaltests.append(test.clone())

        ct.connective = self.connectives
        for action in self.actions:
            ct.actions.append(action.clone())

        return ct


class ConditionalAction(object):
    __module__ = __name__

    def __init__(self):
        pass

    def getType(self):
        raise NotImplementedError()

    def convertToNode(self, node):
        node.setAttribute('type', self.getType())

    def execute(self, context):
        pass


class StepConditional(object):
    __module__ = __name__

    def __init__(self):
        self.device = None
        self.testSuites = []
        return

    def __repr__(self):
        return '[StepConditional: tests suites = %d]' % (self.getDevice(), len(self.testSuites))

    def clone(self):
        nc = Conditional()
        nc.device = device
        for suite in self.testSuites:
            nc.testSuites.append(suite.clone())

        return nc
