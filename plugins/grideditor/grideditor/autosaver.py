# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/grideditor/src/grideditor/autosaver.py
# Compiled at: 2004-08-26 20:56:44
import core.utils, grideditor.utils, logging, ui.context, threading, time
import plugins.grideditor.grideditor as grideditor
import plugins.grideditor.grideditor.constants as constants
logger = logging.getLogger('grideditor.autosaver')

class AutoSaver(object):
    __module__ = __name__

    def __init__(self):
        self.getPreferencesStore().addPreferencesStoreListener(self)
        self.running = False
        self.interval = 0
        self.updateConfiguration()
        ui.context.addContextChangeListener(self)
        self.startIfNecessary()
        self.timer = None
        self.called = True
        return

    def perform(self):
        self.save()

    def save(self):
        logger.debug('auto-saving')
        grideditor.utils.saveCurrentRecipe()
        self.called = True
        self.startTimer()

    def startTimer(self):
        if self.interval == 0:
            return
        if self.called:
            del self.timer
            self.timer = threading.Timer(self.interval, self.save)
            self.timer.setName('AutoSaverTimer')
            self.timer.start()
            self.called = False

    def stop(self):
        self.stopTimer()

    def stopTimer(self):
        if self.timer is not None and self.timer.isAlive():
            self.called = True
            self.timer.cancel()
        return

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
        return grideditor.getActiveEditor().getPreferencesStore()

    def stopIfNecessary(self, canedit):
        self.stopTimer()

    def startIfNecessary(self):
        """Checks if the editor is active in the view, then figures out if it should start saving"""
        if self.interval == 0:
            return
        if not ui.context.getProperty('can-edit'):
            return
        self.startTimer()

    def updateConfiguration(self):
        store = self.getPreferencesStore()
        try:
            prefs = store.getPreferences()
            self.interval = int(prefs.get('editor', constants.TAG_AUTOSAVEINTERVAL))
            self.startIfNecessary()
        except Exception as msg:
            logger.exception(msg)
