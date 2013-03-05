# -*- coding: utf-8 -*-
"""
Module implementing MainWindow.
#+++++++++++++GUI V1++++++++++++++#
@author: AlexanderValdezPortocarrero ñ_ñ
"""
import os, sys
import datetime
from PyQt4.QtGui           import QMainWindow 
from PyQt4.QtCore          import pyqtSignature
from PyQt4.QtCore          import pyqtSignal
from PyQt4                 import QtCore
from PyQt4                 import QtGui

from viewer.ui_unitprocess import Ui_UnitProcess
from viewer.ui_window      import Ui_window
from viewer.ui_mainwindow  import Ui_BasicWindow


from modelProperties  import treeModel

path = os.path.split(os.getcwd())[0]

sys.path.append(path)

from controller  import *

def isRadarFile(file):
        try:
            year = int(file[1:5])
            doy = int(file[5:8])
            set = int(file[8:11])
        except:
            return 0
    
        return 1

def isRadarPath(path):
        try:
            year = int(path[1:5])
            doy = int(path[5:8])
        except:
            return 0
    
        return 1
    

class BasicWindow(QMainWindow,Ui_BasicWindow):
    """
     
    """
    def __init__(self,parent = None):
         """
         
         """
         QMainWindow.__init__(self,parent)
         self.setupUi(self)
         self.__projObjDict = {}
         self.__upObjDict = {}
         self.__arbolDict = {}
         self.readUnitConfObjList=[]
         self.operObjList=[]
         self.idp = 0
         self.online=0
         self.walk=1
         self.indexclick=None
         self.setParameter() 
        
    @pyqtSignature("")
    def on_actionCreate_triggered(self):
        """
        Slot documentation goes here.
        """
        self.setProjectParam()
            
    @pyqtSignature("")
    def on_actionSave_triggered(self):
        """
        Slot documentation goes here.
        """ 
        self.saveProject()   
        
    def on_actionStart_triggered(self):
        """
        """
        self.playProject()
        
    @pyqtSignature("")
    def on_actionCreateToolbar_triggered(self):
        """
        Slot documentation goes here.
        """
        self.setProjectParam()     
    
    @pyqtSignature("")
    def on_actionSaveToolbar_triggered(self):
        """
        Slot documentation goes here.
        """
        self.saveProject()
    
    @pyqtSignature("")
    def on_actionStarToolbar_triggered(self):
        """
        Slot documentation goes here.
        """
        self.playProject()

        
    @pyqtSignature("int")
    def on_proComReadMode_activated(self, p0):
        """
        SELECCION DEL MODO DE LECTURA ON=1, OFF=0
        """
        if p0==0:
           self.online=0
           self.proDelay.setEnabled(False)
        elif p0==1:
            self.online=1
            self.proDelay.setEnabled(True)   
        self.console.clear()
        self.console.append("Choose the type of Walk")

        
        
    @pyqtSignature("int")
    def on_proComDataType_activated(self,index):
        """
        Voltage or Spectra
        """
        if index==0:
           self.datatype='.r'
        elif index==1:
            self.datatype='.pdata'

        self.proDataType.setText(self.datatype)
        self.console.clear()
        self.console.append("Choose your DataPath")
        self.console.append("Use the toolpath or Write the path")   
        
    @pyqtSignature("int")
    def on_proComWalk_activated(self,index):
        """
 
        """
        if index==0:
           self.walk=0
        elif index==1:
            self.walk=1
        
            self.console.clear()
            self.console.append("Now, Push the Button Load to charge the date")
                
    @pyqtSignature("")
    def on_proToolPath_clicked(self):
        """
        Choose your path
        """
        self.dataPath = str(QtGui.QFileDialog.getExistingDirectory(self, 'Open Directory', './',  QtGui.QFileDialog.ShowDirsOnly))
        self.proDataPath.setText(self.dataPath)
        
        self.proComStartDate.clear()
        self.proComEndDate.clear()
        
        if not os.path.exists(self.dataPath):
            self.proOk.setEnabled(False)
            self.console.clear()
            self.console.append("Write a correct a path")
            return 
        self.console.clear()
        self.console.append("Select the read mode")
        
        
    @pyqtSignature("")
    def on_proLoadButton_clicked(self):     
        self.proOk.setEnabled(True)
        self.console.clear()
        self.console.append("You will see the range of date Load")
        self.console.append("First,Don't forget to Choose the Read Mode: OffLine or Online")
        self.console.append("The option Wait is for default 0")   
        self.loadDays()
         
    
    @pyqtSignature("int")
    def on_proComStartDate_activated(self, index):
        """
        SELECCION DEL RANGO DE FECHAS -START DATE
        """
        stopIndex = self.proComEndDate.count() - self.proComEndDate.currentIndex()
        self.proComEndDate.clear()
        
        for i in self.dateList[index:]:
            self.proComEndDate.addItem(i)
            
        self.proComEndDate.setCurrentIndex(self.proComEndDate.count() - stopIndex)

    @pyqtSignature("int")
    def on_proComEndDate_activated(self, index):
        """
        SELECCION DEL RANGO DE FECHAS-END DATE
        """
        startIndex=self.proComStartDate.currentIndex()
        stopIndex = self.proComEndDate.count() - index
        self.proComStartDate.clear()
        for i in self.dateList[:len(self.dateList) - stopIndex + 1]:
            self.proComStartDate.addItem(i)
        self.proComStartDate.setCurrentIndex(startIndex)
             
    @pyqtSignature("")
    def on_proOk_clicked(self):
        """
        Añade al Obj XML de Projecto, name,datatype,date,time,readmode,wait,etc, crea el readUnitProcess del archivo xml.
        Prepara la configuración del diágrama del Arbol del treeView numero 2
        """   
        self.console.clear()
        self.idp +=1
        self.projectObj= Project ()
        self.__projObjDict[self.idp]=self.projectObj
        
        id = self.idp
        name = str(self.proName.text())
        desc=str(self.proDescription.toPlainText())
        self.projectObj.setup(id = id, name=name, description=desc)
        datatype  =  str(self.proComDataType.currentText())
        path      =  str(self.proDataPath.text())
        #path='C://data3'
        online    =  int(self.online)
        walk      =  int(self.walk)
        starDate  =  str(self.proComStartDate.currentText())
        endDate   =  str(self.proComEndDate.currentText())
        reloj1=self.proStartTime.time()
        reloj2=self.proEndTime.time()
        
        self.readUnitConfObj = self.projectObj.addReadUnit(datatype    =    datatype,
                                                            path        =    path,
                                                            startDate   =   starDate,
                                                            endDate     =    endDate,
                                                            startTime=  str(reloj1.hour()) +":"+str(reloj1.minute())+":"+ str(reloj1.second()),
                                                            endTime= str(reloj2.hour()) +":"+str(reloj2.minute())+":"+ str(reloj2.second()),
                                                            online= online,
                                                            walk= walk)
        self.readUnitConfObjList.append(self.readUnitConfObj) 
        
        #Project Explorer
        self.parentItem=self.model.invisibleRootItem()
        self.__arbolDict[self.idp] =QtGui.QStandardItem(QtCore.QString(name).arg(self.idp))
        self.parentItem.appendRow(self.__arbolDict[self.idp])
        self.parentItem=self.__arbolDict[self.idp]
          
        #Project Properties
        self.model_2=treeModel()
        self.model_2.setParams(name       =  self.projectObj.name,
                                directorio =  path,
                                 workspace  =  "C:\\WorkspaceGUI",
                                  remode     =  str(self.proComReadMode.currentText()), 
                                   dataformat =  datatype, 
                                    date       =  str(starDate)+"-"+str(endDate),
                                      initTime   =  str(reloj1.hour()) +":"+str(reloj1.minute())+":"+ str(reloj1.second()),
                                       endTime    =  str(reloj2.hour()) +":"+str(reloj2.minute())+":"+ str(reloj2.second()),
                                        timezone   =  "Local" ,
                                          Summary   = desc)

        self.treeProjectProperties.setModel(self.model_2)
        self.treeProjectProperties.expandAll()
        
        #Disable tabProject after finish the creation
        #self.tabProject.setEnabled(False)
        self.console.clear()
        self.console.append("Now you can add a Unit Processing")
        self.console.append("If you want to save your project")
        self.console.append("click on your project name in the Tree Project Explorer")
