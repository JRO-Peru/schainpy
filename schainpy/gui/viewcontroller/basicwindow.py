# -*- coding: utf-8 -*-
"""
Module implementing MainWindow.
#+++++++++++++GUI V1++++++++++++++#
@author: AlexanderValdezPortocarrero ñ_ñ
"""
import os, sys, time
import datetime
import numpy
import Queue

from collections import OrderedDict
from os.path import  expanduser
from time import sleep
# from gevent import sleep

import ast

from PyQt4.QtGui           import QMainWindow 
from PyQt4.QtCore          import pyqtSignature
from PyQt4.QtCore          import pyqtSignal
from PyQt4                 import QtCore
from PyQt4                 import QtGui
# from PyQt4.QtCore          import QThread
# from PyQt4.QtCore          import QObject, SIGNAL

from schainpy.gui.viewer.ui_unitprocess import Ui_UnitProcess
from schainpy.gui.viewer.ui_ftp      import Ui_Ftp
from schainpy.gui.viewer.ui_mainwindow  import Ui_BasicWindow
from schainpy.controller_api import ControllerThread
from schainpy.controller  import Project

from propertiesViewModel  import TreeModel, PropertyBuffer
from parametersModel import ProjectParms

from schainpy.gui.figures import tools

FIGURES_PATH = tools.get_path()
TEMPORAL_FILE = ".temp.xml"

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
        
        self.dataPath = None
        self.online = 0
        self.walk = 0
        self.create = False
        self.selectedItemTree = None
        self.controllerThread = None
#         self.commCtrlPThread = None
#         self.create_figure()
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
        
        self.__puLocalFolder2FTP = {}
        self.__enable = False
        
#         self.create_comm() 
        self.create_updating_timer()
        self.setGUIStatus()
        
    @pyqtSignature("")
    def on_actionOpen_triggered(self):
        """
        Slot documentation goes here.
        """ 
        self.openProject()  
              
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
    def on_actionStart_triggered(self):
        """
        """
        self.playProject()
    
    @pyqtSignature("")   
    def on_actionPause_triggered(self):
        """
        """
        self.pauseProject()
        
    @pyqtSignature("")   
    def on_actionStop_triggered(self):
        """
        """
        self.stopProject()
    
    @pyqtSignature("")   
    def on_actionAbout_triggered(self):
        """
        """
        self.aboutEvent()
              
    @pyqtSignature("")     
    def on_actionFTP_triggered(self):
        """
        """
        self.configFTPWindowObj = Ftp(self)
        
        if not self.temporalFTP.create:
            self.temporalFTP.setwithoutconfiguration()
            
        self.configFTPWindowObj.setParmsfromTemporal(self.temporalFTP.server,
                                                     self.temporalFTP.remotefolder,
                                                     self.temporalFTP.username,
                                                     self.temporalFTP.password,
                                                     self.temporalFTP.ftp_wei,
                                                     self.temporalFTP.exp_code,
                                                     self.temporalFTP.sub_exp_code,
                                                     self.temporalFTP.plot_pos)
        
        self.configFTPWindowObj.show()
        self.configFTPWindowObj.closed.connect(self.createFTPConfig)
        
    def createFTPConfig(self):
        
        if not self.configFTPWindowObj.create:
            self.console.clear()
            self.console.append("There is no FTP configuration")
            return
        
        self.console.append("Push Ok in Spectra view to Add FTP Configuration")
        
        server, remotefolder, username, password, ftp_wei, exp_code, sub_exp_code, plot_pos = self.configFTPWindowObj.getParmsFromFtpWindow()
        self.temporalFTP.save(server=server,
                              remotefolder=remotefolder,
                              username=username,
                              password=password,
                              ftp_wei=ftp_wei,
                              exp_code=exp_code,
                              sub_exp_code=sub_exp_code,
                              plot_pos=plot_pos)  
        
    @pyqtSignature("")
    def on_actionOpenToolbar_triggered(self):
        """
        Slot documentation goes here.
        """
        self.openProject()
                
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

    @pyqtSignature("")    
    def on_actionPauseToolbar_triggered(self):
        
        self.pauseProject()
        
    @pyqtSignature("")
    def on_actionStopToolbar_triggered(self):
        """
        Slot documentation goes here.
        """
        self.stopProject()
        
    @pyqtSignature("int")
    def on_proComReadMode_activated(self, index):
        """
        SELECCION DEL MODO DE LECTURA ON=1, OFF=0
        """
        if index == 0:
           self.online = 0 
           self.proDelay.setText("0")
           self.proSet.setText("")
           self.proSet.setEnabled(False)
           self.proDelay.setEnabled(False)
        elif index == 1:
            self.online = 1
            self.proSet.setText("")
            self.proDelay.setText("5")
            self.proSet.setEnabled(True)
            self.proDelay.setEnabled(True) 

    @pyqtSignature("int")
    def on_proComDataType_activated(self, index):
        """
        Voltage or Spectra
        """
        self.labelSet.show()
        self.proSet.show()
        
        self.labExpLabel.show()
        self.proExpLabel.show()
        
        self.labelIPPKm.hide()
        self.proIPPKm.hide()
        
        if index == 0:
            extension = '.r'
        elif index == 1:
            extension = '.pdata'
        elif index == 2:
            extension = '.fits'
        elif index == 3:
            extension = '.hdf5'
            
            self.labelIPPKm.show()
            self.proIPPKm.show()
            
            self.labelSet.hide()
            self.proSet.hide()
            
            self.labExpLabel.hide()
            self.proExpLabel.hide()
            
        self.proDataType.setText(extension)

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
        
        current_dpath = './'
        if self.dataPath:
            current_dpath = self.dataPath
        
        datapath = str(QtGui.QFileDialog.getExistingDirectory(self, 'Open Directory', current_dpath, QtGui.QFileDialog.ShowDirsOnly))
        
        #If it was canceled
        if not datapath:
            return
        
        #If any change was done
        if datapath == self.dataPath:
            return
        
        self.proDataPath.setText(datapath)
        
        self.actionStart.setEnabled(False)
        self.actionStarToolbar.setEnabled(False)
        self.proOk.setEnabled(False)
        
        self.proComStartDate.clear()
        self.proComEndDate.clear()
        
        if not os.path.exists(datapath):
            
            self.console.clear()
            self.console.append("Write a valid path")
            return
        
        self.dataPath = datapath
        
        self.console.clear()
        self.console.append("Select the read mode and press 'load button'")
        
          
    @pyqtSignature("")
    def on_proLoadButton_clicked(self):             
        
        self.console.clear()
        
        parameter_list = self.checkInputsProject()
        
        if not parameter_list[0]:
            return
        
        parms_ok, project_name, datatype, ext, data_path, read_mode, delay, walk, set, expLabel = parameter_list
        
        if read_mode == "Offline":
            self.proComStartDate.clear()
            self.proComEndDate.clear()
            self.proComStartDate.setEnabled(True)
            self.proComEndDate.setEnabled(True)
            self.proStartTime.setEnabled(True)
            self.proEndTime.setEnabled(True)
            self.frame_2.setEnabled(True)
                
        if read_mode == "Online":
            self.proComStartDate.addItem("1960/01/30")
            self.proComEndDate.addItem("2018/12/31")
            self.proComStartDate.setEnabled(False)
            self.proComEndDate.setEnabled(False)
            self.proStartTime.setEnabled(False)
            self.proEndTime.setEnabled(False)
            self.frame_2.setEnabled(True)
        
        self.loadDays(data_path, ext, walk, expLabel)
        
    @pyqtSignature("int")
    def on_proComStartDate_activated(self, index):
        """
        SELECCION DEL RANGO DE FECHAS -START DATE
        """
        stopIndex = self.proComEndDate.count() - self.proComEndDate.currentIndex() - 1
        
        self.proComEndDate.clear()
        for i in self.dateList[index:]:
            self.proComEndDate.addItem(i)
        
        if self.proComEndDate.count() - stopIndex - 1 >= 0:
            self.proComEndDate.setCurrentIndex(self.proComEndDate.count() - stopIndex - 1)
        else:
            self.proComEndDate.setCurrentIndex(self.proComEndDate.count() - 1)

    @pyqtSignature("int")
    def on_proComEndDate_activated(self, index):
        """
        SELECCION DEL RANGO DE FECHAS-END DATE
        """
        pass
    
    @pyqtSignature("")
    def on_proOk_clicked(self):
        """
        Añade al Obj XML de Projecto, name,datatype,date,time,readmode,wait,etc, crea el readUnitProcess del archivo xml.
        Prepara la configuración del diágrama del Arbol del treeView numero 2
        """
        
        self.actionStart.setEnabled(False)
        self.actionStarToolbar.setEnabled(False)
                           
        if self.create:
            
            projectId = self.__getNewProjectId()
            
            if not projectId:
                return 0
            
            projectObjView = self.createProjectView(projectId)
            
            if not projectObjView:
                return 0
            
            readUnitObj = self.createReadUnitView(projectObjView)
            
            if not readUnitObj:
                return 0
                       
        else:
            projectObjView = self.updateProjectView()

            if not projectObjView:
                return 0
            
            projectId = projectObjView.getId()
            idReadUnit = projectObjView.getReadUnitId()
            readUnitObj = self.updateReadUnitView(projectObjView, idReadUnit)
            
            if not readUnitObj:
                return 0
            
            self.__itemTreeDict[projectId].setText(projectObjView.name)
        # Project Properties
        self.refreshProjectProperties(projectObjView)
        # Disable tabProject after finish the creation
        
        self.actionStart.setEnabled(True)
        self.actionStarToolbar.setEnabled(True)
        self.console.clear()
        self.console.append("The project parameters were validated")
        
        return 1
        
    @pyqtSignature("")
    def on_proClear_clicked(self):
        
        self.console.clear()
        
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
    def on_volOpComProfile_activated(self, index):
        """
        Check Box habilita ingreso  del rango de Perfiles
        """
        #Profile List
        if  index == 0:
            self.volOpProfile.setToolTip('List of selected profiles. Example: 0, 1, 2, 3, 4, 5, 6, 7')
        
        #Profile Range
        if  index == 1:
            self.volOpProfile.setToolTip('Minimum and maximum profile index. Example: 0, 7')
        
        #Profile Range List
        if index == 2:
            self.volOpProfile.setToolTip('List of profile ranges. Example: (0, 7), (12, 19), (100, 200)')
        
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
    def on_volOpComCode_activated(self, index):
        """
        Check Box habilita ingreso
        """
        if  index == 13:
            self.volOpCode.setEnabled(True)
        else:
            self.volOpCode.setEnabled(False)
            
            if index == 0:
                code = ''
                self.volOpCode.setText(str(code))
                return
            
            if index == 1:
                code = '(1,1,-1)'
                nCode = '1'
                nBaud = '3'
            if index == 2:
                code = '(1,1,-1,1)'
                nCode = '1'
                nBaud = '4'
            if index == 3:
                code = '(1,1,1,-1,1)'
                nCode = '1'
                nBaud = '5'
            if index == 4:
                code = '(1,1,1,-1,-1,1,-1)'
                nCode = '1'
                nBaud = '7'
            if index == 5:
                code = '(1,1,1,-1,-1,-1,1,-1,-1,1,-1)'
                nCode = '1'
                nBaud = '11'
            if index == 6:
                code = '(1,1,1,1,1,-1,-1,1,1,-1,1,-1,1)'
                nCode = '1'
                nBaud = '13'
            if index == 7:
                code = '(1,1,-1,-1,-1,1)'
                nCode = '2'
                nBaud = '3'
            if index == 8:
                code = '(1,1,-1,1,-1,-1,1,-1)'
                nCode = '2'
                nBaud = '4'
            if index == 9:
                code = '(1,1,1,-1,1,-1,-1,-1,1,-1)'
                nCode = '2'
                nBaud = '5'
            if index == 10:
                code = '(1,1,1,-1,-1,1,-1,-1,-1,-1,1,1,-1,1)'
                nCode = '2'
                nBaud = '7'
            if index == 11:
                code = '(1,1,1,-1,-1,-1,1,-1,-1,1,-1,-1 ,-1 ,-1 ,1 ,1,1,-1 ,1 ,1 ,-1 ,1)'
                nCode = '2'
                nBaud = '11'
            if index == 12:
                code = '(1,1,1,1,1,-1,-1,1,1,-1,1,-1,1,-1,-1,-1,-1,-1,1,1,-1,-1,1,-1,1,-1)'
                nCode = '2'
                nBaud = '13'
                
            code = ast.literal_eval(code)
            nCode = int(nCode)
            nBaud = int(nBaud)
            
            code = numpy.asarray(code).reshape((nCode, nBaud)).tolist()
            
            self.volOpCode.setText(str(code))
            
    @pyqtSignature("int")
    def on_volOpCebFlip_stateChanged(self, p0):
        """
        Check Box habilita ingresode del numero de Integraciones a realizar
        """
        if  p0 == 2:
            self.volOpFlip.setEnabled(True)
        if  p0 == 0:
            self.volOpFlip.setEnabled(False)
            self.volOpFlip.clear()
                          
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
        
        filename = str(QtGui.QFileDialog.getOpenFileName(self, "Open text file", self.pathWorkSpace, self.tr("Text Files (*.xml)")))
        self.specHeisOutputMetada.setText(filename)
        
    @pyqtSignature("")
    def on_volOpOk_clicked(self):
        """
        BUSCA EN LA LISTA DE OPERACIONES DEL TIPO VOLTAJE Y LES A�ADE EL PARAMETRO ADECUADO ESPERANDO LA ACEPTACION DEL USUARIO
        PARA AGREGARLO AL ARCHIVO DE CONFIGURACION XML
        """   
        
        checkPath = False
        
        self.actionSaveToolbar.setEnabled(False)
        self.actionStarToolbar.setEnabled(False)
        
        puObj = self.getSelectedItemObj()
        puObj.removeOperations()
        
        if self.volOpCebRadarfrequency.isChecked():
            value = str(self.volOpRadarfrequency.text())
            format = 'float'
            name_operation = 'setRadarFrequency'
            name_parameter = 'frequency'
            if not value == "":
                try:
                    radarfreq = float(self.volOpRadarfrequency.text())*1e6
                except:
                    self.console.clear()
                    self.console.append("Write the parameter Radar Frequency  type float")
                    return 0
                opObj = puObj.addOperation(name=name_operation)
                opObj.addParameter(name=name_parameter, value=radarfreq, format=format)
        
        if self.volOpCebChannels.isChecked():
            value = str(self.volOpChannel.text())
            
            if value == "":
                print "Please fill channel list"
                return 0
            
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
           value = str(self.volOpHeights.text())
           
           if value == "":
                print "Please fill height range"
                return 0
            
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
           value = str(self.volOpFilter.text())
           if value == "":
                print "Please fill filter value"
                return 0
            
           format = 'int'
           name_operation = 'filterByHeights'
           name_parameter = 'window'
           opObj = puObj.addOperation(name=name_operation)
           opObj.addParameter(name=name_parameter, value=value, format=format)  

        if self.volOpCebProfile.isChecked():
            value = str(self.volOpProfile.text())
            
            if value == "":
                print "Please fill profile value"
                return 0
            
            format = 'intlist'
            optype = 'other'
            name_operation = 'ProfileSelector'
            if self.volOpComProfile.currentIndex() == 0:
                name_parameter = 'profileList'
            if self.volOpComProfile.currentIndex() == 1:
                name_parameter = 'profileRangeList'
            if self.volOpComProfile.currentIndex() == 2:
                name_parameter = 'rangeList'
                
            opObj = puObj.addOperation(name='ProfileSelector', optype='other')
            opObj.addParameter(name=name_parameter, value=value, format=format)  
        
        if self.volOpCebDecodification.isChecked():

            if self.volOpComMode.currentIndex() == 0:
                mode = '0'
            if self.volOpComMode.currentIndex() == 1:
                mode = '1'
            if self.volOpComMode.currentIndex() == 2:
                mode = '2'
                    
            if self.volOpComCode.currentIndex() == 0:
                opObj = puObj.addOperation(name='Decoder', optype='other')
                opObj.addParameter(name='mode', value=mode, format='int')  
            else:
                #User defined
                code = str(self.volOpCode.text())
                try:
                    code_tmp = ast.literal_eval(code)
                except:
                    code_tmp = []
                
                if len(code_tmp) < 1:
                    self.console.append("Please fill the code value")
                    return 0
                
                if len(code_tmp) == 1 or type(code_tmp[0]) != int:
                    nBaud = len(code_tmp[0])
                    nCode = len(code_tmp)
                else:
                    nBaud = len(code_tmp)
                    nCode = 1
                    
                opObj = puObj.addOperation(name='Decoder', optype='other')  
            
                code = code.replace("(", "")
                code = code.replace(")", "")
                code = code.replace("[", "")
                code = code.replace("]", "")
                opObj.addParameter(name='code', value=code, format='intlist')
                opObj.addParameter(name='nCode', value=nCode, format='int')
                opObj.addParameter(name='nBaud', value=nBaud, format='int')  
                opObj.addParameter(name='mode', value=mode, format='int')  

        if self.volOpCebFlip.isChecked():
            name_operation = 'deFlip'
            optype = 'self'
            value = str(self.volOpFlip.text())
            name_parameter = 'channelList'
            format = 'intlist'
            
            opObj = puObj.addOperation(name=name_operation, optype=optype)
            if value:
                opObj.addParameter(name=name_parameter, value=value, format=format) 
                               
        if self.volOpCebCohInt.isChecked():
            name_operation = 'CohInt'
            optype = 'other'
            value = str(self.volOpCohInt.text())
            
            if value == "":
                print "Please fill number of coherent integrations"
                return 0
            
            name_parameter = 'n'
            format = 'float'
            
            opObj = puObj.addOperation(name=name_operation, optype=optype)
            opObj.addParameter(name=name_parameter, value=value, format=format) 

        if self.volGraphCebshow.isChecked():    
            name_operation = 'Scope'
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
#             opObj.addParameter(name=name_parameter, value=value, format=format)
            opObj.addParameter(name=name_parameter1, value=opObj.id, format=format1)
            
            channelList = str(self.volGraphChannelList.text()).replace(" ","")
            xvalue = str(self.volGraphfreqrange.text()).replace(" ","")
            yvalue = str(self.volGraphHeightrange.text()).replace(" ","")

            if channelList:
                opObj.addParameter(name='channelList', value=channelList, format='intlist')

            if xvalue:
                xvalueList = xvalue.split(',')
                try:
                   value0 = float(xvalueList[0])
                   value1 = float(xvalueList[1])  
                except:
                    return 0
                opObj.addParameter(name='xmin', value=value0, format='float')
                opObj.addParameter(name='xmax', value=value1, format='float')               
                
                
            if not yvalue == "":
               yvalueList = yvalue.split(",")
               try:
                   value0 = int(yvalueList[0])
                   value1 = int(yvalueList[1])
               except:
                    return 0
                
               opObj.addParameter(name='ymin', value=value0, format='int')
               opObj.addParameter(name='ymax', value=value1, format='int')
                   
            if self.volGraphCebSave.isChecked():
                checkPath = True
                opObj.addParameter(name='save', value='1', format='int')
                opObj.addParameter(name='figpath', value=self.volGraphPath.text(), format='str')
                value = str(self.volGraphPrefix.text()).replace(" ","")
                if value:
                   opObj.addParameter(name='figfile', value=value, format='str')

        localfolder = None
        if checkPath:
            localfolder = str(self.volGraphPath.text())
            if localfolder == '':
                self.console.clear()
                self.console.append("Graphic path should be defined")
                return 0
            
        # if something happend 
        parms_ok, output_path, blocksperfile, profilesperblock = self.checkInputsPUSave(datatype='Voltage')
        if parms_ok:
            name_operation = 'VoltageWriter'
            optype = 'other'
            name_parameter1 = 'path'
            name_parameter2 = 'blocksPerFile'
            name_parameter3 = 'profilesPerBlock'
            value1 = output_path
            value2 = blocksperfile
            value3 = profilesperblock
            format = "int"
            opObj = puObj.addOperation(name=name_operation, optype=optype)
            opObj.addParameter(name=name_parameter1, value=value1)
            opObj.addParameter(name=name_parameter2, value=value2, format=format)
            opObj.addParameter(name=name_parameter3, value=value3, format=format)
            
        self.console.clear()
        try:
            self.refreshPUProperties(puObj)
        except:
            self.console.append("Check input parameters")
            return 0
        
        self.console.append("If you want to save your project")
        self.console.append("click on your project name in the Tree Project Explorer")
        
        self.actionSaveToolbar.setEnabled(True)
        self.actionStarToolbar.setEnabled(True)
        
        return 1
    
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
        save_path = str(QtGui.QFileDialog.getExistingDirectory(self, 'Open Directory', './', QtGui.QFileDialog.ShowDirsOnly))
        self.volGraphPath.setText(save_path)
        
        if not os.path.exists(save_path):
            self.console.clear()
            self.console.append("Set a valid path")
            self.volGraphOk.setEnabled(False)
            return               
    
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
            
    @pyqtSignature("")
    def on_specOpOk_clicked(self):
        """
        AÑADE OPERACION SPECTRA
        """
        
        addFTP = False
        checkPath = False

        self.actionSaveToolbar.setEnabled(False)
        self.actionStarToolbar.setEnabled(False)
        
        projectObj = self.getSelectedProjectObj() 
        puObj = self.getSelectedItemObj()
        
        puObj.removeOperations()
        
        if self.specOpCebRadarfrequency.isChecked():
            value = self.specOpRadarfrequency.text()
            format = 'float'
            name_operation = 'setRadarFrequency'
            name_parameter = 'frequency'
            if not value == "":
                try:
                    radarfreq = float(self.specOpRadarfrequency.text())*1e6
                except:
                    self.console.clear()
                    self.console.append("Write the parameter Radar Frequency  type float")
                    return 0
                opObj = puObj.addOperation(name=name_operation)
                opObj.addParameter(name=name_parameter, value=radarfreq, format=format)
        
        inputId = puObj.getInputId()
        inputPuObj = projectObj.getProcUnitObj(inputId)
        
        if inputPuObj.datatype == 'Voltage' or inputPuObj.datatype == 'USRP':
            
            try:
                value = int(self.specOpnFFTpoints.text())
                puObj.addParameter(name='nFFTPoints', value=value, format='int')
            except:
                self.console.clear()
                self.console.append("Please write the number of FFT")
                return 0
            
            try:
                value1 = int(self.specOpProfiles.text())
                puObj.addParameter(name='nProfiles', value=value1, format='int')
            except:
                self.console.append("Please Write the number of Profiles")
                
            try:
                value2 = int(self.specOpippFactor.text())
                puObj.addParameter(name='ippFactor' , value=value2 , format='int')
            except:
                self.console.append("Please Write the Number of IppFactor")
            
                    
        if self.specOpCebCrossSpectra.isChecked():
            name_parameter = 'pairsList'
            format = 'pairslist'         
            value2 = self.specOppairsList.text()
            
            if value2 == "":
                print "Please fill the pairs list field"
                return 0
            
            puObj.addParameter(name=name_parameter, value=value2, format=format)
                                
        if self.specOpCebHeights.isChecked():
            value = str(self.specOpHeights.text())
            
            if value == "":
                print "Please fill height range"
                return 0
            
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
            value = str(self.specOpChannel.text())
            
            if value == "":
                print "Please fill channel list"
                return 0
            
            format = 'intlist'
            if self.specOpComChannel.currentIndex() == 0:
                name_operation = "selectChannels"
                name_parameter = 'channelList'
            else:
                name_operation = "selectChannelsByIndex" 
                name_parameter = 'channelIndexList'
                
            opObj = puObj.addOperation(name=name_operation)
            opObj.addParameter(name=name_parameter, value=value, format=format)
            
        if self.specOpCebIncoherent.isChecked():
            value = str(self.specOpIncoherent.text())
            
            if value == "":
                print "Please fill Incoherent integration value"
                return 0
               
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

        channelList = str(self.specGgraphChannelList.text()).replace(" ","")
        vel_range = str(self.specGgraphFreq.text()).replace(" ","")
        hei_range = str(self.specGgraphHeight.text()).replace(" ","")
        db_range = str(self.specGgraphDbsrange.text()).replace(" ","")
        
        trange = str(self.specGgraphTminTmax.text()).replace(" ","")
        magrange = str(self.specGgraphmagnitud.text()).replace(" ","")
        phaserange = str(self.specGgraphPhase.text()).replace(" ","")
