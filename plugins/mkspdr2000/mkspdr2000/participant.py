# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/mkspdr2000/src/mkspdr2000/participant.py
# Compiled at: 2004-11-23 04:03:11
import executionengine.executionparticipant, resources.runlog, pressure_gauge.response, logging
logger = logging.getLogger('mkspdr2000.participant')

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

    def prepareStep(self, recipeTime, stepTime, totalTime, step):
        pass

    def setStepGoal(self, recipeTime, stepTime, totalTime, step):
        pass

    def tick(self, recipeTime, stepTime, totalTime, step):
        pass

    def submitHardwareRequest(self, recipeTime, stepTime, totalTime, step):
        pass

    def getDeviceResponse(self, recipeTime, stepTime, totalTime, step):
        responses = []
        instance = self.getHardwareInstance()
        for device in self.devices:
            pressure = instance.getPressure()
            response = pressure_gauge.response.PressureGaugeDeviceResponse(device, pressure)
            responses.append(response)

        return responses

    def checkConditions(self, recipeTime, stepTime, totalTime, step):
        return None
        return

    def handleRecipeEnd(self, recipeTime, stepTime, totalTime, recipe):
        pass

    def enterPurgeState(self):
        pass

    def isPurging(self):
        return False

    def setPurgingDone(self):
        self.purging = True

    def interruptPurge(self):
        pass
