# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/executionengine/src/executionengine/actions.py
# Compiled at: 2004-10-18 23:48:59
import plugins.poi.poi.actions, plugins.executionengine.executionengine.messages as messages, plugins.executionengine.executionengine
import plugins.executionengine.executionengine.images as images, plugins.ui.ui.context, copy, wx
import plugins.resources.resources, plugins.executionengine.executionengine.purgemanager
isValid = False
oldValidValue = True
enablementState = True
runAction = None
pauseAction = None
resumeAction = None
advanceAction = None
abortAction = None
stopPurgeAction = None

def createActions():
    global abortAction
    global advanceAction
    global pauseAction
    global resumeAction
    global runAction
    global stopPurgeAction
    runAction = RunRecipeAction()
    pauseAction = PauseRecipeAction()
    resumeAction = ResumeRecipeAction()
    advanceAction = AdvanceRecipeAction()
    abortAction = AbortRecipeAction()
    stopPurgeAction = StopPurgeAction()


def abortRecipe():
    plugins.executionengine.executionengine.getDefault().getEngine().stop()


def startRecipe():
    plugins.ui.ui.context.setProperty('execution', 'running')
    plugins.ui.ui.context.setProperty('can-edit', False)
    recipe = plugins.ui.ui.context.getProperty('recipe')
    engine = plugins.executionengine.executionengine.getDefault().createEngine()
    engine.setRecipe(recipe)
    engine.start()


def contextChanged(event):
    key = event.getKey()
    modify = key == 'execution' or key == 'recipe'
    if not modify:
        return
    updateActions()


def updateActions():
    global enablementState
    global isValid
    purging = len(plugins.executionengine.executionengine.purgemanager.getPurgeWorkers()) > 0
    stopPurgeAction.setEnabled(purging)
    plugins.executionengine.executionengine.getDefault().fireEnablementState()
    if not isValid or purging or not enablementState:
        runAction.setEnabled(False)
        pauseAction.setEnabled(False)
        resumeAction.setEnabled(False)
        advanceAction.setEnabled(False)
        abortAction.setEnabled(False)
    else:
        execstate = ui.context.getProperty('execution')
        recipe = ui.context.getProperty('recipe')
        if execstate is None:
            runAction.setEnabled(recipe is not None)
        else:
            runAction.setEnabled(execstate is 'stopped' and recipe is not None)
            pauseAction.setEnabled(execstate is 'running')
            resumeAction.setEnabled(execstate is 'paused')
            advanceAction.setEnabled(execstate in ('paused', 'running'))
            abortAction.setEnabled(execstate in ('paused', 'running'))
    tbm = plugins.ui.ui.getDefault().getToolBarManager()
    tbm.update()
    return


class RunRecipeAction(plugins.poi.poi.actions.Action):
    __module__ = __name__

    def __init__(self):
        plugins.poi.poi.actions.Action.__init__(self, messages.get('runmenu.run'), messages.get('runmenu.run.tip'), messages.get('runmenu.run.tip'))
        self.setEnabled(False)
        self.setImage(images.getImage(images.RUN_ENABLED))
        self.setDisabledImage(images.getImage(images.RUN_DISABLED))

    def run(self):
        startRecipe()


class PauseRecipeAction(plugins.poi.poi.actions.Action):
    __module__ = __name__

    def __init__(self):
        plugins.poi.poi.actions.Action.__init__(self, messages.get('runmenu.pause'), messages.get('runmenu.pause.tip'), messages.get('runmenu.pause.tip'))
        self.setEnabled(False)
        self.setImage(images.getImage(images.PAUSE_ENABLED))
        self.setDisabledImage(images.getImage(images.PAUSE_DISABLED))

    def run(self):
        plugins.ui.ui.context.setProperty('execution', 'paused')
        plugins.executionengine.executionengine.getDefault().getEngine().pause()


class ResumeRecipeAction(plugins.poi.poi.actions.Action):
    __module__ = __name__

    def __init__(self):
        plugins.poi.poi.actions.Action.__init__(self, messages.get('runmenu.resume'), messages.get('runmenu.resume.tip'), messages.get('runmenu.resume.tip'))
        self.setEnabled(False)
        self.setImage(images.getImage(images.RESUME_ENABLED))
        self.setDisabledImage(images.getImage(images.RESUME_DISABLED))

    def run(self):
        plugins.ui.ui.context.setProperty('execution', 'running')
        plugins.executionengine.executionengine.getDefault().getEngine().resume()


class AdvanceRecipeAction(plugins.poi.poi.actions.Action):
    __module__ = __name__

    def __init__(self):
        plugins.poi.poi.actions.Action.__init__(self, messages.get('runmenu.advance'), messages.get('runmenu.advance.tip'), messages.get('runmenu.advance.tip'))
        self.setEnabled(False)
        self.setImage(images.getImage(images.ADVANCE_ENABLED))
        self.setDisabledImage(images.getImage(images.ADVANCE_DISABLED))

    def run(self):
        plugins.ui.ui.context.setProperty('execution', 'running')
        plugins.executionengine.executionengine.getDefault().getEngine().advance()


class AbortRecipeAction(plugins.poi.poi.actions.Action):
    __module__ = __name__

    def __init__(self):
        plugins.poi.poi.actions.Action.__init__(self, messages.get('runmenu.abort'), messages.get('runmenu.abort.tip'), messages.get('runmenu.abort.tip'))
        self.setEnabled(False)
        self.setImage(images.getImage(images.ABORT_ENABLED))
        self.setDisabledImage(images.getImage(images.ABORT_DISABLED))

    def run(self):
        abortRecipe()


class StopPurgeAction(plugins.poi.poi.actions.Action):
    __module__ = __name__

    def __init__(self):
        plugins.poi.poi.actions.Action.__init__(self, messages.get('runmenu.stoppurge'), messages.get('runmenu.stoppurge.tip'), messages.get('runmenu.stoppurge.tip'))
        self.setEnabled(False)
        self.setImage(images.getImage(images.STOP_PURGE_ENABLED))
        self.setDisabledImage(images.getImage(images.STOP_PURGE_DISABLED))

    def run(self):
        plugins.executionengine.executionengine.purgemanager.cancelPurge()
