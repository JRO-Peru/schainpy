# -*- coding: utf-8 -*-
"""
Module implementing MainWindow.
#+++++++++++++GUI V1++++++++++++++#
@author: AlexanderValdezPortocarrero ñ_ñ
"""
import os, sys, time
import datetime
import Queue
from PyQt4.QtGui           import QMainWindow 
from PyQt4.QtCore          import pyqtSignature
from PyQt4.QtCore          import pyqtSignal
from PyQt4                 import QtCore
from PyQt4                 import QtGui

from schainpy.gui.viewer.ui_unitprocess import Ui_UnitProcess
from schainpy.gui.viewer.ui_ftp      import Ui_Ftp
from schainpy.gui.viewer.ui_mainwindow  import Ui_BasicWindow
from schainpy.controller  import Project

from modelProperties  import treeModel
from collections import OrderedDict
from os.path import  expanduser
from CodeWarrior.Standard_Suite import file
from comm import *

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
    
class BasicWindow(QMainWindow, Ui_BasicWindow):
    """
    """
    def __init__(self, parent=None):
         """
         
         """
         QMainWindow.__init__(self, parent)
         self.setupUi(self)
         self.__puObjDict = {}
         self.__itemTreeDict = {}
         self.readUnitConfObjList = []
         self.operObjList = []
         self.projecObjView = None
         self.idProject = 0
         # self.idImag = 0
         
         self.idImagscope = 0
         self.idImagspectra = 0
         self.idImagcross = 0
         self.idImagrti = 0
         self.idImagcoherence = 0
         self.idImagpower = 0
         self.idImagrtinoise = 0
         self.idImagspectraHeis = 0
         self.idImagrtiHeis = 0
         
         self.online = 0
         self.walk = 0
         self.create = False
         self.selectedItemTree = None
         self.commCtrlPThread = None
         self.setParameter()
         self.create_comm() 
         self.create_timers()
         self.create_figure()
         self.temporalFTP = ftpBuffer()
         self.projectProperCaracteristica = []
         self.projectProperPrincipal = []
         self.projectProperDescripcion = []
         self.volProperCaracteristica = []
         self.volProperPrincipal = []
         self.volProperDescripcion = []
         self.specProperCaracteristica = []
         self.specProperPrincipal = []
         self.specProperDescripcion = []
         
         self.specHeisProperCaracteristica = []
         self.specHeisProperPrincipal = []
         self.specHeisProperDescripcion = []
         
        # self.pathWorkSpace = './'
         
         self.__projectObjDict = {}
         self.__operationObjDict = {}

    @pyqtSignature("")
    def on_actionCreate_triggered(self):
        """
        Slot documentation goes here.
        """
        self.setInputsProject_View()
        self.create = True
            
    @pyqtSignature("")
    def on_actionSave_triggered(self):
        """
        Slot documentation goes here.
        """ 
        self.saveProject()   
    
    @pyqtSignature("")
    def on_actionClose_triggered(self):
        """
        Slot documentation goes here.
        """ 
        self.close() 
    
    @pyqtSignature("")    
    def on_actionPauseToolbar_triggered(self):
        self.actionStarToolbar.setEnabled(False)
        self.actionPauseToolbar.setEnabled(True)
        self.actionStopToolbar.setEnabled(True)
        self.pauseProject()
     
    @pyqtSignature("")   
    def on_actionStart_triggered(self):
        """
        """
        self.playProject()
    
    
    @pyqtSignature("")     
    def on_actionFTP_triggered(self):
        """
        """
        self.configFTPWindowObj = Ftp(self)
        # if self.temporalFTP.create:
        if self.temporalFTP.createforView:
            server, folder, username, password, ftp_wei, exp_code, sub_exp_code, plot_pos = self.temporalFTP.recover()
            self.configFTPWindowObj.setParmsfromTemporal(server, folder, username, password, ftp_wei, exp_code, sub_exp_code, plot_pos)
        self.configFTPWindowObj.show()
        self.configFTPWindowObj.closed.connect(self.createFTPConfig)
        
    def createFTPConfig(self):
        self.console.clear()
        if not self.configFTPWindowObj.create:
            self.console.append("There is no FTP configuration")
            return
        self.console.append("Push Ok in Spectra view to Add FTP Configuration")
        server, folder, username, password, ftp_wei, exp_code, sub_exp_code, plot_pos = self.configFTPWindowObj.getParmsFromFtpWindow()
        self.temporalFTP.save(server, folder, username, password, ftp_wei, exp_code, sub_exp_code, plot_pos)  
        
    @pyqtSignature("")
    def on_actionOpenToolbar_triggered(self):
        """
        Slot documentation goes here.
        """
        self.create = False
        self.frame_2.setEnabled(True)
        home = expanduser("~")
        self.dir = os.path.join(home, 'schain_workspace')
        # print self.dir
        filename = str(QtGui.QFileDialog.getOpenFileName(self, "Open text file", self.dir, self.tr("Text Files (*.xml)")))
        self.console.clear()
        projectObjLoad = Project()
        try:
            projectObjLoad.readXml(filename)  
        except:
            return 0
        project_name, description = projectObjLoad.name, projectObjLoad.description
        id = projectObjLoad.id
        self.__projectObjDict[id] = projectObjLoad
        # Project Properties
        datatype, data_path, startDate, endDate, startTime, endTime , online , delay, walk, set = self.showProjectProperties(projectObjLoad)        
        # show ProjectView
        self.addProject2ProjectExplorer(id=id, name=project_name)
        self.refreshProjectWindow(project_name, description, datatype, data_path, startDate, endDate, startTime, endTime, online, delay, set)      
        
        if datatype == "Voltage":
            ext = '.r'
            self.specOpProfiles.setEnabled(True)
            self.specOpippFactor.setEnabled(True)
        elif datatype == "Spectra":            
            ext = '.pdata'
        elif datatype == "Fits":
            ext = '.fits'

            
        if online == 0:    
            self.loadDays(data_path, ext, walk)
        else:
                self.proComStartDate.setEnabled(False)
                self.proComEndDate.setEnabled(False)
                self.proStartTime.setEnabled(False)
                self.proEndTime.setEnabled(False)
                self.frame_2.setEnabled(True)
            
        self.tabWidgetProject.setEnabled(True)
        self.tabWidgetProject.setCurrentWidget(self.tabProject) 
        # Disable tabProject after finish the creation
        self.tabProject.setEnabled(True)   
        puObjorderList = OrderedDict(sorted(projectObjLoad.procUnitConfObjDict.items(), key=lambda x: x[0]))
        
        for inputId, puObj in puObjorderList.items():
            # print puObj.datatype, puObj.inputId,puObj.getId(),puObj.parentId
            self.__puObjDict[puObj.getId()] = puObj
            
            if puObj.inputId != "0":
                self.addPU2PELoadXML(id=puObj.getId() , name=puObj.datatype , idParent=puObj.inputId)
                
            if puObj.datatype == "Voltage":
                self.refreshPUWindow(puObj.datatype, puObj)
                self.showPUVoltageProperties(puObj)
                self.showtabPUCreated(datatype=puObj.datatype)
            
            if puObj.datatype == "Spectra":
                self.refreshPUWindow(puObj.datatype, puObj)
                self.showPUSpectraProperties(puObj)
                self.showtabPUCreated(datatype=puObj.datatype)
                
            if puObj.datatype == "SpectraHeis":
                self.refreshPUWindow(puObj.datatype, puObj)
                self.showPUSpectraHeisProperties(puObj)
                self.showtabPUCreated(datatype=puObj.datatype)

        # self.refreshPUWindow(datatype=datatype,puObj=puObj)
                
    @pyqtSignature("")
    def on_actionCreateToolbar_triggered(self):
        """
        Slot documentation goes here.
        """
        self.setInputsProject_View()   
        self.create = True
    
    @pyqtSignature("")
    def on_actionAddPU_triggered(self):
        if len(self.__projectObjDict) == 0:
            outputstr = "First Create a Project then add Processing Unit"
            self.console.clear()
            self.console.append(outputstr)
            return 0
        else:       
           self.addPUWindow()   
           self.console.clear()
           self.console.append("Please, Choose the type of Processing Unit")
           self.console.append("If your Datatype is rawdata, you will start with processing unit Type Voltage")
           self.console.append("If your Datatype is pdata, you will choose between processing unit Type Spectra or Correlation")
           self.console.append("If your Datatype is fits, you will start with processing unit Type SpectraHeis")

           
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
        self.actionStarToolbar.setEnabled(False)
        self.actionPauseToolbar.setEnabled(True)
        self.actionStopToolbar.setEnabled(True)
    
    @pyqtSignature("")
    def on_actionStopToolbar_triggered(self):
        """
        Slot documentation goes here.
        """
        self.actionStarToolbar.setEnabled(True)
        self.actionPauseToolbar.setEnabled(False)
        self.actionStopToolbar.setEnabled(False)
        self.stopProject()
        
    @pyqtSignature("int")
    def on_proComReadMode_activated(self, index):
        """
        SELECCION DEL MODO DE LECTURA ON=1, OFF=0
        """
        if index == 0:
           self.online = 0 
           self.proDelay.setText("0")
           self.proSet.setText("0")
           self.proSet.setEnabled(False)
           self.proDelay.setEnabled(False)
        elif index == 1:
            self.online = 1
            self.proSet.setText(" ")
            self.proDelay.setText("5")
            self.proSet.setEnabled(True)
            self.proDelay.setEnabled(True)   

    @pyqtSignature("int")
    def on_proComDataType_activated(self, index):
        """
        Voltage or Spectra
        """
        if index == 0:
           self.datatype = '.r'
        elif index == 1:
            self.datatype = '.pdata'
        elif index == 2:
            self.datatype = '.fits'

        self.proDataType.setText(self.datatype)
        self.console.clear()

    @pyqtSignature("int")
    def on_proComWalk_activated(self, index):
        """
         
        """
        if index == 0:
           self.walk = 0
        elif index == 1:
            self.walk = 1

    @pyqtSignature("")
    def on_proToolPath_clicked(self):
        """
        Choose your path
        """
        self.dataPath = str(QtGui.QFileDialog.getExistingDirectory(self, 'Open Directory', './', QtGui.QFileDialog.ShowDirsOnly))
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
        self.console.clear()
        parms_ok, project_name, datatype, ext, data_path, read_mode, delay, walk , set = self.checkInputsProject()
        if read_mode == "Offline":
            if parms_ok:   
                self.proComStartDate.clear()
                self.proComEndDate.clear()
                self.loadDays(data_path, ext, walk)
                self.proComStartDate.setEnabled(True)
                self.proComEndDate.setEnabled(True)
                self.proStartTime.setEnabled(True)
                self.proEndTime.setEnabled(True)
                self.frame_2.setEnabled(True)
            return
        if read_mode == "Online":
            if parms_ok:
                self.proComStartDate.addItem("2010/01/30")
                self.proComEndDate.addItem("2013/12/30")
                self.loadDays(data_path, ext, walk)
                self.proComStartDate.setEnabled(False)
                self.proComEndDate.setEnabled(False)
                self.proStartTime.setEnabled(False)
                self.proEndTime.setEnabled(False)
                self.frame_2.setEnabled(True)
    
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
        startIndex = self.proComStartDate.currentIndex()
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
        if self.create:
            self.idProject += 1
            projectId = self.idProject          
            projectObjView = self.createProjectView(projectId)
            readUnitObj = self.createReadUnitView(projectObjView)            
            self.addProject2ProjectExplorer(id=projectId, name=projectObjView.name)            
        else:
            projectObjView = self.updateProjectView()
            projectId = projectObjView.getId()
            idReadUnit = projectObjView.getReadUnitId()
            readUnitObj = self.updateReadUnitView(projectObjView, idReadUnit)
            
            self.__itemTreeDict[projectId].setText(projectObjView.name)
        # Project Properties
        self.showProjectProperties(projectObjView)
        # Disable tabProject after finish the creation
        self.tabProject.setEnabled(True)
        
    @pyqtSignature("")
    def on_proClear_clicked(self):
        self.setInputsProject_View()
        projectObj = self.getSelectedProjectObj()
        
    @pyqtSignature("int")
    def on_volOpCebChannels_stateChanged(self, p0):
        """
        Check Box habilita operaciones de Selecci�n de Canales
        """
        if  p0 == 2:
            self.volOpComChannels.setEnabled(True)
            self.volOpChannel.setEnabled(True)
            
        if  p0 == 0:
            self.volOpComChannels.setEnabled(False)
            self.volOpChannel.setEnabled(False)
            self.volOpChannel.clear()

    @pyqtSignature("int")
    def on_volOpCebHeights_stateChanged(self, p0):
        """
        Check Box habilita operaciones de Selecci�n de Alturas 
        """
        if  p0 == 2:
            self.volOpHeights.setEnabled(True)
            self.volOpComHeights.setEnabled(True)

        if  p0 == 0:
            self.volOpHeights.setEnabled(False)
            self.volOpHeights.clear()
            self.volOpComHeights.setEnabled(False)

    @pyqtSignature("int")
    def on_volOpCebFilter_stateChanged(self, p0):
         """
         Name='Decoder', optype='other'
         """
         if  p0 == 2:
            self.volOpFilter.setEnabled(True)
  
         if  p0 == 0:
            self.volOpFilter.setEnabled(False)
            self.volOpFilter.clear()

    @pyqtSignature("int")
    def on_volOpCebProfile_stateChanged(self, p0):
        """
        Check Box habilita ingreso  del rango de Perfiles
        """
        if  p0 == 2:
            self.volOpComProfile.setEnabled(True)
            self.volOpProfile.setEnabled(True)

        if  p0 == 0:
            self.volOpComProfile.setEnabled(False)
            self.volOpProfile.setEnabled(False)
            self.volOpProfile.clear()
            
    @pyqtSignature("int")
    def on_volOpCebDecodification_stateChanged(self, p0):
        """
        Check Box habilita 
        """
        if  p0 == 2:
            self.volOpComCode.setEnabled(True)
            self.volOpComMode.setEnabled(True)
        if  p0 == 0:
            self.volOpComCode.setEnabled(False)
            self.volOpComMode.setEnabled(False)
                
    @pyqtSignature("int")
    def on_volOpCebCohInt_stateChanged(self, p0):
        """
        Check Box habilita ingresode del numero de Integraciones a realizar
        """
        if  p0 == 2:
            self.volOpCohInt.setEnabled(True)
        if  p0 == 0:
            self.volOpCohInt.setEnabled(False)
            self.volOpCohInt.clear()
            
    @pyqtSignature("int")
    def on_volOpCebRadarfrequency_stateChanged(self, p0):
        """
        Check Box habilita ingresode del numero de Integraciones a realizar
        """
        if  p0 == 2:
            self.volOpRadarfrequency.setEnabled(True)
        if  p0 == 0:
            self.volOpRadarfrequency.clear()
            self.volOpRadarfrequency.setEnabled(False)
    
    @pyqtSignature("")        
    def on_volOutputToolPath_clicked(self):
        dirOutPath = str(QtGui.QFileDialog.getExistingDirectory(self, 'Open Directory', './', QtGui.QFileDialog.ShowDirsOnly))
        self.volOutputPath.setText(dirOutPath)
    
    @pyqtSignature("")     
    def on_specOutputToolPath_clicked(self):
        dirOutPath = str(QtGui.QFileDialog.getExistingDirectory(self, 'Open Directory', './', QtGui.QFileDialog.ShowDirsOnly))
        self.specOutputPath.setText(dirOutPath)
        
    @pyqtSignature("")     
    def on_specHeisOutputToolPath_clicked(self):
        dirOutPath = str(QtGui.QFileDialog.getExistingDirectory(self, 'Open Directory', './', QtGui.QFileDialog.ShowDirsOnly))
        self.specHeisOutputPath.setText(dirOutPath)
    
    @pyqtSignature("")     
    def on_specHeisOutputMetadaToolPath_clicked(self):
        home = expanduser("~")
        self.dir = os.path.join(home, 'schain_workspace')
        filename = str(QtGui.QFileDialog.getOpenFileName(self, "Open text file", self.dir, self.tr("Text Files (*.xml)")))
        self.specHeisOutputMetada.setText(filename)
        
    @pyqtSignature("")
    def on_volOpOk_clicked(self):
        """
        BUSCA EN LA LISTA DE OPERACIONES DEL TIPO VOLTAJE Y LES A�ADE EL PARAMETRO ADECUADO ESPERANDO LA ACEPTACION DEL USUARIO
        PARA AGREGARLO AL ARCHIVO DE CONFIGURACION XML
        """   
        puObj = self.getSelectedPUObj()
        puObj.removeOperations()
        
        if self.volOpCebRadarfrequency.isChecked():
            value = self.volOpRadarfrequency.text()
            format = 'float'
            name_operation = 'setRadarFrequency'
            name_parameter = 'frequency'
            if not value == "":
                try:
                    radarfreq = float(self.volOpRadarfrequency.text())
                except:
                    self.console.clear()
                    self.console.append("Write the parameter Radar Frequency  type float")
                    return 0
                opObj = puObj.addOperation(name=name_operation)
                opObj.addParameter(name=name_parameter, value=radarfreq, format=format)
                    
                    
        
        if self.volOpCebChannels.isChecked():
            value = self.volOpChannel.text()
            format = 'intlist'
            if self.volOpComChannels.currentIndex() == 0:            
                name_operation = "selectChannels"
                name_parameter = 'channelList'
            else:       
                name_operation = "selectChannelsByIndex"
                name_parameter = 'channelIndexList'
                
            opObj = puObj.addOperation(name=name_operation)
            opObj.addParameter(name=name_parameter, value=value, format=format)
            
        if self.volOpCebHeights.isChecked():
           value = self.volOpHeights.text()
           valueList = value.split(',')
           format = 'float'
           if  self.volOpComHeights.currentIndex() == 0:
               name_operation = 'selectHeights'
               name_parameter1 = 'minHei'
               name_parameter2 = 'maxHei'
           else:
               name_operation = 'selectHeightsByIndex'   
               name_parameter1 = 'minIndex'
               name_parameter2 = 'maxIndex'
           opObj = puObj.addOperation(name=name_operation)
           opObj.addParameter(name=name_parameter1, value=valueList[0], format=format)
           opObj.addParameter(name=name_parameter2, value=valueList[1], format=format)
           
        if self.volOpCebFilter.isChecked():
           value = self.volOpFilter.text()
           format = 'int'
           name_operation = 'filterByHeights'
           name_parameter = 'window'
           opObj = puObj.addOperation(name=name_operation)
           opObj.addParameter(name=name_parameter, value=value, format=format)  

        if self.volOpCebProfile.isChecked():
            value = self.volOpProfile.text()
            format = 'intlist'
            optype = 'other'
            name_operation = 'ProfileSelector'
            if  self.volOpComProfile.currentIndex() == 0:
                name_parameter = 'profileList'
            else:
                name_parameter = 'profileRangeList'
            opObj = puObj.addOperation(name='ProfileSelector', optype='other')
            opObj.addParameter(name=name_parameter, value=value, format=format)  
        
        if self.volOpCebDecodification.isChecked():   
            name_operation = 'Decoder'
            optype = 'other'
            format1 = 'floatlist'
            format2 = 'int'
            format3 = 'int'
            format4 = 'int'
            name_parameter1 = 'code'
            name_parameter2 = 'nCode'
            name_parameter3 = 'nBaud'
            name_parameter4 = 'mode'
 
            if self.volOpComCode.currentIndex() == 0:
                value1 = '1,1,-1'
                value2 = '1'
                value3 = '3'
            if self.volOpComCode.currentIndex() == 1:
                value1 = '1,1,-1,1'
                value2 = '1'
                value3 = '4'
            if self.volOpComCode.currentIndex() == 2:
                value1 = '1,1,1,−1,1'
                value2 = '1'
                value3 = '5'
            if self.volOpComCode.currentIndex() == 3:
                value1 = '1,1,1,-1,-1,1,-1'
                value2 = '1'
                value3 = '7'
            if self.volOpComCode.currentIndex() == 4:
                value1 = '1,1,1,-1,-1,-1,1,-1,-1,1,-1'
                value2 = '1'
                value3 = '11'
            if self.volOpComCode.currentIndex() == 5:
                value1 = '1,1,1,1,1,-1,-1,1,1,-1,1,-1,1'
                value2 = '1'
                value3 = '13'
            if self.volOpComCode.currentIndex() == 6:
                value1 = '1,1,-1,-1,-1,1'
                value2 = '2'
                value3 = '3'
            if self.volOpComCode.currentIndex() == 7:
                value1 = '1,1,-1,1,-1,-1,1,-1'
                value2 = '2'
                value3 = '4'
            if self.volOpComCode.currentIndex() == 8:
                value1 = '1,1,1,-1,1,-1,-1,-1,1,-1'
                value2 = '2'
                value3 = '5'
            if self.volOpComCode.currentIndex() == 9:
                value1 = '1,1,1,-1,-1,1,-1,-1,-1,-1,1,1,-1,1'
                value2 = '2'
                value3 = '7'
            if self.volOpComCode.currentIndex() == 10:
                value1 = '1,1,1,-1,-1,-1,1,-1,-1,1,-1,-1 ,-1 ,-1 ,1 ,1,1,-1 ,1 ,1 ,-1 ,1'
                value2 = '2'
                value3 = '11'
            if self.volOpComCode.currentIndex() == 11:
                value1 = '1,1,1,1,1,-1,-1,1,1,-1,1,-1,1,-1,-1,-1,-1,-1,1,1,-1,-1,1,-1,1,-1'
                value2 = '2'
                value3 = '13'
            if self.volOpComMode.currentIndex() == 0:
                value4 = '0'
            if self.volOpComMode.currentIndex() == 1:
                value4 = '1'
            if self.volOpComMode.currentIndex() == 2:
                value4 = '2'
            opObj = puObj.addOperation(name=name_operation, optype='other')  
            if self.volOpComCode.currentIndex() == 12:
                pass
            else:
                opObj.addParameter(name=name_parameter1, value=value1, format=format1)
                opObj.addParameter(name=name_parameter2, value=value2, format=format2)
                opObj.addParameter(name=name_parameter3, value=value3, format=format3)  
                opObj.addParameter(name=name_parameter4, value=value4, format=format4)  
                    
        if self.volOpCebCohInt.isChecked():
            name_operation = 'CohInt'
            optype = 'other'
            value = self.volOpCohInt.text()
            name_parameter = 'n'
            format = 'float'
            
            opObj = puObj.addOperation(name='CohInt', optype='other')
            opObj.addParameter(name=name_parameter, value=value, format=format) 

        if self.volGraphCebshow.isChecked():    
            name_operation = 'Plot'
            optype = 'other'
            name_parameter = 'type'
            value = 'Scope' 
            if self.idImagscope == 0:
                self.idImagscope = 100
            else:
                self.idImagscope = self.idImagscope + 1

            name_parameter1 = 'id'
            value1 = int(self.idImagscope)
            format1 = 'int'        
            format = 'str'
     
            opObj = puObj.addOperation(name=name_operation, optype=optype)
            opObj.addParameter(name=name_parameter, value=value, format=format)
            opObj.addParameter(name=name_parameter1, value=value1, format=format1)
            
            channelList = self.volGraphChannelList.text()
            xvalue = self.volGraphfreqrange.text() 
            yvalue = self.volGraphHeightrange.text()

            if self.volGraphChannelList.isModified():
                try:    
                    value = str(channelList)              
                except: 
                         return 0
                opObj.addParameter(name='channelList', value=value, format='intlist')

            if not xvalue == "":
                xvalueList = xvalue.split(',')
                try:
                   value0 = int(xvalueList[0])
                   value1 = int(xvalueList[1])  
                except:
                       return 0
                opObj.addParameter(name='xmin', value=value0, format='int')
                opObj.addParameter(name='xmax', value=value1, format='int')               
                
                
            if not yvalue == "":
               yvalueList = yvalue.split(",")
               try:
                   value = yvalueList[0]
                   value = yvalueList[1]
               except:
                       return 0
               opObj.addParameter(name='ymin', value=yvalueList[0], format='int')
               opObj.addParameter(name='ymax', value=yvalueList[1], format='int')
                   
            if self.volGraphCebSave.isChecked():
                opObj.addParameter(name='save', value='1', format='int')
                opObj.addParameter(name='figpath', value=self.volGraphPath.text(), format='str')
                value = self.volGraphPrefix.text()
                if not value == "":
                   try:
                       value = str(self.volGraphPrefix.text())
                   except:
                       self.console.clear()
                       self.console.append("Please Write prefix")
                       return 0    
                   opObj.addParameter(name='figfile', value=self.volGraphPrefix.text(), format='str')
                
        # if something happend 
        parms_ok, output_path, blocksperfile, profilesperblock = self.checkInputsPUSave(datatype='Voltage')
        name_operation = 'VoltageWriter'
        optype = 'other'
        name_parameter1 = 'path'
        name_parameter2 = 'blocksPerFile'
        name_parameter3 = 'profilesPerBlock'
        value1 = output_path
        value2 = blocksperfile
        value3 = profilesperblock
        format = "int"
        if parms_ok:
            opObj = puObj.addOperation(name=name_operation, optype=optype)
            opObj.addParameter(name=name_parameter1, value=value1)
            opObj.addParameter(name=name_parameter2, value=value2, format=format)
            opObj.addParameter(name=name_parameter3, value=value3, format=format)
        
            

        #---------NEW VOLTAGE PROPERTIES
        self.showPUVoltageProperties(puObj)
        

        self.console.clear()
        self.console.append("If you want to save your project")
        self.console.append("click on your project name in the Tree Project Explorer")
                 
      
    """
    Voltage Graph
    """
    @pyqtSignature("int")
    def on_volGraphCebSave_stateChanged(self, p0):
        """
        Check Box habilita ingresode del numero de Integraciones a realizar
        """
        if  p0 == 2:
            self.volGraphPath.setEnabled(True)
            self.volGraphPrefix.setEnabled(True)
            self.volGraphToolPath.setEnabled(True)

        if  p0 == 0:
            self.volGraphPath.setEnabled(False)
            self.volGraphPrefix.setEnabled(False)
            self.volGraphToolPath.setEnabled(False)
    
    @pyqtSignature("")
    def on_volGraphToolPath_clicked(self):
        """
        Donde se guardan los DATOS
        """
        self.dataPath = str(QtGui.QFileDialog.getExistingDirectory(self, 'Open Directory', './', QtGui.QFileDialog.ShowDirsOnly))
        self.volGraphPath.setText(self.dataPath)
        
