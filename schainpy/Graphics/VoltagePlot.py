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

from Graphics.BasicGraph import *
from Model.Voltage import Voltage

class Osciloscope():
    
    graphObjDict = {}
    showPower = True
    
    __szchar = 0.7
    __xrange = None
    __yrange = None
    __zrange = None
     
    def __init__(self):
        key = "osc"
        
        baseObj = BasicGraph()
        baseObj.setName(key)
        
        self.graphObjDict[key] = baseObj
        
    
    def setup(self, subpage, title="", xlabel="", ylabel="", colormap="jet", showColorbar=False, showPowerProfile=False):
        pass
    
    def setRanges(self, xrange, yrange, zrange):
        pass
    
    def plotData(self, data , xmin=None, xmax=None, ymin=None, ymax=None, zmin=None, zmax=None):
        pass


    
class VoltagePlot(object):
    '''
    classdocs
    '''

    __m_Voltage = None
    
    def __init__(self, m_Voltage):
        '''
        Constructor
        '''
        self.__m_Voltage = m_Voltage
    
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