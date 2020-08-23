import os
import sys
import glob
import fnmatch
import datetime
import time
import re
import h5py
import numpy

from scipy.optimize import curve_fit
from scipy import asarray as ar, exp
from scipy import stats

from duplicity.path import Path
from numpy.ma.core import getdata

SPEED_OF_LIGHT = 299792458
SPEED_OF_LIGHT = 3e8

try:
    from gevent import sleep
except:
    from time import sleep

from schainpy.model.data.jrodata import Spectra
#from schainpy.model.data.BLTRheaderIO import FileHeader, RecordHeader
from schainpy.model.proc.jroproc_base import ProcessingUnit, Operation
#from schainpy.model.io.jroIO_bltr import BLTRReader
from numpy import imag, shape, NaN


startFp = open(
    '/home/erick/Documents/MIRA35C/20160117/20160117_0000.zspc', "rb")


FILE_HEADER = numpy.dtype([  # HEADER 1024bytes
                          ('Hname', numpy.str_, 32),  # Original file name
                          # Date and time when the file was created
                          ('Htime', numpy.str_, 32),
                          # Name of operator who created the file
                          ('Hoper', numpy.str_, 64),
                          # Place where the measurements was carried out
                          ('Hplace', numpy.str_, 128),
                          # Description of measurements
                          ('Hdescr', numpy.str_, 256),
                          ('Hdummy', numpy.str_, 512),  # Reserved space
                          # Main chunk
                          ('Msign', '<i4'),  # Main chunk signature FZKF or NUIG
                          ('MsizeData', '<i4'),  # Size of data block main chunk
                          # Processing DSP parameters
                          ('PPARsign', '<i4'),  # PPAR signature
                          ('PPARsize', '<i4'),  # PPAR size of block
                          ('PPARprf', '<i4'),  # Pulse repetition frequency
                          ('PPARpdr', '<i4'),  # Pulse duration
                          ('PPARsft', '<i4'),  # FFT length
                          # Number of spectral (in-coherent) averages
                          ('PPARavc', '<i4'),
                          # Number of lowest range gate for moment estimation
                          ('PPARihp', '<i4'),
                          # Count for gates for moment estimation
                          ('PPARchg', '<i4'),
                          # switch on/off polarimetric measurements. Should be 1.
                          ('PPARpol', '<i4'),
                          # Service DSP parameters
                          # STC attenuation on the lowest ranges on/off
                          ('SPARatt', '<i4'),
                          ('SPARtx', '<i4'),  # OBSOLETE
                          ('SPARaddGain0', '<f4'),  # OBSOLETE
                          ('SPARaddGain1', '<f4'),  # OBSOLETE
                          # Debug only. It normal mode it is 0.
                          ('SPARwnd', '<i4'),
                          # Delay between sync pulse and tx pulse for phase corr, ns
                          ('SPARpos', '<i4'),
                          # "add to pulse" to compensate for delay between the leading edge of driver pulse and envelope of the RF signal.
                          ('SPARadd', '<i4'),
                          # Time for measuring txn pulse phase. OBSOLETE
                          ('SPARlen', '<i4'),
                          ('SPARcal', '<i4'),  # OBSOLETE
                          ('SPARnos', '<i4'),  # OBSOLETE
                          ('SPARof0', '<i4'),  # detection threshold
                          ('SPARof1', '<i4'),  # OBSOLETE
                          ('SPARswt', '<i4'),  # 2nd moment estimation threshold
                          ('SPARsum', '<i4'),  # OBSOLETE
                          ('SPARosc', '<i4'),  # flag Oscillosgram mode
                          ('SPARtst', '<i4'),  # OBSOLETE
                          ('SPARcor', '<i4'),  # OBSOLETE
                          ('SPARofs', '<i4'),  # OBSOLETE
                          # Hildebrand div noise detection on noise gate
                          ('SPARhsn', '<i4'),
                          # Hildebrand div noise detection on all gates
                          ('SPARhsa', '<f4'),
                          ('SPARcalibPow_M', '<f4'),  # OBSOLETE
                          ('SPARcalibSNR_M', '<f4'),  # OBSOLETE
                          ('SPARcalibPow_S', '<f4'),  # OBSOLETE
                          ('SPARcalibSNR_S', '<f4'),  # OBSOLETE
                          # Lowest range gate for spectra saving Raw_Gate1 >=5
                          ('SPARrawGate1', '<i4'),
                          # Number of range gates with atmospheric signal
                          ('SPARrawGate2', '<i4'),
                          # flag - IQ or spectra saving on/off
                          ('SPARraw', '<i4'),
                          ('SPARprc', '<i4'), ])  # flag - Moment estimation switched on/off


