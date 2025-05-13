# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/et2216e/src/et2216e/participant.py
# Compiled at: 2005-01-24 15:49:40
import plugins.executionengine.executionengine.executionparticipant
import plugins.furnacezone.furnacezone.response, logging
import plugins.executionengine.executionengine as executionengine
import plugins.furnacezone.furnacezone as furnacezone

logger = logging.getLogger('et2216e.participant')
MAX_ERRORS = 2

class RecipeParticipantFactory(executionengine.executionparticipant.ExecutionParticipantFactory):
    __module__ = __name__

    def getParticipant(self, hwinst, recipe):
        return RecipeParticipant(hwinst, recipe)


class RecipeParticipant(executionengine.executionparticipant.ExecutionParticipant):
    __module__ = __name__

    def __init__(self, hardwareInstance, recipe):
        executionengine.executionparticipant.ExecutionParticipant.__init__(self, hardwareInstance, recipe)
        self.stopHardwareStatusThread()
        self.coefficients = {}
        self.errorCounts = {}
        self.lastTemperatures = {}

    def resumeHardwareStatusThread(self):
        inst = self.getHardwareInstance()
        inst.resumeStatusThread()

    def stopHardwareStatusThread(self):
        inst = self.getHardwareInstance()
        inst.stopStatusThread()

    def prepareDevice(self, device):
        global logger
        logger.debug("Prepare device: '%s'" % str(device))
        instance = self.getHardwareInstance()
        pid = instance.getPIDSettings()
        if pid is None:
            logger.debug('No PID settings specified for %s' % instance)
        devIdx = self.recipe.getDeviceIndex(device)
        self.errorCounts[devIdx] = 0
        self.lastTemperatures[devIdx] = 0
        return

    def prepareStep(self, recipeTime, stepTime, totalTime, step):
        """Called at the beginning of each step"""
        logger.debug("***** Prepare Step: '%s'/%s" % (step, self.devices))
        instance = self.getHardwareInstance()
        for dev in self.devices:
            if not dev.getHardwareID() == instance.getDescription().getName():
                continue
            devIdx = self.recipe.getDeviceIndex(dev)
            devEntry = step.getEntry(devIdx)
            logger.debug("\tIs linear ramp? '%s'/%d" % (devEntry.isLinearRamp(), devEntry.setpointMode))
            self.coefficients.clear()
            if devEntry.isLinearRamp():
                setpoint = float(devEntry.getSetpoint())
                if devEntry.isRampFromLast():
                    previousSetpoint = float(self.getHardwareInstance().getTemperature())
                elif devEntry.isRampFromSetpoint():
                    stepIdx = self.recipe.getStepIndex(step)
                    if not stepIdx == 0:
                        previousSetpoint = float(self.recipe.getStep(stepIdx - 1).getEntry(devIdx).getSetpoint())
                    else:
                        previousSetpoint = float(self.getHardwareInstance().getTemperature())
                self.coefficients[devIdx] = [
                previousSetpoint, (setpoint - previousSetpoint) / step.getDuration()]
                logger.debug(repr(self.coefficients))
                logger.debug(' coefficients for a linear ramp: %d+%dt' % (self.coefficients[devIdx][0], self.coefficients[devIdx][1]))

    def setStepGoal(self, recipeTime, stepTime, totalTime, step):
        logger.debug("Set Step Goals: '%s'" % step)
        instance = self.getHardwareInstance()
        for device in self.devices:
            if not device.getHardwareID() == instance.getDescription().getName():
                continue
            idx = self.recipe.getDeviceIndex(device)
            entry = step.getEntry(idx)
            if entry.isSingleSetpoint():
                setpoint = entry.getSetpoint()
                logger.debug('\tSetpoint: %d' % setpoint)
                try:
                    instance.setSetpoint(setpoint)
                    self.clearErrorCounts(idx)
                except Exception as msg:
                    self.updateErrorCounts(idx, Exception)

    def clearErrorCounts(self, devIndex):
        self.errorCounts[devIndex] = 0

    def updateErrorCounts(self, devIndex, exc):
        self.errorCounts[devIndex] = self.errorCounts[devIndex] + 1
        if self.errorCounts[devIndex] >= MAX_ERRORS:
            logger.error("Too many errors on this channel %d: errors '%d'" % (devIndex, self.errorCounts[devIndex]))
            raise exc

    def linearRampGenerator(self, time, devIdx):
        return int(self.coefficients[devIdx][0] + time * self.coefficients[devIdx][1])

    def tick(self, recipeTime, stepTime, totalTime, step):
        instance = self.getHardwareInstance()
        for dev in self.devices:
            if not dev.getHardwareID() == instance.getDescription().getName():
                continue
            devIdx = self.recipe.getDeviceIndex(dev)
            devEntry = step.getEntry(devIdx)
            if devEntry.isLinearRamp():
                newTemperature = self.linearRampGenerator(stepTime, devIdx)
                try:
                    instance.setSetpoint(newTemperature)
                    self.clearErrorCounts(devIdx)
                except Exception as msg:
                    self.updateErrorCounts(devIdx, Exception)
                else:
                    logger.debug('Ramp setpoint: %d at time %d' % (newTemperature, stepTime))

    def submitHardwareRequest(self, recipeTime, stepTime, totalTime, step):
        logger.debug('Submit hardware requests: %s' % self.devices)

    def updateLinearTimeRamp(self, recipeTime, stepTime, totalTime, step, device, instance):
        devIdx = self.recipe.getDeviceIndex(device)
        devEntry = step.getEntry(devIdx)
        if devEntry.isLinearRamp():
            newTemperature = self.linearRampGenerator(stepTime, devIdx)
            try:
                instance.setSetpoint(newTemperature)
                self.clearErrorCounts(devIdx)
            except Exception as msg:
                self.updateErrorCounts(devIdx, Exception)
            else:
                logger.debug('Ramp setpoint: %d at %d' % (newTemperature, stepTime))

    def getDeviceResponse(self, recipeTime, stepTime, totalTime, step):
        logger.debug('Get device response %s' % self.getHardwareInstance())
        responses = []
        instance = self.getHardwareInstance()
        for device in self.devices:
            if not device.getHardwareID() == instance.getDescription().getName():
                continue
            self.updateLinearTimeRamp(recipeTime, stepTime, totalTime, step, device, instance)
            idx = self.recipe.getDeviceIndex(device)
            try:
                temperature = instance.getTemperature()
                self.lastTemperatures[idx] = temperature
                self.clearErrorCounts(idx)
            except Exception as msg:
                self.updateErrorCounts(idx, Exception)
                temperature = self.lastTemperatures[idx]

            response = furnacezone.response.FurnaceZoneDeviceResponse(device, temperature)
            responses.append(response)

        return responses

    def checkConditions(self, recipeTime, stepTime, totalTime, step):
        return None

    def handleRecipeEnd(self, recipeTime, stepTime, totalTime, recipe):
        self.enterPurgeState()

    def enterPurgeState(self):
        instance = self.getHardwareInstance()
        logger.debug('entering purge')
        for device in self.devices:
            if not device.getHardwareID() == instance.getDescription().getName():
                continue
            if not device.getPurgeActive():
                instance.setSetpoint(0)
                instance.resumeStatusThread()
                logger.debug('No purge for device %s' % str(device))
                continue
            (setpoint, duration) = (
             device.getPurgeSetpoint(), device.getPurgeLength())
            instance.startPurge(setpoint, duration)

    def isPurging(self):
        return self.purging

    def setPurgingDone(self):
        self.purging = True

    def interruptPurge(self):
        instance = self.getHardwareInstance()
        logger.debug('interrupting purge')
        instance.interruptPurge()
