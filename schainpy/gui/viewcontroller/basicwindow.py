# -*- coding: utf-8 -*-
"""
Module implementing MainWindow.
#+++++++++++++INTERFAZ DE USUARIO V1.1++++++++++++++#
"""
import os,sys


import datetime

from PyQt4.QtGui           import QMainWindow
from PyQt4.QtCore          import pyqtSignature
from PyQt4.QtCore          import pyqtSignal
from PyQt4                 import QtCore
from PyQt4                 import QtGui
from timeconversions       import  Doy2Date
from modelProperties       import treeModel

from viewer.ui_unitprocess import Ui_UnitProcess
from viewer.ui_window      import Ui_window
from viewer.ui_mainwindow  import Ui_BasicWindow

print "Nohayproblema"
pathe = os.path.split(os.getcwd())[0]
sys.path.append(pathe)
print "leer", pathe
  
from controller import *


#from controller            import Project,ReadUnitConf,ProcUnitConf,OperationConf,ParameterConf


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
    __projObjDict = None
    __arbolDict = None
    __upObjDict = None
    
    """
    Class documentation goes here.
    #*############VENTANA CUERPO  DEL PROGRAMA##############
    """
    def __init__(self, parent = None):  
        """
        Constructor
        """   
        print "INICIO PROGRAMA "
        QMainWindow.__init__(self, parent)
        self.setupUi(self)
        
        self.__projObjDict = {}
        self.__arbolDict = {}
        self.__upObjDict = {}
        self.__opObjDict= {}
        self.indexclick=None
        self.b=0
               
        self.online=0
        self.datatype=0
        self.dateList=[]
        
        self.proObjList=[]      
        self.idp=0
        self.namep=0
        self.description=0
        self.namepTree=0
        self.valuep=0

        self.upObjList= []     
        self.upn=0
        self.upName=0
        self.upType=0
        self.uporProObjRecover=0
        
        self.readUnitConfObjList=[]
        
        self.upObjVolList=[]
        self.upobjSpecList=[] 
        
        self.operObjList=[]
        
        self.configProject=None
        self.configUP=None
    
        self.readUnitConfObj=None
        self.procUnitConfObj0=None
        self.opObj10=None
        self.opObj12=None
        
        self.setParam()     

  #------------------VistadelNombreCompletousandoelpunteroSobrelosbotones---------------------------#
        QtGui.QToolTip.setFont(QtGui.QFont('SansSerif', 10))
        self.addprojectBtn.setToolTip('Add_New_Project')    
        self.addUnitProces.setToolTip('Add_New_Processing_Unit')  

  #------------------------ManejodeEventosconelmouse------------------------------------------------#
        self.model = QtGui.QStandardItemModel()
        self.treeView.setModel(self.model)
        self.treeView.clicked.connect(self.clickFunctiontree)
        self.treeView.doubleClicked.connect(self.doubleclickFunctiontree)
        self.treeView.expandAll()
        
        #self.treeView.setReadOnly(True)
        self.treeView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.treeView.customContextMenuRequested.connect(self.popup)
        #self.treeView.clicked.connect(self.treefunction1)
        self.model_2=treeModel()


 #-----------------------------------BARRA DE MENU-------------------------------------------------#
 
    def popup(self, pos):
#        for i in self.treeView.selectionModel().selection().indexes():
#            print i.row(), i.column()
        menu = QtGui.QMenu()
        #menu.centralWidget.setObjectName(_fromUtf8("centralWidget"))
        quitAction0 = menu.addAction("Add Branch")
        quitAction1 = menu.addAction("Delete Branch")
        quitAction2 = menu.addAction("Exit")
        #quitAction2 = menu.addAction("Exit")
        print "pos:", pos
        action = menu.exec_(self.mapToGlobal(pos))
        if action == quitAction0:
           self.addUP()
           
        if action == quitAction1:
            for i in self.__arbolDict: 
             if self.__arbolDict[i]==self.indexclick:
                 self.arbolItem=self.__arbolDict[i]
                 print self.arbolItem
                 self.arbolItem.removeRows(self.arbolItem.row(),1)
        if action == quitAction2:
            return
 #----------------------------------- MENU_PROJECT--------------------------------------------------#  
        
    @pyqtSignature("")
    def on_menuFileAbrirObj_triggered(self):
        """
        Abre un archivo de configuracion seleccionado, lee los parametros y
        actualiza los atributos de esta clase; creando los objetos necesarios
        con los parametros leidos desde el archivo.
        """
        print "Leer un archivo xml y extraer sus atributos Not implemented yet"
        
    @pyqtSignature("")
    def on_menuFileCrearObj_triggered(self):
        """
        Crea un proyecto nuevo y lo anade a mi diccionario de proyectos
        y habilita la ventana de configuracion del proyecto.
        
        """
        self.addProject()
             
    @pyqtSignature("")
    def on_menuFileGuardarObj_triggered(self):
        """
        METODO  EJECUTADO CUANDO OCURRE EL EVENTO GUARDAR PROJECTO
        
        Llama al metodo saveProject.
        """ 
