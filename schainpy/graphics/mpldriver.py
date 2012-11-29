import matplotlib
matplotlib.use("TKAgg")
import matplotlib.pyplot
import scitools.numpyutils
from mpl_toolkits.axes_grid1 import make_axes_locatable

def init(idfigure, wintitle, width, height):
    matplotlib.pyplot.ioff()
    fig = matplotlib.pyplot.matplotlib.pyplot.figure(num=idfigure, facecolor="w")
    fig.canvas.manager.set_window_title(wintitle)
    fig.canvas.manager.resize(width,height)
    matplotlib.pyplot.ion()
    return fig

def setWinTitle(fig, title):
    fig.canvas.manager.set_window_title(title)

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

def pcolor(ax, x, y, z, xmin, xmax, ymin, ymax, zmin, zmax, xlabel, ylabel, title, firsttime, mesh):
    if firsttime:
        divider = make_axes_locatable(ax)
        ax_cb = divider.new_horizontal(size="5%", pad=0.05)
        fig1 = ax.get_figure()
        fig1.add_axes(ax_cb)
        
        ax.set_xlim([xmin,xmax])
        ax.set_ylim([ymin,ymax])
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        
        imesh=ax.pcolormesh(x,y,z.T,vmin=zmin,vmax=zmax)
        matplotlib.pyplot.colorbar(imesh, cax=ax_cb)
        ax_cb.yaxis.tick_right()
        for tl in ax_cb.get_yticklabels():
            tl.set_visible(True)
        ax_cb.yaxis.tick_right()
        matplotlib.pyplot.tight_layout()
        return imesh
    else:
        z = z.T
        z = z[0:-1,0:-1]
        mesh.set_array(z.ravel())
        
        return mesh



    