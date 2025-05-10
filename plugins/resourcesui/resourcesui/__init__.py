# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/resourcesui/src/resourcesui/__init__.py
# Compiled at: 2004-11-23 19:36:56
import os, core, core.preferencesstore, ConfigParser, kernel.plugin, kernel.pluginmanager as PluginManager, ui, poi.actions, resources, resourcesui.preferences, resources.version, resourcesui.actions, resourcesui.images as images, resourcesui.messages as messages, resources.utils, logging
default = None
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
        ui.preferences.getDefault().addPage(resourcesui.preferences.PreferencesPage(preferencesStore))

    def handlePartInit(self, part):
        if not isinstance(part, ui.UIPlugin):
            return
        ui.getDefault().removeInitListener(self)
        fileManager = ui.getDefault().getMenuManager().findByPath('atm.file')
        fileManager.appendToGroup('file-additions-begin', poi.actions.Separator())
        fileManager.appendToGroup('file-additions-begin', poi.actions.ActionContributionItem(resourcesui.actions.OpenRecipeManagerAction()))
        fileManager.appendToGroup('file-additions-begin', poi.actions.Separator())
        fileManager.appendToGroup('file-additions-begin', poi.actions.GroupMarker('close-group-end'))
        fileManager.appendToGroup('file-additions-begin', poi.actions.Separator())
        fileManager.appendToGroup('file-additions-begin', poi.actions.ActionContributionItem(resourcesui.actions.CloseCurrentRecipeAction()))
        fileManager.appendToGroup('file-additions-begin', poi.actions.GroupMarker('close-group-begin'))
        fileManager.appendToGroup('file-additions-begin', poi.actions.Separator())
        fileManager.appendToGroup('file-additions-begin', poi.actions.ActionContributionItem(resourcesui.actions.NewRecipeWizardAction(), 'new-wizard'))
        fileManager.update()
