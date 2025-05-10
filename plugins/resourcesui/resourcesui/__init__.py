# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/resourcesui/src/resourcesui/__init__.py
# Compiled at: 2004-11-23 19:36:56
import os, plugins.core.core, plugins.core.core.preferencesstore, configparser, lib.kernel.plugin, lib.kernel.pluginmanager as PluginManager
import plugins.ui.ui, plugins.poi.poi.actions, plugins.resources.resources, plugins.resourcesui.resourcesui.preferences
import plugins.resources.resources.version, plugins.resourcesui.resourcesui.actions, plugins.resourcesui.resourcesui.images as images
import plugins.resourcesui.resourcesui.messages as messages, plugins.resources.resources.utils, logging
default = None
PLUGIN_ID = 'resourcesui'
CONFIG_FILENAME = '.config'
logger = logging.getLogger('resources.ui')

def getDefault():
    global default
    return default


class ResourcesUIPlugin(lib.kernel.plugin.Plugin):
    __module__ = __name__

    def __init__(self):
        global default
        lib.kernel.plugin.Plugin.__init__(self)
        default = self

    def startup(self, contextBundle):
        self.contextBundle = contextBundle
        plugins.ui.ui.getDefault().addInitListener(self)
        images.init(contextBundle)
        messages.init(contextBundle)
        preferencesStore = plugins.resources.resources.getDefault().getPreferencesStore()
        plugins.ui.ui.preferences.getDefault().addPage(plugins.resourcesui.resourcesui.preferences.PreferencesPage(preferencesStore))

    def handlePartInit(self, part):
        if not isinstance(part, plugins.ui.ui.UIPlugin):
            return
        plugins.ui.ui.getDefault().removeInitListener(self)
        fileManager = plugins.ui.ui.getDefault().getMenuManager().findByPath('atm.file')
        fileManager.appendToGroup('file-additions-begin', plugins.poi.poi.actions.Separator())
        fileManager.appendToGroup('file-additions-begin', plugins.poi.poi.actions.ActionContributionItem(plugins.resourcesui.resourcesui.actions.OpenRecipeManagerAction()))
        fileManager.appendToGroup('file-additions-begin', plugins.poi.poi.actions.Separator())
        fileManager.appendToGroup('file-additions-begin', plugins.poi.poi.actions.GroupMarker('close-group-end'))
        fileManager.appendToGroup('file-additions-begin', plugins.poi.poi.actions.Separator())
        fileManager.appendToGroup('file-additions-begin', plugins.poi.poi.actions.ActionContributionItem(plugins.resourcesui.resourcesui.actions.CloseCurrentRecipeAction()))
        fileManager.appendToGroup('file-additions-begin', plugins.poi.poi.actions.GroupMarker('close-group-begin'))
        fileManager.appendToGroup('file-additions-begin', plugins.poi.poi.actions.Separator())
        fileManager.appendToGroup('file-additions-begin', plugins.poi.poi.actions.ActionContributionItem(plugins.resourcesui.resourcesui.actions.NewRecipeWizardAction(), 'new-wizard'))
        fileManager.update()
