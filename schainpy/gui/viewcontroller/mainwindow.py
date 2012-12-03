# -*- coding: utf-8 -*-
"""
Module implementing MainWindow.
#+ ######################INTERFAZ DE USUARIO V1.1##################
"""
from PyQt4.QtGui import QMainWindow
from PyQt4.QtCore import pyqtSignature
from PyQt4.QtCore import pyqtSignal

from PyQt4 import QtCore
from PyQt4 import QtGui

from timeconversions import  Doy2Date

from modelProperties import person_class
from modelProperties import TreeItem


from viewer.ui_window import Ui_window
from viewer.ui_mainwindow import Ui_MainWindow
from viewer.ui_workspace import Ui_Workspace
from viewer.ui_initwindow import Ui_InitWindow

from controller1 import Project,ReadBranch,ProcBranch,UP,UPSUB,UP2SUB,Operation,Parameter

import os

HORIZONTAL_HEADERS = ("ITEM :"," DATOS  :  " )
    
HORIZONTAL = ("RAMA :",)

class MainWindow(QMainWindow, Ui_MainWindow):
    """
    Class documentation goes here.
    #*##################VENTANA CUERPO  DEL PROGRAMA####################
    """
    closed=pyqtSignal()
    def __init__(self, parent = None):
        """
        Constructor
        1-CARGA DE ARCHIVOS DE CONFIGURACION SI EXISTIERA.SI EXISTE EL ARCHIVO PROYECT.xml
        2- ESTABLECE CIERTOS PARAMETROS PARA PRUEBAS
        3- CARGA  LAS VARIABLES DE LA CLASE CON LOS PARAMETROS SELECCIONADOS
        4-VALIDACION DE LA RUTA DE LOS DATOS Y DEL PROYECTO
        5-CARGA LOS DOYS ENCONTRADOS PARA SELECCIONAR EL RANGO
        6-CARGA UN PROYECTO
        """
        
        print "Inicio de Programa"
        QMainWindow.__init__(self, parent)
  
        self.setupUi(self)
        
        QtGui.QToolTip.setFont(QtGui.QFont('SansSerif', 10))
        self.addoBtn.setToolTip('Add_Unit_Process')
        self.addbBtn.setToolTip('Add_Branch')
        self.addpBtn.setToolTip('Add_New_Project')
        self.ventanaproject=0
        
        self.var=0
        self.variableList=[] # Lista de DOYs
        self.iniciodisplay=0
        self.year=0
        self.OpMode=0
        self.starTem=0
        self.endTem=0
#*###################1########################
        if os.path.isfile("Proyect.xml"):
            self.getParam() 
            self.textedit.append("Parameters were loaded from configuration file")
#*###################2########################
        else:
            self.setParam()
#*###################3#########################
        self.setVariables() 
#*###################4#########################
        self.statusDpath = self.existDir(self.dataPath)
        #self.statusRpath = self.dir_exists(self.var_Rpath,  self)
#*###################5 ########################
        self.loadYears()
        self.loadDays() 
#================================       
        
        self.model = QtGui.QStandardItemModel()
        self.treeView.setModel(self.model)
        self.treeView.clicked.connect(self.treefunction1)
#==========Project==========#
        self.projectObjList= []
        self.ProjectObj=0
        self.Pro=0
        self.proObjList=[]
        self.valuep=1
        self.namep=0
        self.idp=0
        self.refresh=0
        self.countBperPObjList= []
#===========Branch==========#        
        self.branchObjList=[]
        self.BranchObj=0
        self.braObjList=[]
        self.Bra=0
        self.idb=0 
        self.nameb=0 
        self.countVperBObjList= []
#===========Voltage==========#        
        self.voltageObjList=[]
        self.VoltageObj=0
        self.Vol=0 
        self.volObjList=[]  
        self.idv=0
        self.namev=0 
#===========Spectra==========#        
        self.spectraObjList=[]
        self.SpectraObj=0  
        self.Spec=0
        self.specObjList=[] 
        self.ids=0
        self.names=0 
#===========Correlation==========#        
        self.correlationObjList=[]
        self.CorrelationObj=0   
        self.Cor=0
        self.corObjList=[]
        self.idc=0
        self.namec=0 
        self.datatype=0
        
