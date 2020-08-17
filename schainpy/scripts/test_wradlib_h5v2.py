#!/usr/bin/env python
#LINUX
#bash: export WRADLIB_DATA=/path/to/wradlib-data
import os,h5py
import matplotlib.pyplot as pl
import wradlib as wrl
import numpy as np
pl.switch_backend("TKAgg")
#filename = wrl.util.get_wradlib_data_file('dx/raa00-dx_10908-0806021655-fbg---bin.gz')


validFilelist = []
path="/home/alex/Downloads/hdf5_wr/d2020204/"
ext=".hdf5"



##path= '/home/alex/Downloads/2019-12-29/'
fileList= os.listdir(path)
for thisFile in fileList:
    ##if (os.path.splitext(thisFile)[0][-4:] != 'dBuZ'):
    ##    continue
    validFilelist.append(thisFile)
    validFilelist.sort()
#---print ("Files",validFilelist)
#print (validFilelist)
i=0
for thisFile in validFilelist:
    i=i+1
    fpath = path+thisFile
    print("fpath",fpath)
    fp    = h5py.File(fpath,'r')
    value='table00'
    data = fp['Data']['dataPP_POW'].get('table00')[()]
    azi   = fp['Pedestal'].get('azimuth')[()]
    fp.close()
    data = 10*np.log10(data/(625**2))
    print("azi",azi.shape)
    print("azi",azi)

    print("data",data.shape)
    ###f = wrl.util.get_wradlib_data_file(fpath)
    #print("f",f)
    ####fcontent = wrl.io.read_rainbow(f)
    ###fcontent = wrl.io.read_generic_hdf5(f)
    #print(fcontent.keys())
    #print (fcontent)
    #print(sfcontent['volume']

    #Get azimuth data
    ############azi = fcontent['Pedestal/azimuth']['data']
    ##print("azi0",azi['data'].shape)
    ##print("azi",azi['data'])
    '''
    azi = fcontent['volume']['scan']['slice']['slicedata']['rayinfo']['data']
    azidepth = float(fcontent['volume']['scan']['slice']['slicedata']['rayinfo']['@depth'])
    azirange = float(fcontent['volume']['scan']['slice']['slicedata']['rayinfo']['@rays'])
    azires = float(fcontent['volume']['scan']['slice']['anglestep'])
    azi = (azi * azirange / 2**azidepth) * azires
    '''
    #---print("AZI",azi.shape)
    #---print("AZI",type(azi))

    ##print("azi_range",azi)
    #print("azidepth",azidepth)
    #print("azirange",azirange)
    #print("azires",azires)
    #print("azi   azi",azi)

    # Create range array
    '''
    stoprange = float(fcontent['volume']['scan']['slice']['stoprange'])
    rangestep = float(fcontent['volume']['scan']['slice']['rangestep'])
    '''
    stoprange = float(33*1.5)
    rangestep = float(0.15)
    r = np.arange(0, stoprange, rangestep)
    #---print("stoprange",stoprange)
    #---print("rangestep",rangestep)
    #---print("r",r.shape)
    #---print("r",type(r))

    # GET reflectivity data#print (fcontent)
    #print(sfcontent['volume']
    '''
    data = fcontent['volume']['scan']['slice']['slicedata']['rawdata']['data']
    datadepth = float(fcontent['volume']['scan']['slice']['slicedata']['rawdata']['@depth'])
    datamin = float(fcontent['volume']['scan']['slice']['slicedata']['rawdata']['@min'])
    datamax = float(fcontent['volume']['scan']['slice']['slicedata']['rawdata']['@max'])
    data = datamin + data * (datamax - datamin) / 2 ** datadepth
    '''
    ########data = fcontent['Data/dataPP_POW/table00']['data']
    ########data = 10*np.log10(data/(625**2))
    #---print("DATA",data.shape)
    #---print("DATA",type(data))

    ##data =fcontent['Data/dataPP_POW/table00']['data']
    ##print("data 1",data.shape)
    ##data = 10*np.log10(fcontent['Data/dataPP_POW/table00']['data']/(625**2))
    ##print("test data",data.shape)
    #print("datadepth",datadepth)
    #print("datamin",datamin)
    #print("datamax",datamax)
    #print("data",data)
    if i==1:
        azi2= azi
        data2= data
        #---print("azi2 shape I es 1",azi2.shape)
    else:
        if i==4:
            #---print (azi[60:].shape)
            azi2= np.concatenate((azi2,azi[40:]))
            data2= np.concatenate((data2,data[40:,:]),axis=0)
        else:
            azi2= np.concatenate((azi2,azi))
            data2= np.concatenate((data2,data),axis=0)

    #---print("azi2 shape",azi2.shape)
    #print(fcontent['volume']['sensorinfo'])
    #print("ESPACIO")
    #print(data)

    #GET ANNOTATION data
    '''
    unit = fcontent['volume']['scan']['slice']['slicedata']['rawdata']['@type']
    time = fcontent['volume']['scan']['slice']['slicedata']['@time']
    date = fcontent['volume']['scan']['slice']['slicedata']['@date']
    lon = fcontent['volume']['sensorinfo']['lon']
    lat = fcontent['volume']['sensorinfo']['lat']
    sensortype = fcontent['volume']['sensorinfo']['@type']
    sensorname = fcontent['volume']['sensorinfo']['@name']
    '''
#---print("AZI2",azi2.shape)
#---print("data2",data2.shape)

# PLOT DATA WITH ANNOTATION
fig = pl.figure(figsize=(8,8))
cgax, pm = wrl.vis.plot_ppi(data2, r=r, az=azi2, fig=fig, proj='cg')

#title = '{0} {1} {2} {3}\n{4}E {5}N'.format(sensortype, sensorname, date,time, lon, lat)
caax = cgax.parasites[0]
#t = pl.title(title, fontsize=12)
#t.set_y(1.1)
cbar = pl.gcf().colorbar(pm, pad=0.075)
caax.set_xlabel('x_range [km]')
caax.set_ylabel('y_range [km]')
pl.text(1.0, 1.05, 'azimuth', transform=caax.transAxes, va='bottom',
        ha='right')
#cbar.set_label('reflectivity [' + unit + ']')
pl.show()

    #print ("FIN")
    #import time
    #time.sleep(2)
    #pl.close()
    # stop here
    #print(fcontent['data'])
    #data, metadata = wrl.io.read_dx(filename)
    #ax, pm = wrl.vis.plot_ppi(data) # simple diagnostic plot
    #cbar = pl.colorbar(pm, shrink=0.75)
