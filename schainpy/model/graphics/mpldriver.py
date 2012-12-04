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

def init(idfigure, wintitle, width, height, facecolor="w"):
    
    matplotlib.pyplot.ioff()
    fig = matplotlib.pyplot.matplotlib.pyplot.figure(num=idfigure, facecolor=facecolor)
    fig.canvas.manager.set_window_title(wintitle)
    fig.canvas.manager.resize(width, height)
    matplotlib.pyplot.ion()
    
    return fig

def setWinTitle(fig, title):
    
    fig.canvas.manager.set_window_title(title)

def setTitle(idfigure, title):
    fig = matplotlib.pyplot.figure(idfigure)
    fig.suptitle(title)

def makeAxes(idfigure, nrow, ncol, xpos, ypos, colspan, rowspan):
    fig = matplotlib.pyplot.figure(idfigure)
    ax = matplotlib.pyplot.subplot2grid((nrow, ncol), (xpos, ypos), colspan=colspan, rowspan=rowspan)
    return ax

def setTextFromAxes(idfigure, ax, title):
    fig = matplotlib.pyplot.figure(idfigure)
    ax.annotate(title, xy=(.1, .99),
                xycoords='figure fraction',
                horizontalalignment='left', verticalalignment='top',
                fontsize=10)
    
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

def pcolor(ax, x, y, z, xmin, xmax, ymin, ymax, zmin, zmax, xlabel, ylabel, title, firsttime, mesh):
    
    if firsttime:
        divider = make_axes_locatable(ax)
        ax_cb = divider.new_horizontal(size="4%", pad=0.05)
        fig1 = ax.get_figure()
        fig1.add_axes(ax_cb)
        
        ax.set_xlim([xmin,xmax])
        ax.set_ylim([ymin,ymax])
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        print x
        imesh=ax.pcolormesh(x,y,z.T,vmin=zmin,vmax=zmax)
        matplotlib.pyplot.colorbar(imesh, cax=ax_cb)
        ax_cb.yaxis.tick_right()
        for tl in ax_cb.get_yticklabels():
            tl.set_visible(True)
        ax_cb.yaxis.tick_right()
        matplotlib.pyplot.tight_layout()
        return imesh
    else:
#        ax.set_xlim([xmin,xmax])
#        ax.set_ylim([ymin,ymax])
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        
        z = z.T
#        z = z[0:-1,0:-1]
        mesh.set_array(z.ravel())
        
        return mesh

###########################################
#Actualizacion de las funciones del driver
###########################################

def createFigure(idfigure, wintitle, width, height, facecolor="w"):
    
    matplotlib.pyplot.ioff()
    fig = matplotlib.pyplot.matplotlib.pyplot.figure(num=idfigure, facecolor=facecolor)
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
    
    ######################################################
    if grid != None:
        ax.grid(b=True, which='major', axis=grid)
    
    matplotlib.pyplot.tight_layout()
    
    iplot = ax.lines[-1]
    
    return iplot

def pline(iplot, x, y, xlabel='', ylabel='', title=''):
    
    ax = iplot.get_axes()
    
    printLabels(ax, xlabel, ylabel, title)
    
    iplot.set_data(x, y)
    
def createPcolor(ax, x, y, z, xmin, xmax, ymin, ymax, zmin, zmax,
                 xlabel='', ylabel='', title='', ticksize = 9,
                 cblabel='', cbsize="5%",
                 XAxisAsTime=False):
    
    divider = make_axes_locatable(ax)
    ax_cb = divider.new_horizontal(size=cbsize, pad=0.05)
    fig = ax.get_figure()
    fig.add_axes(ax_cb)
    
    ax.set_xlim([xmin,xmax])
    ax.set_ylim([ymin,ymax])
    
    printLabels(ax, xlabel, ylabel, title)
    
    imesh = ax.pcolormesh(x,y,z.T,vmin=zmin,vmax=zmax)
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
    matplotlib.pyplot.tight_layout()
    
    if XAxisAsTime:
        
        func = lambda x, pos: ('%s') %(datetime.datetime.fromtimestamp(x).strftime("%H:%M:%S"))
        ax.xaxis.set_major_formatter(FuncFormatter(func))
        ax.xaxis.set_major_locator(LinearLocator(7))
        
#        seconds = numpy.array([xmin, xmax])
#        datesList = map(datetime.datetime.fromtimestamp, seconds)
#        ax.set_xlim([datesList[0],datesList[-1]])
#        ax.xaxis.set_major_locator(MinuteLocator(numpy.arange(0,61,10)))
#        ax.xaxis.set_minor_locator(SecondLocator(numpy.arange(0,61,60)))
#        ax.xaxis.set_major_formatter(DateFormatter("%H:%M:%S"))
#        xdateList = map(datetime.datetime.fromtimestamp, x)
#        xdate = matplotlib.dates.date2num(xdateList)
#        x = xdate
        
#        labels = []
#        for item in ax.xaxis.get_ticklabels():
#            stri = item.get_text()
#            text = datetime.datetime.fromtimestamp(float(stri))
#            labels.append(text)
#            
#        ax.xaxis.set_ticklabels(labels)
    return imesh

def pcolor(imesh, z, xlabel='', ylabel='', title=''):
    
    z = z.T
    
    ax = imesh.get_axes()
    
    printLabels(ax, xlabel, ylabel, title)
    
    imesh.set_array(z.ravel())

def addpcolor(ax, x, y, z, zmin, zmax, xlabel='', ylabel='', title=''):
    
#    xdateList = map(datetime.datetime.fromtimestamp, x)
#    xdate = matplotlib.dates.date2num(xdateList)
    
    printLabels(ax, xlabel, ylabel, title)
    
    imesh = ax.pcolormesh(x,y,z.T,vmin=zmin,vmax=zmax)
    
def draw(fig):
    
    if type(fig) == 'int':
        raise ValueError, "This parameter should be of tpye matplotlib figure"
    
    fig.canvas.draw()