#----------------Voltage Operation-------------------#    

    @pyqtSignature("int")
    def on_volOpCebChannels_stateChanged(self, p0):
        """
        Check Box habilita operaciones de Selecci�n de Canales
        """
        if  p0==2:
            self.volOpComChannels.setEnabled(True)
            self.volOpChannel.setEnabled(True)
            
        if  p0==0:
            self.volOpComChannels.setEnabled(False)
            self.volOpChannel.setEnabled(False)

            
    @pyqtSignature("int")
    def on_volOpCebHeights_stateChanged(self, p0):
        """
        Check Box habilita operaciones de Selecci�n de Alturas 
        """
        if  p0==2:
            self.volOpHeights.setEnabled(True)
            self.volOpComHeights.setEnabled(True)

        if  p0==0:
            self.volOpHeights.setEnabled(False)
            self.volOpComHeights.setEnabled(False)

    @pyqtSignature("int")
    def on_volOpCebFilter_stateChanged(self, p0):
         """
         Name='Decoder', optype='other'
         """
         if  p0==2:
            self.volOpFilter.setEnabled(True)
  
         if  p0==0:
            self.volOpFilter.setEnabled(False)

    @pyqtSignature("int")
    def on_volOpCebProfile_stateChanged(self, p0):
        """
        Check Box habilita ingreso  del rango de Perfiles
        """
        if  p0==2:
            self.volOpComProfile.setEnabled(True)
            self.volOpProfile.setEnabled(True)

        if  p0==0:
            self.volOpComProfile.setEnabled(False)
            self.volOpProfile.setEnabled(False)

    @pyqtSignature("int")
    def on_volOpCebDecodification_stateChanged(self, p0):
        """
        Check Box habilita 
        """
        if  p0==2:
            self.volOpComCode.setEnabled(True)
            self.volOpComMode.setEnabled(True)

        if  p0==0:
            self.volOpComCode.setEnabled(False)
            self.volOpComMode.setEnabled(False)
    
            
    @pyqtSignature("int")
    def on_volOpCebCohInt_stateChanged(self, p0):
        """
        Check Box habilita ingresode del numero de Integraciones a realizar
        """
        if  p0==2:
            self.volOpCohInt.setEnabled(True)
        if  p0==0:
            self.volOpCohInt.setEnabled(False)
           
            
                 
        
    @pyqtSignature("")
    def on_volOpOk_clicked(self):
        """
        BUSCA EN LA LISTA DE OPERACIONES DEL TIPO VOLTAJE Y LES A�ADE EL PARAMETRO ADECUADO ESPERANDO LA ACEPTACION DEL USUARIO
        PARA AGREGARLO AL ARCHIVO DE CONFIGURACION XML
        """   
        for i in self.__arbolDict:       
            if self.__arbolDict[i]==self.indexclick:
               if self.__upObjDict.has_key(i)==True:
                   self.upObj=self.__upObjDict[i]
                       
                   if self.volOpCebChannels.isChecked():
                         if  self.volOpComChannels.currentIndex()== 0:
                             opObj10=self.upObj.addOperation(name="selectChannels")
                             self.operObjList.append(opObj10)
                             value=self.volOpChannel.text()                    
                             opObj10.addParameter(name='channelList', value=value, format='intlist')
                         else:
                             opObj10=self.upObj.addOperation(name="selectChannelsByIndex")
                             self.operObjList.append(opObj10)
                             value=self.volOpChannel.text()                    
                             opObj10.addParameter(name='channelIndexList', value=value, format='intlist')
                                                     
                   if self.volOpCebHeights.isChecked():
                         if  self.volOpComHeights.currentIndex()== 0:
                             opObj10=self.upObj.addOperation(name='selectHeights')
                             value=self.volOpHeights.text()
                             valueList=value.split(',')
                             opObj10.addParameter(name='minHei', value=valueList[0], format='float')
                             opObj10.addParameter(name='maxHei', value=valueList[1], format='float')
                         else:
                             opObj10=self.upObj.addOperation(name='selectHeightsByIndex')
                             value=self.volOpHeights.text()
                             valueList=value.split(',')
                             opObj10.addParameter(name='minIndex', value=valueList[0], format='float')
                             opObj10.addParameter(name='maxIndex', value=valueList[1], format='float')
                             
                   if self.volOpCebFilter.isChecked():
                         opObj10=self.upObj.addOperation(name='filterByHeights')
                         value=self.volOpFilter.text()
                         opObj10.addParameter(name='window', value=value, format='int')
      
                   if self.volOpCebProfile.isChecked():
                         opObj10=self.upObj.addOperation(name='ProfileSelector', optype='other')
                         if  self.volOpComProfile.currentIndex()== 0:
                             self.operObjList.append(opObj10)
                             value=self.volOpProfile.text()
                             opObj10.addParameter(name='profileList', value=value, format='intlist')
                         else:
                             self.operObjList.append(opObj10)
                             value=self.volOpProfile.text()
                             opObj10.addParameter(name='profileRangeList', value=value, format='intlist')
                                                                  
                   if self.volOpCebDecodification.isChecked():
                        opObj10=self.upObj.addOperation(name='Decoder', optype='other') 
                        if self.volOpComCode.currentIndex()==0:
                            opObj10.addParameter(name='code', value='1,1,-1,-1,-1,1', format='floatlist')
                            opObj10.addParameter(name='nCode', value='2', format='int')
                            opObj10.addParameter(name='nBaud', value='3', format='int')
                        if self.volOpComCode.currentIndex()==1:
                            opObj10.addParameter(name='code', value='1,1,−1,1,-1,-1,1,-1', format='floatlist')
                            opObj10.addParameter(name='nCode', value='2', format='int')
                            opObj10.addParameter(name='nBaud', value='4', format='int')
                        if self.volOpComCode.currentIndex()==2:
                            opObj10.addParameter(name='code', value='1,1,1,−1,1,-1,-1,-1,1,-1', format='floatlist')
                            opObj10.addParameter(name='nCode', value='2', format='int')
                            opObj10.addParameter(name='nBaud', value='5', format='int')    
                        if self.volOpComCode.currentIndex()==3:
                            opObj10.addParameter(name='code', value='1,1,1,−1,−1,1,−1,-1,-1,-1,1,1,-1,1', format='floatlist')
                            opObj10.addParameter(name='nCode', value='2', format='int')
                            opObj10.addParameter(name='nBaud', value='7', format='int')
                        if self.volOpComCode.currentIndex()==4:
                            opObj10.addParameter(name='code', value='1,1,1,−1,−1,−1,1,−1,−1,1,−1,-1 ,-1 ,-1 ,1 ,1 ,1 ,-1 ,1 ,1 ,-1 ,1', format='floatlist')
                            opObj10.addParameter(name='nCode', value='2', format='int')
                            opObj10.addParameter(name='nBaud', value='11', format='int')    
                        if self.volOpComCode.currentIndex()==5:
                            opObj10.addParameter(name='code', value='1,1,1,1,1,−1,−1,1,1,−1,1,−1,1,-1,-1,-1,-1,-1,1,1,-1,-1,1,-1,1,-1', format='floatlist')
                            opObj10.addParameter(name='nCode', value='2', format='int')
                            opObj10.addParameter(name='nBaud', value='13', format='int')   
                        
                        if self.volOpComMode.currentIndex()==0:
                           opObj10.addParameter(name='mode', value='0', format='int')
       
                        if self.volOpComMode.currentIndex()==1:   
                            opObj10.addParameter(name='mode', value='1', format='int') 
                  
                        if self.volOpComMode.currentIndex()==2:
                            opObj10.addParameter(name='mode', value='2', format='int')
                              
                   if self.volOpCebCohInt.isChecked():
                           opObj10=self.upObj.addOperation(name='CohInt', optype='other')
                           self.operObjList.append(opObj10)
                           value=self.volOpCohInt.text()
                           opObj10.addParameter(name='n', value=value, format='int') 
        #self.tabopVoltage.setEnabled(False)  
        self.console.clear()
        self.console.append("If you want to save your project")
        self.console.append("click on your project name in the Tree Project Explorer")
                           
