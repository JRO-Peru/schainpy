# -*- coding: utf-8 -*-
"""
Module implementing MainWindow.
#+++++++++++++++++++++INTERFAZ DE USUARIO V1.1++++++++++++++++++++++++#
"""
from PyQt4.QtGui import QMainWindow
from PyQt4.QtCore import pyqtSignature
from PyQt4.QtCore import pyqtSignal
from PyQt4 import QtCore
from PyQt4 import QtGui
from timeconversions import  Doy2Date
from modelProperties import treeModel
from viewer.ui_unitprocess import Ui_UnitProcess
from viewer.ui_window import Ui_window
from viewer.ui_mainwindow import Ui_MainWindow


from controller import Project,ReadUnitConf,ProcUnitConf,OperationConf,ParameterConf
import os


class MainWindow(QMainWindow, Ui_MainWindow):
    __projObjDict = {}
    __arbolDict = {}
    
    """
    Class documentation goes here.
    #*##################VENTANA CUERPO  DEL PROGRAMA####################
    """
    def __init__(self, parent = None):
        """
        Constructor
        """   
        print "Inicio de Programa Interfaz Gráfica"
        QMainWindow.__init__(self, parent)
        self.setupUi(self)
               
        self.online=0
        self.datatype=0
        self.variableList=[]
        
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
        
        
        self.controllerObj=None
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
        METODO CARGA UN ARCHIVO DE CONFIGURACION ANTERIOR
        """
        print "Leer un archivo xml y extraer sus atributos Not implemented yet"
        
    @pyqtSignature("")
    def on_menuFileCrearObj_triggered(self):
        """
        CREAR PROJECT,ANADE UN NUEVO PROYECTO, LLAMA AL MÉTODO QUE CONTIENE LAS OPERACION DE CREACION DE PROYECTOS
        Llama al metodo addProject..
        """
        self.addProject()
             
    @pyqtSignature("")
    def on_menuFileGuardarObj_clicked(self):
        """
        METODO  EJECUTADO CUANDO OCURRE EL EVENTO GUARDAR PROJECTO
        Llama al metodo saveProject.
        """ 
        self.saveProject()
        
    @pyqtSignature("")
    def on_menuFileCerrarObj_clicked(self):
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
           self.datatype='Voltage'
        elif index==1:
            self.datatype='Spectra'
        else :
              self.datatype=''
              self.dataFormatTxt.setReadOnly(False)
        self.dataFormatTxt.setText(self.datatype)
        
    @pyqtSignature("")
    def on_dataPathBrowse_clicked(self):
        """
        OBTENCION DE LA RUTA DE DATOS
        """
        self.dataPath = str(QtGui.QFileDialog.getExistingDirectory(self, 'Open Directory', './',  QtGui.QFileDialog.ShowDirsOnly))
        self.dataPathTxt.setText(self.dataPath)
        self.statusDpath=self.existDir(self.dataPath)
        self.loadDays()   
        
    @pyqtSignature("int")
    def on_starDateCmbBox_activated(self, index):
        """
        SELECCION DEL RANGO DE FECHAS -START DATE
        """
        var_StopDay_index=self.endDateCmbBox.count() - self.endDateCmbBox.currentIndex()
        self.endDateCmbBox.clear()
        for i in self.variableList[index:]:
            self.endDateCmbBox.addItem(i)
        self.endDateCmbBox.setCurrentIndex(self.endDateCmbBox.count() - var_StopDay_index)
        self.getsubList()

    @pyqtSignature("int")
    def on_endDateCmbBox_activated(self, index):
        """
        SELECCION DEL RANGO DE FECHAS-END DATE
        """
        var_StartDay_index=self.starDateCmbBox.currentIndex()
        var_end_index = self.endDateCmbBox.count() - index
        self.starDateCmbBox.clear()
        for i in self.variableList[:len(self.variableList) - var_end_index + 1]:
            self.starDateCmbBox.addItem(i)
        self.starDateCmbBox.setCurrentIndex(var_StartDay_index)
        self.getsubList() #Se carga var_sublist[] con el rango de las fechas seleccionadas
    
    @pyqtSignature("int")
    def on_readModeCmBox_activated(self, p0):
        """
        SELECCION DEL MODO DE LECTURA ON=1, OFF=0
        """
        if p0==0:
           self.online=0
        elif p0==1:
            self.online=1  
        
      #---------------PUSHBUTTON_dataOkBtn_CONFIGURATION PROJECT--------------------------#    
    
    @pyqtSignature("")
    def on_dataOkBtn_clicked(self):
        """
        Añade al Obj XML de Projecto, name,datatype,date,time,readmode,wait,etc, crea el readUnitProcess del archivo xml.
        Prepara la configuración del diágrama del Arbol del treeView numero 2
        """     
        print "En este nivel se pasa el tipo de dato con el que se trabaja,path,startDate,endDate,startTime,endTime,online"

        projectObj=self.proObjList[int(self.proConfCmbBox.currentIndex())]
        datatype=str(self.dataTypeCmbBox.currentText())
        path=str(self.dataPathTxt.text())
        online=int(self.online)
        starDate=str(self.starDateCmbBox.currentText())
        endDate=str(self.endDateCmbBox.currentText())
   
        
        self.readUnitConfObj = projectObj.addReadUnit(datatype=datatype,
                                                path=path,
                                                startDate=starDate,
                                                endDate=endDate,
                                                startTime='06:10:00',
                                                endTime='23:59:59',
                                                online=online)
        
        self.readUnitConfObjList.append(self.readUnitConfObj)
        
        print "self.readUnitConfObj.getId",self.readUnitConfObj.getId(),datatype,path,starDate,endDate,online

        
        self.model_2=treeModel()

        self.model_2.setParams(name=projectObj.name+str(projectObj.id),
                               directorio=path,
                                workspace="C:\\WorkspaceGUI",
                                  remode=str(self.readModeCmBox.currentText()), 
                                   dataformat=datatype, 
                                    date=str(starDate)+"-"+str(endDate),
                                     initTime='06:10:00',
                                       endTime='23:59:59',
                                        timezone="Local" ,
                                         Summary="test de prueba")
        self.model_2.arbol()
        self.treeView_2.setModel(self.model_2)
        self.treeView_2.expandAll()       
        
    
   #-----------------PUSHBUTTON_ADD_PROCESSING UNIT PROJECT------------------#    
    @pyqtSignature("")
    def on_addUnitProces_clicked(self):
        """
        CREAR PROCESSING UNI ,ANADE UNA UNIDAD DE PROCESAMIENTO, LLAMA AL MÉTODO addUP QUE CONTIENE LAS OPERACION DE CREACION DE UNIDADES DE PROCESAMIENTO
        Llama al metodo addUP.
        """
#        print "En este nivel se adiciona una rama de procesamiento, y se le concatena con el id"
#        self.procUnitConfObj0 = self.controllerObj.addProcUnit(datatype='Voltage', inputId=self.readUnitConfObj.getId())      
        self.addUP()
        
        
    #-----------------VENTANA CONFIGURACION DE VOLTAGE---------------------------#     
    
    @pyqtSignature("int")
    def on_selecChannelopVolCEB_stateChanged(self, p0):
        """
        Check Box habilita operaciones de Selección de Canales
        """
        if  p0==2:
            self.numberChannelopVol.setEnabled(True)
            upProcessSelect=self.upObjVolList[int(self.addOpUpselec.currentIndex())]
            opObj10=upProcessSelect.addOperation(name='selectChannels')
            print opObj10.id
            self.operObjList.append(opObj10)
            print " Ingresa seleccion de Canales"
        if  p0==0:
            print " deshabilitado" 
            
    @pyqtSignature("int")
    def on_selecHeighopVolCEB_stateChanged(self, p0):
        """
        Check Box habilita operaciones de Selección de Alturas 
        """
        if  p0==2:
            self.lineHeighProfileTxtopVol.setEnabled(True)
            upProcessSelect=self.upObjVolList[int(self.addOpUpselec.currentIndex())]
            opObj10=upProcessSelect.addOperation(name='selectHeights')
            print opObj10.id
            self.operObjList.append(opObj10)
            print " Select Type of Profile"
        if  p0==0:
            print " deshabilitado" 
            

    @pyqtSignature("int")
    def on_profileSelecopVolCEB_stateChanged(self, p0):
        """
        Check Box habilita ingreso  del rango de Perfiles
        """
        if  p0==2:
            self.lineProfileSelecopVolCEB.setEnabled(True)
            upProcessSelect=self.upObjVolList[int(self.addOpUpselec.currentIndex())]
            opObj10=upProcessSelect.addOperation(name='ProfileSelector', optype='other')
            print opObj10.id
            self.operObjList.append(opObj10)
            print " Select Type of Profile"
        if  p0==0:
            print " deshabilitado" 
            
            
    @pyqtSignature("int")
    def on_coherentIntegrationCEB_stateChanged(self, p0):
        """
        Check Box habilita ingresode del numero de Integraciones a realizar
        """
        if  p0==2:
            self.numberIntegration.setEnabled(True)
            upProcessSelect=self.upObjVolList[int(self.addOpUpselec.currentIndex())]
            opObj10=upProcessSelect.addOperation(name='CohInt', optype='other')
            print opObj10.id
            self.operObjList.append(opObj10)
            print "Choose number of Cohint"
        if  p0==0:
            print " deshabilitado"   
            self.numberChannelopVol.setEnabled(False)  
            
    #-----------------------PUSHBUTTON_ACCEPT_OPERATION----------------------------#       
    
    @pyqtSignature("")
    def on_dataopVolOkBtn_clicked(self):
        """
        BUSCA EN LA LISTA DE OPERACIONES DEL TIPO VOLTAJE Y LES AÑADE EL PARAMETRO ADECUADO ESPERANDO LA ACEPTACION DEL USUARIO
        PARA AGREGARLO AL ARCHIVO DE CONFIGURACION XML
        """   
        if self.selecChannelopVolCEB.isChecked():
            for i in self.operObjList:
                if i.name=='selectChannels':
                    value=self.numberChannelopVol.text()
                    i.addParameter(name='channelList', value=value, format='intlist')

            
            print "channel"
            
        if self.selecHeighopVolCEB.isChecked():
            for i in self.operObjList:
                if i.name=='selectHeights' :
                    value=self.lineHeighProfileTxtopVol.text()
                    valueList=value.split(',')
                    i.addParameter(name='minHei', value=valueList[0], format='float')
                    i.addParameter(name='maxHei', value=valueList[1], format='float')
          
            print "height"
        
        
        if self.selecHeighopVolCEB.isChecked():
            for i in self.operObjList:
                if i.name=='ProfileSelector' :
                    value=self.lineProfileSelecopVolCEB.text()
                    i.addParameter(name='ProfileSelector', value=value, format='intlist')
              
                    
                    
        if self.coherentIntegrationCEB.isChecked():
            for i in self.operObjList:
                if i.name=='CohInt':
                    value=self.numberIntegration.text()
                    i.addParameter(name='n', value=value, format='int')  
        
        
    #-------------------------VENTANA DE CONFIGURACION SPECTRA------------------------#     
        
    @pyqtSignature("int")
    def on_nFFTPointOpSpecCEB_stateChanged(self, p0):
        """
        Habilita la opcion de añadir el parámetro nFFTPoints a la Unidad de Procesamiento .
        """
        if  p0==2:
            self.valuenFFTPointOpSpec.setEnabled(True)
            print " nFFTPoint"
        if  p0==0:
            print " deshabilitado" 
            
    #------------------PUSH_BUTTON_SPECTRA_OK------------------------------------#   
                 
    @pyqtSignature("")
    def on_dataopSpecOkBtn_clicked(self):
        """
        Añade al archivo de configuración el parámetros nFFTPoints a la UP.
        """
        print "Añadimos operaciones Spectra,nchannels,value,format"
        if self.nFFTPointOpSpecCEB.isChecked():
            upProcessSelect=self.upobjSpecList[int(self.addOpSpecUpselec.currentIndex())]
            value=self.valuenFFTPointOpSpec.text()
            upProcessSelect.addParameter(name='nFFTPoints',value=value,format='int')
    #---------------------VENTANA DE CONFIGURACION GRAPH SPECTRA------------------#     

    @pyqtSignature("int")
    def on_SpectraPlotGraphCEB_stateChanged(self, p0):
        """
        Habilita la opcion de Ploteo Spectra Plot
        """
        if  p0==2:
            upProcessSelect=self.upobjSpecList[int(self.addOpSpecUpselec.currentIndex())]
            opObj10=upProcessSelect.addOperation(name='SpectraPlot',optype='other')
            print opObj10.id
            self.operObjList.append(opObj10)
    
        if  p0==0:
            print " deshabilitado" 
    
    @pyqtSignature("int")
    def on_CrossSpectraPlotGraphceb_stateChanged(self, p0):
        """
        Habilita la opción de Ploteo CrossSpectra
        """
        if  p0==2:
            upProcessSelect=self.upobjSpecList[int(self.addOpSpecUpselec.currentIndex())]
            opObj10=upProcessSelect.addOperation(name='CrossSpectraPlot',optype='other')
            print opObj10.id
            self.operObjList.append(opObj10) 
        if  p0==0:
            print " deshabilitado"    
        
    @pyqtSignature("int")
    def on_RTIPlotGraphCEB_stateChanged(self, p0):
        """
        Habilita la opción de Plote RTIPlot
        """
        if  p0==2:
            upProcessSelect=self.upobjSpecList[int(self.addOpSpecUpselec.currentIndex())]
            opObj10=upProcessSelect.addOperation(name='RTIPlot',optype='other')
            print opObj10.id
            self.operObjList.append(opObj10) 
        if  p0==0:
            print " deshabilitado"     
    
    #------------------PUSH_BUTTON_SPECTRA_GRAPH_OK-----------------------------#
    @pyqtSignature("")
    def on_dataGraphSpecOkBtn_clicked(self):
        """
        HABILITAR DE ACUERDO A LOS CHECKBOX QUE TIPO DE PLOTEOS SE VAN A REALIZAR MUESTRA Y GRABA LAS IMAGENES.
        """
        print "Graficar Spec op"
        if self.SpectraPlotGraphCEB.isChecked():
            for i in self.operObjList:
                if i.name=='SpectraPlot':
                    i.addParameter(name='idfigure', value='1', format='int')
                    i.addParameter(name='wintitle', value='SpectraPlot0', format='str')
                    i.addParameter(name='zmin', value='40', format='int')
                    i.addParameter(name='zmax', value='90', format='int')
                    i.addParameter(name='showprofile', value='1', format='int') 
            
        if self.CrossSpectraPlotGraphceb.isChecked():
            for i in self.operObjList:
                if i.name=='CrossSpectraPlot' :
                    i.addParameter(name='idfigure', value='2', format='int')
                    i.addParameter(name='wintitle', value='CrossSpectraPlot', format='str')
                    i.addParameter(name='zmin', value='40', format='int')
                    i.addParameter(name='zmax', value='90', format='int') 
            
        if self.RTIPlotGraphCEB.isChecked():
            for i in self.operObjList:
                if i.name=='RTIPlot':
                    i.addParameter(name='n', value='2', format='int')
                    i.addParameter(name='overlapping', value='1', format='int')
         
        
    def getNumberofProject(self):
#        for i in self.proObjList:
#            print i
        return self.proObjList
#        for  i in self.proObjList:
#            print i
        
    def setParam(self):
        
        self.tabWidgetProject.setEnabled(False)
        self.dataPathTxt.setText('C:\data')
        self.nameProjectTxt.setText("Test")
        self.numberChannelopVol.setEnabled(False)
        self.lineHeighProfileTxtopVol.setEnabled(False)
        self.numberIntegration.setEnabled(False)
        self.valuenFFTPointOpSpec.setEnabled(False)
        self.lineProfileSelecopVolCEB.setEnabled(False)
        
    
    def clickFunctiontree(self,index):
        indexclick= index.model().itemFromIndex(index).text()
        #print indexclick
        NumofPro=indexclick[8:10]
        self.valuep=NumofPro
        #print self.valuep
        NameofPro=indexclick[0:7]
        self.namepTree=NameofPro
        #print self.namepTree

    def addProject(self):
        self.tabWidgetProject.setEnabled(True)
        print "En este nivel se debe crear el proyecto,id,nombre,desc"
        #+++++Creacion del Objeto Controller-XML++++++++++#
     
        self.idp += 1
        self.projectObj = Project()
        self.description="Think"
        id=int(self.idp)
        name=str(self.nameProjectTxt.text())
        desc=str(self.description)
        
        self.projectObj.setup(id = id, name=name, description=desc)
        self.__projObjDict[id] = self.projectObj
        self.parentItem = self.model.invisibleRootItem()
        self.__arbolDict[id] =   QtGui.QStandardItem(QtCore.QString(name+" %0").arg(self.idp))
        self.parentItem.appendRow(self.__arbolDict[self.projectObj.id])
        self.parentItem=self.__arbolDict[id]
        
        #self.configProject=Window(self)
        #self.configProject.closed.connect(self.show)
        #self.configProject.show()
        #self.configProject.closed.connect(self.show)
       # self.configProject.saveButton.clicked.connect(self.reciveParameters)
        #self.configProject.closed.connect(self.createProject)
        

     
        

        
         
        
        #+++++++++++++++++++LISTA DE PROYECTO++++++++++++++++++++++++++++#
        
        
#        self.parentItem=self.projectObj.arbol
#        self.loadProjects()
        
        print "Porfavor ingrese los parÃ¡metros de configuracion del Proyecto"
        
        
        
        
        
    def reciveParameters(self):
        self.namep,self.description =self.configProject.almacena()
        
    def createProject(self):   
        
        print "En este nivel se debe crear el proyecto,id,nombre,desc"
        #+++++Creacion del Objeto Controller-XML++++++++++#
        self.idp += 1
        self.controllerObj = Project()
        id=int(self.idp)
        name=str(self.namep)
        desc=str(self.description)
        self.parentItem=self.model.invisibleRootItem()        
        self.controllerObj.arbol=QtGui.QStandardItem(QtCore.QString("Project %0").arg(self.idp))
        self.controllerObj.setup(id = id, name=name, description=desc)
        self.parentItem.appendRow(self.controllerObj.arbol)        
        self.proObjList.append(self.controllerObj)#+++++++++++++++++++LISTA DE PROYECTO++++++++++++++++++++++++++++#
        self.parentItem=self.controllerObj.arbol
        self.loadProjects()
        
        print "Porfavor ingrese los parámetros de configuracion del Proyecto"
        
    def loadProjects(self):
        
        self.proConfCmbBox.clear()
        for i in self.proObjList:
            self.proConfCmbBox.addItem("Project"+str(i.id))
                    
 
        
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
    
    def loadDays(self):
        """
        METODO PARA CARGAR LOS DIAS
        """
        self.variableList=[]     
        self.starDateCmbBox.clear()
        self.endDateCmbBox.clear()

        Dirlist =  os.listdir(self.dataPath)
        Dirlist.sort()     
        
        for a in range(0, len(Dirlist)):
            fname= Dirlist[a]
            Doy=fname[5:8]
            fname = fname[1:5]
            print fname
            fecha=Doy2Date(int(fname),int(Doy))
            fechaList=fecha.change2date()
            #print fechaList[0]
            Dirlist[a]=fname+"/"+str(fechaList[0])+"/"+str(fechaList[1])
            #+"-"+ fechaList[0]+"-"+fechaList[1]
    
        #---------------AQUI TIENE QUE SER MODIFICADO--------#

        #Se cargan las listas para seleccionar StartDay y StopDay (QComboBox)
        for i in range(0, (len(Dirlist))):
            self.variableList.append(Dirlist[i])
        
        for i in self.variableList:
            self.starDateCmbBox.addItem(i)
            self.endDateCmbBox.addItem(i)
        self.endDateCmbBox.setCurrentIndex(self.starDateCmbBox.count()-1)
    
        self.getsubList()    
        self.dataOkBtn.setEnabled(True)    
        
    def getsubList(self):
        """
        OBTIENE EL RANDO DE LAS FECHAS SELECCIONADAS
        """
        self.subList=[]
        for i in self.variableList[self.starDateCmbBox.currentIndex():self.starDateCmbBox.currentIndex() + self.endDateCmbBox.currentIndex()+1]:
            self.subList.append(i)  
       
    def addUP(self):
        
        self.configUP=UnitProcess(self)
        for i in self.proObjList:
            self.configUP.getfromWindowList.append(i) 
            #print i
        for i in self.upObjList:
            self.configUP.getfromWindowList.append(i)
        self.configUP.loadTotalList()
        self.configUP.show()      
        self.configUP.unitPsavebut.clicked.connect(self.reciveUPparameters)
        self.configUP.closed.connect(self.createUP)
    
    def reciveUPparameters(self):
        
        self.uporProObjRecover,self.upType=self.configUP.almacena()
           
        
    def createUP(self):
        print "En este nivel se adiciona una rama de procesamiento, y se le concatena con el id"
        projectObj=self.proObjList[int(self.proConfCmbBox.currentIndex())]
        
        datatype=str(self.upType)
        uporprojectObj=self.uporProObjRecover
        #+++++++++++LET FLY+++++++++++#
        if uporprojectObj.getElementName()=='ProcUnit':
            inputId=uporprojectObj.getId()
        elif uporprojectObj.getElementName()=='Project':    
            inputId=self.readUnitConfObjList[uporprojectObj.id-1].getId()

            
        self.procUnitConfObj1 = projectObj.addProcUnit(datatype=datatype, inputId=inputId)
        self.upObjList.append(self.procUnitConfObj1)
        print inputId  
        print self.procUnitConfObj1.getId()
        self.parentItem=uporprojectObj.arbol
        self.numbertree=int(self.procUnitConfObj1.getId())-1
        self.procUnitConfObj1.arbol=QtGui.QStandardItem(QtCore.QString(datatype +"%1 ").arg(self.numbertree))
        self.parentItem.appendRow(self.procUnitConfObj1.arbol)        
        self.parentItem=self.procUnitConfObj1.arbol
        self.loadUp()
        self.treeView.expandAll()
        
    def loadUp(self):
        self.addOpUpselec.clear()
        self.addOpSpecUpselec.clear()
        for i in self.upObjList:
            if i.datatype=='Voltage':
                self.upObjVolList.append(i)
                name=i.getElementName()
                id=int(i.id)-1 
                self.addOpUpselec.addItem(name+str(id))      
            if i.datatype=='Spectra':
                self.upobjSpecList.append(i)
                name=i.getElementName()
                id=int(i.id)-1 
                self.addOpSpecUpselec.addItem(name+str(id))
        
        self.resetopVolt()
        self.resetopSpec()

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
        if self.idp==1:
           self.valuep=1
            
        print "Escribiendo el archivo XML"
        filename="C:\\WorkspaceGUI\\CONFIG"+str(self.valuep)+".xml"
        self.controllerObj=self.proObjList[int(self.valuep)-1]
        self.controllerObj.writeXml(filename)




        
class Window(QMainWindow, Ui_window):
    """
    Class documentation goes here.
    """
    closed=pyqtSignal()
    def __init__(self, parent = None):
        """
        Constructor
        """
        QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.name=0
        self.nameproject=None
        self.proyectNameLine.setText('My_name_is...')
        self.descriptionTextEdit.setText('Write a description...')

    
    @pyqtSignature("")
    def on_cancelButton_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        #raise NotImplementedError
        
        self.hide()
        
    @pyqtSignature("")
    def on_okButton_clicked(self):
        """
        Slot documentation goes here.
        """
        #self.almacena()
        self.close()     

    @pyqtSignature("")
    def on_saveButton_clicked(self):
        """
        Slot documentation goes here.
        """
        self.almacena()
#        self.close()   
    
    def almacena(self):
        #print str(self.proyectNameLine.text())
        self.nameproject=str(self.proyectNameLine.text())
        self.description=str(self.descriptionTextEdit.toPlainText())
        return self.nameproject,self.description
     
    def closeEvent(self, event):
        self.closed.emit()
        event.accept()



#--------------------------------------VENTANA DE CONFIGURACION DE LA UP-----------------------#

class UnitProcess(QMainWindow, Ui_UnitProcess):
    """
    Class documentation goes here.
    """
    closed=pyqtSignal()
    def __init__(self, parent = None):
        """
        Constructor
        """
        QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.getFromWindow=None
        self.getfromWindowList=[]
 
        self.listUP=None    
        
    @pyqtSignature("")
    def on_unitPokbut_clicked(self):
        """
        Slot documentation goes here.
        """
        self.close()
        
    @pyqtSignature("")
    def on_unitPsavebut_clicked(self):
        """
        Slot documentation goes here.
        """
 
        print "alex"
        self.almacena()
    
    @pyqtSignature("")
    def on_unitPcancelbut_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        #raise NotImplementedError
        self.hide()  

    def loadTotalList(self):
        self.comboInputBox.clear()
        for i in self.getfromWindowList:
            name=i.getElementName()
            id= i.id
            if i.getElementName()=='ProcUnit':
               id=int(i.id)-1 
            self.comboInputBox.addItem(str(name)+str(id))
        
    def almacena(self):
        self.getFromWindow=self.getfromWindowList[int(self.comboInputBox.currentIndex())]
        #self.nameofUP= str(self.nameUptxt.text())
        self.typeofUP= str(self.comboTypeBox.currentText())
        return  self.getFromWindow,self.typeofUP    

    def closeEvent(self, event):
        self.closed.emit()
        event.accept()
    
    
    

    
    
    