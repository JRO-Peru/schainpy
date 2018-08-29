'''
New Plots Operations

@author: juan.espinoza@jro.igp.gob.pe
'''


import time
import datetime
import numpy

from schainpy.model.graphics.jroplot_base import Plot, plt
from schainpy.utils import log

EARTH_RADIUS = 6.3710e3


def ll2xy(lat1, lon1, lat2, lon2):

    p = 0.017453292519943295
    a = 0.5 - numpy.cos((lat2 - lat1) * p)/2 + numpy.cos(lat1 * p) * \
        numpy.cos(lat2 * p) * (1 - numpy.cos((lon2 - lon1) * p)) / 2
    r = 12742 * numpy.arcsin(numpy.sqrt(a))
    theta = numpy.arctan2(numpy.sin((lon2-lon1)*p)*numpy.cos(lat2*p), numpy.cos(lat1*p)
                          * numpy.sin(lat2*p)-numpy.sin(lat1*p)*numpy.cos(lat2*p)*numpy.cos((lon2-lon1)*p))
    theta = -theta + numpy.pi/2
    return r*numpy.cos(theta), r*numpy.sin(theta)


def km2deg(km):
    '''
    Convert distance in km to degrees
    '''

    return numpy.rad2deg(km/EARTH_RADIUS)


class SpectraPlot(Plot):
    '''
    Plot for Spectra data
    '''

    CODE = 'spc'
    colormap = 'jro'

    def setup(self):
        self.nplots = len(self.data.channels)
        self.ncols = int(numpy.sqrt(self.nplots) + 0.9)
        self.nrows = int((1.0 * self.nplots / self.ncols) + 0.9)
        self.width = 3.4 * self.ncols
        self.height = 3 * self.nrows
        self.cb_label = 'dB'
        if self.showprofile:
            self.width += 0.8 * self.ncols

        self.ylabel = 'Range [km]'

    def plot(self):
        if self.xaxis == "frequency":
            x = self.data.xrange[0]
            self.xlabel = "Frequency (kHz)"
        elif self.xaxis == "time":
            x = self.data.xrange[1]
            self.xlabel = "Time (ms)"
        else:
            x = self.data.xrange[2]
            self.xlabel = "Velocity (m/s)"

        if self.CODE == 'spc_mean':
            x = self.data.xrange[2]
            self.xlabel = "Velocity (m/s)"

        self.titles = []

        y = self.data.heights
        self.y = y
        z = self.data['spc']

        for n, ax in enumerate(self.axes):
            noise = self.data['noise'][n][-1]
            if self.CODE == 'spc_mean':
                mean = self.data['mean'][n][-1]
            if ax.firsttime:
                self.xmax = self.xmax if self.xmax else numpy.nanmax(x)
                self.xmin = self.xmin if self.xmin else -self.xmax
                self.zmin = self.zmin if self.zmin else numpy.nanmin(z)
                self.zmax = self.zmax if self.zmax else numpy.nanmax(z)
                ax.plt = ax.pcolormesh(x, y, z[n].T,
                                       vmin=self.zmin,
                                       vmax=self.zmax,
                                       cmap=plt.get_cmap(self.colormap)
                                       )

                if self.showprofile:
                    ax.plt_profile = self.pf_axes[n].plot(
                        self.data['rti'][n][-1], y)[0]
                    ax.plt_noise = self.pf_axes[n].plot(numpy.repeat(noise, len(y)), y,
                                                        color="k", linestyle="dashed", lw=1)[0]
                if self.CODE == 'spc_mean':
                    ax.plt_mean = ax.plot(mean, y, color='k')[0]
            else:
                ax.plt.set_array(z[n].T.ravel())
                if self.showprofile:
                    ax.plt_profile.set_data(self.data['rti'][n][-1], y)
                    ax.plt_noise.set_data(numpy.repeat(noise, len(y)), y)
                if self.CODE == 'spc_mean':
                    ax.plt_mean.set_data(mean, y)

            self.titles.append('CH {}: {:3.2f}dB'.format(n, noise))