#----------------Voltage Graph-------------------#    
    @pyqtSignature("int")
    def on_volGraphCebSave_stateChanged(self, p0):
        """
        Check Box habilita ingresode del numero de Integraciones a realizar
        """
        if  p0==2:
            self.volGraphPath.setEnabled(True)
            self.volGraphPrefix.setEnabled(True)
            self.volGraphToolPath.setEnabled(True)

        if  p0==0:
            self.volGraphPath.setEnabled(False)
            self.volGraphPrefix.setEnabled(False)
            self.volGraphToolPath.setEnabled(False)
    
    @pyqtSignature("")
    def on_volGraphToolPath_clicked(self):
        """
        Donde se guardan los DATOS
        """
        self.dataPath = str(QtGui.QFileDialog.getExistingDirectory(self, 'Open Directory', './',  QtGui.QFileDialog.ShowDirsOnly))
        self.volGraphPath.setText(self.dataPath)
        
        if not os.path.exists(self.dataPath):
            self.volGraphOk.setEnabled(False)
            return                          
    
    
    @pyqtSignature("int")
    def on_volGraphComType_activated(self,index):
        """
        Metodo que identifica que tipo de dato se va a trabajar VOLTAGE O ESPECTRA
        """
        if index==0:
           self.volGraphIdFigure.setEnabled(False)
           self.volGraphWintitle.setEnabled(False)
           self.volGraphChannelList.setEnabled(False)
           self.volGraphxrange.setEnabled(False)
           self.volGraphyrange.setEnabled(False)
        if index==1:
           self.volGraphIdFigure.setEnabled(True)
           self.volGraphWintitle.setEnabled(True)
           self.volGraphChannelList.setEnabled(True)
           self.volGraphxrange.setEnabled(True)
           self.volGraphyrange.setEnabled(True)    
       
    @pyqtSignature(" ")
    def on_volGraphOk_clicked(self):
        """
        GRAPH
        """   
        for i in self.__arbolDict:       
            if self.__arbolDict[i]==self.indexclick:
               if self.__upObjDict.has_key(i)==True:
                   self.upObj=self.__upObjDict[i]
                 
                   if self.volGraphComType.currentIndex()==1:
                       opObj10=self.upObj.addOperation(name='Scope', optype='other')
                       self.operObjList.append(opObj10)
                       wintitle=self.volGraphWintitle.text()      
                       channelList=self.volGraphChannelList.text()
                       xvalue= self.volGraphxrange.text()         
                       yvalue= self.volGraphxrange.text()      
                     
                       opObj10.addParameter(name='wintitle', value=wintitle, format='str')
                       opObj10.addParameter(name='channelList', value=channelList, format='int')
                       xvalueList=xvalue.split(',')
                       opObj10.addParameter(name='xmin', value=xvalueList[0], format='int')
                       opObj10.addParameter(name='xmax', value=xvalueList[1], format='int')
                       yvalueList=yvalue.split(",")
                       opObj10.addParameter(name='ymin', value=yvalueList[0], format='int')
                       opObj10.addParameter(name='ymax', value=yvalueList[1], format='int')

                       if self.volGraphCebSave.isChecked():
                           opObj10.addParameter(name='save', value='1', format='int')
                           opObj10.addParameter(name='figpath', value= self.volGraphPath.text())
                           opObj10.addParameter(name='figfile', value= self.volGraphPrefix.text())
        self.tabgraphVoltage.setEnabled(False)  
        self.console.clear()
        self.console.append("If you want to save your project")
        self.console.append("click on your project name in the Tree Project Explorer")
        
