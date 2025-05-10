# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/resourcesui/src/resourcesui/actions.py
# Compiled at: 2004-11-19 02:34:47
import wx, ui, core, logging, poi.actions, resources, resources.version, resourcesui.recipeexplorer, resourcesui.exportrecipewizard, resourcesui.newrecipewizard, resourcesui.messages as messages, resourcesui.utils
logger = logging.getLogger('resources.ui')

def createInitialVersionAction(project):
    name = resources.version.getNextVersionName(project)
    workspace = resources.getDefault().getWorkspace()
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
    resourcesui.utils.closeRecipe()
    recipe = core.recipe.loadFromFile(version.getRecipeDataFilename())
    recipe.setUnderlyingResource(version)
    ui.context.setProperty('recipe', recipe)
    ui.context.setProperty('can-edit', True)


def getRecipeFromVersion(version):
    recipe = core.recipe.loadFromFile(version.getRecipeDataFilename())
    recipe.setUnderlyingResource(version)
    return recipe


class OpenRecipeDirectlyAction(poi.actions.Action):
    __module__ = __name__

    def __init__(self):
        poi.actions.Action.__init__(self, 'Debug - Open Recipe Directly\tCtrl+F1', 'Open a raw recipe for debugging', 'Open a recipe for debugging')

    def run(self):
        self.openRecipe()

    def openRecipe(self):
        global logger
        logger.debug('Opening recipe directly')
        dlg = wx.FileDialog(ui.getDefault().getMainFrame().getControl(), 'Select a recipe file', resources.getDefault().getWorkspace().getSharedLocation(), wildcard='Recipe Files (*.recipe)|*.recipe', style=wx.OPEN)
        dlg.CentreOnScreen()
        loaded = False
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            directory = dlg.GetDirectory()
            loaded = True
        dlg.Destroy()
        del dlg
        if loaded:
            version = resources.version.loadRecipeVersionDirect(directory)
            try:
                recipe = core.recipe.loadFromFile(version.getRecipeDataFilename())
            except Exception, msg:
                logger.error("Unable to parse recipe: '%s'" % msg)
                logger.exception(msg)
                return
            else:
                recipe.setUnderlyingResource(version)


class OpenRecipeManagerAction(poi.actions.Action):
    __module__ = __name__

    def __init__(self):
        poi.actions.Action.__init__(self, messages.get('actions.recipemanager.label'), messages.get('actions.recipemanager.help'), messages.get('actions.recipemanager.tip'))

    def run(self):
        explorer = resourcesui.recipeexplorer.RecipeExplorer()
        explorer.createControl(ui.getDefault().getMainFrame().getControl())
        explorer.showModal()


class NewRecipeWizardAction(poi.actions.Action):
    __module__ = __name__

    def __init__(self):
        poi.actions.Action.__init__(self, messages.get('actions.recipewizard.label'), messages.get('actions.recipewizard.help'), messages.get('actions.recipewizard.tip'))

    def run(self):
        wizard = resourcesui.newrecipewizard.NewRecipeWizard()
        wizard.createControl(ui.getDefault().getMainFrame().getControl())
        wizard.showModal()


class ImportWizardAction(poi.actions.Action):
    __module__ = __name__

    def __init__(self):
        poi.actions.Action.__init__(self, messages.get('actions.importwizard.label'), messages.get('actions.importwizard.help'), messages.get('actions.importwizard.tip'))
        self.setEnabled(False)

    def run(self):
        print 'importwizard'


class ExportWizardAction(poi.actions.Action):
    __module__ = __name__

    def __init__(self):
        poi.actions.Action.__init__(self, messages.get('actions.exportwizard.label'), messages.get('actions.exportwizard.help'), messages.get('actions.exportwizard.tip'))

    def run(self):
        wizard = resourcesui.exportrecipewizard.ExportRecipeWizard()
        recipe = ui.context.getProperty('recipe')
        resource = recipe.getUnderlyingResource()
        wizard.setResource(resource)
        wizard.createControl(ui.getDefault().getMainFrame().getControl())
        wizard.showModal()


class CloseCurrentRecipeAction(poi.actions.Action):
    __module__ = __name__

    def __init__(self):
        poi.actions.Action.__init__(self, messages.get('actions.closerecipe.label'), messages.get('actions.closerecipe.help'), messages.get('actions.closerecipe.tip'))
        ui.context.addContextChangeListener(self)
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
        resourcesui.utils.saveCurrentRecipe()
        resourcesui.utils.closeRecipe()
