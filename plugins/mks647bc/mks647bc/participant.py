# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/mks647bc/src/mks647bc/participant.py
# Compiled at: 2004-12-07 10:31:19
import executionengine.executionparticipant, time, mfc.response, logging, mks647bc.userinterface
logger = logging.getLogger('mks647bc.participant')

class RecipeParticipantFactory(executionengine.executionparticipant.ExecutionParticipantFactory):
    __module__ = __name__

    def getParticipant(self, hwinst, recipe):
        return RecipeParticipant(hwinst, recipe)


class RecipeParticipant(executionengine.executionparticipant.ExecutionParticipant):
    __module__ = __name__

    def __init__(self, hardwareInstance, recipe):
        executionengine.executionparticipant.ExecutionParticipant.__init__(self, hardwareInstance, recipe)
        self.stopHardwareStatusThread()

    def resumeHardwareStatusThread(self):
        inst = self.getHardwareInstance()
        inst.resumeStatusThread()

    def stopHardwareStatusThread(self):
        inst = self.getHardwareInstance()
        inst.stopStatusThread()

    def prepareDevice(self, device):
        global logger
        inst = self.getHardwareInstance()
        logger.debug("Prepare device: '%s'" % str(device))
        inst.enableFlow()
        channelNum = device.getChannelNumber()
        gcf = device.getGCF()
        units = device.getUnits()
        range = device.getRange()
        rangeIndex = mks647bc.userinterface.getRangeIndex(units, range)
        inst.channelOn(channelNum)
        inst.setRangeIndex(channelNum, rangeIndex, range)
        inst.setGCF(channelNum, gcf)

    def prepareStep(self, recipeTime, stepTime, totalTime, step):
        """Called at the beginning of each step"""
        logger.debug("Prepare Step: '%s'" % step)
        inst = self.getHardwareInstance()
        for device in self.devices:
            devIdx = self.recipe.getDeviceIndex(device)
            devEntry = step.getEntry(devIdx)
            channelNum = device.getChannelNumber()
            inst.setChannelSetpoint(channelNum, devEntry.getFlow())

    def setStepGoal(self, recipeTime, stepTime, totalTime, step):
        logger.debug("Set Step Goals: '%s'" % step)

    def submitHardwareRequest(self, recipeTime, stepTime, totalTime, step):
        logger.debug('Submit hardware requests')

    def getDeviceResponse(self, recipeTime, stepTime, totalTime, step):
        logger.debug('Get device response me %s' % self)
        responses = []
        instance = self.getHardwareInstance()
        for device in self.devices:
            logger.debug('Asking channel %d for flow' % device.getChannelNumber())
            then = time.time()
            flow = instance.getChannelFlow(device.getChannelNumber())
            response = mfc.response.MFCDeviceResponse(device, flow)
            responses.append(response)
            now = time.time()
            logger.debug('Took %f to gather one channel' % (now - then))

        return responses

    def checkConditions(self, recipeTime, stepTime, totalTime, step):
        return None
        return

    def handleRecipeEnd(self, recipeTime, stepTime, totalTime, recipe):
        self.startPurge()

    def startPurge(self):
        inst = self.getHardwareInstance()
        purgesetpoints = []
        for device in self.devices:
            if not device.hasPurge():
                channel = device.getChannelNumber()
                inst.channelOff(channel)
                inst.getChannelFlow(channel)
                try:
                    inst.channelOff(channel)
                    inst.getChannelFlow(channel)
                except Exception as msg:
                    logger.exception(msg)
                else:
                    continue
            (setpoint, channel, length) = (
             device.getChannelNumber(), device.getPurgeSetpoint(), device.getPurgeLength())
            purgesetpoints.append((setpoint, channel, length))

        inst.startPurge(purgesetpoints)

    def isPurging(self):
        return self.purging

    def setPurgingDone(self):
        self.purging = True

    def interruptPurge(self):
        pass