#------Spectra operation--------#       
    @pyqtSignature("int")
    def on_specOpCebnFFTpoints_stateChanged(self, p0):
        """
        Habilita la opcion de a�adir el par�metro nFFTPoints a la Unidad de Procesamiento .
        """
        if  p0==2:
            self.specOpnFFTpoints.setEnabled(True)
            self.specOppairsList.setEnabled(True)
        if  p0==0:
            self.specOpnFFTpoints.setEnabled(False)
            self.specOppairsList.setEnabled(False)
            
    @pyqtSignature("int")
    def on_specOpCebChannel_stateChanged(self, p0):
        """
        Habilita la opcion de a�adir el par�metro nFFTPoints a la Unidad de Procesamiento .
        """
        if  p0==2:
            self.specOpChannel.setEnabled(True)
            self.specOpComChannel.setEnabled(True)
        if  p0==0:
            self.specOpChannel.setEnabled(False)
            self.specOpComChannel.setEnabled(False)                     
   
    @pyqtSignature("int")
    def on_specOpCebHeights_stateChanged(self, p0):
        """
        Habilita la opcion de a�adir el par�metro nFFTPoints a la Unidad de Procesamiento .
        """
        if  p0==2:
            self.specOpComHeights.setEnabled(True)
            self.specOpHeights.setEnabled(True)
        if  p0==0:
            self.specOpComHeights.setEnabled(False)
            self.specOpHeights.setEnabled(False)            
    
    
    @pyqtSignature("int")
    def on_specOpCebIncoherent_stateChanged(self, p0):
        """
        Habilita la opcion de a�adir el par�metro nFFTPoints a la Unidad de Procesamiento .
        """
        if  p0==2:
            self.specOpIncoherent.setEnabled(True)
        if  p0==0:
            self.specOpIncoherent.setEnabled(False)

    @pyqtSignature("int")
    def on_specOpCebRemoveDC_stateChanged(self, p0):
        """
        Habilita la opcion de a�adir el par�metro nFFTPoints a la Unidad de Procesamiento .
        """
        if  p0==2:
            self.specOpRemoveDC.setEnabled(True)
        if  p0==0:
            self.specOpRemoveDC.setEnabled(False)    
        
    @pyqtSignature("")
    def on_specOpOk_clicked(self):
        """
        AÑADE OPERACION SPECTRA
        """
        for i in self.__arbolDict:       
            if self.__arbolDict[i]==self.indexclick:
               if self.__upObjDict.has_key(i)==True:
                   self.upObj=self.__upObjDict[i]
                   #            self.operObjList.append(opObj10)      
                   if self.specOpCebnFFTpoints.isChecked():                     
                         value1=self.specOpnFFTpoints.text()
                         value2=self.specOppairsList.text()
                         self.upObj.addParameter(name='nFFTPoints',value=value1,format='int')
                         self.upObj.addParameter(name='pairsList', value=value2, format='pairslist')
                   
                   if self.specOpCebHeights.isChecked():
                      if  self.specOpComHeights.currentIndex()== 0:
                          opObj10=self.upObj.addOperation(name='selectHeights')
                          value=self.specOpHeights.text()
                          valueList=value.split(',')
                          opObj10.addParameter(name='minHei', value=valueList[0], format='float')
                          opObj10.addParameter(name='maxHei', value=valueList[1], format='float') 
                      else:
                          opObj10=self.upObj.addOperation(name='selectHeightsByIndex')
                          value=self.specOpHeights.text()
                          valueList=value.split(',')
                          opObj10.addParameter(name='minIndex', value=valueList[0], format='float')
                          opObj10.addParameter(name='maxIndex', value=valueList[1], format='float') 
                       
                   if self.specOpCebChannel.isChecked():
                       if  self.specOpComChannel.currentIndex()== 0:
                           opObj10=self.upObj.addOperation(name="selectChannels")
                           self.operObjList.append(opObj10)
                           value=self.specOpChannel.text()                    
                           opObj10.addParameter(name='channelList', value=value, format='intlist')
                       else:
                           opObj10=self.upObj.addOperation(name="selectChannelsByIndex")
                           self.operObjList.append(opObj10)
                           value=self.specOpChannel.text()                    
                           opObj10.addParameter(name='channelIndexList', value=value, format='intlist')                                    
                       
                   if self.specOpCebIncoherent.isChecked():
                      opObj10=self.upObj.addOperation(name='IncohInt', optype='other')
                      self.operObjList.append(opObj10)
                      value=self.specOpIncoherent.text()                    
                      opObj10.addParameter(name='n', value=value, format='float') 
                      
                   if self.specOpCebRemoveDC.isChecked():
                       opObj10=self.upObj.addOperation(name='removeDC')
                       value=self.specOpRemoveDC.text()     
                       opObj10.addParameter(name='mode', value=value,format='int')   

                        
        self.tabopSpectra.setEnabled(False)
        self.console.clear()
        self.console.append("If you want to save your project")
        self.console.append("click on your project name in the Tree Project Explorer")
        
        
 #------Spectra  Graph--------#
    @pyqtSignature("int")
    def on_specGraphComType_activated(self,index):
        if index==0:
            print "return"        

        if index==1:
            self.setspecGraph()
            self.specGraphTimeRange.setEnabled(False)
            
        if index==2:
            self.setspecGraph()
            self.specGraphTimeRange.setEnabled(False)
            
        if index==3:
            self.setspecGraph()
            
            
        if index==4:
            self.setspecGraph()
            self.specGraphTimeRange.setEnabled(False)
        
        if index==5:
            self.setspecGraph()
            
        if index==6:
            self.setspecGraph()
            self.specGgraphzrange.setEnabled(False)
            
    @pyqtSignature("int")
    def on_specGraphCebSave_stateChanged(self, p0):
        """
        """
        if  p0==2:
            self.specGraphPath.setEnabled(True)
            self.specGraphPrefix.setEnabled(True)
            self.specGraphToolPath.setEnabled(True)
        if  p0==0:
            self.specGraphPath.setEnabled(False)
            self.specGraphPrefix.setEnabled(False)
            slef.specGraphToolPath.setEnabled(False)   
    @pyqtSignature("")
    def on_specGraphToolPath_clicked(self):        
        """
        """
        self.savePath = str(QtGui.QFileDialog.getExistingDirectory(self, 'Open Directory', './',  QtGui.QFileDialog.ShowDirsOnly))
        self.specGraphPath.setText(self.savePath)
        if not os.path.exists(self.savePath):
            self.console.clear()
            self.console.append("Write a correct a path")
            return 
        
    @pyqtSignature("")
    def on_specGraphOk_clicked(self):
        
        for i in self.__arbolDict:       
            if self.__arbolDict[i]==self.indexclick:
               if self.__upObjDict.has_key(i)==True:
                   self.upObj=self.__upObjDict[i]
       
                   if self.specGraphComType.currentIndex()==1:  
                      opObj10=self.upObj.addOperation(name='SpectraPlot',optype='other')
                      self.properSpecGraph(opObj10)                 
                                 
                   if self.specGraphComType.currentIndex()==2:    
                      opObj10=self.upObj.addOperation(name='CrossSpectraPlot',optype='other')
                      self.properSpecGraph(opObj10)        
                      opObj10.addParameter(name='power_cmap', value='jet', format='str')
                      opObj10.addParameter(name='coherence_cmap', value='jet', format='str')
                      opObj10.addParameter(name='phase_cmap', value='RdBu_r', format='str')              
                      
                   if self.specGraphComType.currentIndex()==3:
                      opObj10=self.upObj.addOperation(name='RTIPlot',optype='other')
                      self.properSpecGraph(opObj10)      
                      value =self.specGraphTimeRange.text()
                      opObj10.addParameter(name='timerange', value=value, format='int')   
   
                   if self.specGraphComType.currentIndex()==4:
                      opObj10=self.upObj.addOperation(name='CoherenceMap',optype='other')
                      self.properSpecGraph(opObj10) 
                      opObj10.addParameter(name='coherence_cmap', value='jet', format='str')
                      opObj10.addParameter(name='phase_cmap', value='RdBu_r', format='str')     
                   
                   if self.specGraphComType.currentIndex()==5:
                      opObj10=self.upObj.addOperation(name='RTIfromNoise',optype='other')
                      self.properSpecGraph(opObj10) 
                      self.specGgraphzrange.setEnabled(False)
                    
                   if self.specGraphComType.currentIndex()==6:
                      opObj10=self.upObj.addOperation(name='ProfilePlot',optype='other')
                      self.properSpecGraph(opObj10) 
                      self.specGgraphzrange.setEnabled(False)   
                   
     
        #self.tabgraphSpectra.setEnabled(False)   
        self.specGraphComType.setEnabled(False)
        self.console.clear()
        self.console.append("If you want to save your project")
        self.console.append("click on your project name in the Tree Project Explorer")       
    
    @pyqtSignature("")
    def on_specGraphClear_clicked(self):
        self.clearspecGraph()
        
    def properSpecGraph(self,opObj10):
          
          self.operObjList.append(opObj10)
          wintitle=self.specGraphWinTitle.text()      
          opObj10.addParameter(name='wintitle', value=wintitle, format='str')
          idfigure=self.specGraphIdFigure.text()
          
          opObj10.addParameter(name='idfigure', value=idfigure, format='int')
   
          channelList=self.specGraphChannelList.text()
          if self.specGraphChannelList.isModified():
              opObj10.addParameter(name='channelList', value=channelList, format='intlist') 
          
          xvalue= self.specGgraphxrange.text() 
          if self.specGgraphxrange.isModified():
              xvalueList=xvalue.split(',')
              try:
                       value=int(xvalueList[0])
                       value=int(xvalueList[1])
                       opObj10.addParameter(name='xmin', value=xvalueList[0], format='int')
                       opObj10.addParameter(name='xmax', value=xvalueList[1], format='int')
              except:
                           return 0     
 
          yvalue= self.specGgraphyrange.text()
          if self.specGgraphyrange.isModified():
              yvalueList=yvalue.split(",")
              try:
                       value=int(yvalueList[0])
                       value=int(yvalueList[1])
                       opObj10.addParameter(name='ymin', value=yvalueList[0], format='int')
                       opObj10.addParameter(name='ymax', value=yvalueList[1], format='int')
              except:
                           return 0     
          
          zvalue= self.specGgraphzrange.text()               
          if self.specGgraphzrange.isModified():
                   zvalueList=zvalue.split(",")
                   try:
                       value=int(zvalueList[0])
                       value=int(zvalueList[1])
                       opObj10.addParameter(name='zmin', value=zvalueList[0], format='int')
                       opObj10.addParameter(name='zmax', value=zvalueList[1], format='int')
                   except:
                           return 0
          
          
          if self.specGraphCebSave.isChecked():
              opObj10.addParameter(name='save', value='1', format='bool')
              opObj10.addParameter(name='figpath', value= self.specGraphPath.text(),format='str')
              opObj10.addParameter(name='figfile', value= self.specGraphPrefix.text(),format='str')                
      

    def setspecGraph(self):
        self.specGraphIdFigure.setEnabled(True)
        self.specGraphWinTitle.setEnabled(True)
        self.specGraphChannelList.setEnabled(True)
        self.specGgraphxrange.setEnabled(True)
        self.specGgraphyrange.setEnabled(True)
        self.specGgraphzrange.setEnabled(True)
        self.specGraphTimeRange.setEnabled(True)
