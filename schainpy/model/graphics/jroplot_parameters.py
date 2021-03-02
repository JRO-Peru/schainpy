import os
import datetime
import numpy

from schainpy.model.graphics.jroplot_base import Plot, plt
from schainpy.model.graphics.jroplot_spectra import SpectraPlot, RTIPlot, CoherencePlot
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



class SpectralMomentsPlot(SpectraPlot):
    '''
    Plot for Spectral Moments
    '''
    CODE = 'spc_moments'
    colormap = 'jet'
    plot_type = 'pcolor'


class SnrPlot(RTIPlot):
    '''
    Plot for SNR Data
    '''

    CODE = 'snr'
    colormap = 'jet'

    def update(self, dataOut):

        data = {
            'snr': 10*numpy.log10(dataOut.data_snr)    
        }

        return data, {}

class DopplerPlot(RTIPlot):
    '''
    Plot for DOPPLER Data (1st moment)
    '''

    CODE = 'dop'
    colormap = 'jet'

    def update(self, dataOut):

        data = {
            'dop': 10*numpy.log10(dataOut.data_dop)    
        }

        return data, {}

class PowerPlot(RTIPlot):
    '''
    Plot for Power Data (0 moment)
    '''

    CODE = 'pow'
    colormap = 'jet'

    def update(self, dataOut):

        data = {
            'pow': 10*numpy.log10(dataOut.data_pow)    
        }

        return data, {}

class SpectralWidthPlot(RTIPlot):
    '''
    Plot for Spectral Width Data (2nd moment)
    '''

    CODE = 'width'
    colormap = 'jet'

    def update(self, dataOut):

        data = {
            'width': dataOut.data_width
        }

        return data, {}

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


class GenericRTIPlot(Plot):
    '''
    Plot for data_xxxx object
    '''

    CODE = 'param'
    colormap = 'viridis'
    plot_type = 'pcolorbuffer'

    def setup(self):
        self.xaxis = 'time'
        self.ncols = 1
        self.nrows = self.data.shape(self.attr_data)[0]
        self.nplots = self.nrows
        self.plots_adjust.update({'hspace':0.8, 'left': 0.1, 'bottom': 0.08, 'right':0.95, 'top': 0.95})
        
        if not self.xlabel:
            self.xlabel = 'Time'

        self.ylabel = 'Height [km]'
        if not self.titles:
            self.titles = self.data.parameters \
                if self.data.parameters else ['Param {}'.format(x) for x in range(self.nrows)]

    def update(self, dataOut):

        data = {
            self.attr_data : getattr(dataOut, self.attr_data)
        }

        meta = {}

        return data, meta
    
    def plot(self):
        # self.data.normalize_heights()
        self.x = self.data.times
        self.y = self.data.yrange
        self.z = self.data[self.attr_data]

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
                azimuths = -numpy.radians(self.data.yrange)+numpy.pi/2
                r, theta = numpy.meshgrid(zeniths, azimuths)
                x, y = r*numpy.cos(theta)*numpy.cos(numpy.radians(self.data.meta['elevation'])), r*numpy.sin(
                    theta)*numpy.cos(numpy.radians(self.data.meta['elevation']))
                x = km2deg(x) + self.lon
                y = km2deg(y) + self.lat
            else:
                azimuths = numpy.radians(self.data.yrange)
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

