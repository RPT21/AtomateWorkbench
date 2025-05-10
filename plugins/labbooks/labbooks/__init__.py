# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/labbooks/src/labbooks/__init__.py
# Compiled at: 2004-12-17 20:49:55
import ui, copy, ui.context, poi.views, os, executionengine, resources.workspace, kernel.plugin, kernel.pluginmanager as PluginManager, labbooks.caching, logging, time
logger = logging.getLogger('labbooks')

def getDefault():
    return instance


class LabBooksPlugin(kernel.plugin.Plugin):
    __module__ = __name__

    def __init__(self):
        global instance
        instance = self
        kernel.plugin.Plugin.__init__(self)
        self.contextBundle = None
        self.engine = None
        self.participants = []
        self.stepLabel = 'step'
        self.stepTimeLabel = 'step time'
        self.recipeTimeLabel = 'recipe time'
        self.totalTimeLabel = 'total time'
        ui.getDefault().setSplashText('Loading Lab Books plugin ...')
        return

    def startup(self, contextBundle):
        self.contextBundle = contextBundle
        ui.getDefault().addInitListener(self)
        executionengine.getDefault().addEngineInitListener(self)

    def engineInit(self, engine):
        self.engine = engine
        self.engine.addEngineListener(self)
        self.startEventFile()
        self.createRunLog()

    def startEventFile(self):
        pass

    def createCache(self, prefix, f):
        logger.debug('Cache created: %s' % prefix)
        return labbooks.caching.CacheFile(prefix, f)

    def createRunLog(self):
        """Creates a run log file and the cache"""
        recipe = ui.context.getProperty('recipe')
        version = recipe.getUnderlyingResource()
        self.runlog = resources.workspace.getRunLog(version, int(time.time()))
        self.runlog.create()
        logger.debug('Runlog created %s' % self.runlog.getName())
        self.cacheFile = self.createCache(os.path.join(self.runlog.getLocation(), self.runlog.getName()), self.runlog.getFile())

    def createRunLogHeaders(self):
        self.runlog.appendBuffer('%s\t%s\t%s\t%s' % (self.stepLabel, self.stepTimeLabel, self.recipeTimeLabel, self.totalTimeLabel))
        self.orderedDevices = self.engine.getOrderedDevices()
        for participant in self.participants:
            headers = participant.getRunLogHeaders(self.orderedDevices)
            if headers == None:
                continue
            for header in headers:
                self.runlog.appendBuffer('\t%s' % header)

        self.runlog.writeEndOfLine()
        return

    def engineEvent(self, event):
        logger.debug('Engine event: %s' % event)
        eventType = event.getType()
        ps = copy.copy(self.participants)
        for participant in ps:
            try:
                participant.handleEngineEvent(event, self.runlog)
            except Exception, msg:
                logger.exception(msg)

        if eventType == executionengine.engine.TYPE_DEVICE_RESPONSE:
            self.writeToRunLog(event.getData())
            return
        elif eventType == executionengine.engine.TYPE_STARTING:
            self.createRunLogHeaders()
            return
        elif event.getType() == executionengine.engine.TYPE_ENDING:
            self.endRunLog()
            self.engine.removeEngineListener(self)

    def writeToRunLog(self, envelope):
        stepIndex = str(envelope.getStepIndex() + 1)
        stepTime = str(envelope.getStepTime())
        recipeTime = str(envelope.getRecipeTime())
        totalTime = str(envelope.getTotalTime())
        self.cacheFile.markSecond(envelope.getTotalTime())
        self.runlog.appendBuffer('%s\t%s\t%s\t%s' % (stepIndex, stepTime, recipeTime, totalTime))
        ps = copy.copy(self.participants)
        for participant in ps:
            participant.writeToRunLog(envelope, self.runlog)

        self.runlog.writeEndOfLine()

    def endRunLog(self):
        self.runlog.end()
        self.cacheFile.close()

    def writeEventEntryToFile(self, event):
        eventType = str(event.getType())
        stepIndex = str(self.engine.getCurrentStepIndex())
        loopCount = str(self.engine.getCurrentLoopCount())
        stepTime = str(self.engine.getStepTime())
        recipeTime = str(self.engine.getRecipeTime())
        totalTime = str(self.engine.getTotalTime())
        if eventType == executionengine.engine.TYPE_ENTERING_STEP:
            currentStep = '\t' + repr(self.engine.getCurrentStep())
        else:
            currentStep = ''

    def handlePartInit(self, part):
        ui.getDefault().removeInitListener(self)

    def createView(self, viewID, parent):
        pass

    def registerDeviceParticipant(self, participant):
        self.participants.append(participant)

    def deregisterParticipant(self, participant):
        if participant in self.participants:
            self.participants.remove(participant)

    def disposeDeviceParticipants(self):
        del self.participants[0:]


class RunLogParticipant(object):
    __module__ = __name__

    def __init__(self):
        pass

    def createRunLogHeaders(self, devices):
        pass

    def handleEngineEvent(self, event, runlogFile):
        pass

    def writeToRunLog(self, event, runlogFile):
        pass