class CrossSpectraPlot(Plot):

    CODE = 'cspc'
    colormap = 'jet'
    zmin_coh = None
    zmax_coh = None
    zmin_phase = None
    zmax_phase = None

    def setup(self):

        self.ncols = 4
        self.nrows = len(self.data.pairs)
        self.nplots = self.nrows * 4
        self.width = 3.4 * self.ncols
        self.height = 3 * self.nrows
        self.ylabel = 'Range [km]'
        self.showprofile = False

    def plot(self):

        if self.xaxis == "frequency":
            x = self.data.xrange[0]
            self.xlabel = "Frequency (kHz)"
        elif self.xaxis == "time":
            x = self.data.xrange[1]
            self.xlabel = "Time (ms)"
        else:
            x = self.data.xrange[2]
            self.xlabel = "Velocity (m/s)"
        
        self.titles = []

        y = self.data.heights
        self.y = y
        spc = self.data['spc']
        cspc = self.data['cspc']

        for n in range(self.nrows):
            noise = self.data['noise'][n][-1]
            pair = self.data.pairs[n]
            ax = self.axes[4 * n]
            spc0 = 10.*numpy.log10(spc[pair[0]]/self.data.factor)          
            if ax.firsttime:                                               
                self.xmax = self.xmax if self.xmax else numpy.nanmax(x)    
                self.xmin = self.xmin if self.xmin else -self.xmax         
                self.zmin = self.zmin if self.zmin else numpy.nanmin(spc)  
                self.zmax = self.zmax if self.zmax else numpy.nanmax(spc)  
                ax.plt = ax.pcolormesh(x , y , spc0.T,
                                       vmin=self.zmin,
                                       vmax=self.zmax,
                                       cmap=plt.get_cmap(self.colormap)
                                       )                                   
            else:                                                          
                ax.plt.set_array(spc0.T.ravel())
            self.titles.append('CH {}: {:3.2f}dB'.format(pair[0], noise))

            ax = self.axes[4 * n + 1]
            spc1 = 10.*numpy.log10(spc[pair[1]]/self.data.factor)
            if ax.firsttime:
                ax.plt = ax.pcolormesh(x , y, spc1.T,
                                       vmin=self.zmin,
                                       vmax=self.zmax,
                                       cmap=plt.get_cmap(self.colormap)
                                       )
            else: 
                ax.plt.set_array(spc1.T.ravel())
            self.titles.append('CH {}: {:3.2f}dB'.format(pair[1], noise))
            
            out = cspc[n] / numpy.sqrt(spc[pair[0]] * spc[pair[1]])
            coh = numpy.abs(out)
            phase = numpy.arctan2(out.imag, out.real) * 180 / numpy.pi

            ax = self.axes[4 * n + 2]
            if ax.firsttime:
                ax.plt = ax.pcolormesh(x, y, coh.T,
                                       vmin=0,
                                       vmax=1,
                                       cmap=plt.get_cmap(self.colormap_coh)
                                       )
            else:
                ax.plt.set_array(coh.T.ravel())
            self.titles.append(
                'Coherence Ch{} * Ch{}'.format(pair[0], pair[1]))
                                   
            ax = self.axes[4 * n + 3]
            if ax.firsttime:
                ax.plt = ax.pcolormesh(x, y, phase.T,
                                       vmin=-180,
                                       vmax=180,
                                       cmap=plt.get_cmap(self.colormap_phase) 
                                       )
            else:
                ax.plt.set_array(phase.T.ravel())
            self.titles.append('Phase CH{} * CH{}'.format(pair[0], pair[1]))


class SpectraMeanPlot(SpectraPlot):
    '''
    Plot for Spectra and Mean
    '''
    CODE = 'spc_mean'
    colormap = 'jro'