#         timerange = str(self.specGgraphTimeRange.text()).replace(" ","")
        
        figpath = str(self.specGraphPath.text())
        figfile = str(self.specGraphPrefix.text()).replace(" ","")
        try:
            wrperiod = int(str(self.specGgraphftpratio.text()).replace(" ",""))
        except:
            wrperiod = None
        
        #-----Spectra Plot-----
        if self.specGraphCebSpectraplot.isChecked():
                         
            opObj = puObj.addOperation(name='SpectraPlot', optype='other')
            opObj.addParameter(name='id', value=opObj.id, format='int')      
            
            if not channelList == '':
               opObj.addParameter(name='channelList', value=channelList, format='intlist') 
           
            if not vel_range == '':
               xvalueList = vel_range.split(',')
               try:
                   value1 = float(xvalueList[0])
                   value2 = float(xvalueList[1])
               except:
                   self.console.clear()
                   self.console.append("Invalid velocity/frequency range")
                   return 0
               
               opObj.addParameter(name='xmin', value=value1, format='float')
               opObj.addParameter(name='xmax', value=value2, format='float')
               
            if not hei_range == '':
              yvalueList = hei_range.split(",")
              try:
                   value1 = float(yvalueList[0])
                   value2 = float(yvalueList[1])
              except:
                  self.console.clear()
                  self.console.append("Invalid height range")
                  return 0
              
              opObj.addParameter(name='ymin', value=value1, format='float')
              opObj.addParameter(name='ymax', value=value2, format='float') 
            
            if not db_range == '':
                zvalueList = db_range.split(",")
                try:
                   value1 = float(zvalueList[0])
                   value2 = float(zvalueList[1])
                except:
                   self.console.clear()
                   self.console.append("Invalid db range")
                   return 0
               
                opObj.addParameter(name='zmin', value=value1, format='float')
                opObj.addParameter(name='zmax', value=value2, format='float')      

            if self.specGraphSaveSpectra.isChecked():
                checkPath = True
                opObj.addParameter(name='save', value=1 , format='bool')
                opObj.addParameter(name='figpath', value=figpath, format='str')
                if figfile:
                    opObj.addParameter(name='figfile', value=figfile, format='str') 
                if wrperiod:
                    opObj.addParameter(name='wr_period', value=wrperiod,format='int')
                        
            if self.specGraphftpSpectra.isChecked():
               opObj.addParameter(name='ftp', value='1', format='int')
               self.addFTPConf2Operation(puObj, opObj)
               addFTP = True
               
        if self.specGraphCebCrossSpectraplot.isChecked():
            
            opObj = puObj.addOperation(name='CrossSpectraPlot', optype='other')
#             opObj.addParameter(name='power_cmap', value='jet', format='str')
#             opObj.addParameter(name='coherence_cmap', value='jet', format='str')
#             opObj.addParameter(name='phase_cmap', value='RdBu_r', format='str')
            opObj.addParameter(name='id', value=opObj.id, format='int')
            
            if not vel_range == '':
                xvalueList = vel_range.split(',')
                try:
                    value1 = float(xvalueList[0])
                    value2 = float(xvalueList[1])
                except:
                    self.console.clear()
                    self.console.append("Invalid velocity/frequency range")
                    return 0
                 
                opObj.addParameter(name='xmin', value=value1, format='float')
                opObj.addParameter(name='xmax', value=value2, format='float')

            if not hei_range == '':
                yvalueList = hei_range.split(",")
                try:
                     value1 = float(yvalueList[0])
                     value2 = float(yvalueList[1])
                except:
                    self.console.clear()
                    self.console.append("Invalid height range")
                    return 0
                 
                opObj.addParameter(name='ymin', value=value1, format='float')
                opObj.addParameter(name='ymax', value=value2, format='float')
        
            if not db_range == '':
                zvalueList = db_range.split(",")
                try:
                    value1 = float(zvalueList[0])
                    value2 = float(zvalueList[1])
                except:
                    self.console.clear()
                    self.console.append("Invalid db range")
                    return 0
                
                opObj.addParameter(name='zmin', value=value1, format='float')
                opObj.addParameter(name='zmax', value=value2, format='float')

            if not magrange == '':
                zvalueList = magrange.split(",")
                try:
                    value1 = float(zvalueList[0])
                    value2 = float(zvalueList[1])
                except:
                    self.console.clear()
                    self.console.append("Invalid magnitude range")
                    return 0
                
                opObj.addParameter(name='coh_min', value=value1, format='float')
                opObj.addParameter(name='coh_max', value=value2, format='float')
                
            if not phaserange == '':
                zvalueList = phaserange.split(",")
                try:
                    value1 = float(zvalueList[0])
                    value2 = float(zvalueList[1])
                except:
                    self.console.clear()
                    self.console.append("Invalid phase range")
                    return 0
                
                opObj.addParameter(name='phase_min', value=value1, format='float')
                opObj.addParameter(name='phase_max', value=value2, format='float')
                 
            if self.specGraphSaveCross.isChecked():
                checkPath = True
                opObj.addParameter(name='save', value='1', format='bool')
                opObj.addParameter(name='figpath', value=figpath, format='str')
                if figfile:
                   opObj.addParameter(name='figfile', value=figfile, format='str')
                if wrperiod:
                    opObj.addParameter(name='wr_period', value=wrperiod,format='int')
                    
            if self.specGraphftpCross.isChecked():
               opObj.addParameter(name='ftp', value='1', format='int')
               self.addFTPConf2Operation(puObj, opObj)
               addFTP = True
                     
        if self.specGraphCebRTIplot.isChecked():
            
            opObj = puObj.addOperation(name='RTIPlot', optype='other')
            opObj.addParameter(name='id', value=opObj.id, format='int')
            
            if not channelList == '':
                opObj.addParameter(name='channelList', value=channelList, format='intlist')
            
            if not trange == '':
                xvalueList = trange.split(',')
                try:
                    value1 = float(xvalueList[0])
                    value2 = float(xvalueList[1])
                except:
                    self.console.clear()
                    self.console.append("Invalid time range")
                    return 0
                    
                opObj.addParameter(name='xmin', value=value1, format='float')
                opObj.addParameter(name='xmax', value=value2, format='float')
            
