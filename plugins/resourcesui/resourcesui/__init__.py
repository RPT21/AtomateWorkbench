# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/resourcesui/src/resourcesui/__init__.py
# Compiled at: 2004-11-23 19:36:56
import lib.kernel.plugin, lib.kernel as kernel
import plugins.poi.poi.actions
import plugins.resourcesui.resourcesui.images as images
import plugins.resourcesui.resourcesui.messages as messages, logging
import plugins.ui.ui as ui
import plugins.poi.poi as poi
import plugins.resources.resources as resources
import plugins.resourcesui.resourcesui.actions as resourcesui_actions
import plugins.resourcesui.resourcesui.preferences as resourcesui_preferences

PLUGIN_ID = 'resourcesui'
CONFIG_FILENAME = '.config'
logger = logging.getLogger('resources.ui')

def getDefault():
    global default
    return default


class ResourcesUIPlugin(kernel.plugin.Plugin):
    __module__ = __name__

    def __init__(self):
        global default
        kernel.plugin.Plugin.__init__(self)
        default = self

    def startup(self, contextBundle):
        self.contextBundle = contextBundle
        ui.getDefault().addInitListener(self)
        images.init(contextBundle)
        messages.init(contextBundle)
        preferencesStore = resources.getDefault().getPreferencesStore()
        ui.preferences.getDefault().addPage(resourcesui_preferences.PreferencesPage(preferencesStore))

    def handlePartInit(self, part):
        if not isinstance(part, ui.UIPlugin):
            return
        ui.getDefault().removeInitListener(self)
        fileManager = ui.getDefault().getMenuManager().findByPath('atm.file')
        fileManager.appendToGroup('file-additions-begin', poi.actions.Separator())
        fileManager.appendToGroup('file-additions-begin', poi.actions.ActionContributionItem(resourcesui_actions.OpenRecipeManagerAction()))
        fileManager.appendToGroup('file-additions-begin', poi.actions.Separator())
        fileManager.appendToGroup('file-additions-begin', poi.actions.GroupMarker('close-group-end'))
        fileManager.appendToGroup('file-additions-begin', poi.actions.Separator())
        fileManager.appendToGroup('file-additions-begin', poi.actions.ActionContributionItem(resourcesui_actions.CloseCurrentRecipeAction()))
        fileManager.appendToGroup('file-additions-begin', poi.actions.GroupMarker('close-group-begin'))
        fileManager.appendToGroup('file-additions-begin', poi.actions.Separator())
        fileManager.appendToGroup('file-additions-begin', poi.actions.ActionContributionItem(resourcesui_actions.NewRecipeWizardAction(), 'new-wizard'))
        fileManager.update()