class RTIPlot(Plot):
    '''
    Plot for RTI data
    '''

    CODE = 'rti'
    colormap = 'jro'

    def setup(self):
        self.xaxis = 'time'
        self.ncols = 1
        self.nrows = len(self.data.channels)
        self.nplots = len(self.data.channels)
        self.ylabel = 'Range [km]'
        self.cb_label = 'dB'
        self.titles = ['{} Channel {}'.format(
            self.CODE.upper(), x) for x in range(self.nrows)]

    def plot(self):
        self.x = self.data.times
        self.y = self.data.heights
        self.z = self.data[self.CODE]
        self.z = numpy.ma.masked_invalid(self.z)

        if self.decimation is None:
            x, y, z = self.fill_gaps(self.x, self.y, self.z)
        else:
            x, y, z = self.fill_gaps(*self.decimate())

        for n, ax in enumerate(self.axes):
            self.zmin = self.zmin if self.zmin else numpy.min(self.z)
            self.zmax = self.zmax if self.zmax else numpy.max(self.z)
            if ax.firsttime:
                ax.plt = ax.pcolormesh(x, y, z[n].T,
                                       vmin=self.zmin,
                                       vmax=self.zmax,
                                       cmap=plt.get_cmap(self.colormap)
                                       )
                if self.showprofile:
                    ax.plot_profile = self.pf_axes[n].plot(
                        self.data['rti'][n][-1], self.y)[0]
                    ax.plot_noise = self.pf_axes[n].plot(numpy.repeat(self.data['noise'][n][-1], len(self.y)), self.y,
                                                         color="k", linestyle="dashed", lw=1)[0]
            else:
                ax.collections.remove(ax.collections[0])
                ax.plt = ax.pcolormesh(x, y, z[n].T,
                                       vmin=self.zmin,
                                       vmax=self.zmax,
                                       cmap=plt.get_cmap(self.colormap)
                                       )
                if self.showprofile:
                    ax.plot_profile.set_data(self.data['rti'][n][-1], self.y)
                    ax.plot_noise.set_data(numpy.repeat(
                        self.data['noise'][n][-1], len(self.y)), self.y)


class CoherencePlot(RTIPlot):
    '''
    Plot for Coherence data
    '''

    CODE = 'coh'

    def setup(self):
        self.xaxis = 'time'
        self.ncols = 1
        self.nrows = len(self.data.pairs)
        self.nplots = len(self.data.pairs)
        self.ylabel = 'Range [km]'
        if self.CODE == 'coh':
            self.cb_label = ''
            self.titles = [
                'Coherence Map Ch{} * Ch{}'.format(x[0], x[1]) for x in self.data.pairs]
        else:
            self.cb_label = 'Degrees'
            self.titles = [
                'Phase Map Ch{} * Ch{}'.format(x[0], x[1]) for x in self.data.pairs]


class PhasePlot(CoherencePlot):
    '''
    Plot for Phase map data
    '''

    CODE = 'phase'
    colormap = 'seismic'


class NoisePlot(Plot):
    '''
    Plot for noise 
    '''

    CODE = 'noise'

    def setup(self):
        self.xaxis = 'time'
        self.ncols = 1
        self.nrows = 1
        self.nplots = 1
        self.ylabel = 'Intensity [dB]'
        self.titles = ['Noise']
        self.colorbar = False

    def plot(self):

        x = self.data.times
        xmin = self.data.min_time
        xmax = xmin + self.xrange * 60 * 60
        Y = self.data[self.CODE]

        if self.axes[0].firsttime:
            for ch in self.data.channels:
                y = Y[ch]
                self.axes[0].plot(x, y, lw=1, label='Ch{}'.format(ch))
            plt.legend()
        else:
            for ch in self.data.channels:
                y = Y[ch]
                self.axes[0].lines[ch].set_data(x, y)

        self.ymin = numpy.nanmin(Y) - 5
        self.ymax = numpy.nanmax(Y) + 5


class SnrPlot(RTIPlot):
    '''
    Plot for SNR Data
    '''

    CODE = 'snr'
    colormap = 'jet'


class DopplerPlot(RTIPlot):
    '''
    Plot for DOPPLER Data
    '''

    CODE = 'dop'
    colormap = 'jet'