#             if not timerange == '':
#                 try:
#                     timerange = float(timerange)
#                 except:
#                     self.console.clear()
#                     self.console.append("Invalid time range")
#                     return 0
#                 
#                 opObj.addParameter(name='timerange', value=timerange, format='float')
                
            if not hei_range == '':
                yvalueList = hei_range.split(",")
                try:
                    value1 = float(yvalueList[0])
                    value2 = float(yvalueList[1])
                except:
                    self.console.clear()
                    self.console.append("Invalid height range")
                    return 0
                    
                opObj.addParameter(name='ymin', value=value1, format='float')
                opObj.addParameter(name='ymax', value=value2, format='float')   
                        
            if not db_range == '':
                zvalueList = db_range.split(",")
                try:
                    value1 = float(zvalueList[0])
                    value2 = float(zvalueList[1])
                except:
                    self.console.clear()
                    self.console.append("Invalid db range")
                    return 0
                
                opObj.addParameter(name='zmin', value=value1, format='float')
                opObj.addParameter(name='zmax', value=value2, format='float')     
                
            if self.specGraphSaveRTIplot.isChecked():
                checkPath = True
                opObj.addParameter(name='save', value='1', format='bool')
                opObj.addParameter(name='figpath', value=figpath, format='str')
                if figfile:
                   opObj.addParameter(name='figfile', value=value, format='str')                
                if wrperiod:
                    opObj.addParameter(name='wr_period', value=wrperiod,format='int')
                    
            if self.specGraphftpRTIplot.isChecked():
               opObj.addParameter(name='ftp', value='1', format='int')
               self.addFTPConf2Operation(puObj, opObj)
               addFTP = True
                                 
        if self.specGraphCebCoherencmap.isChecked():
           
            opObj = puObj.addOperation(name='CoherenceMap', optype='other')
#             opObj.addParameter(name=name_parameter, value=value, format=format)
            # opObj.addParameter(name='coherence_cmap', value='jet', format='str')
            # opObj.addParameter(name='phase_cmap', value='RdBu_r', format='str')     
            opObj.addParameter(name='id', value=opObj.id, format='int')
            
#             if not timerange == '':
#                 try:
#                     timerange = int(timerange)
#                 except:
#                     self.console.clear()
#                     self.console.append("Invalid time range")
#                     return 0
#                 
#                 opObj.addParameter(name='timerange', value=timerange, format='int')
                
            if not trange == '':
                xvalueList = trange.split(',')
                try:
                    value1 = float(xvalueList[0])
                    value2 = float(xvalueList[1])
                except:
                    self.console.clear()
                    self.console.append("Invalid time range")
                    return 0
                
                opObj.addParameter(name='xmin', value=value1, format='float')
                opObj.addParameter(name='xmax', value=value2, format='float')  
            
            if not hei_range == '':
                yvalueList = hei_range.split(",")
                try:
                    value1 = float(yvalueList[0])
                    value2 = float(yvalueList[1])
                except:
                    self.console.clear()
                    self.console.append("Invalid height range")
                    return 0
                   
                opObj.addParameter(name='ymin', value=value1, format='float')
                opObj.addParameter(name='ymax', value=value2, format='float')   
                          
            if not magrange == '':
                zvalueList = magrange.split(",")
                try:
                    value1 = float(zvalueList[0])
                    value2 = float(zvalueList[1])
                except:
                    self.console.clear()
                    self.console.append("Invalid magnitude range")
                    return 0
                
                opObj.addParameter(name='zmin', value=value1, format='float')
                opObj.addParameter(name='zmax', value=value2, format='float')
            
            if not phaserange == '':
                zvalueList = phaserange.split(",")
                try:
                    value1 = float(zvalueList[0])
                    value2 = float(zvalueList[1])
                except:
                    self.console.clear()
                    self.console.append("Invalid phase range")
                    return 0
                
                opObj.addParameter(name='phase_min', value=value1, format='float')
                opObj.addParameter(name='phase_max', value=value2, format='float')
                
            if self.specGraphSaveCoherencemap.isChecked():
                checkPath = True
                opObj.addParameter(name='save', value='1', format='bool')
                opObj.addParameter(name='figpath', value=figpath, format='str')
                if figfile:
                   opObj.addParameter(name='figfile', value=value, format='str')
                if wrperiod:
                    opObj.addParameter(name='wr_period', value=wrperiod,format='int')
                    
            if self.specGraphftpCoherencemap.isChecked():
               opObj.addParameter(name='ftp', value='1', format='int')
               self.addFTPConf2Operation(puObj, opObj)       
               addFTP = True    
           
        if self.specGraphPowerprofile.isChecked():
            
           opObj = puObj.addOperation(name='PowerProfilePlot', optype='other')
           opObj.addParameter(name='id', value=opObj.id, format='int')
           
           if not channelList == '':
               opObj.addParameter(name='channelList', value=channelList, format='intlist') 
           
           if not db_range == '':
               xvalueList = db_range.split(',')
               try:
                    value1 = float(xvalueList[0])
                    value2 = float(xvalueList[1])
               except:
                    self.console.clear()
                    self.console.append("Invalid db range")
                    return 0
                
               opObj.addParameter(name='xmin', value=value1, format='float')
               opObj.addParameter(name='xmax', value=value2, format='float')     
  
           if not hei_range == '':
                yvalueList = hei_range.split(",")
                try:
                     value1 = float(yvalueList[0])
                     value2 = float(yvalueList[1])
                except:
                     self.console.clear()
                     self.console.append("Invalid height range")
                     return 0
                
                opObj.addParameter(name='ymin', value=value1, format='float')
                opObj.addParameter(name='ymax', value=value2, format='float')
 
           if self.specGraphSavePowerprofile.isChecked():
                checkPath = True
                opObj.addParameter(name='save', value='1', format='bool')
                opObj.addParameter(name='figpath', value=figpath, format='str')
                if figfile:
                   opObj.addParameter(name='figfile', value=value, format='str')
                if wrperiod:
                    opObj.addParameter(name='wr_period', value=wrperiod,format='int')
                
           if self.specGraphftpPowerprofile.isChecked():
              opObj.addParameter(name='ftp', value='1', format='int')
              self.addFTPConf2Operation(puObj, opObj)
              addFTP = True
           # rti noise
              
        if self.specGraphCebRTInoise.isChecked():
            
            opObj = puObj.addOperation(name='Noise', optype='other')
            opObj.addParameter(name='id', value=opObj.id, format='int')
            
            if not channelList == '':
                opObj.addParameter(name='channelList', value=channelList, format='intlist')
            
#             if not timerange == '':
#                 try:
#                     timerange = float(timerange)
#                 except:
#                     self.console.clear()
#                     self.console.append("Invalid time range")
#                     return 0
#                 
#                 opObj.addParameter(name='timerange', value=timerange, format='float')
                
            if not trange == '':
                xvalueList = trange.split(',')
                try:
                    value1 = float(xvalueList[0])
                    value2 = float(xvalueList[1])
                except:
                    self.console.clear()
                    self.console.append("Invalid time range")
                    return 0
                    
                opObj.addParameter(name='xmin', value=value1, format='float')
                opObj.addParameter(name='xmax', value=value2, format='float')
            
            if not db_range == '':
                yvalueList = db_range.split(",")
                try:
                    value1 = float(yvalueList[0])
                    value2 = float(yvalueList[1])
                except:
                    self.console.clear()
                    self.console.append("Invalid db range")
                    return 0
                
                opObj.addParameter(name='ymin', value=value1, format='float')
                opObj.addParameter(name='ymax', value=value2, format='float')      
                
            if self.specGraphSaveRTInoise.isChecked():
                checkPath = True
                opObj.addParameter(name='save', value='1', format='bool')
                opObj.addParameter(name='figpath', value=figpath, format='str')
                if figfile:
                   opObj.addParameter(name='figfile', value=value, format='str')                
                if wrperiod:
                    opObj.addParameter(name='wr_period', value=wrperiod,format='int')
                    
            # test_ftp
            if self.specGraphftpRTInoise.isChecked():
               opObj.addParameter(name='ftp', value='1', format='int')
               self.addFTPConf2Operation(puObj, opObj)    
               addFTP = True  
        
        if checkPath:
            if not figpath:
                self.console.clear()
                self.console.append("Graphic path should be defined")
                return 0
                
        if addFTP and not figpath:
                self.console.clear()
                self.console.append("You have to save the plots before sending them to FTP Server")
                return 0
        
#      if something happend 
        parms_ok, output_path, blocksperfile, profilesperblock = self.checkInputsPUSave(datatype='Spectra')
        if parms_ok:
            opObj = puObj.addOperation(name='SpectraWriter', optype='other')
            opObj.addParameter(name='path', value=output_path)
            opObj.addParameter(name='blocksPerFile', value=blocksperfile, format='int')
        
        self.console.clear()
        try:
            self.refreshPUProperties(puObj)
        except:
            self.console.append("Check input parameters")
            return 0
        
        self.console.append("If you want to save your project")
        self.console.append("click on your project name in the Tree Project Explorer")

        self.actionSaveToolbar.setEnabled(True)
        self.actionStarToolbar.setEnabled(True)
        
        return 1
    
    """
    Spectra  Graph
    """
    @pyqtSignature("int")
    def on_specGraphCebSpectraplot_stateChanged(self, p0):
        
        self.__checkSpecGraphFilters() 
            
            
    @pyqtSignature("int")
    def on_specGraphCebCrossSpectraplot_stateChanged(self, p0):
        
        self.__checkSpecGraphFilters()
            
    @pyqtSignature("int")
    def on_specGraphCebRTIplot_stateChanged(self, p0):
        
        self.__checkSpecGraphFilters()

    
    @pyqtSignature("int")
    def on_specGraphCebRTInoise_stateChanged(self, p0):
        
        self.__checkSpecGraphFilters()
            
             
    @pyqtSignature("int")
    def on_specGraphCebCoherencmap_stateChanged(self, p0):
        
        self.__checkSpecGraphFilters()
            
    @pyqtSignature("int")
    def on_specGraphPowerprofile_stateChanged(self, p0):
        
        self.__checkSpecGraphFilters()   
    
    @pyqtSignature("int")
    def on_specGraphPhase_stateChanged(self, p0):
        
        self.__checkSpecGraphFilters()
               
    @pyqtSignature("int")
    def on_specGraphSaveSpectra_stateChanged(self, p0):
        """
        """
        self.__checkSpecGraphSaving()
        
    @pyqtSignature("int")
    def on_specGraphSaveCross_stateChanged(self, p0):       
        
        self.__checkSpecGraphSaving()
        
    @pyqtSignature("int")
    def on_specGraphSaveRTIplot_stateChanged(self, p0):       
        
        self.__checkSpecGraphSaving()
            
    @pyqtSignature("int")
    def on_specGraphSaveRTInoise_stateChanged(self, p0):       
        
        self.__checkSpecGraphSaving()
            
    @pyqtSignature("int")
    def on_specGraphSaveCoherencemap_stateChanged(self, p0):       
        
        self.__checkSpecGraphSaving()
            
    @pyqtSignature("int")
    def on_specGraphSavePowerprofile_stateChanged(self, p0):       
        
        self.__checkSpecGraphSaving()
    
    @pyqtSignature("int")
    def on_specGraphftpSpectra_stateChanged(self, p0):
        """
        """
        self.__checkSpecGraphFTP()
            
            
    @pyqtSignature("int")
    def on_specGraphftpCross_stateChanged(self, p0):       
        
        self.__checkSpecGraphFTP()
        
    @pyqtSignature("int")
    def on_specGraphftpRTIplot_stateChanged(self, p0):       
        
        self.__checkSpecGraphFTP()
            
    @pyqtSignature("int")
    def on_specGraphftpRTInoise_stateChanged(self, p0):       
        
        self.__checkSpecGraphFTP()
            
    @pyqtSignature("int")
    def on_specGraphftpCoherencemap_stateChanged(self, p0):       
        
        self.__checkSpecGraphFTP()
            
    @pyqtSignature("int")
    def on_specGraphftpPowerprofile_stateChanged(self, p0):       
        
        self.__checkSpecGraphFTP()
               
    @pyqtSignature("")
    def on_specGraphToolPath_clicked(self):        
        """
        """
        save_path = str(QtGui.QFileDialog.getExistingDirectory(self, 'Open Directory', './', QtGui.QFileDialog.ShowDirsOnly))
        self.specGraphPath.setText(save_path)
        if not os.path.exists(save_path):
            self.console.clear()
            self.console.append("Write a valid path")
            return 
        
    @pyqtSignature("")
    def on_specGraphClear_clicked(self):
        return
    
    @pyqtSignature("")
    def on_specHeisGraphToolPath_clicked(self):        
        """
        """
        save_path = str(QtGui.QFileDialog.getExistingDirectory(self, 'Open Directory', './', QtGui.QFileDialog.ShowDirsOnly))
        self.specHeisGraphPath.setText(save_path)
        if not os.path.exists(save_path):
            self.console.clear()
            self.console.append("Write a valid path")
            return
        
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
        addFTP = False
        checkPath = False

        self.actionSaveToolbar.setEnabled(False)
        self.actionStarToolbar.setEnabled(False)
        
        puObj = self.getSelectedItemObj()
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
            name_operation = 'SpectraHeisScope'
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
#             opObj.addParameter(name=name_parameter, value=value, format=format)
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
                checkPath = True
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
               self.addFTPConf2Operation(puObj, opObj)
               addFTP = True
               
        if self.specHeisGraphCebRTIplot.isChecked():
            name_operation = 'RTIfromSpectraHeis'
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
#             opObj.addParameter(name=name_parameter, value=value, format=format)
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
                checkPath = True
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
               self.addFTPConf2Operation(puObj, opObj)
               addFTP = True

        localfolder = None
        if checkPath:
            localfolder = str(self.specGraphPath.text())
            if localfolder == '':
                self.console.clear()
                self.console.append("Graphic path should be defined")
                return 0
                
        if addFTP and not localfolder:
            self.console.clear()
            self.console.append("You should save plots before send them to FTP Server")
            return 0
            
        # if something happened
        parms_ok, output_path, blocksperfile, metada = self.checkInputsPUSave(datatype='SpectraHeis')
        if parms_ok:
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
            opObj = puObj.addOperation(name=name_operation, optype=optype)
            opObj.addParameter(name=name_parameter1, value=value1)
            opObj.addParameter(name=name_parameter2, value=value2, format=format2)
            opObj.addParameter(name=name_parameter3, value=value3, format=format3)

        self.console.clear()
        try:
            self.refreshPUProperties(puObj)
        except:
            self.console.append("Check input parameters")
            return 0
        
        self.console.append("Click on save icon ff you want to save your project")
        
        self.actionSaveToolbar.setEnabled(True)
        self.actionStarToolbar.setEnabled(True)
        
        return 1
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
    
    def __checkSpecGraphSaving(self):
        
        enable = False
            
        if self.specGraphSaveSpectra.checkState():
            enable = True
        
        if self.specGraphSaveCross.checkState():
            enable = True
        
        if self.specGraphSaveRTIplot.checkState():
            enable = True
        
        if self.specGraphSaveCoherencemap.checkState():
            enable = True
            
        if self.specGraphSavePowerprofile.checkState():
            enable = True
        
        if self.specGraphSaveRTInoise.checkState():
            enable = True
            
        self.specGraphPath.setEnabled(enable)
        self.specGraphPrefix.setEnabled(enable)
        self.specGraphToolPath.setEnabled(enable)
        
        self.specGgraphftpratio.setEnabled(enable)
        
    def __checkSpecGraphFTP(self):
        
        enable = False
        
        if self.specGraphftpSpectra.checkState():
            enable = True
        
        if self.specGraphftpCross.checkState():
            enable = True
        
        if self.specGraphftpRTIplot.checkState():
            enable = True
        
        if self.specGraphftpCoherencemap.checkState():
            enable = True
            
        if self.specGraphftpPowerprofile.checkState():
            enable = True
        
        if self.specGraphftpRTInoise.checkState():
            enable = True
            
