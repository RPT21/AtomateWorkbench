# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/executionengine/src/executionengine/executionparticipant.py
# Compiled at: 2004-08-27 19:09:56


class ExecutionParticipantFactory(object):
    __module__ = __name__

    def getParticipant(self, hwinst, recipe):
        raise Exception('Not implemented')


class ExecutionParticipant(object):
    __module__ = __name__

    def __init__(self, hardwareInstance, recipe):
        self.purging = False
        self.hardwareInstance = hardwareInstance
        self.devices = []
        self.recipe = recipe

    def getHardwareInstance(self):
        return self.hardwareInstance

    def interrupt(self):
        self.hardwareInstance.interruptOperation()

    def addDevice(self, device):
        self.devices.append(device)
        self.prepareDevice(device)

    def getLabel(self):
        return map((lambda dev: dev.getLabel()), self.devices)

    def prepareDevice(self, device):
        pass

    def prepareStep(self, recipeTime, stepTime, totalTime, step):
        """Called at the beginning of each step"""
        pass

    def setStepGoal(self, recipeTime, stepTime, totalTime, step):
        pass

    def tick(self, recipeTime, stepTime, totalTime, step):
        pass

    def submitHardwareRequest(self, recipeTime, stepTime, totalTime, step):
        pass

    def getDeviceResponse(self, recipeTime, stepTime, totalTime, step):
        return []

    def checkConditions(self, recipeTime, stepTime, totalTime, step):
        return None
        return

    def handleRecipeEnd(self, recipeTime, stepTime, totalTime, recipe):
        pass

    def isPurging(self):
        return self.purging

    def setPurgingDone(self):
        self.purging = True

    def interruptPurge(self):
        pass