#         self.specGraphPath.setEnabled(True)
#         self.specGraphToolPath.setEnabled(True)
#         self.specGraphPrefix.setEnabled(True)
    def clearspecGraph(self):
        self.specGraphComType.setEnabled(True)
        self.specGraphComType.setCurrentIndex(0)
        self.specGraphIdFigure.clear()
        self.specGraphWinTitle.clear()
        self.specGraphChannelList.clear()
        self.specGgraphxrange.clear()
        self.specGgraphyrange.clear()
        self.specGgraphzrange.clear()
        self.specGraphTimeRange.clear()
        
    def playProject(self):

        for i in self.__arbolDict:            
            if self.__arbolDict[i]==self.indexclick:
                self.projectObj=self.__projObjDict[i] 
        filename="C:\WorkspaceGUI\config"+str(self.projectObj.name)+str(self.projectObj.id)+".xml"
        self.projectObj.readXml(filename)
        #controllerObj.printattr()
        
        self.projectObj.createObjects()
        self.projectObj.connectObjects()
        self.projectObj.run()
        self.console.clear()
        self.console.append("Please Wait...")

                          
    def saveProject(self):

        for i in self.__arbolDict:            
            if self.__arbolDict[i]==self.indexclick:
                self.projectObj=self.__projObjDict[i] 
        filename="C:\WorkspaceGUI\config"+str(self.projectObj.name)+str(self.projectObj.id)+".xml"
        self.projectObj.writeXml(filename)     
        self.console.clear()
        self.console.append("Now,  you can push the icon Start in the toolbar or push start in menu run")
        
                
    def clickFunction(self,index):  
        self.indexclick= index.model().itemFromIndex(index)
       
    def doubleclickFunction(self):
        for i in self.__arbolDict: 
            if self.__arbolDict[i]==self.indexclick:
                if self.__projObjDict.has_key(i)==True:       
                   self.proName.setText(str(self.__projObjDict[i].name))
                   self.proDataPath.setText(str(self.readUnitConfObjList[i-1].path))
                   self.model_2=treeModel()        
                   self.model_2.setParams(name       = str(self.__projObjDict[i].name),
                                           directorio = str(self.readUnitConfObjList[i-1].path),
                                           workspace  =  "C:\\WorkspaceGUI",
                                           remode     =  "off Line", 
                                           dataformat =  self.readUnitConfObjList[i-1].datatype, 
                                           date       =  str(self.readUnitConfObjList[i-1].startDate)+"-"+str(self.readUnitConfObjList[i-1].endDate),
                                           initTime   =   str(self.readUnitConfObjList[i-1].startTime),
                                           endTime    = str(self.readUnitConfObjList[i-1].endTime),
                                           timezone   =  "Local" ,
                                           Summary    =  str(self.__projObjDict[i].description))  
                   self.treeProjectProperties.setModel(self.model_2)
                   self.treeProjectProperties.expandAll()
                   self.tabWidgetProject.setCurrentWidget(self.tabProject)
                   
        if self.indexclick.text()=='Voltage':
           self.tabVoltage.setEnabled(True)
           self.tabSpectra.setEnabled(False)
           self.tabCorrelation.setEnabled(False)
           self.tabWidgetProject.setCurrentWidget(self.tabVoltage)

           self.volOpComChannels.setEnabled(False)
           self.volOpComHeights.setEnabled(False)
           self.volOpFilter.setEnabled(False)
           self.volOpComProfile.setEnabled(False)
           self.volOpComCode.setEnabled(False)
           self.volOpCohInt.setEnabled(False)
           self.volOpChannel.clear()
           self.volOpHeights.clear()
           self.volOpProfile.clear()
           self.volOpFilter.clear()
        
           self.volOpChannel.setEnabled(False)
           self.volOpHeights.setEnabled(False)
           self.volOpProfile.setEnabled(False)
           self.volOpCebHeights.clearFocus()
