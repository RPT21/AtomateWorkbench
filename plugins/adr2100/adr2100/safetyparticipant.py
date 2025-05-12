# uncompyle6 version 3.9.1
# Python bytecode version base 2.3 (62011)
# Decompiled from: Python 3.12.2 (tags/v3.12.2:6abddd9, Feb  6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)]
# Embedded file name: ../plugins/adr2100/src/adr2100/safetyparticipant.py
# Compiled at: 2005-01-06 20:53:16
import executionengine, executionengine.engine, safetyinterlock

class ADR2100InterlockParticipant(safetyinterlock.InterlockParticipant):
    __module__ = __name__

    def __init__(self):
        safetyinterlock.InterlockParticipant.__init__(self)
        self.cachedAnalog = [1, 1, 1, 1, 1, 1, 1, 1]
        self.cachedDigital = [1, 1, 1, 1, 1, 1, 1, 1]
        self.valid = False
        self.engine = None
        executionengine.getDefault().addEngineInitListener(self)
        self.hardware = None
        self.errors = []
        return

    def setHardware(self, hardware):
        self.hardware = hardware

    def getName(self):
        if self.hardware is None:
            return 'Stranded ADR 2100!'
        if self.hardware.getDescription() is None:
            return 'Unconfigured ADR 2100'
        return '%s - ADR 2100 IO Board' % self.hardware.getDescription().getName()

    def engineInit(self, engine):
        self.engine = engine
        engine.addEngineListener(self)

    def engineEvent(self, event):
        if event.getType() == executionengine.engine.TYPE_ENDING:
            self.engine.removeEngineListener(self)
            self.engine = None
        return

    def isValid(self):
        return self.valid

    def touch(self, inst):
        """
        diff = map(lambda (x,y): x == y, zip(digitalPorts, self.cachedDigital))        
        giff = map(lambda (x,y): x == y, zip(analogPorts, self.cachedAnalog))
        
        diff = (diff[1], diff[3], diff[5], diff[7])
                
        #if not (False in diff): #and not (False in giff):
        #    return
                    
        #update = False
        self.valid = True
        
        self.cachedDigital = digitalPorts
        update = True
        digs = self.cachedDigital
        goodDigitals = (digs[1], digs[3], digs[5], digs[7])
        
        validDigital = False
        validAnalog = False
        
        #self.valid = not (False in (goodDigitals))
        validDigital = not (False in (goodDigitals))
        self.errors = []
        
        if not validDigital:
            x = 0
            for i in goodDigitals:
                if i confiis False:
                    self.errors.append("Port D Bit %d is Off"%x)
                x+=1
        
        # try second
        
        self.cachedAnalog = analogPorts
        #update = True
        anals = self.cachedAnalog
        #validAnalog =  0.8 <= anals[0] <= 0.9
        validAnalog = True
        
        if not validAnalog:
            self.errors.append("Analog port 0 value %0.3f not in range [0.8,0.9]"%anals[0])
        
        self.valid = validDigital and validAnalog
        
        # fake it
        self.valid = True
        """
        (self.valid, self.errors) = inst.executeValidationCode()
        if self.valid:
            self.errors = []
        self.fireUpdate()

    def getStatusMessages(self):
        return self.errors

    def fireUpdate(self):
        safetyinterlock.InterlockParticipant.fireUpdate(self)
        if self.engine is not None and not self.valid:
            self.valid = None
            self.engine.stop()
        return