#         if not os.path.exists(self.dataPath):
#             self.volGraphOk.setEnabled(False)
#             return                          
    
    @pyqtSignature("int")
    def on_volGraphCebshow_stateChanged(self, p0):
        """
        Check Box habilita ingresode del numero de Integraciones a realizar
        """   
        if p0 == 0:
 
           self.volGraphChannelList.setEnabled(False)
           self.volGraphfreqrange.setEnabled(False)
           self.volGraphHeightrange.setEnabled(False)
        if p0 == 2:

           self.volGraphChannelList.setEnabled(True)
           self.volGraphfreqrange.setEnabled(True)
           self.volGraphHeightrange.setEnabled(True)  

    """
    Spectra operation
    """       
    @pyqtSignature("int")
    def on_specOpCebRadarfrequency_stateChanged(self, p0):
        """
        Check Box habilita ingresode del numero de Integraciones a realizar
        """
        if  p0 == 2:
            self.specOpRadarfrequency.setEnabled(True)
        if  p0 == 0:
            self.specOpRadarfrequency.clear()
            self.specOpRadarfrequency.setEnabled(False)
    
    
    @pyqtSignature("int")
    def on_specOpCebCrossSpectra_stateChanged(self, p0):
        """
        Habilita la opcion de a�adir el par�metro CrossSpectra a la Unidad de Procesamiento .
        """
        if  p0 == 2:
          #  self.specOpnFFTpoints.setEnabled(True)
            self.specOppairsList.setEnabled(True)
        if  p0 == 0:
          #  self.specOpnFFTpoints.setEnabled(False)
            self.specOppairsList.setEnabled(False)
            
    @pyqtSignature("int")
    def on_specOpCebChannel_stateChanged(self, p0):
        """
        Habilita la opcion de a�adir el par�metro numero de Canales a la Unidad de Procesamiento .
        """
        if  p0 == 2:
            self.specOpChannel.setEnabled(True)
            self.specOpComChannel.setEnabled(True)
        if  p0 == 0:
            self.specOpChannel.setEnabled(False)
            self.specOpComChannel.setEnabled(False)                       
   
    @pyqtSignature("int")
    def on_specOpCebHeights_stateChanged(self, p0):
        """
        Habilita la opcion de a�adir el par�metro de alturas a la Unidad de Procesamiento .
        """
        if  p0 == 2:
            self.specOpComHeights.setEnabled(True)
            self.specOpHeights.setEnabled(True)
        if  p0 == 0:
            self.specOpComHeights.setEnabled(False)
            self.specOpHeights.setEnabled(False)            
    
    
    @pyqtSignature("int")
    def on_specOpCebIncoherent_stateChanged(self, p0):
        """
        Habilita la opcion de a�adir el par�metro integraciones incoherentes a la Unidad de Procesamiento .
        """
        if  p0 == 2:
            self.specOpIncoherent.setEnabled(True)
        if  p0 == 0:
            self.specOpIncoherent.setEnabled(False)

    @pyqtSignature("int")
    def on_specOpCebRemoveDC_stateChanged(self, p0):
        """
        Habilita la opcion de a�adir el par�metro remover DC a la Unidad de Procesamiento .
        """
        if  p0 == 2:
            self.specOpComRemoveDC.setEnabled(True)
        if  p0 == 0:
            self.specOpComRemoveDC.setEnabled(False)    
            
    @pyqtSignature("int")
    def on_specOpCebgetNoise_stateChanged(self, p0):
        """
        Habilita la opcion de a�adir la estimacion de ruido a la Unidad de Procesamiento .
        """
        if  p0 == 2:
            self.specOpgetNoise.setEnabled(True)

        if  p0 == 0:
            self.specOpgetNoise.setEnabled(False) 

    def refreshID(self, puObj):
        opObj = puObj.getOpObjfromParamValue(value="Scope")
        if opObj == None:
            pass
        else:
           name_parameter1 = 'id'
           format1 = 'int'
           if self.idImagscope == 0:
              self.idImagscope = 100
           else:
              self.idImagscope = self.idImagscope + 1
           value1 = int(self.idImagscope)
           opObj.changeParameter(name=name_parameter1, value=value1, format=format1)
        
        opObj = puObj.getOpObjfromParamValue(value="SpectraPlot")
        if opObj == None:
            pass
        else:
           name_parameter1 = 'id'
           format1 = 'int'
           if self.idImagspectra == 0:
              self.idImagspectra = 200
           else:
              self.idImagspectra = self.idImagspectra + 1
           value1 = int(self.idImagspectra)
           opObj.changeParameter(name=name_parameter1, value=value1, format=format1)
        
                        
        opObj = puObj.getOpObjfromParamValue(value="CrossSpectraPlot")
        if opObj == None:
            pass
        else:
            name_parameter1 = 'id'
            format1 = 'int'
            if self.idImagcross == 0:
               self.idImagcross = 300
            else:
               self.idImagcross = self.idImagcross + 1
            value1 = int(self.idImagcross)
            opObj.changeParameter(name=name_parameter1, value=value1, format=format1)      
                                                        
        opObj = puObj.getOpObjfromParamValue(value="RTIPlot")
        if opObj == None:
            pass
        else:
            name_parameter1 = 'id'
            format1 = 'int'
            if self.idImagrti == 0:
               self.idImagrti = 400
            else:
               self.idImagrti = self.idImagrti + 1
            value1 = int(self.idImagrti)
            opObj.changeParameter(name=name_parameter1, value=value1, format=format1) 
            
        opObj = puObj.getOpObjfromParamValue(value="CoherenceMap")
        if opObj == None:
            pass
        else:
            name_parameter1 = 'id'
            format1 = 'int'
            if self.idImagcoherence == 0:
               self.idImagcoherence = 500
            else:
               self.idImagcoherence = self.idImagcoherence + 1
            value1 = int(self.idImagcoherence)
            opObj.changeParameter(name=name_parameter1, value=value1, format=format1) 
        
        opObj = puObj.getOpObjfromParamValue(value="PowerProfilePlot")
        if opObj == None:
            pass
        else:
            name_parameter1 = 'id'
            format1 = 'int'
            if self.idImagpower == 0:
               self.idImagpower = 600
            else:
               self.idImagpower = self.idImagpower + 1
            value1 = int(self.idImagpower)
            opObj.changeParameter(name=name_parameter1, value=value1, format=format1) 
            
        opObj = puObj.getOpObjfromParamValue(value="Noise")
        if opObj == None:
            pass
        else:
            name_parameter1 = 'id'
            format1 = 'int'
            if self.idImagrtinoise == 0:
               self.idImagrtinoise = 700
            else:
               self.idImagrtinoise = self.idImagrtinoise + 1
            value1 = int(self.idImagrtinoise)
            opObj.changeParameter(name=name_parameter1, value=value1, format=format1) 
            
        opObj = puObj.getOpObjfromParamValue(value="SpectraHeisScope")
        if opObj == None:
            pass
        else:
            name_parameter1 = 'id'
            format1 = 'int'
            if self.idImagspectraHeis == 0:
               self.idImagspectraHeis = 800
            else:
               self.idImagspectraHeis = self.idImagspectraHeis + 1
            value1 = int(self.idImagspectraHeis)
            opObj.changeParameter(name=name_parameter1, value=value1, format=format1) 
            
        opObj = puObj.getOpObjfromParamValue(value="RTIfromSpectraHeis")
        if opObj == None:
            pass
        else:
            name_parameter1 = 'id'
            format1 = 'int'
            if self.idImagrtiHeis == 0:
               self.idImagrtiHeis = 900
            else:
               self.idImagrtiHeis = self.idImagrtiHeis + 1
            value1 = int(self.idImagrtiHeis)
            opObj.changeParameter(name=name_parameter1, value=value1, format=format1) 
            
    @pyqtSignature("")
    def on_specOpOk_clicked(self):
        """
        AÑADE OPERACION SPECTRA
        """
        puObj = self.getSelectedPUObj()
        puObj.removeOperations()
        
        if self.specOpCebRadarfrequency.isChecked():
            value = self.specOpRadarfrequency.text()
            format = 'float'
            name_operation = 'setRadarFrequency'
            name_parameter = 'frequency'
            if not value == "":
                try:
                    radarfreq = float(self.specOpRadarfrequency.text())
                except:
                    self.console.clear()
                    self.console.append("Write the parameter Radar Frequency  type float")
                    return 0
                opObj = puObj.addOperation(name=name_operation)
                opObj.addParameter(name=name_parameter, value=radarfreq, format=format)
        

        if self.proComDataType.currentText() == 'Voltage':
            name_parameter = 'nFFTPoints'
            value = self.specOpnFFTpoints.text()
            name_parameter1 = 'nProfiles'
            value1 = self.specOpProfiles.text()
            name_parameter2 = 'ippFactor'
            value2 = self.specOpippFactor.text()
            format = 'int'
            try:
                value = int(self.specOpnFFTpoints.text())
            except:
                self.console.clear()
                self.console.append("Please Write the number of FFT")
                return 0
            puObj.addParameter(name=name_parameter, value=value, format=format)
            if not value1 == "":
                try:
                    value1 = int(self.specOpProfiles.text())
                except:
                    self.console.clear()
                    self.console.append("Please Write the number of Profiles")
                    return 0
                puObj.addParameter(name=name_parameter1, value=value1, format=format)
            if not value2 == "":
                try:
                    value2 = int(self.specOpippFactor.text())
                except:
                    self.console.clear()
                    self.console.append("Please Write the Number of IppFactor")
                puObj.addParameter(name=name_parameter2 , value=value2 , format=format)
                    
        if self.specOpCebCrossSpectra.isChecked():
            name_parameter = 'pairsList'
            format = 'pairslist'         
            value2 = self.specOppairsList.text()
            puObj.addParameter(name=name_parameter, value=value2, format=format)
                                
        if self.specOpCebHeights.isChecked():
            value = self.specOpHeights.text()
            valueList = value.split(',')
            format = 'float'
            value0 = valueList[0]
            value1 = valueList[1]
            
            if self.specOpComHeights.currentIndex() == 0:
                name_operation = 'selectHeights'
                name_parameter1 = 'minHei'
                name_parameter2 = 'maxHei'
            else:
                name_operation = 'selectHeightsByIndex'
                name_parameter1 = 'minIndex'
                name_parameter2 = 'maxIndex'
            opObj = puObj.addOperation(name=name_operation)    
            opObj.addParameter(name=name_parameter1, value=value0, format=format)
            opObj.addParameter(name=name_parameter2, value=value1, format=format) 
          
        if self.specOpCebChannel.isChecked():
            value = self.specOpChannel.text()
            format = 'intlist'
            if self.specOpComChannel.currentIndex() == 0:
                name_operation = "selectChannels"
                name_parameter = 'channelList'
            else:
                name_operation = "selectChannelsByIndex" 
                name_parameter = 'channelIndexList'
            opObj = puObj.addOperation(name="selectChannels")
            opObj.addParameter(name=name_parameter, value=value, format=format)
            
        if self.specOpCebIncoherent.isChecked():
            value = self.specOpIncoherent.text()   
            name_operation = 'IncohInt'
            optype = 'other'
            if self.specOpCobIncInt.currentIndex() == 0:
                name_parameter = 'timeInterval'
                format = 'float'
            else:
                name_parameter = 'n'
                format = 'float'

            opObj = puObj.addOperation(name=name_operation, optype=optype)
            opObj.addParameter(name=name_parameter, value=value, format=format)
           
        if self.specOpCebRemoveDC.isChecked():
            name_operation = 'removeDC'
            name_parameter = 'mode'
            format = 'int'
            if self.specOpComRemoveDC.currentIndex() == 0:
                value = 1
            else:
                value = 2
            opObj = puObj.addOperation(name=name_operation)
            opObj.addParameter(name=name_parameter, value=value, format=format)
            
        if self.specOpCebRemoveInt.isChecked():
            name_operation = 'removeInterference'
            opObj = puObj.addOperation(name=name_operation)
            
                                        
        if self.specOpCebgetNoise.isChecked():
            value = self.specOpgetNoise.text()
            valueList = value.split(',')
            format = 'float'
            name_operation = "getNoise"
            opObj = puObj.addOperation(name=name_operation)

            if not value == '':
               valueList = value.split(',')
               length = len(valueList)
               if length == 1:
                   try:
                       value1 = float(valueList[0])
                   except:
                       self.console.clear()
                       self.console.append("Please Write  correct parameter Get Noise")
                       return 0
                   name1 = 'minHei'
                   opObj.addParameter(name=name1, value=value1, format=format)
               elif length == 2:
                   try:
                       value1 = float(valueList[0])
                       value2 = float(valueList[1])
                   except:
                       self.console.clear()
                       self.console.append("Please Write  corrects parameter Get Noise")
                       return 0
                   name1 = 'minHei'
                   name2 = 'maxHei'
                   opObj.addParameter(name=name1, value=value1, format=format)
                   opObj.addParameter(name=name2, value=value2, format=format)    
                                    
               elif length == 3:
                   try:
                       value1 = float(valueList[0])
                       value2 = float(valueList[1])
                       value3 = float(valueList[2])
                   except:
                       self.console.clear()
                       self.console.append("Please Write  corrects parameter Get Noise")
                       return 0
                   name1 = 'minHei'
                   name2 = 'maxHei'
                   name3 = 'minVel'
                   opObj.addParameter(name=name1, value=value1, format=format)
                   opObj.addParameter(name=name2, value=value2, format=format)
                   opObj.addParameter(name=name3, value=value3, format=format)    

               elif length == 4:
                   try:
                       value1 = float(valueList[0])
                       value2 = float(valueList[1])
                       value3 = float(valueList[2])
                       value4 = float(valueList[3])
                   except:
                       self.console.clear()
                       self.console.append("Please Write  corrects parameter Get Noise")
                       return 0
                   name1 = 'minHei'
                   name2 = 'maxHei'
                   name3 = 'minVel'
                   name4 = 'maxVel'
                   opObj.addParameter(name=name1, value=value1, format=format)
                   opObj.addParameter(name=name2, value=value2, format=format)
                   opObj.addParameter(name=name3, value=value3, format=format)   
                   opObj.addParameter(name=name4, value=value4, format=format)   
                   
               elif length > 4:
                   self.console.clear()
                   self.console.append("Get Noise Operation only accepts  4 parameters")
                   return 0
                      
        #-----Spectra Plot-----
        if self.specGraphCebSpectraplot.isChecked():   
            name_operation = 'Plot'
            optype = 'other'
            name_parameter = 'type'
            value = 'SpectraPlot'
            format = 'str'
            if self.idImagspectra == 0:
                self.idImagspectra = 200
            else:
                self.idImagspectra = self.idImagspectra + 1
            name_parameter1 = 'id'
            value1 = int(self.idImagspectra)
            format1 = 'int'
            
            format = 'str'
            
            channelList = self.specGgraphChannelList.text()
            xvalue = self.specGgraphFreq.text() 
            yvalue = self.specGgraphHeight.text()
            zvalue = self.specGgraphDbsrange.text()               
            opObj = puObj.addOperation(name=name_operation, optype=optype)
            opObj.addParameter(name=name_parameter, value=value, format=format)
            opObj.addParameter(name=name_parameter1, value=value1, format=format1)      
            
            if not channelList == '':
               name_parameter = 'channelList'
               format = 'intlist'
               opObj.addParameter(name=name_parameter, value=channelList, format=format) 
           
            if not xvalue == '':
               xvalueList = xvalue.split(',')
               try:
                   value1 = float(xvalueList[0])
                   value2 = float(xvalueList[1])
               except:
                       self.console.clear()
                       self.console.append("Please Write  corrects parameter freq")
                       return 0
               name1 = 'xmin'
               name2 = 'xmax'
               format = 'float'
               opObj.addParameter(name=name1, value=value1, format=format)
               opObj.addParameter(name=name2, value=value2, format=format)
            #------specGgraphHeight---
            if not yvalue == '':
                  yvalueList = yvalue.split(",")
                  try:
                       value1 = float(yvalueList[0])
                       value2 = float(yvalueList[1])
                  except:
                      self.console.clear()
                      self.console.append("Please Write  corrects parameter Height")
                      return 0 
                  name1 = 'ymin'
                  name2 = 'ymax'
                  format = 'float'
                  opObj.addParameter(name=name1, value=value1, format=format)
                  opObj.addParameter(name=name2, value=value2, format=format) 
            
            if not zvalue == '':
                zvalueList = zvalue.split(",")
                try:
                       value = float(zvalueList[0])
                       value = float(zvalueList[1])
                except:
                       self.console.clear()
                       self.console.append("Please Write  corrects parameter Dbsrange")
                       return 0    
                format = 'float'
                opObj.addParameter(name='zmin', value=zvalueList[0], format=format)
                opObj.addParameter(name='zmax', value=zvalueList[1], format=format)      

            if self.specGraphSaveSpectra.isChecked():
                name_parameter1 = 'save'
                name_parameter2 = 'figpath'
                name_parameter3 = 'figfile'
                value1 = '1'
                value2 = self.specGraphPath.text()
                value3 = self.specGraphPrefix.text()
                format1 = 'bool'
                format2 = 'str'
                opObj.addParameter(name=name_parameter1, value=value1 , format=format1)
                opObj.addParameter(name=name_parameter2, value=value2, format=format2)
                if not value3 == "":
                   try:
                       value3 = str(self.specGraphPrefix.text())
                   except:
                       self.console.clear()
                       self.console.append("Please Write prefix")
                       return 0    
                   opObj.addParameter(name='figfile', value=self.specGraphPrefix.text(), format='str')
                
             #   opObj.addParameter(name=name_parameter3, value=value3, format=format2) 
             #   opObj.addParameter(name='wr_period', value='5',format='int')
                        
            if self.specGraphftpSpectra.isChecked():
               opObj.addParameter(name='ftp', value='1', format='int')
               self.addFTPConfiguration(puObj, opObj)
               
        if self.specGraphCebCrossSpectraplot.isChecked():
            name_operation = 'Plot'
            optype = 'other'
            opObj = puObj.addOperation(name=name_operation, optype=optype)
            opObj.addParameter(name='type', value="CrossSpectraPlot", format='str') 
            opObj.addParameter(name='power_cmap', value='jet', format='str')
            opObj.addParameter(name='coherence_cmap', value='jet', format='str')
            opObj.addParameter(name='phase_cmap', value='RdBu_r', format='str') 
                   
            if self.idImagcross == 0:
                self.idImagcross = 300
            else:
                self.idImagcross = self.idImagcross + 1
            value1 = int(self.idImagcross)
            channelList = self.specGgraphChannelList.text()
            xvalue = self.specGgraphFreq.text()
            yvalue = self.specGgraphHeight.text()
            zvalue = self.specGgraphDbsrange.text() 
                           
            opObj.addParameter(name='id', value=value1, format='int')
    
            if self.specGgraphChannelList.isModified():
                opObj.addParameter(name='channelList', value=channelList, format='intlist') 

            if not xvalue == '':
               xvalueList = xvalue.split(',')
               try:
                    value = float(xvalueList[0])
                    value = float(xvalueList[1])
               except:
                    return 0 
               format = 'float'
               opObj.addParameter(name='xmin', value=xvalueList[0], format=format)
               opObj.addParameter(name='xmax', value=xvalueList[1], format=format)
               
            if not yvalue == '':
               yvalueList = yvalue.split(",")
               try:
                        value = float(yvalueList[0])
                        value = float(yvalueList[1])
               except:
                            return 0
               format = 'float'
               opObj.addParameter(name='ymin', value=yvalueList[0], format=format)
               opObj.addParameter(name='ymax', value=yvalueList[1], format=format)
                        
        
            if not zvalue == '':
                    zvalueList = zvalue.split(",")
                    try:
                        value = float(zvalueList[0])
                        value = float(zvalueList[1])
                    except:
                            return 0
                    opObj.addParameter(name='zmin', value=zvalueList[0], format='float')
                    opObj.addParameter(name='zmax', value=zvalueList[1], format='float')
 
            if self.specGraphSaveCross.isChecked():
                opObj.addParameter(name='save', value='1', format='bool')
                opObj.addParameter(name='figpath', value=self.specGraphPath.text(), format='str')
                value = self.specGraphPrefix.text()
                if not value == "":
                   try:
                       value = str(self.specGraphPrefix.text())
                   except:
                       self.console.clear()
                       self.console.append("Please Write prefix")
                       return 0    
                   opObj.addParameter(name='figfile', value=value, format='str')                
                # opObj.addParameter(name='figfile', value=self.specGraphPrefix.text(), format='str') 
            if self.specGraphftpCross.isChecked():
               opObj.addParameter(name='ftp', value='1', format='int')
               self.addFTPConfiguration(puObj, opObj)
                     
        if self.specGraphCebRTIplot.isChecked():
            name_operation = 'Plot'
            optype = 'other'
            name_parameter = 'type'
            value = 'RTIPlot'
            format = 'str'
          
            if self.idImagrti == 0:
                self.idImagrti = 400
            else:
                self.idImagrti = self.idImagrti + 1
            
            name_parameter1 = 'id'
            value1 = int(self.idImagrti)
            format1 = 'int'
            
            format = 'str'
            
            opObj = puObj.addOperation(name=name_operation, optype=optype)
            opObj.addParameter(name=name_parameter, value=value, format=format)
            opObj.addParameter(name=name_parameter1, value=value1, format=format1)

            channelList = self.specGgraphChannelList.text()
            xvalue = self.specGgraphTminTmax.text()     
            yvalue = self.specGgraphHeight.text()
            zvalue = self.specGgraphDbsrange.text()
            timerange = self.specGgraphTimeRange.text()
            
            if not channelList == '':
                opObj.addParameter(name='channelList', value=channelList, format='intlist')
            
            if not xvalue == '':
                xvalueList = xvalue.split(',')
                try:
                    value = float(xvalueList[0])
                    value = float(xvalueList[1])
                except:
                        return 0  
                format = 'float'
                opObj.addParameter(name='xmin', value=xvalueList[0], format=format)
                opObj.addParameter(name='xmax', value=xvalueList[1], format=format)
            
            if not timerange == '':
                format = 'int'
                try:
                    timerange = int(timerange)
                except:
                    return 0
                opObj.addParameter(name='timerange', value=timerange, format=format)

                
            if not yvalue == '':
                yvalueList = yvalue.split(",")
                try:
                    value = float(yvalueList[0])
                    value = float(yvalueList[1])
                except:
                        return 0
                format = 'float'
                opObj.addParameter(name='ymin', value=yvalueList[0], format=format)
                opObj.addParameter(name='ymax', value=yvalueList[1], format=format)   
                        
            if not zvalue == '':
                zvalueList = zvalue.split(",")
                try:
                    value = float(zvalueList[0])
                    value = float(zvalueList[1])
                except:
                    return 0 
                format = 'float'
                opObj.addParameter(name='zmin', value=zvalueList[0], format=format)
                opObj.addParameter(name='zmax', value=zvalueList[1], format=format)     
                
            if self.specGraphSaveRTIplot.isChecked():
               opObj.addParameter(name='save', value='1', format='bool')
               opObj.addParameter(name='figpath', value=self.specGraphPath.text(), format='str')
               value = self.specGraphPrefix.text()
               if not value == "":
                  try:
                      value = str(self.specGraphPrefix.text())
                  except:
                       self.console.clear()
                       self.console.append("Please Write prefix")
                       return 0    
                  opObj.addParameter(name='figfile', value=value, format='str')                
               
            # test_ftp
            if self.specGraphftpRTIplot.isChecked():
               opObj.addParameter(name='ftp', value='1', format='int')
               self.addFTPConfiguration(puObj, opObj)
                                 
        if self.specGraphCebCoherencmap.isChecked():
            name_operation = 'Plot'
            optype = 'other'
            name_parameter = 'type'
            value = 'CoherenceMap'
            format = 'str'
            if self.idImagcoherence == 0:
                self.idImagcoherence = 500
            else:
                self.idImagcoherence = self.idImagcoherence + 1
            
            name_parameter1 = 'id'
            value1 = int(self.idImagcoherence)
            format1 = 'int'
           
            opObj = puObj.addOperation(name=name_operation, optype=optype)
            opObj.addParameter(name=name_parameter, value=value, format=format)
            # opObj.addParameter(name='coherence_cmap', value='jet', format='str')
            # opObj.addParameter(name='phase_cmap', value='RdBu_r', format='str')     
            opObj.addParameter(name=name_parameter1, value=value1, format=format1)
       
            channelList = self.specGgraphChannelList.text()
            if not channelList == '':
                opObj.addParameter(name='channelList', value=channelList, format='intlist') 
            
            timerange = self.specGgraphTimeRange.text()
            if not timerange == '':
                try:
                    timerange = int(timerange)
                except:
                    return 0
                format = 'int'
                opObj.addParameter(name='timerange', value=timerange, format=format)

            xvalue = self.specGgraphTminTmax.text() 
            if not xvalue == '':
                xvalueList = xvalue.split(',')
                try:
                    value = float(xvalueList[0])
                    value = float(xvalueList[1])
                except:
                       return 0
                format = 'float'
                opObj.addParameter(name='xmin', value=xvalueList[0], format=format)
                opObj.addParameter(name='xmax', value=xvalueList[1], format=format)  
            
            yvalue = self.specGgraphHeight.text()
            if not yvalue == '':
                yvalueList = yvalue.split(",")
                try:
                    value = float(yvalueList[0])
                    value = float(yvalueList[1])
                except:
                       return 0
                format = 'float'
                opObj.addParameter(name='ymin', value=yvalueList[0], format=format)
                opObj.addParameter(name='ymax', value=yvalueList[1], format=format)   
              
            zvalue = self.specGgraphmagnitud.text()               
            if not zvalue == '':
                zvalueList = zvalue.split(",")
                try:
                    value = float(zvalueList[0])
                    value = float(zvalueList[1])
                except:
                       return 0
                opObj.addParameter(name='zmin', value=zvalueList[0], format='float')
                opObj.addParameter(name='zmax', value=zvalueList[1], format='float')
    
            if self.specGraphSaveCoherencemap.isChecked():
                opObj.addParameter(name='save', value='1', format='bool')
                opObj.addParameter(name='figpath', value=self.specGraphPath.text(), format='str')
                value = self.specGraphPrefix.text()
                if not value == "":
                   try:
                      value = str(self.specGraphPrefix.text())
                   except:
                       self.console.clear()
                       self.console.append("Please Write prefix")
                       return 0    
                   opObj.addParameter(name='figfile', value=value, format='str')
           
             # test_ftp
            if self.specGraphftpCoherencemap.isChecked():
               opObj.addParameter(name='ftp', value='1', format='int')
               self.addFTPConfiguration(puObj, opObj)           
           
        if self.specGraphPowerprofile.isChecked():
           name_operation = 'Plot'
           optype = 'other'
           name_parameter = 'type'
           value = 'PowerProfilePlot'
           format = 'str'

           if self.idImagpower == 0:
                self.idImagpower = 600
           else:
                self.idImagpower = self.idImagpower + 1
           value1 = int(self.idImagpower)
           opObj = puObj.addOperation(name=name_operation, optype=optype)
           opObj.addParameter(name=name_parameter, value=value, format='str') 
           opObj.addParameter(name='id', value=value1, format='int')
    
           channelList = self.specGgraphChannelList.text()
           if not channelList == '':
               opObj.addParameter(name='channelList', value=channelList, format='intlist') 
           
           xvalue = self.specGgraphDbsrange.text() 
           if not xvalue == '':
               xvalueList = xvalue.split(',')
               try:
                    value = float(xvalueList[0])
                    value = float(xvalueList[1])
               except:
                    return 0
               format = 'float'
               opObj.addParameter(name='xmin', value=xvalueList[0], format=format)
               opObj.addParameter(name='xmax', value=xvalueList[1], format=format)     
  
           yvalue = self.specGgraphHeight.text()
           if not yvalue == '':
               yvalueList = yvalue.split(",")
               try:
                    value = float(yvalueList[0])
                    value = float(yvalueList[1])
               except:
                    return 0  
               format = 'float'
               opObj.addParameter(name='ymin', value=yvalueList[0], format=format)
               opObj.addParameter(name='ymax', value=yvalueList[1], format=format)   
           
 
           if self.specGraphSavePowerprofile.isChecked():
               opObj.addParameter(name='save', value='1', format='bool')
               opObj.addParameter(name='figpath', value=self.specGraphPath.text(), format='str')
               value = self.specGraphPrefix.text()
               if not value == "":
                  try:
                      value = str(self.specGraphPrefix.text())
                  except:
                       self.console.clear()
                       self.console.append("Please Write prefix")
                       return 0    
                  opObj.addParameter(name='figfile', value=value, format='str')
                
                
           if self.specGraphftpPowerprofile.isChecked():
              opObj.addParameter(name='ftp', value='1', format='int')
              self.addFTPConfiguration(puObj, opObj)
           # rti noise
              
        if self.specGraphCebRTInoise.isChecked():
            name_operation = 'Plot'
            optype = 'other'
            name_parameter = 'type'
            value = 'Noise'
            format = 'str'
          
            if self.idImagrtinoise == 0:
                self.idImagrtinoise = 700
            else:
                self.idImagrtinoise = self.idImagrtinoise + 1
            
            name_parameter1 = 'id'
            value1 = int(self.idImagrtinoise)
            format1 = 'int'
            format = 'str'
            
            opObj = puObj.addOperation(name=name_operation, optype=optype)
            opObj.addParameter(name=name_parameter, value=value, format=format)
            opObj.addParameter(name=name_parameter1, value=value1, format=format1)

            channelList = self.specGgraphChannelList.text()
            xvalue = self.specGgraphTminTmax.text()     
            yvalue = self.specGgraphDbsrange.text()
            timerange = self.specGgraphTimeRange.text()     

            
            if not channelList == '':
                opObj.addParameter(name='channelList', value=channelList, format='intlist')
            
            if not timerange == '':
                format = 'int'
                try:
                    timerange = int(timerange)
                except:
                    return 0
                opObj.addParameter(name='timerange', value=timerange, format=format)
                
            if not xvalue == '':
                xvalueList = xvalue.split(',')
                try:
                    value = float(xvalueList[0])
                    value = float(xvalueList[1])
                except:
                        return 0  
                format = 'float'
                opObj.addParameter(name='xmin', value=xvalueList[0], format=format)
                opObj.addParameter(name='xmax', value=xvalueList[1], format=format)
            
            if not yvalue == '':
                yvalueList = yvalue.split(",")
                try:
                    value = float(yvalueList[0])
                    value = float(yvalueList[1])
                except:
                        return 0
                format = 'float'
                opObj.addParameter(name='ymin', value=yvalueList[0], format=format)
                opObj.addParameter(name='ymax', value=yvalueList[1], format=format)      
                
            if self.specGraphSaveRTInoise.isChecked():
               opObj.addParameter(name='save', value='1', format='bool')
               opObj.addParameter(name='figpath', value=self.specGraphPath.text(), format='str')
               value = self.specGraphPrefix.text()
               if not value == "":
                  try:
                      value = str(self.specGraphPrefix.text())
                  except:
                       self.console.clear()
                       self.console.append("Please Write prefix")
                       return 0    
                  opObj.addParameter(name='figfile', value=value, format='str')                
               
            # test_ftp
            if self.specGraphftpRTInoise.isChecked():
               opObj.addParameter(name='ftp', value='1', format='int')
               self.addFTPConfiguration(puObj, opObj)      
              
               