self.Hname = None
self.Htime = None
self.Hoper = None
self.Hplace = None
self.Hdescr = None
self.Hdummy = None

self.Msign = None
self.MsizeData = None

self.PPARsign = None
self.PPARsize = None
self.PPARprf = None
self.PPARpdr = None
self.PPARsft = None
self.PPARavc = None
self.PPARihp = None
self.PPARchg = None
self.PPARpol = None
# Service DSP parameters
self.SPARatt = None
self.SPARtx = None
self.SPARaddGain0 = None
self.SPARaddGain1 = None
self.SPARwnd = None
self.SPARpos = None
self.SPARadd = None
self.SPARlen = None
self.SPARcal = None
self.SPARnos = None
self.SPARof0 = None
self.SPARof1 = None
self.SPARswt = None
self.SPARsum = None
self.SPARosc = None
self.SPARtst = None
self.SPARcor = None
self.SPARofs = None
self.SPARhsn = None
self.SPARhsa = None
self.SPARcalibPow_M = None
self.SPARcalibSNR_M = None
self.SPARcalibPow_S = None
self.SPARcalibSNR_S = None
self.SPARrawGate1 = None
self.SPARrawGate2 = None
self.SPARraw = None
self.SPARprc = None


header = numpy.fromfile(fp, FILE_HEADER, 1)
'''      numpy.fromfile(file, dtype, count, sep='')
    file : file or str
    Open file object or filename.
    
    dtype : data-type
    Data type of the returned array. For binary files, it is used to determine 
    the size and byte-order of the items in the file.
    
    count : int
    Number of items to read. -1 means all items (i.e., the complete file).
    
    sep : str
    Separator between items if file is a text file. Empty ("") separator means 
    the file should be treated as binary. Spaces (" ") in the separator match zero 
    or more whitespace characters. A separator consisting only of spaces must match 
    at least one whitespace.
    
'''

Hname = str(header['Hname'][0])
Htime = str(header['Htime'][0])
Hoper = str(header['Hoper'][0])
Hplace = str(header['Hplace'][0])
Hdescr = str(header['Hdescr'][0])
Hdummy = str(header['Hdummy'][0])

Msign = header['Msign'][0]
MsizeData = header['MsizeData'][0]

PPARsign = header['PPARsign'][0]
PPARsize = header['PPARsize'][0]
PPARprf = header['PPARprf'][0]
PPARpdr = header['PPARpdr'][0]
PPARsft = header['PPARsft'][0]
PPARavc = header['PPARavc'][0]
PPARihp = header['PPARihp'][0]
PPARchg = header['PPARchg'][0]
PPARpol = header['PPARpol'][0]
# Service DSP parameters
SPARatt = header['SPARatt'][0]
SPARtx = header['SPARtx'][0]
SPARaddGain0 = header['SPARaddGain0'][0]
SPARaddGain1 = header['SPARaddGain1'][0]
SPARwnd = header['SPARwnd'][0]
SPARpos = header['SPARpos'][0]
SPARadd = header['SPARadd'][0]
SPARlen = header['SPARlen'][0]
SPARcal = header['SPARcal'][0]
SPARnos = header['SPARnos'][0]
SPARof0 = header['SPARof0'][0]
SPARof1 = header['SPARof1'][0]
SPARswt = header['SPARswt'][0]
SPARsum = header['SPARsum'][0]
SPARosc = header['SPARosc'][0]
SPARtst = header['SPARtst'][0]
SPARcor = header['SPARcor'][0]
SPARofs = header['SPARofs'][0]
SPARhsn = header['SPARhsn'][0]
SPARhsa = header['SPARhsa'][0]
SPARcalibPow_M = header['SPARcalibPow_M'][0]
SPARcalibSNR_M = header['SPARcalibSNR_M'][0]
SPARcalibPow_S = header['SPARcalibPow_S'][0]
SPARcalibSNR_S = header['SPARcalibSNR_S'][0]
SPARrawGate1 = header['SPARrawGate1'][0]
SPARrawGate2 = header['SPARrawGate2'][0]
SPARraw = header['SPARraw'][0]
SPARprc = header['SPARprc'][0]


