# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/executionengine/src/executionengine/engine.py
# Compiled at: 2004-12-07 11:22:43
import plugins.ui.ui, wx, plugins.executionengine.executionengine.userinterface, plugins.executionengine.executionengine.userinterface.hwiniterrorsdialog
import plugins.core.core.conditional, plugins.hardware.hardware.hardwaremanager, threading, copy, time, logging, plugins.poi.poi.operation, plugins.poi.poi.dialogs.progress
logger = logging.getLogger('executionengine')
TYPE_STARTING = 'type-starting'
TYPE_ENDING = 'type-ending'
TYPE_ENTERING_STEP = 'type-entering-step'
TYPE_EXITING_STEP = 'type-exiting-step'
TYPE_CHECKING_CONDITIONALS = 'type-checking-conditionals'
TYPE_SETTING_STEP_GOALS = 'type-setting-step-goals'
TYPE_CONDITIONAL_EXECUTING = 'type-conditional-executing'
TYPE_HOLD = 'type-hold'
TYPE_ADVANCE = 'type-advance'
TYPE_PAUSE = 'type-pause'
TYPE_RESUME = 'type-resume'
TYPE_ABORTING = 'type-aborting'
TYPE_HARDWARE_INIT_ERROR = 'type-hardware-init-error'
TYPE_HARDWARE_INIT_START = 'type-hardware-init-start'
TYPE_HARDWARE_INIT_END = 'type-hardware-init-end'
TYPE_EXECUTION_ERROR = 'type-execution-error'
TYPE_DEVICE_RESPONSE = 'type-device-response'
TYPE2TEXT = {TYPE_STARTING: 'STARTING', TYPE_ENDING: 'ENDING', TYPE_ENTERING_STEP: 'ENTERING STEP', TYPE_EXITING_STEP: 'EXITING STEP', TYPE_CHECKING_CONDITIONALS: 'CHECKING CONDITIONALS', TYPE_SETTING_STEP_GOALS: 'SETTING STEP GOALS', TYPE_HOLD: 'HOLD', TYPE_ADVANCE: 'ADVANCE', TYPE_PAUSE: 'PAUSE', TYPE_RESUME: 'RESUME', TYPE_ABORTING: 'ABORTING', TYPE_HARDWARE_INIT_ERROR: 'HARDWARE INIT ERROR', TYPE_HARDWARE_INIT_START: 'HARDWARE INIT START', TYPE_HARDWARE_INIT_END: 'HARDWARE INIT END', TYPE_EXECUTION_ERROR: 'EXECUTION ERROR', TYPE_DEVICE_RESPONSE: 'DEVICE REPLIES', TYPE_CONDITIONAL_EXECUTING: 'CONDITIONAL_EXECUTING'}

class DeviceResponse(object):
    __module__ = __name__

    def __init__(self, device):
        self.device = device

    def getDevice(self):
        return self.device


class DeviceRepliesEnvelope(object):
    __module__ = __name__

    def __init__(self, stepIndex, loopCount, recipeTime, stepTime, totalTime):
        self.stepIndex = stepIndex
        self.loopCount = loopCount
        self.recipeTime = recipeTime
        self.stepTime = stepTime
        self.totalTime = totalTime
        self.replies = {}

    def getStepIndex(self):
        return self.stepIndex

    def getLoopCount(self):
        return self.loopCount

    def getRecipeTime(self):
        return self.recipeTime

    def getStepTime(self):
        return self.stepTime

    def getTotalTime(self):
        return self.totalTime

    def addReply(self, device, reply):
        self.replies[device] = reply

    def getReplies(self):
        return self.replies.values()

    def getReply(self, device):
        if not self.replies.has_key(device):
            raise LookupError("No reply for device '%s' in envelope" % device)
        return self.replies[device]

    def getResponseByType(self, type):

        def typefilter(reply):
            return reply.getDevice().getType() == type

        return filter(typefilter, self.getReplies())

    def dispose(self):
        self.replies.clear()

    def __repr__(self):
        return "[DeviceRepliesEnvelope replies='%d']" % len(self.replies)


class EngineEvent(object):
    __module__ = __name__

    def __init__(self, source, etype):
        self.source = source
        self.etype = etype
        self.data = None
        return

    def setData(self, data):
        self.data = data

    def getData(self):
        return self.data

    def getSource(self):
        return self.source

    def getType(self):
        return self.etype

    def __repr__(self):
        return "[EngineEvent type='%s'/data='%s']" % (self.getType(), self.getData())