#      if something happend 
        parms_ok, output_path, blocksperfile, profilesperblock = self.checkInputsPUSave(datatype='Spectra')
        name_operation = 'SpectraWriter'
        optype = 'other'
        name_parameter1 = 'path'
        name_parameter2 = 'blocksPerFile'
        name_parameter3 = 'profilesPerBlock'
        value1 = output_path
        value2 = blocksperfile
        value3 = profilesperblock
        format = "int"
        if parms_ok:
            opObj = puObj.addOperation(name=name_operation, optype=optype)
            opObj.addParameter(name=name_parameter1, value=value1)
            opObj.addParameter(name=name_parameter2, value=value2, format=format)
            opObj.addParameter(name=name_parameter3, value=value3, format=format)

        self.showPUSpectraProperties(puObj)
            
        self.console.clear()
        self.console.append("If you want to save your project")
        self.console.append("click on your project name in the Tree Project Explorer")
            
    """
    Spectra  Graph
    """
    @pyqtSignature("int")
    def on_specGraphCebSpectraplot_stateChanged(self, p0):
        
        if  p0 == 2:
            self.specGgraphChannelList.setEnabled(True)
            self.specGgraphFreq.setEnabled(True)
            self.specGgraphHeight.setEnabled(True)
            self.specGgraphDbsrange.setEnabled(True)
        if  p0 == 0:
            self.specGgraphFreq.setEnabled(False)
            self.specGgraphHeight.setEnabled(False)
            self.specGgraphDbsrange.setEnabled(False)  
            
            
    @pyqtSignature("int")
    def on_specGraphCebCrossSpectraplot_stateChanged(self, p0):
        
        if  p0 == 2:
            self.specGgraphFreq.setEnabled(True)
            self.specGgraphHeight.setEnabled(True)
            self.specGgraphDbsrange.setEnabled(True)
        if  p0 == 0:
            self.specGgraphFreq.setEnabled(False)
            self.specGgraphHeight.setEnabled(False)
            self.specGgraphDbsrange.setEnabled(False)  
            
    @pyqtSignature("int")
    def on_specGraphCebRTIplot_stateChanged(self, p0):
        
        if  p0 == 2:
            self.specGgraphChannelList.setEnabled(True)
            self.specGgraphTminTmax.setEnabled(True)
            self.specGgraphHeight.setEnabled(True)
            self.specGgraphDbsrange.setEnabled(True)
            self.specGgraphTimeRange.setEnabled(True)

        if  p0 == 0:
            self.specGgraphTminTmax.setEnabled(False)
            self.specGgraphHeight.setEnabled(False)
            self.specGgraphDbsrange.setEnabled(False)
            self.specGgraphTimeRange.setEnabled(False)

    
    @pyqtSignature("int")
    def on_specGraphCebRTInoise_stateChanged(self, p0):
        if  p0 == 2:
            self.specGgraphChannelList.setEnabled(True)
            self.specGgraphTminTmax.setEnabled(True)
            self.specGgraphDbsrange.setEnabled(True)
            self.specGgraphTimeRange.setEnabled(True)

        if  p0 == 0:
            self.specGgraphTminTmax.setEnabled(False)
            self.specGgraphDbsrange.setEnabled(False)
            self.specGgraphTimeRange.setEnabled(False)

            
            
             
    @pyqtSignature("int")
    def on_specGraphCebCoherencmap_stateChanged(self, p0):
        
        if  p0 == 2:
            self.specGgraphTminTmax.setEnabled(True)
            self.specGgraphHeight.setEnabled(True)
            self.specGgraphmagnitud.setEnabled(True)
            self.specGgraphTimeRange.setEnabled(True)
            
        if  p0 == 0:
            self.specGgraphTminTmax.setEnabled(False)
            self.specGgraphHeight.setEnabled(False)
            self.specGgraphmagnitud.setEnabled(False)
            self.specGgraphTimeRange.setEnabled(False)



            
    @pyqtSignature("int")
    def on_specGraphPowerprofile_stateChanged(self, p0):
        
        if  p0 == 2:
    
            self.specGgraphHeight.setEnabled(True)
            self.specGgraphDbsrange.setEnabled(True)
        if  p0 == 0:
            self.specGgraphHeight.setEnabled(False)
            self.specGgraphDbsrange.setEnabled(False)        
    
    @pyqtSignature("int")
    def on_specGraphPhase_stateChanged(self, p0):
        
        if  p0 == 2:
            self.specGgraphTminTmax.setEnabled(True)
            self.specGgraphPhaserange.setEnabled(True)

        if  p0 == 0:
            self.specGgraphTminTmax.setEnabled(False)
            self.specGgraphPhaserange.setEnabled(False)
               
    @pyqtSignature("int")
    def on_specGraphSaveSpectra_stateChanged(self, p0):
        """
        """
        if  p0 == 2:
            self.specGraphPath.setEnabled(True)
            self.specGraphPrefix.setEnabled(True)
            self.specGraphToolPath.setEnabled(True)
        if  p0 == 0:
            self.specGraphPath.setEnabled(False)
            self.specGraphPrefix.setEnabled(False)
            self.specGraphToolPath.setEnabled(False)   
            
            
    @pyqtSignature("int")
    def on_specGraphSaveCross_stateChanged(self, p0):       
        if  p0 == 2:
            self.specGraphPath.setEnabled(True)
            self.specGraphPrefix.setEnabled(True)
            self.specGraphToolPath.setEnabled(True)
        
    @pyqtSignature("int")
    def on_specGraphSaveRTIplot_stateChanged(self, p0):       
        if  p0 == 2:
            self.specGraphPath.setEnabled(True)
            self.specGraphPrefix.setEnabled(True)
            self.specGraphToolPath.setEnabled(True)
            
    @pyqtSignature("int")
    def on_specGraphSaveRTInoise_stateChanged(self, p0):       
        if  p0 == 2:
            self.specGraphPath.setEnabled(True)
            self.specGraphPrefix.setEnabled(True)
            self.specGraphToolPath.setEnabled(True)
            
    @pyqtSignature("int")
    def on_specGraphSaveCoherencemap_stateChanged(self, p0):       
        if  p0 == 2:
            self.specGraphPath.setEnabled(True)
            self.specGraphPrefix.setEnabled(True)
            self.specGraphToolPath.setEnabled(True)
            
            
    @pyqtSignature("int")
    def on_specGraphSavePowerprofile_stateChanged(self, p0):       
        if  p0 == 2:
            self.specGraphPath.setEnabled(True)
            self.specGraphPrefix.setEnabled(True)
            self.specGraphToolPath.setEnabled(True)
    
    
    #-------ftp-----#        
    @pyqtSignature("int")
    def on_specGraphftpSpectra_stateChanged(self, p0):
        """
        """
        if  p0 == 2:
            self.specGgraphftpratio.setEnabled(True)

        if  p0 == 0:
            self.specGgraphftpratio.setEnabled(False)
            
            
    @pyqtSignature("int")
    def on_specGraphftpCross_stateChanged(self, p0):       
        if  p0 == 2:
            self.specGgraphftpratio.setEnabled(True)
        
    @pyqtSignature("int")
    def on_specGraphftpRTIplot_stateChanged(self, p0):       
        if  p0 == 2:
            self.specGgraphftpratio.setEnabled(True)
            
    @pyqtSignature("int")
    def on_specGraphftpRTInoise_stateChanged(self, p0):       
        if  p0 == 2:
            self.specGgraphftpratio.setEnabled(True)
            
    @pyqtSignature("int")
    def on_specGraphftpCoherencemap_stateChanged(self, p0):       
        if  p0 == 2:
            self.specGgraphftpratio.setEnabled(True)
            
    @pyqtSignature("int")
    def on_specGraphftpPowerprofile_stateChanged(self, p0):       
        if  p0 == 2:
            self.specGgraphftpratio.setEnabled(True)
            
    #-------------------#
             

               
    @pyqtSignature("")
    def on_specGraphToolPath_clicked(self):        
        """
        """
        self.savePath = str(QtGui.QFileDialog.getExistingDirectory(self, 'Open Directory', './', QtGui.QFileDialog.ShowDirsOnly))
        self.specGraphPath.setText(self.savePath)
        if not os.path.exists(self.savePath):
            self.console.clear()
            self.console.append("Write a correct a path")
            return 
        
    @pyqtSignature("")
    def on_specHeisGraphToolPath_clicked(self):        
        """
        """
        self.savePath = str(QtGui.QFileDialog.getExistingDirectory(self, 'Open Directory', './', QtGui.QFileDialog.ShowDirsOnly))
        self.specHeisGraphPath.setText(self.savePath)
        if not os.path.exists(self.savePath):
            self.console.clear()
            self.console.append("Write a correct a path")
            return 

    @pyqtSignature("")
    def on_specGraphClear_clicked(self):
        self.clearspecGraph()
        
    @pyqtSignature("int")
    def on_specHeisOpCebIncoherent_stateChanged(self, p0):
        """
        Habilita la opcion de a�adir el par�metro integraciones incoherentes a la Unidad de Procesamiento .
        """
        if  p0 == 2:
            self.specHeisOpIncoherent.setEnabled(True)
            self.specHeisOpCobIncInt.setEnabled(True)
        if  p0 == 0:
            self.specHeisOpIncoherent.setEnabled(False)     
            self.specHeisOpCobIncInt.setEnabled(False)
        
    @pyqtSignature("")
    def on_specHeisOpOk_clicked(self):
        """
        AÑADE OPERACION SPECTRAHEIS
        """
        puObj = self.getSelectedPUObj()
        puObj.removeOperations()
        
        if self.specHeisOpCebIncoherent.isChecked():
            value = self.specHeisOpIncoherent.text()   
            name_operation = 'IncohInt4SpectraHeis'
            optype = 'other'
            if self.specOpCobIncInt.currentIndex() == 0:
                name_parameter = 'timeInterval'
                format = 'float'
            opObj = puObj.addOperation(name=name_operation, optype=optype)
            opObj.addParameter(name=name_parameter, value=value, format=format)
            
        # ---- Spectra Plot-----
        if self.specHeisGraphCebSpectraplot.isChecked():   
            name_operation = 'Plot'
            optype = 'other'
            name_parameter = 'type'
            value = 'SpectraHeisScope'
            format = 'str'
            if self.idImagspectraHeis == 0:
                self.idImagspectraHeis = 800
            else:
                self.idImagspectraHeis = self.idImagspectraHeis + 1
            name_parameter1 = 'id'
            value1 = int(self.idImagspectraHeis)
            format1 = 'int'
            
            format = 'str'
            
            channelList = self.specHeisGgraphChannelList.text()
            xvalue = self.specHeisGgraphXminXmax.text() 
            yvalue = self.specHeisGgraphYminYmax.text()            
            opObj = puObj.addOperation(name=name_operation, optype=optype)
            opObj.addParameter(name=name_parameter, value=value, format=format)
            opObj.addParameter(name=name_parameter1, value=value1, format=format1)      
            
            if not channelList == '':
               name_parameter = 'channelList'
               format = 'intlist'
               opObj.addParameter(name=name_parameter, value=channelList, format=format) 
           
            if not xvalue == '':
               xvalueList = xvalue.split(',')
               try:
                   value1 = float(xvalueList[0])
                   value2 = float(xvalueList[1])
               except:
                       self.console.clear()
                       self.console.append("Please Write  corrects parameter xmin-xmax")
                       return 0
               name1 = 'xmin'
               name2 = 'xmax'
               format = 'float'
               opObj.addParameter(name=name1, value=value1, format=format)
               opObj.addParameter(name=name2, value=value2, format=format)
            #------specHeisGgraphYmin-Ymax---
            if not yvalue == '':
                  yvalueList = yvalue.split(",")
                  try:
                       value1 = float(yvalueList[0])
                       value2 = float(yvalueList[1])
                  except:
                      self.console.clear()
                      self.console.append("Please Write  corrects parameter Ymix-Ymax")
                      return 0 
                  name1 = 'ymin'
                  name2 = 'ymax'
                  format = 'float'
                  opObj.addParameter(name=name1, value=value1, format=format)
                  opObj.addParameter(name=name2, value=value2, format=format) 
            
            if self.specHeisGraphSaveSpectra.isChecked():
                name_parameter1 = 'save'
                name_parameter2 = 'figpath'
                name_parameter3 = 'figfile'
                value1 = '1'
                value2 = self.specHeisGraphPath.text()
                value3 = self.specHeisGraphPrefix.text()
                format1 = 'bool'
                format2 = 'str'
                opObj.addParameter(name=name_parameter1, value=value1 , format=format1)
                opObj.addParameter(name=name_parameter2, value=value2, format=format2)
                if not value3 == "":
                   try:
                       value3 = str(self.specHeisGraphPrefix.text())
                   except:
                       self.console.clear()
                       self.console.append("Please Write prefix")
                       return 0    
                   opObj.addParameter(name='figfile', value=self.specHeisGraphPrefix.text(), format='str')
                
             #   opObj.addParameter(name=name_parameter3, value=value3, format=format2) 
             #   opObj.addParameter(name='wr_period', value='5',format='int')
                        
            if self.specHeisGraphftpSpectra.isChecked():
               opObj.addParameter(name='ftp', value='1', format='int')
               self.addFTPConfiguration(puObj, opObj)
               
        if self.specHeisGraphCebRTIplot.isChecked():
            name_operation = 'Plot'
            optype = 'other'
            name_parameter = 'type'
            value = 'RTIfromSpectraHeis'
            format = 'str'
          
            if self.idImagrtiHeis == 0:
                self.idImagrtiHeis = 900
            else:
                self.idImagrtiHeis = self.idImagrtiHeis + 1
            
            name_parameter1 = 'id'
            value1 = int(self.idImagrtiHeis)
            format1 = 'int'
            
            format = 'str'
            
            opObj = puObj.addOperation(name=name_operation, optype=optype)
            opObj.addParameter(name=name_parameter, value=value, format=format)
            opObj.addParameter(name=name_parameter1, value=value1, format=format1)

            channelList = self.specHeisGgraphChannelList.text()
            xvalue = self.specHeisGgraphTminTmax.text()     
            yvalue = self.specHeisGgraphYminYmax.text()
            timerange = self.specHeisGgraphTimeRange.text()
            
            if not channelList == '':
                opObj.addParameter(name='channelList', value=channelList, format='intlist')
            
            if not xvalue == '':
                xvalueList = xvalue.split(',')
                try:
                    value = float(xvalueList[0])
                    value = float(xvalueList[1])
                except:
                        return 0  
                format = 'float'
                opObj.addParameter(name='xmin', value=xvalueList[0], format=format)
                opObj.addParameter(name='xmax', value=xvalueList[1], format=format)
            
            if not timerange == '':
                format = 'int'
                try:
                    timerange = int(timerange)
                except:
                    return 0
                opObj.addParameter(name='timerange', value=timerange, format=format)

                
            if not yvalue == '':
                yvalueList = yvalue.split(",")
                try:
                    value = float(yvalueList[0])
                    value = float(yvalueList[1])
                except:
                        return 0
                format = 'float'
                opObj.addParameter(name='ymin', value=yvalueList[0], format=format)
                opObj.addParameter(name='ymax', value=yvalueList[1], format=format)   
                        
            if self.specHeisGraphSaveRTIplot.isChecked():
               opObj.addParameter(name='save', value='1', format='bool')
               opObj.addParameter(name='figpath', value=self.specHeisGraphPath.text(), format='str')
               value = self.specHeisGraphPrefix.text()
               if not value == "":
                  try:
                      value = str(self.specHeisGraphPrefix.text())
                  except:
                       self.console.clear()
                       self.console.append("Please Write prefix")
                       return 0    
                  opObj.addParameter(name='figfile', value=value, format='str')                
               
            # test_ftp
            if self.specHeisGraphftpRTIplot.isChecked():
               opObj.addParameter(name='ftp', value='1', format='int')
               self.addFTPConfiguration(puObj, opObj)
               
        # if something happened
        parms_ok, output_path, blocksperfile, metada = self.checkInputsPUSave(datatype='SpectraHeis')
        name_operation = 'FitsWriter'
        optype = 'other'
        name_parameter1 = 'path'
        name_parameter2 = 'dataBlocksPerFile'
        name_parameter3 = 'metadatafile'
        value1 = output_path
        value2 = blocksperfile
        value3 = metada
        format2 = "int"
        format3 = "str"
        if parms_ok:
            opObj = puObj.addOperation(name=name_operation, optype=optype)
            opObj.addParameter(name=name_parameter1, value=value1)
            opObj.addParameter(name=name_parameter2, value=value2, format=format2)
            opObj.addParameter(name=name_parameter3, value=value3, format=format3)

        self.showPUSpectraHeisProperties(puObj)
            
        self.console.clear()
        self.console.append("If you want to save your project")
        self.console.append("click on your project name in the Tree Project Explorer")
            
        

    @pyqtSignature("int")
    def on_specHeisGraphCebSpectraplot_stateChanged(self, p0):
        
        if  p0 == 2:
            self.specHeisGgraphChannelList.setEnabled(True)
            self.specHeisGgraphXminXmax.setEnabled(True)
            self.specHeisGgraphYminYmax.setEnabled(True)
        if  p0 == 0:
            self.specHeisGgraphXminXmax.setEnabled(False)
            self.specHeisGgraphYminYmax.setEnabled(False) 

    @pyqtSignature("int")
    def on_specHeisGraphCebRTIplot_stateChanged(self, p0):
        
        if  p0 == 2:
            self.specHeisGgraphChannelList.setEnabled(True)
            self.specHeisGgraphTminTmax.setEnabled(True)
            self.specHeisGgraphYminYmax.setEnabled(True)
            self.specHeisGgraphTimeRange.setEnabled(True)

        if  p0 == 0:
            self.specHeisGgraphTminTmax.setEnabled(False)
            self.specHeisGgraphYminYmax.setEnabled(False)
            self.specHeisGgraphTimeRange.setEnabled(False)
            
    @pyqtSignature("int")
    def on_specHeisGraphSaveSpectra_stateChanged(self, p0):
        """
        """
        if  p0 == 2:
            self.specHeisGraphPath.setEnabled(True)
            self.specHeisGraphPrefix.setEnabled(True)
            self.specHeisGraphToolPath.setEnabled(True)
        if  p0 == 0:
            self.specHeisGraphPath.setEnabled(False)
            self.specHeisGraphPrefix.setEnabled(False)
            self.specHeisGraphToolPath.setEnabled(False)  
    
    @pyqtSignature("int")
    def on_specHeisGraphSaveRTIplot_stateChanged(self, p0):       
        if  p0 == 2:
            self.specHeisGraphPath.setEnabled(True)
            self.specHeisGraphPrefix.setEnabled(True)
            self.specHeisGraphToolPath.setEnabled(True)
            
   #-------ftp-----#        
    @pyqtSignature("int")
    def on_specHeisGraphftpSpectra_stateChanged(self, p0):
        """
        """
        if  p0 == 2:
            self.specHeisGgraphftpratio.setEnabled(True)

        if  p0 == 0:
            self.specHeisGgraphftpratio.setEnabled(False)
            
    @pyqtSignature("int")
    def on_specHeisGraphftpRTIplot_stateChanged(self, p0):       
        if  p0 == 2:
            self.specHeisGgraphftpratio.setEnabled(True)
            
    @pyqtSignature("")
    def on_specHeisGraphClear_clicked(self):
        pass
            
    def on_click(self, index):
        
        self.selectedItemTree = self.projectExplorerModel.itemFromIndex(index)
        if self.getSelectedProjectObj():
            projectObjView = self.getSelectedProjectObj()
            project_name, description = projectObjView.name, projectObjView.description
            id = int(projectObjView.id)
            idReadUnit = projectObjView.getReadUnitId()
            readUnitObj = projectObjView.getProcUnitObj(idReadUnit)
            datatype, data_path, startDate, endDate, startTime, endTime , online , delay, walk , set = self.showProjectProperties(projectObjView)        
            # show ProjectView           
            self.refreshProjectWindow(project_name, description, datatype, data_path, startDate, endDate, startTime, endTime, online, delay, set)
            if datatype == 'Voltage':
                ext = '.r'
            elif datatype == 'Spectra':
                ext = '.pdata'
            elif datatype == 'Fits':
                ext = '.fits'
            if online == 0:
                self.proComStartDate.clear()
                self.proComEndDate.clear()
                self.loadDays(data_path, ext, walk)
            self.tabProject.setEnabled(True)
            self.tabVoltage.setEnabled(False)
            self.tabSpectra.setEnabled(False)
            self.tabCorrelation.setEnabled(False)
            self.tabSpectraHeis.setEnabled(False)
            self.tabWidgetProject.setCurrentWidget(self.tabProject)            
                                    
        if  self.selectedItemTree.text() == 'Voltage':
            datatype = 'Voltage'
            puObj = self.getSelectedPUObj()  
            self.showtabPUCreated(datatype=datatype)
            if len(puObj.getOperationObjList()) == 1:
                self.setInputsPU_View(datatype)
            else:
                self.refreshPUWindow(datatype=datatype, puObj=puObj)
            self.showPUVoltageProperties(puObj)
                
        if self.selectedItemTree.text() == 'Spectra':
            
            datatype = 'Spectra'
            puObj = self.getSelectedPUObj() 
            self.showtabPUCreated(datatype=datatype)
            if readUnitObj.datatype == 'Spectra':
                self.specOpnFFTpoints.setEnabled(False)
                self.specOpProfiles.setEnabled(False)
                self.specOpippFactor.setEnabled(False)
                
            else:
                self.specOpnFFTpoints.setEnabled(True)
                self.specOpProfiles.setEnabled(True)
                self.specOpippFactor.setEnabled(True)
                
            if len(puObj.getOperationObjList()) == 1:
                self.setInputsPU_View(datatype)
                
                opObj = puObj.getOperationObj(name="init")   
                if opObj == None:
                    self.specOpnFFTpoints.clear()
                    self.specOpProfiles.clear()
                    self.specOpippFactor.clear()
                else:
                    parmObj = opObj.getParameterObj(parameterName='nFFTPoints')
                    if parmObj == None:
                        self.specOpnFFTpoints.clear()
                    else:
                        value = opObj.getParameterValue(parameterName='nFFTPoints')  
                        self.specOpnFFTpoints.setText(str(value))
                        
                    parmObj = opObj.getParameterObj(parameterName='nProfiles')
                    if parmObj == None:
                        self.specOpProfiles.clear()
                    else:
                        value = opObj.getParameterValue(parameterName='nProfiles')  
                        self.specOpProfiles.setText(str(value))
                        
                    parmObj = opObj.getParameterObj(parameterName="ippFactor")
                    if parmObj == None:
                        self.specOpippFactor.clear()
                    else:
                        value = opObj.getParameterValue(parameterName='ippFactor')
                        self.specOpippFactor.setText(str(value))
                
                opObj = puObj.getOperationObj(name="init")  
                if opObj == None:
                    self.specOppairsList.clear()
                    self.specOpCebCrossSpectra.setCheckState(0)
                else:                  
                    parmObj = opObj.getParameterObj(parameterName='pairsList')  
                    if parmObj == None:
                        self.specOppairsList.clear()
                        self.specOpCebCrossSpectra.setCheckState(0)
                    else:
                        value = opObj.getParameterValue(parameterName='pairsList')  
                        value = str(value)[1:-1]
                        self.specOppairsList.setText(str(value))
                        self.specOppairsList.setEnabled(True)
                        self.specOpCebCrossSpectra.setCheckState(QtCore.Qt.Checked)
        
            else:
                self.refreshPUWindow(datatype=datatype, puObj=puObj)   
            self.showPUSpectraProperties(puObj)                         

        if self.selectedItemTree.text() == 'Correlation':
            self.tabCorrelation.setEnabled(True) 
            self.tabVoltage.setEnabled(False)
            self.tabSpectra.setEnabled(False)
            self.tabWidgetProject.setCurrentWidget(self.tabCorrelation) 
        
        if self.selectedItemTree.text() == 'SpectraHeis':
            datatype = 'SpectraHeis'
            puObj = self.getSelectedPUObj() 
            self.showtabPUCreated(datatype=datatype)
            if len(puObj.getOperationObjList()) == 1:
                self.setInputsPU_View(datatype)
            else:
                self.refreshPUWindow(datatype=datatype, puObj=puObj)
            self.showPUSpectraHeisProperties(puObj)
            
                  
    def on_right_click(self, pos):
        
        self.menu = QtGui.QMenu()
        quitAction0 = self.menu.addAction("NewProject")
        quitAction1 = self.menu.addAction("NewProcessingUnit")
        quitAction2 = self.menu.addAction("Delete")
        quitAction3 = self.menu.addAction("Exit")
        
        if len(self.__itemTreeDict) == 0:
            quitAction2.setEnabled(False)
        else:
            quitAction2.setEnabled(True)
        
        action = self.menu.exec_(self.mapToGlobal(pos))
        
        if action == quitAction0:
           self. setInputsProject_View()
           self.create = True
           
        if action == quitAction1:
            if len(self.__projectObjDict) == 0:
                outputstr = "First Create a Project then add Processing Unit"
                self.console.clear()
                self.console.append(outputstr)
                return 0
            else:       
               self.addPUWindow()   
               self.console.clear()
               self.console.append("Please, Choose the type of Processing Unit")
               self.console.append("If your Datatype is rawdata, you will start with processing unit Type Voltage")
               self.console.append("If your Datatype is pdata, you will choose between processing unit Type Spectra or Correlation")
               self.console.append("If your Datatype is fits, you will start with processing unit Type SpectraHeis")

        if action == quitAction2:
            index = self.selectedItemTree
            try:
                index.parent()
            except:
                self.console.append('First left click on Project or Processing Unit')
                return 0
            # print index.parent(),index
            if index.parent() == None:
               self.projectExplorerModel.removeRow(index.row())
            else:
                index.parent().removeRow(index.row())
            self.deleteProjectorPU()  
            self.console.clear()                
            # for i in self.projectExplorerTree.selectionModel().selection().indexes():
            #     print i.row()

        if action == quitAction3:
            return
    
    def refreshProjectWindow(self, project_name, description, datatype, data_path, startDate, endDate, startTime, endTime, online, delay, set):
        
        self.proName.setText(str(project_name))
        
        if datatype == 'Voltage':
            ext = '.r'
            value = 0
        elif datatype == 'Spectra':
            ext = '.pdata'
            value = 1
        elif datatype == 'Fits':
            ext = 'fits'
            value = 2
        self.proDataType.setText(ext)
        self.proDataPath.setText(str(data_path))
        self.proComDataType.setCurrentIndex(value)
        self.proComReadMode.setCurrentIndex(int(online))
        self.proDelay.setText(str(delay))
        self.proSet.setText(str(set))
        self.proComStartDate.clear()
        self.proComEndDate.clear()
        self.proComStartDate.addItem(str(startDate))
        self.proComEndDate.addItem(str(endDate))
        starTime = str(startTime)
        starlist = starTime.split(":")
        endTime = str(endTime)
        endlist = endTime.split(":")
        self.time.setHMS(int(starlist[0]), int(starlist[1]), int(starlist[2])) 
        self.proStartTime.setTime(self.time)
        self.time.setHMS(int(endlist[0]), int(endlist[1]), int(endlist[2])) 
        self.proEndTime.setTime(self.time)
        self.proDescription.clear()
        self.proDescription.append(description)
             
    def refreshPUWindow(self, datatype, puObj):
        
        if datatype == 'Voltage':
            opObj = puObj.getOperationObj(name='setRadarFrequency')
            if opObj == None:
                self.volOpRadarfrequency.clear()
                self.volOpCebRadarfrequency.setCheckState(0)
            else:
                value = opObj.getParameterValue(parameterName='frequency')
                value = str(value)
                self.volOpRadarfrequency.setText(value)  
                self.volOpRadarfrequency.setEnabled(True)
                self.volOpCebRadarfrequency.setCheckState(QtCore.Qt.Checked)
            
            
            opObj = puObj.getOperationObj(name="selectChannels")
            if opObj == None:
                self.volOpChannel.clear()
                self.volOpCebChannels.setCheckState(0)
            
            else:
                value = opObj.getParameterValue(parameterName='channelList')             
                value = str(value)[1:-1]
                self.volOpChannel.setText(value)
                self.volOpChannel.setEnabled(True)
                self.volOpCebChannels.setCheckState(QtCore.Qt.Checked)

                                
            opObj = puObj.getOperationObj(name="selectHeights")
            if opObj == None:
                self.volOpHeights.clear()
                self.volOpCebHeights.setCheckState(0)
            else:
               value1 = int(opObj.getParameterValue(parameterName='minHei'))             
               value1 = str(value1)
               value2 = int(opObj.getParameterValue(parameterName='maxHei'))             
               value2 = str(value2)
               value = value1 + "," + value2
               self.volOpHeights.setText(value)
               self.volOpHeights.setEnabled(True)
               self.volOpCebHeights.setCheckState(QtCore.Qt.Checked)
            
            opObj = puObj.getOperationObj(name="filterByHeights")           
            if opObj == None:
                self.volOpFilter.clear()
                self.volOpCebFilter.setCheckState(0)
            else:
                value = opObj.getParameterValue(parameterName='window')             
                value = str(value)
                self.volOpFilter.setText(value)
                self.volOpFilter.setEnabled(True)
                self.volOpCebFilter.setCheckState(QtCore.Qt.Checked)

            opObj = puObj.getOperationObj(name="ProfileSelector") 
            if opObj == None:  
                self.volOpProfile.clear()
                self.volOpCebProfile.setCheckState(0)       
            else:
               for parmObj in opObj.getParameterObjList():
                   if parmObj.name == "profileRangeList":
                       value = opObj.getParameterValue(parameterName='profileRangeList')             
                       value = str(value)[1:-1]
                       self.volOpProfile.setText(value)  
                       self.volOpProfile.setEnabled(True)                                            
                       self.volOpCebProfile.setCheckState(QtCore.Qt.Checked)
                       self.volOpComProfile.setCurrentIndex(1)
                   if parmObj.name == "profileList":
                       value = opObj.getParameterValue(parameterName='profileList')             
                       value = str(value)[1:-1]
                       self.volOpProfile.setText(value)  
                       self.volOpProfile.setEnabled(True)                                            
                       self.volOpCebProfile.setCheckState(QtCore.Qt.Checked)
                       self.volOpComProfile.setCurrentIndex(0)
                        
                       
            opObj = puObj.getOperationObj(name="Decoder")
            if opObj == None:
                self.volOpCebDecodification.setCheckState(0)
            else:
                try:                              
                    valueCode = opObj.getParameterValue(parameterName='nCode')
                    status = "on"
                except:
                    status = "off"
                if not status == "off":
                    if int(valueCode) == 1:
                        valueBaud = opObj.getParameterValue(parameterName='nBaud')
                        if int(valueBaud) == 3:
                           self.volOpComCode.setCurrentIndex(0)
                        if int(valueBaud) == 4:
                            self.volOpComCode.setCurrentIndex(1)
                        if int(valueBaud) == 5:
                            self.volOpComCode.setCurrentIndex(2)
                        if int(valueBaud) == 7:
                            self.volOpComCode.setCurrentIndex(3)
                        if int(valueBaud) == 11:
                            self.volOpComCode.setCurrentIndex(4)
                        if int(valueBaud) == 13:
                            self.volOpComCode.setCurrentIndex(5)
                    else:
                        valueBaud = opObj.getParameterValue(parameterName='nBaud')
                        if int(valueBaud) == 3:
                           self.volOpComCode.setCurrentIndex(6)
                        if int(valueBaud) == 4:
                            self.volOpComCode.setCurrentIndex(7)
                        if int(valueBaud) == 5:
                            self.volOpComCode.setCurrentIndex(8)
                        if int(valueBaud) == 7:
                            self.volOpComCode.setCurrentIndex(9)
                        if int(valueBaud) == 11:
                            self.volOpComCode.setCurrentIndex(10)
                        if int(valueBaud) == 13:
                            self.volOpComCode.setCurrentIndex(11)               
                    
                    for parmObj in opObj.getParameterObjList():
                        if parmObj.name == "nBaud":
                           value = opObj.getParameterValue(parameterName='nBaud') 
                        if parmObj.name == "mode":
                           value = opObj.getParameterValue(parameterName='mode')             
                           self.volOpComMode.setCurrentIndex(value)
                else:
                    self.volOpComCode.setCurrentIndex(12)   
                self.volOpCebDecodification.setCheckState(QtCore.Qt.Checked)
            
            opObj = puObj.getOperationObj(name="CohInt")   
            if opObj == None:
                self.volOpCohInt.clear()
                self.volOpCebCohInt.setCheckState(0)
            else:
                value = opObj.getParameterValue(parameterName='n')
                self.volOpCohInt.setText(str(value))
                self.volOpCohInt.setEnabled(True)
                self.volOpCebCohInt.setCheckState(QtCore.Qt.Checked)
            
            opObj = puObj.getOperationObj(name='Plot')
            if opObj == None:
                self.volGraphCebshow.setCheckState(0)
            else:
                self.volGraphCebshow.setCheckState(QtCore.Qt.Checked)
                value = opObj.getParameterObj(parameterName='channelList')
                if value == None:
                    self.volGraphChannelList.clear()
                else:
                    value = opObj.getParameterValue(parameterName='channelList')             
                    value = str(value)[1:-1]
                    self.volGraphChannelList.setText(value)  
                    self.volOpProfile.setEnabled(True) 
                    
                for parmObj in opObj.getParameterObjList():
                    if parmObj.name == "xmin":
                        value1 = opObj.getParameterValue(parameterName='xmin') 
                        value1 = str(value1)
                        value2 = opObj.getParameterValue(parameterName='xmax')            
                        value2 = str(value2)
                        value = value1 + "," + value2
                        self.volGraphfreqrange.setText(value)
                    else:
                        self.volGraphfreqrange.clear()
                for parmObj in opObj.getParameterObjList():
                    if parmObj.name == "ymin":
                        value1 = opObj.getParameterValue(parameterName='ymin')
                        value1 = str(value1) 
                        value2 = opObj.getParameterValue(parameterName='ymax') 
                        value2 = str(value2)           
                        value = value1 + "," + value2
                        value2 = str(value2)
                        self.volGraphHeightrange.setText(value)
                    else:
                        self.volGraphHeightrange.clear()
                        
                        
                for parmObj in opObj.getParameterObjList():
                    if parmObj.name == "save":
                        self.volGraphCebSave.setCheckState(QtCore.Qt.Checked)
                    else:
                         self.volGraphCebSave.setCheckState(QtCore.Qt.Unchecked)
            
            # outputVoltageWrite
            opObj = puObj.getOperationObj(name='VoltageWriter')
            if opObj == None:
                self.volOutputPath.clear()
                self.volOutputblocksperfile.clear()
                self.volOutputprofilesperblock.clear()
            else:
                value = opObj.getParameterObj(parameterName='path')
                if value == None:
                    self.volOutputPath.clear()
                else:
                    value = opObj.getParameterValue(parameterName='path')
                    path = str(value)
                    self.volOutputPath.setText(path) 
                value = opObj.getParameterObj(parameterName='blocksPerFile')
                if value == None:
                   self.volOutputblocksperfile.clear()
                else:
                    value = opObj.getParameterValue(parameterName='blocksPerFile')
                    blocksperfile = str(value)
                    self.volOutputblocksperfile.setText(blocksperfile)
                value = opObj.getParameterObj(parameterName='profilesPerBlock')
                if value == None:
                    self.volOutputprofilesperblock.clear()
                else:
                    value = opObj.getParameterValue(parameterName='profilesPerBlock')
                    profilesPerBlock = str(value)
                    self.volOutputprofilesperblock.setText(profilesPerBlock)

        if datatype == 'Spectra':
            
            opObj = puObj.getOperationObj(name='setRadarFrequency')
            if opObj == None:
                self.specOpRadarfrequency.clear()
                self.specOpCebRadarfrequency.setCheckState(0)
            else:
                value = opObj.getParameterValue(parameterName='frequency')
                value = str(value)
                self.specOpRadarfrequency.setText(value)  
                self.specOpRadarfrequency.setEnabled(True)
                self.specOpCebRadarfrequency.setCheckState(QtCore.Qt.Checked)
            
            opObj = puObj.getOperationObj(name="init")   
            if opObj == None:
                self.specOpnFFTpoints.clear()
                self.specOpProfiles.clear()   
                self.specOpippFactor.clear()             
            else:
                parmObj = opObj.getParameterObj(parameterName='nFFTPoints')
                if parmObj == None:
                    self.specOpnFFTpoints.clear()
                else:
                    self.specOpnFFTpoints.setEnabled(True)
                    value = opObj.getParameterValue(parameterName='nFFTPoints')  
                    self.specOpnFFTpoints.setText(str(value))
                    
                parmObj = opObj.getParameterObj(parameterName='nProfiles')
                if parmObj == None:
                    self.specOpProfiles.clear()
                else:
                    self.specOpProfiles.setEnabled(True)
                    value = opObj.getParameterValue(parameterName='nProfiles')  
                    self.specOpProfiles.setText(str(value))
                    
                parmObj = opObj.getParameterObj(parameterName='ippFactor')
                if parmObj == None:
                    self.specOpippFactor.clear()
                else:
                    self.specOpippFactor.setEnabled(True)
                    value = opObj.getParameterValue(parameterName='ippFactor')
                    self.specOpippFactor.setText(str(value))
                                
            opObj = puObj.getOperationObj(name="init")  
            if opObj == None:
                self.specOppairsList.clear()
                self.specOpCebCrossSpectra.setCheckState(0)
            else:                  
                parmObj = opObj.getParameterObj(parameterName='pairsList')  
                if parmObj == None:
                    self.specOppairsList.clear()
                    self.specOpCebCrossSpectra.setCheckState(0)
                else:
                    value = opObj.getParameterValue(parameterName='pairsList')  
                    value = str(value)[1:-1]
                    self.specOppairsList.setText(str(value))
                    self.specOppairsList.setEnabled(True)
                    self.specOpCebCrossSpectra.setCheckState(QtCore.Qt.Checked)
                
            opObj = puObj.getOperationObj(name="selectChannels")
            if opObj == None:
                self.specOpChannel.clear()
                self.specOpCebChannel.setCheckState(0)
            else:   
               value = opObj.getParameterValue(parameterName='channelList')             
               value = str(value)[1:-1]
               self.specOpChannel.setText(value)
               self.specOpChannel.setEnabled(True)
               self.specOpCebChannel.setCheckState(QtCore.Qt.Checked)
                
            opObj = puObj.getOperationObj(name="selectHeights")
            if opObj == None:
                self.specOpHeights.clear()
                self.specOpCebHeights.setCheckState(0)
            else:
               value1 = int(opObj.getParameterValue(parameterName='minHei'))             
               value1 = str(value1)
               value2 = int(opObj.getParameterValue(parameterName='maxHei'))             
               value2 = str(value2)
               value = value1 + "," + value2
               self.specOpHeights.setText(value)
               self.specOpHeights.setEnabled(True)
               self.specOpCebHeights.setCheckState(QtCore.Qt.Checked)
           
            opObj = puObj.getOperationObj(name="IncohInt")                   
            if opObj == None:
                self.specOpIncoherent.clear()
                self.specOpCebIncoherent.setCheckState(0)  
            else:    
                for parmObj in opObj.getParameterObjList():
                   if parmObj.name == 'timeInterval':
                       value = opObj.getParameterValue(parameterName='timeInterval')             
                       value = float(value)
                       self.specOpIncoherent.setText(str(value))
                       self.specOpIncoherent.setEnabled(True)
                       self.specOpCebIncoherent.setCheckState(QtCore.Qt.Checked)
                       self.specOpCobIncInt.setCurrentIndex(0)
                       
                   if parmObj.name == 'n':
                       value = opObj.getParameterValue(parameterName='n')             
                       value = float(value)
                       self.specOpIncoherent.setText(str(value))
                       self.specOpIncoherent.setEnabled(True)
                       self.specOpCebIncoherent.setCheckState(QtCore.Qt.Checked)
                       self.specOpCobIncInt.setCurrentIndex(1)
                       
            opObj = puObj.getOperationObj(name="removeDC") 
            if opObj == None:
                self.specOpCebRemoveDC.setCheckState(0)
            else:                     
                self.specOpCebRemoveDC.setCheckState(QtCore.Qt.Checked)
                value = opObj.getParameterValue(parameterName='mode')
                if value == 1:
                    self.specOpComRemoveDC.setCurrentIndex(0)
                elif value == 2:
                    self.specOpComRemoveDC.setCurrentIndex(1)
                               
            opObj = puObj.getOperationObj(name="removeInterference") 
            if opObj == None:
                self.specOpCebRemoveInt.setCheckState(0)
            else:                     
                self.specOpCebRemoveInt.setCheckState(QtCore.Qt.Checked)
                
            opObj = puObj.getOperationObj(name='getNoise')
            if opObj == None:
                self.specOpCebgetNoise.setCheckState(0)
                self.specOpgetNoise.clear()
            else:
                self.specOpCebgetNoise.setCheckState(QtCore.Qt.Checked)               
                parmObj = opObj.getParameterObj(parameterName='minHei')
                if parmObj == None:
                    self.specOpgetNoise.clear()
                    value1 = None
                else:
                        value1 = opObj.getParameterValue(parameterName='minHei') 
                        value1 = str(value1)
                        parmObj = opObj.getParameterObj(parameterName='maxHei')
                        if parmObj == None:
                            value2 = None
                            value = value1
                            self.specOpgetNoise.setText(value)
                            self.specOpgetNoise.setEnabled(True)
                        else:
                            value2 = opObj.getParameterValue(parameterName='maxHei') 
                            value2 = str(value2)
                            parmObj = opObj.getParameterObj(parameterName='minVel')
                            if parmObj == None:
                                value3 = None
                                value = value1 + "," + value2
                                self.specOpgetNoise.setText(value)
                                self.specOpgetNoise.setEnabled(True)
                            else:
                                value3 = opObj.getParameterValue(parameterName='minVel') 
                                value3 = str(value3)
                                parmObj = opObj.getParameterObj(parameterName='maxVel')
                                if parmObj == None:
                                    value4 = None
                                    value = value1 + "," + value2 + "," + value3
                                    self.specOpgetNoise.setText(value)
                                    self.specOpgetNoise.setEnabled(True)
                                else:
                                    value4 = opObj.getParameterValue(parameterName='maxVel') 
                                    value4 = str(value4)
                                    value = value1 + "," + value2 + "," + value3 + ',' + value4
                                    self.specOpgetNoise.setText(value)
                                    self.specOpgetNoise.setEnabled(True)
                        
            opObj = puObj.getOperationObj(name='Plot')
            opObj = puObj.getOpObjfromParamValue(value="SpectraPlot")
            if opObj == None:
                self.specGraphCebSpectraplot.setCheckState(0)
                self.specGraphSaveSpectra.setCheckState(0)
                self.specGraphftpSpectra.setCheckState(0)

            else:
                operationSpectraPlot = "Enable"
                self.specGraphCebSpectraplot.setCheckState(QtCore.Qt.Checked)
                parmObj = opObj.getParameterObj(parameterName='channelList')
                if parmObj == None:
                       self.specGgraphChannelList.clear()
                else:
                    value = opObj.getParameterValue(parameterName='channelList')
                    channelListSpectraPlot = str(value)[1:-1]
                    self.specGgraphChannelList.setText(channelListSpectraPlot)
                    self.specGgraphChannelList.setEnabled(True)
               
                parmObj = opObj.getParameterObj(parameterName='xmin')
                if parmObj == None:
                    self.specGgraphFreq.clear()
                else:
                        value1 = opObj.getParameterValue(parameterName='xmin') 
                        value1 = str(value1)
                        value2 = opObj.getParameterValue(parameterName='xmax')            
                        value2 = str(value2)
                        value = value1 + "," + value2
                        self.specGgraphFreq.setText(value)
                        self.specGgraphFreq.setEnabled(True)
                                   
                parmObj = opObj.getParameterObj(parameterName='ymin')
                if parmObj == None:
                    self.specGgraphHeight.clear()
                else:
                        value1 = opObj.getParameterValue(parameterName='ymin') 
                        value1 = str(value1)
                        value2 = opObj.getParameterValue(parameterName='ymax')            
                        value2 = str(value2)
                        value = value1 + "," + value2
                        self.specGgraphHeight.setText(value)
                        self.specGgraphHeight.setEnabled(True)

                parmObj = opObj.getParameterObj(parameterName='zmin')
                if parmObj == None:
                    self.specGgraphDbsrange.clear()
                else:
                        value1 = opObj.getParameterValue(parameterName='zmin') 
                        value1 = str(value1)
                        value2 = opObj.getParameterValue(parameterName='zmax')            
                        value2 = str(value2)
                        value = value1 + "," + value2
                        self.specGgraphDbsrange.setText(value)
                        self.specGgraphDbsrange.setEnabled(True)
                
                
                parmObj = opObj.getParameterObj(parameterName="figpath")
                if parmObj == None:
                        self.specGraphSaveSpectra.setCheckState(0)
                else:
                        self.specGraphSaveSpectra.setCheckState(QtCore.Qt.Checked)
                        value = opObj.getParameterValue(parameterName='figpath')
                        self.specGraphPath.setText(value)
                        
                parmObj = opObj.getParameterObj(parameterName="ftp")
                if parmObj == None:
                        self.specGraphftpSpectra.setCheckState(0)
                else:
                        self.specGraphftpSpectra.setCheckState(QtCore.Qt.Checked)
                        try:
                            value = opObj.getParameterValue(parameterName='wr_period')
                        except:
                            value = " "
                        self.specGgraphftpratio.setText(str(value))
                        
            opObj = puObj.getOpObjfromParamValue(value="CrossSpectraPlot")
            if opObj == None:
                self.specGraphCebCrossSpectraplot.setCheckState(0)
                self.specGraphSaveCross.setCheckState(0)
    
            else:
                operationCrossSpectraPlot = "Enable"
                self.specGraphCebCrossSpectraplot.setCheckState(QtCore.Qt.Checked)
                parmObj = opObj.getParameterObj(parameterName='xmin')
                if parmObj == None:
                    self.specGgraphFreq.clear()
                else:
                        value1 = opObj.getParameterValue(parameterName='xmin') 
                        value1 = str(value1)
                        value2 = opObj.getParameterValue(parameterName='xmax')            
                        value2 = str(value2)
                        value = value1 + "," + value2
                        self.specGgraphFreq.setText(value)
                        self.specGgraphFreq.setEnabled(True)
                                   
                parmObj = opObj.getParameterObj(parameterName='ymin')
                if parmObj == None:
                    self.specGgraphHeight.clear()
                else:
                        value1 = opObj.getParameterValue(parameterName='ymin') 
                        value1 = str(value1)
                        value2 = opObj.getParameterValue(parameterName='ymax')            
                        value2 = str(value2)
                        value = value1 + "," + value2
                        self.specGgraphHeight.setText(value)
                        self.specGgraphHeight.setEnabled(True)

                parmObj = opObj.getParameterObj(parameterName='zmin')
                if parmObj == None:
                    self.specGgraphDbsrange.clear()
                else:
                        value1 = opObj.getParameterValue(parameterName='zmin') 
                        value1 = str(value1)
                        value2 = opObj.getParameterValue(parameterName='zmax')            
                        value2 = str(value2)
                        value = value1 + "," + value2
                        self.specGgraphDbsrange.setText(value)
                        self.specGgraphDbsrange.setEnabled(True)
                
                parmObj = opObj.getParameterObj(parameterName="figpath")
                if parmObj == None:
                    self.specGraphSaveCross.setCheckState(0)
                    
                else:
                        self.specGraphSaveCross.setCheckState(QtCore.Qt.Checked)
                        value = opObj.getParameterValue(parameterName='figpath')
                        self.specGraphPath.setText(value)
                
                parmObj = opObj.getParameterObj(parameterName="ftp")
                if parmObj == None:
                        self.specGraphftpCross.setCheckState(0)
                else:
                        self.specGraphftpCross.setCheckState(QtCore.Qt.Checked)
                        try:
                            value = opObj.getParameterValue(parameterName='wr_period')
                        except:
                            value = " "
                        self.specGgraphftpratio.setText(str(value))
                
            opObj = puObj.getOpObjfromParamValue(value="RTIPlot")
            if opObj == None:
                self.specGraphCebRTIplot.setCheckState(0)
                self.specGraphSaveRTIplot.setCheckState(0)
                self.specGraphftpRTIplot.setCheckState(0)
            else:
                self.specGraphCebRTIplot.setCheckState(QtCore.Qt.Checked)
                parmObj = opObj.getParameterObj(parameterName='channelList')
                if parmObj == None:
                       self.specGgraphChannelList.clear()
                else:
                    value = opObj.getParameterValue(parameterName='channelList')
                    channelListRTIPlot = str(value)[1:-1]
                    self.specGgraphChannelList.setText(channelListRTIPlot)
                    self.specGgraphChannelList.setEnabled(True)
                    
                parmObj = opObj.getParameterObj(parameterName='xmin')
                if parmObj == None:
                    self.specGgraphTminTmax.clear()
                else:
                        value1 = opObj.getParameterValue(parameterName='xmin') 
                        value1 = str(value1)
                        value2 = opObj.getParameterValue(parameterName='xmax')            
                        value2 = str(value2)
                        value = value1 + "," + value2
                        self.specGgraphTminTmax.setText(value)
                        self.specGgraphTminTmax.setEnabled(True)
                        
                parmObj = opObj.getParameterObj(parameterName='timerange')
                if parmObj == None:
                    self.specGgraphTimeRange.clear()
                else:
                        value1 = opObj.getParameterValue(parameterName='timerange') 
                        value1 = str(value1)
                        self.specGgraphTimeRange.setText(value1)
                        self.specGgraphTimeRange.setEnabled(True)
                                   
                parmObj = opObj.getParameterObj(parameterName='ymin')
                if parmObj == None:
                    self.specGgraphHeight.clear()
                else:
                        value1 = opObj.getParameterValue(parameterName='ymin') 
                        value1 = str(value1)
                        value2 = opObj.getParameterValue(parameterName='ymax')            
                        value2 = str(value2)
                        value = value1 + "," + value2
                        self.specGgraphHeight.setText(value)
                        self.specGgraphHeight.setEnabled(True)

                parmObj = opObj.getParameterObj(parameterName='zmin')
                if parmObj == None:
                    self.specGgraphDbsrange.clear()
                else:
                        value1 = opObj.getParameterValue(parameterName='zmin') 
                        value1 = str(value1)
                        value2 = opObj.getParameterValue(parameterName='zmax')            
                        value2 = str(value2)
                        value = value1 + "," + value2
                        self.specGgraphDbsrange.setText(value)
                        self.specGgraphDbsrange.setEnabled(True)
                                
                parmObj = opObj.getParameterObj(parameterName="figpath")
                if parmObj == None:
                    self.specGraphSaveRTIplot.setCheckState(0)
                else:
                        self.specGraphSaveRTIplot.setCheckState(QtCore.Qt.Checked)
                        value = opObj.getParameterValue(parameterName='figpath')
                        self.specGraphPath.setText(value)
                #---------add----#
                parmObj = opObj.getParameterObj(parameterName="ftp")
                if parmObj == None:
                    self.specGraphftpRTIplot.setCheckState(0)
                else:
                        self.specGraphftpRTIplot.setCheckState(QtCore.Qt.Checked)
                        try:
                            value = opObj.getParameterValue(parameterName='wr_period')
                        except:
                            value = " "
                        self.specGgraphftpratio.setText(str(value))
                        
                
            opObj = puObj.getOpObjfromParamValue(value="CoherenceMap")
            if opObj == None:
                self.specGraphCebCoherencmap.setCheckState(0)
                self.specGraphSaveCoherencemap.setCheckState(0)
                self.specGraphftpCoherencemap.setCheckState(0)
            
            else:
                operationCoherenceMap = "Enable"
                self.specGraphCebCoherencmap.setCheckState(QtCore.Qt.Checked)
                parmObj = opObj.getParameterObj(parameterName='xmin')
                if parmObj == None:
                    self.specGgraphTminTmax.clear()
                else:
                        value1 = opObj.getParameterValue(parameterName='xmin') 
                        value1 = str(value1)
                        value2 = opObj.getParameterValue(parameterName='xmax')            
                        value2 = str(value2)
                        value = value1 + "," + value2
                        self.specGgraphTminTmax.setText(value)
                        self.specGgraphTminTmax.setEnabled(True)
                
                parmObj = opObj.getParameterObj(parameterName='timerange')
                if parmObj == None:
                    self.specGgraphTimeRange.clear()
                else:
                        value1 = opObj.getParameterValue(parameterName='timerange') 
                        value1 = str(value1)
                        self.specGgraphTimeRange.setText(value1)
                        self.specGgraphTimeRange.setEnabled(True)
                        
                parmObj = opObj.getParameterObj(parameterName='ymin')
                if parmObj == None:
                    self.specGgraphHeight.clear()
                else:
                        value1 = opObj.getParameterValue(parameterName='ymin') 
                        value1 = str(value1)
                        value2 = opObj.getParameterValue(parameterName='ymax')            
                        value2 = str(value2)
                        value = value1 + "," + value2
                        self.specGgraphHeight.setText(value)
                        self.specGgraphHeight.setEnabled(True)
                        
                parmObj = opObj.getParameterObj(parameterName='zmin')
                if parmObj == None:
                    self.specGgraphmagnitud.clear()
                else:
                        value1 = opObj.getParameterValue(parameterName='zmin') 
                        value1 = str(value1)
                        value2 = opObj.getParameterValue(parameterName='zmax')            
                        value2 = str(value2)
                        value = value1 + "," + value2
                        self.specGgraphmagnitud.setText(value)
                        self.specGgraphmagnitud.setEnabled(True)
                        
                parmObj = opObj.getParameterObj(parameterName="figpath")
                if parmObj == None:
                    self.specGraphSaveCoherencemap.setCheckState(0)
                else:
                        self.specGraphSaveCoherencemap.setCheckState(QtCore.Qt.Checked)
                        value = opObj.getParameterValue(parameterName='figpath')
                        self.specGraphPath.setText(value)
                        
                parmObj = opObj.getParameterObj(parameterName="ftp")
                if parmObj == None:
                    self.specGraphftpCoherencemap.setCheckState(0)
                else:
                        self.specGraphftpCoherencemap.setCheckState(QtCore.Qt.Checked)
                        try:
                            value = opObj.getParameterValue(parameterName='wr_period')
                        except:
                            value = " "
                        self.specGgraphftpratio.setText(str(value))
                        

            opObj = puObj.getOpObjfromParamValue(value="PowerProfilePlot")
            if opObj == None:
                self.specGraphPowerprofile.setCheckState(0)
                self.specGraphSavePowerprofile.setCheckState(0)
                operationPowerProfilePlot = "Disabled"
                channelList = None
                freq_vel = None
                heightsrange = None
            else:
                operationPowerProfilePlot = "Enable"
                self.specGraphPowerprofile.setCheckState(QtCore.Qt.Checked)
                parmObj = opObj.getParameterObj(parameterName='xmin')
                if parmObj == None:
                    self.specGgraphDbsrange.clear()
                else:
                        value1 = opObj.getParameterValue(parameterName='xmin') 
                        value1 = str(value1)
                        value2 = opObj.getParameterValue(parameterName='xmax')            
                        value2 = str(value2)
                        value = value1 + "," + value2
                        self.specGgraphDbsrange.setText(value)
                        self.specGgraphDbsrange.setEnabled(True)
                        
                parmObj = opObj.getParameterObj(parameterName='ymin')
                if parmObj == None:
                    self.specGgraphHeight.clear()
                else:
                        value1 = opObj.getParameterValue(parameterName='ymin') 
                        value1 = str(value1)
                        value2 = opObj.getParameterValue(parameterName='ymax')            
                        value2 = str(value2)
                        value = value1 + "," + value2
                        self.specGgraphHeight.setText(value)
                        self.specGgraphHeight.setEnabled(True)
                        
                parmObj = opObj.getParameterObj(parameterName="figpath")
                if parmObj == None:
                    self.specGraphSavePowerprofile.setCheckState(0)
                else:
                        self.specGraphSavePowerprofile.setCheckState(QtCore.Qt.Checked)
                        value = opObj.getParameterValue(parameterName='figpath')
                        self.specGraphPath.setText(value)
                
                parmObj = opObj.getParameterObj(parameterName="ftp")
                if parmObj == None:
                   self.specGraphftpPowerprofile.setCheckState(0)
                else:
                    self.specGraphftpPowerprofile.setCheckState(QtCore.Qt.Checked)
                    try:
                        value = opObj.getParameterValue(parameterName='wr_period')
                    except:
                        value = " "
                    self.specGgraphftpratio.setText(str(value))
            # -noise
            opObj = puObj.getOpObjfromParamValue(value="Noise")
            if opObj == None:
                self.specGraphCebRTInoise.setCheckState(0)
                self.specGraphSaveRTInoise.setCheckState(0)
                self.specGraphftpRTInoise.setCheckState(0)
            else:
                self.specGraphCebRTInoise.setCheckState(QtCore.Qt.Checked)
                parmObj = opObj.getParameterObj(parameterName='channelList')
                if parmObj == None:
                       self.specGgraphChannelList.clear()
                else:
                    value = opObj.getParameterValue(parameterName='channelList')
                    channelListRTINoise = str(value)[1:-1]
                    self.specGgraphChannelList.setText(channelListRTINoise)
                    self.specGgraphChannelList.setEnabled(True)
                    
                parmObj = opObj.getParameterObj(parameterName='xmin')
                if parmObj == None:
                    self.specGgraphTminTmax.clear()
                else:
                        value1 = opObj.getParameterValue(parameterName='xmin') 
                        value1 = str(value1)
                        value2 = opObj.getParameterValue(parameterName='xmax')            
                        value2 = str(value2)
                        value = value1 + "," + value2
                        self.specGgraphTminTmax.setText(value)
                        self.specGgraphTminTmax.setEnabled(True)
                
                parmObj = opObj.getParameterObj(parameterName='timerange')
                if parmObj == None:
                    self.specGgraphTimeRange.clear()
                else:
                        value1 = opObj.getParameterValue(parameterName='timerange') 
                        value1 = str(value1)
                        self.specGgraphTimeRange.setText(value1)
                        self.specGgraphTimeRange.setEnabled(True)
                
                                   
                parmObj = opObj.getParameterObj(parameterName='ymin')
                if parmObj == None:
                    self.specGgraphDbsrange.clear()
                else:
                        value1 = opObj.getParameterValue(parameterName='ymin') 
                        value1 = str(value1)
                        value2 = opObj.getParameterValue(parameterName='ymax')            
                        value2 = str(value2)
                        value = value1 + "," + value2
                        self.specGgraphDbsrange.setText(value)
                        self.specGgraphDbsrange.setEnabled(True)
                                
                parmObj = opObj.getParameterObj(parameterName="figpath")
                if parmObj == None:
                    self.specGraphSaveRTInoise.setCheckState(0)
                else:
                        self.specGraphSaveRTInoise.setCheckState(QtCore.Qt.Checked)
                        value = opObj.getParameterValue(parameterName='figpath')
                        self.specGraphPath.setText(value)
                #---------add----#
                parmObj = opObj.getParameterObj(parameterName="ftp")
                if parmObj == None:
                    self.specGraphftpRTInoise.setCheckState(0)
                else:
                        self.specGraphftpRTInoise.setCheckState(QtCore.Qt.Checked)
                        try:
                            value = opObj.getParameterValue(parameterName='wr_period')
                        except:
                            value = " "
                        self.specGgraphftpratio.setText(str(value))        
                   
            # outputSpectraWrite
            opObj = puObj.getOperationObj(name='SpectraWriter')
            if opObj == None:
                self.specOutputPath.clear()
                self.specOutputblocksperfile.clear()
                self.specOutputprofileperblock.clear()
            else:
                value = opObj.getParameterObj(parameterName='path')
                if value == None:
                    self.specOutputPath.clear()
                else:
                    value = opObj.getParameterValue(parameterName='path')
                    path = str(value)
                    self.specOutputPath.setText(path) 
                value = opObj.getParameterObj(parameterName='blocksPerFile')
                if value == None:
                   self.specOutputblocksperfile.clear()
                else:
                    value = opObj.getParameterValue(parameterName='blocksPerFile')
                    blocksperfile = str(value)
                    self.specOutputblocksperfile.setText(blocksperfile)
                value = opObj.getParameterObj(parameterName='profilesPerBlock')
                if value == None:
                    self.specOutputprofileperblock.clear()
                else:
                    value = opObj.getParameterValue(parameterName='profilesPerBlock')
                    profilesPerBlock = str(value)
                    self.specOutputprofileperblock.setText(profilesPerBlock)
       
        if datatype == 'SpectraHeis':
            opObj = puObj.getOperationObj(name="IncohInt4SpectraHeis")                   
            if opObj == None:
                self.specHeisOpIncoherent.clear()
                self.specHeisOpCebIncoherent.setCheckState(0)  
            else:    
                for parmObj in opObj.getParameterObjList():
                   if parmObj.name == 'timeInterval':
                       value = opObj.getParameterValue(parameterName='timeInterval')             
                       value = float(value)
                       self.specHeisOpIncoherent.setText(str(value))
                       self.specHeisOpIncoherent.setEnabled(True)
                       self.specHeisOpCebIncoherent.setCheckState(QtCore.Qt.Checked)
                       self.specHeisOpCobIncInt.setCurrentIndex(0)
            # SpectraHeis Graph           
            opObj = puObj.getOperationObj(name='Plot')
            opObj = puObj.getOpObjfromParamValue(value="SpectraHeisScope")
            if opObj == None:
                self.specHeisGraphCebSpectraplot.setCheckState(0)
                self.specHeisGraphSaveSpectra.setCheckState(0)
                self.specHeisGraphftpSpectra.setCheckState(0)

            else:
                operationSpectraHeisScope = "Enable"
                self.specHeisGraphCebSpectraplot.setCheckState(QtCore.Qt.Checked)
                parmObj = opObj.getParameterObj(parameterName='channelList')
                if parmObj == None:
                       self.specHeisGgraphChannelList.clear()
                else:
                    value = opObj.getParameterValue(parameterName='channelList')
                    channelListSpectraHeisScope = str(value)[1:-1]
                    self.specHeisGgraphChannelList.setText(channelListSpectraHeisScope)
                    self.specHeisGgraphChannelList.setEnabled(True)
               
                parmObj = opObj.getParameterObj(parameterName='xmin')
                if parmObj == None:
                    self.specHeisGgraphXminXmax.clear()
                else:
                        value1 = opObj.getParameterValue(parameterName='xmin') 
                        value1 = str(value1)
                        value2 = opObj.getParameterValue(parameterName='xmax')            
                        value2 = str(value2)
                        value = value1 + "," + value2
                        self.specHeisGgraphXminXmax.setText(value)
                        self.specHeisGgraphXminXmax.setEnabled(True)
                                   
                parmObj = opObj.getParameterObj(parameterName='ymin')
                if parmObj == None:
                    self.specHeisGgraphYminYmax.clear()
                else:
                        value1 = opObj.getParameterValue(parameterName='ymin') 
                        value1 = str(value1)
                        value2 = opObj.getParameterValue(parameterName='ymax')            
                        value2 = str(value2)
                        value = value1 + "," + value2
                        self.specHeisGgraphYminYmax.setText(value)
                        self.specHeisGgraphYminYmax.setEnabled(True)            
                
                parmObj = opObj.getParameterObj(parameterName="figpath")
                if parmObj == None:
                        self.specHeisGraphSaveSpectra.setCheckState(0)
                else:
                        self.specHeisGraphSaveSpectra.setCheckState(QtCore.Qt.Checked)
                        value = opObj.getParameterValue(parameterName='figpath')
                        self.specHeisGraphPath.setText(value)
                        
                parmObj = opObj.getParameterObj(parameterName="ftp")
                if parmObj == None:
                        self.specHeisGraphftpSpectra.setCheckState(0)
                else:
                        self.specHeisGraphftpSpectra.setCheckState(QtCore.Qt.Checked)
                        try:
                            value = opObj.getParameterValue(parameterName='wr_period')
                        except:
                            value = " "
                        self.specHeisGgraphftpratio.setText(str(value))
                                    
                                                
            opObj = puObj.getOpObjfromParamValue(value="RTIfromSpectraHeis")
            if opObj == None:
                self.specHeisGraphCebRTIplot.setCheckState(0)
                self.specHeisGraphSaveRTIplot.setCheckState(0)
                self.specHeisGraphftpRTIplot.setCheckState(0)
            else:
                self.specHeisGraphCebRTIplot.setCheckState(QtCore.Qt.Checked)
                parmObj = opObj.getParameterObj(parameterName='channelList')
                if parmObj == None:
                       self.specHeisGgraphChannelList.clear()
                else:
                    value = opObj.getParameterValue(parameterName='channelList')
                    channelListRTIPlot = str(value)[1:-1]
                    self.specGgraphChannelList.setText(channelListRTIPlot)
                    self.specGgraphChannelList.setEnabled(True)
                    
                parmObj = opObj.getParameterObj(parameterName='xmin')
                if parmObj == None:
                    self.specHeisGgraphTminTmax.clear()
                else:
                        value1 = opObj.getParameterValue(parameterName='xmin') 
                        value1 = str(value1)
                        value2 = opObj.getParameterValue(parameterName='xmax')            
                        value2 = str(value2)
                        value = value1 + "," + value2
                        self.specHeisGgraphTminTmax.setText(value)
                        self.specHeisGgraphTminTmax.setEnabled(True)
                        
                parmObj = opObj.getParameterObj(parameterName='timerange')
                if parmObj == None:
                    self.specGgraphTimeRange.clear()
                else:
                        value1 = opObj.getParameterValue(parameterName='timerange') 
                        value1 = str(value1)
                        self.specHeisGgraphTimeRange.setText(value1)
                        self.specHeisGgraphTimeRange.setEnabled(True)
                                   
                parmObj = opObj.getParameterObj(parameterName='ymin')
                if parmObj == None:
                    self.specHeisGgraphYminYmax.clear()
                else:
                        value1 = opObj.getParameterValue(parameterName='ymin') 
                        value1 = str(value1)
                        value2 = opObj.getParameterValue(parameterName='ymax')            
                        value2 = str(value2)
                        value = value1 + "," + value2
                        self.specHeisGgraphYminYmax.setText(value)
                        self.specHeisGgraphYminYmax.setEnabled(True)
                                
                parmObj = opObj.getParameterObj(parameterName="figpath")
                if parmObj == None:
                    self.specHeisGraphSaveRTIplot.setCheckState(0)
                else:
                        self.specHeisGraphSaveRTIplot.setCheckState(QtCore.Qt.Checked)
                        value = opObj.getParameterValue(parameterName='figpath')
                        self.specHeisGraphPath.setText(value)
                #---------add----#
                parmObj = opObj.getParameterObj(parameterName="ftp")
                if parmObj == None:
                    self.specHeisGraphftpRTIplot.setCheckState(0)
                else:
                        self.specHeisGraphftpRTIplot.setCheckState(QtCore.Qt.Checked)
                        try:
                            value = opObj.getParameterValue(parameterName='wr_period')
                        except:
                            value = " "
                        self.specHeisGgraphftpratio.setText(str(value))
                
                
                
            # outputSpectraHeisWrite
            opObj = puObj.getOperationObj(name='FitsWriter')
            if opObj == None:
                self.specHeisOutputPath.clear()
                self.specHeisOutputblocksperfile.clear()
                self.specHeisOutputMetada.clear()
            else:
                value = opObj.getParameterObj(parameterName='path')
                if value == None:
                    self.specHeisOutputPath.clear()
                else:
                    value = opObj.getParameterValue(parameterName='path')
                    path = str(value)
                    self.specHeisOutputPath.setText(path) 
                value = opObj.getParameterObj(parameterName='dataBlocksPerFile')
                if value == None:
                   self.specHeisOutputblocksperfile.clear()
                else:
                    value = opObj.getParameterValue(parameterName='dataBlocksPerFile')
                    blocksperfile = str(value)
                    self.specHeisOutputblocksperfile.setText(blocksperfile)
                value = opObj.getParameterObj(parameterName='metadatafile')
                if value == None:
                    self.specHeisOutputMetada.clear()
                else:
                    value = opObj.getParameterValue(parameterName='metadatafile')
                    metada = str(value)
                    self.specHeisOutputMetada.setText(metada)
             

          
    def setspecGraph(self):

        self.specGgraphChannelList.setEnabled(True)

    def clearspecGraph(self):

        self.specGgraphChannelList.clear()

    def create_comm(self):
        self.commCtrlPThread = CommCtrlProcessThread()
        self.commCtrlPThread.start()
    
    def create_timers(self):
        self.comm_data_timer = QtCore.QTimer(self)
        self.comm_data_timer.timeout.connect(self.on_comm_data_timer)
        self.comm_data_timer.start(10)
    
    def create_figure(self):
        self.queue_plot = Queue.Queue()
        self.plotmanager = PlotManager(self.queue_plot)
        self.plot_timer = QtCore.QTimer()
        QtCore.QObject.connect(self.plot_timer, QtCore.SIGNAL("timeout()"), self.periodicCall)
        self.plot_timer.start(100)
        self.running = 1

    def periodicCall(self):
        """
        Check every 100 ms if there is something new in the queue.
        """
        self.plotmanager.processIncoming()
        if not self.running:
            app.quit()

    def on_comm_data_timer(self):
        # lee el data_queue y la coloca en el queue de ploteo
        try:
            reply = self.commCtrlPThread.data_q.get(block=False)
            self.queue_plot.put(reply.data)
            
        except Queue.Empty:
            pass

    def createProjectView(self, id):
        
        self.create = False
        project_name, description, datatype, data_path, starDate, endDate, startTime, endTime, online, delay, walk, set = self.getParmsFromProjectWindow()
        
        projectObjView = Project()
        projectObjView.setup(id=id, name=project_name, description=description)
        
        self.__projectObjDict[id] = projectObjView
        
        return projectObjView 
    
    def updateProjectView(self):
        
        project_name, description, datatype, data_path, starDate, endDate, startTime, endTime, online, delay, walk, set = self.getParmsFromProjectWindow()
        
        projectObjView = self.getSelectedProjectObj()
        projectObjView.update(name=project_name, description=description)
               
        return projectObjView
         
    def createReadUnitView(self, projectObjView):
        
        project_name, description, datatype, data_path, startDate, endDate, startTime, endTime, online, delay, walk , set = self.getParmsFromProjectWindow()
        if set == None:     
            readUnitConfObj = projectObjView.addReadUnit(datatype=datatype,
                                                    path=data_path,
                                                    startDate=startDate,
                                                    endDate=endDate,
                                                    startTime=startTime,
                                                    endTime=endTime,
                                                    online=online,
                                                    delay=delay,
                                                    walk=walk)
        else:
            readUnitConfObj = projectObjView.addReadUnit(datatype=datatype,
                                                            path=data_path,
                                                            startDate=startDate,
                                                            endDate=endDate,
                                                            startTime=startTime,
                                                            endTime=endTime,
                                                            online=online,
                                                            delay=delay,
                                                            walk=walk,
                                                            set=set)
        
        return readUnitConfObj

    def updateReadUnitView(self, projectObjView, idReadUnit):
        
        project_name, description, datatype, data_path, startDate, endDate, startTime, endTime, online, delay, walk , set = self.getParmsFromProjectWindow()
        
        readUnitConfObj = projectObjView.getProcUnitObj(idReadUnit)
        
        if set == None:
        
            readUnitConfObj.update(datatype=datatype,
                                    path=data_path,
                                    startDate=startDate,
                                    endDate=endDate,
                                    startTime=startTime,
                                    endTime=endTime,
                                    online=online,
                                    delay=delay,
                                    walk=walk)
                                    
        else:
            readUnitConfObj.update(datatype=datatype,
                        path=data_path,
                        startDate=startDate,
                        endDate=endDate,
                        startTime=startTime,
                        endTime=endTime,
                        online=online,
                        delay=delay,
                        walk=walk,
                        set=set)
            
            
        
        return readUnitConfObj
        
    def createProcUnitView(self, projectObjView, datatype, inputId):
        
        procUnitConfObj = projectObjView.addProcUnit(datatype=datatype, inputId=inputId)
        
        self.__puObjDict[procUnitConfObj.getId()] = procUnitConfObj
        
        return procUnitConfObj
    
    def updateProcUnitView(self, id):
        
        procUnitConfObj = projectObjView.getProcUnitObj(id)
        procUnitConfObj.removeOperations()
        
        return procUnitConfObj
        
    def addPUWindow(self):
        
        self.configUPWindowObj = UnitProcessWindow(self)
        fatherObj = self.getSelectedPUObj()
        try:
            fatherObj.getElementName()
        except:
            self.console.append("First left click on Project or Processing Unit")
            return 0
            
        if fatherObj.getElementName() == 'Project':
            readUnitConfObj = fatherObj.getReadUnitObj()
            self.configUPWindowObj.dataTypeProject = str(readUnitConfObj.datatype)
            
        self.configUPWindowObj.getfromWindowList.append(fatherObj)
        self.configUPWindowObj.loadTotalList()
        self.configUPWindowObj.show()
        self.configUPWindowObj.closed.connect(self.createPUWindow)
        
    def createPUWindow(self):
        
        self.console.clear()
        
        if not self.configUPWindowObj.create:
            return
        
        fatherObj = self.configUPWindowObj.getFromWindow
        datatype = self.configUPWindowObj.typeofUP  
    
        if fatherObj.getElementName() == 'Project':
            inputId = fatherObj.getReadUnitId()
            projectObjView = fatherObj   
        else:
            inputId = fatherObj.getId()
            projectObjView = self.getSelectedProjectObj()
        
        #----------------------------
        puObj = self.createProcUnitView(projectObjView, datatype, inputId)
        #----------------------------
        self.addPU2ProjectExplorer(id=puObj.getId(), name=datatype)
        
        self.showtabPUCreated(datatype)
        
        self.setInputsPU_View(datatype)
        
        self.showPUinitView()   
        
    def addFTPparmXML(self, obj, server, folder, username, password, ftp_wei, exp_code, sub_exp_code, plot_pos):
        obj.addParameter(name='server', value=server, format='str')
        obj.addParameter(name='folder', value=folder, format='str')
        obj.addParameter(name='username', value=username, format='str')
        obj.addParameter(name='password', value=password, format='str')
        if ftp_wei == None:
            pass
        else:
            obj.addParameter(name='ftp_wei', value=int(ftp_wei), format='int')
        if exp_code == None:
            pass
        else:
            obj.addParameter(name='exp_code', value=int(exp_code), format='int')
        if sub_exp_code == None:
            pass
        else:
            obj.addParameter(name='sub_exp_code', value=int(sub_exp_code), format='int')
        if plot_pos == None:
            pass
        else:
            obj.addParameter(name='plot_pos', value=int(plot_pos), format='int')    
        
    def addFTPConfiguration(self, puObj, opObj):
        if self.temporalFTP.create:
           server, folder, username, password, ftp_wei, exp_code, sub_exp_code, plot_pos = self.temporalFTP.recover()
           self.addFTPparmXML(opObj, server, folder, username, password, ftp_wei, exp_code, sub_exp_code, plot_pos)
        else:
            self.temporalFTP.setwithoutconfiguration()
            server, folder, username, password, ftp_wei, exp_code, sub_exp_code, plot_pos = self.temporalFTP.recover()
            self.addFTPparmXML(opObj, server, folder, username, password, ftp_wei, exp_code, sub_exp_code, plot_pos)
   
        if puObj.datatype == "Spectra":
            value = self.specGgraphftpratio.text()
        if puObj.datatype == "SpectraHeis":
             value = self.specHeisGgraphftpratio.text()
        if not value == "":
            try:
                if puObj.datatype == "Spectra":
                    value = int(self.specGgraphftpratio.text())
                if puObj.datatype == "SpectraHeis":
                    value = int(self.specHeisGgraphftpratio.text())
            except:
                   self.console.clear()
                   self.console.append("Please Write the Ratio")
                   return 0
            opObj.addParameter(name='wr_period', value=value, format='int')   
     
    def bufferProject(self, caracteristica, principal, description):
        self.projectProperCaracteristica.append(caracteristica)
        self.projectProperPrincipal.append(principal)
        self.projectProperDescripcion.append(description)
        return self.projectProperCaracteristica, self.projectProperPrincipal, self.projectProperDescripcion
        
    
    def showProjectProperties(self, projectObjView):
        
        project_name, description = projectObjView.name, projectObjView.description
        
        id = projectObjView.id
        readUnitId = projectObjView.getReadUnitId()
        readUnitObj = projectObjView.getProcUnitObj(readUnitId)
        operationObj = readUnitObj.getOperationObj(name='run')
        
        
        datatype = operationObj.getParameterValue(parameterName='datatype')
        dpath = operationObj.getParameterValue(parameterName='path')
        startDate = operationObj.getParameterValue(parameterName='startDate')
        endDate = operationObj.getParameterValue(parameterName='endDate')
        startDate = str(startDate)
        endDate = str(endDate)
        startDateList = startDate.split('-')
        endDateList = endDate.split('-')
        startDate = startDateList[0] + "/" + startDateList[1] + "/" + startDateList[2]
        endDate = endDateList[0] + "/" + endDateList[1] + "/" + endDateList[2]
        
        startTime = operationObj.getParameterValue(parameterName='startTime')
        endTime = operationObj.getParameterValue(parameterName='endTime')
        online = operationObj.getParameterValue(parameterName='online')
        walk = operationObj.getParameterValue(parameterName='walk')
        delay = operationObj.getParameterValue(parameterName='delay')
        try:
            set = operationObj.getParameterValue(parameterName='set')
        except:
            set = " "
        
        if online == 0:
            remode = "offline"
        else:
            remode = "online"
        
        if walk == 0:
            walk_str = 'On Files'
        else:
            walk_str = 'On Folder'
            
        self.bufferProject("Properties", "Name", project_name),
        self.bufferProject("Properties", "Data Path", dpath)
        self.bufferProject("Properties", "Workspace", self.pathWorkSpace)
        self.bufferProject("Parameters", "Read Mode ", remode)
        self.bufferProject("Parameters", "DataType  ", datatype)
        self.bufferProject("Parameters", "Start Date", str(startDate))
        self.bufferProject("Parameters", "End Date   ", str(endDate))
        self.bufferProject("Parameters", "Start Time", str(startTime))
        self.bufferProject("Parameters", "End Time  ", str(endTime))
        self.bufferProject("Parameters", "Delay  ", str(delay))
        try:
            set = operationObj.getParameterValue(parameterName='set')
            self.bufferProject("Parameters", "Set  ", set)
        except:
            set = " "
        self.bufferProject("Parameters", "Walk  ", str(walk_str))
        self.bufferProject("Parameters", "Time zone", "Local")
        self.bufferProject("Description", "Summary  ", description)
            
        self.propertiesModel = treeModel()
        self.propertiesModel.showProjectParms(self.projectProperCaracteristica, self.projectProperPrincipal, self.projectProperDescripcion)
        self.treeProjectProperties.setModel(self.propertiesModel)
        self.treeProjectProperties.expandAll()  
        self.treeProjectProperties.resizeColumnToContents(0)
        self.treeProjectProperties.resizeColumnToContents(1)
        
        self.projectProperCaracteristica = []
        self.projectProperPrincipal = []
        self.projectProperDescripcion = []
        
        return datatype , dpath , startDate , endDate, startTime, endTime, online, delay, walk, set
                       
    def showPUinitView(self):
        self.propertiesModel = treeModel()
        self.propertiesModel.initPUVoltageView()
        self.treeProjectProperties.setModel(self.propertiesModel)
        self.treeProjectProperties.expandAll()
        self.treeProjectProperties.allColumnsShowFocus()
        self.treeProjectProperties.resizeColumnToContents(1)
        
    def bufferVoltage(self, caracteristica, principal, description):
        self.volProperCaracteristica.append(caracteristica)
        self.volProperPrincipal.append(principal)
        self.volProperDescripcion.append(description)
        return self.volProperCaracteristica, self.volProperPrincipal, self.volProperDescripcion
        
    def showPUVoltageProperties(self, puObj):
       
        
        type = puObj.name
        self.bufferVoltage("Processing Unit", "Type", type)
        
        opObj = puObj.getOperationObj(name="setRadarFrequency")
        if opObj == None:
            radarfrequency = None
        else:
            value = opObj.getParameterValue(parameterName='frequency')             
            value = str(value)
            radarfrequency = value
            self.bufferVoltage("Processing Unit", "Radar Frequency", radarfrequency)
        
        opObj = puObj.getOperationObj(name="selectChannels")
        if opObj == None:
            channel = None
        else:
            value = opObj.getParameterValue(parameterName='channelList')             
            value = str(value)[1:-1]
            channel = value
            self.bufferVoltage("Processing Unit", "Select Channel", channel)
            
            
                            
        opObj = puObj.getOperationObj(name="selectHeights")
        if opObj == None:
            heights = None
        else:
           value1 = int(opObj.getParameterValue(parameterName='minHei'))             
           value1 = str(value1)
           value2 = int(opObj.getParameterValue(parameterName='maxHei'))             
           value2 = str(value2)
           value = value1 + "," + value2
           heights = value
           self.bufferVoltage("Processing Unit", "Select Heights", heights)

        
        opObj = puObj.getOperationObj(name="filterByHeights")           
        if opObj == None:
            filter = None
        else:
            value = opObj.getParameterValue(parameterName='window')             
            value = str(value)
            filter = value
            self.bufferVoltage("Processing Unit", "Filter", filter)


        opObj = puObj.getOperationObj(name="ProfileSelector") 
        if opObj == None:  
            profile = None       
        else: 
           for parmObj in opObj.getParameterObjList():
               if parmObj.name == "profileRangeList":
                   value = opObj.getParameterValue(parameterName='profileRangeList')             
                   value = str(value)[1:-1]
                   profile = value
                   self.bufferVoltage("Processing Unit", "Select Profile", profile)

               if parmObj.name == "profileList":
                   value = opObj.getParameterValue(parameterName='profileList')             
                   value = str(value)[1:-1]
                   profile = value
                   self.bufferVoltage("Processing Unit", "Select Profile", profile)
        
        opObj = puObj.getOperationObj(name="CohInt")   
        if opObj == None:
            coherentintegration = None
        else:
            value = opObj.getParameterValue(parameterName='n')
            coherentintegration = value
            self.bufferVoltage("Processing Unit", "Coherente Integration", coherentintegration)

        
                     
        opObj = puObj.getOperationObj(name="Decoder")
        if opObj == None:
            self.volOpCebDecodification.setCheckState(0)
            code = None
            mode = None
        else:
            self.volOpCebDecodification.setCheckState(QtCore.Qt.Checked)
            try:
                valueBaud = opObj.getParameterValue(parameterName='nBaud')
            except:
                status = "off"
            try:
                valueCode = opObj.getParameterValue(parameterName='nCode')
                status = "on"
            except:
                status = "off"
            
            if not status == "off":
                if int(valueCode) == 1:
                   Comp = ""              
                else:
                   Comp = "+" + "Comp."
                code = "Barker" + str(valueBaud) + str(Comp)
            else:
                code = "Default" 
            self.bufferVoltage("Decodification", "Code", code)
            
            try:
                value = opObj.getParameterValue(parameterName='mode')
                status = "on"
            except:    
                 status = "off"  
             
            if not status == "off":     
                self.volOpComMode.setCurrentIndex(value)
                if int(value) == 0:
                   mode = "Time"
                else:
                   mode = "freq" + str(value)
            else:
                mode = "Default"
            self.bufferVoltage("Decodification", "Mode", mode)

        # graph
        opObj = puObj.getOperationObj(name='Plot')
        if opObj == None:
            self.volGraphCebshow.setCheckState(0)
            operation = "Disabled"
            channelList = None
            freq_vel = None
            heightsrange = None
        else:
            operation = 'Enabled'
            self.bufferVoltage("Scope", "Operation", operation),
            self.volGraphCebshow.setCheckState(QtCore.Qt.Checked)
            value = opObj.getParameterObj(parameterName='channelList')
            if value == None:
                channelList = None
            else:
                 value = opObj.getParameterValue(parameterName='channelList')       
                 value = str(value)[1:-1]
                 channelList = value 
                 self.bufferVoltage("Scope", "Channel List", channelList)

            
            value1 = opObj.getParameterObj(parameterName='xmin') 
            if value1 == None:
                freq_vel = None
            else:
                value1 = opObj.getParameterValue(parameterName='xmin')
                value1 = str(value1)
            value2 = opObj.getParameterObj(parameterName='xmax')            
            if value2 == None:
                freq_vel = None
            else:  
                value2 = opObj.getParameterValue(parameterName='xmax')
                value2 = str(value2)
                value = value1 + "," + value2
                freq_vel = value
                self.bufferVoltage("Scope", "Freq/Vel", freq_vel)

            value1 = opObj.getParameterObj(parameterName='ymin') 
            if value1 == None:
                heightsrange = None
            else:
                value1 = opObj.getParameterValue(parameterName='ymin') 
                value1 = str(value1)
            value2 = opObj.getParameterObj(parameterName='ymax')            
            if value2 == None:
                fheightsrange = None
            else:  
                value2 = opObj.getParameterValue(parameterName='ymax') 
                value2 = str(value2)
                value = value1 + "," + value2
                heightsrange = value
                self.bufferVoltage("Scope", "Height Range", heightsrange)

            parmObj = opObj.getParameterObj(parameterName="figpath")
            if parmObj == None:
                 self.volGraphCebSave.setCheckState(QtCore.Qt.Unchecked)
                 figpath = None
            else:
                 self.volGraphCebSave.setCheckState(QtCore.Qt.Checked)
                 value = opObj.getParameterValue(parameterName='figpath')
                 figpath = value
                 self.bufferVoltage("Scope", "Path", figpath)
        # outputVoltageWrite
        opObj = puObj.getOperationObj(name='VoltageWriter')
        if opObj == None:
            pass
        else:
            operation = 'Enabled'
            self.bufferVoltage("Output", "Operation", operation)
            value = opObj.getParameterObj(parameterName='path')
            if value == None:
                path = None
            else:
                value = opObj.getParameterValue(parameterName='path')
                path = str(value)
                self.bufferVoltage("Output", "Path", path)
            value = opObj.getParameterObj(parameterName='blocksPerFile')
            if value == None:
                blocksperfile = None
            else:
                value = opObj.getParameterValue(parameterName='blocksPerFile')
                blocksperfile = str(value)
                self.bufferVoltage("Output", "BlocksPerFile", blocksperfile)
            value = opObj.getParameterObj(parameterName='profilesPerBlock')
            if value == None:
                profilesPerBlock = None
            else:
                value = opObj.getParameterValue(parameterName='profilesPerBlock')
                profilesPerBlock = str(value)
                self.bufferVoltage("Output", "ProfilesPerBlock", profilesPerBlock)
        
                                 
      # set model PU Properties
        
        self.propertiesModel = treeModel()
        self.propertiesModel.showPUVoltageParms(self.volProperCaracteristica, self.volProperPrincipal, self.volProperDescripcion)
        self.volProperCaracteristica = []
        self.volProperPrincipal = []
        self.volProperDescripcion = []
        self.treeProjectProperties.setModel(self.propertiesModel)
        self.treeProjectProperties.expandAll()
        self.treeProjectProperties.allColumnsShowFocus()
        self.treeProjectProperties.resizeColumnToContents(0)
        self.treeProjectProperties.resizeColumnToContents(1)
        
    def bufferSpectra(self, caracteristica, principal, description):
        self.specProperCaracteristica.append(caracteristica)
        self.specProperPrincipal.append(principal)
        self.specProperDescripcion.append(description)
        return self.specProperCaracteristica, self.specProperPrincipal, self.specProperDescripcion
        
    def showPUSpectraProperties(self, puObj):
        type = puObj.name
        self.bufferSpectra("Processing Unit", "Type", type)
        
        opObj = puObj.getOperationObj(name="setRadarFrequency")
        if opObj == None:
            radarfrequency = None
        else:
            value = opObj.getParameterValue(parameterName='frequency')             
            value = str(value)
            radarfrequency = value
            self.bufferSpectra("Processing Unit", "Radar Frequency", radarfrequency)
        

        opObj = puObj.getOperationObj(name="init")   
        if opObj == None:
            self.specOpnFFTpoints.clear()
            self.specOpProfiles.clear()
            self.specOpippFactor.clear()
        else:
            parmObj = opObj.getParameterObj(parameterName='nProfiles')
            if parmObj == None:
                nProfiles = None
            else:
                value = opObj.getParameterValue(parameterName='nProfiles')  
                nProfiles = value
                self.bufferSpectra("Processing Unit", "nProfiles", nProfiles)
            
            parmObj = opObj.getParameterObj(parameterName='nFFTPoints')
            if parmObj == None:
                nFFTPoints = None
            else:
                value = opObj.getParameterValue(parameterName='nFFTPoints')  
                nFFTPoints = value
                self.bufferSpectra("Processing Unit", "nFFTpoints", nFFTPoints)
           
            parmObj = opObj.getParameterObj(parameterName='ippFactor')
            if parmObj == None:
                ippFactor = None
            else:
                value = opObj.getParameterValue(parameterName='ippFactor')
                ippFactor = value
                self.bufferSpectra("Processing Unit", "Ipp Factor", ippFactor)


        opObj = puObj.getOperationObj(name="init")  
        if opObj == None:
            pairsList = None
        else:
            parm = opObj.getParameterObj(parameterName='pairsList')  
            if parm == None:
                pairsList = None
            else:              
                value = opObj.getParameterValue(parameterName='pairsList')  
                value = str(value)[1:-1]
                pairsList = value
                self.bufferSpectra("Processing Unit", "PairsList", pairsList)

            
        opObj = puObj.getOperationObj(name="selectChannels")
        if opObj == None:
            channel = None
        else:   
           value = opObj.getParameterValue(parameterName='channelList')             
           value = str(value)[1:-1]
           channel = value
           self.bufferSpectra("Processing Unit", "Channel", channel)
                    
        opObj = puObj.getOperationObj(name="selectHeights")
        if opObj == None:
            heights = None
        else:
           value1 = int(opObj.getParameterValue(parameterName='minHei'))             
           value1 = str(value1)
           value2 = int(opObj.getParameterValue(parameterName='maxHei'))             
           value2 = str(value2)
           value = value1 + "," + value2
           heights = value
           self.bufferSpectra("Processing Unit", "Heights", heights)
       
        opObj = puObj.getOperationObj(name="IncohInt")                   
        if opObj == None:
            incoherentintegration = None
        else:  
            try:  
                value = opObj.getParameterValue(parameterName='timeInterval')
            except:
                value = opObj.getParameterValue(parameterName='n')
                
            value = float(value)
            incoherentintegration = str(value)
            self.bufferSpectra("Processing Unit", "Incoherent Integration", incoherentintegration)     

            
        opObj = puObj.getOperationObj(name="removeDC") 
        if opObj == None:
            removeDC = None
        else: 
            value = opObj.getParameterValue(parameterName='mode')
            self.bufferSpectra("Processing Unit", "Remove DC", value)
            
        opObj = puObj.getOperationObj(name="removeInterference") 
        if opObj == None:
            removeInterference = None
        else:       
            self.bufferSpectra("Processing Unit", "Remove Interference", "1")
        
        opObj = puObj.getOperationObj(name="getNoise") 
        if opObj == None:
            getNoise = None
        else:
            value1 = opObj.getParameterObj(parameterName='minHei') 
            if value1 == None:
                getNoise = None
                getNoise = "Default"
                self.bufferSpectra("Processing Unit", "Get Noise", getNoise)  
                
            else:
                value1 = opObj.getParameterValue(parameterName='minHei')
                value1 = str(value1)
                value2 = opObj.getParameterObj(parameterName='maxHei')            
                if value2 == None:
                    getNoise = None
                    value = value1 
                    getNoise = value
                    self.bufferSpectra("Processing Unit", "Get Noise", getNoise)     
                else:  
                    value2 = opObj.getParameterValue(parameterName='maxHei')
                    value2 = str(value2)
                    value3 = opObj.getParameterObj(parameterName='minVel')            
                    if value3 == None:
                        getNoise = None
                        value = value1 + "," + value2
                        getNoise = value
                        self.bufferSpectra("Processing Unit", "Get Noise", getNoise)
                    else:  
                        value3 = opObj.getParameterValue(parameterName='minVel')
                        value3 = str(value3)
                        value4 = opObj.getParameterObj(parameterName='maxVel')            
                        if value4 == None:
                            getNoise = None
                            value = value1 + "," + value2 + ',' + value3
                            getNoise = value
                            self.bufferSpectra("Processing Unit", "Get Noise", getNoise)
                        else:
                            value4 = opObj.getParameterValue(parameterName='maxVel')
                            value4 = str(value4)
                            value = value1 + "," + value2 + ',' + value3 + ',' + value4
                            getNoise = value
                            self.bufferSpectra("Processing Unit", "Get Noise", getNoise)

            
        opObj = puObj.getOpObjfromParamValue(value="SpectraPlot")
        if opObj == None:
            operationSpectraPlot = "Disabled"
            freq_vel = None
            heightsrange = None
            channelListSpectraPlot = None
        else:
            operationSpectraPlot = "Enable"
            self.bufferSpectra("Spectra Plot", "Operation", operationSpectraPlot)
            parmObj = opObj.getParameterObj(parameterName='channelList')
            if parmObj == None:
                channelListSpectraPlot = None
            else:
                value = opObj.getParameterValue(parameterName='channelList')
                channelListSpectraPlot = str(value)[1:-1]
                self.bufferSpectra("Spectra Plot", "Channel List", channelListSpectraPlot)
            
            
            value1 = opObj.getParameterObj(parameterName='xmin') 
            if value1 == None:
                freq_vel = None
            else:
                value1 = opObj.getParameterValue(parameterName='xmin')
                value1 = str(value1)
            value2 = opObj.getParameterObj(parameterName='xmax')            
            if value2 == None:
                freq_vel = None
            else:  
                value2 = opObj.getParameterValue(parameterName='xmax')
                value2 = str(value2)
                value = value1 + "," + value2
                freq_vel = value
                self.bufferSpectra("Spectra Plot", "Freq/Vel", freq_vel)
            
            value1 = opObj.getParameterObj(parameterName='ymin') 
            if value1 == None:
                heightsrange = None
            else:
                value1 = opObj.getParameterValue(parameterName='ymin') 
                value1 = str(value1)
            value2 = opObj.getParameterObj(parameterName='ymax')            
            if value2 == None:
                fheightsrange = None
            else:  
                value2 = opObj.getParameterValue(parameterName='ymax') 
                value2 = str(value2)
                value = value1 + "," + value2
                heightsrange = value
                self.bufferSpectra("Spectra Plot", "Height Range", heightsrange)
            
            value1 = opObj.getParameterObj(parameterName='zmin') 
            if value1 == None:
                dBrange = None
            else:
                value1 = opObj.getParameterValue(parameterName='zmin') 
                value1 = str(value1)
            value2 = opObj.getParameterObj(parameterName='zmax')            
            if value2 == None:
                fdBrange = None
            else:  
                value2 = opObj.getParameterValue(parameterName='zmax') 
                value2 = str(value2)
                value = value1 + "," + value2
                dbrange = value
                self.bufferSpectra("Spectra Plot", "dB Range", dbrange)
            
            parmObj = opObj.getParameterObj(parameterName="figpath")
            if parmObj == None:
               path = None
            else:
               path = opObj.getParameterValue(parameterName='figpath')
               self.bufferSpectra("Spectra Plot", "Save Path", path)
            
            parmObj = opObj.getParameterObj(parameterName="ftp")
            if parmObj == None:
                    status = 'disable'
            else:
                    status = 'enable'
                    self.bufferSpectra("Spectra Plot", "FTP", status)
                    self.showWr_Period(puObj, opObj, nameplotop="Spectra Plot")
                    self.saveFTPvalues(opObj)
             
        opObj = puObj.getOpObjfromParamValue(value="CrossSpectraPlot")
        if opObj == None:
            self.specGraphCebCrossSpectraplot.setCheckState(0)
            operationCrossSpectraPlot = "Disabled"
            channelList = None
            freq_vel = None
            heightsrange = None
        else:
            operationCrossSpectraPlot = "Enable"
            self.specGraphCebCrossSpectraplot.setCheckState(QtCore.Qt.Checked)
            self.bufferSpectra("Cross Spectra Plot", "Operation", operationCrossSpectraPlot)         
            
            value1 = opObj.getParameterObj(parameterName='xmin') 
            if value1 == None:
                freq_vel = None
            else:
                value1 = opObj.getParameterValue(parameterName='xmin')
                value1 = str(value1)
            value2 = opObj.getParameterObj(parameterName='xmax')            
            if value2 == None:
                freq_vel = None
            else:  
                value2 = opObj.getParameterValue(parameterName='xmax')
                value2 = str(value2)
                value = value1 + "," + value2
                freq_vel = value
                self.bufferSpectra("Cross Spectra Plot", "Freq/Vel", freq_vel)
             
            value1 = opObj.getParameterObj(parameterName='ymin') 
            if value1 == None:
                heightsrange = None
            else:
                value1 = opObj.getParameterValue(parameterName='ymin') 
                value1 = str(value1)
            value2 = opObj.getParameterObj(parameterName='ymax')            
            if value2 == None:
                fheightsrange = None
            else:  
                value2 = opObj.getParameterValue(parameterName='ymax') 
                value2 = str(value2)
                value = value1 + "," + value2
                heightsrange = value
                self.bufferSpectra("Cross Spectra Plot", "Height Range", heightsrange)
            
            value1 = opObj.getParameterObj(parameterName='zmin') 
            if value1 == None:
                dBrange = None
            else:
                value1 = opObj.getParameterValue(parameterName='zmin') 
                value1 = str(value1)
            value2 = opObj.getParameterObj(parameterName='zmax')            
            if value2 == None:
                fdBrange = None
            else:  
                value2 = opObj.getParameterValue(parameterName='zmax') 
                value2 = str(value2)
                value = value1 + "," + value2
                dbrange = value
                self.bufferSpectra("Cross Spectra Plot", "dB Range", dbrange)
            
            parmObj = opObj.getParameterObj(parameterName="figpath")
            if parmObj == None:
               path = None
            else:
               path = opObj.getParameterValue(parameterName='figpath')
               self.bufferSpectra("Cross Spectra Plot", "Save Path", path)
            
            parmObj = opObj.getParameterObj(parameterName="ftp")
            if parmObj == None:
                    status = 'disable'
            else:
                    status = 'enable'
                    self.bufferSpectra("Cross Spectra Plot", "FTP", status)
                    self.showWr_Period(puObj, opObj, nameplotop="Cross Spectra Plot")
                    self.saveFTPvalues(opObj)
            
            
        opObj = puObj.getOpObjfromParamValue(value="RTIPlot")
        if opObj == None:
            self.specGraphCebRTIplot.setCheckState(0)
            operationRTIPlot = "Disabled"
            channelList = None
            freq_vel = None
            heightsrange = None
        else:
            operationRTIPlot = "Enable"
            self.specGraphCebRTIplot.setCheckState(QtCore.Qt.Checked)
            self.bufferSpectra("RTI Plot", "Operation", operationRTIPlot)
            parmObj = opObj.getParameterObj(parameterName='channelList')
            if parmObj == None:
                channelListRTIPlot = None
            else:
                value = opObj.getParameterValue(parameterName='channelList')
                channelListRTIPlot = str(value)[1:-1]
                self.bufferSpectra("RTI Plot", "Channel List", channelListRTIPlot)
            
            
            value1 = opObj.getParameterObj(parameterName='xmin') 
            if value1 == None:
                freq_vel = None
            else:
                value1 = opObj.getParameterValue(parameterName='xmin')
                value1 = str(value1)
            value2 = opObj.getParameterObj(parameterName='xmax')            
            if value2 == None:
                freq_vel = None
            else:  
                value2 = opObj.getParameterValue(parameterName='xmax')
                value2 = str(value2)
                value = value1 + "," + value2
                tmintmax = value
                self.bufferSpectra("RTI Plot", "Tmin,Tmax", tmintmax)
                
            parmObj = opObj.getParameterObj(parameterName='timerange')
            if parmObj == None:
                timerange = None
            else:
                value = opObj.getParameterValue(parameterName='timerange')
                timerange = str(value)
                self.bufferSpectra("RTI Plot", "Time Range", timerange)
            
            value1 = opObj.getParameterObj(parameterName='ymin') 
            if value1 == None:
                heightsrange = None
            else:
                value1 = opObj.getParameterValue(parameterName='ymin') 
                value1 = str(value1)
            value2 = opObj.getParameterObj(parameterName='ymax')            
            if value2 == None:
                fheightsrange = None
            else:  
                value2 = opObj.getParameterValue(parameterName='ymax') 
                value2 = str(value2)
                value = value1 + "," + value2
                heightsrange = value
                self.bufferSpectra("RTI Plot", "Height Range", heightsrange)
            
            value1 = opObj.getParameterObj(parameterName='zmin') 
            if value1 == None:
                dBrange = None
            else:
                value1 = opObj.getParameterValue(parameterName='zmin') 
                value1 = str(value1)
            value2 = opObj.getParameterObj(parameterName='zmax')            
            if value2 == None:
                fdBrange = None
            else:  
                value2 = opObj.getParameterValue(parameterName='zmax') 
                value2 = str(value2)
                value = value1 + "," + value2
                dbrange = value
                self.bufferSpectra("RTI Plot", "dB Range", dbrange)
            
            parmObj = opObj.getParameterObj(parameterName="figpath")
            if parmObj == None:
               path = None
            else:
               path = opObj.getParameterValue(parameterName='figpath')
               self.bufferSpectra("RTI Plot", "Save Path", path)
            
            parmObj = opObj.getParameterObj(parameterName="ftp")
            if parmObj == None:
                    status = 'disable'
            else:
                status = 'enable'
                self.bufferSpectra("RTI Plot", "FTP", status)
                self.showWr_Period(puObj, opObj, nameplotop="RTI Plot")
                self.saveFTPvalues(opObj)
            
            
        opObj = puObj.getOpObjfromParamValue(value="CoherenceMap")
        if opObj == None:
            self.specGraphCebCoherencmap.setCheckState(0)
            operationCoherenceMap = "Disabled"
            channelList = None
            freq_vel = None
            heightsrange = None
        else:
            operationCoherenceMap = "Enable"
            self.specGraphCebCoherencmap.setCheckState(QtCore.Qt.Checked)
            self.bufferSpectra("Coherence Map Plot", "Operation", operationCoherenceMap)
            parmObj = opObj.getParameterObj(parameterName='channelList')
            if parmObj == None:
                channelListRTIPlot = None
            else:
                value = opObj.getParameterValue(parameterName='channelList')
                channelListRTIPlot = str(value)[1:-1]
                self.bufferSpectra("Coherence Map Plot", "Channel List", channelListRTIPlot)
            
            
            value1 = opObj.getParameterObj(parameterName='xmin') 
            if value1 == None:
                freq_vel = None
            else:
                value1 = opObj.getParameterValue(parameterName='xmin')
                value1 = str(value1)
            value2 = opObj.getParameterObj(parameterName='xmax')            
            if value2 == None:
                freq_vel = None
            else:  
                value2 = opObj.getParameterValue(parameterName='xmax')
                value2 = str(value2)
                value = value1 + "," + value2
                tmintmax = value
                self.bufferSpectra("Coherence Map Plot", "Tmin,Tmax", tmintmax)
                
            parmObj = opObj.getParameterObj(parameterName='timerange')
            if parmObj == None:
                timerange = None
            else:
                value = opObj.getParameterValue(parameterName='timerange')
                timerange = str(value)
                self.bufferSpectra("Coherence Map Plot", "Time Range", timerange)
            
            value1 = opObj.getParameterObj(parameterName='ymin') 
            if value1 == None:
                heightsrange = None
            else:
                value1 = opObj.getParameterValue(parameterName='ymin') 
                value1 = str(value1)
            value2 = opObj.getParameterObj(parameterName='ymax')            
            if value2 == None:
                fheightsrange = None
            else:  
                value2 = opObj.getParameterValue(parameterName='ymax') 
                value2 = str(value2)
                value = value1 + "," + value2
                heightsrange = value
                self.bufferSpectra("Coherence Map Plot", "Height Range", heightsrange)
            
            value1 = opObj.getParameterObj(parameterName='zmin') 
            if value1 == None:
                dBrange = None
            else:
                value1 = opObj.getParameterValue(parameterName='zmin') 
                value1 = str(value1)
            value2 = opObj.getParameterObj(parameterName='zmax')            
            if value2 == None:
                fdBrange = None
            else:  
                value2 = opObj.getParameterValue(parameterName='zmax') 
                value2 = str(value2)
                value = value1 + "," + value2
                dbrange = value
                self.bufferSpectra("Coherence Map Plot", "Magnitud", dbrange)
            
            parmObj = opObj.getParameterObj(parameterName="figpath")
            if parmObj == None:
               path = None
            else:
               path = opObj.getParameterValue(parameterName='figpath')
               self.bufferSpectra("Coherence Map Plot", "Save Path", path)
            
            parmObj = opObj.getParameterObj(parameterName="ftp")
            if parmObj == None:
                    status = 'disable'
            else:
                status = 'enable'
                self.bufferSpectra("Coherence Map Plot", "FTP", status)
                self.showWr_Period(puObj, opObj, nameplotop="Coherence Map Plot")
                self.saveFTPvalues(opObj)
    
            
        
        opObj = puObj.getOpObjfromParamValue(value="PowerProfilePlot")
        if opObj == None:
            self.specGraphPowerprofile.setCheckState(0)
            operationPowerProfilePlot = "Disabled"
            channelList = None
            freq_vel = None
            heightsrange = None
        else:
            operationPowerProfilePlot = "Enable"
            self.specGraphPowerprofile.setCheckState(QtCore.Qt.Checked)
            self.bufferSpectra("PowerProfile Plot", "Operation", operationPowerProfilePlot)
            parmObj = opObj.getParameterObj(parameterName='channelList')
            if parmObj == None:
                channelListSpectraPlot = None
            else:
                value = opObj.getParameterValue(parameterName='channelList')
                channelListSpectraPlot = str(value)[1:-1]
                self.bufferSpectra("PowerProfile Plot", "Channel List", channelListSpectraPlot)
            
            
            value1 = opObj.getParameterObj(parameterName='xmin') 
            if value1 == None:
                freq_vel = None
            else:
                value1 = opObj.getParameterValue(parameterName='xmin')
                value1 = str(value1)
            value2 = opObj.getParameterObj(parameterName='xmax')            
            if value2 == None:
                freq_vel = None
            else:  
                value2 = opObj.getParameterValue(parameterName='xmax')
                value2 = str(value2)
                value = value1 + "," + value2
                dbrange = value
                self.bufferSpectra("PowerProfile Plot", "dbRange", dbrange)
            
            value1 = opObj.getParameterObj(parameterName='ymin') 
            if value1 == None:
                heightsrange = None
            else:
                value1 = opObj.getParameterValue(parameterName='ymin') 
                value1 = str(value1)
            value2 = opObj.getParameterObj(parameterName='ymax')            
            if value2 == None:
                fheightsrange = None
            else:  
                value2 = opObj.getParameterValue(parameterName='ymax') 
                value2 = str(value2)
                value = value1 + "," + value2
                heightsrange = value
                self.bufferSpectra("PowerProfile Plot", "Height Range", heightsrange)
            
            
            parmObj = opObj.getParameterObj(parameterName="figpath")
            if parmObj == None:
               path = None
            else:
               path = opObj.getParameterValue(parameterName='figpath')
               self.bufferSpectra("PowerProfile Plot", "Save Path", path)
            
            parmObj = opObj.getParameterObj(parameterName="ftp")
            if parmObj == None:
                    status = 'disable'
            else:
                status = 'enable'
                self.bufferSpectra("PowerProfile Plot", "FTP", status)
                self.showWr_Period(puObj, opObj, nameplotop="PowerProfile Plot")
                self.saveFTPvalues(opObj)
                
        # noise
        opObj = puObj.getOpObjfromParamValue(value="Noise")
        if opObj == None:
            self.specGraphCebRTInoise.setCheckState(0)
            operationRTINoise = "Disabled"
            channelList = None
            freq_vel = None
            dbRange = None
        else:
            operationRTINoise = "Enable"
            self.specGraphCebRTInoise.setCheckState(QtCore.Qt.Checked)
            self.bufferSpectra("Noise Plot", "Operation", operationRTINoise)
            parmObj = opObj.getParameterObj(parameterName='channelList')
            if parmObj == None:
                channelListRTINoise = None
            else:
                value = opObj.getParameterValue(parameterName='channelList')
                channelListRTINoise = str(value)[1:-1]
                self.bufferSpectra("Noise Plot", "Channel List", channelListRTINoise)
            
            
            value1 = opObj.getParameterObj(parameterName='xmin') 
            if value1 == None:
                freq_vel = None
            else:
                value1 = opObj.getParameterValue(parameterName='xmin')
                value1 = str(value1)
            value2 = opObj.getParameterObj(parameterName='xmax')            
            if value2 == None:
                freq_vel = None
            else:  
                value2 = opObj.getParameterValue(parameterName='xmax')
                value2 = str(value2)
                value = value1 + "," + value2
                tmintmax = value
                self.bufferSpectra("Noise Plot", "Tmin,Tmax", tmintmax)
            
            parmObj = opObj.getParameterObj(parameterName='timerange')
            if parmObj == None:
                timerange = None
            else:
                value = opObj.getParameterValue(parameterName='timerange')
                timerange = str(value)
                self.bufferSpectra("Noise Plot", "Time Range", timerange)
                
                
            
            value1 = opObj.getParameterObj(parameterName='ymin') 
            if value1 == None:
                DBrange = None
            else:
                value1 = opObj.getParameterValue(parameterName='ymin') 
                value1 = str(value1)
            value2 = opObj.getParameterObj(parameterName='ymax')            
            if value2 == None:
                fdBrange = None
            else:  
                value2 = opObj.getParameterValue(parameterName='ymax') 
                value2 = str(value2)
                value = value1 + "," + value2
                dBrange = value
                self.bufferSpectra("Noise Plot", "dB Range", dBrange)
                            
            parmObj = opObj.getParameterObj(parameterName="figpath")
            if parmObj == None:
               path = None
            else:
               path = opObj.getParameterValue(parameterName='figpath')
               self.bufferSpectra("Noise Plot", "Save Path", path)
            
            parmObj = opObj.getParameterObj(parameterName="ftp")
            if parmObj == None:
                    status = 'disable'
            else:
                    status = 'enable'
                    self.bufferSpectra("Noise Plot", "FTP", status)
                    self.showWr_Period(puObj, opObj, nameplotop="Noise Plot")
                    self.saveFTPvalues(opObj)
        
        if self.temporalFTP.create:
            self.bufferSpectra("FTP", "Server", self.temporalFTP.server)
            self.bufferSpectra("FTP", "Folder", self.temporalFTP.folder)
            self.bufferSpectra("FTP", "Username", self.temporalFTP.username)
            self.bufferSpectra("FTP", "Password", self.temporalFTP.password)
            self.bufferSpectra("FTP", "Ftp_wei", self.temporalFTP.ftp_wei)
            self.bufferSpectra("FTP", "Exp_code", self.temporalFTP.exp_code)
            self.bufferSpectra("FTP", "Sub_exp_code", self.temporalFTP.sub_exp_code)
            self.bufferSpectra("FTP", "Plot_pos", self.temporalFTP.plot_pos)  
            # self.temporalFTP.create=False
            self.temporalFTP.withoutconfig = False      
        
        if self.temporalFTP.withoutconfig:        
            self.bufferSpectra("FTP", "Server", self.temporalFTP.server)
            self.bufferSpectra("FTP", "Folder", self.temporalFTP.folder)
            self.bufferSpectra("FTP", "Username", self.temporalFTP.username)
            self.bufferSpectra("FTP", "Password", self.temporalFTP.password)
            self.bufferSpectra("FTP", "Ftp_wei", self.temporalFTP.ftp_wei)
            self.bufferSpectra("FTP", "Exp_code", self.temporalFTP.exp_code)
            self.bufferSpectra("FTP", "Sub_exp_code", self.temporalFTP.sub_exp_code)
            self.bufferSpectra("FTP", "Plot_pos", self.temporalFTP.plot_pos)
            self.temporalFTP.withoutconfig = False
            
            ####
            self.temporalFTP.create = False

        # outputSpectraWrite
        opObj = puObj.getOperationObj(name='SpectraWriter')
        if opObj == None:
            pass
        else:
            operation = 'Enabled'
            self.bufferSpectra("Output", "Operation", operation)
            value = opObj.getParameterObj(parameterName='path')
            if value == None:
                path = None
            else:
                value = opObj.getParameterValue(parameterName='path')
                path = str(value)
                self.bufferSpectra("Output", "Path", path)
            value = opObj.getParameterObj(parameterName='blocksPerFile')
            if value == None:
                blocksperfile = None
            else:
                value = opObj.getParameterValue(parameterName='blocksPerFile')
                blocksperfile = str(value)
                self.bufferSpectra("Output", "BlocksPerFile", blocksperfile)
            value = opObj.getParameterObj(parameterName='profilesPerBlock')
            if value == None:
                profilesPerBlock = None
            else:
                value = opObj.getParameterValue(parameterName='profilesPerBlock')
                profilesPerBlock = str(value)
                self.bufferSpectra("Output", "ProfilesPerBlock", profilesPerBlock)
        