#        my_id = arbol_selected()
#        filename = savefindow.show()
#        self.saveProject(id, filename)
        print "probsave"
        self.saveProject()
        
    @pyqtSignature("")
    def on_menuFileCerrarObj_triggered(self):
        """
        METODO EJECUTADO CUANDO OCURRE EL EVENTO CERRAR
        Llama al metodo close.
        """ 
        self.close()
        
   #-----------------------------------MENU_RUN----------------------------------------------------#   
    
    @pyqtSignature("")
    def on_menuRUNStartObj_clicked(self):
        """
        METODO EJECUTADO CUANDO OCURRE EL EVENTO RUN 
        Llama al metodo RUN.
        """ 
        
        print "Leyendo el archivo XML"
        for i in self.__arbolDict:            
            if self.__arbolDict[i]==self.indexclick:
                self.projectObj=self.__projObjDict[i] 
                print "Encontre project"
        filename="C:\WorkspaceGUI\config"+str(self.projectObj.id)+".xml"
        self.projectObj.readXml(filename)
        #controllerObj.printattr()
        
        self.projectObj.createObjects()
        self.projectObj.connectObjects()
        self.projectObj.run()
        print "Not implemented yet"
        
    @pyqtSignature("") 
    def on_menuRUNPausaObj_clicked(self):
        """
        METODO EJECUTADO CUANDO OCURRE EL EVENTO PAUSA
        Llama al metodo PAUSA.
        """ 
        print "Not implemented yet"
    
   #-----------------------------------MENU_OPTION-------------------------------------------------#   
    
    @pyqtSignature("") 
    def on_menuOptConfigLogfileObj_clicked(self):
        """
        METODO EJECUTADO CUANDO OCURRE EL EVENTO ConfigLog
        Llama al metodo close.
        """ 
        print "Not implemented yet"
   
    @pyqtSignature("") 
    def on_menuOptConfigserverObj_clicked(self):
        """
        METODO EJECUTADO CUANDO OCURRE EL EVENTO Config Server
        Llama al metodo close.
        """ 
        print "Not implemented yet"   
    #-----------------------------------MENU_HELP-------------------------------------------------------#   
    
    @pyqtSignature("") 
    def on_menuHELPAboutObj_clicked(self):
        """
        METODO EJECUTADO CUANDO OCURRE EL EVENTO HELP
        Llama al metodo close.
        """ 
        print "Not implemented yet"
    
      
  #-----------------------------------BARRA DE HERRAMIENTAS----------------------------------------#
    
    @pyqtSignature("")
    def on_actOpenObj_triggered(self):
        """
        METODO CARGA UN ARCHIVO DE CONFIGURACION ANTERIOR
        """
        print "Leer un archivo xml y extraer sus atributos Not implemented yet"
       
    @pyqtSignature("")
    def on_actCreateObj_triggered(self):
        """
        CREAR PROJECT ,ANADE UN NUEVO PROYECTO, LLAMA AL MÉTODO QUE CONTIENE LAS OPERACION DE CREACION DE PROYECTOS
        Llama al metodo addProject.
        """
        self.addProject()
                    
    @pyqtSignature("")
    def on_actStopObj_triggered(self):
        """
        METODO EJECUTADO CUANDO OCURRE EL EVENTO PAUSA
        Llama al metodo PAUSA.
        """ 
        print "Not implemented yet"

    @pyqtSignature("")
    def on_actPlayObj_triggered(self):
        """
        METODO EJECUTADO CUANDO OCURRE EL EVENTO PAUSA
        Llama al metodo PAUSA.
        """ 
        print "Leyendo el archivo XML"
        for i in self.__arbolDict:            
            if self.__arbolDict[i]==self.indexclick:
                self.projectObj=self.__projObjDict[i] 
                print "Encontre project"
        filename="C:\WorkspaceGUI\config"+str(self.projectObj.id)+".xml"
        self.projectObj.readXml(filename)
        #controllerObj.printattr()
        
        self.projectObj.createObjects()
        self.projectObj.connectObjects()
        self.projectObj.run()
        print "Not implemented yet"
   
    @pyqtSignature("")
    def on_actSaveObj_triggered(self):
        """
        METODO EJECUTADO CUANDO OCURRE EL EVENTO SAVE
        Llama al metodo SAVE.
        """ 
        self.saveProject()
      
   #-----------------------------------PUSHBUTTON_CREATE PROJECT----------------------------------#      
         
    @pyqtSignature("")
    def on_addprojectBtn_clicked(self):
        """
        CREAR PROJECT ,ANADE UN NUEVO PROYECTO, LLAMA AL MÉTODO QUE CONTIENE LAS OPERACION DE CREACION DE PROYECTOS
        Llama al metodo addProject.
        """ 
        self.addProject()
        self.setProjectParam()
    
   #------------------------------------VENTANA CONFIGURACION PROJECT----------------------------#     
   
    @pyqtSignature("int")
    def on_dataTypeCmbBox_activated(self,index):
        """
        Metodo que identifica que tipo de dato se va a trabajar VOLTAGE O ESPECTRA
        """
        self.dataFormatTxt.setReadOnly(True)
        if index==0:
           self.datatype='.r'
        elif index==1:
            self.datatype='.pdata'
        else :
              self.datatype=''
              self.dataFormatTxt.setReadOnly(False)
        self.dataFormatTxt.setText(self.datatype)  
        self.loadDays()
        
    @pyqtSignature("")
    def on_dataPathBrowse_clicked(self):
        """
        OBTENCION DE LA RUTA DE DATOS
        """
        self.dataPath = str(QtGui.QFileDialog.getExistingDirectory(self, 'Open Directory', './',  QtGui.QFileDialog.ShowDirsOnly))
        self.dataPathTxt.setText(self.dataPath)
        
        self.starDateCmbBox.clear()
        self.endDateCmbBox.clear()
        
        if not os.path.exists(self.dataPath):
            self.dataOkBtn.setEnabled(False)
            return
        
        self.loadDays()  
        
    @pyqtSignature("int")
    def on_starDateCmbBox_activated(self, index):
        """
        SELECCION DEL RANGO DE FECHAS -START DATE
        """
        stopIndex = self.endDateCmbBox.count() - self.endDateCmbBox.currentIndex()
        self.endDateCmbBox.clear()
        
        for i in self.dateList[index:]:
            self.endDateCmbBox.addItem(i)
            
        self.endDateCmbBox.setCurrentIndex(self.endDateCmbBox.count() - stopIndex)

    @pyqtSignature("int")
    def on_endDateCmbBox_activated(self, index):
        """
        SELECCION DEL RANGO DE FECHAS-END DATE
        """
        startIndex=self.starDateCmbBox.currentIndex()
        stopIndex = self.endDateCmbBox.count() - index
        self.starDateCmbBox.clear()
        for i in self.dateList[:len(self.dateList) - stopIndex + 1]:
            self.starDateCmbBox.addItem(i)
        self.starDateCmbBox.setCurrentIndex(startIndex)
    
    @pyqtSignature("int")
    def on_readModeCmBox_activated(self, p0):
        """
        SELECCION DEL MODO DE LECTURA ON=1, OFF=0
        """
        if p0==0:
           self.online=0
        elif p0==1:
            self.online=1  
        
    #---------------PUSHBUTTON_DATA    "      OKBUTTON    "_CONFIGURATION PROJECT--------------------------#    
    
    @pyqtSignature("")
    def on_dataOkBtn_clicked(self):
        """
        Añade al Obj XML de Projecto, name,datatype,date,time,readmode,wait,etc, crea el readUnitProcess del archivo xml.
        Prepara la configuración del diágrama del Arbol del treeView numero 2
        """     
        print "DATOS DEL PROJECT PATH,DATE,TIME"   
           
