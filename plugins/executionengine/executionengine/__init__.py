# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/executionengine/src/executionengine/__init__.py
# Compiled at: 2004-12-13 23:17:23
import plugins.ui.ui, wx, logging, copy, plugins.core.core.preferencesstore, plugins.ui.ui.context
import plugins.executionengine.executionengine.messages as messages, plugins.executionengine.executionengine.actions
import plugins.executionengine.executionengine.engine, plugins.executionengine.executionengine.perspective as perspective
import plugins.executionengine.executionengine.preferences
import plugins.executionengine.executionengine.userinterface.eventviewer, plugins.poi.poi.actions.menumanager
import plugins.executionengine.executionengine.images as images
import plugins.ui.ui.preferences, lib.kernel.plugin
import plugins.executionengine.executionengine.userinterface.purgemanagerviewer
import plugins.executionengine.executionengine.userinterface.engineiniterrordialog, plugins.validator.validator
import plugins.executionengine.executionengine.purgemanager as purgemanager
import plugins.ui.ui as ui, plugins.poi.poi as poi
import plugins.executionengine.executionengine.actions as execution_actions

logger = logging.getLogger('executionengine')
DEFAULT_RESOLUTION = 0.2
PLUGIN_ID = 'executionengine'

def getDefault():
    global instance
    return instance


