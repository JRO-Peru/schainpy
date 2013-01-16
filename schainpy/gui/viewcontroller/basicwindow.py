# -*- coding: utf-8 -*-
"""
Module implementing MainWindow.
#+++++++++++++INTERFAZ DE USUARIO V1.1++++++++++++++#
"""
import os
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
from controller            import Project,ReadUnitConf,ProcUnitConf,OperationConf,ParameterConf


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
        
        self.indexclick=None
               
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

  #-----------------------------------NEW PROPERTIES------------------------------------------------#
        QtGui.QToolTip.setFont(QtGui.QFont('SansSerif', 10))
        self.addprojectBtn.setToolTip('Add_New_Project')    
        self.addUnitProces.setToolTip('Add_New_Processing_Unit')  

  #-----------------------------------NEW PROPERTIES------------------------------------------------#
        self.model = QtGui.QStandardItemModel()
        self.treeView.setModel(self.model)
        self.treeView.clicked.connect(self.clickFunctiontree)
        self.treeView.expandAll()
        #self.treeView.clicked.connect(self.treefunction1)





 #-----------------------------------BARRA DE MENU-------------------------------------------------#
 
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
    
    @pyqtSignature("") 
    def on_menuHELPPrfObj_clicked(self):
        """
        METODO EJECUTADO CUANDO OCURRE EL EVENTO HElp
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
        
        self.startDateCmbBox.clear()
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
                
#               self.model.clear()
#               self.parentItem = self.model.invisibleRootItem()
#               self.__arbolDict[i]= QtGui.QStandardItem(QtCore.QString(name+" %0").arg(self.idp))
#               self.parentItem.appendRow(self.__arbolDict[self.idp               
           
#               print self.projectObj
#               print i
#               print "get",self.__arbolDict.items()
#               print "keys",self.__arbolDict.keys()

        self.idp += 1
        self.projectObj = Project()
        print "self.projectObj",self.projectObj
        self.__projObjDict[self.idp] = self.projectObj


        self.description="Think"          
        id=self.idp
        name=str(self.nameProjectTxt.text())
        print "name",name
        desc=str(self.description)
         
        self.projectObj.setup(id = id, name=name, description=desc)
        print "self.projectObj.id",self.projectObj.id
#               print self.projectObj.name
#               print self.projectObj.description
 
        datatype=str(self.dataTypeCmbBox.currentText())
        path=str(self.dataPathTxt.text())
        online=int(self.online)
        starDate=str(self.starDateCmbBox.currentText())
        endDate=str(self.endDateCmbBox.currentText())

 
        self.readUnitConfObj = self.projectObj.addReadUnit(datatype=datatype,
                                                 path=path,
                                                 startDate=starDate,
                                                 endDate=endDate,
                                                 startTime='06:10:00',
                                                 endTime='23:59:59',
                                                 online=online)
         
        self.readUnitConfObjList.append(self.readUnitConfObj)
        print "self.readUnitConfObj.getId",self.readUnitConfObj.getId(),datatype            
       
        reloj1=self.startTimeEdit.time()
        reloj2=self.timeEdit_2.time()
        print reloj1.hour()
        print reloj1.minute()
        print reloj1.second()

        self.model_2=treeModel()        
        self.model_2.setParams(name       =self.projectObj.name,
                               directorio =path,
                               workspace  ="C:\\WorkspaceGUI",
                               remode     =str(self.readModeCmBox.currentText()), 
                               dataformat =datatype, 
                               date       =str(starDate)+"-"+str(endDate),
                               initTime   = str(reloj1.hour()) +":"+str(reloj1.minute())+":"+ str(reloj1.second()),
                               endTime    = str(reloj2.hour()) +":"+str(reloj2.minute())+":"+ str(reloj2.second()),
                               timezone   ="Local" ,
                               Summary    ="test de prueba")                                                 
        
        self.model_2.arbol()
        self.treeView_2.setModel(self.model_2)
        self.treeView_2.expandAll()                     

        self.parentItem = self.model.invisibleRootItem()
        #self.__arbolDict[self.idp] =   QtGui.QStandardItem(QtCore.QString(name).arg(self.idp))
        self.__arbolDict[self.idp] =   QtGui.QStandardItem(QtCore.QString(name).arg(self.idp))

        print self.__arbolDict[self.idp]
        self.parentItem.appendRow(self.__arbolDict[self.idp])
        self.parentItem=self.__arbolDict[self.idp]
        self.tabProject.setEnabled(False)

        
        
        
   #-----------------PUSHBUTTON_ADD_PROCESSING UNIT PROJECT------------------#    
    @pyqtSignature("")
    def on_addUnitProces_clicked(self):
        """
        CREAR PROCESSING UNI ,ANADE UNA UNIDAD DE PROCESAMIENTO, LLAMA AL MÉTODO addUP QUE CONTIENE LAS OPERACION DE CREACION DE UNIDADES DE PROCESAMIENTO
        Llama al metodo addUP.
        """
#        print "En este nivel se adiciona una rama de procesamiento, y se le concatena con el id"
        self.addUP()
        
        
              #----------------------------BASICO-----------------------------------#  
                
    def getNumberofProject(self):
#        for i in self.proObjList:
#            print i
        return self.proObjList
#        for  i in self.proObjList:
#            print i
        
    def setParam(self):
        
        self.tabWidgetProject.setEnabled(False)
        self.tabVoltage.setEnabled(False)
        self.tabSpectra.setEnabled(False)
        self.tabCorrelation.setEnabled(False)
        self.dataPathTxt.setText('C:\data')
        self.nameProjectTxt.setText("Test")
        self.numberChannelopVol.setEnabled(False)
        self.lineHeighProfileTxtopVol.setEnabled(False)
        self.numberIntegration.setEnabled(False)
        self.valuenFFTPointOpSpec.setEnabled(False)
        self.lineProfileSelecopVolCEB.setEnabled(False)
        
    def clickFunctiontree(self,index):
        self.indexclick= index.model().itemFromIndex(index)
        print "OPCION CLICK"
        print "ArbolDict",self.indexclick
        print "name:",self.indexclick.text()
        #print self.tabWidgetProject.currentIndex()
        
        #return self.indexclick
        for i in self.__arbolDict: 
            if self.__arbolDict[i]==self.indexclick:
                print "INDEXCLICK=ARBOLDICT",i
                if self.__projObjDict.has_key(i)==True:       
                    self.tabWidgetProject.setCurrentWidget(self.tabProject)
               
        if self.indexclick.text()=='Voltage':
           self.tabVoltage.setEnabled(True)
           self.tabWidgetProject.setCurrentWidget(self.tabVoltage)

        if self.indexclick.text()=='Spectra':
           self.tabSpectra.setEnabled(True) 
           self.tabWidgetProject.setCurrentWidget(self.tabSpectra)
            
        if self.indexclick.text()=='Correlation':
           self.tabCorrelation.setEnabled(True) 
           self.tabWidgetProject.setCurrentWidget(self.tabCorrelation) 
           

#        self.indexclick= index.model().itemFromIndex(index).text()
#        return self.indexclick
#        print self.indexclick()
#        print index.model().itemFromIndex(index)
#        print  self.indexclick
#        NumofPro=self.indexclick[8:10]
#        self.valuep=NumofPro
#        #print self.valuep
#        NameofPro=self.indexclick[0:7]
#        self.namepTree=NameofPro
#        print self.namepTree

    def addProject(self):
        self.tabWidgetProject.setEnabled(True)
        self.tabWidgetProject.setCurrentWidget(self.tabProject)
        self.tabProject.setEnabled(True)
        #self.tabVoltage.setEnabled(False)
        print "HABILITA WIDGET"
        #+++++++++++++++++++Creacion del Objeto Controller-XML+++++++++++++#
        
#        self.idp += 1
#        self.projectObj = Project()
#        print self.projectObj
#        self.__projObjDict[self.idp] = self.projectObj
#        
#        #++++++++++++++++++Creación del Arbol++++++++++++++++++++#
#        
#        name='Test'
#        
#        self.parentItem = self.model.invisibleRootItem()
#        self.__arbolDict[self.idp] =   QtGui.QStandardItem(QtCore.QString(name).arg(self.idp))
#        
#        print "Nombre del projecto es :",self.__arbolDict[self.idp].setAccessibleText('HOLA')
#        print self.__arbolDict[self.idp]
#        self.parentItem.appendRow(self.__arbolDict[self.idp])
#        self.parentItem=self.__arbolDict[self.idp]
        
       
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
        
        self.timeEdit_2.setTime(self.time)
        
       
    def addUP(self):
        
        self.configUP=UnitProcess(self)
        
        for i in self.__arbolDict:       
            if self.__arbolDict[i]==self.indexclick:
               print "INDEXCLICK=ARBOLDICT",i
               if self.__projObjDict.has_key(i)==True:
                   self.projectObj=self.__projObjDict[int(i)]
                   print "self.projectObj.id",self.projectObj.id
                   self.configUP.dataTypeProject=str(self.dataTypeCmbBox.currentText())
                   self.configUP.getfromWindowList.append(self.projectObj) 
                                      
                   for i in self.projectObj.procUnitConfObjDict:
                      if self.projectObj.procUnitConfObjDict[i].getElementName()=='ProcUnit':
                         self.upObj=self.projectObj.procUnitConfObjDict[i]
                         self.configUP.getfromWindowList.append(self.upObj)          
               else:
                   self.upObj=self.__upObjDict[i]
                   print "self.upObj.id",self.upObj.id
                   self.configUP.getfromWindowList.append(self.upObj)
                   
                   
            
        self.configUP.loadTotalList()
        self.configUP.show()      
        #self.configUP.unitPsavebut.clicked.connect(self.reciveUPparameters)
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
        #self.selecChannelopVolCEB.setEnabled(False)
        self.lineHeighProfileTxtopVol.clear()
        self.lineProfileSelecopVolCEB.clear()
        self.numberChannelopVol.clear()
        self.numberIntegration.clear()
            
    
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
                self.projectObj=self.__projObjDict[int(i)] 
                print "Encontre project"
        filename="C:\WorkspaceGUI\config"+str(self.projectObj.id)+".xml"
        print "Escribo Project"
        self.projectObj.writeXml(filename)


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
        # TODO: not implemented yet
        #raise NotImplementedError
        self.create=False
        self.close()  

    def loadTotalList(self):
        self.comboInputBox.clear()
        for i in self.getfromWindowList:
            
            name=i.getElementName()
            if name=='Project':
                id= i.id
                name=i.name
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

               
           #self.comboInputBox.addItem(str(name))    
            self.comboInputBox.addItem(str(name)+str(id))    

    def closeEvent(self, event):
        self.closed.emit()
        event.accept()
    
    
    
    
              
    #-----------------VENTANA CONFIGURACION DE VOLTAGE---------------------------#     
#    
#    @pyqtSignature("int")
#    def on_selecChannelopVolCEB_stateChanged(self, p0):
#        """
#        Check Box habilita operaciones de Selecci�n de Canales
#        """
#        if  p0==2:
#            self.numberChannelopVol.setEnabled(True)
#            upProcessSelect=self.upObjVolList[int(self.addOpUpselec.currentIndex())]
#            opObj10=upProcessSelect.addOperation(name='selectChannels')
#            print opObj10.id
#            self.operObjList.append(opObj10)
#            print " Ingresa seleccion de Canales"
#        if  p0==0:
#            print " deshabilitado" 
#            
#    @pyqtSignature("int")
#    def on_selecHeighopVolCEB_stateChanged(self, p0):
#        """
#        Check Box habilita operaciones de Selecci�n de Alturas 
#        """
#        if  p0==2:
#            self.lineHeighProfileTxtopVol.setEnabled(True)
#            upProcessSelect=self.upObjVolList[int(self.addOpUpselec.currentIndex())]
#            opObj10=upProcessSelect.addOperation(name='selectHeights')
#            print opObj10.id
#            self.operObjList.append(opObj10)
#            print " Select Type of Profile"
#        if  p0==0:
#            print " deshabilitado" 
#            
#
#    @pyqtSignature("int")
#    def on_profileSelecopVolCEB_stateChanged(self, p0):
#        """
#        Check Box habilita ingreso  del rango de Perfiles
#        """
#        if  p0==2:
#            self.lineProfileSelecopVolCEB.setEnabled(True)
#            upProcessSelect=self.upObjVolList[int(self.addOpUpselec.currentIndex())]
#            opObj10=upProcessSelect.addOperation(name='ProfileSelector', optype='other')
#            print opObj10.id
#            self.operObjList.append(opObj10)
#            print " Select Type of Profile"
#        if  p0==0:
#            print " deshabilitado" 
#            
#            
#    @pyqtSignature("int")
#    def on_coherentIntegrationCEB_stateChanged(self, p0):
#        """
#        Check Box habilita ingresode del numero de Integraciones a realizar
#        """
#        if  p0==2:
#            self.numberIntegration.setEnabled(True)
#            upProcessSelect=self.upObjVolList[int(self.addOpUpselec.currentIndex())]
#            opObj10=upProcessSelect.addOperation(name='CohInt', optype='other')
#            print opObj10.id
#            self.operObjList.append(opObj10)
#            print "Choose number of Cohint"
#        if  p0==0:
#            print " deshabilitado"   
#            self.numberChannelopVol.setEnabled(False)  
#            
#    #-----------------------PUSHBUTTON_ACCEPT_OPERATION----------------------------#       
#    
#    @pyqtSignature("")
#    def on_dataopVolOkBtn_clicked(self):
#        """
#        BUSCA EN LA LISTA DE OPERACIONES DEL TIPO VOLTAJE Y LES A�ADE EL PARAMETRO ADECUADO ESPERANDO LA ACEPTACION DEL USUARIO
#        PARA AGREGARLO AL ARCHIVO DE CONFIGURACION XML
#        """   
#        if self.selecChannelopVolCEB.isChecked():
#            for i in self.operObjList:
#                if i.name=='selectChannels':
#                    value=self.numberChannelopVol.text()
#                    i.addParameter(name='channelList', value=value, format='intlist')
#
#            
#            print "channel"
#            
#        if self.selecHeighopVolCEB.isChecked():
#            for i in self.operObjList:
#                if i.name=='selectHeights' :
#                    value=self.lineHeighProfileTxtopVol.text()
#                    valueList=value.split(',')
#                    i.addParameter(name='minHei', value=valueList[0], format='float')
#                    i.addParameter(name='maxHei', value=valueList[1], format='float')
#          
#            print "height"
#        
#        
#        if self.selecHeighopVolCEB.isChecked():
#            for i in self.operObjList:
#                if i.name=='ProfileSelector' :
#                    value=self.lineProfileSelecopVolCEB.text()
#                    i.addParameter(name='ProfileSelector', value=value, format='intlist')
#              
#                    
#                    
#        if self.coherentIntegrationCEB.isChecked():
#            for i in self.operObjList:
#                if i.name=='CohInt':
#                    value=self.numberIntegration.text()
#                    i.addParameter(name='n', value=value, format='int')  
#        
#        
#    #-------------------------VENTANA DE CONFIGURACION SPECTRA------------------------#     
#        
#    @pyqtSignature("int")
#    def on_nFFTPointOpSpecCEB_stateChanged(self, p0):
#        """
#        Habilita la opcion de a�adir el par�metro nFFTPoints a la Unidad de Procesamiento .
#        """
#        if  p0==2:
#            self.valuenFFTPointOpSpec.setEnabled(True)
#            print " nFFTPoint"
#        if  p0==0:
#            print " deshabilitado" 
#            
#    #------------------PUSH_BUTTON_SPECTRA_OK------------------------------------#   
#                 
#    @pyqtSignature("")
#    def on_dataopSpecOkBtn_clicked(self):
#        """
#        A�ade al archivo de configuraci�n el par�metros nFFTPoints a la UP.
#        """
#        print "A�adimos operaciones Spectra,nchannels,value,format"
#        if self.nFFTPointOpSpecCEB.isChecked():
#            upProcessSelect=self.upobjSpecList[int(self.addOpSpecUpselec.currentIndex())]
#            value=self.valuenFFTPointOpSpec.text()
#            upProcessSelect.addParameter(name='nFFTPoints',value=value,format='int')
#    #---------------------VENTANA DE CONFIGURACION GRAPH SPECTRA------------------#     
#
#    @pyqtSignature("int")
#    def on_SpectraPlotGraphCEB_stateChanged(self, p0):
#        """
#        Habilita la opcion de Ploteo Spectra Plot
#        """
#        if  p0==2:
#            upProcessSelect=self.upobjSpecList[int(self.addOpSpecUpselec.currentIndex())]
#            opObj10=upProcessSelect.addOperation(name='SpectraPlot',optype='other')
#            print opObj10.id
#            self.operObjList.append(opObj10)
#    
#        if  p0==0:
#            print " deshabilitado" 
#    
#    @pyqtSignature("int")
#    def on_CrossSpectraPlotGraphceb_stateChanged(self, p0):
#        """
#        Habilita la opci�n de Ploteo CrossSpectra
#        """
#        if  p0==2:
#            upProcessSelect=self.upobjSpecList[int(self.addOpSpecUpselec.currentIndex())]
#            opObj10=upProcessSelect.addOperation(name='CrossSpectraPlot',optype='other')
#            print opObj10.id
#            self.operObjList.append(opObj10) 
#        if  p0==0:
#            print " deshabilitado"    
#        
#    @pyqtSignature("int")
#    def on_RTIPlotGraphCEB_stateChanged(self, p0):
#        """
#        Habilita la opci�n de Plote RTIPlot
#        """
#        if  p0==2:
#            upProcessSelect=self.upobjSpecList[int(self.addOpSpecUpselec.currentIndex())]
#            opObj10=upProcessSelect.addOperation(name='RTIPlot',optype='other')
#            print opObj10.id
#            self.operObjList.append(opObj10) 
#        if  p0==0:
#            print " deshabilitado"     
#    
#    #------------------PUSH_BUTTON_SPECTRA_GRAPH_OK-----------------------------#
#    @pyqtSignature("")
#    def on_dataGraphSpecOkBtn_clicked(self):
#        """
#        HABILITAR DE ACUERDO A LOS CHECKBOX QUE TIPO DE PLOTEOS SE VAN A REALIZAR MUESTRA Y GRABA LAS IMAGENES.
#        """
#        print "Graficar Spec op"
#        if self.SpectraPlotGraphCEB.isChecked():
#            for i in self.operObjList:
#                if i.name=='SpectraPlot':
#                    i.addParameter(name='idfigure', value='1', format='int')
#                    i.addParameter(name='wintitle', value='SpectraPlot0', format='str')
#                    i.addParameter(name='zmin', value='40', format='int')
#                    i.addParameter(name='zmax', value='90', format='int')
#                    i.addParameter(name='showprofile', value='1', format='int') 
#            
#        if self.CrossSpectraPlotGraphceb.isChecked():
#            for i in self.operObjList:
#                if i.name=='CrossSpectraPlot' :
#                    i.addParameter(name='idfigure', value='2', format='int')
#                    i.addParameter(name='wintitle', value='CrossSpectraPlot', format='str')
#                    i.addParameter(name='zmin', value='40', format='int')
#                    i.addParameter(name='zmax', value='90', format='int') 
#            
#        if self.RTIPlotGraphCEB.isChecked():
#            for i in self.operObjList:
#                if i.name=='RTIPlot':
#                    i.addParameter(name='n', value='2', format='int')
#                    i.addParameter(name='overlapping', value='1', format='int')
#                            
#        

    