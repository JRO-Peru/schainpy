import numpy
import datetime
import sys

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.ticker import *
import matplotlib.gridspec as gridspec
import matplotlib.cm as cm
import matplotlib.colorbar

def createFigure(id, wintitle, width, height, facecolor="w"):
    figsize = (width,height)
    fig = Figure(figsize=figsize, facecolor=facecolor)

    return fig

def createAxes(fig, nrow, ncol, x, y, ratio):
    width_ratios = []
    for i in range(ncol):
        if i%2==0:
            width_ratios.append(ratio)
        else:
            width_ratios.append(1)
    
    gs = gridspec.GridSpec(nrow, ncol, width_ratios=width_ratios)
    ax = fig.add_subplot(gs[x,y])
    
    return ax

def saveFigure(fig, filename):    
    fig.savefig(filename)


def printLabels(ax, xlabel, ylabel, title):
    
    ax.set_xlabel(xlabel, size=11)
    ax.set_ylabel(ylabel, size=11)
    ax.set_title(title, size=12)

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
    
    imesh = ax.pcolormesh(x,y,z.T, vmin=zmin, vmax=zmax, cmap=cm.get_cmap(colormap))
    cb = fig.colorbar(imesh, cax=ax_cb)
    cb.set_label(cblabel)
    
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
    
    fig.tight_layout()
    
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

def addpcolorbuffer(ax, x, y, z, zmin, zmax, xlabel='', ylabel='', title='', colormap='jet'):
    
    printLabels(ax, xlabel, ylabel, title)
    
    ax.collections.remove(ax.collections[0])
    
    ax.pcolormesh(x,y,z.T,vmin=zmin,vmax=zmax, cmap=matplotlib.pyplot.get_cmap(colormap))


def draw(fig):
    
    if type(fig) == 'int':
        raise ValueError, "This parameter should be of tpye matplotlib figure"
    
    fig.canvas.draw()


def createPline(ax, x, y, xmin, xmax, ymin, ymax, xlabel='', ylabel='', title='',
                ticksize=9, xtick_visible=True, ytick_visible=True,
                nxticks=4, nyticks=10,
                grid=None):
    
    """
    
    Input:
        grid    :    None, 'both', 'x', 'y'
    """
    fig = ax.get_figure()
    ax.set_xlim([xmin,xmax])
    ax.set_ylim([ymin,ymax])
    
    printLabels(ax, xlabel, ylabel, title)
    
    ######################################################
    if (xmax-xmin)<=1:
        xtickspos = numpy.linspace(xmin,xmax,nxticks)
        xtickspos = numpy.array([float("%.1f"%i) for i in xtickspos])
        ax.set_xticks(xtickspos)
    else:
        xtickspos = numpy.arange(nxticks)*int((xmax-xmin)/(nxticks)) + int(xmin)
#         xtickspos = numpy.arange(nxticks)*float(xmax-xmin)/float(nxticks) + int(xmin)
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
    
    ax.plot(x, y)
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
    fig.tight_layout()
    return iplot

def set_linedata(ax, x, y, idline):
    
    ax.lines[idline].set_data(x,y)
    
def pline(iplot, x, y, xlabel='', ylabel='', title=''):
    
    ax = iplot.get_axes()
    
    printLabels(ax, xlabel, ylabel, title)
    
    set_linedata(ax, x, y, idline=0)

def addpline(ax, x, y, color, linestyle, lw):
    
    ax.plot(x,y,color=color,linestyle=linestyle,lw=lw)

def createPmultiline(ax, x, y, xmin, xmax, ymin, ymax, xlabel='', ylabel='', title='', legendlabels=None,
                ticksize=9, xtick_visible=True, ytick_visible=True,
                nxticks=4, nyticks=10,
                grid=None):
    
    """
    
    Input:
        grid    :    None, 'both', 'x', 'y'
    """
    
