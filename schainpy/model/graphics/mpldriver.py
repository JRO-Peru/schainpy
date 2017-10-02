import numpy
import datetime
import sys
import matplotlib

if 'linux' in sys.platform:
    matplotlib.use("GTK3Agg")

if 'darwin' in sys.platform:
    matplotlib.use('TKAgg')
#Qt4Agg', 'GTK', 'GTKAgg', 'ps', 'agg', 'cairo', 'MacOSX', 'GTKCairo', 'WXAgg', 'template', 'TkAgg', 'GTK3Cairo', 'GTK3Agg', 'svg', 'WebAgg', 'CocoaAgg', 'emf', 'gdk', 'WX'
import matplotlib.pyplot

from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.ticker import FuncFormatter, LinearLocator

###########################################
#Actualizacion de las funciones del driver
###########################################

# create jro colormap

jet_values = matplotlib.pyplot.get_cmap("jet", 100)(numpy.arange(100))[10:90]
blu_values = matplotlib.pyplot.get_cmap("seismic_r", 20)(numpy.arange(20))[10:15]
ncmap = matplotlib.colors.LinearSegmentedColormap.from_list("jro", numpy.vstack((blu_values, jet_values)))
matplotlib.pyplot.register_cmap(cmap=ncmap)

def createFigure(id, wintitle, width, height, facecolor="w", show=True, dpi = 80):

    matplotlib.pyplot.ioff()

    fig = matplotlib.pyplot.figure(num=id, facecolor=facecolor, figsize=(1.0*width/dpi, 1.0*height/dpi))
    fig.canvas.manager.set_window_title(wintitle)
#     fig.canvas.manager.resize(width, height)
    matplotlib.pyplot.ion()

    if show:
        matplotlib.pyplot.show()

    return fig

def closeFigure(show=False, fig=None):

#     matplotlib.pyplot.ioff()
#     matplotlib.pyplot.pause(0)

    if show:
        matplotlib.pyplot.show()

    if fig != None:
        matplotlib.pyplot.close(fig)
#         matplotlib.pyplot.pause(0)
#         matplotlib.pyplot.ion()

        return

    matplotlib.pyplot.close("all")
#     matplotlib.pyplot.pause(0)
#     matplotlib.pyplot.ion()

    return

def saveFigure(fig, filename):

#     matplotlib.pyplot.ioff()
    fig.savefig(filename, dpi=matplotlib.pyplot.gcf().dpi)
#     matplotlib.pyplot.ion()

def clearFigure(fig):

    fig.clf()

def setWinTitle(fig, title):

    fig.canvas.manager.set_window_title(title)

def setTitle(fig, title):

    fig.suptitle(title)

def createAxes(fig, nrow, ncol, xpos, ypos, colspan, rowspan, polar=False):

    matplotlib.pyplot.ioff()
    matplotlib.pyplot.figure(fig.number)
    axes = matplotlib.pyplot.subplot2grid((nrow, ncol),
                                        (xpos, ypos),
                                        colspan=colspan,
                                        rowspan=rowspan,
                                        polar=polar)

    axes.grid(True)

    matplotlib.pyplot.ion()
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
    ax.set_title(title, size=8)

def createPline(ax, x, y, xmin, xmax, ymin, ymax, xlabel='', ylabel='', title='',
                ticksize=9, xtick_visible=True, ytick_visible=True,
                nxticks=4, nyticks=10,
                grid=None,color='blue'):

    """

    Input:
        grid    :    None, 'both', 'x', 'y'
    """

    matplotlib.pyplot.ioff()

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

    ax.plot(x, y, color=color)
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

    matplotlib.pyplot.ion()

    return iplot

def set_linedata(ax, x, y, idline):

    ax.lines[idline].set_data(x,y)

def pline(iplot, x, y, xlabel='', ylabel='', title=''):

    ax = iplot.get_axes()

    printLabels(ax, xlabel, ylabel, title)

    set_linedata(ax, x, y, idline=0)

def addpline(ax, x, y, color, linestyle, lw):

    ax.plot(x,y,color=color,linestyle=linestyle,lw=lw)


def createPcolor(ax, x, y, z, xmin, xmax, ymin, ymax, zmin, zmax,
                 xlabel='', ylabel='', title='', ticksize = 9,
                 colormap='jet',cblabel='', cbsize="5%",
                 XAxisAsTime=False):

    matplotlib.pyplot.ioff()

    divider = make_axes_locatable(ax)
    ax_cb = divider.new_horizontal(size=cbsize, pad=0.05)
    fig = ax.get_figure()
    fig.add_axes(ax_cb)

    ax.set_xlim([xmin,xmax])
    ax.set_ylim([ymin,ymax])

    printLabels(ax, xlabel, ylabel, title)

    z = numpy.ma.masked_invalid(z)
    cmap=matplotlib.pyplot.get_cmap(colormap)
    cmap.set_bad('white',1.)
    imesh = ax.pcolormesh(x,y,z.T, vmin=zmin, vmax=zmax, cmap=cmap)
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

    ax.grid(True)
    matplotlib.pyplot.ion()
    return imesh