#               print self.projectObj
#               print i
#               print "get",self.__arbolDict.items()
#               print "keys",self.__arbolDict.keys()

        self.idp += 1
        self.projectObj = Project()
        self.__projObjDict[self.idp] = self.projectObj

        self.description="Think" 
                 
        id      =   self.idp
        name    =   str(self.nameProjectTxt.text())
        desc    =   str(self.description)
         
        self.projectObj.setup(id = id, name=name, description=desc)
        print "self.projectObj.id",self.projectObj.id
        
        #-------AÑADIENDO PARAMETROS A LA UNIDAD DE LECTURA---------#
 
        datatype  =  str(self.dataTypeCmbBox.currentText())
        path      =  str(self.dataPathTxt.text())
        online    =  int(self.online)
        starDate  =  str(self.starDateCmbBox.currentText())
        endDate   =  str(self.endDateCmbBox.currentText())
        
        
        reloj1=self.startTimeEdit.time()
        print 
        
        reloj2=self.endTimeEdit.time()
        
        print reloj1.hour()
        print reloj1.minute()
        print reloj1.second()

        self.readUnitConfObj = self.projectObj.addReadUnit(datatype    =    datatype,
                                                           path        =    path,
                                                           startDate   =    starDate,
                                                           endDate     =    endDate,
                                                           startTime   =    str(reloj1.hour()) +":"+str(reloj1.minute())+":"+ str(reloj1.second()),
                                                           endTime     =    str(reloj2.hour()) +":"+str(reloj2.minute())+":"+ str(reloj2.second()),
                                                           online      =    online)
        print self.readUnitConfObj.datatype,"self.readUnitConfObj.datatype"
         
        self.readUnitConfObjList.append(self.readUnitConfObj)           
             
        #--------VISUALIZACION EN LA VENTANA PROJECT PROPERTIES-----------------#
        #self.model_2=treeModel()        
        self.model_2=treeModel()
        self.model_2.setParams(name       =  self.projectObj.name,
                               directorio =  path,
                               workspace  =  "C:\\WorkspaceGUI",
                               remode     =  str(self.readModeCmBox.currentText()), 
                               dataformat =  datatype, 
                               date       =  str(starDate)+"-"+str(endDate),
                               initTime   =  str(reloj1.hour()) +":"+str(reloj1.minute())+":"+ str(reloj1.second()),
                               endTime    =  str(reloj2.hour()) +":"+str(reloj2.minute())+":"+ str(reloj2.second()),
                               timezone   =  "Local" ,
                               Summary    =  "test de prueba")                                                 
        
        self.model_2.arbol()
        self.model_2.showtree()
        self.treeView_2.setModel(self.model_2)
        self.treeView_2.expandAll()  
        
        #--------CREACIÓNDELDIAGRAMADELARBOL------------------------#                   
        self.parentItem = self.model.invisibleRootItem()
        #self.__arbolDict[self.idp] =   QtGui.QStandardItem(QtCore.QString(name).arg(self.idp))
        self.__arbolDict[self.idp] =   QtGui.QStandardItem(QtCore.QString(name).arg(self.idp))

        print self.__arbolDict[self.idp]
        self.parentItem.appendRow(self.__arbolDict[self.idp])
        self.parentItem=self.__arbolDict[self.idp]
    
        #--------BLOQUEO-------#    
        self.tabProject.setEnabled(False)

        
   #-----------------PUSHBUTTON_ADD_PROCESSING UNIT PROJECT------------------#    
    @pyqtSignature("")
    def on_addUnitProces_clicked(self):
        """
        CREAR PROCESSING UNIT ,añade unidad de procesamiento, LLAMA AL MÉTODO addUP QUE CONTIENE LAS OPERACION DE CREACION DE UNIDADES DE PROCESAMIENTO
        Llama al metodo addUP.
        """
        self.addUP()      
        
    def setParam(self):
        
        self.tabWidgetProject.setEnabled(False)
        self.tabVoltage.setEnabled(False)
        self.tabSpectra.setEnabled(False)
        self.tabCorrelation.setEnabled(False)
        self.dataPathTxt.setText('C:\data2')
        self.nameProjectTxt.setText("Test")
        self.numberChannelopVol.setEnabled(False)
        self.lineFilteropVolCEB.setEnabled(False)
        self.lineHeighProfileTxtopVol.setEnabled(False)
        self.numberIntegration.setEnabled(False)
        self.valuenFFTPointOpSpec.setEnabled(False)
        self.lineProfileSelecopVolCEB.setEnabled(False)
        self.valueSelecChOpVol.setEnabled(False)
        self.valueSelecHeigOpVol.setEnabled(False)
        self.profileSelecOpVol.setEnabled(False)
        self.decodeCcob.setEnabled(False)
        self.decodeMcob.setEnabled(False)
        
        self.wiWineTxtGraphicsVol.setEnabled(False)
        self.channelLisstTxtVol.setEnabled(False)
        self.xminTxtVol.setEnabled(False)
        self.yminTxtVol.setEnabled(False)
        
        self.setDisableAllSpecop()
        self.setDisableAllElementSpecGraph()
#         self.winTitleGraphSpec.setEnabled(False)
#         self.channelListgraphSpec.setEnabled(False)
#         self.xminGraphSpec.setEnabled(False)
#         self.yminGraphSpec.setEnabled(False)
#         self.zminGraphSpec.setEnabled(False)
#         self.timeRangeGraphSpec.setEnabled(False)   
#         self.dataPathTxtSpec.setEnabled(False)
#         self.dataPrefixGraphSpec.setEnabled(False) 
        
    def setProjectParam(self):
        self.nameProjectTxt.setText("Test")
        self.dataPathTxt.setText('C:\data2')
        self.dataTypeCmbBox.clear()
        self.dataTypeCmbBox.addItem("Voltage")
        self.dataTypeCmbBox.addItem("Spectra")
        startTime="00:00:00"
        endTime="23:59:59"
        starlist=startTime.split(":")
        endlist=endTime.split(":")
        print starlist[0],starlist[1],starlist[2]
        print endlist[0],endlist[1],endlist[2]
        self.time.setHMS(int(starlist[0]),int(starlist[1]),int(starlist[2])) 
        self.startTimeEdit.setTime(self.time)
        self.time.setHMS(int(endlist[0]),int(endlist[1]),int(endlist[2])) 
        self.endTimeEdit.setTime(self.time)

    def clickFunctiontree(self,index):
        
        self.indexclick= index.model().itemFromIndex(index)
        print "OPCION CLICK"
        print "ArbolDict",self.indexclick
        print "name:",self.indexclick.text()
        #print self.tabWidgetProject.currentIndex()
        



    def doubleclickFunctiontree(self):
        for i in self.__arbolDict: 
            if self.__arbolDict[i]==self.indexclick:
                print "INDEXCLICK=ARBOLDICT",i
                if self.__projObjDict.has_key(i)==True:       
                    self.tabWidgetProject.setCurrentWidget(self.tabProject)
                    self.nameProjectTxt.setText(str(self.__projObjDict[i].name))
                    self.dataTypeCmbBox.clear()
                    self.dataTypeCmbBox.addItem(str(self.readUnitConfObjList[i-1].datatype))
                    print str(self.readUnitConfObjList[i-1].path)
                    self.dataPathTxt.setText(str(self.readUnitConfObjList[i-1].path))
                    self.starDateCmbBox.clear()
                    self.endDateCmbBox.clear()
                    self.starDateCmbBox.addItem(str(self.readUnitConfObjList[i-1].startDate))
                    self.endDateCmbBox.addItem(str(self.readUnitConfObjList[i-1].endDate))
                    startTime=self.readUnitConfObjList[i-1].startTime 
                    endTime=self.readUnitConfObjList[i-1].endTime
                    starlist=startTime.split(":")
                    endlist=endTime.split(":")
                    print starlist[0],starlist[1],starlist[2]
                    print endlist[0],endlist[1],endlist[2]
                    self.time.setHMS(int(starlist[0]),int(starlist[1]),int(starlist[2])) 
                    self.startTimeEdit.setTime(self.time)
                    self.time.setHMS(int(endlist[0]),int(endlist[1]),int(endlist[2])) 
                    self.endTimeEdit.setTime(self.time)
                    
                            #--------VISUALIZACION EN LA VENTANA PROJECT PROPERTIES-----------------#
