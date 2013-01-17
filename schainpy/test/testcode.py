import numpy
import scipy.signal
import matplotlib
matplotlib.use("TKAgg")
import pylab as pl

import time

def getInverseFilter(code, lenfilter=8*28):
    
    nBauds = len(code)
    
    if lenfilter == None:
        lenfilter = 10*nBauds
    
    codeBuffer = numpy.zeros((lenfilter), dtype=numpy.float32)
    codeBuffer[0:nBauds] = code
    
    inverse_filter = numpy.real(numpy.fft.ifft(1.0/numpy.fft.fft(codeBuffer)))
    inverse_filter = numpy.roll(inverse_filter, shift=120)
    
#    pl.plot(codeBuffer)
#    pl.plot(inverse_filter)
#    pl.show()
    
    return inverse_filter

def getSignal(nChannels, nHeis):
    
    u = numpy.complex(1,2)
    u  /= numpy.abs(u)
    
    signal = numpy.random.rand(nChannels, nHeis)
    signal = signal.astype(numpy.complex)
    
    signal *= u
    
    return signal

def time_decoding(signal, code):
    
    ini = time.time()
    
    nBauds = len(code)
    nChannels, nHeis = signal.shape
    datadec = numpy.zeros((nChannels, nHeis - nBauds + 1), dtype=numpy.complex)
    
    tmpcode = code.astype(numpy.complex)
    #######################################
    ini = time.time()
        
    for i in range(nChannels):
        datadec[i,:] = numpy.correlate(signal[i,:], code, mode='valid')/nBauds
    
    print time.time() - ini
    
    return datadec

def freq_decoding(signal, code):
    
    ini = time.time()
    
    nBauds = len(code)
    nChannels, nHeis = signal.shape
    
    codeBuffer = numpy.zeros((nHeis), dtype=numpy.float32)
        
    codeBuffer[0:nBauds] = code
    
    fft_code = numpy.conj(numpy.fft.fft(codeBuffer)).reshape(1, -1)
    
    ######################################
    ini = time.time()
    
    fft_data = numpy.fft.fft(signal, axis=1)
    
    conv = fft_data*fft_code
    
    data = numpy.fft.ifft(conv, axis=1)/nBauds
    
    datadec = data[:,:-nBauds+1]
    
    print time.time() - ini
    
    return datadec

def fftconvol_decoding(signal, code):
    
    ini = time.time()
    
    nBauds = len(code)
    nChannels, nHeis = signal.shape
    datadec = numpy.zeros((nChannels, nHeis - nBauds + 1), dtype=numpy.complex)
    
    tmpcode = code.astype(numpy.complex)
    #######################################
    ini = time.time()
        
    for i in range(nChannels):
        datadec[i,:] = scipy.signal.fftconvolve(signal[i,:], code[-1::-1], mode='valid')/nBauds
    
    print time.time() - ini
    
    return datadec

def filter_decoding(signal, code):
    
    ini = time.time()
    
    nBauds = len(code)
    nChannels, nHeis = signal.shape
    
    inverse_filter = getInverseFilter(code)
    
    datadec = numpy.zeros((nChannels, nHeis + len(inverse_filter) - 1), dtype=numpy.complex)
    #######################################
    ini = time.time()
        
    for i in range(nChannels):
        datadec[i,:] = numpy.convolve(signal[i,:], inverse_filter, mode='full')
    
    datadec = datadec[:,120:120+nHeis]
    
    print time.time() - ini
    
    return datadec

nChannels, nHeis = 8, 3900
index = 300
code = numpy.array([1, 1, -1, -1, -1, 1, 1, 1, -1, -1, -1, -1, -1, -1, -1, 1, -1, 1, -1, 1, 1, -1, 1, 1, -1, -1, 1, -1])
signal = getSignal(nChannels, nHeis)
signal[0,index:index+len(code)] = code*10

signalout = time_decoding(signal, code)
signalout1 = freq_decoding(signal, code)
signalout2 = fftconvol_decoding(signal, code)
signalout3 = filter_decoding(signal, code)

#pl.plot(numpy.abs(signal[0]))
pl.plot(numpy.abs(signalout[0]))
#pl.plot(numpy.abs(signalout1[0]))
#pl.plot(numpy.abs(signalout2[0]))
pl.plot(numpy.abs(signalout3[0])+0.5)
pl.show()

        