#         self.specGgraphftpratio.setEnabled(enable)
        
    def __checkSpecGraphFilters(self):
        
        freq = False
        height = False
        db = False
        time = False
        magnitud = False
        phase = False
        channelList = False
        
        if self.specGraphCebSpectraplot.checkState():
            freq = True
            height = True
            db = True
            channelList = True
        
        if self.specGraphCebCrossSpectraplot.checkState():
            freq = True
            height = True
            db = True
            magnitud = True
            phase = True
        
        if self.specGraphCebRTIplot.checkState():
            height = True
            db = True
            time = True
            channelList = True
        
        if self.specGraphCebCoherencmap.checkState():
            height = True
            time = True
            magnitud = True
            phase = True
            
        if self.specGraphPowerprofile.checkState():
            height = True
            db = True
            channelList = True
        
        if self.specGraphCebRTInoise.checkState():
            db = True
            time = True
            channelList = True
            
        
        self.specGgraphFreq.setEnabled(freq)
        self.specGgraphHeight.setEnabled(height)
        self.specGgraphDbsrange.setEnabled(db)
        self.specGgraphTminTmax.setEnabled(time)
        
        self.specGgraphmagnitud.setEnabled(magnitud)
        self.specGgraphPhase.setEnabled(phase)
        self.specGgraphChannelList.setEnabled(channelList)
        
    def __getParmsFromProjectWindow(self):
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
            outputstr = "Enter a project Name"
            self.console.append(outputstr)
            parms_ok = False
            project_name = None
        
        description = str(self.proDescription.toPlainText())
        
        datatype = str(self.proComDataType.currentText())
        
        ext = str(self.proDataType.text())
        
        dpath = str(self.proDataPath.text())

        if dpath == '':
            outputstr = 'Datapath is empty'
            self.console.append(outputstr)
            parms_ok = False
            dpath = None
        
        if dpath != None: 
            if not os.path.isdir(dpath):
                outputstr = 'Datapath (%s) does not exist' % dpath
                self.console.append(outputstr)
                parms_ok = False
                dpath = None
        
        online = int(self.proComReadMode.currentIndex())
        
        delay = None
        if online==1:
            try:
                delay = int(str(self.proDelay.text()))
            except:
                outputstr = 'Delay value (%s) must be a integer number' %str(self.proDelay.text())
                self.console.append(outputstr)
                parms_ok = False
                
        
        set = None
        value = str(self.proSet.text())
        try:
            set = int(value)
        except:
            pass
        
        ippKm = None
        
        value = str(self.proIPPKm.text())
        
        try:
            ippKm = float(value)
        except:
            if datatype=="USRP":
                outputstr = 'IPP value (%s) must be a float number' % str(self.proIPPKm.text())
                self.console.append(outputstr)
                parms_ok = False
        
        walk = int(self.proComWalk.currentIndex())
        expLabel = str(self.proExpLabel.text())
        
        startDate = str(self.proComStartDate.currentText())
        endDate = str(self.proComEndDate.currentText())
        
