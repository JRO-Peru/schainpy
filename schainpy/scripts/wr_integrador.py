import os,numpy,h5py
from shutil import copyfile

def isNumber(str):
    try:
        float(str)
        return True
    except:
        return False

def getfirstFilefromPath(path,meta,ext):
    validFilelist = []
    fileList      = os.listdir(path)
    if len(fileList)<1:
     return None
    # meta    1234 567 8-18 BCDE
    # H,D,PE  YYYY DDD EPOC .ext

    for thisFile in fileList:
        if meta =="PE":
            try:
                number= int(thisFile[len(meta)+7:len(meta)+17])
            except:
                 print("There is a file or folder with different format")
        if meta == "D":
            try:
                number= int(thisFile[8:11])
            except:
                print("There is a file or folder with different format")

        if not isNumber(str=number):
            continue
        if (os.path.splitext(thisFile)[-1].lower() != ext.lower()):
            continue
        validFilelist.sort()
        validFilelist.append(thisFile)
    if len(validFilelist)>0:
        validFilelist = sorted(validFilelist,key=str.lower)
        return validFilelist
    return None

def gettimeutcfromDirFilename(path,file):
    dir_file= path+"/"+file
    fp      = h5py.File(dir_file,'r')
    epoc    = fp['Metadata'].get('utctimeInit')[()]
    fp.close()
    return epoc

def getDatavaluefromDirFilename(path,file,value):
    dir_file= path+"/"+file
    fp      = h5py.File(dir_file,'r')
    array    = fp['Data'].get(value)[()]
    fp.close()
    return array


#·········· Velocidad de Pedestal·················
w = input ("Ingresa velocidad de Pedestal:   ")
w = 4
w = float(w)
#·········· Resolucion minimo en grados···········
alfa = input ("Ingresa resolucion minima en grados:  ")
alfa = 1
alfa = float(alfa)
#·········· IPP del Experimento ··················
IPP  = input ("Ingresa el IPP del experimento:   ")
IPP  = 0.0004
IPP  = float(IPP)
#·········· MODE ··················
mode = input ("Ingresa el MODO del experimento T or F:   ")
mode = "T"
mode = str(mode)

#·········· Tiempo en generar la resolucion min···
#············ MCU ·· var_ang = w * (var_tiempo)···
var_tiempo  = alfa/w
#·········· Tiempo Equivalente en perfiles········
#··········  var_tiempo =  IPP * ( num_perfiles )·
num_perfiles = int(var_tiempo/IPP)

#··········DATA PEDESTAL··························
dir_pedestal = "/home/alex/Downloads/pedestal"
#·········· DATA ADQ······························
if mode=="T":
    dir_adq  = "/home/alex/Downloads/hdf5_testPP/d2020194" # Time domain
else:
    dir_adq  = "/home/alex/Downloads/hdf5_test/d2020194"   # Frequency domain

print( "Velocidad angular             :", w)
print( "Resolucion minima en grados   :", alfa)
print( "Numero de perfiles equivalente:", num_perfiles)
print( "Mode                          :", mode)

#············ First File·············
list_pedestal = getfirstFilefromPath(path=dir_pedestal,meta="PE",ext=".hdf5")
list_adq      = getfirstFilefromPath(path=dir_adq ,meta="D",ext=".hdf5")

#············ utc time ··············
utc_pedestal= gettimeutcfromDirFilename(path=dir_pedestal,file=list_pedestal[0])
utc_adq     = gettimeutcfromDirFilename(path=dir_adq     ,file=list_adq[0])

print("utc_pedestal                  :",utc_pedestal)
print("utc_adq                       :",utc_adq)
#·············Relacion:  utc_adq (+/-) var_tiempo*nro_file= utc_pedestal
time_Interval_p   = 0.01
n_perfiles_p      = 100
if utc_adq>utc_pedestal:
    nro_file = int((int(utc_adq) - int(utc_pedestal))/(time_Interval_p*n_perfiles_p))
    ff_pedestal  = list_pedestal[nro_file]
    utc_pedestal = gettimeutcfromDirFilename(path=dir_pedestal,file=ff_pedestal)
    nro_key_p    = int((utc_adq-utc_pedestal)/time_Interval_p)
    if utc_adq >utc_pedestal:
        ff_pedestal  = ff_pedestal
    else:
        nro_file      = nro_file-1
        ff_pedestal  = list_pedestal[nro_file]
    angulo       = getDatavaluefromDirFilename(path=dir_pedestal,file=ff_pedestal,value="azimuth")
    nro_key_p    = int((utc_adq-utc_pedestal)/time_Interval_p)
    print("nro_file                      :",nro_file)
    print("name_file                     :",ff_pedestal)
    print("utc_pedestal_file             :",utc_pedestal)
    print("nro_key_p                     :",nro_key_p)
    print("utc_pedestal_init             :",utc_pedestal+nro_key_p*time_Interval_p)
    print("angulo_array                  :",angulo[nro_key_p])
#4+25+25+25+21
#while True:
list_pedestal = getfirstFilefromPath(path=dir_pedestal,meta="PE",ext=".hdf5")
list_adq      = getfirstFilefromPath(path=dir_adq ,meta="D",ext=".hdf5")

nro_file       = nro_file #10
nro_key_perfil = nro_key_p
blocksPerFile  = 100
wr_path        = "/home/alex/Downloads/hdf5_wr/"
# Lectura  de archivos de adquisicion para adicion de azimuth
for thisFile in range(len(list_adq)):
    print("thisFileAdq",thisFile)
    angulo_adq    = numpy.zeros(blocksPerFile)
    tmp           = 0
    for j in range(blocksPerFile):
        iterador    = nro_key_perfil + 25*(j-tmp)
        if iterador < n_perfiles_p:
            nro_file = nro_file
        else:
            nro_file = nro_file+1
            tmp      = j
            iterador = nro_key_perfil
        ff_pedestal  = list_pedestal[nro_file]
        angulo       = getDatavaluefromDirFilename(path=dir_pedestal,file=ff_pedestal,value="azimuth")
        angulo_adq[j]= angulo[iterador]
    copyfile(dir_adq+"/"+list_adq[thisFile],wr_path+list_adq[thisFile])
    fp      = h5py.File(wr_path+list_adq[thisFile],'a')
    grp     = fp.create_group("Pedestal")
    dset    = grp.create_dataset("azimuth"  , data=angulo_adq)
    fp.close()
    print("Angulo",angulo_adq)
    print("Angulo",len(angulo_adq))
    nro_key_perfil=iterador + 25
    if nro_key_perfil<  n_perfiles_p:
        nro_file = nro_file
    else:
        nro_file = nro_file+1
        nro_key_perfil= nro_key_p
