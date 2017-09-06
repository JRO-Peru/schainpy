'''
Created on Aug 1, 2017

@author: Juan C. Espinoza
'''

import os
import sys
import time
import json
import datetime

import numpy

try:
    import madrigal
    import madrigal.cedar
except:
    print 'You should install "madrigal library" module if you want to read/write Madrigal data'

from schainpy.model.proc.jroproc_base import Operation
from schainpy.model.data.jrodata import Parameters

MISSING = -32767
DEF_CATALOG = {
    'principleInvestigator': 'Marco Milla',
    'expPurpose': None,
    'expMode': None,
    'cycleTime': None,
    'correlativeExp': None,
    'sciRemarks': None,
    'instRemarks': None
    }
DEF_HEADER = {
    'kindatDesc': None,
    'analyst': 'Jicamarca User',
    'comments': None,
    'history': None
    }
MNEMONICS = {
    10: 'jro',
    11: 'jbr',
    840: 'jul',
    13: 'jas',
    1000: 'pbr',
    1001: 'hbr',
    1002: 'obr',
}

def load_json(obj):
    '''
    Parse json as string instead of unicode
    '''

    if isinstance(obj, str):
        obj = json.loads(obj)

    return {str(k): load_json(v) if isinstance(v, dict) else str(v) if isinstance(v, unicode) else v
        for k, v in obj.items()}


class MAD2Writer(Operation):
    
    def __init__(self, **kwargs):
        
        Operation.__init__(self, **kwargs)
        self.dataOut = Parameters()
        self.path = None
        self.dataOut = None
        self.ext = '.dat'

        return
    
    def run(self, dataOut, path, oneDList, twoDParam='', twoDList='{}', metadata='{}', **kwargs):
        '''
        Inputs:
            path - path where files will be created
            oneDList - json of one-dimensional parameters in record where keys
            are Madrigal codes (integers or mnemonics) and values the corresponding
            dataOut attribute e.g: {
                'gdlatr': 'lat',
                'gdlonr': 'lon',
                'gdlat2':'lat',
                'glon2':'lon'}
            twoDParam - independent parameter to get the number of rows e.g:
                heighList
            twoDList - json of two-dimensional parameters in record where keys
            are Madrigal codes (integers or mnemonics) and values the corresponding
            dataOut attribute if multidimensional array specify as tupple
            ('attr', pos) e.g: {
                'gdalt': 'heightList',
                'vn1p2': ('data_output', 0),
                'vn2p2': ('data_output', 1),
                'vn3': ('data_output', 2),
                'snl': ('data_SNR', 'db')
                }
            metadata - json of madrigal metadata (kinst, kindat, catalog and header)      
        '''
        if not self.isConfig:
            self.setup(dataOut, path, oneDList, twoDParam, twoDList, metadata, **kwargs)
            self.isConfig = True
            
        self.putData() 
        return
    
    def setup(self, dataOut, path, oneDList, twoDParam, twoDList, metadata, **kwargs):
        '''
        Configure Operation        
        '''
        
        self.dataOut = dataOut
        self.nmodes = self.dataOut.nmodes     
        self.path = path
        self.blocks = kwargs.get('blocks', None)
        self.counter = 0        
        self.oneDList = load_json(oneDList)
        self.twoDList = load_json(twoDList)
        self.twoDParam = twoDParam
        meta = load_json(metadata)        
        self.kinst = meta.get('kinst')
        self.kindat = meta.get('kindat')
        self.catalog = meta.get('catalog', DEF_CATALOG)
        self.header = meta.get('header', DEF_HEADER)

        return

    def setFile(self):
        '''
        Create new cedar file object
        '''

        self.mnemonic = MNEMONICS[self.kinst]   #TODO get mnemonic from madrigal
        date = datetime.datetime.utcfromtimestamp(self.dataOut.utctime)

        filename = '%s%s_%s%s' % (self.mnemonic,
                                  date.strftime('%Y%m%d_%H%M%S'),
                                  self.dataOut.mode,
                                  self.ext)     
       
        self.fullname = os.path.join(self.path, filename)

        if os.path.isfile(self.fullname) : 
            print "Destination path '%s' already exists. Previous file deleted. " %self.fullname
            os.remove(self.fullname)
        
        try:
            print '[Writing] creating file : %s' % (self.fullname)
            self.cedarObj = madrigal.cedar.MadrigalCedarFile(self.fullname, True)  
        except ValueError, e:
            print '[Error]: Impossible to create a cedar object with "madrigal.cedar.MadrigalCedarFile" '
            return
        
        return 1  
     
    def writeBlock(self):
        '''
        Add data records to cedar file taking data from oneDList and twoDList
        attributes.
        Allowed parameters in: parcodes.tab
        '''

        startTime = datetime.datetime.utcfromtimestamp(self.dataOut.utctime)
        endTime = startTime + datetime.timedelta(seconds=self.dataOut.paramInterval)
        nrows = len(getattr(self.dataOut, self.twoDParam))

        rec = madrigal.cedar.MadrigalDataRecord(
            self.kinst,
            self.kindat,
            startTime.year,
            startTime.month,
            startTime.day,
            startTime.hour,
            startTime.minute,
            startTime.second,
            startTime.microsecond/10000,
            endTime.year,
            endTime.month,
            endTime.day,
            endTime.hour,
            endTime.minute,
            endTime.second,
            endTime.microsecond/10000,
            self.oneDList.keys(),
            self.twoDList.keys(),
            nrows
            )
                    
        # Setting 1d values        
        for key in self.oneDList:
            rec.set1D(key, getattr(self.dataOut, self.oneDList[key]))

        # Setting 2d values
        invalid = numpy.isnan(self.dataOut.data_output)
        self.dataOut.data_output[invalid] = MISSING
        out = {}
        for key, value in self.twoDList.items():
            if isinstance(value, str):
                out[key] = getattr(self.dataOut, value)
            elif isinstance(value, tuple):
                attr, x = value
                if isinstance(x, (int, float)):
                    out[key] = getattr(self.dataOut, attr)[int(x)]
                elif x.lower()=='db':
                    tmp = getattr(self.dataOut, attr)
                    SNRavg = numpy.average(tmp, axis=0)
                    out[key] = 10*numpy.log10(SNRavg)

        for n in range(nrows):
            for key in out:
                rec.set2D(key, n, out[key][n])

        self.cedarObj.append(rec)
        self.cedarObj.dump()
        print '[Writing] Record No. {} (mode {}).'.format(
            self.counter,
            self.dataOut.mode
            )

    def setHeader(self):
        '''
        Create an add catalog and header to cedar file
        ''' 
        
        header = madrigal.cedar.CatalogHeaderCreator(self.fullname)        
        header.createCatalog(**self.catalog)
        header.createHeader(**self.header)
        header.write()
              
    def putData(self):

        if self.dataOut.flagNoData:
            return 0
        
        if self.counter == 0:
            self.setFile()            
        
        if self.counter <= self.dataOut.nrecords:
            self.writeBlock()
            self.counter += 1
        
        if self.counter == self.dataOut.nrecords or self.counter == self.blocks:
            self.setHeader()
            self.counter = 0