# set model PU Properties
        
        self.propertiesModel = treeModel()
        self.propertiesModel.showPUSpectraParms(self.specProperCaracteristica, self.specProperPrincipal, self.specProperDescripcion)
                                                
        self.treeProjectProperties.setModel(self.propertiesModel)
        self.treeProjectProperties.expandAll()
        self.treeProjectProperties.allColumnsShowFocus()
        self.treeProjectProperties.resizeColumnToContents(0)
        self.treeProjectProperties.resizeColumnToContents(1)
        
        self.specProperCaracteristica = []
        self.specProperDescripcion = []
        self.specProperPrincipal = []
        
        
    def bufferSpectraHeis(self, caracteristica, principal, description):
        self.specHeisProperCaracteristica.append(caracteristica)
        self.specHeisProperPrincipal.append(principal)
        self.specHeisProperDescripcion.append(description)
        return self.specHeisProperCaracteristica, self.specHeisProperPrincipal, self.specHeisProperDescripcion

        
    def showPUSpectraHeisProperties(self, puObj):
        type = puObj.name
        self.bufferSpectraHeis("Processing Unit", "Type", type)
        
        opObj = puObj.getOperationObj(name="IncohInt4SpectraHeis")                   
        if opObj == None:
            incoherentintegration = None
        else:   
            value = opObj.getParameterValue(parameterName='timeInterval')             
            value = float(value)
            incoherentintegration = str(value)
            self.bufferSpectraHeis("Processing Unit", "Incoherent Integration", incoherentintegration)  
        # spectraheis graph
        opObj = puObj.getOpObjfromParamValue(value="SpectraHeisScope")
        if opObj == None:
            self.specHeisGraphCebSpectraplot.setCheckState(0)
            operationSpectraHeisPlot = "Disabled"
            xmin_xmax = None
            ymin_ymax = None
            channelListSpectraPlot = None
        else:
            operationSpectraHeisPlot = "Enable"
            self.specHeisGraphCebSpectraplot.setCheckState(QtCore.Qt.Checked)
            self.bufferSpectraHeis("SpectraHeis Plot", "Operation", operationSpectraHeisPlot)
            parmObj = opObj.getParameterObj(parameterName='channelList')
            if parmObj == None:
                channelListSpectraPlot = None
            else:
                value = opObj.getParameterValue(parameterName='channelList')
                channelListSpectraPlot = str(value)[1:-1]
                self.bufferSpectraHeis("SpectraHeis Plot", "Channel List", channelListSpectraPlot)
            
            
            value1 = opObj.getParameterObj(parameterName='xmin') 
            if value1 == None:
                xmin_xmax = None
            else:
                value1 = opObj.getParameterValue(parameterName='xmin')
                value1 = str(value1)
            value2 = opObj.getParameterObj(parameterName='xmax')            
            if value2 == None:
                xmin_xmax = None
            else:  
                value2 = opObj.getParameterValue(parameterName='xmax')
                value2 = str(value2)
                value = value1 + "," + value2
                xmin_xmax = value
                self.bufferSpectraHeis("SpectraHeis Plot", "Xmin-Xmax", xmin_xmax)
            
            value1 = opObj.getParameterObj(parameterName='ymin') 
            if value1 == None:
                ymin_ymax = None
            else:
                value1 = opObj.getParameterValue(parameterName='ymin') 
                value1 = str(value1)
            value2 = opObj.getParameterObj(parameterName='ymax')            
            if value2 == None:
                ymin_ymax = None
            else:  
                value2 = opObj.getParameterValue(parameterName='ymax') 
                value2 = str(value2)
                value = value1 + "," + value2
                ymin_ymax = value
                self.bufferSpectraHeis("SpectraHeis Plot", "Ymin-Ymax", ymin_ymax)
                      
            parmObj = opObj.getParameterObj(parameterName="figpath")
            if parmObj == None:
               path = None
            else:
               path = opObj.getParameterValue(parameterName='figpath')
               self.bufferSpectraHeis("SpectraHeis Plot", "Save Path", path)
            
            parmObj = opObj.getParameterObj(parameterName="ftp")
            if parmObj == None:
                    status = 'disable'
            else:
                    status = 'enable'
                    self.bufferSpectraHeis("SpectraHeis Plot", "FTP", status)
                    self.showWr_Period(puObj, opObj, nameplotop="SpectraHeis Plot")
                    self.saveFTPvalues(opObj)
                    
        opObj = puObj.getOpObjfromParamValue(value="RTIfromSpectraHeis")
        if opObj == None:
            self.specHeisGraphCebRTIplot.setCheckState(0)
            operationRTIPlot = "Disabled"
            channelList = None
            freq_vel = None
            heightsrange = None
        else:
            operationRTIPlot = "Enable"
            self.specHeisGraphCebRTIplot.setCheckState(QtCore.Qt.Checked)
            self.bufferSpectraHeis("RTIHeis Plot", "Operation", operationRTIPlot)
            parmObj = opObj.getParameterObj(parameterName='channelList')
            if parmObj == None:
                channelListRTIPlot = None
            else:
                value = opObj.getParameterValue(parameterName='channelList')
                channelListRTIPlot = str(value)[1:-1]
                self.bufferSpectraHeis("RTIHeis Plot", "Channel List", channelListRTIPlot)
            
            
            value1 = opObj.getParameterObj(parameterName='xmin') 
            if value1 == None:
                freq_vel = None
            else:
                value1 = opObj.getParameterValue(parameterName='xmin')
                value1 = str(value1)
            value2 = opObj.getParameterObj(parameterName='xmax')            
            if value2 == None:
                freq_vel = None
            else:  
                value2 = opObj.getParameterValue(parameterName='xmax')
                value2 = str(value2)
                value = value1 + "," + value2
                tmintmax = value
                self.bufferSpectraHeis("RTIHeis Plot", "Tmin,Tmax", tmintmax)
                
            parmObj = opObj.getParameterObj(parameterName='timerange')
            if parmObj == None:
                timerange = None
            else:
                value = opObj.getParameterValue(parameterName='timerange')
                timerange = str(value)
                self.bufferSpectraHeis("RTIHeis Plot", "Time Range", timerange)
            
            value1 = opObj.getParameterObj(parameterName='ymin') 
            if value1 == None:
                heightsrange = None
            else:
                value1 = opObj.getParameterValue(parameterName='ymin') 
                value1 = str(value1)
            value2 = opObj.getParameterObj(parameterName='ymax')            
            if value2 == None:
                fheightsrange = None
            else:  
                value2 = opObj.getParameterValue(parameterName='ymax') 
                value2 = str(value2)
                value = value1 + "," + value2
                heightsrange = value
                self.bufferSpectraHeis("RTIHeis Plot", "Ymin-Ymax", heightsrange)
            
            parmObj = opObj.getParameterObj(parameterName="figpath")
            if parmObj == None:
               path = None
            else:
               path = opObj.getParameterValue(parameterName='figpath')
               self.bufferSpectraHeis("RTIHeis Plot", "Save Path", path)
            
            parmObj = opObj.getParameterObj(parameterName="ftp")
            if parmObj == None:
                    status = 'disable'
            else:
                status = 'enable'
                self.bufferSpectraHeis("RTIHeis Plot", "FTP", status)
                self.showWr_Period(puObj, opObj, nameplotop="RTIHeis Plot")
                self.saveFTPvalues(opObj)
                
        if self.temporalFTP.create:
            self.bufferSpectraHeis("FTP", "Server", self.temporalFTP.server)
            self.bufferSpectraHeis("FTP", "Folder", self.temporalFTP.folder)
            self.bufferSpectraHeis("FTP", "Username", self.temporalFTP.username)
            self.bufferSpectraHeis("FTP", "Password", self.temporalFTP.password)
            self.bufferSpectraHeis("FTP", "Ftp_wei", self.temporalFTP.ftp_wei)
            self.bufferSpectraHeis("FTP", "Exp_code", self.temporalFTP.exp_code)
            self.bufferSpectraHeis("FTP", "Sub_exp_code", self.temporalFTP.sub_exp_code)
            self.bufferSpectraHeis("FTP", "Plot_pos", self.temporalFTP.plot_pos)  
            # self.temporalFTP.create=False
            self.temporalFTP.withoutconfig = False      
        
        if self.temporalFTP.withoutconfig:        
            self.bufferSpectraHeis("FTP", "Server", self.temporalFTP.server)
            self.bufferSpectraHeis("FTP", "Folder", self.temporalFTP.folder)
            self.bufferSpectraHeis("FTP", "Username", self.temporalFTP.username)
            self.bufferSpectraHeis("FTP", "Password", self.temporalFTP.password)
            self.bufferSpectraHeis("FTP", "Ftp_wei", self.temporalFTP.ftp_wei)
            self.bufferSpectraHeis("FTP", "Exp_code", self.temporalFTP.exp_code)
            self.bufferSpectraHeis("FTP", "Sub_exp_code", self.temporalFTP.sub_exp_code)
            self.bufferSpectraHeis("FTP", "Plot_pos", self.temporalFTP.plot_pos)
            self.temporalFTP.withoutconfig = False
            
            ####
            self.temporalFTP.create = False

        # outputSpectraHeisWrite
        opObj = puObj.getOperationObj(name='FitsWriter')
        if opObj == None:
            pass
        else:
            operation = 'Enabled'
            self.bufferSpectraHeis("Output", "Operation", operation)
            value = opObj.getParameterObj(parameterName='path')
            if value == None:
                path = None
            else:
                value = opObj.getParameterValue(parameterName='path')
                path = str(value)
                self.bufferSpectraHeis("Output", "Path", path)
            value = opObj.getParameterObj(parameterName='dataBlocksPerFile')
            if value == None:
                blocksperfile = None
            else:
                value = opObj.getParameterValue(parameterName='dataBlocksPerFile')
                blocksperfile = str(value)
                self.bufferSpectraHeis("Output", "BlocksPerFile", blocksperfile)
            value = opObj.getParameterObj(parameterName='metadatafile')
            if value == None:
                metadata = None
            else:
                value = opObj.getParameterValue(parameterName='metadatafile')
                metadata = str(value)
                self.bufferSpectraHeis("Output", "Metadata", metadata)
        