def pcolor(imesh, z, xlabel='', ylabel='', title=''):

    z = numpy.ma.masked_invalid(z)
    
    cmap=matplotlib.pyplot.get_cmap('jet')
    cmap.set_bad('white',1.)

    z = z.T
    ax = imesh.get_axes()
    printLabels(ax, xlabel, ylabel, title)
    imesh.set_array(z.ravel())
    ax.grid(True)


def addpcolor(ax, x, y, z, zmin, zmax, xlabel='', ylabel='', title='', colormap='jet'):

    printLabels(ax, xlabel, ylabel, title)
    z = numpy.ma.masked_invalid(z)
    cmap=matplotlib.pyplot.get_cmap(colormap)
    cmap.set_bad('white',1.)
    ax.pcolormesh(x,y,z.T,vmin=zmin,vmax=zmax, cmap=matplotlib.pyplot.get_cmap(colormap))
    ax.grid(True)

def addpcolorbuffer(ax, x, y, z, zmin, zmax, xlabel='', ylabel='', title='', colormap='jet'):

    printLabels(ax, xlabel, ylabel, title)

    ax.collections.remove(ax.collections[0])

    z = numpy.ma.masked_invalid(z)
    
    cmap=matplotlib.pyplot.get_cmap(colormap)
    cmap.set_bad('white',1.)

    ax.pcolormesh(x,y,z.T,vmin=zmin,vmax=zmax, cmap=cmap)
    ax.grid(True)


def createPmultiline(ax, x, y, xmin, xmax, ymin, ymax, xlabel='', ylabel='', title='', legendlabels=None,
                ticksize=9, xtick_visible=True, ytick_visible=True,
                nxticks=4, nyticks=10,
                grid=None):

    """

    Input:
        grid    :    None, 'both', 'x', 'y'
    """

    matplotlib.pyplot.ioff()

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

    matplotlib.pyplot.tight_layout()

    matplotlib.pyplot.ion()

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

    """

    Input:
        grid    :    None, 'both', 'x', 'y'
    """

    matplotlib.pyplot.ioff()

#    lines = ax.plot(x, y.T, marker=marker,markersize=markersize,linestyle=linestyle)
    lines = ax.plot(x, y.T)
#     leg = ax.legend(lines, legendlabels, loc=2, bbox_to_anchor=(1.01, 1.00), numpoints=1, handlelength=1.5, \
#                     handletextpad=0.5, borderpad=0.5, labelspacing=0.5, borderaxespad=0.)

    leg = ax.legend(lines, legendlabels,
                    loc='upper right', bbox_to_anchor=(1.16, 1), borderaxespad=0)

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

    matplotlib.pyplot.tight_layout()

    if XAxisAsTime:

        func = lambda x, pos: ('%s') %(datetime.datetime.utcfromtimestamp(x).strftime("%H:%M:%S"))
        ax.xaxis.set_major_formatter(FuncFormatter(func))
        ax.xaxis.set_major_locator(LinearLocator(7))

    matplotlib.pyplot.ion()

    return iplot

def pmultilineyaxis(iplot, x, y, xlabel='', ylabel='', title=''):

    ax = iplot.get_axes()
    printLabels(ax, xlabel, ylabel, title)

    for i in range(len(ax.lines)):
        line = ax.lines[i]
        line.set_data(x,y[i,:])

def createPolar(ax, x, y,
                xlabel='', ylabel='', title='', ticksize = 9,
                 colormap='jet',cblabel='', cbsize="5%",
                 XAxisAsTime=False):

    matplotlib.pyplot.ioff()

    ax.plot(x,y,'bo', markersize=5)
#     ax.set_rmax(90)
    ax.set_ylim(0,90)
    ax.set_yticks(numpy.arange(0,90,20))
#     ax.text(0, -110, ylabel, rotation='vertical', va ='center', ha = 'center' ,size='11')
#     ax.text(0, 50, ylabel, rotation='vertical', va ='center', ha = 'left' ,size='11')
#     ax.text(100, 100, 'example', ha='left', va='center', rotation='vertical')
    ax.yaxis.labelpad = 230
    printLabels(ax, xlabel, ylabel, title)
    iplot = ax.lines[-1]

    if '0.' in matplotlib.__version__[0:2]:
        print "The matplotlib version has to be updated to 1.1 or newer"
        return iplot

    if '1.0.' in matplotlib.__version__[0:4]:
        print "The matplotlib version has to be updated to 1.1 or newer"
        return iplot

#     if grid != None:
#         ax.grid(b=True, which='major', axis=grid)

    matplotlib.pyplot.tight_layout()

    matplotlib.pyplot.ion()


    return iplot

def polar(iplot, x, y, xlabel='', ylabel='', title=''):

    ax = iplot.get_axes()

#     ax.text(0, -110, ylabel, rotation='vertical', va ='center', ha = 'center',size='11')
    printLabels(ax, xlabel, ylabel, title)

    set_linedata(ax, x, y, idline=0)

def draw(fig):

    if type(fig) == 'int':
        raise ValueError, "Error drawing: Fig parameter should be a matplotlib figure object figure"

    fig.canvas.draw()

def pause(interval=0.000001):

    matplotlib.pyplot.pause(interval)
