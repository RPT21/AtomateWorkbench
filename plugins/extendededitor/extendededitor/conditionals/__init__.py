# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/extendededitor/src/extendededitor/conditionals/__init__.py
# Compiled at: 2004-11-18 18:59:11
import core.conditional, logging
logger = logging.getLogger('extendededitor')

class AbortRecipeAction(core.conditional.ConditionalAction):
    __module__ = __name__

    def execute(self, context):
        """context is engine"""
        logger.debug('Executing abort recipe action in context %s' % context)
        context.forceEnd = True

    def getType(self):
        return 'abort-recipe'

    def __repr__(self):
        return 'Abort Recipe'


class AdvanceStepAction(core.conditional.ConditionalAction):
    __module__ = __name__

    def execute(self, context):
        logger.debug('Executing advance step conditional action')
        context.forceAdvance = True

    def getType(self):
        return 'advance-step'

    def __repr__(self):
        return 'Advance'


class HoldStepAction(core.conditional.ConditionalAction):
    __module__ = __name__

    def execute(self, context):
        logger.debug('Executing hold step conditional action')
        context.hold = True

    def getType(self):
        return 'hold-step'

    def __repr__(self):
        return 'Hold'


def holdStepActionFactory(node, recipe):
    return HoldStepAction()


def advanceStepActionFactory(node, recipe):
    return AdvanceStepAction()


def abortRecipeActionFactory(node, recipe):
    return AbortRecipeAction()


core.conditional.addConditionalActionFactory('advance-step', advanceStepActionFactory)
core.conditional.addConditionalActionFactory('hold-step', holdStepActionFactory)
core.conditional.addConditionalActionFactory('abort-recipe', abortRecipeActionFactory)
