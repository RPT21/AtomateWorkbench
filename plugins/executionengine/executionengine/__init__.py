# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/executionengine/src/executionengine/__init__.py
# Compiled at: 2004-12-13 23:17:23
import ui, wx, logging, copy, core.preferencesstore, ui.context, ui.preferences, kernel.plugin, kernel.pluginmanager as PluginManager, executionengine.messages as messages, executionengine.actions, executionengine.engine, executionengine.perspective, executionengine.userinterface.eventviewer, poi.actions.menumanager, executionengine.images as images, executionengine.preferences, executionengine.userinterface.purgemanagerviewer, executionengine.userinterface.engineiniterrordialog, validator, purgemanager
logger = logging.getLogger('executionengine')
instance = None
DEFAULT_RESOLUTION = 0.2
PLUGIN_ID = 'executionengine'

def getDefault():
    global instance
    return instance


class ExecutionEnginePlugin(kernel.plugin.Plugin):
    __module__ = __name__

    def __init__(self):
        global instance
        kernel.plugin.Plugin.__init__(self)
        self.contextBundle = None
        ui.getDefault().addCloseVetoListener(self)
        ui.getDefault().addCloseListener(self)
        self.engine = None
        instance = self
        self.initErrors = []
        self.engineInitListeners = []
        self.participantFactories = {}
        self.enablementStateParticipants = []
        ui.getDefault().setSplashText('Loading execution plugin ...')
        return

    def closing(self):
        self.perspective.dispose()
        return True

    def closeVeto(self):
        if len(executionengine.purgemanager.getPurgeWorkers()) > 0:
            logger.debug('Vetoing')
            return True
        if self.engine is None:
            return False
        return self.engine.isRunning()
        return

    def addEngineInitListener(self, listener):
        if not listener in self.engineInitListeners:
            self.engineInitListeners.append(listener)

    def removeEngineInitListener(self, listener):
        if listener in self.engineInitListeners:
            self.engineInitListeners.remove(listener)

    def fireEngineInit(self, engine):
        validator.getDefault().pause()
        map((lambda listener: listener.engineInit(engine)), self.engineInitListeners)

    def getEngine(self):
        return self.engine

    def clearEngine(self):
        logger.debug('Clear engine')
        ui.context.setProperty('can-edit', True)
        ui.context.setProperty('execution', 'stopped')
        errors = self.engine.getErrors()
        validator.getDefault().resume()
        if len(errors):
            wx.CallAfter(self.showErrorsDialog, errors)
            return
        self.engine.removeEngineListener(self)
        self.engine = None
        return

    def showErrorsDialog(self, errors):
        dlg = executionengine.userinterface.engineiniterrordialog.EngineInitErrorDialog(errors)
        dlg.ShowModal()
        del self.engine
        self.engine = None
        return

    def registerRecipeParticipantFactory(self, deviceID, factory):
        self.participantFactories[deviceID] = factory

    def getRecipeParticipantFactory(self, deviceID):
        if not self.participantFactories.has_key(deviceID):
            return None
        return self.participantFactories[deviceID]
        return

    def createEngine(self):
        self.clearHardwareInitErrors()
        res = DEFAULT_RESOLUTION
        try:
            res = float(self.preferencesStore.getPreferences().get('execution', 'dataResolution'))
            logger.debug('Setting data resolution to %f' % res)
        except Exception, msg:
            logger.error('Unable to get data resolution, setting to %f second' % DEFAULT_RESOLUTION)
            logger.exception(msg)

        self.engine = executionengine.engine.Engine()
        self.engine.setDataResolution(res)
        self.engine.addEngineListener(self)
        self.fireEngineInit(self.engine)
        return self.engine

    def clearHardwareInitErrors(self):
        del self.initErrors[0:]

    def engineEvent(self, event):
        if event.getType() == executionengine.engine.TYPE_ENDING:
            logger.debug('Going to call clear engine for: %s' % event)
            self.clearEngine()
        if event.getType() == executionengine.engine.TYPE_HARDWARE_INIT_ERROR:
            self.addHardwareInitError(event)

    def addHardwareInitError(self, event):
        logger.debug('Adding hardware init error: %s' % event)
        self.initErrors.append(event)

    def startup(self, contextBundle):
        global PLUGIN_ID
        self.contextBundle = contextBundle
        messages.init(contextBundle)
        images.init(contextBundle)
        ui.getDefault().addInitListener(self)
        preferencesStore = core.preferencesstore.PreferencesStore(PLUGIN_ID)
        self.preferencesStore = preferencesStore
        ui.preferences.getDefault().addPage(executionengine.preferences.PreferencesPage(preferencesStore))
        validator.getDefault().addValidationListener(self)
        purgemanager.addListener(self)

    def getPreferencesStore(self):
        return self.preferencesStore

    def workerRemoved(self, worker):
        executionengine.actions.updateActions()

    def workerAdded(self, worker):
        pass

    def purgeStart(self, worker):
        executionengine.actions.updateActions()

    def purgeEnd(self, worker):
        pass

    def purgePause(self, worker):
        pass

    def validationEvent(self, valid, errors):
        wx.CallAfter(self.internalValidationEvent, valid, errors)

    def internalValidationEvent(self, valid, errors):
        executionengine.actions.isValid = valid
        executionengine.actions.updateActions()

    def handlePartInit(self, part):
        ui.getDefault().removeInitListener(self)
        runManager = self.createRunMenuManager()
        ui.getDefault().getMenuManager().appendToGroup('mb-additions-begin', runManager)
        ui.getDefault().getMenuManager().update()
        ui.getDefault().getToolBarManager().update(True)
        executionengine.userinterface.purgemanagerviewer.init()
        self.perspective = executionengine.perspective.Perspective(ui.getDefault().getMainFrame().getStage())
        ui.getDefault().getMainFrame().addPerspective('run', self.perspective)

    def addEnablementStateParticipant(self, participant):
        if not participant in self.enablementStateParticipants:
            self.enablementStateParticipants.append(participant)

    def removeEnablementStateParticipant(self, participant):
        if participant in self.enablementStateParticipants:
            self.enablementStateParticipants.remove(partipant)

    def fireEnablementState(self):
        participants = copy.copy(self.enablementStateParticipants)
        if self.engine is not None:
            return
        for participant in participants:
            if not participant.canEnable():
                logger.debug('Participant disable run actions: %s' % participant)
                executionengine.actions.enablementState = False
                return

        executionengine.actions.enablementState = True
        return

    def updateEnablementState(self):
        executionengine.actions.updateActions()

    def createRunMenuManager(self):
        executionengine.actions.createActions()
        ui.context.addContextChangeListener(executionengine.actions)
        mng = poi.actions.menumanager.MenuManager(messages.get('mainmenu.run'), 'atm.run')
        tbm = ui.getDefault().getToolBarManager()
        tbm.addItem(poi.actions.Separator())
        tbm.addItem(poi.actions.ActionContributionItem(executionengine.actions.runAction))
        tbm.addItem(poi.actions.ActionContributionItem(executionengine.actions.pauseAction))
        tbm.addItem(poi.actions.ActionContributionItem(executionengine.actions.resumeAction))
        tbm.addItem(poi.actions.ActionContributionItem(executionengine.actions.advanceAction))
        tbm.addItem(poi.actions.ActionContributionItem(executionengine.actions.abortAction))
        tbm.addItem(poi.actions.ActionContributionItem(executionengine.actions.stopPurgeAction))
        mng.addItem(poi.actions.ActionContributionItem(executionengine.actions.runAction))
        mng.addItem(poi.actions.ActionContributionItem(executionengine.actions.pauseAction))
        mng.addItem(poi.actions.ActionContributionItem(executionengine.actions.resumeAction))
        mng.addItem(poi.actions.ActionContributionItem(executionengine.actions.advanceAction))
        mng.addItem(poi.actions.ActionContributionItem(executionengine.actions.abortAction))
        mng.addItem(poi.actions.Separator('run-additions-begin'))
        mng.addItem(poi.actions.GroupMarker('run-additions-end'))
        return mng
