"""
Classes to save parameters from Windows.

-Project window
-Voltage window
-Spectra window
-SpectraHeis window
-Correlation window

"""

class ProjectParms():
    
    parmsOk = False
    name = None
    description = None
    datatype = None
    ext = None
    dpath = None
    startDate = None
    endDate = None
    startTime = None
    endTime  = None
    online  = None
    delay = None
    walk  = None
    expLabel = None
    set = None
    ippKm = None
    
    def __init__(self):
        
        self.parmsOk = True
        self.description = ''
        self.expLabel = ''
        self.set = ''
        self.ippKm = ''
        self.walk = None
        self.delay = ''
    
    def getDatatypeIndex(self):
        
        indexDatatype = None
        
        if 'voltage' in self.datatype.lower():
            indexDatatype = 0
        if 'spectra' in self.datatype.lower():
            indexDatatype = 1
        if 'fits' in self.datatype.lower():
            indexDatatype = 2
        if 'usrp' in self.datatype.lower():
            indexDatatype = 3
        return indexDatatype

    def getExt(self):
        
        ext = None
        
        if self.datatype.lower() == 'voltage':
            ext = '.r'
        if self.datatype.lower() == 'spectra':
            ext = '.pdata'
        if self.datatype.lower() == 'fits':
            ext = '.fits'
        if self.datatype.lower() == 'usrp':
            ext = '.hdf5'
        return ext
               
    def set(self, project_name, datatype, ext, dpath, online,
            startDate=None, endDate=None, startTime=None, endTime=None,
            delay=None, walk=None, set=None, ippKm=None, parmsOk=True, expLabel=''):
        
        name = project_name
        datatype = datatype
        ext = ext
        dpath = dpath
        startDate = startDate
        endDate = endDate
        startTime = startTime
        endTime  = endTime
        online  = online
        delay = delay
        walk  = walk
        set = set
        ippKm = ippKm 
        expLabel = expLabel
        
        self.parmsOk = parmsOk
    
    def isValid(self):
        
        return self.parmsOk