class SkyMapPlot(Plot):
    '''
    Plot for meteors detection data
    '''

    CODE = 'param'

    def setup(self):

        self.ncols = 1
        self.nrows = 1
        self.width = 7.2
        self.height = 7.2
        self.nplots = 1
        self.xlabel = 'Zonal Zenith Angle (deg)'
        self.ylabel = 'Meridional Zenith Angle (deg)'
        self.polar = True
        self.ymin = -180
        self.ymax = 180
        self.colorbar = False

    def plot(self):

        arrayParameters = numpy.concatenate(self.data['param'])
        error = arrayParameters[:, -1]
        indValid = numpy.where(error == 0)[0]
        finalMeteor = arrayParameters[indValid, :]
        finalAzimuth = finalMeteor[:, 3]
        finalZenith = finalMeteor[:, 4]

        x = finalAzimuth * numpy.pi / 180
        y = finalZenith

        ax = self.axes[0]

        if ax.firsttime:
            ax.plot = ax.plot(x, y, 'bo', markersize=5)[0]
        else:
            ax.plot.set_data(x, y)

        dt1 = self.getDateTime(self.data.min_time).strftime('%y/%m/%d %H:%M:%S')
        dt2 = self.getDateTime(self.data.max_time).strftime('%y/%m/%d %H:%M:%S')
        title = 'Meteor Detection Sky Map\n %s - %s \n Number of events: %5.0f\n' % (dt1,
                                                                                     dt2,
                                                                                     len(x))
        self.titles[0] = title


class ParametersPlot(RTIPlot):
    '''
    Plot for data_param object
    '''

    CODE = 'param'
    colormap = 'seismic'

    def setup(self):
        self.xaxis = 'time'
        self.ncols = 1
        self.nrows = self.data.shape(self.CODE)[0]
        self.nplots = self.nrows
        if self.showSNR:
            self.nrows += 1
            self.nplots += 1

        self.ylabel = 'Height [km]'
        if not self.titles:
            self.titles = self.data.parameters \
                if self.data.parameters else ['Param {}'.format(x) for x in range(self.nrows)]
            if self.showSNR:
                self.titles.append('SNR')

    def plot(self):
        self.data.normalize_heights()
        self.x = self.data.times
        self.y = self.data.heights
        if self.showSNR:
            self.z = numpy.concatenate(
                (self.data[self.CODE], self.data['snr'])
            )
        else:
            self.z = self.data[self.CODE]

        self.z = numpy.ma.masked_invalid(self.z)

        if self.decimation is None:
            x, y, z = self.fill_gaps(self.x, self.y, self.z)
        else:
            x, y, z = self.fill_gaps(*self.decimate())

        for n, ax in enumerate(self.axes):

            self.zmax = self.zmax if self.zmax is not None else numpy.max(
                self.z[n])
            self.zmin = self.zmin if self.zmin is not None else numpy.min(
                self.z[n])

            if ax.firsttime:
                if self.zlimits is not None:
                    self.zmin, self.zmax = self.zlimits[n]

                ax.plt = ax.pcolormesh(x, y, z[n].T * self.factors[n],
                                       vmin=self.zmin,
                                       vmax=self.zmax,
                                       cmap=self.cmaps[n]
                                       )
            else:
                if self.zlimits is not None:
                    self.zmin, self.zmax = self.zlimits[n]
                ax.collections.remove(ax.collections[0])
                ax.plt = ax.pcolormesh(x, y, z[n].T * self.factors[n],
                                       vmin=self.zmin,
                                       vmax=self.zmax,
                                       cmap=self.cmaps[n]
                                       )


class OutputPlot(ParametersPlot):
    '''
    Plot data_output object
    '''

    CODE = 'output'
    colormap = 'seismic'


