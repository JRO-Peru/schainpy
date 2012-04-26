import numpy
from Model.Spectra import Spectra

def hildebrand_sekhon(Data, navg=1):
    """
    This method is for the objective determination of de noise level in Doppler spectra. This 
    implementation technique is based on the fact that the standard deviation of the spectral 
    densities is equal to the mean spectral density for white Gaussian noise
    
    Inputs:
        Data    :    heights
        navg    :    numbers of averages
        
    Return:
        -1        :    any error
        anoise    :    noise's level
    """
    divisor = 8
    ratio = 7 / divisor
    data = Data.reshape(-1)
    npts = data.size #numbers of points of the data
    
    if npts < 32:
        print "error in noise - requires at least 32 points"
        return -1.0
    
    # data sorted in ascending order
    nmin = int(npts/divisor + ratio);
    s = 0.0
    s2 = 0.0
    data2 = data[:npts] 
    data2.sort()
    
    for i in range(nmin):
        s  += data2[i]
        s2 += data2[i]**2;
          
    icount = nmin
    iflag = 0 
    
    for i in range(nmin, npts):
        s  += data2[i];
        s2 += data2[i]**2
        icount=icount+1;
        p  = s / float(icount);
        p2 = p**2;
        q  = s2 / float(icount) - p2;
        leftc = p2;
        rightc = q * float(navg);

        if leftc > rightc: 
            iflag = 1; #No weather signal
        # Signal detect: R2 < 1 (R2 = leftc/rightc)
        if(leftc < rightc):
            if iflag:
                break

    anoise = 0.0;
    for j in range(i):
        anoise += data2[j];

    anoise = anoise / float(i);

    return anoise;


class Noise():
    """
    Clase que implementa los metodos necesarios para deternimar el nivel de ruido en un Spectro Doppler
    """
    m_DataObj = None


    def __init__(self, m_Spectra=None):
        """
        Inicializador de la clase Noise para la la determinacion del nivel de ruido en un Spectro Doppler.

        Affected:
            self.m_DataObj
        
        Return:
            None
        """
        if m_Spectra == None:
            m_Spectra = Spectra()
        
        if not(isinstance(m_Spectra, Spectra)):
            raise ValueError, "in Noise class, m_Spectra must be an Spectra class object"
        
        self.m_DataObj = m_Spectra
        
        
    def getNoiseLevelByHildebrandSekhon(self):
        """
        Determino el nivel de ruido usando el metodo Hildebrand-Sekhon
        
        Return:
            noise level
        """
        data = self.m_DataObj.data_spc
        daux = None

        for channel in range(self.m_DataObj.nChannels):
            daux = data[channel,:,:]
            noiselevel = hildebrand_sekhon(daux)
            print noiselevel
        

        for pair in range(self.m_DataObj.nPairs):
            daux = data[pair,:,:]
            noiselevel = hildebrand_sekhon(daux)
            print noiselevel
