# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/grideditor/src/grideditor/utils/__init__.py
# Compiled at: 2004-11-19 02:30:04
import wx, plugins.ui.ui as ui, plugins.ui.ui.context, logging
import plugins.executionengine.executionengine.engine
import plugins.resourcesui.resourcesui as resourcesui
import plugins.executionengine.executionengine as executionengine
import plugins.resourcesui.resourcesui.utils
import plugins.grideditor.grideditor.recipeoptionsdialog as grideditor_recipeoptionsdialog
import plugins.grideditor.grideditor as grideditor

saving = False
logger = logging.getLogger('grideditor')

def parseColorOption(optionstr):
    try:
        rgb = optionstr.split(',')
        rgb = list(map(int, rgb))
        return wx.Colour(rgb[0], rgb[1], rgb[2])
    except Exception as msg:
        logger.exception(msg)
        logger.warning("Invalid color string option '%s'. Returning RED" % optionstr)
        return wx.RED


hasrun = False

class ExecutionListener(object):
    __module__ = __name__

    def __init__(self):
        self.engine = None
        executionengine.getDefault().addEngineInitListener(self)
        return

    def engineInit(self, engine):
        self.engine = engine
        self.engine.addEngineListener(self)

    def engineEvent(self, event):
        t = event.getType()
        if t == executionengine.engine.TYPE_STARTING:
            logger.debug('setting has run to true')
            resourcesui.utils.setHasRun(True)
        elif t == executionengine.engine.TYPE_HARDWARE_INIT_ERROR:
            logger.debug('Setting has run to false')
            resourcesui.utils.setHasRun(False)
        if t == executionengine.engine.TYPE_ENDING:
            self.engine.removeEngineListener(self)


elistener = ExecutionListener()

def hasRun():
    """Returns true if a run has occurred since the recipe was last modified"""
    global hasrun
    return hasrun


def clearHasRun():
    global hasrun
    hasrun = False


def saveCurrentRecipe():
    global saving
    resourcesui.utils.saveCurrentRecipe()
    if True:
        return
    logger.debug('Saving current recipe')
    if saving:
        logger.debug('In the process of saving, canceling this save')
        return
    saving = True
    recipe = ui.context.getProperty('recipe')
    if recipe is None:
        saving = False
        return
    if not recipe.isDirty() and not hasRun():
        logger.debug('The recipe is not dirty, no save')
        saving = False
        return
    version = recipe.getUnderlyingResource()
    project = version.getProject()
    if hasRun():
        logger.debug('Modifying underlying version because it was run')
        clearHasRun()
        newversion = project.promoteVersion(version)
        recipe.setUnderlyingResource(newversion)
        version = newversion
    try:
        buff = recipe.getRaw()
        version.setBuffer(buff)
        version.writeBuffer()
    except Exception as msg:
        logger.exception(msg)
        logger.error("Cannot save recipe '%s':'%s'" % (version, msg))

    recipe.setDirty(False)
    markRecipeModelDirty()
    saving = False


def markRecipeModelDirty():
    recipeModel = grideditor.getDefault().getEditor().getInput()
    recipeModel.touch()


def showRecipeOptions(device):
    editor = grideditor.getActiveEditor()
    dlg = grideditor_recipeoptionsdialog.RecipeOptionsDialog(editor)
    dlg.createControl(ui.getDefault().getMainFrame().getControl())
    dlg.setShowDevice(device)
    dlg.showModal()