class ExecutionEnginePlugin(lib.kernel.plugin.Plugin):
    __module__ = __name__

    def __init__(self):
        global instance
        lib.kernel.plugin.Plugin.__init__(self)
        self.contextBundle = None
        plugins.ui.ui.getDefault().addCloseVetoListener(self)
        plugins.ui.ui.getDefault().addCloseListener(self)
        self.engine = None
        instance = self
        self.initErrors = []
        self.engineInitListeners = []
        self.participantFactories = {}
        self.enablementStateParticipants = []
        plugins.ui.ui.getDefault().setSplashText('Loading execution plugin ...')
        return

    def closing(self):
        self.perspective.dispose()
        return True

    def closeVeto(self):
        if len(plugins.executionengine.executionengine.purgemanager.getPurgeWorkers()) > 0:
            logger.debug('Vetoing')
            return True
        if self.engine is None:
            return False
        return self.engine.isRunning()

    def addEngineInitListener(self, listener):
        if not listener in self.engineInitListeners:
            self.engineInitListeners.append(listener)

    def removeEngineInitListener(self, listener):
        if listener in self.engineInitListeners:
            self.engineInitListeners.remove(listener)

    def fireEngineInit(self, engine):
        plugins.validator.validator.getDefault().pause()
        list(map((lambda listener: listener.engineInit(engine)), self.engineInitListeners))

    def getEngine(self):
        return self.engine

    def clearEngine(self):
        logger.debug('Clear engine')
        plugins.ui.ui.context.setProperty('can-edit', True)
        plugins.ui.ui.context.setProperty('execution', 'stopped')
        errors = self.engine.getErrors()
        plugins.validator.validator.getDefault().resume()
        if len(errors):
            wx.CallAfter(self.showErrorsDialog, errors)
            return
        self.engine.removeEngineListener(self)
        self.engine = None
        return

    def showErrorsDialog(self, errors):
        dlg = plugins.executionengine.executionengine.userinterface.engineiniterrordialog.EngineInitErrorDialog(errors)
        dlg.ShowModal()
        del self.engine
        self.engine = None
        return

    def registerRecipeParticipantFactory(self, deviceID, factory):
        self.participantFactories[deviceID] = factory

    def getRecipeParticipantFactory(self, deviceID):
        if deviceID not in self.participantFactories:
            return None
        return self.participantFactories[deviceID]

    def createEngine(self):
        self.clearHardwareInitErrors()
        res = DEFAULT_RESOLUTION
        try:
            res = float(self.preferencesStore.getPreferences().get('execution', 'dataResolution'))
            logger.debug('Setting data resolution to %f' % res)
        except Exception as msg:
            logger.error('Unable to get data resolution, setting to %f second' % DEFAULT_RESOLUTION)
            logger.exception(msg)

        self.engine = plugins.executionengine.executionengine.engine.Engine()
        self.engine.setDataResolution(res)
        self.engine.addEngineListener(self)
        self.fireEngineInit(self.engine)
        return self.engine

    def clearHardwareInitErrors(self):
        del self.initErrors[0:]

    def engineEvent(self, event):
        if event.getType() == plugins.executionengine.executionengine.engine.TYPE_ENDING:
            logger.debug('Going to call clear engine for: %s' % event)
            self.clearEngine()
        if event.getType() == plugins.executionengine.executionengine.engine.TYPE_HARDWARE_INIT_ERROR:
            self.addHardwareInitError(event)

    def addHardwareInitError(self, event):
        logger.debug('Adding hardware init error: %s' % event)
        self.initErrors.append(event)

    def startup(self, contextBundle):
        global PLUGIN_ID
        self.contextBundle = contextBundle
        messages.init(contextBundle)
        images.init(contextBundle)
        plugins.ui.ui.getDefault().addInitListener(self)
        preferencesStore = plugins.core.core.preferencesstore.PreferencesStore(PLUGIN_ID)
        self.preferencesStore = preferencesStore
        plugins.ui.ui.preferences.getDefault().addPage(plugins.executionengine.executionengine.preferences.PreferencesPage(preferencesStore))
        plugins.validator.validator.getDefault().addValidationListener(self)
        purgemanager.addListener(self)

    def getPreferencesStore(self):
        return self.preferencesStore

    def workerRemoved(self, worker):
        plugins.executionengine.executionengine.actions.updateActions()

    def workerAdded(self, worker):
        pass

    def purgeStart(self, worker):
        plugins.executionengine.executionengine.actions.updateActions()

    def purgeEnd(self, worker):
        pass

    def purgePause(self, worker):
        pass

    def validationEvent(self, valid, errors):
        wx.CallAfter(self.internalValidationEvent, valid, errors)

    def internalValidationEvent(self, valid, errors):
        plugins.executionengine.executionengine.actions.isValid = valid
        plugins.executionengine.executionengine.actions.updateActions()

    def handlePartInit(self, part):
        plugins.ui.ui.getDefault().removeInitListener(self)
        runManager = self.createRunMenuManager()
        plugins.ui.ui.getDefault().getMenuManager().appendToGroup('mb-additions-begin', runManager)
        plugins.ui.ui.getDefault().getMenuManager().update()
        plugins.ui.ui.getDefault().getToolBarManager().update(True)
        plugins.executionengine.executionengine.userinterface.purgemanagerviewer.init()
        self.perspective = perspective.Perspective(plugins.ui.ui.getDefault().getMainFrame().getStage())
        plugins.ui.ui.getDefault().getMainFrame().addPerspective('run', self.perspective)

    def addEnablementStateParticipant(self, participant):
        if not participant in self.enablementStateParticipants:
            self.enablementStateParticipants.append(participant)

    def removeEnablementStateParticipant(self, participant):
        if participant in self.enablementStateParticipants:
            self.enablementStateParticipants.remove(participant)

    def fireEnablementState(self):
        participants = copy.copy(self.enablementStateParticipants)
        if self.engine is not None:
            return
        for participant in participants:
            if not participant.canEnable():
                logger.debug('Participant disable run actions: %s' % participant)
                plugins.executionengine.executionengine.actions.enablementState = False
                return

        plugins.executionengine.executionengine.actions.enablementState = True
        return

    def updateEnablementState(self):
        plugins.executionengine.executionengine.actions.updateActions()

    def createRunMenuManager(self):
        plugins.executionengine.executionengine.actions.createActions()
        ui.context.addContextChangeListener(plugins.executionengine.executionengine.actions)
        mng = poi.actions.menumanager.MenuManager(messages.get('mainmenu.run'), 'atm.run')
        tbm = ui.getDefault().getToolBarManager()
        tbm.addItem(poi.actions.Separator())
        tbm.addItem(poi.actions.ActionContributionItem(execution_actions.runAction))
        tbm.addItem(poi.actions.ActionContributionItem(execution_actions.pauseAction))
        tbm.addItem(poi.actions.ActionContributionItem(execution_actions.resumeAction))
        tbm.addItem(poi.actions.ActionContributionItem(execution_actions.advanceAction))
        tbm.addItem(poi.actions.ActionContributionItem(execution_actions.abortAction))
        tbm.addItem(poi.actions.ActionContributionItem(execution_actions.stopPurgeAction))
        mng.addItem(poi.actions.ActionContributionItem(execution_actions.runAction))
        mng.addItem(poi.actions.ActionContributionItem(execution_actions.pauseAction))
        mng.addItem(poi.actions.ActionContributionItem(execution_actions.resumeAction))
        mng.addItem(poi.actions.ActionContributionItem(execution_actions.advanceAction))
        mng.addItem(poi.actions.ActionContributionItem(execution_actions.abortAction))
        mng.addItem(poi.actions.Separator('run-additions-begin'))
        mng.addItem(poi.actions.GroupMarker('run-additions-end'))
        return mng
