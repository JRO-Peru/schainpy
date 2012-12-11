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
from viewer.ui_workspace import Ui_Workspace
from viewer.ui_initwindow import Ui_InitWindow

from controller import Project,ReadUnitConf,ProcUnitConf,OperationConf,ParameterConf
import os

HORIZONTAL_HEADERS = ("ITEM :"," DATOS  :  " )
    
HORIZONTAL = ("RAMA :",)

class MainWindow(QMainWindow, Ui_MainWindow):
    nop=None
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
        
        
        self.operObjList=[]
        
        self.configProject=None
        self.configUP=None
        
        self.controllerObj=None
        self.readUnitConfObj=None
        self.procUnitConfObj0=None
        self.opObj10=None
        self.opObj12=None
        
        
        self.setParam()

        
    def getNumberofProject(self):
#        for i in self.proObjList:
#            print i
        return self.proObjList
#        for  i in self.proObjList:
#            print i
        
    def setParam(self):
        self.dataPathTxt.setText('C:\\Users\\alex\\Documents\\ROJ\\ew_drifts')
        
    
    def clickFunctiontree(self,index):
        indexclick= index.model().itemFromIndex(index).text()
        #print indexclick
        NumofPro=indexclick[8:10]
        self.valuep=NumofPro
        #print self.valuep
        NameofPro=indexclick[0:7]
        self.namepTree=NameofPro
        #print self.namepTree

  
    @pyqtSignature("")
    def on_addpBtn_clicked(self):
        """
        ANADIR UN NUEVO PROYECTO
        """ 
        print "En este nivel se abre el window"


        self.showWindow()
        
    def showWindow(self):
        self.configProject=Window(self)
        #self.configProject.closed.connect(self.show)
        self.configProject.show()
        #self.configProject.closed.connect(self.show)
        self.configProject.saveButton.clicked.connect(self.reciveParameters)
        self.configProject.closed.connect(self.createProject)
        
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
                    
    @pyqtSignature("int")
    def on_dataTypeCmbBox_activated(self,index):
        self.dataFormatTxt.setReadOnly(True)
        if index==0:
           self.datatype='Voltage'
        elif index==1:
            self.datatype='Spectra'
        else :
              self.datatype=''
              self.dataFormatTxt.setReadOnly(False)
        self.dataFormatTxt.setText(self.datatype)
        
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
        SELECCION DEL RANGO DE FECHAS -STAR DATE
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
        Slot documentation goes here.
        """
        if p0==0:
           self.online=0
        elif p0==1:
            self.online=1
            
    @pyqtSignature("")
    def on_dataOkBtn_clicked(self):
        """
        Slot documentation goes here.
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
        
        
        
        
        
        
        
    @pyqtSignature("")
    def on_addUnitProces_clicked(self):
        """
        Slot documentation goes here.
        """
#        print "En este nivel se adiciona una rama de procesamiento, y se le concatena con el id"
#        self.procUnitConfObj0 = self.controllerObj.addProcUnit(datatype='Voltage', inputId=self.readUnitConfObj.getId())      
        self.showUp()

    def showUp(self):
        
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
        
        for i in self.upObjList:
            name=i.getElementName()
            id=int(i.id)-1 
            self.addOpUpselec.addItem(name+str(id))
         

            
    @pyqtSignature("int")
    def on_selecChannelopVolCEB_stateChanged(self, p0):
        """
        Slot documentation goes here.
        """
        if  p0==2:
            upProcessSelect=self.upObjList[int(self.addOpUpselec.currentIndex())]
            opObj10=upProcessSelect.addOperation(name='selectChannels')
            print opObj10.id
            self.operObjList.append(opObj10)
            print " Ingresa seleccion de Canales"
        if  p0==0:
            print " deshabilitado" 
            
    @pyqtSignature("int")
    def on_selecHeighopVolCEB_stateChanged(self, p0):
        """
        Slot documentation goes here.
        """
        if  p0==2:
            upProcessSelect=self.upObjList[int(self.addOpUpselec.currentIndex())]
            opObj10=upProcessSelect.addOperation(name='selectHeights')
            print opObj10.id
            self.operObjList.append(opObj10)
            print " Select Type of Profile"
        if  p0==0:
            print " deshabilitado" 
            
           
            
    @pyqtSignature("int")
    def on_coherentIntegrationCEB_stateChanged(self, p0):
        """
        Slot documentation goes here.
        """
        if  p0==2:
            upProcessSelect=self.upObjList[int(self.addOpUpselec.currentIndex())]
            opObj10=upProcessSelect.addOperation(name='CohInt', optype='other')
            print opObj10.id
            self.operObjList.append(opObj10)
            print "Choose number of Cohint"
        if  p0==0:
            print " deshabilitado"         
            

    @pyqtSignature("")
    def on_dataopVolOkBtn_clicked(self):
        """
        Slot documentation goes here.
        """   
