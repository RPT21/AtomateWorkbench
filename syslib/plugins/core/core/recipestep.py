# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/core/src/core/recipestep.py
# Compiled at: 2004-09-22 20:15:31
import core.conditional, core.stepentry, core.recipe, logging
logger = logging.getLogger('core')

def fromNode(node, recipe):
    step = RecipeStep()
    logger.debug("Creating recipe step from node: '%s'" % node)
    duration = long(node.getAttribute('duration'))
    step.setDuration(duration)
    entries = node.getChildNamed('entries')
    repeats = node.getAttribute('repeat')
    if repeats is not None:
        val = repeats.lower() == 'true'
        step.setDoesRepeat(val)
        if val:
            enclosingSteps = int(node.getAttribute('enclosing'))
            repeatcount = int(node.getAttribute('repeatcount'))
            step.setRepeatEnclosingSteps(enclosingSteps)
            step.setRepeatCount(repeatcount)
    if entries != None:
        i = 0
        for entryNode in entries.getChildren():
            device = recipe.getDevice(i)
            entry = device.parseFromNode(entryNode)
            step.addEntry(entry)
            i += 1

    conditionals = node.getChildNamed('conditionals')
    if conditionals != None:
        for conditionalNode in conditionals.getChildren('conditional'):
            try:
                conditional = core.conditional.parseFromNode(conditionalNode, recipe)
                step.addConditional(conditional)
            except Exception, msg:
                logger.exception('Unable to parse conditional %s' % msg)
                continue

    return step
    return


class RecipeStep(object):
    __module__ = __name__

    def __init__(self):
        self.entries = []
        self.conditionals = []
        self.repeats = False
        self.repeatEnclosingSteps = 0
        self.repeatCount = 0
        self.duration = 60

    def getRepeatCount(self):
        return self.repeatCount

    def setRepeatCount(self, count):
        self.repeatCount = count

    def getDuration(self):
        return self.duration

    def setDuration(self, duration):
        self.duration = duration

    def doesRepeat(self):
        return self.repeats

    def getRepeatEnclosingSteps(self):
        return self.repeatEnclosingSteps

    def setDoesRepeat(self, repeats):
        self.repeats = repeats

    def setRepeatEnclosingSteps(self, numSteps):
        self.repeatEnclosingSteps = numSteps

    def setConditionals(self, conditionals):
        self.conditionals = conditionals

    def addEntry(self, entry):
        self.entries.append(entry)

    def insertEntry(self, index, entry):
        self.entries.insert(index, entry)

    def removeEntry(self, index):
        del self.entries[index]

    def getEntries(self):
        return self.entries

    def getEntryIndex(self, entry):
        if not entry in self.entries:
            return -1
        return self.entries.index(entry)

    def getEntry(self, deviceIndex):
        return self.entries[deviceIndex]

    def getConditionals(self):
        return self.conditionals

    def removeConditional(self, conditional):
        self.conditionals.remove(conditional)

    def addConditional(self, conditional):
        self.conditionals.append(conditional)

    def convertToNode(self, root):
        root.setAttribute('duration', str(self.getDuration()))
        if self.doesRepeat():
            root.setAttribute('repeat', 'true')
            root.setAttribute('repeatcount', str(self.getRepeatCount()))
            root.setAttribute('enclosing', str(self.getRepeatEnclosingSteps()))
        conditionalsNode = root.createChild('conditionals')
        for conditional in self.getConditionals():
            condNode = conditionalsNode.createChild('conditional')
            conditional.convertToNode(condNode)

        entriesNode = root.createChild('entries')
        for entry in self.getEntries():
            entryNode = entriesNode.createChild('entry')
            entry.convertToNode(entryNode)

    def reprConditionals(self):
        buff = ''
        for conditional in self.conditionals:
            buff += str(conditional)

        return buff

    def __repr__(self):
        return "[RecipStep: duration='%s', conditionals=(%s), numEntries='%i', repeats='%i', repeatEnclosingSteps='%i', repeatCount='%d', id='%s')]" % (self.getDuration(), self.reprConditionals(), len(self.getEntries()), self.doesRepeat(), self.getRepeatEnclosingSteps(), self.getRepeatCount(), str(id(self)))

    def clone(self):
        nc = RecipeStep()
        nc.duration = self.duration
        nc.repeatCount = self.repeatCount
        nc.repeats = self.repeats
        nc.repeatEnclosingSteps = self.repeatEnclosingSteps
        for conditional in self.conditionals:
            nc.conditionals.append(conditional.clone())

        for entry in self.entries:
            nentry = entry.clone()
            nc.entries.append(entry)

        return nc