#         startDateList = startDate.split("/")
#         endDateList = endDate.split("/")
#         
#         startDate = datetime.date(int(startDateList[0]), int(startDateList[1]), int(startDateList[2]))
#         endDate = datetime.date(int(endDateList[0]), int(endDateList[1]), int(endDateList[2]))
        
        startTime = self.proStartTime.time()
        endTime = self.proEndTime.time()
        
        startTime = str(startTime.toString("H:m:s"))
        endTime = str(endTime.toString("H:m:s"))

        projectParms = ProjectParms()
        
        projectParms.name = project_name
        projectParms.description = description
        projectParms.datatype = datatype
        projectParms.ext = ext
        projectParms.dpath = dpath
        projectParms.online = online
        projectParms.startDate = startDate
        projectParms.endDate = endDate
        projectParms.startTime = startTime
        projectParms.endTime = endTime
        projectParms.delay = delay
        projectParms.walk = walk
        projectParms.expLabel = expLabel
        projectParms.set = set
        projectParms.ippKm = ippKm
        projectParms.parmsOk = parms_ok
        
        return projectParms
        
    
    def __getParmsFromProjectObj(self, projectObjView):
        
        parms_ok = True
        
        project_name, description = projectObjView.name, projectObjView.description
        
        readUnitObj = projectObjView.getReadUnitObj()
        datatype = readUnitObj.datatype
        
        operationObj = readUnitObj.getOperationObj(name='run')
            
        dpath = operationObj.getParameterValue(parameterName='path')
        startDate = operationObj.getParameterValue(parameterName='startDate')
        endDate = operationObj.getParameterValue(parameterName='endDate')
        
        startDate = startDate.strftime("%Y/%m/%d")
        endDate = endDate.strftime("%Y/%m/%d")
        
        startTime = operationObj.getParameterValue(parameterName='startTime')
        endTime = operationObj.getParameterValue(parameterName='endTime')

        startTime = startTime.strftime("%H:%M:%S")
        endTime = endTime.strftime("%H:%M:%S")
        
        online = 0
        try:
            online = operationObj.getParameterValue(parameterName='online')
        except:
            pass
        
        delay = ''
        try:
            delay = operationObj.getParameterValue(parameterName='delay')
        except:
            pass
        
        walk = 0
        try:
            walk = operationObj.getParameterValue(parameterName='walk')
        except:
            pass
            
        set = ''
        try:
            set = operationObj.getParameterValue(parameterName='set')
        except:
            pass
        
        expLabel = ''
        try:
            expLabel = operationObj.getParameterValue(parameterName='expLabel')
        except:
            pass
        
        ippKm = ''
        if datatype.lower() == 'usrp':
            try:
                ippKm = operationObj.getParameterValue(parameterName='ippKm')
            except:
                pass
            
        projectParms = ProjectParms()
        
        projectParms.name = project_name
        projectParms.description = description
        projectParms.datatype = datatype
        projectParms.ext = None
        projectParms.dpath = dpath
        projectParms.online = online
        projectParms.startDate = startDate
        projectParms.endDate = endDate
        projectParms.startTime = startTime
        projectParms.endTime = endTime
        projectParms.delay=delay
        projectParms.walk=walk
        projectParms.set=set
        projectParms.ippKm=ippKm
        projectParms.expLabel = expLabel
        projectParms.parmsOk=parms_ok
        
        return projectParms
    
    def refreshProjectWindow(self, projectObjView):
        
        projectParms = self.__getParmsFromProjectObj(projectObjView)            
        
        index = projectParms.getDatatypeIndex()
        
        self.proName.setText(projectParms.name)
        self.proDescription.clear()
        self.proDescription.append(projectParms.description)
         
        self.on_proComDataType_activated(index=index)
        self.proDataPath.setText(projectParms.dpath)
        self.proComDataType.setCurrentIndex(index)
        self.proComReadMode.setCurrentIndex(projectParms.online)
        self.proDelay.setText(str(projectParms.delay))
        self.proSet.setText(str(projectParms.set))
        self.proIPPKm.setText(str(projectParms.ippKm))
        self.proComWalk.setCurrentIndex(projectParms.walk)
        self.proExpLabel.setText(str(projectParms.expLabel).strip())
        
        dateList = self.loadDays(data_path = projectParms.dpath,
                                 ext = projectParms.getExt(),
                                 walk = projectParms.walk,
                                 expLabel = projectParms.expLabel)
        
        try:
            startDateIndex = dateList.index(projectParms.startDate)
        except:
            startDateIndex = 0
        
        try:
            endDateIndex = dateList.index(projectParms.endDate)
        except:
            endDateIndex = int(self.proComEndDate.count()-1)
        
        self.proComStartDate.setCurrentIndex(startDateIndex)
        self.proComEndDate.setCurrentIndex(endDateIndex)
        
        startlist = projectParms.startTime.split(":")
        endlist = projectParms.endTime.split(":")
        
        self.time.setHMS(int(startlist[0]), int(startlist[1]), int(startlist[2])) 
        self.proStartTime.setTime(self.time)
        
        self.time.setHMS(int(endlist[0]), int(endlist[1]), int(endlist[2]))
        self.proEndTime.setTime(self.time)

    
    def __refreshVoltageWindow(self, puObj):
        
        opObj = puObj.getOperationObj(name='setRadarFrequency')
        if opObj == None:
            self.volOpRadarfrequency.clear()
            self.volOpCebRadarfrequency.setCheckState(0)
        else:
            value = opObj.getParameterValue(parameterName='frequency')
            value = str(float(value)/1e6)
            self.volOpRadarfrequency.setText(value)  
            self.volOpRadarfrequency.setEnabled(True)
            self.volOpCebRadarfrequency.setCheckState(QtCore.Qt.Checked)
        
        opObj = puObj.getOperationObj(name="selectChannels")
        
        if opObj == None:
            opObj = puObj.getOperationObj(name="selectChannelsByIndex")
        
        if opObj == None:
            self.volOpChannel.clear()
            self.volOpCebChannels.setCheckState(0)
        else:
            channelEnabled = False
            try:
                value = opObj.getParameterValue(parameterName='channelList')             
                value = str(value)[1:-1]
                channelEnabled = True
                channelMode = 0
            except:
                pass
            try:
                value = opObj.getParameterValue(parameterName='channelIndexList')             
                value = str(value)[1:-1]
                channelEnabled = True
                channelMode = 1
            except:
                pass
            
            if channelEnabled:
                self.volOpChannel.setText(value)
                self.volOpChannel.setEnabled(True)
                self.volOpCebChannels.setCheckState(QtCore.Qt.Checked)
                self.volOpComChannels.setCurrentIndex(channelMode)
                    
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
               
                if parmObj.name == "profileList":
                    value = parmObj.getValue()              
                    value = str(value)[1:-1]
                    self.volOpProfile.setText(value)  
                    self.volOpProfile.setEnabled(True)                                            
                    self.volOpCebProfile.setCheckState(QtCore.Qt.Checked)
                    self.volOpComProfile.setCurrentIndex(0)
                   
                if parmObj.name == "profileRangeList":
                    value = parmObj.getValue()              
                    value = str(value)[1:-1]
                    self.volOpProfile.setText(value)  
                    self.volOpProfile.setEnabled(True)                                            
                    self.volOpCebProfile.setCheckState(QtCore.Qt.Checked)
                    self.volOpComProfile.setCurrentIndex(1)
                
                if parmObj.name == "rangeList":
                    value = parmObj.getValue()           
                    value = str(value)[1:-1]
                    self.volOpProfile.setText(value)  
                    self.volOpProfile.setEnabled(True)                                            
                    self.volOpCebProfile.setCheckState(QtCore.Qt.Checked)
                    self.volOpComProfile.setCurrentIndex(2)
                   
        opObj = puObj.getOperationObj(name="Decoder")
        self.volOpCode.setText("") 
        if opObj == None:
            self.volOpCebDecodification.setCheckState(0)
        else:
            self.volOpCebDecodification.setCheckState(QtCore.Qt.Checked)
            
            parmObj = opObj.getParameterObj('code')
            
            if parmObj == None:
                self.volOpComCode.setCurrentIndex(0)
            else:
                
                parmObj1 = opObj.getParameterObj('nCode')
                parmObj2 = opObj.getParameterObj('nBaud')
                
                if parmObj1 == None or parmObj2 == None:
                    self.volOpComCode.setCurrentIndex(0)
                else:
                    code = ast.literal_eval(str(parmObj.getValue()))
                    nCode = parmObj1.getValue()
                    nBaud = parmObj2.getValue()
                    
                    code = numpy.asarray(code).reshape((nCode, nBaud)).tolist()
                    
                    #User defined by default
                    self.volOpComCode.setCurrentIndex(13)
                    self.volOpCode.setText(str(code)) 
                    
                    if nCode == 1:
                        if nBaud == 3:
                           self.volOpComCode.setCurrentIndex(1)
                        if nBaud == 4:
                            self.volOpComCode.setCurrentIndex(2)
                        if nBaud == 5:
                            self.volOpComCode.setCurrentIndex(3)
                        if nBaud == 7:
                            self.volOpComCode.setCurrentIndex(4)
                        if nBaud == 11:
                            self.volOpComCode.setCurrentIndex(5)
                        if nBaud == 13:
                            self.volOpComCode.setCurrentIndex(6)
                            
                    if nCode == 2:
                        if nBaud == 3:
                           self.volOpComCode.setCurrentIndex(7)
                        if nBaud == 4:
                            self.volOpComCode.setCurrentIndex(8)
                        if nBaud == 5:
                            self.volOpComCode.setCurrentIndex(9)
                        if nBaud == 7:
                            self.volOpComCode.setCurrentIndex(10)
                        if nBaud == 11:
                            self.volOpComCode.setCurrentIndex(11)
                        if nBaud == 13:
                            self.volOpComCode.setCurrentIndex(12)
            

        opObj = puObj.getOperationObj(name="deFlip")   
        if opObj == None:
            self.volOpFlip.clear()
            self.volOpFlip.setEnabled(False)
            self.volOpCebFlip.setCheckState(0)
        else:
            try:
                value = opObj.getParameterValue(parameterName='channelList')
                value = str(value)[1:-1]
            except:
                value = ""
                
            self.volOpFlip.setText(value)
            self.volOpFlip.setEnabled(True)
            self.volOpCebFlip.setCheckState(QtCore.Qt.Checked)
            
        opObj = puObj.getOperationObj(name="CohInt")   
        if opObj == None:
            self.volOpCohInt.clear()
            self.volOpCebCohInt.setCheckState(0)
        else:
            value = opObj.getParameterValue(parameterName='n')
            self.volOpCohInt.setText(str(value))
            self.volOpCohInt.setEnabled(True)
            self.volOpCebCohInt.setCheckState(QtCore.Qt.Checked)
        
        opObj = puObj.getOperationObj(name='Scope')
        if opObj == None:
            self.volGraphCebshow.setCheckState(0)
        else:
            self.volGraphCebshow.setCheckState(QtCore.Qt.Checked)
            
            parmObj = opObj.getParameterObj(parameterName='channelList')
            
            if parmObj == None:
                self.volGraphChannelList.clear()
            else:
                value = parmObj.getValue()            
                value = str(value)
                self.volGraphChannelList.setText(value)  
                self.volOpProfile.setEnabled(True) 
            
            parmObj1 = opObj.getParameterObj(parameterName='xmin')
            parmObj2 = opObj.getParameterObj(parameterName='xmax')
            
            if parmObj1 == None or parmObj2 ==None:
                self.volGraphfreqrange.clear()
            else:
                value1 = parmObj1.getValue()
                value1 = str(value1) 
                value2 = parmObj2.getValue()          
                value2 = str(value2)
                value = value1 + "," + value2
                self.volGraphfreqrange.setText(value)
            
            parmObj1 = opObj.getParameterObj(parameterName='ymin')
            parmObj2 = opObj.getParameterObj(parameterName='ymax')
            
            if parmObj1 == None or parmObj2 ==None:
                self.volGraphHeightrange.clear()
            else:
                value1 = parmObj1.getValue()
                value1 = str(value1) 
                value2 = parmObj2.getValue()
                value2 = str(value2)           
                value = value1 + "," + value2
                value2 = str(value2)
                self.volGraphHeightrange.setText(value)
            
            parmObj = opObj.getParameterObj(parameterName='save')
            
            if parmObj == None:
                self.volGraphCebSave.setCheckState(QtCore.Qt.Unchecked)
            else:
                value = parmObj.getValue()
                if int(value):
                    self.volGraphCebSave.setCheckState(QtCore.Qt.Checked)
                else:
                    self.volGraphCebSave.setCheckState(QtCore.Qt.Unchecked)
                    
            parmObj = opObj.getParameterObj(parameterName='figpath')
            if parmObj == None:
                self.volGraphPath.clear()
            else:
                value = parmObj.getValue()
                path = str(value)
                self.volGraphPath.setText(path) 

            parmObj = opObj.getParameterObj(parameterName='figfile')
            if parmObj == None:
                self.volGraphPrefix.clear()
            else:
                value = parmObj.getValue()
                figfile = str(value)
                self.volGraphPrefix.setText(figfile) 
                
        # outputVoltageWrite
        opObj = puObj.getOperationObj(name='VoltageWriter')
        
        if opObj == None:
            self.volOutputPath.clear()
            self.volOutputblocksperfile.clear()
            self.volOutputprofilesperblock.clear()
        else:
            parmObj = opObj.getParameterObj(parameterName='path')
            if parmObj == None:
                self.volOutputPath.clear()
            else:
                value = parmObj.getValue()
                path = str(value)
                self.volOutputPath.setText(path) 
            
            parmObj = opObj.getParameterObj(parameterName='blocksPerFile')
            if parmObj == None:
               self.volOutputblocksperfile.clear()
            else:
                value = parmObj.getValue()
                blocksperfile = str(value)
                self.volOutputblocksperfile.setText(blocksperfile)
                
            parmObj = opObj.getParameterObj(parameterName='profilesPerBlock')
            if parmObj == None:
                self.volOutputprofilesperblock.clear()
            else:
                value = parmObj.getValue()
                profilesPerBlock = str(value)
                self.volOutputprofilesperblock.setText(profilesPerBlock)
        
        return
        
    def __refreshSpectraWindow(self, puObj):
        
        inputId = puObj.getInputId()
        inputPUObj = self.__puObjDict[inputId]
        
        if inputPUObj.datatype == 'Voltage':
            self.specOpnFFTpoints.setEnabled(True)
            self.specOpProfiles.setEnabled(True)
            self.specOpippFactor.setEnabled(True)
        else:
            self.specOpnFFTpoints.setEnabled(False)
            self.specOpProfiles.setEnabled(False)
            self.specOpippFactor.setEnabled(False)
        
        opObj = puObj.getOperationObj(name='setRadarFrequency')
        if opObj == None:
            self.specOpRadarfrequency.clear()
            self.specOpCebRadarfrequency.setCheckState(0)
        else:
            value = opObj.getParameterValue(parameterName='frequency')
            value = str(float(value)/1e6)
            self.specOpRadarfrequency.setText(value)  
            self.specOpRadarfrequency.setEnabled(True)
            self.specOpCebRadarfrequency.setCheckState(QtCore.Qt.Checked)
        
        opObj = puObj.getOperationObj(name="run")   
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
                            
        opObj = puObj.getOperationObj(name="run")  
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
            opObj = puObj.getOperationObj(name="selectChannelsByIndex")
            
        if opObj == None:
            self.specOpChannel.clear()
            self.specOpCebChannel.setCheckState(0)
        else:
            channelEnabled = False
            try:
                value = opObj.getParameterValue(parameterName='channelList')             
                value = str(value)[1:-1]
                channelEnabled = True
                channelMode = 0
            except:
                pass
            try:
                value = opObj.getParameterValue(parameterName='channelIndexList')             
                value = str(value)[1:-1]
                channelEnabled = True
                channelMode = 1
            except:
                pass
            
            if channelEnabled:
                self.specOpChannel.setText(value)
                self.specOpChannel.setEnabled(True)
                self.specOpCebChannel.setCheckState(QtCore.Qt.Checked)
                self.specOpComChannel.setCurrentIndex(channelMode)
            
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
        
        self.specGraphPath.clear()
        self.specGraphPrefix.clear()
        self.specGgraphFreq.clear()
        self.specGgraphHeight.clear()
        self.specGgraphDbsrange.clear()
        self.specGgraphmagnitud.clear()
        self.specGgraphPhase.clear()
        self.specGgraphChannelList.clear()
        self.specGgraphTminTmax.clear()
        self.specGgraphTimeRange.clear()
        self.specGgraphftpratio.clear()
        
        opObj = puObj.getOperationObj(name='SpectraPlot')
        
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
            
            parmObj = opObj.getParameterObj(parameterName="save")
            if parmObj == None:
                self.specGraphSaveSpectra.setCheckState(0)
            else:
                self.specGraphSaveSpectra.setCheckState(QtCore.Qt.Checked)
                     
            parmObj = opObj.getParameterObj(parameterName="ftp")
            if parmObj == None:
                self.specGraphftpSpectra.setCheckState(0)
            else:
                self.specGraphftpSpectra.setCheckState(QtCore.Qt.Checked)
                
            parmObj = opObj.getParameterObj(parameterName="figpath")
            if parmObj:
                value = parmObj.getValue()
                self.specGraphPath.setText(value)
            
            parmObj = opObj.getParameterObj(parameterName="wr_period")
            if parmObj:
                value = parmObj.getValue()
                self.specGgraphftpratio.setText(str(value))
            
        opObj = puObj.getOperationObj(name='CrossSpectraPlot')
        
        if opObj == None:
            self.specGraphCebCrossSpectraplot.setCheckState(0)
            self.specGraphSaveCross.setCheckState(0)
            self.specGraphftpCross.setCheckState(0)
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

            parmObj = opObj.getParameterObj(parameterName='coh_min')
            if parmObj == None:
                self.specGgraphmagnitud.clear()
            else:
                value1 = opObj.getParameterValue(parameterName='coh_min') 
                value1 = str(value1)
                value2 = opObj.getParameterValue(parameterName='coh_max')            
                value2 = str(value2)
                value = value1 + "," + value2
                self.specGgraphmagnitud.setText(value)
                self.specGgraphmagnitud.setEnabled(True)
                
            parmObj = opObj.getParameterObj(parameterName='phase_min')
            if parmObj == None:
                self.specGgraphPhase.clear()
            else:
                value1 = opObj.getParameterValue(parameterName='phase_min') 
                value1 = str(value1)
                value2 = opObj.getParameterValue(parameterName='phase_max')            
                value2 = str(value2)
                value = value1 + "," + value2
                self.specGgraphPhase.setText(value)
                self.specGgraphPhase.setEnabled(True)
                
            parmObj = opObj.getParameterObj(parameterName="save")
            if parmObj == None:
                self.specGraphSaveCross.setCheckState(0)
            else:
                self.specGraphSaveCross.setCheckState(QtCore.Qt.Checked)
                     
            parmObj = opObj.getParameterObj(parameterName="ftp")
            if parmObj == None:
                self.specGraphftpCross.setCheckState(0)
            else:
                self.specGraphftpCross.setCheckState(QtCore.Qt.Checked)

            parmObj = opObj.getParameterObj(parameterName="figpath")
            if parmObj:
                value = parmObj.getValue()
                self.specGraphPath.setText(value)
            
            parmObj = opObj.getParameterObj(parameterName="wr_period")
            if parmObj:
                value = parmObj.getValue()
                self.specGgraphftpratio.setText(str(value))
                
        opObj = puObj.getOperationObj(name='RTIPlot')
        
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
                
            parmObj = opObj.getParameterObj(parameterName="save")
            if parmObj == None:
                self.specGraphSaveRTIplot.setCheckState(0)
            else:
                self.specGraphSaveRTIplot.setCheckState(QtCore.Qt.Checked)
                     
            parmObj = opObj.getParameterObj(parameterName="ftp")
            if parmObj == None:
                self.specGraphftpRTIplot.setCheckState(0)
            else:
                self.specGraphftpRTIplot.setCheckState(QtCore.Qt.Checked)

            parmObj = opObj.getParameterObj(parameterName="figpath")
            if parmObj:
                value = parmObj.getValue()
                self.specGraphPath.setText(value)
            
            parmObj = opObj.getParameterObj(parameterName="wr_period")
            if parmObj:
                value = parmObj.getValue()
                self.specGgraphftpratio.setText(str(value))
                
        opObj = puObj.getOperationObj(name='CoherenceMap')
        
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

            parmObj = opObj.getParameterObj(parameterName='coh_min')
            if parmObj == None:
                self.specGgraphmagnitud.clear()
            else:
                value1 = opObj.getParameterValue(parameterName='coh_min') 
                value1 = str(value1)
                value2 = opObj.getParameterValue(parameterName='coh_max')            
                value2 = str(value2)
                value = value1 + "," + value2
                self.specGgraphmagnitud.setText(value)
                self.specGgraphmagnitud.setEnabled(True)
                
            parmObj = opObj.getParameterObj(parameterName='phase_min')
            if parmObj == None:
                self.specGgraphPhase.clear()
            else:
                value1 = opObj.getParameterValue(parameterName='phase_min') 
                value1 = str(value1)
                value2 = opObj.getParameterValue(parameterName='phase_max')            
                value2 = str(value2)
                value = value1 + "," + value2
                self.specGgraphPhase.setText(value)
                self.specGgraphPhase.setEnabled(True)
            
            parmObj = opObj.getParameterObj(parameterName="save")
            if parmObj == None:
                self.specGraphSaveCoherencemap.setCheckState(0)
            else:
                self.specGraphSaveCoherencemap.setCheckState(QtCore.Qt.Checked)
                     
            parmObj = opObj.getParameterObj(parameterName="ftp")
            if parmObj == None:
                self.specGraphftpCoherencemap.setCheckState(0)
            else:
                self.specGraphftpCoherencemap.setCheckState(QtCore.Qt.Checked)

            parmObj = opObj.getParameterObj(parameterName="figpath")
            if parmObj:
                value = parmObj.getValue()
                self.specGraphPath.setText(value)
            
            parmObj = opObj.getParameterObj(parameterName="wr_period")
            if parmObj:
                value = parmObj.getValue()
                self.specGgraphftpratio.setText(str(value))
                
        opObj = puObj.getOperationObj(name='PowerProfilePlot')
        
        if opObj == None:
            self.specGraphPowerprofile.setCheckState(0)
            self.specGraphSavePowerprofile.setCheckState(0)
            self.specGraphftpPowerprofile.setCheckState(0)
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
            
            parmObj = opObj.getParameterObj(parameterName="save")
            if parmObj == None:
                self.specGraphSavePowerprofile.setCheckState(0)
            else:
                self.specGraphSavePowerprofile.setCheckState(QtCore.Qt.Checked)
                     
            parmObj = opObj.getParameterObj(parameterName="ftp")
            if parmObj == None:
                self.specGraphftpPowerprofile.setCheckState(0)
            else:
                self.specGraphftpPowerprofile.setCheckState(QtCore.Qt.Checked)

            parmObj = opObj.getParameterObj(parameterName="figpath")
            if parmObj:
                value = parmObj.getValue()
                self.specGraphPath.setText(value)
            
            parmObj = opObj.getParameterObj(parameterName="wr_period")
            if parmObj:
                value = parmObj.getValue()
                self.specGgraphftpratio.setText(str(value))
                
        opObj = puObj.getOperationObj(name='Noise')
        
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
                            
            parmObj = opObj.getParameterObj(parameterName="save")
            if parmObj == None:
                self.specGraphSaveRTInoise.setCheckState(0)
            else:
                self.specGraphSaveRTInoise.setCheckState(QtCore.Qt.Checked)
                     
            parmObj = opObj.getParameterObj(parameterName="ftp")
            if parmObj == None:
                self.specGraphftpRTInoise.setCheckState(0)
            else:
                self.specGraphftpRTInoise.setCheckState(QtCore.Qt.Checked)

            parmObj = opObj.getParameterObj(parameterName="figpath")
            if parmObj:
                value = parmObj.getValue()
                self.specGraphPath.setText(value)
            
            parmObj = opObj.getParameterObj(parameterName="wr_period")
            if parmObj:
                value = parmObj.getValue()
                self.specGgraphftpratio.setText(str(value))
                
        opObj = puObj.getOperationObj(name='SpectraWriter')
        if opObj == None:
            self.specOutputPath.clear()
            self.specOutputblocksperfile.clear()
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
        
        return
    
    def __refreshSpectraHeisWindow(self, puObj):

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
        
        self.specHeisGgraphXminXmax.clear()
        self.specHeisGgraphYminYmax.clear()
        
        self.specHeisGgraphChannelList.clear()
        self.specHeisGgraphTminTmax.clear()
        self.specHeisGgraphTimeRange.clear()
        self.specHeisGgraphftpratio.clear()
        
        opObj = puObj.getOperationObj(name='SpectraHeisScope')
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
                    
            parmObj = opObj.getParameterObj(parameterName="save")
            if parmObj == None:
                self.specHeisGraphSaveSpectra.setCheckState(0)
            else:
                self.specHeisGraphSaveSpectra.setCheckState(QtCore.Qt.Checked)
                     
            parmObj = opObj.getParameterObj(parameterName="ftp")
            if parmObj == None:
                self.specHeisGraphftpSpectra.setCheckState(0)
            else:
                self.specHeisGraphftpSpectra.setCheckState(QtCore.Qt.Checked)

            parmObj = opObj.getParameterObj(parameterName="figpath")
            if parmObj:
                value = parmObj.getValue()
                self.specHeisGraphPath.setText(value)
            
            parmObj = opObj.getParameterObj(parameterName="wr_period")
            if parmObj:
                value = parmObj.getValue()
                self.specHeisGgraphftpratio.setText(str(value))
                
        opObj = puObj.getOperationObj(name='RTIfromSpectraHeis')
        
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
            
            parmObj = opObj.getParameterObj(parameterName="save")
            if parmObj == None:
                self.specHeisGraphSaveRTIplot.setCheckState(0)
            else:
                self.specHeisGraphSaveRTIplot.setCheckState(QtCore.Qt.Checked)
                     
            parmObj = opObj.getParameterObj(parameterName="ftp")
            if parmObj == None:
                self.specHeisGraphftpRTIplot.setCheckState(0)
            else:
                self.specHeisGraphftpRTIplot.setCheckState(QtCore.Qt.Checked)

            parmObj = opObj.getParameterObj(parameterName="figpath")
            if parmObj:
                value = parmObj.getValue()
                self.specHeisGraphPath.setText(value)
            
            parmObj = opObj.getParameterObj(parameterName="wr_period")
            if parmObj:
                value = parmObj.getValue()
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
        
        return
    
    def __refreshCorrelationWindow(self, puObj):
        pass
    
    def refreshPUWindow(self, puObj):
        
        if puObj.datatype == 'Voltage':
            self.__refreshVoltageWindow(puObj)

        if puObj.datatype == 'Spectra':
            self.__refreshSpectraWindow(puObj)
            
        if puObj.datatype == 'SpectraHeis':
            self.__refreshSpectraHeisWindow(puObj)

    def refreshProjectProperties(self, projectObjView):
        
        propertyBuffObj = PropertyBuffer()
        name = projectObjView.name
        
        propertyBuffObj.append("Properties", "Name", projectObjView.name),
        propertyBuffObj.append("Properties", "Description", projectObjView.description)
        propertyBuffObj.append("Properties", "Workspace", self.pathWorkSpace)
        
        readUnitObj = projectObjView.getReadUnitObj()
        runOperationObj = readUnitObj.getOperationObj(name='run')
        
        for thisParmObj in runOperationObj.getParameterObjList():
            propertyBuffObj.append("Reading parms", thisParmObj.name, str(thisParmObj.getValue()))
             
        propertiesModel = propertyBuffObj.getPropertyModel()
        
        self.treeProjectProperties.setModel(propertiesModel)
        self.treeProjectProperties.expandAll()  
        self.treeProjectProperties.resizeColumnToContents(0)
        self.treeProjectProperties.resizeColumnToContents(1)
        
    def refreshPUProperties(self, puObjView):
        
        ############ FTP CONFIG ################################
        #Deleting FTP Conf. This processing unit have not got any
        #FTP configuration by default
        if puObjView.id in self.__puLocalFolder2FTP.keys():
            self.__puLocalFolder2FTP.pop(puObjView.id)
        ########################################################
        
        propertyBuffObj = PropertyBuffer()
        
        for thisOp in puObjView.getOperationObjList():
            
            operationName = thisOp.name
            
            if operationName == 'run':
                operationName = 'Properties'  
            
            else:
                if not thisOp.getParameterObjList():
                    propertyBuffObj.append(operationName, '--', '--')
                    continue
            
            for thisParmObj in thisOp.getParameterObjList():
                propertyBuffObj.append(operationName, thisParmObj.name, str(thisParmObj.getValue()))
                
                ############ FTP CONFIG ################################
                if thisParmObj.name == "ftp_wei" and thisParmObj.getValue():
                    value = thisParmObj.getValue()
                    self.temporalFTP.ftp_wei = value
                
                if thisParmObj.name == "exp_code" and thisParmObj.getValue():
                    value = thisParmObj.getValue()
                    self.temporalFTP.exp_code = value
                
                if thisParmObj.name == "sub_exp_code" and thisParmObj.getValue():
                    value = thisParmObj.getValue()
                    self.temporalFTP.sub_exp_code = value
                
                if thisParmObj.name == "plot_pos" and thisParmObj.getValue():
                    value = thisParmObj.getValue()
                    self.temporalFTP.plot_pos = value
                    
                if thisParmObj.name == 'ftp' and thisParmObj.getValue():
                    figpathObj = thisOp.getParameterObj('figpath')
                    if figpathObj:
                        self.__puLocalFolder2FTP[puObjView.id] = figpathObj.getValue()
                
                ########################################################
        
        propertiesModel = propertyBuffObj.getPropertyModel()
        
        self.treeProjectProperties.setModel(propertiesModel)
        self.treeProjectProperties.expandAll()  
        self.treeProjectProperties.resizeColumnToContents(0)
        self.treeProjectProperties.resizeColumnToContents(1)

    def refreshGraphicsId(self):
        
        projectObj = self.getSelectedProjectObj()
        
        for idPU, puObj in projectObj.procUnitConfObjDict.items():
            
            for opObj in puObj.getOperationObjList():
                
                if opObj.name not in ('Scope', 'SpectraPlot', 'CrossSpectraPlot', 'RTIPlot', 'CoherenceMap', 'PowerProfilePlot', 'Noise', 'SpectraHeisScope', 'RTIfromSpectraHeis'):
                    continue
                
                opObj.changeParameter(name='id', value=opObj.id, format='int')
    
    def on_click(self, index):
        
        self.selectedItemTree = self.projectExplorerModel.itemFromIndex(index)
        
        projectObjView = self.getSelectedProjectObj()
        
        if not projectObjView:
            return
        
        self.create = False
        selectedObjView = self.getSelectedItemObj()
        
        #A project has been selected
        if projectObjView == selectedObjView:
            
            self.refreshProjectWindow(projectObjView)
            self.refreshProjectProperties(projectObjView)
            
            self.tabProject.setEnabled(True)
            self.tabVoltage.setEnabled(False)
            self.tabSpectra.setEnabled(False)
            self.tabCorrelation.setEnabled(False)
            self.tabSpectraHeis.setEnabled(False)
            self.tabWidgetProject.setCurrentWidget(self.tabProject)  
            
            return    
        
        #A processing unit has been selected
        voltEnable = False
        specEnable = False
        corrEnable = False
        specHeisEnable = False
        tabSelected = self.tabProject
        
        puObj = selectedObjView
        
        self.refreshPUWindow(puObj)
        self.refreshPUProperties(puObj)
        self.showtabPUCreated(puObj.datatype)
                  
    def on_right_click(self, pos):
        
        self.menu = QtGui.QMenu()
        quitAction0 = self.menu.addAction("Create a New Project")
        quitAction1 = self.menu.addAction("Create a New Processing Unit")
        quitAction2 = self.menu.addAction("Delete Item")
        quitAction3 = self.menu.addAction("Quit")
        
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
                outputstr = "You need to create a Project before adding a Processing Unit"
                self.console.clear()
                self.console.append(outputstr)
                return 0
            else:       
               self.addPUWindow()   
               self.console.clear()
               self.console.append("Please, Choose the type of Processing Unit")