#        print self.selecChannelopVolCEB.isOn()
#        print self.selecHeighopVolCEB.isOn()  
#        print self.coherentIntegrationCEB.isOn()
        
        
        
#        if self.coherentIntegrationCEB.enabled():
#            self.operObjList[0].        
#        
     
    @pyqtSignature("")
    def on_dataopSpecOkBtn_clicked(self):
        """
        Slot documentation goes here.
        """
        print "Añadimos operaciones Spectra,nchannels,value,format"

        opObj10 = self.procUnitConfObj0.addOperation(name='selectChannels')
        opObj10.addParameter(name='channelList', value='3,4,5', format='intlist')

        opObj10 = self.procUnitConfObj0.addOperation(name='selectHeights')
        opObj10.addParameter(name='minHei', value='90', format='float')
        opObj10.addParameter(name='maxHei', value='180', format='float')
    
        opObj12 = self.procUnitConfObj0.addOperation(name='CohInt', optype='other')
        opObj12.addParameter(name='n', value='10', format='int')
        

    @pyqtSignature("")
    def on_dataGraphSpecOkBtn_clicked(self):
        """
        Slot documentation goes here.
        """
        print "Graficar Spec op"
        # TODO: not implemented yet
        #raise NotImplementedError

        
               
        
    @pyqtSignature("")
    def on_actionguardarObj_triggered(self):
        """
        GUARDAR EL ARCHIVO DE CONFIGURACION XML
        """
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

    def loadTotalList(self):
        self.comboInputBox.clear()
        for i in self.getfromWindowList:
            name=i.getElementName()
            id= i.id
            if i.getElementName()=='ProcUnit':
               id=int(i.id)-1 
            self.comboInputBox.addItem(str(name)+str(id))

    @pyqtSignature("QString")
    def on_comboInputBox_activated(self, p0):
        """
        Slot documentation goes here.
        """
        
        # TODO: not implemented yet
        #raise NotImplementedError
    
    @pyqtSignature("QString")
    def on_comboTypeBox_activated(self, p0):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        #raise NotImplementedError
        
    @pyqtSignature("")
    def on_unitPokbut_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        #raise NotImplementedError
        self.close()
        
    @pyqtSignature("")
    def on_unitPsavebut_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        #raise NotImplementedError
        #self.getListMainWindow()
        print "alex"
        
        #for i in self.getfromWindowList:
            #print i
            
        self.almacena()
    
    @pyqtSignature("")
    def on_unitPcancelbut_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        #raise NotImplementedError
        self.hide()
        
    def almacena(self):
        self.getFromWindow=self.getfromWindowList[int(self.comboInputBox.currentIndex())]
        #self.nameofUP= str(self.nameUptxt.text())
        self.typeofUP= str(self.comboTypeBox.currentText())
        return  self.getFromWindow,self.typeofUP    

    def closeEvent(self, event):
        self.closed.emit()
        event.accept()
    
    
    

    
    
    