#                     self.model_2=treeModel()        
#                     self.model_2.setParams(name       = str(self.__projObjDict[i].name),
#                                            directorio = str(self.readUnitConfObjList[i-1].path),
#                                            workspace  =  "C:\\WorkspaceGUI",
#                                            remode     =  str(self.readModeCmBox.currentText()), 
#                                            dataformat =  "Voltage", 
#                                            date       =  str(self.readUnitConfObjList[i-1].startDate)+"-"+str(self.readUnitConfObjList[i-1].endDate),
#                                            initTime   =  str(starlist[0]) +":"+str(starlist[1])+":"+ str(starlist[2]),
#                                            endTime    =  str(endlist[0]) +":"+str(endlist[1])+":"+ str(endlist[2]),
#                                            timezone   =  "Local" ,
#                                            Summary    =  "test de prueba")                                                    
#                     
#                     self.model_2.arbol()
#                     self.model_2.showtree()
#                     self.treeView_2.setModel(self.model_2)
#                     self.treeView_2.expandAll() 
                    
                    #self.dataPathTxt.setText(str(self.__projObjDict[i].addReadUnit.path()))
               
        if self.indexclick.text()=='Voltage':
           self.tabVoltage.setEnabled(True)
           self.tabWidgetProject.setCurrentWidget(self.tabVoltage)
#           for i in self.__opObjDict[i]
#                self.OpObj=

        if self.indexclick.text()=='Spectra':
           self.tabSpectra.setEnabled(True) 
           self.tabWidgetProject.setCurrentWidget(self.tabSpectra)
           
            
        if self.indexclick.text()=='Correlation':
           self.tabCorrelation.setEnabled(True) 
           self.tabWidgetProject.setCurrentWidget(self.tabCorrelation) 
                                                                         
    def addProject(self):
      
        self.tabWidgetProject.setEnabled(True)
        #---------------KILL-----------------#