#            self.volOpCebChannels.clear()
#            self.volOpCebHeights.clear()
#            self.volOpCebFilter.clear()
#            self.volOpCebProfile.clear()
#            self.volOpCebDecodification.clear()
#            self.volOpCebCohInt.clear()
     

        if self.indexclick.text()=='Spectra':
           self.tabSpectra.setEnabled(True) 
           self.tabVoltage.setEnabled(False)
           self.tabCorrelation.setEnabled(False)
           self.tabWidgetProject.setCurrentWidget(self.tabSpectra)         
            
        if self.indexclick.text()=='Correlation':
           self.tabCorrelation.setEnabled(True) 
           self.tabVoltage.setEnabled(False)
           self.tabSpectra.setEnabled(False)
           self.tabWidgetProject.setCurrentWidget(self.tabCorrelation)                    
        
    def popup(self, pos):

        menu = QtGui.QMenu()
        quitAction0 = menu.addAction("AddNewProject")
        quitAction1 = menu.addAction("AddNewProcessingUnit")
        quitAction2 = menu.addAction("Exit")
        #quitAction2 = menu.addAction("Exit")
        action = menu.exec_(self.mapToGlobal(pos))
        if action == quitAction0:
           self.setProjectParam()
        if action == quitAction1:
           self.addPU()   
           self.console.clear()
           self.console.append("Please, Choose the type of Processing Unit")
           self.console.append("If your Datatype is rawdata, you will start with processing unit Type Voltage")
           self.console.append("If your Datatype is pdata, you will choose between processing unit Type Spectra or Correlation")
        if action == quitAction2:
            return
    
    def setProjectParam(self):
        self.tabWidgetProject.setEnabled(True)
        self.tabWidgetProject.setCurrentWidget(self.tabProject)
        self.tabProject.setEnabled(True)
        
        self.proName.clear()
        self.proDataPath.clear()
        self.proComDataType.clear()
        self.proComDataType.addItem("Voltage")
        self.proComDataType.addItem("Spectra")
        startTime="00:00:00"
        endTime="23:59:59"
        starlist=startTime.split(":")
        endlist=endTime.split(":")

        self.time.setHMS(int(starlist[0]),int(starlist[1]),int(starlist[2])) 
        self.proStartTime.setTime(self.time)
        self.time.setHMS(int(endlist[0]),int(endlist[1]),int(endlist[2])) 
        self.proEndTime.setTime(self.time)
        self.proDescription.clear()
        
        self.console.clear()
        self.console.append("Please, Write a name Project")
        self.console.append("Introduce Project Parameters")
        self.console.append("Select data type Voltage( .rawdata)  or Spectra(.pdata)")
        
        
    def addPU(self):
        self.configUP=UnitProcess(self)
        for i in self.__arbolDict:       
            if self.__arbolDict[i]==self.indexclick:
               if self.__projObjDict.has_key(i)==True:
                   self.projectObj=self.__projObjDict[int(i)]
                   self.configUP.dataTypeProject=str(self.proComDataType.currentText())
                   self.configUP.getfromWindowList.append(self.projectObj) 
               else:
                   self.upObj=self.__upObjDict[i]
                   self.configUP.getfromWindowList.append(self.upObj)

        self.configUP.loadTotalList()
        self.configUP.show()      
        self.configUP.closed.connect(self.createUP)
        
    def createUP(self):
             
        if not self.configUP.create:
            return
        
        self.uporProObjRecover=self.configUP.getFromWindow
        
        self.upType = self.configUP.typeofUP
        for i in self.__arbolDict: 
             if self.__arbolDict[i]==self.indexclick:
                  if self.__projObjDict.has_key(i)==True: 
                     self.projectObj=self.__projObjDict[int(i)] 
                     
                  if self.__upObjDict.has_key(i)==True:
                      self.upObj=self.__upObjDict[i]
                      getIdProject=self.upObj.id[0]
                      self.projectObj=self.__projObjDict[int(getIdProject)] 
        
        datatype=str(self.upType)
        uporprojectObj=self.uporProObjRecover
        
        if uporprojectObj.getElementName()=='ProcUnit':
             inputId=uporprojectObj.getId()
             self.console.clear()
             self.console.append("Double Clik on the Processing Unit to enable the tab")
             self.console.append("Before Add other Processing Unit complete the tab")
        else:
            inputId=self.readUnitConfObjList[uporprojectObj.id-1].getId()
            self.console.clear()
            self.console.append("Double Clik on the Processing Unit to enable the tab")
            self.console.append("Before Add other Project or Processing Unit complete the tab")
            
        self.procUnitConfObj1 = self.projectObj.addProcUnit(datatype=datatype, inputId=inputId)
        self.__upObjDict[self.procUnitConfObj1.id]= self.procUnitConfObj1    
        self.parentItem=self.__arbolDict[uporprojectObj.id]
        self.numbertree=int(self.procUnitConfObj1.getId())-1         
        self.__arbolDict[self.procUnitConfObj1.id]=QtGui.QStandardItem(QtCore.QString(datatype).arg(self.numbertree))
        self.parentItem.appendRow(self.__arbolDict[self.procUnitConfObj1.id])        
        self.parentItem=self.__arbolDict[self.procUnitConfObj1.id]
        self.treeProjectExplorer.expandAll()

        
    def searchData(self,path,ext,walk,expLabel=''):
        dateList=[]
        fileList=[]
        if walk== 0:
            files= os.listdir(path)
            for thisFile in files:
                if not os.path.isfile(thisFile):
                    continue
                thisExt = os.path.splitext(thisFile)[-1]
                
                if thisExt != ext:
                    continue
                
                fileList.append(file)
            
            for thisFile in fileList:
                
                if not isRadarFile(thisFile):
                    self.console.clear()
                    self.console.append("Please, Choose the Correct Path")
                    self.proOk.setEnabled(False)
                    continue
                
                year = int(thisFile[1:5])
                doy = int(thisFile[5:8])
                
                date = datetime.date(year,1,1) + datetime.timedelta(doy-1)
                dateformat = date.strftime("%Y/%m/%d")
                
                if dateformat not in dateList:
                    dateList.append(dateformat)                
                
        if walk == 1:
            
            dirList =  os.listdir(path)
            dirList.sort()     
            
            dateList = []
            
            for thisDir in dirList:
                
                if not isRadarPath(thisDir):
                    self.console.clear()
                    self.console.append("Please, Choose the Correct Path")
                    self.proOk.setEnabled(False)
                    continue
                
                doypath = os.path.join(path, thisDir, expLabel)
                
                files = os.listdir(doypath)
                fileList = []
                
                for thisFile in files:
                    
                    if os.path.splitext(thisFile)[-1] != ext:
                        continue
                    
                    if not isRadarFile(thisFile):
                        self.proOk.setEnabled(False)
                        self.console.clear()
                        self.console.append("Please, Choose the Correct Path")  
                        continue
                
                    fileList.append(thisFile)
                    break
                
                if fileList == []:
                    continue
                
                year = int(thisDir[1:5])
                doy = int(thisDir[5:8])
                
                date = datetime.date(year,1,1) + datetime.timedelta(doy-1)
                dateformat = date.strftime("%Y/%m/%d")
                dateList.append(dateformat)

        return dateList
    
    def loadDays(self):
        """
        Method to loads day
        """
        ext=str(self.proDataType.text())
        try:
            punto = str(ext[1:2])
            ext=self.datatype
        except:
            self.console.clear()
            self.console.append("Please, Choose DataType")
            return 0
        
        #-------------------------#
        walk= self.walk
        
        path=str(self.proDataPath.text())
        self.proComStartDate.clear()
        self.proComEndDate.clear()
        #Load List to select start day and end day.(QComboBox)
        dateList=self.searchData(path,ext=ext,walk=walk)
        self.dateList=dateList
        for thisDate in dateList:
            self.proComStartDate.addItem(thisDate)
            self.proComEndDate.addItem(thisDate)
        self.proComEndDate.setCurrentIndex(self.proComStartDate.count()-1)
                
    def setParameter(self):
        self.setWindowTitle("ROJ-Signal Chain")
        self.setWindowIcon(QtGui.QIcon("figure/adn.jpg"))
        self.tabWidgetProject.setEnabled(False)
        self.tabVoltage.setEnabled(False)
        self.tabSpectra.setEnabled(False)
        self.tabCorrelation.setEnabled(False)
        
        self.proName.clear()
        self.proDataPath.setText('C:\Rawdata')
        self.console.append("Welcome to Signal Chain please Create a New Project")
        self.proStartTime.setDisplayFormat("hh:mm:ss")
        self.time =QtCore.QTime()
        self.hour =0
        self.min  =0
        self.sec  =0 
        self.proEndTime.setDisplayFormat("hh:mm:ss")
        startTime="00:00:00"
        endTime="23:59:59"
        starlist=startTime.split(":")
        endlist=endTime.split(":")
        self.time.setHMS(int(starlist[0]),int(starlist[1]),int(starlist[2])) 
        self.proStartTime.setTime(self.time)
        self.time.setHMS(int(endlist[0]),int(endlist[1]),int(endlist[2])) 
        self.proEndTime.setTime(self.time)
        self.proOk.setEnabled(False)
        #set model Project Explorer
        self.model = QtGui.QStandardItemModel()
        self.model.setHorizontalHeaderLabels(("Project Explorer",))
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.treeProjectExplorer)
        self.treeProjectExplorer.setModel(self.model)
        self.treeProjectExplorer.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.treeProjectExplorer.customContextMenuRequested.connect(self.popup)
        self.treeProjectExplorer.clicked.connect(self.clickFunction)

        self.treeProjectExplorer.doubleClicked.connect(self.doubleclickFunction)
        self.treeProjectExplorer.expandAll()
        #set model Project Properties
        
        self.model_2=treeModel()
        self.model_2.showtree()
        self.treeProjectProperties.setModel(self.model_2)
        self.treeProjectProperties.expandAll()
        #set Project
        self.proDelay.setEnabled(False)  
         
         #set Operation Voltage
        self.volOpComChannels.setEnabled(False)
        self.volOpComHeights.setEnabled(False)
        self.volOpFilter.setEnabled(False)
        self.volOpComProfile.setEnabled(False)
        self.volOpComCode.setEnabled(False)
        self.volOpCohInt.setEnabled(False)
        
        self.volOpChannel.setEnabled(False)
        self.volOpHeights.setEnabled(False)
        self.volOpProfile.setEnabled(False)
        self.volOpComMode.setEnabled(False)
        
        self.volGraphPath.setEnabled(False)
        self.volGraphPrefix.setEnabled(False)
        self.volGraphToolPath.setEnabled(False)
        
        #set Graph Voltage
        self.volGraphIdFigure.setEnabled(False)
        self.volGraphWintitle.setEnabled(False)
        self.volGraphChannelList.setEnabled(False)
        self.volGraphxrange.setEnabled(False)
        self.volGraphyrange.setEnabled(False)  
        #set Operation Spectra
        self.specOpnFFTpoints.setEnabled(False)
        self.specOppairsList.setEnabled(False)
        self.specOpComChannel.setEnabled(False)
        self.specOpComHeights.setEnabled(False)
        self.specOpIncoherent.setEnabled(False)
        self.specOpRemoveDC .setEnabled(False)
        self.specOpRemoveInterference.setEnabled(False)
        
        self.specOpChannel.setEnabled(False)
        self.specOpHeights.setEnabled(False)
        #set Graph Spectra  
        self.specGraphIdFigure.setEnabled(False)      
        self.specGraphWinTitle.setEnabled(False)
        self.specGraphChannelList.setEnabled(False)
        self.specGgraphxrange.setEnabled(False)
        self.specGgraphyrange.setEnabled(False)
        self.specGgraphzrange.setEnabled(False)
        self.specGraphTimeRange.setEnabled(False)
        self.specGraphPath.setEnabled(False)
        self.specGraphToolPath.setEnabled(False)
        self.specGraphPrefix.setEnabled(False)
        
        
        #tool tip gui
        QtGui.QToolTip.setFont(QtGui.QFont('SansSerif', 10))
        self.treeProjectExplorer.setToolTip('Right clik to add Project or Unit Process')
        #tool tip gui project
        self.proComWalk.setToolTip('Search 0: Search in format .r or pdata ,Search 1 : Search in D2009123004')
        self.proComWalk.setCurrentIndex(1)
        #tool tip gui volOp
        self.volOpChannel.setToolTip('Example: 1,2,3,4,5')    
        self.volOpHeights.setToolTip('Example: 90,180')
        self.volOpFilter.setToolTip('Example: 3')
        self.volOpProfile.setToolTip('Example:0,125 ')
        self.volOpCohInt.setToolTip('Example: 100')
        self.volOpOk.setToolTip('If you have finish, please Ok ')
        #tool tip gui volGraph
        self.volGraphIdFigure.setToolTip('Example: 1')
        self.volGraphxrange.setToolTip('Example: 10,150')
        self.volGraphyrange.setToolTip('Example: 20,180')
        self.volGraphOk.setToolTip('If you have finish, please Ok ')
        #tool tip gui specOp
        self.specOpnFFTpoints.setToolTip('Example: 100')
        self.specOpIncoherent.setToolTip('Example: 150')
        self.specOpRemoveDC .setToolTip('Example: 1')

        
        self.specOpChannel.setToolTip('Example: 1,2,3,4,5')
        self.specOpHeights.setToolTip('Example: 90,180')
        self.specOppairsList.setToolTip('Example: (0,1),(2,3)')
        #tool tip gui specGraph
        self.specGraphIdFigure.setToolTip('Example: 2')      
        self.specGraphWinTitle.setToolTip('Example: Myplot')
        self.specGraphChannelList.setToolTip('Example: Myplot')
        self.specGgraphxrange.setToolTip('Example: 10,150')
        self.specGgraphyrange.setToolTip('Example: 20,160')
        self.specGgraphzrange.setToolTip('Example: 30,170')

        self.specGraphPrefix.setToolTip('Example: figure')
        
        