SRVI_STRUCTURE = numpy.dtype([
                            ('frame_cnt', '<u4'),
                            ('time_t', '<u4'),   #
                            ('tpow', '<f4'),     #
                            ('npw1', '<f4'),     #
                            ('npw2', '<f4'),     #
                            ('cpw1', '<f4'),     #
                            ('pcw2', '<f4'),     #
                            ('ps_err', '<u4'),   #
                            ('te_err', '<u4'),   #
                            ('rc_err', '<u4'),   #
                            ('grs1', '<u4'),     #
                            ('grs2', '<u4'),     #
                            ('azipos', '<f4'),     #
                            ('azivel', '<f4'),     #
                            ('elvpos', '<f4'),     #
                            ('elvvel', '<f4'),     #
                            ('northAngle', '<f4'),
                            ('microsec', '<u4'),   #
                            ('azisetvel', '<f4'),  #
                            ('elvsetpos', '<f4'),  #
                            ('RadarConst', '<f4'), ])   #

JUMP_STRUCTURE = numpy.dtype([
                            ('jump', '<u140'),
                            ('SizeOfDataBlock1', numpy.str_, 32),
                            ('jump', '<i4'),
                            ('DataBlockTitleSRVI1', numpy.str_, 32),
                            ('SizeOfSRVI1', '<i4'), ])


# frame_cnt=0,  time_t= 0,  tpow=0,   npw1=0,   npw2=0,
# cpw1=0,   pcw2=0,       ps_err=0,   te_err=0,   rc_err=0,   grs1=0,
# grs2=0,   azipos=0,   azivel=0,   elvpos=0,   elvvel=0,   northangle=0,
# microsec=0,   azisetvel=0,   elvsetpos=0,   RadarConst=0


frame_cnt = frame_cnt
dwell = time_t
tpow = tpow
npw1 = npw1
npw2 = npw2
cpw1 = cpw1
pcw2 = pcw2
ps_err = ps_err
te_err = te_err
rc_err = rc_err
grs1 = grs1
grs2 = grs2
azipos = azipos
azivel = azivel
elvpos = elvpos
elvvel = elvvel
northAngle = northAngle
microsec = microsec
azisetvel = azisetvel
elvsetpos = elvsetpos
RadarConst5 = RadarConst


# print fp
# startFp = open('/home/erick/Documents/Data/huancayo.20161019.22.fdt',"rb") #The method tell() returns the current position of the file read/write pointer within the file.
# startFp = open(fp,"rb") #The method tell() returns the current position of the file read/write pointer within the file.
# RecCounter=0
# Off2StartNxtRec=811248
# print 'OffsetStartHeader ',self.OffsetStartHeader,'RecCounter ', self.RecCounter, 'Off2StartNxtRec ' , self.Off2StartNxtRec
#OffRHeader= self.OffsetStartHeader + self.RecCounter*self.Off2StartNxtRec
#startFp.seek(OffRHeader, os.SEEK_SET)
print('debe ser 48, RecCounter*811248', self.OffsetStartHeader, self.RecCounter, self.Off2StartNxtRec)
print('Posicion del bloque:        ', OffRHeader)

header = numpy.fromfile(startFp, SRVI_STRUCTURE, 1)

self.frame_cnt = header['frame_cnt'][0]
self.time_t = header['frame_cnt'][0]   #
self.tpow = header['frame_cnt'][0]     #
self.npw1 = header['frame_cnt'][0]     #
self.npw2 = header['frame_cnt'][0]     #
self.cpw1 = header['frame_cnt'][0]     #
self.pcw2 = header['frame_cnt'][0]     #
self.ps_err = header['frame_cnt'][0]    #
self.te_err = header['frame_cnt'][0]    #
self.rc_err = header['frame_cnt'][0]    #
self.grs1 = header['frame_cnt'][0]      #
self.grs2 = header['frame_cnt'][0]      #
self.azipos = header['frame_cnt'][0]     #
self.azivel = header['frame_cnt'][0]     #
self.elvpos = header['frame_cnt'][0]     #
self.elvvel = header['frame_cnt'][0]     #
self.northAngle = header['frame_cnt'][0]    #
self.microsec = header['frame_cnt'][0]      #
self.azisetvel = header['frame_cnt'][0]     #
self.elvsetpos = header['frame_cnt'][0]     #
self.RadarConst = header['frame_cnt'][0]    #


self.ipp = 0.5 * (SPEED_OF_LIGHT / self.PRFhz)

self.RHsize = 180 + 20 * self.nChannels
self.Datasize = self.nProfiles * self.nChannels * self.nHeights * 2 * 4
# print 'Datasize',self.Datasize
endFp = self.OffsetStartHeader + self.RecCounter * self.Off2StartNxtRec

print('==============================================')

print('==============================================')