#        self.tabWidgetProject.setTabsClosable(True)  
#        self.tabWidgetProject.tabCloseRequested.connect(self.tabWidgetProject.removeTab)
        #------------------------------------#
        self.tabWidgetProject.setCurrentWidget(self.tabProject)
        self.tabProject.setEnabled(True)
        #self.tabVoltage.setEnabled(False)
        print "HABILITA WIDGET"        
       
    def existDir(self, var_dir):
        """
        METODO PARA VERIFICAR SI LA RUTA EXISTE-VAR_DIR
        VARIABLE DIRECCION
        """
        if os.path.isdir(var_dir): 
            return True
        else:
            self.textEdit.append("Incorrect path:" + str(var_dir))
            return False
    
    def searchData(self, path, ext, expLabel='', walk=1):
        
        dateList = []
        fileList = []
        
        if walk == 0:
            files = os.listdir(path)    
            for thisFile in files:
                if not os.path.isfile(thisFile):
                    continue
                thisExt = os.path.splitext(thisFile)[-1]
                
                if thisExt != ext:
                    continue
                
                fileList.append(file)
            
            for thisFile in fileList:
                
                if not isRadarFile(thisFile):
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
                    continue
                
                doypath = os.path.join(path, thisDir, expLabel)
                
                files = os.listdir(doypath)
                fileList = []
                
                for thisFile in files:
                    
                    if os.path.splitext(thisFile)[-1] != ext:
                        continue
                    
                    if not isRadarFile(thisFile):
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
        METODO PARA CARGAR LOS DIAS
        """
        ext = self.datatype
        path = str(self.dataPathTxt.text())
        
        self.starDateCmbBox.clear()
        self.endDateCmbBox.clear()

        dateList = self.searchData(path, ext=ext)
        #Se cargan las listas para seleccionar StartDay y StopDay (QComboBox)
        self.dateList = dateList
        
        for thisDate in dateList:
            self.starDateCmbBox.addItem(thisDate)
            self.endDateCmbBox.addItem(thisDate)
            
        self.endDateCmbBox.setCurrentIndex(self.starDateCmbBox.count()-1) 
        self.dataOkBtn.setEnabled(True) 
            
    def HourChanged(self): 
        #self.hour = self.HourScrollBar.value() 
        self.set_time() 

    def MinChanged(self): 
        #self.min = self.MinScrollBar.value() 
        self.set_time() 

    def SecChanged(self): 
        #self.sec = self.SecScrollBar.value() 
        self.set_time() 

    def set_time(self): 
        self.time.setHMS(self.hour, self.min, self.sec) 
        self.startTimeEdit.setTime(self.time)
        
        self.endTimeEdit.setTime(self.time)
        
       
    def addUP(self):
        
        self.configUP=UnitProcess(self)
        
        for i in self.__arbolDict:       
            if self.__arbolDict[i]==self.indexclick:
               print "INDEXCLICK=ARBOLDICT",i
               if self.__projObjDict.has_key(i)==True:
                   self.projectObj=self.__projObjDict[int(i)]
                   print "self.projectObj.id",self.projectObj.id
                   #-----------Añadiendo Tipo de dato y Projecto a la Clase UnitProcess que abre la ventana de selección----#
                   self.configUP.dataTypeProject=str(self.dataTypeCmbBox.currentText())
                   self.configUP.getfromWindowList.append(self.projectObj) 
                                      
#                   for i in self.projectObj.procUnitConfObjDict:
#                      if self.projectObj.procUnitConfObjDict[i].getElementName()=='ProcUnit':
#                         self.upObj=self.projectObj.procUnitConfObjDict[i]
#                         self.configUP.getfromWindowList.append(self.upObj)          
               else:
                   #-----------Añadiendo Unidad de Procesamiento a una Unidad de Procesamiento----#
                   self.upObj=self.__upObjDict[i]
                   print "self.upObj.id",self.upObj.id
                   self.configUP.getfromWindowList.append(self.upObj)

        self.configUP.loadTotalList()
        self.configUP.show()      
        self.configUP.closed.connect(self.createUP)

    def createUP(self):
        
        print "ADICION DE BRANCH Y ID"
        
        if not self.configUP.create:
            return
        
        self.uporProObjRecover=self.configUP.getFromWindow
        
        self.upType = self.configUP.typeofUP
        for i in self.__arbolDict: 
             print self.__arbolDict[i],"VALORES DEL DIC"
             if self.__arbolDict[i]==self.indexclick:
                  if self.__projObjDict.has_key(i)==True:
                    # print "self.__projObjDict[int(i)]" ,__projObjDict[int(i)] 
                     self.projectObj=self.__projObjDict[int(i)] 
                     print self.__projObjDict[int(i)]
                     
                  if self.__upObjDict.has_key(i)==True:
                      print "Entro al else"
                      print self.__upObjDict.items()
                      self.upObj=self.__upObjDict[i]
                      getIdProject=self.upObj.id[0]
                      print getIdProject
                      self.projectObj=self.__projObjDict[int(getIdProject)] 
        
        datatype=str(self.upType)
        uporprojectObj=self.uporProObjRecover
        
        if uporprojectObj.getElementName()=='ProcUnit':
             inputId=uporprojectObj.getId()
        else:
            inputId=self.readUnitConfObjList[uporprojectObj.id-1].getId()
       
        print 'uporprojectObj.id:',uporprojectObj.id,'inputId:',inputId       
        self.procUnitConfObj1 = self.projectObj.addProcUnit(datatype=datatype, inputId=inputId)
        self.__upObjDict[self.procUnitConfObj1.id]= self.procUnitConfObj1    
        print "PRIMERA UP_VEAMOS",self.__upObjDict.items()
        self.parentItem=self.__arbolDict[uporprojectObj.id]
        #print "i","self.__arbolDict[i]",i ,self.__arbolDict[i] 
        self.numbertree=int(self.procUnitConfObj1.getId())-1
        print self.procUnitConfObj1.id," ID DE LA UNIDAD DE PROCESAMIENTO "
        #self.__arbolDict[self.procUnitConfObj1.id]=QtGui.QStandardItem(QtCore.QString(datatype+"%1").arg(self.numbertree))
        
        
        
        self.__arbolDict[self.procUnitConfObj1.id]=QtGui.QStandardItem(QtCore.QString(datatype).arg(self.numbertree))
        self.parentItem.appendRow(self.__arbolDict[self.procUnitConfObj1.id])        
        self.parentItem=self.__arbolDict[self.procUnitConfObj1.id]
    #   self.loadUp()
        self.treeView.expandAll()

    def resetopVolt(self):
        self.selecChannelopVolCEB.setChecked(False)
        self.selecHeighopVolCEB.setChecked(False)
        self.coherentIntegrationCEB.setChecked(False)
        self.profileSelecopVolCEB.setChecked(False)
        self.FilterCEB.setChecked(False)
        
        #self.selecChannelopVolCEB.setEnabled(False)
        self.lineHeighProfileTxtopVol.clear()
        self.lineProfileSelecopVolCEB.clear()
        self.numberChannelopVol.clear()
        self.numberIntegration.clear()
        self.lineFilteropVolCEB.clear()
    
    def resetopSpec(self):
        
        self.nFFTPointOpSpecCEB.setChecked(False)
        self.valuenFFTPointOpSpec.clear()
    
    def resetgraphSpec(self):
        self.SpectraPlotGraphCEB.setChecked(False)
        self.CrossSpectraPlotGraphceb.setChecked(False)
        self.RTIPlotGraphCEB.setChecked(False)                  

    def saveProject(self):
        print "entro"
        #filename="C:\WorkspaceGUI\config1.xml"
        for i in self.__arbolDict:            
            if self.__arbolDict[i]==self.indexclick:
                self.projectObj=self.__projObjDict[i] 
                print "Encontre project"
        filename="C:\WorkspaceGUI\config"+str(self.projectObj.id)+".xml"
        print "Escribo Project"
        self.projectObj.writeXml(filename)

# -----------------OPCIONES DE CONFIGURACION VOLTAGE---------------------------#      

    @pyqtSignature("")
    def on_dataGraphicsVolPathBrowse_clicked(self):
        """
        OBTENCION DE LA RUTA DE DATOS
        """
        self.dataPath = str(QtGui.QFileDialog.getExistingDirectory(self, 'Open Directory', './',  QtGui.QFileDialog.ShowDirsOnly))
        self.dataPathtxtGraphicsVol.setText(self.dataPath)
        
        if not os.path.exists(self.dataPath):
            self.dataGraphVolOkBtn.setEnabled(False)
            return

# -----------------VENTANA CONFIGURACION DE VOLTAGE---------------------------#     

    @pyqtSignature("int")
    def on_selecChannelopVolCEB_stateChanged(self, p0):
        """
        Check Box habilita operaciones de Selecci�n de Canales
        """
        if  p0==2:
            self.numberChannelopVol.setEnabled(True)
            self.valueSelecChOpVol.setEnabled(True)
            print " Ingresa seleccion de Canales"
        if  p0==0:
            self.numberChannelopVol.setEnabled(False)
            self.valueSelecChOpVol.setEnabled(False)
            print " deshabilitado" 
            
    @pyqtSignature("int")
    def on_selecHeighopVolCEB_stateChanged(self, p0):
        """
        Check Box habilita operaciones de Selecci�n de Alturas 
        """
        if  p0==2:
            self.lineHeighProfileTxtopVol.setEnabled(True)
            self.valueSelecHeigOpVol.setEnabled(True)
            print " Select Type of Profile"
        if  p0==0:
            self.lineHeighProfileTxtopVol.setEnabled(False)
            self.valueSelecHeigOpVol.setEnabled(False)
            print " deshabilitado" 
            

    @pyqtSignature("int")
    def on_filterCEB_stateChanged(self, p0):
         """
         Name='Decoder', optype='other'
         """
         if  p0==2:
            self.lineFilteropVolCEB.setEnabled(True)
            print " Select Type of Profile"
         if  p0==0:
            self.lineFilteropVolCEB.setEnabled(False)
            print " deshabilitado" 
         
    @pyqtSignature("int")
    def on_profileSelecopVolCEB_stateChanged(self, p0):
        """
        Check Box habilita ingreso  del rango de Perfiles
        """
        if  p0==2:
            self.lineProfileSelecopVolCEB.setEnabled(True)
            self.profileSelecOpVol.setEnabled(True)
            print " Select Type of Profile"
        if  p0==0:
            self.lineProfileSelecopVolCEB.setEnabled(False)
            self.profileSelecOpVol.setEnabled(False)
            print " deshabilitado" 
    
   
    @pyqtSignature("int")
    def on_decodeCEB_stateChanged(self, p0):
        """
        Check Box habilita ingresode del numero de Integraciones a realizar
        """
        if  p0==2:
            self.decodeCcob.setEnabled(True)
            self.decodeMcob.setEnabled(True)
            print "Choose number of Cohint"
        if  p0==0:
            print " deshabilitado"   
            self.decodeCcob.setEnabled(False)
            self.decodeMcob.setEnabled(False)
    
            
    @pyqtSignature("int")
    def on_coherentIntegrationCEB_stateChanged(self, p0):
        """
        Check Box habilita ingresode del numero de Integraciones a realizar
        """
        if  p0==2:
            self.numberIntegration.setEnabled(True)
            print "Choose number of Cohint"
        if  p0==0:
            print " deshabilitado"   
            self.numberIntegration.setEnabled(False)
            
    #-----------------------VOL_PUSHBUTTON_ACCEPT_OPERATION----------------------------#       
    
    @pyqtSignature("")
    def on_dataopVolOkBtn_clicked(self):
        """
        BUSCA EN LA LISTA DE OPERACIONES DEL TIPO VOLTAJE Y LES A�ADE EL PARAMETRO ADECUADO ESPERANDO LA ACEPTACION DEL USUARIO
        PARA AGREGARLO AL ARCHIVO DE CONFIGURACION XML
        """   
        for i in self.__arbolDict:       
            if self.__arbolDict[i]==self.indexclick:
               print "INDEXCLICK=ARBOLDICT",i
               if self.__upObjDict.has_key(i)==True:
                   self.upObj=self.__upObjDict[i]
                   print self.__upObjDict[i].name
                   print "TamañodeupObjDict",len(self.__upObjDict)
                  # if len(self.__upObjDict)>=1 and len(self.__upObjDict)> self.b:
                       
                   if self.selecChannelopVolCEB.isChecked():
                         if  self.valueSelecChOpVol.currentIndex()== 0:
                             opObj10=self.upObj.addOperation(name="selectChannels")
                             self.operObjList.append(opObj10)
                             value=self.numberChannelopVol.text()                    
                             opObj10.addParameter(name='channelList', value=value, format='intlist')
                         else:
                             opObj10=self.upObj.addOperation(name="selectChannelsByIndex")
                             self.operObjList.append(opObj10)
                             value=self.numberChannelopVol.text()                    
                             opObj10.addParameter(name='channelIndexList', value=value, format='intlist')
                             print "channel"
                                                     
                   if self.selecHeighopVolCEB.isChecked():
                         if  self.valueSelecHeigOpVol.currentIndex()== 0:
                             opObj10=self.upObj.addOperation(name='selectHeights')
                             value=self.lineHeighProfileTxtopVol.text()
                             valueList=value.split(',')
                             opObj10.addParameter(name='minHei', value=valueList[0], format='float')
                             opObj10.addParameter(name='maxHei', value=valueList[1], format='float')
                         else:
                             opObj10=self.upObj.addOperation(name='selectHeightsByIndex')
                             value=self.lineHeighProfileTxtopVol.text()
                             valueList=value.split(',')
                             opObj10.addParameter(name='minIndex', value=valueList[0], format='float')
                             opObj10.addParameter(name='maxIndex', value=valueList[1], format='float')
                                
                         print "height"
                             
                   if self.filterCEB.isChecked():
                         opObj10=self.upObj.addOperation(name='filterByHeights')
                         value=self.lineFilteropVolCEB.text()
                         opObj10.addParameter(name='window', value=value, format='int')
                         print "filter"    
     
                   if self.profileSelecopVolCEB.isChecked():
                         obj10=self.upObj.addOperation(name='ProfileSelector', optype='other')
                         if  self.profileSelecOpVol.currentIndex()== 0:
                             self.operObjList.append(opObj10)
                             value=self.lineProfileSelecopVolCEB.text()
                             obj10.addParameter(name='profileList', value=value, format='intlist')
                         else:
                             self.operObjList.append(opObj10)
                             value=self.lineProfileSelecopVolCEB.text()
                             obj10.addParameter(name='profileRangeList', value=value, format='intlist')
                             print "profile"
          
                   if self.decodeCEB.isChecked():
                        opObj10=self.upObj.addOperation(name='Decoder') 
                        if self.decodeCcob.currentIndex()==0:
                            opObj10.addParameter(name='code', value='1,1,-1,-1,-1,1', format='floatlist')
                            opObj10.addParameter(name='nCode', value='2', format='int')
                            opObj10.addParameter(name='nBaud', value='3', format='int')
                        if self.decodeCcob.currentIndex()==1:
                            opObj10.addParameter(name='code', value='1,1,−1,1,-1,-1,1,-1', format='floatlist')
                            opObj10.addParameter(name='nCode', value='2', format='int')
                            opObj10.addParameter(name='nBaud', value='4', format='int')
                        if self.decodeCcob.currentIndex()==2:
                            opObj10.addParameter(name='code', value='1,1,1,−1,1,-1,-1,-1,1,-1', format='floatlist')
                            opObj10.addParameter(name='nCode', value='2', format='int')
                            opObj10.addParameter(name='nBaud', value='5', format='int')    
                        if self.decodeCcob.currentIndex()==3:
                            opObj10.addParameter(name='code', value='1,1,1,−1,−1,1,−1,-1,-1,-1,1,1,-1,1', format='floatlist')
                            opObj10.addParameter(name='nCode', value='2', format='int')
                            opObj10.addParameter(name='nBaud', value='7', format='int')
                        if self.decodeCcob.currentIndex()==4:
                            opObj10.addParameter(name='code', value='1,1,1,−1,−1,−1,1,−1,−1,1,−1,-1 ,-1 ,-1 ,1 ,1 ,1 ,-1 ,1 ,1 ,-1 ,1', format='floatlist')
                            opObj10.addParameter(name='nCode', value='2', format='int')
                            opObj10.addParameter(name='nBaud', value='11', format='int')    
                        if self.decodeCcob.currentIndex()==5:
                            opObj10.addParameter(name='code', value='1,1,1,1,1,−1,−1,1,1,−1,1,−1,1,-1,-1,-1,-1,-1,1,1,-1,-1,1,-1,1,-1', format='floatlist')
                            opObj10.addParameter(name='nCode', value='2', format='int')
                            opObj10.addParameter(name='nBaud', value='13', format='int')   
                        
                        if self.decodeMcob.currentIndex()==0:
                           opObj10.addParameter(name='mode', value='0', format='int')
       
                        if self.decodeMcob.currentIndex()==1:   
                            opObj10.addParameter(name='mode', value='1', format='int') 
                  
                        if self.decodeMcob.currentIndex()==2:
                            opObj10.addParameter(name='mode', value='2', format='int')
                              
                   if self.coherentIntegrationCEB.isChecked():
                           opObj10=self.upObj.addOperation(name='CohInt', optype='other')
                           print opObj10.id
                           self.operObjList.append(opObj10)
                           value=self.numberIntegration.text()
                           opObj10.addParameter(name='n', value=value, format='int') 
                           print "Coherent"
                           
                           
#                        print "TamañodeupObjDict",len(self.__upObjDict)
#                        self.b=len(self.__upObjDict)
#                        print "self.b", self.b                      
#                        self.model_2.properties_projecto("estaesunaprueba")
#                        anadir=self.model_2.properties_projecto("estaesunaprueba")
#                        self.model_2.addProjectproperties(anadir)
#                        self.model_2.showtree()
#                        self.treeView_2.setModel(self.model_2)
#                        self.treeView_2.expandAll() 
#                    else:
#                         print"It doesn't works"
                                      
#            self.o     
     
         
    # -----------------VENTANA CONFIGURACION GRAPH VOLTAGE---------------------------#                   
   
    @pyqtSignature("int")
    def on_dataTypeSelecVol_activated(self,index):
        """
        Metodo que identifica que tipo de dato se va a trabajar VOLTAGE O ESPECTRA
        """
        
        if index==0:
           self.wiWineTxtGraphicsVol.setEnabled(True)
           self.channelLisstTxtVol.setEnabled(True)
           self.xminTxtVol.setEnabled(True)
           self.yminTxtVol.setEnabled(True)    
    
    @pyqtSignature(" ")
    def on_dataGraphVolOkBtn_clicked(self):
        """
        GRAPH
        """   
        for i in self.__arbolDict:       
            if self.__arbolDict[i]==self.indexclick:
               print "INDEXCLICK=ARBOLDICT",i
               if self.__upObjDict.has_key(i)==True:
                   self.upObj=self.__upObjDict[i]
                   print self.__upObjDict[i].name
                   
                   if self.valueSelecChOpVol.currentIndex()==0:
                       opObj10=self.upObj.addOperation(name='Scope', optype='other')
                       self.operObjList.append(opObj10)
                       wintitle=self.wiWineTxtGraphicsVol.text()      
                       channelList=self.channelLisstTxtVol.text()
                       xvalue= self.xminTxtVol.text()         
                       yvalue= self.yminTxtVol.text()      
                     
                       opObj10.addParameter(name='wintitle', value=wintitle, format='str')
                       opObj10.addParameter(name='channelList', value=channelList, format='int')
                       xvalueList=xvalue.split(',')
                       opObj10.addParameter(name='xmin', value=xvalueList[0], format='int')
                       opObj10.addParameter(name='xmax', value=xvalueList[1], format='int')
                       yvalueList=yvalue.split(",")
                       opObj10.addParameter(name='ymin', value=yvalueList[0], format='int')
                       opObj10.addParameter(name='ymax', value=yvalueList[1], format='int')

                       if self.savedataCEBGraphicsVol.isChecked():
                           opObj10.addParameter(name='save', value='1', format='int')
                           opObj10.addParameter(name='figpath', value= self.dataPathtxtGraphicsVol.text())
                           opObj10.addParameter(name='figfile', value= self.dataPrefixtxtGraphicsVol.text())



    #-------------------------VENTANA DE CONFIGURACION SPECTRA------------------------#     
        
    @pyqtSignature("int")
    def on_nFFTPointOpSpecCEB_stateChanged(self, p0):
        """
        Habilita la opcion de a�adir el par�metro nFFTPoints a la Unidad de Procesamiento .
        """
        if  p0==2:
            self.valuenFFTPointOpSpec.setEnabled(True)
            print " nFFTPoint"
        if  p0==0:
            print " deshabilitado" 
            self.valuenFFTPointOpSpec.setEnabled(False)
                      
    @pyqtSignature("int")
    def on_SelectHeiopSpecCEB_stateChanged(self, p0):
        """
        Habilita la opcion de a�adir el par�metro nFFTPoints a la Unidad de Procesamiento .
        """
        if  p0==2:
            self.valueSelecChOpHei.setEnabled(True)
            self.selecHeiopSpec.setEnabled(True)
            print "selectHeights"
        if  p0==0:
            print " deshabilitado" 
            self.valueSelecChOpHei.setEnabled(False)
            self.selecHeiopSpec.setEnabled(False)            
            
    @pyqtSignature("int")
    def on_selecChannelopSpecCEB_stateChanged(self, p0):
        """
        Habilita la opcion de a�adir el par�metro nFFTPoints a la Unidad de Procesamiento .
        """
        if  p0==2:
            self.valueSelecChOpSpec.setEnabled(True)
            self.numberChannelopSpec.setEnabled(True)
            print "selectChannel"
        if  p0==0:
            print " deshabilitado" 
            self.valueSelecChOpSpec.setEnabled(False)
            self.numberChannelopSpec.setEnabled(False)        
    
    @pyqtSignature("int")
    def on_IncohIntOpSpecCEB_stateChanged(self, p0):
        """
        Habilita la opcion de a�adir el par�metro nFFTPoints a la Unidad de Procesamiento .
        """
        if  p0==2:
            self.valueIncohIntOpSpec.setEnabled(True)

            print "selectIncohInt"
        if  p0==0:
            print " deshabilitado" 
            self.valueIncohIntOpSpec.setEnabled(False)

    @pyqtSignature("int")
    def on_removedcOpSpecCEB_stateChanged(self, p0):
        """
        Habilita la opcion de a�adir el par�metro nFFTPoints a la Unidad de Procesamiento .
        """
        if  p0==2:
            self.valueremoveDCOpSpec.setEnabled(True)

            print "removedcOpSpecCEB"
        if  p0==0:
            print " deshabilitado" 
            self.valueremoveDCOpSpec.setEnabled(False)
            
            
    def setDisableAllSpecop(self):
        self.valuenFFTPointOpSpec.setEnabled(False)
        self.valueSelecChOpHei.setEnabled(False)
        self.selecHeiopSpec.setEnabled(False)            
        self.numberChannelopSpec.setEnabled(False)
        self.valueSelecChOpSpec.setEnabled(False)
        self.valueIncohIntOpSpec.setEnabled(False)
        self.valueremoveDCOpSpec.setEnabled(False)
    #-----------------------SPEC_PUSHBUTTON_ACCEPT_OPERATION----------------------------#   
    
    


    @pyqtSignature("")
    def on_dataopSpecOkBtn_clicked(self):
        """
        AÑADE OPERACION SPECTRA
        """
        print "AÑADEOPERACIONSPECTRA"
        for i in self.__arbolDict:       
            if self.__arbolDict[i]==self.indexclick:
               print "INDEXCLICK=ARBOLDICT",i
               if self.__upObjDict.has_key(i)==True:
                   self.upObj=self.__upObjDict[i]
                   print self.__upObjDict[i].name
                   #            self.operObjList.append(opObj10)
       
                   if self.nFFTPointOpSpecCEB.isChecked():                     
                        value=self.valuenFFTPointOpSpec.text()
                        self.upObj.addParameter(name='nFFTPoints',value=value,format='int')
                        print "nFFTpoints"
                   
                   
                   if self.SelectHeiopSpecCEB.isChecked():
                      if  self.valueSelecChOpHei.currentIndex()== 0:
                          opObj10=self.upObj.addOperation(name='selectHeights')
                          value=self.selecHeiopSpec.text()
                          valueList=value.split(',')
                          opObj10.addParameter(name='minHei', value=valueList[0], format='float')
                          opObj10.addParameter(name='maxHei', value=valueList[1], format='float') 
                      else:
                          opObj10=self.upObj.addOperation(name='selectHeightsByIndex')
                          value=self.selecHeiopSpec.text()
                          valueList=value.split(',')
                          opObj10.addParameter(name='minIndex', value=valueList[0], format='float')
                          opObj10.addParameter(name='maxIndex', value=valueList[1], format='float') 
                       
                   if self.selecChannelopSpecCEB.isChecked():
                       if  self.valueSelecChOpSpec.currentIndex()== 0:
                           opObj10=self.upObj.addOperation(name="selectChannels")
                           self.operObjList.append(opObj10)
                           value=self.numberChannelopSpec.text()                    
                           opObj10.addParameter(name='channelList', value=value, format='intlist')
                       else:
                           opObj10=self.upObj.addOperation(name="selectChannelsByIndex")
                           self.operObjList.append(opObj10)
                           value=self.numberChannelopSpec.text()                    
                           opObj10.addParameter(name='channelIndexList', value=value, format='intlist')
                           print "channel"                                       
                       
                   if self.IncohIntOpSpecCEB.isChecked():
                      opObj10=self.upObj.addOperation(name='IncohInt', optype='other')
                      self.operObjList.append(opObj10)
                      value=self.valueIncohIntOpSpec.text()                    
                      opObj10.addParameter(name='n', value=value, format='float') 
                      
                   if self.removedcOpSpecCEB.isChecked():
                       opObj10=self.upObj.addOperation(name='removeDC')
                       value=self.valueremoveDCOpSpec.text()     
                       opObj10.addParameter(name='mode', value=value,format='int')
                 
                   
    #---------------------VENTANA DE CONFIGURACION GRAPH SPECTRA------------------#       
    @pyqtSignature("int")
    def on_dataTypeSelectorCmb_activated(self,index):
        self.setClearAllElementGraph()
        self.setEnableAllElementGraph()
        if index==0:
            self.timeRangeGraphSpec.setEnabled(False)
        if index==1:
            self.timeRangeGraphSpec.setEnabled(False)
        if index==2:
            self.timeRangeGraphSpec.setEnabled(False)
        if index==3:
            self.timeRangeGraphSpec.setEnabled(False)
     
        
    @pyqtSignature("int")
    def on_saveGraphSpec_stateChanged(self, p0):
        """
        Habilita la opcion de a�adir el par�metro nFFTPoints a la Unidad de Procesamiento .
        """
        if  p0==2:
            self.dataPathTxtSpec.setEnabled(True)
            self.dataPrefixGraphSpec.setEnabled(True)
            print " nFFTPoint"
        if  p0==0:
            print " deshabilitado" 
            self.dataPathTxtSpec.setEnabled(False)
            self.dataPrefixGraphSpec.setEnabled(False)
        
        
    @pyqtSignature("")
    def on_dataGraphSpecOkBtn_clicked(self):
        
        print "AÑADEOPERACIONSPECTRA"
      
        for i in self.__arbolDict:       
            if self.__arbolDict[i]==self.indexclick:
               print "INDEXCLICK=ARBOLDICT",i
               if self.__upObjDict.has_key(i)==True:
                   self.upObj=self.__upObjDict[i]
                   print self.__upObjDict[i].name
        
                   if self.dataTypeSelectorCmb.currentIndex()==0:  
                      opObj10=self.upObj.addOperation(name='SpectraPlot',optype='other')
                      opObj10.addParameter(name='idfigure', value='1', format='int')
                      self.properSpecGraph(opObj10)
                                 
                   if self.dataTypeSelectorCmb.currentIndex()==1:    
                      opObj10=self.upObj.addOperation(name='CrossSpectraPlot',optype='other')
                      self.properSpecGraph(opObj10)        
                      opObj10.addParameter(name='power_cmap', value='jet', format='str')
                      opObj10.addParameter(name='coherence_cmap', value='jet', format='str')
                      opObj10.addParameter(name='phase_cmap', value='RdBu_r', format='str')              
                      
                   if self.dataTypeSelectorCmb.currentIndex()==2:
                      opObj10=self.upObj.addOperation(name='RTIPlot',optype='other')
                      self.properSpecGraph(opObj10)         
   
                   if self.dataTypeSelectorCmb.currentIndex()==3:
                      opObj10=self.upObj.addOperation(name='CoherenceMap',optype='other')
                      self.properSpecGraph(opObj10) 
                      opObj10.addParameter(name='coherence_cmap', value='jet', format='str')
                      opObj10.addParameter(name='phase_cmap', value='RdBu_r', format='str')     
                   
                   if self.dataTypeSelectorCmb.currentIndex()==4:
                      opObj10=self.upObj.addOperation(name='RTIfromNoise',optype='other')
                      self.properSpecGraph(opObj10) 
                   self.setDisableAllElementSpecGraph()
                   print "Funciona o no"
               
    @pyqtSignature("")    
    def on_dataGraphSpecCancelBtn_clicked(self): 
            print "alexvaldez" 

    def properSpecGraph(self,opObj10):
          print opObj10.id                         
          self.operObjList.append(opObj10)
          wintitle=self.winTitleGraphSpec.text()      
          opObj10.addParameter(name='wintitle', value=wintitle, format='str')
          idfigure=self.idfigureGraphSpec.text()
          opObj10.addParameter(name='idfigure', value=idfigure, format='int')

          
          channelList=self.channelListgraphSpec.text()
          if self.channelListgraphSpec.isModified():
              opObj10.addParameter(name='channelList', value=channelList, format='intlist') 
          
          xvalue= self.xminGraphSpec.text() 
          if self.xminGraphSpec.isModified():
              xvalueList=xvalue.split(',')
              opObj10.addParameter(name='xmin', value=xvalueList[0], format='int')
              opObj10.addParameter(name='xmax', value=xvalueList[1], format='int')
          else:
              print "cambio"
          yvalue= self.yminGraphSpec.text()
          if self.yminGraphSpec.isModified():
              yvalueList=yvalue.split(",")
              opObj10.addParameter(name='ymin', value=yvalueList[0], format='int')
              opObj10.addParameter(name='ymax', value=yvalueList[1], format='int')
          else:
              print "cambio"
          zvalue= self.zminGraphSpec.text()       
          if self.zminGraphSpec.isModified():
             zvalueList=zvalue.split(",")            
          if opObj10.name=="RTIfromNoise":
              print "No_z"
          else:
              if self.zminGraphSpec.isModified():
                  zvalueList=zvalue.split(",")
                  opObj10.addParameter(name='zmin', value=zvalueList[0], format='int')
                  opObj10.addParameter(name='zmax', value=zvalueList[1], format='int')
                  opObj10.addParameter(name='showprofile', value='1', format='int') 

              else:
                  print "cambio"
          
          if self.savedataCEBGraphicsVol.isChecked():
              opObj10.addParameter(name='save', value='1', format='int')
              opObj10.addParameter(name='figpath', value= self.dataPathTxtSpec.text())
              opObj10.addParameter(name='figfile', value= self.dataPrefixGraphSpec.text())  
        

    def setClearAllElementGraph(self):
            self.winTitleGraphSpec.clear()
            self.channelListgraphSpec.clear()
            self.xminGraphSpec.clear()
            self.yminGraphSpec.clear()
            self.zminGraphSpec.clear()
            self.timeRangeGraphSpec.clear()    
            self.dataPathTxtSpec.clear()
            self.dataPrefixGraphSpec.clear() 
            
    def setDisableAllElementSpecGraph(self):
            self.winTitleGraphSpec.setEnabled(False)
            self.channelListgraphSpec.setEnabled(False)
            self.xminGraphSpec.setEnabled(False)
            self.yminGraphSpec.setEnabled(False)
            self.zminGraphSpec.setEnabled(False)
            self.timeRangeGraphSpec.setEnabled(False)   
            self.dataPathTxtSpec.setEnabled(False)
            self.dataPrefixGraphSpec.setEnabled(False) 
#             
    def setEnableAllElementGraph(self):
            self.winTitleGraphSpec.setEnabled(True)
            self.channelListgraphSpec.setEnabled(True)
            self.xminGraphSpec.setEnabled(True)
            self.yminGraphSpec.setEnabled(True)
            self.zminGraphSpec.setEnabled(True)
            self.timeRangeGraphSpec.setEnabled(True)   
#      
        
        
        
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
            print "name",name
            if name=='Project':
                id= i.id
                name=i.name
                print "tipodeproyecto",self.dataTypeProject
                if self.dataTypeProject=='Voltage':
                    self.comboTypeBox.clear()
                    self.comboTypeBox.addItem("Voltage")
                    self.comboTypeBox.addItem("Spectra")
                    self.comboTypeBox.addItem("Correlation") 
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
      
  