# set model PU Properties
        
        self.propertiesModel = treeModel()
        self.propertiesModel.showPUSpectraHeisParms(self.specHeisProperCaracteristica, self.specHeisProperPrincipal, self.specHeisProperDescripcion)
                                                
        self.treeProjectProperties.setModel(self.propertiesModel)
        self.treeProjectProperties.expandAll()
        self.treeProjectProperties.allColumnsShowFocus()
        self.treeProjectProperties.resizeColumnToContents(0)
        self.treeProjectProperties.resizeColumnToContents(1)
        
        self.specHeisProperCaracteristica = []
        self.specHeisProperDescripcion = []
        self.specHeisProperPrincipal = []
        
        
    def showWr_Period(self, puObj, opObj, nameplotop):
        parmObj = opObj.getParameterObj(parameterName='wr_period')
        if parmObj == None:
            wr_period = None
        else:
            value = opObj.getParameterValue(parameterName='wr_period')
            wr_period = str(value)
            if puObj.datatype == "Spectra":
                self.bufferSpectra(nameplotop, "wr_period", wr_period)
            if puObj.datatype == "SpectraHeis":
                self.bufferSpectraHeis(nameplotop, "wr_period", wr_period)
           
    def saveFTPvalues(self, opObj):
        parmObj = opObj.getParameterObj(parameterName="server")
        if parmObj == None:
            server = 'jro-app.igp.gob.pe'                      
        else:
            server = opObj.getParameterValue(parameterName='server')
        
        parmObj = opObj.getParameterObj(parameterName="folder")
        if parmObj == None:
            folder = '/home/wmaster/graficos'
        else:
            folder = opObj.getParameterValue(parameterName='folder')
        
        parmObj = opObj.getParameterObj(parameterName="username")
        if parmObj == None:
            username = 'wmaster'
        else:
            username = opObj.getParameterValue(parameterName='username')
        
        parmObj = opObj.getParameterObj(parameterName="password")
        if parmObj == None:
            password = 'mst2010vhf'
        else:
            password = opObj.getParameterValue(parameterName='password')
        
        parmObj = opObj.getParameterObj(parameterName="ftp_wei")
        if parmObj == None:
            ftp_wei = '0'
        else:
            ftp_wei = opObj.getParameterValue(parameterName='ftp_wei')
        
        parmObj = opObj.getParameterObj(parameterName="exp_code")
        if parmObj == None:
            exp_code = '0'
        else:
            exp_code = opObj.getParameterValue(parameterName='exp_code')
        
        parmObj = opObj.getParameterObj(parameterName="sub_exp_code")
        if parmObj == None:
            sub_exp_code = '0'
        else:
            sub_exp_code = opObj.getParameterValue(parameterName='sub_exp_code')

        parmObj = opObj.getParameterObj(parameterName="plot_pos")
        if parmObj == None:
            plot_pos = '0'
            self.temporalFTP.setwithoutconfiguration()
        else:
            plot_pos = opObj.getParameterValue(parameterName='plot_pos')
            self.temporalFTP.save(server, folder, username, password, ftp_wei, exp_code, sub_exp_code, plot_pos)

    def addProject2ProjectExplorer(self, id, name):
        
        itemTree = QtGui.QStandardItem(QtCore.QString(str(name)))
        self.parentItem = self.projectExplorerModel.invisibleRootItem()
        self.parentItem.appendRow(itemTree)
        self.parentItem = itemTree
        self.projectExplorerTree.setCurrentIndex(self.parentItem.index())

        self.selectedItemTree = itemTree
        
        self.__itemTreeDict[id] = itemTree
        
    def addPU2ProjectExplorer(self, id, name):