#     matplotlib.pyplot.ioff()
    fig = ax.get_figure()
      
    lines = ax.plot(x.T, y)
    leg = ax.legend(lines, legendlabels, loc='upper right')
    leg.get_frame().set_alpha(0.5)
    ax.set_xlim([xmin,xmax])
    ax.set_ylim([ymin,ymax]) 
    printLabels(ax, xlabel, ylabel, title)
    
    xtickspos = numpy.arange(nxticks)*int((xmax-xmin)/(nxticks)) + int(xmin)
    ax.set_xticks(xtickspos)
    
    for tick in ax.get_xticklabels():
        tick.set_visible(xtick_visible)
        
    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(ticksize) 
    
    for tick in ax.get_yticklabels():
        tick.set_visible(ytick_visible)
    
    for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontsize(ticksize)
        
    iplot = ax.lines[-1]
    
    if '0.' in matplotlib.__version__[0:2]:
        print "The matplotlib version has to be updated to 1.1 or newer"
        return iplot
    
    if '1.0.' in matplotlib.__version__[0:4]:
        print "The matplotlib version has to be updated to 1.1 or newer"
        return iplot
    
    if grid != None:
        ax.grid(b=True, which='major', axis=grid)
    
#     matplotlib.pyplot.tight_layout()
#     
#     matplotlib.pyplot.ion()
    
    fig.tight_layout()
    
    return iplot


def pmultiline(iplot, x, y, xlabel='', ylabel='', title=''):
    
    ax = iplot.get_axes()
    
    printLabels(ax, xlabel, ylabel, title)
    
    for i in range(len(ax.lines)):
        line = ax.lines[i]
        line.set_data(x[i,:],y)

def createPmultilineYAxis(ax, x, y, xmin, xmax, ymin, ymax, xlabel='', ylabel='', title='', legendlabels=None,
                ticksize=9, xtick_visible=True, ytick_visible=True,
                nxticks=4, nyticks=10, marker='.', markersize=10, linestyle="None", 
                grid=None, XAxisAsTime=False):
    
    
#     matplotlib.pyplot.ioff()
    fig = ax.get_figure()

    lines = ax.plot(x, y.T, linestyle='None', marker='.', markersize=markersize)
    leg = ax.legend(lines, legendlabels, loc='upper left', bbox_to_anchor=(1.01, 1.00), numpoints=1, handlelength=1.5, \
                    handletextpad=0.5, borderpad=0.5, labelspacing=0.5, borderaxespad=0.)
    
    for label in leg.get_texts(): label.set_fontsize(9)
    
    ax.set_xlim([xmin,xmax])
    ax.set_ylim([ymin,ymax]) 
    printLabels(ax, xlabel, ylabel, title)
    
#    xtickspos = numpy.arange(nxticks)*int((xmax-xmin)/(nxticks)) + int(xmin)
#    ax.set_xticks(xtickspos)
    
    for tick in ax.get_xticklabels():
        tick.set_visible(xtick_visible)
        
    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(ticksize) 
    
    for tick in ax.get_yticklabels():
        tick.set_visible(ytick_visible)
    
    for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontsize(ticksize)
        
    iplot = ax.lines[-1]
    
    if '0.' in matplotlib.__version__[0:2]:
        print "The matplotlib version has to be updated to 1.1 or newer"
        return iplot
    
    if '1.0.' in matplotlib.__version__[0:4]:
        print "The matplotlib version has to be updated to 1.1 or newer"
        return iplot
    
    if grid != None:
        ax.grid(b=True, which='major', axis=grid)
    
#     matplotlib.pyplot.tight_layout()
    
    if XAxisAsTime:
        
        func = lambda x, pos: ('%s') %(datetime.datetime.utcfromtimestamp(x).strftime("%H:%M:%S"))
        ax.xaxis.set_major_formatter(FuncFormatter(func))
        ax.xaxis.set_major_locator(LinearLocator(7))
    
    fig.tight_layout()
#     matplotlib.pyplot.ion()
    
    return iplot

def pmultilineyaxis(iplot, x, y, xlabel='', ylabel='', title=''):
    
    ax = iplot.get_axes()
    
    printLabels(ax, xlabel, ylabel, title)
    
    for i in range(len(ax.lines)):
        line = ax.lines[i]
        line.set_data(x,y[i,:])