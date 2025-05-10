# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/resources/src/resources/__init__.py
# Compiled at: 2004-11-02 04:11:02
PLUGIN_ID = 'resources'
import stat, os, sys, shutil, ConfigParser, core, core.preferencesstore, kernel, kernel.plugin, kernel.pluginmanager as PluginManager, resources.utils, resources
default = None

def getDefault():
    global default
    return default


class Resource(object):
    __module__ = __name__

    def __init__(self, name):
        self.name = name
        self.location = None
        self.handle = None
        self.parent = None
        return

    def getParent(self):
        return self.parent

    def equals(self, resource):
        if id(self) == id(resource):
            return True
        return self.location == resource.location and self.getName() == resource.getName()

    def remove(self):
        pass

    def internal_setParent(self, parent):
        self.parent = parent

    def create(self):
        self.handle = os.stat(self.location)

    def load(self):
        self.handle = os.stat(self.location)

    def getHandle(self):
        """Not meant to be called by clients"""
        return self.handle

    def getName(self):
        return self.name

    def getLocation(self):
        return self.location

    def setLocation(self, location):
        self.location = location

    def getCreationDate(self):
        return self.handle[stat.ST_CTIME]

    def getModificationDate(self):
        return self.handle[stat.ST_MTIME]

    def isShared(self):
        return self.location.find(resources.getDefault().getWorkspace().getSharedLocation()) >= 0


import resources.workspace as workspace

class ResourcesPlugin(kernel.plugin.Plugin):
    __module__ = __name__

    def __init__(self):
        global default
        kernel.plugin.Plugin.__init__(self)
        default = self
        self.workspace = None
        return

    def startup(self, contextBundle):
        self.setupPreferencesStore()
        workspace.init()

    def getDefaultPreferences(self):
        config = ConfigParser.SafeConfigParser()
        self.fillDefaultPreferences(config)
        return config

    def fillDefaultPreferences(self, config):
        config.add_section('workspace')
        config.set('workspace', 'localworkspace.path', resources.utils.getUsersDirectory())

    def createDefaultPreferences(self):
        config = self.preferencesStore.getPreferences()
        self.fillDefaultPreferences(config)
        self.preferencesStore.commit()

    def setupPreferencesStore(self):
        preferencesStore = core.preferencesstore.PreferencesStore(PLUGIN_ID)
        self.preferencesStore = preferencesStore
        self.sanityCheck()
        preferencesStore.setDefaultPreferences(self.getDefaultPreferences())
        self.preferencesStore.addPreferencesStoreListener(self)
        self.prepareWorkspace()

    def sanityCheck(self):
        """Checks configuration for normal values"""
        prefs = self.preferencesStore.getPreferences()
        if self.preferencesStore.isNew():
            self.createDefaultPreferences()
        try:
            if not prefs.has_section('workspace'):
                self.createDefaultPreferences()
        except Exception, msg:
            logger.exception(msg)

        self.preferencesStore.commit()

    def prepareWorkspace(self):
        prefs = self.preferencesStore.getPreferences()
        path = prefs.get('workspace', 'localworkspace.path')
        resources.workspace.setLocalPrefix(path)

    def preferencesStoreChanged(self, store):
        self.prepareWorkspace()

    def getPreferencesStore(self):
        return self.preferencesStore

    def getWorkspace(self):
        return workspace


import resources.workspace
