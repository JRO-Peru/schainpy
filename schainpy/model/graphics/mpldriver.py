import numpy
import datetime
import matplotlib
matplotlib.use("TKAgg")
import matplotlib.pyplot
import matplotlib.dates
#import scitools.numpyutils
from mpl_toolkits.axes_grid1 import make_axes_locatable

from matplotlib.dates import DayLocator, HourLocator, MinuteLocator, SecondLocator, DateFormatter
from matplotlib.ticker import FuncFormatter
from matplotlib.ticker import *

###########################################
#Actualizacion de las funciones del driver
###########################################

def createFigure(idfigure, wintitle, width, height, facecolor="w"):
    
    matplotlib.pyplot.ioff()
    fig = matplotlib.pyplot.figure(num=idfigure, facecolor=facecolor)
    fig.canvas.manager.set_window_title(wintitle)
    fig.canvas.manager.resize(width, height)
    matplotlib.pyplot.ion()
    
    return fig

def closeFigure():
    
    matplotlib.pyplot.ioff()
    matplotlib.pyplot.show()
    
    return

def saveFigure(fig, filename):
    fig.savefig(filename)

def setWinTitle(fig, title):
    
    fig.canvas.manager.set_window_title(title)

def setTitle(fig, title):
    
    fig.suptitle(title)

def createAxes(fig, nrow, ncol, xpos, ypos, colspan, rowspan):
    
    matplotlib.pyplot.figure(fig.number)
    axes = matplotlib.pyplot.subplot2grid((nrow, ncol),
                                        (xpos, ypos),
                                        colspan=colspan,
                                        rowspan=rowspan)
    return axes

def setAxesText(ax, text):
    
    ax.annotate(text,
                xy = (.1, .99),
                xycoords = 'figure fraction',
                horizontalalignment = 'left',
                verticalalignment = 'top',
                fontsize = 10)

def printLabels(ax, xlabel, ylabel, title):
    
    ax.set_xlabel(xlabel, size=11)
    ax.set_ylabel(ylabel, size=11)
    ax.set_title(title, size=12)
    
def createPline(ax, x, y, xmin, xmax, ymin, ymax, xlabel='', ylabel='', title='',
                ticksize=9, xtick_visible=True, ytick_visible=True,
                nxticks=4, nyticks=10,
                grid=None):
    
    """
    
    Input:
        grid    :    None, 'both', 'x', 'y'
    """
        
    ax.plot(x, y)
    ax.set_xlim([xmin,xmax])
    ax.set_ylim([ymin,ymax])
    
    printLabels(ax, xlabel, ylabel, title)
    
    ######################################################
    xtickspos = numpy.arange(nxticks)*int((xmax-xmin)/nxticks) + int(xmin)
    ax.set_xticks(xtickspos)
    
    for tick in ax.get_xticklabels():
        tick.set_visible(xtick_visible)
        
    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(ticksize) 
    
    ######################################################
    for tick in ax.get_yticklabels():
        tick.set_visible(ytick_visible)
    
    for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontsize(ticksize)
        
    iplot = ax.lines[-1]
    
    ######################################################
    if '0.' in matplotlib.__version__[0:2]:
        print "The matplotlib version has to be updated to 1.1 or newer"
        return iplot
    
    if '1.0.' in matplotlib.__version__[0:4]:
        print "The matplotlib version has to be updated to 1.1 or newer"
        return iplot
    
    if grid != None:
        ax.grid(b=True, which='major', axis=grid)
    
    matplotlib.pyplot.tight_layout()
    
    return iplot

def pline(iplot, x, y, xlabel='', ylabel='', title=''):
    
    ax = iplot.get_axes()
    
    printLabels(ax, xlabel, ylabel, title)
    
    iplot.set_data(x, y)
    
def createPcolor(ax, x, y, z, xmin, xmax, ymin, ymax, zmin, zmax,
                 xlabel='', ylabel='', title='', ticksize = 9,
                 colormap='jet',cblabel='', cbsize="5%",
                 XAxisAsTime=False):
    
    divider = make_axes_locatable(ax)
    ax_cb = divider.new_horizontal(size=cbsize, pad=0.05)
    fig = ax.get_figure()
    fig.add_axes(ax_cb)
    
    ax.set_xlim([xmin,xmax])
    ax.set_ylim([ymin,ymax])
    
    printLabels(ax, xlabel, ylabel, title)
    
    imesh = ax.pcolormesh(x,y,z.T, vmin=zmin, vmax=zmax, cmap=matplotlib.pyplot.get_cmap(colormap))
    cb =  matplotlib.pyplot.colorbar(imesh, cax=ax_cb)
    cb.set_label(cblabel)
    
#    for tl in ax_cb.get_yticklabels():
#        tl.set_visible(True)
    
    for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontsize(ticksize)
        
    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(ticksize) 
    
    for tick in cb.ax.get_yticklabels():
        tick.set_fontsize(ticksize)
                
    ax_cb.yaxis.tick_right()
    
    if '0.' in matplotlib.__version__[0:2]:
        print "The matplotlib version has to be updated to 1.1 or newer"
        return imesh
    
    if '1.0.' in matplotlib.__version__[0:4]:
        print "The matplotlib version has to be updated to 1.1 or newer"
        return imesh
    
    matplotlib.pyplot.tight_layout()
    
    if XAxisAsTime:
        
        func = lambda x, pos: ('%s') %(datetime.datetime.utcfromtimestamp(x).strftime("%H:%M:%S"))
        ax.xaxis.set_major_formatter(FuncFormatter(func))
        ax.xaxis.set_major_locator(LinearLocator(7))
        
    return imesh

def pcolor(imesh, z, xlabel='', ylabel='', title=''):
    
    z = z.T
    
    ax = imesh.get_axes()
    
    printLabels(ax, xlabel, ylabel, title)
    
    imesh.set_array(z.ravel())

def addpcolor(ax, x, y, z, zmin, zmax, xlabel='', ylabel='', title=''):
    
    printLabels(ax, xlabel, ylabel, title)
    
    imesh = ax.pcolormesh(x,y,z.T,vmin=zmin,vmax=zmax)
    
def draw(fig):
    
    if type(fig) == 'int':
        raise ValueError, "This parameter should be of tpye matplotlib figure"
    
    fig.canvas.draw()