import mpldriver

class Figure:
    axesList = None
    def __init__(self): 
        pass
        
    def init(self, idfigure, wintitle, width, height, nplots): 
        self.idfigure = idfigure
        self.wintitle = wintitle
        self.width = width
        self.height = height
        self.nplots = nplots
        mpldriver.init(idfigure, wintitle, width, height)
        
        self.axesList = []
    
    def setTitle(self, title):
        mpldriver.setTitle(self.idfigure, title)
    
    def setTextFromAxes(self, title):
        mpldriver.setTextFromAxes(self.idfigure, self.axesList[0].ax, title)
    
    def makeAxes(self, nrow, ncol, xpos, ypos, colspan, rowspan):
        ax = mpldriver.makeAxes(self.idfigure, nrow, ncol, xpos, ypos, colspan, rowspan)
        axesObj = Axes(ax)
        self.axesList.append(axesObj)
    
    def draw(self):
        mpldriver.draw(self.idfigure)
    
    def run(self):
        pass
            

class Axes:
    firsttime = None
    ax = None
    
    def __init__(self, ax):
        self.firsttime = True
        self.ax = ax
    
    def pline(self, x, y, xmin, xmax, ymin, ymax, xlabel, ylabel, title):
        
        mpldriver.pline(ax=self.ax,
                        x=x, 
                        y=y, 
                        xmin=xmin, 
                        xmax=xmax, 
                        ymin=ymin, 
                        ymax=ymax, 
                        xlabel=xlabel, 
                        ylabel=ylabel, 
                        title=title, 
                        firsttime=self.firsttime)
        
        self.firsttime = False
        
    def pcolor(self):
        pass