#=================        
        #self.window=Window()
        self.Workspace=Workspace()
        #self.DataType=0
        
        
#*###################

    def treefunction1(self, index):
        a= index.model().itemFromIndex(index).text()
        print a
        b=a[8:10]
        self.valuep=b
        c=a[0:7]
        self.namep=c

#    def ventanaconfigura(self):
#        '''
#         METODO QUE SE ENCARGA DE LLAMAR A LA CLASE
#         VENTANA CONFIGURACION DE PROYECTO
#        '''
#        self.Luna =Workspace(self)
#        self.Luna.closed.connect(self.show)
#        self.Luna.show()
#        self.hide()

#    def closeEvent(self, event):
#        self.closed.emit()
#        event.accept()
       
    #+######################BARRA DE MENU###################

    # *####################MENU FILE #########################
    
    @pyqtSignature("")
    def on_actionabrirObj_triggered(self):
        """
        Ubicado en la Barra de Menu, OPCION FILE, CARGA UN ARCHIVO DE CONFIGURACION ANTERIOR
        """
        # TODO: not implemented yet
        #raise NotImplementedError
        
    
    @pyqtSignature("")
    def on_actioncrearObj_triggered(self):
        """
       CREACION DE UN NUEVO EXPERIMENTO
        """
        self.on_addpBtn_clicked()
        
    @pyqtSignature("")
    def on_actionguardarObj_triggered(self):
        """
        GUARDAR EL ARCHIVO DE CONFIGURACION XML
        """
        # TODO: not implemented yet
        #raise NotImplementedError
        self.SaveConfig()
        
    @pyqtSignature("")
    def on_actionCerrarObj_triggered(self):
        """
       CERRAR LA APLICACION GUI
        """
        self.close()

#*######################### MENU RUN  ################## 

    @pyqtSignature("")
    def on_actionStartObj_triggered(self):
        """
        EMPEZAR EL PROCESAMIENTO.
        """
        # TODO: not implemented yet
        #raise NotImplementedErr    

    @pyqtSignature("")
    def on_actionPausaObj_triggered(self):
        """
       PAUSAR LAS OPERACIONES
        """
        # TODO: not implemented yet
        # raise NotImplemente

#*###################MENU OPTIONS######################
    
    @pyqtSignature("")
    def on_actionconfigLogfileObj_triggered(self):
        """
        Slot Documentation goes here
        """
        self.Luna = Workspace(self)
        #print self.Luna.dirCmbBox.currentText()
    
    @pyqtSignature("")
    def on_actionconfigserverObj_triggered(self):
        """
        CONFIGURACION DE SERVIDOR.
        """
        # TODO: not implemented yet
        #raise NotImplementedError

