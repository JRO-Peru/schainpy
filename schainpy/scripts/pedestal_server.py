###########################################################################
############################### SERVIDOR###################################
######################### SIMULADOR DE PEDESTAL############################
###########################################################################
import time
import math
import numpy
import struct
from time import sleep
import zmq
import pickle
port="5556"
context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://*:%s"%port)
###### PARAMETROS DE ENTRADA################################
print("PEDESTAL RESOLUCION 0.01")
print("MAXIMA VELOCIDAD DEL PEDESTAL")
ang_elev = 4.12
ang_azi  = 30
velocidad= input ("Ingresa velocidad:")
velocidad= float(velocidad)
print (velocidad)
############################################################
sleep(3)
print("Start program")
t1 = time.time()
count=0
while(True):
    tmp_vuelta   = int(360/velocidad)
    t1=t1+tmp_vuelta*count
    count= count+1
    muestras_seg = 100
    t2 = time.time()
    for i in range(tmp_vuelta):
        for j in range(muestras_seg):
            tmp_variable = (i+j/100.0)
            ang_azi      = (tmp_variable)*float(velocidad)
            seconds      = t1+ tmp_variable
            topic=10001
            print ("Azim°: ","%.4f"%ang_azi,"Time:" ,"%.5f"%seconds)
            seconds_dec=(seconds-int(seconds))*1e6
            ang_azi_dec= (ang_azi-int(ang_azi))*1e3
            ang_elev_dec=(ang_elev-int(ang_elev))*1e3
            sleep(0.0088)
            socket.send_string("%d %d %d %d %d %d %d"%(topic,ang_elev,ang_elev_dec,ang_azi,ang_azi_dec,seconds,seconds_dec))
    t3 = time.time()
    print ("Total time for 1 vuelta in Seconds",t3-t2)