#         id1= round(int(id)/10.)*10
#         id= int(id)
#         id=id-id1
        itemTree = QtGui.QStandardItem(QtCore.QString(str(name)))
        
        self.parentItem = self.selectedItemTree
        self.parentItem.appendRow(itemTree)   
        self.projectExplorerTree.expandAll()
        self.parentItem = itemTree
        self.projectExplorerTree.setCurrentIndex(self.parentItem.index())

        self.selectedItemTree = itemTree
               
        self.__itemTreeDict[id] = itemTree
         
    def addPU2PELoadXML(self, id, name, idParent):
        
        itemTree = QtGui.QStandardItem(QtCore.QString(str(name)))
        if self.__itemTreeDict.has_key(idParent):
            self.parentItem = self.__itemTreeDict[idParent]
        else:
            self.parentItem = self.selectedItemTree
        self.parentItem.appendRow(itemTree)   
        self.projectExplorerTree.expandAll()
        self.parentItem = itemTree
        self.projectExplorerTree.setCurrentIndex(self.parentItem.index())

        self.selectedItemTree = itemTree
               
        self.__itemTreeDict[id] = itemTree
        # print "stop"
    
    def getSelectedProjectObj(self):
        
        for key in self.__itemTreeDict.keys():
            if self.__itemTreeDict[key] != self.selectedItemTree:
                continue
            
            if self.__projectObjDict.has_key(key):
                projectObj = self.__projectObjDict[key]
            else:
                puObj = self.__puObjDict[key]
                if puObj.parentId == None:
                    id = puObj.getId()[0]
                else:
                    id = puObj.parentId
                projectObj = self.__projectObjDict[id]
            
            return projectObj
        
        self.showWarning()
        
        return None

    def getSelectedPUObj(self):
        
        for key in self.__itemTreeDict.keys():
            if self.__itemTreeDict[key] != self.selectedItemTree:
                continue
            
            if self.__projectObjDict.has_key(key) == True:
                fatherObj = self.__projectObjDict[key]
            else:
                fatherObj = self.__puObjDict[key]
                    
            return fatherObj
        
        self.showWarning()
        
        return None
      
    def playProject(self, ext=".xml"):
        
            projectObj = self.getSelectedProjectObj()
            
            filename = os.path.join(str(self.pathWorkSpace),
                                    "%s_%s%s" %(str(projectObj.name), str(projectObj.id), ext)
                                    )
            
            self.console.clear()
            projectObj.writeXml(filename)  
            self.console.append("Please Wait...")