#*################# MENU HELPS##########################
       
    @pyqtSignature("")
    def on_actionAboutObj_triggered(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        #raise NotImplementedError
        
    @pyqtSignature("")
    def on_actionPrfObj_triggered(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        #raise NotImplementedError 

#+##################################################

    @pyqtSignature("")
    def on_actionOpenObj_triggered(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        #raise No
       
    @pyqtSignature("")
    def on_actioncreateObj_triggered(self):
        """
        Slot documentation goes here.
        """
        self.on_addpBtn_clicked()
         
    @pyqtSignature("")
    def on_actionstopObj_triggered(self):
        """
       CARGA UN ARCHIVO DE CONFIGURACION ANTERIOR
        """
        # TODO: not implemented yet
        #raise NotImplementedError

    @pyqtSignature("")
    def on_actionPlayObj_triggered(self):
        """
        EMPEZAR EL PROCESAMIENTO.
        """
        # TODO: not implemented yet
        #raise NotImplementedError

#*################VENTANA EXPLORADOR DE PROYECTOS######################
    
    @pyqtSignature("")
    def on_addpBtn_clicked(self):
        """
        AADIR UN NUEVO PROYECTO
        """
        self.windowshow()
        self.idp += 1    
        self.Pro=Project()
        self.proObjList.append(self.Pro)
        self.parentItem=self.model.invisibleRootItem()
        self.ProjectObj = QtGui.QStandardItem(QtCore.QString("Project %0").arg(self.idp))
        self.parentItem.appendRow(self.ProjectObj)
        self.projectObjList.append(self.ProjectObj)
        self.parentItem=self.ProjectObj

    @pyqtSignature("")
    def on_addbBtn_clicked(self):
        """
        AÃ‘ADIR UNA RAMA DE PROCESAMIENTO 
        """
        #print self.valuep
        #print  self.namep 
        #print self.valueb
      
        #if self.namep ==str("Project"):
        self.idb += 1
        self.Bra=self.proObjList[int(self.valuep)-1].addProcBranch(id=self.idb,name='Branch')
        self.braObjList.append(self.Bra)
        self.parentItem=self.projectObjList[int(self.valuep)-1]
            #=
        self.countBperPObjList.append(self.valuep)
#        LisBperP=self.countBperPObjList
          
        self.BranchObj= QtGui.QStandardItem(QtCore.QString("Branch  %1 ").arg(self.idb))
        self.parentItem.appendRow(self.BranchObj)
        self.branchObjList.append(self.BranchObj)         
        self.parentItem=self.BranchObj
        
    @pyqtSignature("")
    def on_addoBtn_clicked(self):
        """
       AÃ‘ADIR UN TIPO DE PROCESAMIENTO.
        """
        if self.namep ==str("Project"):
            self.totalTree()
#=====================
        if self.namep ==str("Voltage"):
            self.ids += 1 
            self.Spec=self.volObjList[int(self.valuep)-1].addUPSUB(id=self.ids, name='Spectra', type='Pri') 
            self.specObjList.append(self.Spec)
            self.parentItem=self.voltageObjList[int(self.valuep)-1]
            self.SpectraObj= QtGui.QStandardItem(QtCore.QString("Spectra %2").arg(self.ids))
            self.parentItem.appendRow(self.SpectraObj)
            self.spectraObjList.append(self.SpectraObj)
            self.parentItem=self.SpectraObj
      
        if self.namep ==str("Spectra"):
            self.idc += 1
            self.Cor=self.specObjList[int(self.valuep)-1].addUP2SUB(id=self.idc, name='Correlation', type='Pri') 
            self.corObjList.append(self.Cor)
            self.parentItem=self.spectraObjList[int(self.valuep)-1]  
            self.CorrelationObj= QtGui.QStandardItem(QtCore.QString("Correlation %3").arg(self.idc))
            self.parentItem.appendRow(self.CorrelationObj)
            self.correlationObjList.append(self.CorrelationObj)
            self.parentItem=self.CorrelationObj
           
        if self.namep == str("Branch "):      
            if self.DataType== str("r"):
                self.idv += 1
                if len(self.valuep)==0:
                    print "construir rama"
                else:                   
                    self.Vol=self.braObjList[int(self.valuep)-1].addUP(id=self.idv, name='Voltage', type='Pri') 
                    self.volObjList.append(self.Vol)
                    self.parentItem=self.branchObjList[int(self.valuep)-1] 
                    self.VoltageObj= QtGui.QStandardItem(QtCore.QString("Voltage %2").arg(self.idv))
                    self.parentItem.appendRow(self.VoltageObj)
                    self.voltageObjList.append(self.VoltageObj)
                    self.parentItem=self.VoltageObj
           
            if self.DataType== str("pdata"):
                self.ids += 1
                if len(self.valuep)==0:
                    print "construir rama"
                else:  
                    self.Spec=self.braObjList[int(self.valuep)-1].addUPSUB(id=self.ids, name='Spectra', type='Pri') 
                    self.specObjList.append(self.Spec)  
                    self.parentItem=self.branchObjList[int(self.valuep)-1]
                    self.SpectraObj= QtGui.QStandardItem(QtCore.QString("Spectra %2").arg(self.ids))
                    self.parentItem.appendRow(self.SpectraObj)
                    self.spectraObjList.append(self.SpectraObj)
                    self.parentItem=self.SpectraObj

    def totalTree(self):
        b= self.proObjList[int(self.valuep)-1]
        b.procBranchObjList # Objetos de tipo Branch  
        print "Project"+str(self.valuep) +"Branch",  
        for i in range(0 , len(b.procBranchObjList)):
            print b.procBranchObjList[i].id, #objetos de tipo branch 1,2,3 o 4,5 o 6
        print ""
        for i in range(0 , len(b.procBranchObjList)):
            print "Branch"+ str(b.procBranchObjList[i].id)
            
        for i in range(0 , len(b.procBranchObjList)):
            print b.procBranchObjList[i].id
            c= self.braObjList[(b.procBranchObjList[i].id)-1]    
            c.upsubObjList
            for i in range(0,len(c.upsubObjList)):
                print "Spectra"+str(c.upsubObjList[i].id),
#*********************VENTANA CONFIGURACION DE PROYECTOS************************************

#***********************PESTAÑA DE PROYECTOS************************

#*************************MODO BASICO O AVANZADO*****************
    
    @pyqtSignature("QString")
    def on_operationModeCmbBox_activated(self, p0):
        """
        Slot documentation goes here.
        """
        pass  
    
#***********************TIPOS DE DATOS A GRABAR******************************

    @pyqtSignature("int")
    def on_dataFormatCmbBox_activated(self,index):
        """
        SE EJECUTA CUANDO SE ELIGE UN ITEM DE LA LISTA 
        ADEMAS SE CARGA LA LISTA DE DIAS SEGUN EL TIPO DE ARCHIVO SELECCIONADO
        """
        self.dataFormatTxt.setReadOnly(True)
        if  index == 0:
            self.DataType ='r'
        elif index == 1:
                self.DataType ='pdata'
        else :
                self.DataType =''
                self.dataFormatTxt.setReadOnly(False)
        self.dataFormatTxt.setText(self.DataType)
# self.loadDays(self)

    @pyqtSignature("")
    def on_dataPathBrowse_clicked(self):
        """
        OBTENCION DE LA RUTA DE DATOS
        """
        self.dataPath = str(QtGui.QFileDialog.getExistingDirectory(self, 'Open Directory', './',  QtGui.QFileDialog.ShowDirsOnly))
        self.dataPathTxt.setText(self.dataPath)
        self.statusDpath=self.existDir(self.dataPath)
        self.loadYears()
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
    
    @pyqtSignature("QString")
    def on_readModeCmBox_activated(self, p0):
        """
        Slot documentation goes here.
        """
        print  self.readModeCmBox.currentText()
                  
    @pyqtSignature("int")
    def on_initialTimeSlider_valueChanged(self, initvalue):
        """
        SELECCION DE LA HORA DEL EXPERIMENTO -INITIAL TIME
        """
        self.iniciodisplay=initvalue
        self.initialtimeLcd.display(initvalue)
        self.starTem=initvalue
        
    @pyqtSignature("int")
    def on_finalTimeSlider_valueChanged(self, finalvalue):
        """
       SELECCION DE LA HORA DEL EXPERIMENTO -FINAL TIME
        """
        finalvalue = self.iniciodisplay + finalvalue
        if finalvalue >24:
            finalvalue = 24
        self.finaltimeLcd.display(finalvalue)
        self.endTem=finalvalue
        
    @pyqtSignature("QString")
    def on_yearCmbBox_activated(self, year):
        """
        SELECCION DEL AÃ‘O
        """
        self.year = year
        #print self.year
       
    @pyqtSignature("")
    def on_dataCancelBtn_clicked(self):
        """
        SAVE- BUTTON CANCEL
        """
        # TODO: not implemented yet
        #raise NotImplementedError
                
    @pyqtSignature("")
    def on_dataOkBtn_clicked(self):
        """
        SAVE-BUTTON OK
        """
        #print self.ventanaproject.almacena()
        print "alex"
        print self.Workspace.dirCmbBox.currentText()
        self.model_2=treeModel()
        #lines = unicode(self.textEdit_2.toPlainText()).split('\n')
        #print lines
        if self.ventanaproject.almacena()==None:
            name=str(self.namep)
        name=str(self.ventanaproject.almacena())
            
        self.model_2.setParams(name=name,
                                directorio=str(self.dataPathTxt.text()),
                                workspace=str(self.Workspace.dirCmbBox.currentText()),
                                 opmode=str(self.operationModeCmbBox.currentText()),
                                  remode=str(self.readModeCmBox.currentText()), 
                                   dataformat=str(self.dataFormatTxt.text()), 
                                    date=str(self.starDateCmbBox.currentText())+"-"+str(self.endDateCmbBox.currentText()),
                                     initTime=str( self.starTem),
                                       endTime=str(self.endTem),
                                        timezone="Local" )
                                        # Summary=str(self.textEdit_2.textCursor()))
        self.model_2.arbol()
        self.treeView_2.setModel(self.model_2)
        self.treeView_2.expandAll()
        
#*############METODOS PARA EL PATH-YEAR-DAYS###########################
   
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
               
    def loadYears(self):
        """
        METODO PARA SELECCIONAR EL AÑO
        """
        self.variableList=[]
        self.yearCmbBox.clear()
        if self.statusDpath == False:
            self.dataOkBtn.setEnabled(False)
            return
        if self.DataType == '':
            return
    
        Dirlist =  os.listdir(self.dataPath)

        for y in range(0, len(Dirlist)):
            fyear= Dirlist[y]
            fyear = fyear[1:5]
            Dirlist[y]=fyear 
            
        Dirlist=list(set(Dirlist))
        Dirlist.sort()

        if len(Dirlist) == 0: 
            self.textEdit.append("File not found")
            self.dataOkBtn.setEnabled(False)
            return
        #Se cargan las listas para seleccionar StartDay y StopDay (QComboBox)
        for i in range(0, (len(Dirlist))):
            self.variableList.append(Dirlist[i])
        for i in self.variableList:
            self.yearCmbBox.addItem(i)

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
            Dirlist[a]=fname+"-"+str(fechaList[0])+"-"+str(fechaList[1])
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
            
#*################ METODO PARA GUARDAR ARCHIVO DE CONFIGURACION ################# 
#    def SaveConfig(self):
#        
#            desc = "Este es un test"
#            filename=str(self.workspace.dirCmbBox.currentText())+"\\"+"Config"+str(self.valuep)+".xml" 
#            projectObj=self.proObjList[int(self.valuep)-1]
#            projectObj.setParms(id =int(self.valuep),name=str(self.namep),description=desc)
#            print self.valuep
#            print self.namep
#
#            readBranchObj = projectObj.addReadBranch(id=str(self.valuep),
#                                                       dpath=str(self.dataPathTxt.text()),
#                                                        dataformat=str(self.dataFormatTxt.text()),
#                                                        opMode=str(self.operationModeCmbBox.currentText()),
#                                                          readMode=str(self.readModeCmBox.currentText()),
#                                                           startDate=str(self.starDateCmbBox.currentText()),
#                                                             endDate=str(self.endDateCmbBox.currentText()), 
#                                                               startTime=str(self.starTem), 
#                                                                   endTime=str(self.endTem))
#
#           
#            branchNumber= len(projectObj.procBranchObjList)   #Numero de Ramas
#        #=======================readBranchObj==============
#            for i in range(0,branchNumber):
#                projectObj.procBranchObjList[i]
#                idb=projectObj.procBranchObjList[i].id        
#    #       opObjTotal={}  
#            
#            for j in range(0,branchNumber):
#                idb=projectObj.procBranchObjList[j].id 
#                branch=self.braObjList[(idb)-1] 
#                branch.upObjList
#                volNumber=len(branch.upObjList)
#                for i in range(0,volNumber):
#                    unitProcess=branch.upObjList[i]
#                    idv=branch.upObjList[i].id
#                    
#                    opObj11 = unitProcess.addOperation(id=1,name='removeDC', priority=1)
#                    opObj11.addParameter(name='type', value='1')
#                    opObj2 = unitProcess.addOperation(id=2,name='removeInterference', priority=1)
#                    opObj3 = unitProcess.addOperation(id=3,name='removeSatelites', priority=1)
#                    opObj4 = unitProcess.addOperation(id=4,name='coherent Integration', priority=1)
#
#            projectObj.writeXml(filename)
#                                
#*############METODOS PARA INICIALIZAR-CONFIGURAR-CARGAR ARCHIVO-CARGAR VARIABLES########################

    def setParam(self):
        """
        INICIALIZACION DE PARAMETROS PARA PRUEBAS
        """
        #self.dataProyectTxt.setText('Test')
        self.dataFormatTxt.setText('r')
        self.dataPathTxt.setText('C:\\Users\\alex\\Documents\\ROJ\\ew_drifts')
        self.dataWaitTxt.setText('0')
   
    def make_parameters_conf(self):    
        """
        ARCHIVO DE CONFIGURACION cCRA parameters.conf
        """
        pass

    def getParam(self):
        """
        CARGA  Proyect.xml
        """
        print "Archivo XML AUN No adjuntado"

    def setVariables(self):
        """
        ACTUALIZACION DEL VALOR DE LAS VARIABLES CON LOS PARAMETROS SELECCIONADOS
        """
        self.dataPath = str(self.dataPathTxt.text()) #0
        self.DataType= str(self.dataFormatTxt.text()) #3
    
    def windowshow(self):
        self.ventanaproject= Window(self)
        self.ventanaproject.closed.connect(self.show)
        self.ventanaproject.show()
#        self.window()
#        self.window.closed.connect(self.show)
#        self.window.show()
        #self.hide()
        
    def closeEvent(self, event):
        self.closed.emit()
        event.accept()


class treeModel(QtCore.QAbstractItemModel):
    '''
    a model to display a few names, ordered by encabezado
    '''
    name=None
    directorio=None 
    workspace=None
    opmode=None
    remode=None
    dataformat=None
    date=None
    initTime=None
    endTime=None
    timezone=None
    #Summary=None
    
    def __init__(self ,parent=None):
        super(treeModel, self).__init__(parent)
        self.people = []
        
    def arbol(self):     
            for caracteristica,principal, descripcion in   (("Properties","Name",self.name), 
                                                            ("Properties","Data Path",self.directorio),
                                                            ("Properties","Workspace",self.workspace),
                                                            ("Properties","Operation Mode ",self.opmode),  
                                                            ("Parameters", "Read Mode     ",self.remode),
                                                            ("Parameters", "DataFormat    ",self.dataformat),
                                                            ("Parameters", "Date          ",self.date),
                                                            ("Parameters", "Init Time     ",self.initTime),
                                                            ("Parameters", "Final Time    ",self.endTime),
                                                            ("Parameters", " Time zone    ",self.timezone),
                                                            ("Parameters", "Profiles      ","1"),
                                                          #  ("Description", "Summary      ", self.Summary),
                                                            ):
                person = person_class(caracteristica, principal, descripcion)
                self.people.append(person)
                
            self.rootItem = TreeItem(None, "ALL", None)
            self.parents = {0 : self.rootItem}
            self.setupModelData()
        
    #def veamos(self):
    #    self.update= MainWindow(self)
    #    self.update.dataProyectTxt.text()
    #    return self.update.dataProyectTxt.text()
    def setParams(self,name,directorio,workspace,opmode,remode,dataformat,date,initTime,endTime,timezone):
        self.name=name
        self.workspace=workspace
        self.directorio= directorio
        self.opmode=opmode
        self.remode=remode
        self.dataformat=dataformat
        self.date=date
        self.initTime=initTime
        self.endTime=endTime
        self.timezone=timezone
        #self.Summary=Summary
        
    
    def columnCount(self, parent=None):
        if parent and parent.isValid():
            return parent.internalPointer().columnCount()
        else:
            return len(HORIZONTAL_HEADERS)

    def data(self, index, role):
        if not index.isValid():
            return QtCore.QVariant()

        item = index.internalPointer()
        if role == QtCore.Qt.DisplayRole:
            return item.data(index.column())
        if role == QtCore.Qt.UserRole:
            if item:
                return item.person

        return QtCore.QVariant()

    def headerData(self, column, orientation, role):
        if (orientation == QtCore.Qt.Horizontal and
        role == QtCore.Qt.DisplayRole):
            try:
                return QtCore.QVariant(HORIZONTAL_HEADERS[column])
            except IndexError:
                pass

        return QtCore.QVariant()

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QtCore.QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()

        childItem = index.internalPointer()
        if not childItem:
            return QtCore.QModelIndex()
        
        parentItem = childItem.parent()

        if parentItem == self.rootItem:
            return QtCore.QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent=QtCore.QModelIndex()):
        if parent.column() > 0:
            return 0
        if not parent.isValid():
            p_Item = self.rootItem
        else:
            p_Item = parent.internalPointer()
        return p_Item.childCount()
    
    def setupModelData(self):
        for person in self.people:
            if person.descripcion:
                encabezado = person.caracteristica
     
            
            if not self.parents.has_key(encabezado):                
                newparent = TreeItem(None, encabezado, self.rootItem)
                self.rootItem.appendChild(newparent)

                self.parents[encabezado] = newparent

            parentItem = self.parents[encabezado]
            newItem = TreeItem(person, "", parentItem)
            parentItem.appendChild(newItem)
        
    def searchModel(self, person):
        '''
        get the modelIndex for a given appointment
        '''
        def searchNode(node):
            '''
            a function called recursively, looking at all nodes beneath node
            '''
            for child in node.childItems:
                if person == child.person:
                    index = self.createIndex(child.row(), 0, child)
                    return index
                    
                if child.childCount() > 0:
                    result = searchNode(child)
                    if result:
                        return result
        
        retarg = searchNode(self.parents[0])
        #print retarg
        return retarg
            
    def find_GivenName(self, principal):
        app = None
        for person in self.people:
            if person.principal == principal:
                app = person
                break
        if app != None:
            index = self.searchModel(app)
            return (True, index)            
        return (False, None)

             
    
class Workspace(QMainWindow, Ui_Workspace):
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
        #*#######   DIRECTORIO DE TRABAJO  #########*#
        self.dirCmbBox.setItemText(0, QtGui.QApplication.translate("MainWindow", "C:\WorkSpaceGui", None, QtGui.QApplication.UnicodeUTF8))
        self.dir=str("C:\WorkSpaceGui")
        self.dirCmbBox.addItem(self.dir)
                  
    @pyqtSignature("")
    def on_dirBrowsebtn_clicked(self):
        """
        Slot documentation goes here.
        """
        self.dirBrowse = str(QtGui.QFileDialog.getExistingDirectory(self, 'Open Directory', './',  QtGui.QFileDialog.ShowDirsOnly))
        self.dirCmbBox.addItem(self.dirBrowse)
        
    @pyqtSignature("")
    def on_dirButton_clicked(self):
        """
        Slot documentation goes here.
        """

    @pyqtSignature("")
    def on_dirOkbtn_clicked(self):
        """
        VISTA DE INTERFAZ GRÃFICA
        """
        self.showmemainwindow()
    
               
    @pyqtSignature("")
    def on_dirCancelbtn_clicked(self):
        """
        Cerrar
        """
        self.close()
        
    def showmemainwindow(self):
        self.Dialog= MainWindow(self)
        self.Dialog.closed.connect(self.show)
        self.Dialog.show()
        self.hide()

    def closeEvent(self, event):
        self.closed.emit()
        event.accept()
    

class InitWindow(QMainWindow, Ui_InitWindow):
    """
    Class documentation goes here.
    """
    def __init__(self, parent = None):
        """
        Constructor
        """
        QMainWindow.__init__(self, parent)
        self.setupUi(self)
    
    
    @pyqtSignature("")
    def on_pushButton_2_clicked(self):
        """
        Close First Window 
        """
        self.close()  

    @pyqtSignature("")
    def on_pushButton_clicked(self):
        """
        Show Workspace Window
        """
        self.showmeconfig()
    
    def showmeconfig(self):
        '''
        Method to call Workspace
        '''
      
        self.config=Workspace(self)
        self.config.closed.connect(self.show)
        self.config.show()
        self.hide()


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
        # TODO: not implemented yet
        #raise NotImplementedError
        self.almacena()
        print self.nameproject
        self.close()
        
    
    def almacena(self):
        #print str(self.proyectNameLine.text())
        self.nameproject=str(self.proyectNameLine.text())
        return self.nameproject
     
    def closeEvent(self, event):
        self.closed.emit()
        event.accept()
    
        
        


    