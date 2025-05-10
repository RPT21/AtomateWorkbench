# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/mks146/src/mks146/participant.py
# Compiled at: 2004-10-21 23:29:44
import executionengine.executionparticipant, mfc.response, logging
logger = logging.getLogger('mks146.participant')

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
        global logger
        inst = self.getHardwareInstance()
        inst.stopStatusThread()
        logger.debug('Status thread stopped')

    def prepareDevice(self, device):
        inst = self.getHardwareInstance()
        logger.debug("Prepare device: '%s'" % str(device))
        for device in self.devices:
            channelNum = device.getChannelNumber()
            gcf = 1.0
            units = 1
            inst.enableChannel(channelNum)
            inst.setSetpointMode(channelNum, 'S')
            inst.setRange(channelNum, device.getRange())

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
        logger.debug('Get device response')
        responses = []
        instance = self.getHardwareInstance()
        for device in self.devices:
            flow = instance.getChannelCondition(device.getChannelNumber())[1]
            response = mfc.response.MFCDeviceResponse(device, flow)
            responses.append(response)

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
                logger.debug('Disabling channel %d' % device.getChannelNumber())
                channel = device.getChannelNumber()
                inst.disableChannel(channel)
                try:
                    inst.getChannelCondition(channel)
                except Exception, msg:
                    pass
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