#             try:
            self.commCtrlPThread.cmd_q.put(ProcessCommand(ProcessCommand.PROCESS, filename))
# #  
#             except:
#                 self.console.append("Error............................................!")
#                 self.actionStarToolbar.setEnabled(True)
#                 self.actionPauseToolbar.setEnabled(False)
#                 self.actionStopToolbar.setEnabled(False)
            
#         filename = '/home/dsuarez/workspace_signalchain/schain_guiJune04/test/ewdrifts3.xml'
#         data = filename
#         self.commCtrlPThread.cmd_q.put(ProcessCommand(ProcessCommand.PROCESS, data))
        
    def stopProject(self):
        stop = True
        self.commCtrlPThread.cmd_q.put(ProcessCommand(ProcessCommand.STOP, stop))
    
    def pauseProject(self):
        self.commCtrlPThread.cmd_q.put(ProcessCommand(ProcessCommand.PAUSE, data=True))

                          
    def saveProject(self):
        
        puObj = self.getSelectedPUObj() 
        if puObj.name == 'VoltageProc':
            self.on_volOpOk_clicked()   
        if puObj.name == 'SpectraProc':
            self.on_specOpOk_clicked()   
        if puObj.name == 'SpectraHeisProc':
            self.on_specHeisOpOk_clicked()
        projectObj = self.getSelectedProjectObj()  
        puObjorderList = OrderedDict(sorted(projectObj.procUnitConfObjDict.items(), key=lambda x: x[0]))
        
        for inputId, puObj in puObjorderList.items():
            # print puObj.datatype, puObj.inputId,puObj.getId(),puObj.parentId
                
            if puObj.name == "VoltageProc":
                self.refreshID(puObj) 
            
            if puObj.name == "SpectraProc":            
                self.refreshID(puObj)   
            if puObj.name == "SpectraHeisProc":
                self.refreshID(puObj)   
          
        filename = self.pathWorkSpace + "/" + str(projectObj.name) + str(projectObj.id) + ".xml"
        projectObj.writeXml(filename)     
        self.console.append("Now,  you can push the icon Start in the toolbar or push start in menu run")

        
    def deleteProjectorPU(self):
        """
        Metodo para eliminar el proyecto en el dictionario de proyectos y en el dictionario de vista de arbol
        """
        for key in self.__itemTreeDict.keys():
            if self.__itemTreeDict[key] != self.selectedItemTree:
                continue
            
            if self.__projectObjDict.has_key(key) == True:
                
                del self.__projectObjDict[key]
                del self.__itemTreeDict[key]
                
            else:
                puObj = self.__puObjDict[key]
                if puObj.parentId == None:
                    id = puObj.getId()[0]
                else:
                    id = puObj.parentId
                projectObj = self.__projectObjDict[id]
                del self.__puObjDict[key]
                del self.__itemTreeDict[key]
                del projectObj.procUnitConfObjDict[key]
                for key in projectObj.procUnitConfObjDict.keys():
                    if projectObj.procUnitConfObjDict[key].inputId != puObj.getId():
                        continue
                    del self.__puObjDict[projectObj.procUnitConfObjDict[key].getId()]
                    del self.__itemTreeDict[projectObj.procUnitConfObjDict[key].getId()]
                    del projectObj.procUnitConfObjDict[key]
                # print projectObj.procUnitConfObjDict
            # print self.__itemTreeDict,self.__projectObjDict,self.__puObjDict    
        self.showWarning()

    def showWarning(self):
        pass
    
    def getParmsFromProjectWindow(self):
        """
        Return Inputs Project:
        - id
        - project_name
        - datatype
        - ext
        - data_path
        - readmode
        - delay
        - set
        - walk
        """
        project_name = str(self.proName.text())
        try:
           name = str(self.proName.text())
        except:
            self.console.clear()
            self.console.append("Please Write  a name")
            return 0          
            
        desc = str(self.proDescription.toPlainText())
        datatype = str(self.proComDataType.currentText())
        data_path = str(self.proDataPath.text())
        if not os.path.exists(path):
            self.proOk.setEnabled(False)
            self.console.clear()
            self.console.append("Write a correct a path")
            return 

        online = int(self.online)
        if online == 0:
            delay = 0
            set = 0
        else:
            delay = self.proDelay.text()
            try:
                delay = int(self.proDelay.text())
            except:
                self.console.clear()
                self.console.append("Please Write  a number for delay")
                return 0
            
            set = self.proSet.text()
            try:
                set = int(self.proSet.text())
            except:
                self.console.clear()
                set = None
                
        
        walk = int(self.walk)
        starDate = str(self.proComStartDate.currentText())
        endDate = str(self.proComEndDate.currentText())
        reloj1 = self.proStartTime.time()
        reloj2 = self.proEndTime.time()
        startTime = str(reloj1.hour()) + ":" + str(reloj1.minute()) + ":" + str(reloj1.second())
        endTime = str(reloj2.hour()) + ":" + str(reloj2.minute()) + ":" + str(reloj2.second())
        
        return  project_name, desc, datatype, data_path, starDate, endDate, startTime, endTime, online, delay, walk , set 

    def removefromtree(self, row):
        self.parentItem.removeRow(row)

    
    def setInputsProject_View(self):
        self.tabWidgetProject.setEnabled(True)
        self.tabWidgetProject.setCurrentWidget(self.tabProject)
        self.tabProject.setEnabled(True)
        self.frame_2.setEnabled(False)      
        self.proName.clear()
        self.proName.setFocus()
        self.proName.setSelection(0, 0)
        self.proName.setCursorPosition(0)
        self.proDataType.setText('.r')
        self.proDataPath.clear()
        self.proComDataType.clear()
        self.proComDataType.addItem("Voltage")
        self.proComDataType.addItem("Spectra")
        self.proComDataType.addItem("Fits")
        
        self.proComStartDate.clear()
        self.proComEndDate.clear()
        
        startTime = "00:00:00"
        endTime = "23:59:59"
        starlist = startTime.split(":")
        endlist = endTime.split(":")
        self.proDelay.setText("0")
        self.proSet.setText("0")
        self.time.setHMS(int(starlist[0]), int(starlist[1]), int(starlist[2])) 
        self.proStartTime.setTime(self.time)
        self.time.setHMS(int(endlist[0]), int(endlist[1]), int(endlist[2])) 
        self.proEndTime.setTime(self.time)
        self.proDescription.clear()    
        self.proOk.setEnabled(False)
        self.console.clear()
