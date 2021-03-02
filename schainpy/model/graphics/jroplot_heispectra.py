# Copyright (c) 2012-2020 Jicamarca Radio Observatory
# All rights reserved.
#
# Distributed under the terms of the BSD 3-clause license.
"""Classes to plo Specra Heis data

"""

import numpy

from schainpy.model.graphics.jroplot_base import Plot, plt


class SpectraHeisPlot(Plot):

    CODE = 'spc_heis'

    def setup(self):

        self.nplots = len(self.data.channels)
        self.ncols = int(numpy.sqrt(self.nplots) + 0.9)
        self.nrows = int((1.0 * self.nplots / self.ncols) + 0.9)
        self.height = 2.6 * self.nrows
        self.width = 3.5 * self.ncols
        self.plots_adjust.update({'wspace': 0.4, 'hspace':0.4, 'left': 0.1, 'right': 0.95, 'bottom': 0.08})
        self.ylabel = 'Intensity [dB]'
        self.xlabel = 'Frequency [KHz]'
        self.colorbar = False

    def update(self, dataOut):

        data = {}
        meta = {}
        spc = 10*numpy.log10(dataOut.data_spc / dataOut.normFactor)
        data['spc_heis'] = spc
    
        return data, meta 

    def plot(self):

        c = 3E8
        deltaHeight = self.data.yrange[1] - self.data.yrange[0]
        x = numpy.arange(-1*len(self.data.yrange)/2., len(self.data.yrange)/2.)*(c/(2*deltaHeight*len(self.data.yrange)*1000))
        self.y = self.data[-1]['spc_heis']
        self.titles = []

        for n, ax in enumerate(self.axes):
            ychannel = self.y[n,:]
            if ax.firsttime:
                self.xmin = min(x) if self.xmin is None else self.xmin
                self.xmax = max(x) if self.xmax is None else self.xmax
                ax.plt = ax.plot(x, ychannel, lw=1, color='b')[0]
            else:
                ax.plt.set_data(x, ychannel)

            self.titles.append("Channel {}: {:4.2f}dB".format(n, numpy.max(ychannel)))


class RTIHeisPlot(Plot):

    CODE = 'rti_heis'

    def setup(self):

        self.xaxis = 'time'
        self.ncols = 1
        self.nrows = 1
        self.nplots = 1
        self.ylabel = 'Intensity [dB]'
        self.xlabel = 'Time'
        self.titles = ['RTI']
        self.colorbar = False
        self.height = 4
        self.plots_adjust.update({'right': 0.85 })

    def update(self, dataOut):

        data = {}
        meta = {}
        spc = dataOut.data_spc / dataOut.normFactor
        spc = 10*numpy.log10(numpy.average(spc, axis=1))
        data['rti_heis'] = spc
    
        return data, meta 

    def plot(self):

        x = self.data.times
        Y = self.data['rti_heis']

        if self.axes[0].firsttime:
            self.ymin = numpy.nanmin(Y) - 5 if self.ymin == None else self.ymin
            self.ymax = numpy.nanmax(Y) + 5 if self.ymax == None else self.ymax
            for ch in self.data.channels:
                y = Y[ch]
                self.axes[0].plot(x, y, lw=1, label='Ch{}'.format(ch))
            plt.legend(bbox_to_anchor=(1.18, 1.0))
        else:
            for ch in self.data.channels:
                y = Y[ch]
                self.axes[0].lines[ch].set_data(x, y)