#                self.console.append("If your Datatype is rawdata, you will start with processing unit Type Voltage")
#                self.console.append("If your Datatype is pdata, you will choose between processing unit Type Spectra or Correlation")
#                self.console.append("If your Datatype is fits, you will start with processing unit Type SpectraHeis")

        if action == quitAction2:
            index = self.selectedItemTree
            try:
                index.parent()
            except:
                self.console.append('Please first select a Project or Processing Unit')
                return 0
            # print index.parent(),index
            if index.parent() == None:
               self.projectExplorerModel.removeRow(index.row())
            else:
                index.parent().removeRow(index.row())
            self.removeItemTreeFromProject()  
            self.console.clear()                
            # for i in self.projectExplorerTree.selectionModel().selection().indexes():
            #     print i.row()

        if action == quitAction3:
            self.close()
            return 0
        
    def createProjectView(self, id):
        
#         project_name, description, datatype, data_path, starDate, endDate, startTime, endTime, online, delay, walk, set = self.getParmsFromProjectWindow()
        id = str(id)
        projectParms = self.__getParmsFromProjectWindow()
        
        if not projectParms.isValid():
            return None
        
        projectObjView = Project()
        projectObjView.setup(id=id, name=projectParms.name, description=projectParms.description)
        
        self.__projectObjDict[id] = projectObjView
        self.addProject2ProjectExplorer(id=id, name=projectObjView.name) 
        
        self.create = False
        
        return projectObjView 
    
    def updateProjectView(self):
        
#         project_name, description, datatype, data_path, starDate, endDate, startTime, endTime, online, delay, walk, set = self.getParmsFromProjectWindow()
        
        projectParms = self.__getParmsFromProjectWindow()

        if not projectParms.isValid():
            return None
        
        projectObjView = self.getSelectedProjectObj()
        projectObjView.update(name=projectParms.name, description=projectParms.description)
               
        return projectObjView
         
    def createReadUnitView(self, projectObjView):
        
#         project_name, description, datatype, data_path, startDate, endDate, startTime, endTime, online, delay, walk, set = self.getParmsFromProjectWindow()
        
        projectParms = self.__getParmsFromProjectWindow()
        
        if not projectParms.isValid():
            return None
        
        if projectParms.datatype in ("Voltage", "Spectra", "Fits"):
            readUnitConfObj = projectObjView.addReadUnit(datatype=projectParms.datatype,
                                                            path=projectParms.dpath,
                                                            startDate=projectParms.startDate,
                                                            endDate=projectParms.endDate,
                                                            startTime=projectParms.startTime,
                                                            endTime=projectParms.endTime,
                                                            online=projectParms.online,
                                                            walk=projectParms.walk
                                                            )
            
            if projectParms.set:
                readUnitConfObj.addParameter(name="set", value=projectParms.set, format="int")
            
            if projectParms.delay:
                readUnitConfObj.addParameter(name="delay", value=projectParms.delay, format="int")
            
            if projectParms.expLabel:
                readUnitConfObj.addParameter(name="expLabel", value=projectParms.expLabel)
            
        if projectParms.datatype == "USRP":
            readUnitConfObj = projectObjView.addReadUnit(datatype=projectParms.datatype,
                                                            path=projectParms.dpath,
                                                            startDate=projectParms.startDate,
                                                            endDate=projectParms.endDate,
                                                            startTime=projectParms.startTime,
                                                            endTime=projectParms.endTime,
                                                            online=projectParms.online,
                                                            ippKm=projectParms.ippKm
                                                            )
            
            if projectParms.delay:
                readUnitConfObj.addParameter(name="delay", value=projectParms.delay, format="int")
                
        return readUnitConfObj

    def updateReadUnitView(self, projectObjView, idReadUnit):
        
#         project_name, description, datatype, data_path, startDate, endDate, startTime, endTime, online, delay, walk , set = self.getParmsFromProjectWindow()
        
        readUnitConfObj = projectObjView.getProcUnitObj(idReadUnit)
        
        projectParms = self.__getParmsFromProjectWindow()
        
        if not projectParms.isValid():
            return None
        
        if projectParms.datatype in ["Voltage", "Spectra", "Fits"]:
            readUnitConfObj.update(datatype=projectParms.datatype,
                                    path=projectParms.dpath,
                                    startDate=projectParms.startDate,
                                    endDate=projectParms.endDate,
                                    startTime=projectParms.startTime,
                                    endTime=projectParms.endTime,
                                    online=projectParms.online,
                                    walk=projectParms.walk
                                    )
            if projectParms.set:
                readUnitConfObj.addParameter(name="set", value=projectParms.set, format="int")
        
            if projectParms.delay:
                readUnitConfObj.addParameter(name="delay", value=projectParms.delay, format="int")
            
            if projectParms.expLabel:
                readUnitConfObj.addParameter(name="expLabel", value=projectParms.expLabel)
                
        if projectParms.datatype == "USRP":
            readUnitConfObj.update(datatype=projectParms.datatype,
                                    path=projectParms.dpath,
                                    startDate=projectParms.startDate,
                                    endDate=projectParms.endDate,
                                    startTime=projectParms.startTime,
                                    endTime=projectParms.endTime,
                                    online=projectParms.online,
                                    ippKm=projectParms.ippKm
                                    ) 

            if projectParms.delay:
                readUnitConfObj.addParameter(name="delay", value=projectParms.delay, format="int")
                
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
        fatherObj = self.getSelectedItemObj()
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
        
        puObj = self.createProcUnitView(projectObjView, datatype, inputId)
        
        self.addPU2ProjectExplorer(puObj)
        
        self.showtabPUCreated(datatype)
        
        self.clearPUWindow(datatype)
        
        self.showPUinitView()   
        
    def addFTPConf2Operation(self, puObj, opObj):

        if not self.temporalFTP.create:
            self.temporalFTP.setwithoutconfiguration()
            
#         opObj.addParameter(name='server', value=self.temporalFTP.server, format='str')
#         opObj.addParameter(name='remotefolder', value=self.temporalFTP.remotefolder, format='str')
#         opObj.addParameter(name='username', value=self.temporalFTP.username, format='str')
#         opObj.addParameter(name='password', value=self.temporalFTP.password, format='str')
        
        if self.temporalFTP.ftp_wei:
            opObj.addParameter(name='ftp_wei', value=int(self.temporalFTP.ftp_wei), format='int')
        if self.temporalFTP.exp_code:
            opObj.addParameter(name='exp_code', value=int(self.temporalFTP.exp_code), format='int')
        if self.temporalFTP.sub_exp_code:
            opObj.addParameter(name='sub_exp_code', value=int(self.temporalFTP.sub_exp_code), format='int')
        if self.temporalFTP.plot_pos:
            opObj.addParameter(name='plot_pos', value=int(self.temporalFTP.plot_pos), format='int')
               