class PolarMapPlot(Plot):
    '''
    Plot for weather radar
    '''

    CODE = 'param'
    colormap = 'seismic'

    def setup(self):
        self.ncols = 1
        self.nrows = 1
        self.width = 9
        self.height = 8
        self.mode = self.data.meta['mode']
        if self.channels is not None:
            self.nplots = len(self.channels)
            self.nrows = len(self.channels)
        else:
            self.nplots = self.data.shape(self.CODE)[0]
            self.nrows = self.nplots
            self.channels = list(range(self.nplots))
        if self.mode == 'E':
            self.xlabel = 'Longitude'
            self.ylabel = 'Latitude'
        else:
            self.xlabel = 'Range (km)'
            self.ylabel = 'Height (km)'
        self.bgcolor = 'white'
        self.cb_labels = self.data.meta['units']
        self.lat = self.data.meta['latitude']
        self.lon = self.data.meta['longitude']
        self.xmin, self.xmax = float(
            km2deg(self.xmin) + self.lon), float(km2deg(self.xmax) + self.lon)
        self.ymin, self.ymax = float(
            km2deg(self.ymin) + self.lat), float(km2deg(self.ymax) + self.lat)
        #  self.polar = True

    def plot(self):

        for n, ax in enumerate(self.axes):
            data = self.data['param'][self.channels[n]]

            zeniths = numpy.linspace(
                0, self.data.meta['max_range'], data.shape[1])
            if self.mode == 'E':
                azimuths = -numpy.radians(self.data.heights)+numpy.pi/2
                r, theta = numpy.meshgrid(zeniths, azimuths)
                x, y = r*numpy.cos(theta)*numpy.cos(numpy.radians(self.data.meta['elevation'])), r*numpy.sin(
                    theta)*numpy.cos(numpy.radians(self.data.meta['elevation']))
                x = km2deg(x) + self.lon
                y = km2deg(y) + self.lat
            else:
                azimuths = numpy.radians(self.data.heights)
                r, theta = numpy.meshgrid(zeniths, azimuths)
                x, y = r*numpy.cos(theta), r*numpy.sin(theta)
            self.y = zeniths

            if ax.firsttime:
                if self.zlimits is not None:
                    self.zmin, self.zmax = self.zlimits[n]
                ax.plt = ax.pcolormesh(  # r, theta, numpy.ma.array(data, mask=numpy.isnan(data)),
                    x, y, numpy.ma.array(data, mask=numpy.isnan(data)),
                    vmin=self.zmin,
                    vmax=self.zmax,
                    cmap=self.cmaps[n])
            else:
                if self.zlimits is not None:
                    self.zmin, self.zmax = self.zlimits[n]
                ax.collections.remove(ax.collections[0])
                ax.plt = ax.pcolormesh(  # r, theta, numpy.ma.array(data, mask=numpy.isnan(data)),
                    x, y, numpy.ma.array(data, mask=numpy.isnan(data)),
                    vmin=self.zmin,
                    vmax=self.zmax,
                    cmap=self.cmaps[n])

            if self.mode == 'A':
                continue

            # plot district names
            f = open('/data/workspace/schain_scripts/distrito.csv')
            for line in f:
                label, lon, lat = [s.strip() for s in line.split(',') if s]
                lat = float(lat)
                lon = float(lon)
                # ax.plot(lon, lat, '.b', ms=2)
                ax.text(lon, lat, label.decode('utf8'), ha='center',
                        va='bottom', size='8', color='black')

            # plot limites
            limites = []
            tmp = []
            for line in open('/data/workspace/schain_scripts/lima.csv'):
                if '#' in line:
                    if tmp:
                        limites.append(tmp)
                    tmp = []
                    continue
                values = line.strip().split(',')
                tmp.append((float(values[0]), float(values[1])))
            for points in limites:
                ax.add_patch(
                    Polygon(points, ec='k', fc='none', ls='--', lw=0.5))

            # plot Cuencas
            for cuenca in ('rimac', 'lurin', 'mala', 'chillon', 'chilca', 'chancay-huaral'):
                f = open('/data/workspace/schain_scripts/{}.csv'.format(cuenca))
                values = [line.strip().split(',') for line in f]
                points = [(float(s[0]), float(s[1])) for s in values]
                ax.add_patch(Polygon(points, ec='b', fc='none'))

            # plot grid
            for r in (15, 30, 45, 60):
                ax.add_artist(plt.Circle((self.lon, self.lat),
                                         km2deg(r), color='0.6', fill=False, lw=0.2))
                ax.text(
                    self.lon + (km2deg(r))*numpy.cos(60*numpy.pi/180),
                    self.lat + (km2deg(r))*numpy.sin(60*numpy.pi/180),
                    '{}km'.format(r),
                    ha='center', va='bottom', size='8', color='0.6', weight='heavy')

        if self.mode == 'E':
            title = 'El={}$^\circ$'.format(self.data.meta['elevation'])
            label = 'E{:02d}'.format(int(self.data.meta['elevation']))
        else:
            title = 'Az={}$^\circ$'.format(self.data.meta['azimuth'])
            label = 'A{:02d}'.format(int(self.data.meta['azimuth']))

        self.save_labels = ['{}-{}'.format(lbl, label) for lbl in self.labels]
        self.titles = ['{} {}'.format(
            self.data.parameters[x], title) for x in self.channels]
       