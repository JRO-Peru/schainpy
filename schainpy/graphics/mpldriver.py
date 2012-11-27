import matplotlib
matplotlib.use("TKAgg")
import matplotlib.pyplot
import scitools.numpyutils

def init(idfigure, wintitle, width, height):
    matplotlib.pyplot.ioff()
    fig = matplotlib.pyplot.matplotlib.pyplot.figure(num=idfigure, facecolor="w")
    fig.canvas.manager.set_window_title(wintitle)
    fig.canvas.manager.resize(width,height)
    matplotlib.pyplot.ion()
    
def setTextFromAxes(idfigure, ax, title):
    fig = matplotlib.pyplot.figure(idfigure)
    ax.annotate(title, xy=(.1, .99),
                xycoords='figure fraction',
                horizontalalignment='left', verticalalignment='top',
                fontsize=10)

def setTitle(idfigure, title):
    fig = matplotlib.pyplot.figure(idfigure)
    fig.suptitle(title)

def makeAxes(idfigure, nrow, ncol, xpos, ypos, colspan, rowspan):
    fig = matplotlib.pyplot.figure(idfigure)
    ax = matplotlib.pyplot.subplot2grid((nrow, ncol), (xpos, ypos), colspan=colspan, rowspan=rowspan)
    return ax

def pline(ax, x, y, xmin, xmax, ymin, ymax, xlabel, ylabel, title, firsttime):
    if firsttime:
        ax.plot(x, y)
        ax.set_xlim([xmin,xmax])
        ax.set_ylim([ymin,ymax])
        ax.set_xlabel(xlabel, size=8)
        ax.set_ylabel(ylabel, size=8)
        ax.set_title(title, size=10)
        matplotlib.pyplot.tight_layout()
    else:
        ax.lines[0].set_data(x,y)

def draw(idfigure):
    fig = matplotlib.pyplot.figure(idfigure)
    fig.canvas.draw()

def pcolor():
    pass



    