# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/core/src/core/preferencesstore.py
# Compiled at: 2004-08-04 10:44:13
import ConfigParser, kernel, os
PREFERENCES_FILENAME = '.preferences'

class PreferencesStore(object):
    __module__ = __name__

    def __init__(self, pluginid):
        self.pluginid = pluginid
        self.configurationStoreListeners = []
        self.config = None
        self.defaults = None
        self.new = False
        return

    def isNew(self):
        return self.new

    def setDefaultPreferences(self, prefs):
        self.defaults = prefs

    def getDefaultPreferences(self):
        return self.defaults

    def getConfigurationFileName(self):
        global PREFERENCES_FILENAME
        return os.path.join(kernel.getPluginWorkspacePath(self.pluginid), PREFERENCES_FILENAME)

    def addPreferencesStoreListener(self, listener):
        if not listener in self.configurationStoreListeners:
            self.configurationStoreListeners.append(listener)

    def removePreferencesStoreListener(self, listener):
        if listener in self.configurationStoreListeners:
            self.configurationStoreListener.remove(listener)

    def firePreferencesStoreChanged(self):
        for listener in self.configurationStoreListeners:
            listener.preferencesStoreChanged(self)

    def commit(self):
        try:
            filename = self.getConfigurationFileName()
            f = open(filename, 'w')
            self.config.write(f)
            f.close()
        except Exception, msg:
            raise Exception("Unable to commit Preferences '%s':'%s'" % (msg, self.getConfigurationFileName()))

        self.firePreferencesStoreChanged()

    def openConfig(self):
        try:
            filename = self.getConfigurationFileName()
            if not os.path.exists(filename):
                open(filename, 'w').close()
                self.new = True
            f = open(filename, 'r')
            self.config = ConfigParser.SafeConfigParser()
            self.config.readfp(f)
            f.close()
        except Exception, msg:
            raise Exception("Unable to open Preferences '%s':'%s'" % (msg, self.getConfigurationFileName()))

    def getPreferences(self):
        if self.config is None:
            self.openConfig()
        return self.config
        return