class Engine(threading.Thread):
    __module__ = __name__

    def __init__(self):
        threading.Thread.__init__(self)
        self.throttle = 0.2
        self.forceEnd = False
        self.running = False
        self.recipe = None
        self.engineListeners = []
        self.interrupted = False
        self.currentLoops = 0
        self.lock = threading.Condition()
        self.currentStep = None
        self.forceAdvance = False
        self.hold = False
        self.manualHold = False
        self.stepStartTime = 0
        self.stepTime = 0
        self.recipeTime = 0
        self.totalTime = 0
        self.loopStartTime = 0
        self.errors = []
        self.recipeParticipants = {}
        self.currentStepIndex = 0
        self.loopStartStep = None
        self.loopStartStepIndex = -1
        self.cleaning = False
        self.stepStack = []
        return

    def setDataResolution(self, resolution):
        self.throttle = resolution

    def pushStep(self, step, stepIndex):
        global logger
        logger.debug('Pushing step onto loop stack. Current length: %d' % len(self.stepStack))
        self.stepStack.append([step, stepIndex, 0])

    def popStep(self):
        logger.debug('Popping from stack')
        del self.stepStack[len(self.stepStack) - 1]
        logger.debug('\tNew stack length %d' % len(self.stepStack))

    def peek(self):
        """Return a reference to the step at the top of the stack"""
        if len(self.stepStack) == 0:
            raise LookupError('The stack is empty')
        return self.stepStack[len(self.stepStack) - 1]

    def getCurrentStepIndex(self):
        return self.currentStepIndex

    def getCurrentStep(self):
        return self.currentStep

    def hasErrors(self):
        return len(self.errors) > 0

    def getErrors(self):
        return self.errors

    def addError(self, error):
        self.errors.append(error)

    def clearErrors(self):
        del self.errors[0:]

    def getRecipeTime(self):
        return self.recipeTime

    def getStepTime(self):
        return self.stepTime

    def getTotalTime(self):
        return self.totalTime

    def fireEngineEvent(self, etype, data=None):
        wx.CallAfter(self.internalFireEngineEvent, etype, data)

    def internalFireEngineEvent(self, etype, data):
        event = EngineEvent(self, etype)
        event.setData(data)
        listeners = copy.copy(self.engineListeners)
        map((lambda listener: listener.engineEvent(event)), listeners)

    def addEngineListener(self, listener):
        if not listener in self.engineListeners:
            self.engineListeners.append(listener)

    def removeEngineListener(self, listener):
        if listener in self.engineListeners:
            self.engineListeners.remove(listener)

    def getOrderedDevices(self):
        return self.recipe.getDevices()

    def setRecipe(self, recipeItem):
        """This method expects a parsed recipe"""
        self.recipe = recipeItem

    def getCurrentLoopCount(self):
        return self.currentLoops

    def debugPrintState(self):
        lit = -1
        if self.isInLoopingInterval():
            lit = self.currentLoops
        logger.debug("EXECSTEP: Current Step Index: '%d'/In Loop: '%s'/Iterations: '%d'/Duration: '%s'/Delta: '%s'" % (self.currentStepIndex, self.isInLoopingInterval(), lit, self.currentStep.getDuration(), self.getStepTime()))

    def markStepLoopStart(self):
        self.loopStartTime = time.time()
        self.debugPrintState()

    def prepareRun(self):
        self.clearErrors()
        self.fireEngineEvent(TYPE_STARTING)
        self.currentStep = self.recipe.getStep(0)

    def switchContext(self, stateName):
        ui.context.setProperty('execution', stateName)

    def run(self):
        logger.debug('preparing run')
        self.prepareRun()
        try:
            logger.debug('preparing devices')
            self.prepareDevices()
        except Exception as msg:
            logger.exception(msg)
            logger.error("* ERROR: Cannot initialize devices: '%s'" % msg)
            self.internalCleanup()
            return

        self.running = True
        self.recipeTime = 0
        self.switchContext('running')
        try:
            while True:
                proceed = self.prepareStep()
                if not proceed:
                    self.internalCleanup()
                    return
                self.stepTime = 0
                self.fireEngineEvent(TYPE_ENTERING_STEP)
                try:
                    self.setStepGoals()
                except Exception as msg:
                    logger.exception(msg)
                    self.internalErrorAbort('Error while setting step goals %s' % msg)
                    return

                while True:
                    stthen = time.time()
                    self.markStepLoopStart()
                    hwrStart = time.time()
                    self.lock.acquire()
                    logger.debug('--acquire--')
                    if self.interrupted:
                        logger.debug('self.interrupted')
                        self.internalCleanup()
                        self.interrupted = False
                        self.lock.notify()
                        self.lock.release()
                        return
                    try:
                        self.submitHardwareRequests()
                    except Exception as msg:
                        logger.exception(msg)
                        print("* ERROR: Could not submit request for hardware status at step '%s':'%s'" % (self.currentStep, msg))
                        self.lock.release()
                        self.internalErrorAbort('Error while submitting hardware requests %s' % msg)
                        return

                    hwrEnd = time.time()
                    delta = self.throttle - (hwrEnd - hwrStart)
                    logger.debug('Delta was %f for throttle %f' % (delta, self.throttle))
                    if delta > 0:
                        logger.debug('Will wait for %f for delta' % delta)
                        self.lock.wait(delta)
                    if self.interrupted:
                        logger.debug('run: was interrupted during send.  aborting')
                        self.lock.notify()
                        self.lock.release()
                        logger.debug('run: released')
                        self.internalErrorAbort('Internal interruption')
                        return
                    try:
                        envelope = self.gatherDeviceReplies()
                    except Exception as msg:
                        logger.exception(msg)
                        self.lock.release()
                        self.internalErrorAbort('Error while gathering device replies %s' % msg)
                        return

                    self.fireStepData(envelope)
                    if not self.manualHold:
                        sa = self.checkConditions(envelope)
                        logger.debug("Conditional action: '%s'" % str(sa))
                        if sa is not None:
                            (suite, action) = sa
                            action[0].execute(self)
                            self.fireEngineEvent(TYPE_CONDITIONAL_EXECUTING, sa)
                        else:
                            self.hold = False
                    canAdvance = self.canAdvance()
                    if canAdvance:
                        logger.debug('Prepping advance to next step')
                        nextStepIndex = self.getNextStepIndex()
                        self.fireEngineEvent(TYPE_EXITING_STEP)
                    if self.atEnd():
                        logger.debug('End of recipe')
                        self.lock.release()
                        self.internalCleanup()
                        return
                    if canAdvance:
                        logger.debug('Advancing...')
                        self.advanceStep(nextStepIndex)
                        self.lock.release()
                        break
                    delta = time.time() - self.loopStartTime
                    self.totalTime += delta
                    if not (self.hold and self.manualHold):
                        self.stepTime += delta
                        self.recipeTime += delta
                    logger.debug('Delta time %f' % delta)
                    logger.debug('-- release --')
                    self.lock.release()
                    self.printDebug()
                    stnow = time.time()
                    logger.debug('TOTAL TIME IN LOOP: %f' % (stnow - stthen))

        except Exception as msg:
            logger.exception(msg)
            logger.error('Error in execution: %s' % msg)
            self.internalErrorAbort('Error while executing recipe %s' % msg)

        return

    def getLoopCount(self):
        return self.peek()[2]

    def examineLoopStack(self, currentIndex):
        revstack = copy.copy(self.stepStack)
        revstack.reverse()
        logger.debug('Iterating thru stack to remove loop ends')
        newindex = currentIndex + 1
        logger.debug("Current stack: '%s'" % self.stepStack)
        for elem in revstack:
            (step, stepIndex, loopCount) = elem
            logger.debug("\tITER: /%d/%d/'%s'" % (stepIndex + step.getRepeatEnclosingSteps(), currentIndex, id(step)))
            if stepIndex + step.getRepeatEnclosingSteps() == currentIndex:
                logger.debug('\t\tloop count: %d = %d' % (loopCount, step.getRepeatCount()))
                if loopCount >= step.getRepeatCount():
                    newindex = currentIndex + 1
                    self.popStep()
                else:
                    newindex = stepIndex
                    break
            else:
                break

        logger.debug("After cleanup: '%s'" % self.stepStack)
        return newindex

    def getNextStepIndex(self):
        logger.debug('Getting next step')
        if self.isLooping():
            nextStepIndex = self.examineLoopStack(self.currentStepIndex)
        else:
            nextStepIndex = self.currentStepIndex + 1
        logger.debug("Next step: '%d'" % nextStepIndex)
        return nextStepIndex

    def advanceStep(self, nextStepIndex):
        self.currentStepIndex = nextStepIndex
        logger.debug('Next stepo indox: %d, %d' % (self.currentStepIndex, self.recipe.getStepsCount()))
        if self.recipe.getStepsCount() <= self.currentStepIndex:
            self.currentStep = None
        else:
            self.currentStep = self.recipe.getStep(self.currentStepIndex)
        return

    def printDebug(self):
        print('RECIPE TIMING[ Step Time:', self.getStepTime(), '/Recipe Time:', self.getRecipeTime(), '/Total Time:', self.getTotalTime())

    def gatherDeviceReplies(self):
        logger.debug('Gathering device replies')
        then = time.time()
        envelope = DeviceRepliesEnvelope(self.currentStepIndex, self.currentLoops, self.getRecipeTime(), self.getStepTime(), self.getTotalTime())
        for participant in self.recipeParticipants.values():
            then_dev = time.time()
            responses = participant.getDeviceResponse(self.getRecipeTime(), self.getStepTime(), self.getTotalTime(), self.currentStep)
            for response in responses:
                envelope.addReply(response.getDevice(), response)

            now_dev = time.time()
            logger.debug('Took %f to gather device reply for %s' % (now_dev - then_dev, participant))

        now = time.time()
        logger.debug('Took %f to gather all replies' % (now - then))
        return envelope

    def checkConditions(self, replyEnvelope):
        self.fireEngineEvent(TYPE_CHECKING_CONDITIONALS)
        conditionals = self.currentStep.getConditionals()
        if len(conditionals) == 0:
            return None
        logger.debug('Evaluating %d conditionals' % len(conditionals))
        for suite in conditionals:
            logger.debug("\tEvaluating condition test suite name '%s'" % suite.getName())
            if suite.evaluate(replyEnvelope):
                actions = suite.getActions()
                logger.debug('\t\tPositive evaluation, returning action %s' % actions)
                return (suite, actions)

        return None
        return

    def atEnd(self):
        """
            Return False if the hold condition is not on
            Return True if there is a loop and it is the end of the loop and it is the last of the steps
            Return True if it is the last of the steps
        """
        logger.debug("Is at end? '%d'/'%d'='%d'" % (self.currentStepIndex + 1, self.recipe.getStepsCount(), self.currentStepIndex + 1 >= self.recipe.getStepsCount()))
        if self.forceEnd:
            return True
        if self.hold:
            return False
        if self.isLooping():
            return False
        if self.getStepTime() >= self.currentStep.getDuration():
            if self.currentStepIndex + 1 >= self.recipe.getStepsCount():
                return True
        return False

    def canAdvance(self):
        """
            Return True if the forceAdvance was set
            Return False if the 'hold' condition is set
            Return True if the time is past the duration for this step
        """
        shouldIt = False
        self.lock.acquire()
        if self.forceAdvance:
            forceAdvance = False
            shouldIt = True
        elif self.hold:
            shouldIt = False
        elif self.getStepTime() >= self.currentStep.getDuration():
            shouldIt = True
        self.lock.release()
        return shouldIt

    def isLooping(self):
        """Returns true if the step stack is greater than zero, which means we're looping"""
        return len(self.stepStack) > 0

    def fireStepData(self, envelope):
        global TYPE_DEVICE_RESPONSE
        self.fireEngineEvent(TYPE_DEVICE_RESPONSE, envelope)

    def submitHardwareRequests(self):
        logger.debug('Submitting hardware requests')

    def internalErrorAbort(self, msg):
        logger.error('Internal error. Aborting')
        self.fireEngineEvent(TYPE_EXECUTION_ERROR, 'Error: %s' % msg)
        self.internalCleanup()

    def getCurrentStep(self):
        return self.currentStep

    def setStepGoals(self):
        self.fireEngineEvent(TYPE_SETTING_STEP_GOALS, self.getCurrentStep())
        for participant in self.recipeParticipants.values():
            participant.setStepGoal(self.getRecipeTime(), self.getStepTime(), self.getTotalTime, self.getCurrentStep())

    def isInLoopingInterval(self):
        """
        Returns true if the loopStartStep is not none
        """
        return self.loopStartStep is not None
        return

    def isAtEndOfLoop(self):
        lstep = self.loopStartStep
        deltaSteps = self.currentStepIndex - self.loopStartStepIndex
        return self.getRepeatEnclosingSteps() >= deltaSteps

    def hasFinishedLooping(self):
        return self.currentLoops >= lstep.getRepeatCount()

    def clearLoopFlag(self):
        self.loopStartStep = None
        return

    def returnToLoopStart(self):
        self.currentStepIndex = self.loopStartStepIndex
        self.currentLoops += 1

    def incrementLoopIndex(self, currentIndex):
        revstack = copy.copy(self.stepStack)
        revstack.reverse()
        for elem in revstack:
            step = elem[0]
            stepIndex = elem[1]
            if stepIndex == currentIndex:
                elem[2] += 1
                logger.debug(self.stepStack)
            break

    def prepareStep(self):
        logger.debug("Prepare Step: Looping='%s' / %s" % (self.loopStartStep != None, self.currentStep))
        self.recipeStartTime = time.time()
        loopStepIndex = -1
        self.interrupted = False
        self.forceAdvance = False
        self.manualHold = False
        self.hold = False
        if self.isLooping():
            logger.debug("Current loop index: '%s'" % self.stepStack)
            self.incrementLoopIndex(self.currentStepIndex)
            logger.debug("Current loop index: '%s'" % self.stepStack)
            (ignored, loopStepIndex, ignored) = self.peek()
        if self.currentStep is None:
            return False
        if self.currentStep.doesRepeat():
            logger.debug('does repeat, but is it the same? %d - %d' % (loopStepIndex, self.currentStepIndex))
        if self.currentStep.doesRepeat() and loopStepIndex != self.currentStepIndex:
            self.pushStep(self.currentStep, self.currentStepIndex)
        for participant in self.recipeParticipants.values():
            participant.prepareStep(self.getRecipeTime(), self.getStepTime(), self.getTotalTime(), self.currentStep)

        return True
        return

    def prepareDevices(self):
        """
        Read each device.  Check the status of each device.  If not
        initialized, initialize.  
        
        Send notification of initialization.
        
        The assumption here is that the device has a configured hardware.
        It does not check for a None value or non-existent hardware
        """
        f = ui.getDefault().getMainFrame().getControl()
        dlg = poi.dialogs.progress.ProgressDialog(f)
        dlg.setCancelable(True)

        class HardwareInitRunner(poi.operation.RunnableWithProgress):
            __module__ = __name__

            def run(innerself, monitor):
                done = False
                hwinst = None

                class Cancelator(threading.Thread):
                    """Monitors the monitor's cancelation status. Notifies hwinst to interrupt if exists"""
                    __module__ = __name__

                    def run(self):
                        while not done:
                            if monitor.isCanceled():
                                if hwinst is not None:
                                    hwinst.interruptOperation()
                                    return
                            time.sleep(0.25)

                        return

                cancelator = Cancelator()
                cancelator.setName('Hardware Initializer')
                cancelator.start()
                failure = False
                lendevices = len(self.recipe.getDevices())
                monitor.beginTask('Initializing devices', lendevices)
                for device in self.recipe.getDevices():
                    logger.debug('\tpreparing %s' % device)
                    if monitor.isCanceled():
                        raise Exception('Initialization canceled by user')
                    hwhints = device.getHardwareHints()
                    hwui = hwhints.getChildNamed('id').getValue()
                    description = hardware.hardwaremanager.getHardwareByName(hwui)
                    try:
                        hwinst = description.getInstance()
                    except Exception as msg:
                        logger.exception(msg)
                        failure = True
                        itm = 'No hardware associated with this device: %s' % description
                        self.addError(itm)
                        self.fireEngineEvent(TYPE_HARDWARE_INIT_ERROR, itm)
                        monitor.worked(1)
                        continue

                    status = hwinst.getStatus()
                    if status != hardware.hardwaremanager.STATUS_RUNNING:
                        monitor.subTask("Starting hardware '%s'" % description.getName())
                        try:
                            logger.debug("Initializing: '%s'" % str(hwinst))
                            hwinst.initialize()
                        except Exception as msg:
                            logger.exception(msg)
                            failure = True
                            self.addError(core.error.WorkbenchException("Initialize Error: '%s'" % msg))
                            self.fireEngineEvent(TYPE_HARDWARE_INIT_ERROR, '%s-%s' % (description.getName(), msg))
                            monitor.worked(1)
                            continue

                    try:
                        self.configureRecipeParticipant(device, hwinst, self.recipe)
                        logger.debug("Done configuring device '%s'" % str(device))
                    except Exception as msg:
                        logger.exception(msg)
                        failure = True
                        self.addError("Unable to configure hardware for recipe '%s':%s" % (description.getName(), msg))
                        monitor.worked(1)
                        continue

                    monitor.worked(1)

                done = True
                logger.debug('waiting for cancelator to die')
                cancelator.join()
                if failure:
                    raise Exception('Initialization errors')
                return

        self.switchContext('initializing-hardware')
        self.fireEngineEvent(TYPE_HARDWARE_INIT_START)
        try:
            dlg.run(HardwareInitRunner())
        except Exception as msg:
            logger.exception(msg)
            self.fireEngineEvent(TYPE_HARDWARE_INIT_END)
            raise Exception('Unable to initialize devices')

        logger.debug('Finished initializing devices with result')
        self.fireEngineEvent(TYPE_HARDWARE_INIT_END)

    def getRecipeParticipant(self, hwinst):
        if not self.recipeParticipants.has_key(hwinst):
            return None
        return self.recipeParticipants[hwinst]
        return

    def createRecipeParticipant(self, hwinst, recipe):
        logger.debug("Creating recipe participant for '%s'" % str(hwinst))
        description = hwinst.getDescription()
        hwtypeid = description.getHardwareType()
        factory = executionengine.getDefault().getRecipeParticipantFactory(hwtypeid)
        participant = factory.getParticipant(hwinst, recipe)
        self.recipeParticipants[hwinst] = participant
        return participant

    def configureRecipeParticipant(self, device, hwinst, recipe):
        logger.debug("Configuring recipe participant for '%s'/'%s'" % (device, hwinst))
        participant = self.getRecipeParticipant(hwinst)
        if participant is None:
            participant = self.createRecipeParticipant(hwinst, recipe)
        if participant is None:
            logger.warn("No participant exists for '%s'" % str(device))
            return
        participant.addDevice(device)
        return

    def stop(self):
        logger.debug('Stop called, but ignoring')
        self.interrupted = True
        if True:
            return
        stopperThread = threading.Thread()
        stopperThread.run = self.internalStop
        stopperThread.start()

    def internalStop(self):
        logger.debug('internalstop: acquire')
        map((lambda participant: participant.interrupt()), self.recipeParticipants.values())
        self.lock.acquire()
        logger.debug('internalstop: got it')
        self.interrupted = True
        self.lock.release()
        logger.debug('internalstop: released')

    def notifyParticipanEnd(self):
        for participant in self.recipeParticipants.values():
            participant.handleRecipeEnd(self.getRecipeTime(), self.getStepTime(), self.getTotalTime(), self.recipe)

    def internalCleanup(self):
        if self.cleaning:
            return
        self.cleaning = True
        logger.debug('Internal Cleanup')
        self.running = False
        logger.debug('self runnin gset, gwan fire %s' % TYPE_ENDING)
        self.fireEngineEvent(TYPE_ENDING)
        logger.debug('notify participants end')
        self.notifyParticipanEnd()
        logger.debug('internal cleanup complete')

    def removeAllEngineListeners(self):
        del self.engineListeners[0:]

    def advance(self):
        logger.debug('advance')
        self.forceAdvance = True
        self.fireEngineEvent(TYPE_ADVANCE)

    def pause(self):
        logger.debug('pause')
        self.hold = True
        self.manualHold = True
        self.fireEngineEvent(TYPE_PAUSE)

    def resume(self):
        logger.debug('resume')
        self.markStepLoopStart()
        self.fireEngineEvent(TYPE_RESUME)
        self.hold = False
        self.manualHold = False

    def beginPurge(self):
        pass

    def endPurge(self):
        pass

    def isPurging(self):
        return False

    def isRunning(self):
        return self.running
