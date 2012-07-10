'''
Created on Feb 7, 2012

@author $Author$
@version $Id$
'''
import os, sys
import numpy
import plplot

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from Graphics.BaseGraph import *
from Model.Voltage import Voltage

class Osciloscope:
    
    voltageObj = Voltage()
    
    linearGraphObj = LinearPlot()
    
    __isPlotConfig = False
        
    __isPlotIni = False
    
    __xrange = None
    
    __yrange = None
    
    voltageObj = Voltage()
    
    nGraphs = 0
    
    indexPlot = None
    
    graphObjList = []
    m_LinearPlot= LinearPlot()


    m_Voltage= Voltage()


        
    def __init__(self, Voltage, index=0):
        
        """
        
        Inputs:
            
            type:   "power" ->> Potencia
                    "iq"    ->> Real + Imaginario
        """
        
        self.__isPlotConfig = False
        
        self.__isPlotIni = False
        
        self.__xrange = None
        
        self.__yrange = None
        
        self.voltageObj = None
        
        self.nGraphs = 0
        
        self.indexPlot = index
        
        self.graphObjList = [] 
        
        self.voltageObj = Voltage
        
    
    def __addGraph(self, subpage, title="", xlabel="", ylabel="", XAxisAsTime=False):
        
        graphObj = LinearPlot()
        graphObj.setup(subpage, title="", xlabel="", ylabel="", XAxisAsTime=False)
        #graphObj.setScreenPos()
                
        self.graphObjList.append(graphObj)
        
        del graphObj
    
#    def setXRange(self, xmin, xmax):
#        self.__xrange = (xmin, xmax)
#    
#    def setYRange(self, ymin, ymax):
#        self.__yrange = (ymin, ymax)    

    
    def setup(self, titleList=None, xlabelList=None, ylabelList=None, XAxisAsTime=False):
        
        nChan = int(self.voltageObj.m_SystemHeader.numChannels)
        
        myTitle = ""
        myXlabel = ""
        myYlabel = ""
        
        for chan in range(nChan):
            if titleList != None:
                myTitle = titleList[chan]
                myXlabel = xlabelList[chan]
                myYlabel = ylabelList[chan]
                
            self.__addGraph(chan+1, title=myTitle, xlabel=myXlabel, ylabel=myYlabel, XAxisAsTime=XAxisAsTime)
        
        self.nGraphs = nChan
        self.__isPlotConfig = True

    def iniPlot(self, winTitle=""):
        
        plplot.plsstrm(self.indexPlot)
        plplot.plparseopts([winTitle], plplot.PL_PARSE_FULL)
        plplot.plsetopt("geometry", "%dx%d" %(700, 115*self.nGraphs))
        plplot.plsdev("xwin")
        plplot.plscolbg(255,255,255)
        plplot.plscol0(1,0,0,0)
        plplot.plinit()
        plplot.plspause(False)
        plplot.plssub(1, self.nGraphs)
        
        self.__isPlotIni = True     
    
    def plotData(self, xmin=None, xmax=None, ymin=None, ymax=None, titleList=None, xlabelList=None, ylabelList=None, XAxisAsTime=False, type='iq', winTitle="Voltage"):
        
        if not(self.__isPlotConfig):
            self.setup(titleList, xlabelList, ylabelList, XAxisAsTime)
        
        if not(self.__isPlotIni):
            self.iniPlot(winTitle)
        
        plplot.plsstrm(self.indexPlot)
        
        data = self.voltageObj.data
              
        x = self.voltageObj.heightList
        
        if xmin == None: xmin = x[0]
        if xmax == None: xmax = x[-1]
        if ymin == None: ymin = numpy.nanmin(abs(data))
        if ymax == None: ymax = numpy.nanmax(abs(data))
        
        plplot.plbop()
        for chan in range(self.nGraphs):
            y = data[chan,:]
            
            self.graphObjList[chan].plotComplexData(x, y, xmin, xmax, ymin, ymax, 8, type)
        
        plplot.plflush()
        plplot.pleop()
    
    def end(self):
        plplot.plend()
        
class VoltagePlot(object):
    '''
    classdocs
    '''

    __m_Voltage = None
    
    def __init__(self, voltageObj):
        '''
        Constructor
        '''
        self.__m_Voltage = voltageObj
    
    def setup(self):
        pass
    
    def addGraph(self, type, xrange=None, yrange=None, zrange=None):
        pass
    
    def plotData(self):
        pass

if __name__ == '__main__':
    
    import numpy
    
    plplot.plsetopt("geometry", "%dx%d" %(450*2, 200*2))
    plplot.plsdev("xcairo")
    plplot.plscolbg(255,255,255)
    plplot.plscol0(1,0,0,0)
    plplot.plinit()
    plplot.plssub(1, 2)
    
    nx = 64
    ny = 100
    
    data = numpy.random.uniform(-50,50,(nx,ny))
    
    baseObj = RTI()
    baseObj.setup(1, "Spectrum", "Frequency", "Range", "br_green", False, False)
    baseObj.plotData(data)
    
    data = numpy.random.uniform(-50,50,(nx,ny))
    
    base2Obj = RTI()
    base2Obj.setup(2, "Spectrum", "Frequency", "Range", "br_green", True, True)
    base2Obj.plotData(data)
    
    plplot.plend()
    exit(0)