class UnitProcess(QMainWindow, Ui_UnitProcess):
    """
    Class documentation goes here.
    """
    closed=pyqtSignal()
    create= False
    def __init__(self, parent = None):
        """
        Constructor
        """
        QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.getFromWindow=None
        self.getfromWindowList=[]
        self.dataTypeProject=None
 
        self.listUP=None    
        
    @pyqtSignature("")
    def on_unitPokbut_clicked(self):
        """
        Slot documentation goes here.
        """
        self.create =True
        self.getFromWindow=self.getfromWindowList[int(self.comboInputBox.currentIndex())]
        #self.nameofUP= str(self.nameUptxt.text())
        self.typeofUP= str(self.comboTypeBox.currentText())
        self.close()

    
    @pyqtSignature("")
    def on_unitPcancelbut_clicked(self):
        """
        Slot documentation goes here.
        """
        self.create=False
        self.close()  

    def loadTotalList(self):
        self.comboInputBox.clear()
        for i in self.getfromWindowList:
            
            name=i.getElementName()
            if name=='Project':
                id= i.id
                name=i.name
                if self.dataTypeProject=='Voltage':
                    self.comboTypeBox.clear()
                    self.comboTypeBox.addItem("Voltage")

                if self.dataTypeProject=='Spectra':
                    self.comboTypeBox.clear()
                    self.comboTypeBox.addItem("Spectra")
                    self.comboTypeBox.addItem("Correlation") 
            
            if name=='ProcUnit':
               id=int(i.id)-1 
               name=i.datatype
               if name == 'Voltage':
                  self.comboTypeBox.clear()
                  self.comboTypeBox.addItem("Spectra")
                  self.comboTypeBox.addItem("Correlation")
               if name == 'Spectra':
                  self.comboTypeBox.clear()
                  self.comboTypeBox.addItem("Spectra")
                  self.comboTypeBox.addItem("Correlation")

               
            self.comboInputBox.addItem(str(name))    
           #self.comboInputBox.addItem(str(name)+str(id))    

    def closeEvent(self, event):
        self.closed.emit()
        event.accept()