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
    project_name = None
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
        self.expLabel = ''
        self.set = None
        self.ippKm = None
        self.walk = None
        self.delay = None
    
    def getDatatypeIndex(self):
        
        indexDatatype = None
        
        if self.datatype.lower() == 'voltage':
            indexDatatype = 0
        if self.datatype.lower() == 'spectra':
            indexDatatype = 1
        if self.datatype.lower() == 'fits':
            indexDatatype = 2
        if self.datatype.lower() == 'usrp':
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
            delay=None, walk=None, set=None, ippKm=None, parmsOk=True):
        
        project_name = project_name
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
        
        self.parmsOk = parmsOk