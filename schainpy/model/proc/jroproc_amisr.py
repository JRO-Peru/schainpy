'''
@author: Daniel Suarez
'''

from jroproc_base import ProcessingUnit, Operation
from model.data.jroamisr import AMISR

class AMISRProc(ProcessingUnit):
    def __init__(self):
        ProcessingUnit.__init__(self)
        self.objectDict = {}
        self.dataOut = AMISR()
        
    def run(self):
        if self.dataIn.type == 'AMISR':
            self.dataOut.copy(self.dataIn) 


class PrintInfo(Operation):
    def __init__(self):
        self.__isPrinted = False
    
    def run(self, dataOut):
        
        if not self.__isPrinted:
            print 'Number of Records by File: %d'%dataOut.nRecords
            print 'Number of Pulses: %d'%dataOut.nProfiles
            print 'Number of Pulses by Frame: %d'%dataOut.npulseByFrame
            print 'Number of Samples by Pulse: %d'%len(dataOut.heightList)
            print 'Ipp Seconds: %f'%dataOut.ippSeconds
            print 'Number of Beams: %d'%dataOut.nBeams
            print 'BeamCodes:'
            beamStrList = ['Beam %d -> Code=%d, azimuth=%2.2f,  zenith=%2.2f, gain=%2.2f'%(k,v[0],v[1],v[2],v[3]) for k,v in dataOut.beamCodeDict.items()]
            for b in beamStrList:
                print b
            self.__isPrinted = True
        
        return
        
        
class BeamSelector(Operation):
    profileIndex = None
    nProfiles = None
    
    def __init__(self):
        
        self.profileIndex = 0
    
    def incIndex(self):
        self.profileIndex += 1
        
        if self.profileIndex >= self.nProfiles:
            self.profileIndex = 0
    
    def isProfileInRange(self, minIndex, maxIndex):
        
        if self.profileIndex < minIndex:
            return False
        
        if self.profileIndex > maxIndex:
            return False
        
        return True
    
    def isProfileInList(self, profileList):
        
        if self.profileIndex not in profileList:
            return False
        
        return True
    
    def run(self, dataOut, beam=None):
        
        dataOut.flagNoData = True
        self.nProfiles = dataOut.nProfiles

        if beam != None:
            if self.isProfileInList(dataOut.beamRangeDict[beam]):
                beamInfo = dataOut.beamCodeDict[beam]
                dataOut.azimuth = beamInfo[1]
                dataOut.zenith = beamInfo[2]
                dataOut.gain = beamInfo[3]
                dataOut.flagNoData = False
                
            self.incIndex()
            return 1
        
        else:
            raise ValueError, "BeamSelector needs beam value"
        
        return 0              