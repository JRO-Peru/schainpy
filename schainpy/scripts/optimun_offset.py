import h5py
import numpy
import matplotlib.pyplot as plt
import glob
import os
 
#----------------------    Functions     ---------------------
 
def findFiles(path):
    
    dirList = []
    fileList = []
    
    for thisPath in os.listdir(path):
        dirList.append(os.path.join(path,thisPath))
        dirList.sort()
    
    for thisDirectory in dirList:
		files = glob.glob1(thisDirectory, "*.hdf5")
		files.sort()
		for thisFile in files:
			fileList.append(os.path.join(thisDirectory,thisFile))   
    
    return fileList
 
def readFiles(fileList):
    
    meteors_array = numpy.zeros((1,4))
    
    for thisFile in fileList:
        
        #Leer
		f1 = h5py.File(thisFile,'r')
		grp1 = f1['Data']
		grp2 = grp1['data_output']     
		meteors1 = grp2['table0'][:]
		meteors_array = numpy.vstack((meteors_array,meteors1))
        #cerrar
		f1.close()

    meteors_array = numpy.delete(meteors_array, 0, axis=0)
    meteors_list = [meteors_array[:,0],meteors_array[:,1],meteors_array[:,2],meteors_array[:,3]]
    return meteors_list
        
def estimateMean(offset_list):
    
    mean_off = []
    axisY_off = []
    axisX_off = []
    
    for thisOffset in offset_list:
		mean_aux = numpy.mean(thisOffset, axis = 0)
		mean_off.append(mean_aux)
		axisX_off.append(numpy.array([0,numpy.size(thisOffset)]))
		axisY_off.append(numpy.array([mean_aux,mean_aux]))
        
    return mean_off, axisY_off, axisX_off
 
def plotPhases(offset0, axisY0, axisX0, title):
    f, axarr = plt.subplots(4, sharey=True)
    color = ['b','g','r','c']
# plt.grid()
    for i in range(len(offset0)):
		thisMeteor = offset0[i]
		thisY = axisY0[i]
		thisX = axisX0[i]
		thisColor = color[i]
	
		opt = thisColor + 'o'
		axarr[i].plot(thisMeteor,opt)
		axarr[i].plot(thisX, thisY, thisColor)
		axarr[i].set_ylabel('Offset ' + str(i))
   
    plt.ylim((-180,180))
    axarr[0].set_title(title + ' Offsets')
    axarr[3].set_xlabel('Number of estimations')
    
    return
 
def filterOffsets(offsets0, stdvLimit):
    offsets1 = []
    
    for thisOffset in offsets0:
        pstd = numpy.std(thisOffset)*stdvLimit
        pmean = numpy.mean(thisOffset)
        outlier1 = thisOffset > pmean - pstd
        outlier2 = thisOffset < pmean + pstd       
        not_outlier = numpy.logical_and(outlier1,outlier2)
        thisOffset1 = thisOffset[not_outlier]
        offsets1.append(thisOffset1)
    
    return offsets1
 
#----------------------     Setup    ---------------------------
 
<<<<<<< HEAD
path = '/home/nanosat/Pictures/JASMET30_mp/201608/phase'
=======
path = '/home/jespinoza/Pictures/JASMET30/201608/phase'
>>>>>>> master
stdvLimit = 0.5
 
#----------------------   Script     ---------------------------
 
fileList = findFiles(path)
offsets0 = readFiles(fileList)
mean0, axisY0, axisX0 = estimateMean(offsets0)
plotPhases(offsets0, axisY0, axisX0, 'Original')
 
offsets1 = filterOffsets(offsets0, stdvLimit)
mean1, axisY1, axisX1 = estimateMean(offsets1)
plotPhases(offsets1, axisY1, axisX1, 'Filtered')
 
print "Original Offsets: %.2f, %.2f, %.2f, %.2f" % (mean0[0],mean0[1],mean0[2],mean0[3])
print "Filtered Offsets: %.2f, %.2f, %.2f, %.2f" % (mean1[0],mean1[1],mean1[2],mean1[3])
 
plt.show()
