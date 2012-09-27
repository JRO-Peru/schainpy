import numpy
from schainPlot import *


class RTIFigure(Figure):
    def __init__(self, idstream, nframe, wintitle, colormap, driver, showColorbar, showPowerProfile):
        self.idStream = idStream
        self.nFrames = nFrames
        self.winTitle = winTitle
        self.colormap = colormap
        self.driver = driver
        self.showGraph1 = showColorbar
        self.showGraph2 = showPowerProfile
        self.overplot = 1 # igual a 1 porque el grafico es RTI, para el caso de Spectra(Spc,CrossSpc) overplot = 0
        
        self.width = 700
        self.height = 150
        self.ncol = int(numpy.sqrt(self.nFrames)+0.9)
        self.nrow = int(self.nFrames*1./ncol + 0.9)
        
        
    def __createFrames(self):
        for frame in range(self.nFrames):
            frameObj = RTIFrame(idFrame = frame,
                             showGraph1 = self.showGraph1,
                             showGraph2 = self.showGraph2
                             )
            
            self.frameObjList.append(frameObj)
    
    
        
        
        
    
class RTIFrame(Frame):
    def __init__(self,idFrame, showColorbar, showPowerProfile):
        self.idFrame = idFrame
        self.showGraph1 = showColorbar
        self.showGraph2 = showPowerProfile
    
    def setXYPos
        

class SelfSpcFigure(Figure):
    def __init__(self):
        pass
    
class SelfSpcFrame(Frame):
    def __init__(self):
        pass

class CrossSpcFigure(Figure):
    def __init__(self):
        pass

class CrossSpcFrame(Frame):
    def __init__(self):
        pass

class ScopeFigure(Figure):
    def __init__(self):
        pass

class ScopeFrame(Frame):
    def __init__(self):
        pass
    