#         self.console.append("Please, Write a name Project")
#         self.console.append("Introduce Project Parameters")DC
#         self.console.append("Select data type Voltage( .rawdata)  or Spectra(.pdata)")
    
    def setInputsPU_View(self, datatype):
        projectObjView = self.getSelectedProjectObj()
        idReadUnit = projectObjView.getReadUnitId()
        readUnitObj = projectObjView.getProcUnitObj(idReadUnit)
        
        if datatype == 'Voltage':
            self.volOpComChannels.setEnabled(False)
            self.volOpComHeights.setEnabled(False)
            self.volOpFilter.setEnabled(False)
            self.volOpComProfile.setEnabled(False)
            self.volOpComCode.setEnabled(False)
            self.volOpCohInt.setEnabled(False)
            self.volOpChannel.setEnabled(False)
            self.volOpHeights.setEnabled(False)
            self.volOpProfile.setEnabled(False)   
            self.volOpRadarfrequency.setEnabled(False)   
            self.volOpCebChannels.setCheckState(0)
            self.volOpCebRadarfrequency.setCheckState(0)
            self.volOpCebHeights.setCheckState(0)
            self.volOpCebFilter.setCheckState(0)
            self.volOpCebProfile.setCheckState(0)
            self.volOpCebDecodification.setCheckState(0)
            self.volOpCebCohInt.setCheckState(0)       
            
            self.volOpChannel.clear()
            self.volOpHeights.clear()
            self.volOpProfile.clear()
            self.volOpFilter.clear()
            self.volOpCohInt.clear()
            self.volOpRadarfrequency.clear()
        
        if datatype == 'Spectra':

            if readUnitObj.datatype == 'Spectra':
                self.specOpnFFTpoints.setEnabled(False)
                self.specOpProfiles.setEnabled(False)
                self.specOpippFactor.setEnabled(False)
            else:
                self.specOpnFFTpoints.setEnabled(True)
                self.specOpProfiles.setEnabled(True)
                self.specOpippFactor.setEnabled(True)
            
            self.specOpCebCrossSpectra.setCheckState(0)
            self.specOpCebChannel.setCheckState(0)
            self.specOpCebHeights.setCheckState(0)
            self.specOpCebIncoherent.setCheckState(0)
            self.specOpCebRemoveDC.setCheckState(0)
            self.specOpCebRemoveInt.setCheckState(0)
            self.specOpCebgetNoise.setCheckState(0)
            self.specOpCebRadarfrequency.setCheckState(0)
            
            self.specOpRadarfrequency.setEnabled(False) 
            self.specOppairsList.setEnabled(False)
            self.specOpChannel.setEnabled(False)
            self.specOpHeights.setEnabled(False)
            self.specOpIncoherent.setEnabled(False)
            self.specOpgetNoise.setEnabled(False)
            
            self.specOpRadarfrequency.clear() 
            self.specOpnFFTpoints.clear()
            self.specOpProfiles.clear()
            self.specOpippFactor.clear
            self.specOppairsList.clear()
            self.specOpChannel.clear()
            self.specOpHeights.clear()
            self.specOpIncoherent.clear()
            self.specOpgetNoise.clear()
            
            self.specGraphCebSpectraplot.setCheckState(0)
            self.specGraphCebCrossSpectraplot.setCheckState(0)
            self.specGraphCebRTIplot.setCheckState(0)
            self.specGraphCebRTInoise.setCheckState(0)
            self.specGraphCebCoherencmap.setCheckState(0)
            self.specGraphPowerprofile.setCheckState(0)
            
            self.specGraphSaveSpectra.setCheckState(0)
            self.specGraphSaveCross.setCheckState(0)
            self.specGraphSaveRTIplot.setCheckState(0)
            self.specGraphSaveRTInoise.setCheckState(0)
            self.specGraphSaveCoherencemap.setCheckState(0)
            self.specGraphSavePowerprofile.setCheckState(0)
            
            self.specGraphftpRTIplot.setCheckState(0)
            self.specGraphftpRTInoise.setCheckState(0)
            self.specGraphftpCoherencemap.setCheckState(0)
                     
            self.specGraphPath.clear()
            self.specGraphPrefix.clear()
            
            self.specGgraphftpratio.clear()
            
            self.specGgraphChannelList.clear()
            self.specGgraphFreq.clear()
            self.specGgraphHeight.clear()
            self.specGgraphDbsrange.clear()
            self.specGgraphmagnitud.clear()
            self.specGgraphTminTmax.clear()   
            self.specGgraphTimeRange.clear()  
            
        if datatype == 'SpectraHeis':
            self.specHeisOpCebIncoherent.setCheckState(0)
            self.specHeisOpIncoherent.setEnabled(False)
            self.specHeisOpIncoherent.clear()
            
            self.specHeisGraphCebSpectraplot.setCheckState(0)
            self.specHeisGraphCebRTIplot.setCheckState(0)
            
            self.specHeisGraphSaveSpectra.setCheckState(0)
            self.specHeisGraphSaveRTIplot.setCheckState(0)
            
            self.specHeisGraphftpSpectra.setCheckState(0)
            self.specHeisGraphftpRTIplot.setCheckState(0)
            
            self.specHeisGraphPath.clear()
            self.specHeisGraphPrefix.clear()
            self.specHeisGgraphChannelList.clear()
            self.specHeisGgraphXminXmax.clear()
            self.specHeisGgraphYminYmax.clear()
            self.specHeisGgraphTminTmax.clear()
            self.specHeisGgraphTimeRange.clear()
            self.specHeisGgraphftpratio.clear()   
            
            
            
              
                        
    def showtabPUCreated(self, datatype):
        if datatype == "Voltage":
            self.tabVoltage.setEnabled(True)
            self.tabProject.setEnabled(False)
            self.tabSpectra.setEnabled(False)
            self.tabCorrelation.setEnabled(False)
            self.tabSpectraHeis.setEnabled(False)
            self.tabWidgetProject.setCurrentWidget(self.tabVoltage)
            
        if datatype == "Spectra":
            self.tabVoltage.setEnabled(False)
            self.tabProject.setEnabled(False)
            self.tabSpectra.setEnabled(True)
            self.tabCorrelation.setEnabled(False)
            self.tabSpectraHeis.setEnabled(False)
            self.tabWidgetProject.setCurrentWidget(self.tabSpectra)
        if datatype == "SpectraHeis":
            self.tabVoltage.setEnabled(False)
            self.tabProject.setEnabled(False)
            self.tabSpectra.setEnabled(False)
            self.tabCorrelation.setEnabled(False)
            self.tabSpectraHeis.setEnabled(True)
            self.tabWidgetProject.setCurrentWidget(self.tabSpectraHeis)
    
            
    def searchData(self, data_path, ext, walk, expLabel=''):
        dateList = []
        fileList = []
        
        if walk == 0:
            files = os.listdir(data_path)
            for thisFile in files:
                thisExt = os.path.splitext(thisFile)[-1]
                if thisExt == ext:
                    fileList.append(thisFile)
            
            for thisFile in fileList:
                try:
                    year = int(thisFile[1:5])
                    doy = int(thisFile[5:8])
                    
                    date = datetime.date(year, 1, 1) + datetime.timedelta(doy - 1)
                    dateformat = date.strftime("%Y/%m/%d")
                    
                    if dateformat not in dateList:
                        dateList.append(dateformat)    
                except:
                    continue            
 # REVISION---------------------------------1               
        if walk == 1:
            
            dirList = os.listdir(data_path)
            
            dirList.sort()     
            
            dateList = []
            
            for thisDir in dirList:
                
                if not isRadarPath(thisDir):
                    self.console.clear()
                    self.console.append("Please, Choose the Correct Path")
                    self.proOk.setEnabled(False)
                    continue
                
                doypath = os.path.join(data_path, thisDir, expLabel)
                if not os.path.exists(doypath):
                    self.console.clear()
                    self.console.append("Please, Choose the Correct Path")
                    return 
                files = os.listdir(doypath)
                fileList = []
                
                for thisFile in files:
                    thisExt = os.path.splitext(thisFile)[-1]
                    if thisExt != ext:
                       self.console.clear()
                       self.console.append("There is no datatype selected in the Path Directory")
                       self.proOk.setEnabled(False)
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
                
                date = datetime.date(year, 1, 1) + datetime.timedelta(doy - 1)
                dateformat = date.strftime("%Y/%m/%d")
                dateList.append(dateformat)

        if len(dateList) > 0:
            self.proOk.setEnabled(True)
            return dateList
            
        
#         self.proOk.setEnabled(False)
        return None
    
    def checkInputsProject(self):
        """
        Check Inputs Project:
        - project_name
        - datatype
        - ext
        - data_path
        - readmode
        - delay
        - set
        - walk
        """
        parms_ok = True
        project_name = str(self.proName.text())
        if project_name == '' or project_name == None:
            outputstr = "Enter the Project Name"
            self.console.append(outputstr)
            parms_ok = False
            project_name = None
        
        datatype = str(self.proComDataType.currentText())
        if not(datatype in ['Voltage', 'Spectra', 'Fits']):
            outputstr = 'datatype = %s, this must be either Voltage, Spectra or SpectraHeis' % datatype
            self.console.append(outputstr)
            parms_ok = False
            datatype = None
        
        ext = str(self.proDataType.text())
        if not(ext in ['.r', '.pdata', '.fits']):
            outputstr = "extension files must be .r , .pdata or .fits"
            self.console.append(outputstr)
            parms_ok = False
            ext = None
        
        data_path = str(self.proDataPath.text())

        if data_path == '':
            outputstr = 'Datapath is empty'
            self.console.append(outputstr)
            parms_ok = False
            data_path = None
        
        if data_path != None: 
            if not os.path.exists(data_path):
                outputstr = 'Datapath:%s does not exists' % data_path
                self.console.append(outputstr)
                parms_ok = False
                data_path = None
        
        read_mode = str(self.proComReadMode.currentText())
        if not(read_mode in ['Online', 'Offline']):
            outputstr = 'Read Mode: %s, this must be either Online or Offline' % read_mode
            self.console.append(outputstr)
            parms_ok = False
            read_mode = None
        
        try:
            delay = int(str(self.proDelay.text()))
        except:
            outputstr = 'Delay: %s, this must be a integer number' % str(self.proName.text())
            self.console.append(outputstr)
            parms_ok = False
            delay = None
            
        try:
            set = int(str(self.proSet.text()))
        except:
            # outputstr = 'Set: %s, this must be a integer number' % str(self.proName.text())
            # self.console.append(outputstr)
            # parms_ok = False
            set = None
        
        walk_str = str(self.proComWalk.currentText())
        if walk_str == 'On Files':
            walk = 0
        elif walk_str == 'On Folder':
            walk = 1
        else:
            outputstr = 'Walk: %s, this must be either On Files or On Folders' % walk_str
            self.console.append(outputstr)
            parms_ok = False
            walk = None
        
        return parms_ok, project_name, datatype, ext, data_path, read_mode, delay, walk, set

    def checkInputsPUSave(self, datatype):
        """
        Check Inputs Spectra Save:
        - path
        - blocks Per File
        - sufix
        - dataformat
        """
        parms_ok = True
        
        if datatype == "Voltage":
            output_path = str(self.volOutputPath.text())
            blocksperfile = str(self.volOutputblocksperfile.text())
            profilesperblock = str(self.volOutputprofilesperblock.text())
             
        if datatype == "Spectra":
            output_path = str(self.specOutputPath.text())
            blocksperfile = str(self.specOutputblocksperfile.text())
            profilesperblock = str(self.specOutputprofileperblock.text())
            
        if datatype == "SpectraHeis":
            output_path = str(self.specHeisOutputPath.text())
            blocksperfile = str(self.specHeisOutputblocksperfile.text())
            metada = str(self.specHeisOutputMetada.text())
            
        if output_path == '':
            outputstr = 'Outputpath is empty'
            self.console.append(outputstr)
            parms_ok = False
            data_path = None
        
        if output_path != None: 
            if not os.path.exists(output_path):
                outputstr = 'OutputPath:%s does not exists' % output_path
                self.console.append(outputstr)
                parms_ok = False
                output_path = None
        
        
        try:
            profilesperblock = int(profilesperblock)
        except:
            if datatype == "Voltage":
                outputstr = 'Profilesperblock: %s, this must be a integer number' % str(self.volOutputprofilesperblock.text())
                self.console.append(outputstr)
                parms_ok = False
                profilesperblock = None

            elif datatype == "Spectra":
                outputstr = 'Profilesperblock: %s, this must be a integer number' % str(self.specOutputprofileperblock.text())
                self.console.append(outputstr)
                parms_ok = False
                profilesperblock = None
            
        try:
            blocksperfile = int(blocksperfile)
        except:
            if datatype == "Voltage":
                outputstr = 'Blocksperfile: %s, this must be a integer number' % str(self.volOutputblocksperfile.text())
            elif datatype == "Spectra":
                outputstr = 'Blocksperfile: %s, this must be a integer number' % str(self.specOutputblocksperfile.text())
            elif datatype == "SpectraHeis":
                outputstr = 'Blocksperfile: %s, this must be a integer number' % str(self.specHeisOutputblocksperfile.text())
        
            self.console.append(outputstr)
            parms_ok = False
            blocksperfile = None
            
        if datatype == "SpectraHeis":
            if metada == '':
                outputstr = 'Choose metada file'
                self.console.append(outputstr)
                parms_ok = False
            if metada != None: 
               if not  os.path.isfile(metada):
                    outputstr = 'Metadata:%s does not exists' % metada
                    self.console.append(outputstr)
                    parms_ok = False
                    output_path = None

        if datatype == "Voltage":
            return parms_ok, output_path, blocksperfile, profilesperblock        

             
        if datatype == "Spectra":
            return parms_ok, output_path, blocksperfile, profilesperblock        

            
        if datatype == "SpectraHeis":    
            return parms_ok, output_path, blocksperfile, metada      
    
    def loadDays(self, data_path, ext, walk):
        """
        Method to loads day
        """
        dateList = self.searchData(data_path, ext, walk)
        if dateList == None:
            self.console.clear()
            outputstr = "The path: %s is empty with file extension *%s" % (data_path, ext)
            self.console.append(outputstr)
            return
        
        self.dateList = dateList
        for thisDate in dateList:
            self.proComStartDate.addItem(thisDate)
            self.proComEndDate.addItem(thisDate)
        self.proComEndDate.setCurrentIndex(self.proComStartDate.count() - 1)
        
    def setWorkSpaceGUI(self, pathWorkSpace):
         self.pathWorkSpace = pathWorkSpace    
   
    """
    Comandos Usados en Console
    """
    def __del__(self):
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        
    def normalOutputWritten(self, text):
        self.console.append(text)        
        
                
    def setParameter(self):
        
        self.setWindowTitle("ROJ-Signal Chain")
        self.setWindowIcon(QtGui.QIcon("schainpy/gui/figure/adn.jpg"))
        sys.stdout = ShowMeConsole(textWritten=self.normalOutputWritten)
        # sys.stderr = ShowMeConsole(textWritten=self.normalOutputWritten)
        self.tabWidgetProject.setEnabled(False)
        self.tabVoltage.setEnabled(False)
        self.tabSpectra.setEnabled(False)
        self.tabCorrelation.setEnabled(False)
        self.frame_2.setEnabled(False)
        
        self.actionCreate.setShortcut('Ctrl+P')
        self.actionStart.setShortcut('Ctrl+R')
        self.actionSave.setShortcut('Ctrl+S')
        self.actionClose.setShortcut('Ctrl+Q')
        
        self.actionStarToolbar.setEnabled(True)
        self.actionPauseToolbar.setEnabled(False)
        self.actionStopToolbar.setEnabled(False)
        
        self.proName.clear()
        self.proDataPath.setText('')
        self.console.setReadOnly(True)
        self.console.append("Welcome to Signal Chain please Create a New Project")
        self.proStartTime.setDisplayFormat("hh:mm:ss")
        self.proDataType.setEnabled(False)
        self.time = QtCore.QTime()
        self.hour = 0
        self.min = 0
        self.sec = 0 
        self.proEndTime.setDisplayFormat("hh:mm:ss")
        startTime = "00:00:00"
        endTime = "23:59:59"
        starlist = startTime.split(":")
        endlist = endTime.split(":")
        self.time.setHMS(int(starlist[0]), int(starlist[1]), int(starlist[2])) 
        self.proStartTime.setTime(self.time)
        self.time.setHMS(int(endlist[0]), int(endlist[1]), int(endlist[2])) 
        self.proEndTime.setTime(self.time)
        self.proOk.setEnabled(False)
        # set model Project Explorer
        self.projectExplorerModel = QtGui.QStandardItemModel()
        self.projectExplorerModel.setHorizontalHeaderLabels(("Project Explorer",))
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.projectExplorerTree)
        self.projectExplorerTree.setModel(self.projectExplorerModel)
        self.projectExplorerTree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.projectExplorerTree.customContextMenuRequested.connect(self.on_right_click)
        self.projectExplorerTree.clicked.connect(self.on_click)
        self.projectExplorerTree.expandAll()
        # set model Project Properties
        
        self.propertiesModel = treeModel()
        self.propertiesModel.initProjectView()
        self.treeProjectProperties.setModel(self.propertiesModel)
        self.treeProjectProperties.expandAll()
        self.treeProjectProperties.allColumnsShowFocus()
        self.treeProjectProperties.resizeColumnToContents(1)
   
        # set Project
        self.proDelay.setEnabled(False)  
        self.proSet.setEnabled(False)
        self.proDataType.setReadOnly(True)
         
         # set Operation Voltage
        self.volOpComChannels.setEnabled(False)
        self.volOpComHeights.setEnabled(False)
        self.volOpFilter.setEnabled(False)
        self.volOpComProfile.setEnabled(False)
        self.volOpComCode.setEnabled(False)
        self.volOpCohInt.setEnabled(False)
        self.volOpRadarfrequency.setEnabled(False)
        
        self.volOpChannel.setEnabled(False)
        self.volOpHeights.setEnabled(False)
        self.volOpProfile.setEnabled(False)
        self.volOpComMode.setEnabled(False)
        
        self.volGraphPath.setEnabled(False)
        self.volGraphPrefix.setEnabled(False)
        self.volGraphToolPath.setEnabled(False)
        
        # set Graph Voltage
        self.volGraphChannelList.setEnabled(False)
        self.volGraphfreqrange.setEnabled(False)
        self.volGraphHeightrange.setEnabled(False)
        
        # set Operation Spectra
        self.specOpnFFTpoints.setEnabled(False)
        self.specOpProfiles.setEnabled(False)
        self.specOpippFactor.setEnabled(False)
        self.specOppairsList.setEnabled(False)
        self.specOpComChannel.setEnabled(False)
        self.specOpComHeights.setEnabled(False)
        self.specOpIncoherent.setEnabled(False)
        self.specOpgetNoise.setEnabled(False)
        self.specOpRadarfrequency.setEnabled(False)
        
        
        self.specOpChannel.setEnabled(False)
        self.specOpHeights.setEnabled(False)
        # set Graph Spectra  
        self.specGgraphChannelList.setEnabled(False)
        self.specGgraphFreq.setEnabled(False)
        self.specGgraphHeight.setEnabled(False)
        self.specGgraphDbsrange.setEnabled(False)
        self.specGgraphmagnitud.setEnabled(False)
        self.specGgraphTminTmax.setEnabled(False)
        self.specGgraphTimeRange.setEnabled(False)
        self.specGraphPath.setEnabled(False)
        self.specGraphToolPath.setEnabled(False)
        self.specGraphPrefix.setEnabled(False)
        
        self.specGgraphftpratio.setEnabled(False)
        # set Operation SpectraHeis
        self.specHeisOpIncoherent.setEnabled(False)
        self.specHeisOpCobIncInt.setEnabled(False)
        # set Graph SpectraHeis
        self.specHeisGgraphChannelList.setEnabled(False)
        self.specHeisGgraphXminXmax.setEnabled(False)
        self.specHeisGgraphYminYmax.setEnabled(False)
        self.specHeisGgraphTminTmax.setEnabled(False)
        self.specHeisGgraphTimeRange.setEnabled(False)
        self.specHeisGgraphftpratio.setEnabled(False)
        self.specHeisGraphPath.setEnabled(False)
        self.specHeisGraphPrefix.setEnabled(False)
        self.specHeisGraphToolPath.setEnabled(False)
        
        
        # tool tip gui
        QtGui.QToolTip.setFont(QtGui.QFont('SansSerif', 10))
        self.projectExplorerTree.setToolTip('Right clik to add Project or Unit Process')
        # tool tip gui project
        self.proComWalk.setToolTip('<b>On Files</b>:<i>Search file in format .r or pdata</i> <b>On Folders</b>:<i>Search file in a directory DYYYYDOY</i>')
        self.proComWalk.setCurrentIndex(0)
        # tool tip gui volOp
        self.volOpChannel.setToolTip('Example: 1,2,3,4,5')    
        self.volOpHeights.setToolTip('Example: 90,180')
        self.volOpFilter.setToolTip('Example: 3')
        self.volOpProfile.setToolTip('Example:0,125 ')
        self.volOpCohInt.setToolTip('Example: 100')
        self.volOpOk.setToolTip('If you have finish, please Ok ')
        # tool tip gui volGraph
        self.volGraphfreqrange.setToolTip('Example: 10,150')
        self.volGraphHeightrange.setToolTip('Example: 20,180')
        # tool tip gui specOp
        self.specOpnFFTpoints.setToolTip('Example: 100')
        self.specOpProfiles.setToolTip('Example: 100')
        self.specOpippFactor.setToolTip('Example:1')
        self.specOpIncoherent.setToolTip('Example: 150')
        self.specOpgetNoise.setToolTip('Example:20,180,30,120 (minHei,maxHei,minVel,maxVel)')
        
        self.specOpChannel.setToolTip('Example: 1,2,3,4,5')
        self.specOpHeights.setToolTip('Example: 90,180')
        self.specOppairsList.setToolTip('Example: (0,1),(2,3)')
        # tool tip gui specGraph
        
        self.specGgraphChannelList.setToolTip('Example: Myplot')
        self.specGgraphFreq.setToolTip('Example: 10,150')
        self.specGgraphHeight.setToolTip('Example: 20,160')
        self.specGgraphDbsrange.setToolTip('Example: 30,170')

        self.specGraphPrefix.setToolTip('Example: figure')   
        
class UnitProcessWindow(QMainWindow, Ui_UnitProcess):
    """
    Class documentation goes here.
    """
    closed = pyqtSignal()
    create = False
    
    def __init__(self, parent=None):
        """
        Constructor
        """
        QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.getFromWindow = None
        self.getfromWindowList = []
        self.dataTypeProject = None
 
        self.listUP = None    
        
    @pyqtSignature("")
    def on_unitPokbut_clicked(self):
        """
        Slot documentation goes here.
        """
        self.create = True
        self.getFromWindow = self.getfromWindowList[int(self.comboInputBox.currentIndex())]
        # self.nameofUP= str(self.nameUptxt.text())
        self.typeofUP = str(self.comboTypeBox.currentText())
        self.close()

    
    @pyqtSignature("")
    def on_unitPcancelbut_clicked(self):
        """
        Slot documentation goes here.
        """
        self.create = False
        self.close()
        
    def loadTotalList(self):
        self.comboInputBox.clear()
        for i in self.getfromWindowList:
            
            name = i.getElementName()
            if name == 'Project':
                id = i.id
                name = i.name
                if self.dataTypeProject == 'Voltage':
                    self.comboTypeBox.clear()
                    self.comboTypeBox.addItem("Voltage")

                if self.dataTypeProject == 'Spectra':
                    self.comboTypeBox.clear()
                    self.comboTypeBox.addItem("Spectra")
                    self.comboTypeBox.addItem("Correlation")
                if self.dataTypeProject == 'Fits': 
                    self.comboTypeBox.clear()
                    self.comboTypeBox.addItem("SpectraHeis")
                
            
            if name == 'ProcUnit':
               id = int(i.id) - 1 
               name = i.datatype
               if name == 'Voltage':
                  self.comboTypeBox.clear()
                  self.comboTypeBox.addItem("Spectra")
                  self.comboTypeBox.addItem("SpectraHeis")
                  self.comboTypeBox.addItem("Correlation")
               if name == 'Spectra':
                  self.comboTypeBox.clear()
                  self.comboTypeBox.addItem("Spectra")
                  self.comboTypeBox.addItem("SpectraHeis")
                  self.comboTypeBox.addItem("Correlation")
               if name == 'SpectraHeis':
                  self.comboTypeBox.clear()
                  self.comboTypeBox.addItem("SpectraHeis")
                   
            self.comboInputBox.addItem(str(name))    
           # self.comboInputBox.addItem(str(name)+str(id))    

    def closeEvent(self, event):
        self.closed.emit()
        event.accept()
        
class Ftp(QMainWindow, Ui_Ftp):
    """
    Class documentation goes here.
    """
    create = False
    closed = pyqtSignal()
    server = None
    folder = None
    username = None
    password = None
    ftp_wei = None
    exp_code = None
    sub_exp_code = None
    plot_pos = None 
    
    def __init__(self, parent=None):
        """
        Constructor
        """
        QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.setParameter()
        
    def setParameter(self):
        self.setWindowTitle("ROJ-Signal Chain")
        self.serverFTP.setToolTip('Example: jro-app.igp.gob.pe')    
        self.folderFTP.setToolTip('Example: /home/wmaster/graficos')
        self.usernameFTP.setToolTip('Example: operator')
        self.passwordFTP.setToolTip('Example: mst2010vhf ')
        self.weightFTP.setToolTip('Example: 0')
        self.expcodeFTP.setToolTip('Example: 0')
        self.subexpFTP.setToolTip('Example: 0')
        self.plotposFTP.setToolTip('Example: 0')
        
    def setParmsfromTemporal(self, server, folder, username, password, ftp_wei, exp_code, sub_exp_code, plot_pos):
        self.serverFTP.setText(str(server))
        self.folderFTP.setText(str(folder))
        self.usernameFTP.setText(str(username))
        self.passwordFTP.setText(str(password))
        self.weightFTP.setText(str(ftp_wei))
        self.expcodeFTP.setText(str(exp_code))
        self.subexpFTP.setText(str(sub_exp_code))
        self.plotposFTP.setText(str(plot_pos))   
        
    def getParmsFromFtpWindow(self):
        """
        Return Inputs Project:
        - server
        - folder
        - username
        - password
        - ftp_wei
        - exp_code
        - sub_exp_code
        - plot_pos
        """
        name_server_ftp = str(self.serverFTP.text())
        try:
           name = str(self.serverFTP.text())
        except:
            self.console.clear()
            self.console.append("Please Write  a FTP Server")
            return 0     
        
        folder_server_ftp = str(self.folderFTP.text())
        try:
           folder = str(self.folderFTP.text())
        except:
            self.console.clear()
            self.console.append("Please Write  a Folder")
            return 0  
        
        username_ftp = str(self.usernameFTP.text())
        try:
           username = str(self.usernameFTP.text())
        except:
            self.console.clear()
            self.console.append("Please Write  a User Name")
            return 0   
    
        password_ftp = str(self.passwordFTP.text())
        try:
           password = str(self.passwordFTP.text())
        except:
            self.console.clear()
            self.console.append("Please Write  a passwordFTP")
            return 0
        
        ftp_wei = self.weightFTP.text()
        if not ftp_wei == "":
            try:
               ftp_wei = int(self.weightFTP.text())
            except:
                self.console.clear()
                self.console.append("Please Write  a ftp_wei number")
                return 0
        
        exp_code = self.expcodeFTP.text()
        if not exp_code == "":
            try:
               exp_code = int(self.expcodeFTP.text())
            except:
                self.console.clear()
                self.console.append("Please Write  a  exp_code number")
                return 0
        
        
        sub_exp_code = self.subexpFTP.text()
        if not sub_exp_code == "":
            try:
               sub_exp_code = int(self.subexpFTP.text())
            except:
                self.console.clear()
                self.console.append("Please Write  a  sub_exp_code number")
                return 0
        
        plot_pos = self.plotposFTP.text()
        if not plot_pos == "":
            try:
               plot_pos = int(self.plotposFTP.text())
            except:
                self.console.clear()
                self.console.append("Please Write  a  plot_pos number")
                return 0    
         
        return  name_server_ftp, folder_server_ftp, username_ftp, password_ftp, ftp_wei, exp_code, sub_exp_code, plot_pos

    @pyqtSignature("")       
    def on_ftpOkButton_clicked(self):
        server, folder, username, password, ftp_wei, exp_code, sub_exp_code, plot_pos = self.getParmsFromFtpWindow()
        self.create = True
        self.close()
        
    @pyqtSignature("")
    def on_ftpCancelButton_clicked(self):
        self.create = False
        self.close()
    
    def closeEvent(self, event):
        self.closed.emit()
        event.accept()
        
class ftpBuffer():
    server = None
    folder = None
    username = None
    password = None
    ftp_wei = None
    exp_code = None
    sub_exp_code = None
    plot_pos = None
    create = False
    withoutconfig = False
    createforView = False
    
    
    def __init__(self):
        self.server = None
        self.folder = None
        self.username = None
        self.password = None
        self.ftp_wei = None
        self.exp_code = None
        self.sub_exp_code = None
        self.plot_pos = None
        # self.create = False
        
    def setwithoutconfiguration(self):
        self.server = "jro-app.igp.gob.pe"
        self.folder = "/home/wmaster/graficos"
        self.username = "operator"
        self.password = "mst2010vhf"
        self.ftp_wei = "0"
        self.exp_code = "0"
        self.sub_exp_code = "0"
        self.plot_pos = "0"
        self.withoutconfig = True
        
    def save(self, server, folder, username, password, ftp_wei, exp_code, sub_exp_code, plot_pos):
        self.server = server
        self.folder = folder
        self.username = username
        self.password = password
        self.ftp_wei = ftp_wei
        self.exp_code = exp_code
        self.sub_exp_code = sub_exp_code
        self.plot_pos = plot_pos
        self.create = True
        self.withoutconfig = False 
        self.createforView = True 
           
        
    def recover(self):
        return self.server, self.folder, self.username, self.password, self.ftp_wei, self.exp_code, self.sub_exp_code, self.plot_pos  

class ShowMeConsole(QtCore.QObject):
        textWritten = QtCore.pyqtSignal(str)
        def write (self, text):
            self.textWritten.emit(str(text))

class PlotManager():
    def __init__(self, queue):
        self.queue = queue
        self.objPlotDict = {}

    def processIncoming(self):
        while self.queue.qsize():
            try:
                dataFromQueue = self.queue.get(True)
                if dataFromQueue == None:
                    continue
                 
                dataPlot = dataFromQueue['data']
                kwargs = dataFromQueue['kwargs']                 
                id = kwargs['id']
                if 'channelList' in kwargs.keys():
                    channelList = kwargs['channelList']
                else:
                    channelList = None
                plotname = kwargs.pop('type')

                if not(id in self.objPlotDict.keys()):
                    className = eval(plotname)
                    self.objPlotDict[id] = className(id, channelList, dataPlot)
                    self.objPlotDict[id].show()
                      
                self.objPlotDict[id].run(dataPlot , **kwargs)
   
            except Queue.Empty:
                pass
            
            