#     def __checkFTPProcUnit(self, projectObj, localfolder):
#         
#         puId = None
#         puObj = None
#             
#         for thisPuId, thisPuObj in projectObj.procUnitItems():
#             
#             if not thisPuObj.name == "SendToServer":
#                 continue
#             
#             opObj = thisPuObj.getOperationObj(name='run')
#             
#             parmObj = opObj.getParameterObj('localfolder')
# 
#             #localfolder parameter should always be set, if it is not set then ProcUnit should be removed
#             if not parmObj:
#                 projectObj.removeProcUnit(thisPuId)
#                 continue
#             
#             thisLocalfolder = parmObj.getValue()
#             
#             if localfolder != thisLocalfolder:
#                 continue
#             
#             puId = thisPuId
#             puObj = thisPuObj
#             break
#         
#         return puObj
    
    def createFTPProcUnitView(self):
        
        if not self.temporalFTP.create:
            self.temporalFTP.setwithoutconfiguration()
        
        projectObj = self.getSelectedProjectObj()
        
        self.removeAllFTPProcUnitView(projectObj)
            
        if not self.__puLocalFolder2FTP:
            return
        
        folderList = ",".join(self.__puLocalFolder2FTP.values())
                
        procUnitConfObj = projectObj.addProcUnit(name="SendToServer")
            
        procUnitConfObj.addParameter(name='server', value=self.temporalFTP.server, format='str')
        procUnitConfObj.addParameter(name='username', value=self.temporalFTP.username, format='str')
        procUnitConfObj.addParameter(name='password', value=self.temporalFTP.password, format='str')
        procUnitConfObj.addParameter(name='localfolder', value=folderList, format='list')
        procUnitConfObj.addParameter(name='remotefolder', value=self.temporalFTP.remotefolder, format='str')
        procUnitConfObj.addParameter(name='ext', value=self.temporalFTP.extension, format='str')
        procUnitConfObj.addParameter(name='period', value=self.temporalFTP.period, format='int')
        procUnitConfObj.addParameter(name='protocol', value=self.temporalFTP.protocol, format='str')
        
        procUnitConfObj.addParameter(name='ftp_wei', value=self.temporalFTP.ftp_wei, format='int')
        procUnitConfObj.addParameter(name='exp_code', value=self.temporalFTP.exp_code, format='int')
        procUnitConfObj.addParameter(name='sub_exp_code', value=self.temporalFTP.sub_exp_code, format='int')
        procUnitConfObj.addParameter(name='plot_pos', value=self.temporalFTP.plot_pos, format='int')
            
        self.__puObjDict[procUnitConfObj.getId()] = procUnitConfObj

    def removeAllFTPProcUnitView(self, projectObj):
        
        for thisPuId, thisPuObj in projectObj.procUnitItems():
            
            if not thisPuObj.name == "SendToServer":
                continue
            
            projectObj.removeProcUnit(thisPuId)
        
            if thisPuId not in self.__puObjDict.keys():
                continue
            
            self.__puObjDict.pop(thisPuId)

    def showPUinitView(self):
        
        self.propertiesModel = TreeModel()
        self.propertiesModel.initPUVoltageView()
        self.treeProjectProperties.setModel(self.propertiesModel)
        self.treeProjectProperties.expandAll()
        self.treeProjectProperties.allColumnsShowFocus()
        self.treeProjectProperties.resizeColumnToContents(1)

    def saveFTPFromOpObj(self, operationObj):
        
        if operationObj.name != "SendByFTP":
            return
        
        server = operationObj.getParameterValue("server")
        username = operationObj.getParameterValue("username")
        password = operationObj.getParameterValue("password")
        localfolder = operationObj.getParameterValue("localfolder")
        remotefolder = operationObj.getParameterValue("remotefolder")
        ext = operationObj.getParameterValue("ext")
        period = operationObj.getParameterValue("period")
            
        self.temporalFTP.save(server=server,
                              remotefolder=remotefolder,
                              username=username,
                              password=password,
                              localfolder=localfolder,
                              extension=ext)
        
        return
    
    def saveFTPFromProcUnitObj(self, puObj):
        
        opObj = puObj.getOperationObj(name="run")
        
        parmObj = opObj.getParameterObj(parameterName="server")
        if parmObj == None:
            server = 'jro-app.igp.gob.pe'                      
        else:
            server = parmObj.getValue()
        
        parmObj = opObj.getParameterObj(parameterName="remotefolder")
        if parmObj == None:
            remotefolder = '/home/wmaster/graficos'
        else:
            remotefolder = parmObj.getValue()
        
        parmObj = opObj.getParameterObj(parameterName="username")
        if parmObj == None:
            username = 'wmaster'
        else:
            username = parmObj.getValue()
        
        parmObj = opObj.getParameterObj(parameterName="password")
        if parmObj == None:
            password = 'mst2010vhf'
        else:
            password = parmObj.getValue()
        
        parmObj = opObj.getParameterObj(parameterName="ftp_wei")
        if parmObj == None:
            ftp_wei = 0
        else:
            ftp_wei = parmObj.getValue()
        
        parmObj = opObj.getParameterObj(parameterName="exp_code")
        if parmObj == None:
            exp_code = 0
        else:
            exp_code = parmObj.getValue()
        
        parmObj = opObj.getParameterObj(parameterName="sub_exp_code")
        if parmObj == None:
            sub_exp_code = 0
        else:
            sub_exp_code = parmObj.getValue()

        parmObj = opObj.getParameterObj(parameterName="plot_pos")
        if parmObj == None:
            plot_pos = 0
        else:
            plot_pos = parmObj.getValue()

        parmObj = opObj.getParameterObj(parameterName="localfolder")
        if parmObj == None:
            localfolder = None
        else:
            localfolder = parmObj.getValue()

        parmObj = opObj.getParameterObj(parameterName="ext")
        if parmObj == None:
            extension = '.png'
        else:
            extension = parmObj.getValue()
                            
        self.temporalFTP.save(server=server,
                              remotefolder=remotefolder,
                              username=username,
                              password=password,
                              ftp_wei=ftp_wei,
                              exp_code=exp_code,
                              sub_exp_code=sub_exp_code,
                              plot_pos=plot_pos,
                              localfolder=localfolder,
                              extension=extension)

    def addProject2ProjectExplorer(self, id, name):
        
        itemTree = QtGui.QStandardItem(QtCore.QString(str(name)))
        
        parentItem = self.projectExplorerModel.invisibleRootItem()
        parentItem.appendRow(itemTree)
        
        self.projectExplorerTree.setCurrentIndex(itemTree.index())

        self.selectedItemTree = itemTree
        
        self.__itemTreeDict[id] = itemTree
        
    def addPU2ProjectExplorer(self, puObj):
        
        id, name = puObj.id, puObj.datatype
        
        itemTree = QtGui.QStandardItem(QtCore.QString(str(name)))
        
        parentItem = self.selectedItemTree
        parentItem.appendRow(itemTree)   
        self.projectExplorerTree.expandAll()
        
        self.projectExplorerTree.setCurrentIndex(itemTree.index())

        self.selectedItemTree = itemTree
               
        self.__itemTreeDict[id] = itemTree
         
    def addPU2PELoadXML(self, puObj):
        
        id, name, inputId = puObj.id, puObj.datatype, puObj.inputId
        
        itemTree = QtGui.QStandardItem(QtCore.QString(str(name)))
        
        if self.__itemTreeDict.has_key(inputId):
            parentItem = self.__itemTreeDict[inputId]
        else:
            #If parent is a Reader object
            parentItem = self.__itemTreeDict[id[:-1]]
            
        parentItem.appendRow(itemTree)   
        self.projectExplorerTree.expandAll()
        parentItem = itemTree
        self.projectExplorerTree.setCurrentIndex(parentItem.index())
        
        self.__itemTreeDict[id] = itemTree
        self.selectedItemTree = itemTree
    
    def getSelectedProjectObj(self):
        """
        Return the current project object selected. If a processing unit is 
        actually selected this function returns associated project.
        
        None if any project or processing unit is selected
        """
        for key in self.__itemTreeDict.keys():
            if self.__itemTreeDict[key] != self.selectedItemTree:
                continue
            
            if self.__projectObjDict.has_key(key):
                projectObj = self.__projectObjDict[key]
                return projectObj
            
            puObj = self.__puObjDict[key]
            
            if puObj.parentId == None:
                projectId = puObj.getId()[0]
            else:
                projectId = puObj.parentId
                
            projectObj = self.__projectObjDict[projectId]
            return projectObj
        
        return None

    def getSelectedItemObj(self):
        """
        Return the current project or processing unit object selected
        
        None if any project or processing unit is selected
        """
        for key in self.__itemTreeDict.keys():
            if self.__itemTreeDict[key] != self.selectedItemTree:
                continue
            
            if self.__projectObjDict.has_key(key) == True:
                fatherObj = self.__projectObjDict[key]
            else:
                fatherObj = self.__puObjDict[key]
            
            return fatherObj
        
        return None
    
    def _WarningWindow(self, text, information):
        
        msgBox = QtGui.QMessageBox()
        msgBox.setText(text)
        msgBox.setInformativeText(information)
        msgBox.setStandardButtons(QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
        msgBox.setDefaultButton(QtGui.QMessageBox.Ok)
        ret = msgBox.exec_()
        
        answer = False
        
        if ret == QtGui.QMessageBox.Ok:
            answer = True
            
        return answer
    
    def __getNewProjectId(self):
        
        loadProject = False
        
        for thisId in range(1,10):
            newId = str(thisId)
            if newId in self.__projectObjDict.keys():
                continue
            
            loadProject = True
            projectId = newId
            break
        
        if not loadProject:
            self.console.clear()
            self.console.append("The maximum number of projects has been loaded, a new project can not be loaded")
            return None
        
        return projectId
    
    def openProject(self):
        
        self.actionStart.setEnabled(False)
        self.actionStarToolbar.setEnabled(False)
        
        self.create = False
        self.frame_2.setEnabled(True)
        
        # print self.dir
        filename = str(QtGui.QFileDialog.getOpenFileName(self, "Open text file", self.pathWorkSpace, self.tr("Text Files (*.xml)")))
        
        projectObjLoad = Project()
        
        try:
            projectObjLoad.readXml(filename)
        except:
            self.console.clear()
            self.console.append("The selected xml file could not be loaded ...")
            return 0
        
        self.refreshProjectWindow(projectObjLoad)
        self.refreshProjectProperties(projectObjLoad)
        
        projectId = projectObjLoad.id
        
        if projectId in self.__projectObjDict.keys():
            
#             answer = self._WarningWindow("You already have a project loaded with the same Id",
#                                             "Do you want to load the file anyway?")
#             if not answer:
#                 return
            
            projectId = self.__getNewProjectId()
            
            if not projectId:
                return
            
            projectObjLoad.updateId(projectId)
        
        self.__projectObjDict[projectId] = projectObjLoad
        
        self.addProject2ProjectExplorer(id=projectId, name=projectObjLoad.name)
            
        self.tabWidgetProject.setEnabled(True)
        self.tabWidgetProject.setCurrentWidget(self.tabProject) 
        # Disable tabProject after finish the creation
        self.tabProject.setEnabled(True)   
        puObjorderList = OrderedDict(sorted(projectObjLoad.procUnitConfObjDict.items(), key=lambda x: x[0]))
        
        for puId, puObj in puObjorderList.items():
            
            self.__puObjDict[puId] = puObj

            if puObj.name == "SendToServer":
                self.saveFTPFromProcUnitObj(puObj)
            
            ############## COMPATIBLE WITH OLD VERSIONS ################
            operationObj = puObj.getOperationObj("SendByFTP")
            
            if operationObj:
                self.saveFTPFromOpObj(operationObj)
            ############################################################
            
            if puObj.inputId == '0':
                continue
            
            self.addPU2PELoadXML(puObj)
            
            self.refreshPUWindow(puObj)
            self.refreshPUProperties(puObj)
            self.showtabPUCreated(datatype=puObj.datatype)
                
        self.console.clear()
        self.console.append("The selected xml file has been loaded successfully")
        
        self.actionStart.setEnabled(True)
        self.actionStarToolbar.setEnabled(True)

    def create_updating_timer(self):
        self.comm_data_timer = QtCore.QTimer(self)
        self.comm_data_timer.timeout.connect(self.on_comm_updating_timer)
        self.comm_data_timer.start(1000)
     
    def on_comm_updating_timer(self):
        # Verifica si algun proceso ha sido inicializado y sigue ejecutandose
        # Si el proceso se ha parado actualizar el GUI (stopProject)
        if not self.__enable:
            return
         
        if self.controllerThread.isFinished():
            self.stopProject()
    
#     def jobStartedFromThread(self, success):
#         
#         self.console.clear()
#         self.console.append("Job started")
#     
#     def jobFinishedFromThread(self, success):
#         
#         self.stopProject()
    
    def playProject(self, ext=".xml", save=1):
        
        projectObj = self.getSelectedProjectObj()
        
        if not projectObj:
            print "Please select a project before pressing PLAY button"
            return
        
        if save:
            filename = self.saveProject()
            if filename == None:
                self.console.append("Process did not initialize.")
                return
        else:
            filename = TEMPORAL_FILE
            projectObj.writeXml( os.path.join(self.pathWorkSpace,filename) )

        self.actionStart.setEnabled(False)
        self.actionPause.setEnabled(True)
        self.actionStop.setEnabled(True)
        
        self.actionStarToolbar.setEnabled(False)
        self.actionPauseToolbar.setEnabled(True)
        self.actionStopToolbar.setEnabled(True)
        
        self.console.append("Please Wait...")
        
        self.controllerThread = ControllerThread(filename)
        
#         QObject.connect( self.controllerThread, SIGNAL( "jobFinished( PyQt_PyObject )" ), self.jobFinishedFromThread )
#         QObject.connect( self.controllerThread, SIGNAL( "jobStarted( PyQt_PyObject )" ), self.jobStartedFromThread )
        self.console.clear()
        self.controllerThread.start()
        sleep(0.5)
        self.__enable = True
        
    def stopProject(self):
        
        self.__enable = False
        
#         self.commCtrlPThread.cmd_q.put(ProcessCommand(ProcessCommand.STOP, True))
        self.controllerThread.stop()
        
        while self.controllerThread.isRunning():
            sleep(0.5)
            
        self.actionStart.setEnabled(True)
        self.actionPause.setEnabled(False)
        self.actionStop.setEnabled(False)
        
        self.actionStarToolbar.setEnabled(True)
        self.actionPauseToolbar.setEnabled(False)
        self.actionStopToolbar.setEnabled(False)
        
        self.restorePauseIcon()
     
    def pauseProject(self):
        
#         self.commCtrlPThread.cmd_q.put(ProcessCommand(ProcessCommand.PAUSE, data=True))
        self.controllerThread.pause()
        
        self.actionStart.setEnabled(False)
        self.actionPause.setEnabled(True)
        self.actionStop.setEnabled(True)
        
        self.actionStarToolbar.setEnabled(False)
        self.actionPauseToolbar.setEnabled(True)
        self.actionStopToolbar.setEnabled(True)
               
    def saveProject(self, filename=None):
        
        self.actionStart.setEnabled(False)
        self.actionStarToolbar.setEnabled(False)
        
        projectObj = self.getSelectedProjectObj()  
        self.refreshGraphicsId()
        
        sts = True
        selectedItemObj = self.getSelectedItemObj() 
        
        #A Processing Unit has been selected
        if projectObj == selectedItemObj:
            if not self.on_proOk_clicked():
                return None
        
        #A Processing Unit has been selected
        if projectObj != selectedItemObj:
            puObj = selectedItemObj
            
            if puObj.name == 'VoltageProc':
                sts = self.on_volOpOk_clicked()   
            if puObj.name == 'SpectraProc':
                sts = self.on_specOpOk_clicked()   
            if puObj.name == 'SpectraHeisProc':
                sts = self.on_specHeisOpOk_clicked()
            
            if not sts:
                return None
        
        self.createFTPProcUnitView()
        
        if not filename:
            filename = os.path.join( str(self.pathWorkSpace), "%s%s" %(str(projectObj.name), '.xml') )
            
        projectObj.writeXml(filename)     
        self.console.append("\nPress Play button to start data processing ...")
        
        self.actionStart.setEnabled(True)
        self.actionStarToolbar.setEnabled(True)
        
        return filename
        
    def removeItemTreeFromProject(self):
        """
        Metodo para eliminar el proyecto en el dictionario de proyectos y en el dictionario de vista de arbol
        """
        for key in self.__itemTreeDict.keys():
            
            #Check again because an item can delete multiple items (childs)
            if key not in self.__itemTreeDict.keys():
                continue
            
            if self.__itemTreeDict[key] != self.selectedItemTree:
                continue
            
            if self.__projectObjDict.has_key(key) == True:
                
                del self.__projectObjDict[key]
                del self.__itemTreeDict[key]
                
            else:
                puObj = self.__puObjDict[key]
                idProjectParent = puObj.parentId
                projectObj = self.__projectObjDict[idProjectParent]
                
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
        self.proComDataType.addItem("USRP")
        
        self.proComStartDate.clear()
        self.proComEndDate.clear()
        
        startTime = "00:00:00"
        endTime = "23:59:59"
        starlist = startTime.split(":")
        endlist = endTime.split(":")
        self.proDelay.setText("60")
        self.proSet.setText("")
        
        self.labelSet.show()
        self.proSet.show()
        
        self.labelIPPKm.hide()
        self.proIPPKm.hide()
        
        self.time.setHMS(int(starlist[0]), int(starlist[1]), int(starlist[2])) 
        self.proStartTime.setTime(self.time)
        self.time.setHMS(int(endlist[0]), int(endlist[1]), int(endlist[2])) 
        self.proEndTime.setTime(self.time)
        self.proDescription.clear()    
        self.proOk.setEnabled(False)
#         self.console.append("Please, Write a name Project")
#         self.console.append("Introduce Project Parameters")DC
#         self.console.append("Select data type Voltage( .rawdata)  or Spectra(.pdata)")
    
    def clearPUWindow(self, datatype):
        
        projectObjView = self.getSelectedProjectObj()
        
        if not projectObjView:
            return
        
        puObj = self.getSelectedItemObj()
        inputId = puObj.getInputId()
        inputPUObj = projectObjView.getProcUnitObj(inputId)
        
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

            if inputPUObj.datatype == 'Spectra':
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
        if not(datatype in ['Voltage', 'Spectra', 'Fits', 'USRP']):
            outputstr = 'datatype = %s, this must be either Voltage, Spectra, SpectraHeis or USRP' % datatype
            self.console.append(outputstr)
            parms_ok = False
            datatype = None
        
        ext = str(self.proDataType.text())
        if not(ext in ['.r', '.pdata', '.fits', '.hdf5']):
            outputstr = "extension files must be .r , .pdata, .fits or .hdf5"
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
            if not os.path.isdir(data_path):
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
        
        delay = None
        if read_mode == "Online":
            parms_ok = False
            try:
                delay = int(str(self.proDelay.text()))
                parms_ok = True
            except:
                outputstr = 'Delay: %s, this must be a integer number' % str(self.proDelay.text())
                self.console.append(outputstr)
            
        try:
            set = int(str(self.proSet.text()))
        except:
            # outputstr = 'Set: %s, this must be a integer number' % str(self.proName.text())
            # self.console.append(outputstr)
            # parms_ok = False
            set = None
        
        walk = int(self.proComWalk.currentIndex())
        expLabel = str(self.proExpLabel.text())
        
        return parms_ok, project_name, datatype, ext, data_path, read_mode, delay, walk, set, expLabel

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
            profilesperblock = 0
            
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

    def findDatafiles(self, data_path, ext, walk, expLabel=''):
        
        dateList = []
        fileList = []
        
        if ext == ".r":
            from schainpy.model.io.jroIO_base import JRODataReader
            
            readerObj = JRODataReader()
            dateList = readerObj.findDatafiles(path=data_path,
                                               expLabel=expLabel,
                                               ext=ext,
                                               walk=walk)

        if ext == ".pdata":
            from schainpy.model.io.jroIO_base import JRODataReader
            
            readerObj = JRODataReader()
            dateList = readerObj.findDatafiles(path=data_path,
                                               expLabel=expLabel,
                                               ext=ext,
                                               walk=walk)

        if ext == ".fits":
            from schainpy.model.io.jroIO_base import JRODataReader
            
            readerObj = JRODataReader()
            dateList = readerObj.findDatafiles(path=data_path,
                                               expLabel=expLabel,
                                               ext=ext,
                                               walk=walk)

        if ext == ".hdf5":
            from schainpy.model.io.jroIO_usrp import USRPReader
            
            readerObj = USRPReader()
            dateList = readerObj.findDatafiles(path=data_path)
            
        return dateList
    
    def loadDays(self, data_path, ext, walk, expLabel=''):
        """
        Method to loads day
        """
        self.proOk.setEnabled(False)
        self.proComStartDate.clear()
        self.proComEndDate.clear()
        
        self.dateList = []
        
        if not os.path.isdir(data_path):
            return
        
        self.dataPath = data_path
        
        dateList = self.findDatafiles(data_path, ext=ext, walk=walk, expLabel=expLabel)
        
        if not dateList:
#             self.console.clear()
            outputstr = "The path %s has no files with extension *%s" % (data_path, ext)
            self.console.append(outputstr)
            return
        
        dateStrList = []
        for thisDate in dateList:
            dateStr = thisDate.strftime("%Y/%m/%d")
            
            self.proComStartDate.addItem(dateStr)
            self.proComEndDate.addItem(dateStr)
            dateStrList.append(dateStr)
        
        self.proComStartDate.setCurrentIndex(0)
        self.proComEndDate.setCurrentIndex(self.proComEndDate.count() - 1)
        
        self.dateList = dateStrList
        self.proOk.setEnabled(True)
        
        self.console.clear()
        self.console.append("Successful load")
        
        return self.dateList
        
    def setWorkSpaceGUI(self, pathWorkSpace=None):
        
        if pathWorkSpace == None:
            home = os.path.expanduser("~")
            pathWorkSpace = os.path.join(home,'schain_workspace')
        
        self.pathWorkSpace = pathWorkSpace    
   
    """
    Comandos Usados en Console
    """
    def __del__(self):
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        
    def normalOutputWritten(self, text):
        color_black = QtGui.QColor(0,0,0)
        self.console.setTextColor(color_black)
        self.console.append(text)   
        
    def errorOutputWritten(self, text):
        color_red = QtGui.QColor(255,0,0)
        color_black = QtGui.QColor(0,0,0)
        
        self.console.setTextColor(color_red)
        self.console.append(text)   
        self.console.setTextColor(color_black)
        
    def setGUIStatus(self):
        
        self.setWindowTitle("ROJ-Signal Chain")
        self.setWindowIcon(QtGui.QIcon( os.path.join(FIGURES_PATH,"adn.jpg") ))
        
        self.tabWidgetProject.setEnabled(False)
        self.tabVoltage.setEnabled(False)
        self.tabSpectra.setEnabled(False)
        self.tabCorrelation.setEnabled(False)
        self.frame_2.setEnabled(False)
        
        self.actionCreate.setShortcut('Ctrl+N')
        self.actionOpen.setShortcut('Ctrl+O')
        self.actionSave.setShortcut('Ctrl+S')
        self.actionClose.setShortcut('Ctrl+X')
        
        self.actionStart.setShortcut('Ctrl+1')
        self.actionPause.setShortcut('Ctrl+2')
        self.actionStop.setShortcut('Ctrl+3')
        
        self.actionFTP.setShortcut('Ctrl+F')

        self.actionStart.setEnabled(False)
        self.actionPause.setEnabled(False)
        self.actionStop.setEnabled(False)
            
        self.actionStarToolbar.setEnabled(False)
        self.actionPauseToolbar.setEnabled(False)
        self.actionStopToolbar.setEnabled(False)
        
        self.proName.clear()
        self.proDataPath.setText('')
        self.console.setReadOnly(True)
        self.console.append("Welcome to Signal Chain\nOpen a project or Create a new one")
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
        
        self.propertiesModel = TreeModel()
        self.propertiesModel.initProjectView()
        self.treeProjectProperties.setModel(self.propertiesModel)
        self.treeProjectProperties.expandAll()
        self.treeProjectProperties.allColumnsShowFocus()
        self.treeProjectProperties.resizeColumnToContents(1)
   
        # set Project
        self.proExpLabel.setEnabled(True)  
        self.proDelay.setEnabled(False)  
        self.proSet.setEnabled(True)
        self.proDataType.setReadOnly(True)
         
         # set Operation Voltage
        self.volOpComChannels.setEnabled(False)
        self.volOpComHeights.setEnabled(False)
        self.volOpFilter.setEnabled(False)
        self.volOpComProfile.setEnabled(False)
        self.volOpComCode.setEnabled(False)
        self.volOpFlip.setEnabled(False)
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
        self.volOpFilter.setToolTip('Example: 2')
        self.volOpProfile.setToolTip('Example:0,127')
        self.volOpCohInt.setToolTip('Example: 128')
        self.volOpFlip.setToolTip('ChannelList where flip will be applied. Example: 0,2,3')
        self.volOpOk.setToolTip('If you have finished, please Ok ')
        # tool tip gui volGraph
        self.volGraphfreqrange.setToolTip('Height range. Example: 50,100')
        self.volGraphHeightrange.setToolTip('Amplitude. Example: 0,10000')
        # tool tip gui specOp
        self.specOpnFFTpoints.setToolTip('Example: 128')
        self.specOpProfiles.setToolTip('Example: 128')
        self.specOpippFactor.setToolTip('Example:1.0')
        self.specOpIncoherent.setToolTip('Example: 10')
        self.specOpgetNoise.setToolTip('Example:20,180,30,120 (minHei,maxHei,minVel,maxVel)')
        
        self.specOpChannel.setToolTip('Example: 0,1,2,3')
        self.specOpHeights.setToolTip('Example: 90,180')
        self.specOppairsList.setToolTip('Example: (0,1),(2,3)')
        # tool tip gui specGraph
        
        self.specGgraphChannelList.setToolTip('Example: 0,3,4')
        self.specGgraphFreq.setToolTip('Example: -20,20')
        self.specGgraphHeight.setToolTip('Example: 100,400')
        self.specGgraphDbsrange.setToolTip('Example: 30,170')

        self.specGraphPrefix.setToolTip('Example: EXPERIMENT_NAME')   

        self.labelSet.show()
        self.proSet.show()
        
        self.labelIPPKm.hide()
        self.proIPPKm.hide()
        
        sys.stdout = ShowMeConsole(textWritten=self.normalOutputWritten)
#         sys.stderr = ShowMeConsole(textWritten=self.errorOutputWritten)
        
        
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
    remotefolder = None
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
        self.setGUIStatus()
        
    def setGUIStatus(self):
        self.setWindowTitle("ROJ-Signal Chain")
        self.serverFTP.setToolTip('Example: jro-app.igp.gob.pe')    
        self.folderFTP.setToolTip('Example: /home/wmaster/graficos')
        self.usernameFTP.setToolTip('Example: myusername')
        self.passwordFTP.setToolTip('Example: mypass ')
        self.weightFTP.setToolTip('Example: 0')
        self.expcodeFTP.setToolTip('Example: 0')
        self.subexpFTP.setToolTip('Example: 0')
        self.plotposFTP.setToolTip('Example: 0')
        
    def setParmsfromTemporal(self, server, remotefolder, username, password, ftp_wei, exp_code, sub_exp_code, plot_pos):
        self.serverFTP.setText(str(server))
        self.folderFTP.setText(str(remotefolder))
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
        - remotefolder
        - username
        - password
        - ftp_wei
        - exp_code
        - sub_exp_code
        - plot_pos
        """
        name_server_ftp = str(self.serverFTP.text())
        if not name_server_ftp:
            self.console.clear()
            self.console.append("Please Write  a FTP Server")
            return 0     
        
        folder_server_ftp = str(self.folderFTP.text())
        if not folder_server_ftp:
            self.console.clear()
            self.console.append("Please Write  a Folder")
            return 0  
        
        username_ftp = str(self.usernameFTP.text())
        if not username_ftp:
            self.console.clear()
            self.console.append("Please Write  a User Name")
            return 0   
    
        password_ftp = str(self.passwordFTP.text())
        if not password_ftp:
            self.console.clear()
            self.console.append("Please Write  a passwordFTP")
            return 0
        
        ftp_wei = str(self.weightFTP.text())
        if not ftp_wei == "":
            try:
               ftp_wei = int(self.weightFTP.text())
            except:
                self.console.clear()
                self.console.append("Please Write  a ftp_wei number")
                return 0
        
        exp_code = str(self.expcodeFTP.text())
        if not exp_code == "":
            try:
               exp_code = int(self.expcodeFTP.text())
            except:
                self.console.clear()
                self.console.append("Please Write  a  exp_code number")
                return 0
        
        
        sub_exp_code = str(self.subexpFTP.text())
        if not sub_exp_code == "":
            try:
               sub_exp_code = int(self.subexpFTP.text())
            except:
                self.console.clear()
                self.console.append("Please Write  a  sub_exp_code number")
                return 0
        
        plot_pos = str(self.plotposFTP.text())
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
        server, remotefolder, username, password, ftp_wei, exp_code, sub_exp_code, plot_pos = self.getParmsFromFtpWindow()
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
    remotefolder = None
    username = None
    password = None
    ftp_wei = None
    exp_code = None
    sub_exp_code = None
    plot_pos = None
    create = False
    withoutconfig = False
    createforView = False
    localfolder = None
    extension = None
    period = None
    protocol = None
    
    def __init__(self):
        
        self.create = False
        self.server = None
        self.remotefolder = None
        self.username = None
        self.password = None
        self.ftp_wei = None
        self.exp_code = None
        self.sub_exp_code = None
        self.plot_pos = None
        # self.create = False
        self.localfolder = None
        self.extension = None
        self.period = None
        self.protocol = None
        
    def setwithoutconfiguration(self):
        
        self.create = False
        self.server = "jro-app.igp.gob.pe"
        self.remotefolder = "/home/wmaster/graficos"
        self.username = "wmaster"
        self.password = "mst2010vhf"
        self.withoutconfig = True
        self.localfolder = './'
        self.extension = '.png'
        self.period = 60
        self.protocol = 'ftp'
        self.createforView = True
        
        if not self.ftp_wei:
            self.ftp_wei = 0
        
        if not self.exp_code:
            self.exp_code = 0
            
        if not self.sub_exp_code:
            self.sub_exp_code = 0
        
        if not self.plot_pos:
            self.plot_pos = 0
        
    def save(self, server, remotefolder, username, password, ftp_wei=0, exp_code=0, sub_exp_code=0, plot_pos=0, localfolder='./', extension='.png', period=60, protocol='ftp'):
        
        self.server = server
        self.remotefolder = remotefolder
        self.username = username
        self.password = password
        self.ftp_wei = ftp_wei
        self.exp_code = exp_code
        self.sub_exp_code = sub_exp_code
        self.plot_pos = plot_pos
        self.create = True
        self.withoutconfig = False 
        self.createforView = True 
        self.localfolder = localfolder
        self.extension = extension
        self.period = period
        self.protocol = protocol
        
    def recover(self):
        
        return self.server, self.remotefolder, self.username, self.password, self.ftp_wei, self.exp_code, self.sub_exp_code, self.plot_pos, self.extension, self.period, self.protocol

class ShowMeConsole(QtCore.QObject):
        textWritten = QtCore.pyqtSignal(str)
        def write (self, text):
            self.textWritten.emit(str(text))
