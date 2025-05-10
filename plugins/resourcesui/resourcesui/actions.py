# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/resourcesui/src/resourcesui/actions.py
# Compiled at: 2004-11-19 02:34:47
import wx, plugins.ui.ui, plugins.core.core, logging, plugins.poi.poi.actions, plugins.resources.resources
import plugins.resources.resources.version, plugins.resourcesui.resourcesui.recipeexplorer
import plugins.resourcesui.resourcesui.exportrecipewizard, plugins.resourcesui.resourcesui.newrecipewizard
import plugins.resourcesui.resourcesui.messages as messages, plugins.resourcesui.resourcesui.utils
logger = logging.getLogger('resources.ui')

def createInitialVersionAction(project):
    name = plugins.resources.resources.version.getNextVersionName(project)
    workspace = plugins.resources.resources.getDefault().getWorkspace()
    version = workspace.getRecipeVersion(project, name)
    version.create()
    return version


def switchRecipeVersion(version):
    """
    Switches the existing version in the property to a new version
    """
    pass


def openRecipeVersion(version):
    """
    Opens the recipe version, just sets the can-edit to true
    """
    plugins.resourcesui.resourcesui.utils.closeRecipe()
    recipe = plugins.core.core.recipe.loadFromFile(version.getRecipeDataFilename())
    recipe.setUnderlyingResource(version)
    plugins.ui.ui.context.setProperty('recipe', recipe)
    plugins.ui.ui.context.setProperty('can-edit', True)


def getRecipeFromVersion(version):
    recipe = plugins.core.core.recipe.loadFromFile(version.getRecipeDataFilename())
    recipe.setUnderlyingResource(version)
    return recipe


class OpenRecipeDirectlyAction(plugins.poi.poi.actions.Action):
    __module__ = __name__

    def __init__(self):
        plugins.poi.poi.actions.Action.__init__(self, 'Debug - Open Recipe Directly\tCtrl+F1', 'Open a raw recipe for debugging', 'Open a recipe for debugging')

    def run(self):
        self.openRecipe()

    def openRecipe(self):
        global logger
        logger.debug('Opening recipe directly')
        dlg = wx.FileDialog(plugins.ui.ui.getDefault().getMainFrame().getControl(), 'Select a recipe file', plugins.resources.resources.getDefault().getWorkspace().getSharedLocation(), wildcard='Recipe Files (*.recipe)|*.recipe', style=wx.OPEN)
        dlg.CentreOnScreen()
        loaded = False
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            directory = dlg.GetDirectory()
            loaded = True
        dlg.Destroy()
        del dlg
        if loaded:
            version = plugins.resources.resources.version.loadRecipeVersionDirect(directory)
            try:
                recipe = plugins.core.core.recipe.loadFromFile(version.getRecipeDataFilename())
            except Exception as msg:
                logger.error("Unable to parse recipe: '%s'" % msg)
                logger.exception(msg)
                return
            else:
                recipe.setUnderlyingResource(version)


class OpenRecipeManagerAction(plugins.poi.poi.actions.Action):
    __module__ = __name__

    def __init__(self):
        plugins.poi.poi.actions.Action.__init__(self, messages.get('actions.recipemanager.label'), messages.get('actions.recipemanager.help'), messages.get('actions.recipemanager.tip'))

    def run(self):
        explorer = plugins.resourcesui.resourcesui.recipeexplorer.RecipeExplorer()
        explorer.createControl(plugins.ui.ui.getDefault().getMainFrame().getControl())
        explorer.showModal()


class NewRecipeWizardAction(plugins.poi.poi.actions.Action):
    __module__ = __name__

    def __init__(self):
        plugins.poi.poi.actions.Action.__init__(self, messages.get('actions.recipewizard.label'), messages.get('actions.recipewizard.help'), messages.get('actions.recipewizard.tip'))

    def run(self):
        wizard = plugins.resourcesui.resourcesui.newrecipewizard.NewRecipeWizard()
        wizard.createControl(plugins.ui.ui.getDefault().getMainFrame().getControl())
        wizard.showModal()


class ImportWizardAction(plugins.poi.poi.actions.Action):
    __module__ = __name__

    def __init__(self):
        plugins.poi.poi.actions.Action.__init__(self, messages.get('actions.importwizard.label'), messages.get('actions.importwizard.help'), messages.get('actions.importwizard.tip'))
        self.setEnabled(False)

    def run(self):
        print('importwizard')


class ExportWizardAction(plugins.poi.poi.actions.Action):
    __module__ = __name__

    def __init__(self):
        plugins.poi.poi.actions.Action.__init__(self, messages.get('actions.exportwizard.label'), messages.get('actions.exportwizard.help'), messages.get('actions.exportwizard.tip'))

    def run(self):
        wizard = plugins.resourcesui.resourcesui.exportrecipewizard.ExportRecipeWizard()
        recipe = plugins.ui.ui.context.getProperty('recipe')
        resource = recipe.getUnderlyingResource()
        wizard.setResource(resource)
        wizard.createControl(plugins.ui.ui.getDefault().getMainFrame().getControl())
        wizard.showModal()


class CloseCurrentRecipeAction(plugins.poi.poi.actions.Action):
    __module__ = __name__

    def __init__(self):
        plugins.poi.poi.actions.Action.__init__(self, messages.get('actions.closerecipe.label'), messages.get('actions.closerecipe.help'), messages.get('actions.closerecipe.tip'))
        plugins.ui.ui.context.addContextChangeListener(self)
        self.setEnabled(False)

    def contextChanged(self, event):
        key = event.getKey()
        value = event.getNewValue()
        if key != 'can-edit':
            return
        self.setEnabled(value)

    def run(self):
        self.closeRecipe()

    def closeRecipe(self):
        plugins.resourcesui.resourcesui.utils.saveCurrentRecipe()
        plugins.resourcesui.resourcesui.utils.closeRecipe()
