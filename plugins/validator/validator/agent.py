# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/validator/src/validator/agent.py
# Compiled at: 2004-09-16 00:20:16
import threading, plugins.core.core.utils
import plugins.validator.validator.utils, logging, plugins.ui.ui.context
import plugins.validator.validator.constants as validator_constants
import plugins.validator.validator.__init__ as validator
import plugins.ui.ui as ui

logger = logging.getLogger('validator')

class ValidatorAgent(object):
    __module__ = __name__

    def __init__(self):
        self.closing = False
        self.running = False
        self.timer = None
        self.interval = 0
        self.getPreferencesStore().addPreferencesStoreListener(self)
        self.updateConfiguration()
        plugins.ui.ui.context.addContextChangeListener(self)
        return

    def markstopped(self):
        self.closing = True

    def perform(self):
        self.validate()

    def validate(self):
        self.running = False
        validator.getDefault().validate()

    def stop(self):
        if self.running:
            self.timer.cancel()
            self.running = False

    def contextChanged(self, event):
        if event.getKey() != 'can-edit':
            return
        self.stopIfNecessary(event.getNewValue())
        self.startIfNecessary()

    def preferencesStoreChanged(self, store):
        if self.running:
            self.stop()
        self.updateConfiguration()

    def getPreferencesStore(self):
        return validator.getDefault().getPreferencesStore()

    def stopIfNecessary(self, canedit):
        if self.running:
            self.running = False
            self.timer.cancel()

    def startIfNecessary(self):
        """Checks if the editor is active in the view, then figures out if it should start saving"""
        if self.closing:
            return
        if self.interval == 0:
            return
        if not ui.context.getProperty('can-edit'):
            return
        if self.running:
            return
        logger.debug('Starting validation at %f' % (self.interval / 1000.0))
        self.running = True
        self.timer = threading.Timer(self.interval / 1000.0, self.perform)
        self.timer.name = 'ValidatorAgentTimer'
        self.timer.start()

    def updateConfiguration(self):
        store = self.getPreferencesStore()
        try:
            prefs = store.getPreferences()
            self.interval = int(prefs.get('main', validator_constants.TAG_VALIDATORDELAY))
            self.startIfNecessary()
        except Exception as msg:
            logger.exception(msg)
