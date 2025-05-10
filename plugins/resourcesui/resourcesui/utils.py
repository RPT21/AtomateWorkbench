# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/resourcesui/src/resourcesui/utils.py
# Compiled at: 2004-11-02 23:05:03
import lib.kernel, logging, plugins.ui.ui.context
logger = logging.getLogger('resources.ui')
saving = False
hasrun = False

def setHasRun(hasit):
    global hasrun
    hasrun = hasit


def closeRecipe():
    global logger
    logger.debug("Closing recipe: '%s'" % plugins.ui.ui.context.getProperty('recipe'))
    oldrecipe = plugins.ui.ui.context.getProperty('recipe')
    if oldrecipe is not None:
        oldrecipe.dispose()
    plugins.ui.ui.context.setProperty('recipe', None)
    plugins.ui.ui.context.setProperty('can-edit', False)
    return


def hasRun():
    """Returns true if a run has occurred since the recipe was last modified"""
    return hasrun


def clearHasRun():
    global hasrun
    hasrun = False


def saveCurrentRecipe():
    global saving
    logger.debug('Saving current recipe')
    if saving:
        logger.debug('In the process of saving, canceling this save')
        return
    saving = True
    recipe = plugins.ui.ui.context.getProperty('recipe')
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
        newversion = project.promoteVersion(version)
        recipe.setUnderlyingResource(newversion)
        version = newversion
        clearHasRun()
    try:
        writeRecipe(recipe, version)
    except Exception as msg:
        logger.exception(msg)

    recipe.setDirty(False)
    saving = False
    notifyGridEditor()
    return


def notifyGridEditor():
    import plugins.grideditor.grideditor
    recipeModel = plugins.grideditor.grideditor.getDefault().getEditor().getInput()
    recipeModel.touch()


def writeRecipe(recipe, version):
    try:
        buff = recipe.getRaw()
        version.setBuffer(buff)
        version.writeBuffer()
    except Exception as msg:
        logger.exception(msg)
        raise
