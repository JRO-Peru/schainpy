"""
$Author$
$Id$

"""
import datetime
from controller import *
from model import *


class Test():
    def __init__(self):
        self.createObjects()
        self.run()
        
    def createObjects(self):
        
        self.upConfig = controller.UPConf(id=1, name="voltageproc", type="voltage")
        
        opConf = self.upConfig.addOperation(name="init", priority=0)
        
        opConf1 = self.upConfig.addOperation(name="CohInt", priority=1, type="other")
        opConf1.addParameter(name="nCohInt", value=100)
        
        opConf2 = self.upConfig.addOperation(name="Scope", priority=2, type="other")
        opConf2.addParameter(name="idfigure", value=1)
        
        
        self.upConfigSpc = controller.UPConf(id=2, name="spectraproc", type="spectra")
        opConf = self.upConfigSpc.addOperation(name="init", priority=0)
        opConf.addParameter(name="nFFTPoints", value=8)
        
        opConf3 = self.upConfigSpc.addOperation(name="SpectraPlot", priority=1, type="other")
        opConf3.addParameter(name="idfigure", value=2)
        
#        opConf = self.upConfig.addOperation(name="selectChannels", priority=3)
#        opConf.addParameter(name="channelList", value=[0,1])
        
        
        #########################################
        self.objR = jrodataIO.VoltageReader()
        self.objP = jroprocessing.VoltageProc()
        self.objSpc = jroprocessing.SpectraProc()
        
        self.objInt = jroprocessing.CohInt()

        self.objP.addOperation(self.objInt, opConf1.id)
        
        self.objScope = jroplot.Scope()
        
        self.objP.addOperation(self.objScope, opConf2.id)
        
        self.objSpcPlot = jroplot.SpectraPlot()
        
        self.objSpc.addOperation(self.objSpcPlot, opConf3.id)
        
        self.connect(self.objR, self.objP)
        
        self.connect(self.objP, self.objSpc)
        
    def connect(self, obj1, obj2):
        obj2.setInput(obj1.getOutput())
        
    def run(self):
        
        while(True):
            self.objR.run(path="/Users/dsuarez/Remote/EW_DRIFTS2",
                    startDate=datetime.date(2012,1,1), 
                    endDate=datetime.date(2012,12,30), 
                    startTime=datetime.time(0,0,0), 
                    endTime=datetime.time(23,59,59), 
                    set=0, 
                    expLabel = "", 
                    ext = None, 
                    online = False)
            
            for opConf in self.upConfig.getOperationObjList():
                kwargs={}
                for parm in opConf.getParameterObjList():
                    kwargs[parm.name]=parm.value
                    
                self.objP.call(opConf,**kwargs)
                
            ############################
            for opConfSpc in self.upConfigSpc.getOperationObjList():
                kwargs={}
                for parm in opConfSpc.getParameterObjList():
                    kwargs[parm.name]=parm.value
                    
                self.objSpc.call(opConfSpc,**kwargs)
            
            if self.objR.flagNoMoreFiles:
                break
            
            if self.objR.flagIsNewBlock:
                print 'Block No %04d, Time: %s' %(self.objR.nTotalBlocks, 
                                                  datetime.datetime.fromtimestamp(self.objR.basicHeaderObj.utc + self.objR.basicHeaderObj.miliSecond/1000.0),)

            
    

if __name__ == "__main__":
    Test()