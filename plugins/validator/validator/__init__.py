# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/validator/src/validator/__init__.py
# Compiled at: 2004-10-13 01:18:15
import wx, configparser, plugins.core.core.preferencesstore, plugins.ui.ui.preferences, lib.kernel.plugin
import plugins.ui.ui as ui
import plugins.validator.validator.messages as messages_lib
import plugins.validator.validator.agent as agent_lib
import logging, plugins.validator.validator.userinterface.preferences
logger = logging.getLogger('validator')
PLUGIN_ID = 'validator'
instance = None

def getDefault():
    global instance
    return instance


class ValidatorPlugin(lib.kernel.plugin.Plugin):
    __module__ = __name__

    def __init__(self):
        global instance
        self.paused = False
        self.validating = False
        lib.kernel.plugin.Plugin.__init__(self)
        self.preferencesStore = None
        instance = self
        self.recipeModel = None
        self.validationParticipants = []
        self.validationListeners = []
        self.valid = True
        self.errors = []
        return

    def handlePartInit(self, part):
        ui.getDefault().removeInitListener(self)

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    def addValidationParticipant(self, participant):
        if not participant in self.validationParticipants:
            self.validationParticipants.append(participant)

    def removeValidationParticipant(self, participant):
        if participant in self.validationParticipants:
            self.validationParticipants.remove(participant)

    def addValidationListener(self, listener):
        if not listener in self.validationListeners:
            self.validationListeners.append(listener)

    def removeValidationListener(self, listener):
        if listener in self.validationListeners:
            self.validationListeners.remove(listener)

    def fireValidationEvent(self, valid, errors):
        wx.CallAfter(self.internalFireValidationEvent, valid, errors)

    def internalFireValidationEvent(self, valid, errors):
        map((lambda listener: listener.validationEvent(valid, errors)), self.validationListeners)

    def startup(self, contextBundle):
        messages.init(contextBundle)
        self.setupPreferencesStore()
        ui.getDefault().addInitListener(self)
        ui.getDefault().addCloseListener(self)
        self.validatoragent = agent_lib.ValidatorAgent()

    def setupRecipe(self, oldRecipe, recipe):
        if oldRecipe is not None and self.recipeModel is not None:
            self.recipeModel.removeModifyListener(self)
            self.recipeModel = None
        if recipe is not None:
            self.recipeModel = recipe
            self.recipeModel.addModifyListener(self)
        return

    def inputChanged(self, oldInput, newInput):
        self.setupRecipe(oldInput, newInput)

    def nudge(self):
        self.validatoragent.startIfNecessary()

    def recipeModelChanged(self, event):
        self.validatoragent.startIfNecessary()

    def contextChanged(self, event):
        pass

    def closing(self):
        """fired by ui when closing"""
        self.validatoragent.markstopped()
        self.validatoragent.stop()

    def validate(self):
        global logger
        if self.paused:
            return
        if self.validating:
            return
        self.validating = True
        recipe = ui.context.getProperty('recipe')
        valid = True
        errors = []
        try:
            for participant in self.validationParticipants:
                if not participant.validate(recipe):
                    valid = False
                    errors.extend(participant.getErrors())

        except Exception as msg:
            logger.exception(msg)
            logger.error("Exception while validating! '%s'" % msg)

        self.validating = False
        self.valid = valid
        self.errors = errors
        logger.debug('Validation participants finished with %s' % valid)
        self.fireValidationEvent(valid, errors)
        self.validating = False

    def getDefaultPreferences(self):
        config = configparser.RawConfigParser()
        self.fillDefaultPreferences(config)
        return config

    def isValid(self):
        return self.valid

    def getErrors(self):
        return self.errors

    def fillDefaultPreferences(self, config):
        if not config.has_section('main'):
            config.add_section('main')
        config.set('main', 'validatordelay', '500')

    def createDefaultPreferences(self):
        config = self.preferencesStore.getPreferences()
        self.fillDefaultPreferences(config)
        self.preferencesStore.commit()

    def sanityCheck(self):
        """Checks configuration for normal values"""
        prefs = self.preferencesStore.getPreferences()
        if self.preferencesStore.isNew():
            self.createDefaultPreferences()
        try:
            if not prefs.has_section('main'):
                prefs.add_section('main')
            ivs = int(prefs.get('main', 'validatordelay'))
            if ivs < 0:
                ivs = 0
            prefs.set('main', 'validatordelay', str(ivs))
        except Exception as msg:
            logger.exception(msg)
            self.createDefaultPreferences()

        self.preferencesStore.commit()

    def setupPreferencesStore(self):
        preferencesStore = plugins.core.core.preferencesstore.PreferencesStore(PLUGIN_ID)
        self.preferencesStore = preferencesStore
        self.sanityCheck()
        preferencesStore.setDefaultPreferences(self.getDefaultPreferences())
        ui.preferences.getDefault().addPage(plugins.validator.validator.userinterface.preferences.PreferencesPage(preferencesStore))
        self.preferencesStore.addPreferencesStoreListener(self)

    def preferencesStoreChanged(self, store):
        pass

    def getPreferencesStore(self):
        return self.preferencesStore
