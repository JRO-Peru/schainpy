# -*- coding: utf-8 -*-
from PyQt4 import QtCore
import itertools

HORIZONTAL_HEADERS = ("Property","Value " )
    
HORIZONTAL = ("RAMA :",)
   
class treeModel(QtCore.QAbstractItemModel):
    '''
    a model to display a few names, ordered by encabezado
    
    '''
    def __init__(self ,parent=None):
        super(treeModel, self).__init__(parent)
        self.people = []
        self.initProjectProperties()
        self.initPUVoltageProperties()
        self.initPUSpectraProperties()
        self.initPUSpectraHeisProperties()
        
    def initProjectProperties(self):

        name=None
        directorio=None 
        workspace=None
        remode=None
        dataformat=None
        startDate=None
        endDate=None
        startTime=None
        endTime=None
        delay=None
        set= None
        walk=None
        timezone=None
        Summary=None        
        description=None
        
    def initPUVoltageProperties(self):
        type=None
        channel=None
        heights=None
        filter=None
        profile=None
        code=None
        mode=None
        coherentintegration=None
        
    def initPUSpectraProperties(self):
        type =None
        nFFTpoints =None
        ippFactor = None
        pairsList =None
        channel =None
        heights =None
        incoherentintegration =None
        removeDC = None
        removeInterference =None
        getNoise = None
        operationSpecPlot=None
        operationCrossSpecPlot = None
        operationRTIPlot = None
        operationCohermap = None
        operationPowProfilePlot = None
        
    def initPUSpectraHeisProperties(self):
        type =None
        incoherentintegration =None
        operationSpecHeisPlot=None
        operationRTIHeisPlot = None

    def initProjectView(self):
        """
        Reemplazo del método showtree
        """
        HORIZONTAL_HEADERS = ("Property","Value " )
        HORIZONTAL = ("RAMA :",)
        self.rootItem = TreeItem(None, "ALL", None)
        self.parents = {0 : self.rootItem}
        self.setupModelData()
    
    def initPUVoltageView(self):
        HORIZONTAL_HEADERS = ("Operation"," Parameter Value " )
        HORIZONTAL = ("RAMA :",)
        self.rootItem = TreeItem(None, "ALL", None)
        self.parents = {0 : self.rootItem}
        self.setupModelData()
        
    def showProjectParms(self,caracteristicaList,principalList,descripcionList):
        """
        set2Obje
        """   
        for caracteristica,principal, descripcion in  itertools.izip(caracteristicaList,principalList,descripcionList):     
            person = person_class(caracteristica, principal, descripcion)
            self.people.append(person)
        self.rootItem = TreeItem(None, "ALL", None)
        self.parents = {0 : self.rootItem}
        self.setupModelData()
    
    def showPUVoltageParms(self,caracteristicaList,principalList,descripcionList):

        for caracteristica,principal, descripcion in itertools.izip(caracteristicaList,principalList,descripcionList):
            person = person_class(caracteristica, principal, descripcion)
            self.people.append(person)
        self.rootItem = TreeItem(None, "ALL", None)
        self.parents = {0 : self.rootItem}
        self.setupModelData()
            
        
    def showPUSpectraParms(self,caracteristicaList,principalList,descripcionList):

        for caracteristica,principal, descripcion in itertools.izip(caracteristicaList,principalList,descripcionList):
            person = person_class(caracteristica, principal, descripcion)
            self.people.append(person)
        self.rootItem = TreeItem(None, "ALL", None)
        self.parents = {0 : self.rootItem}
        self.setupModelData()
        
    def showPUSpectraHeisParms(self,caracteristicaList,principalList,descripcionList):

        for caracteristica,principal, descripcion in itertools.izip(caracteristicaList,principalList,descripcionList):
            person = person_class(caracteristica, principal, descripcion)
            self.people.append(person)
        self.rootItem = TreeItem(None, "ALL", None)
        self.parents = {0 : self.rootItem}
        self.setupModelData()

    
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


class person_class(object):
    '''
    a trivial custom data object
    '''
    def __init__(self, caracteristica, principal, descripcion):
        self.caracteristica = caracteristica
        self.principal = principal
        self.descripcion = descripcion

    def __repr__(self):
        return "PERSON - %s %s"% (self.principal, self.caracteristica)
    
class TreeItem(object):
    '''
    a python object used to return row/column data, and keep note of
    it's parents and/or children
    '''
    def __init__(self, person, header, parentItem):
        self.person = person
        self.parentItem = parentItem
        self.header = header
        self.childItems = []

    def appendChild(self, item):
        self.childItems.append(item)

    def child(self, row):
        return self.childItems[row]

    def childCount(self):
        return len(self.childItems)

    def columnCount(self):
        return 2
    
    def data(self, column):
        if self.person == None:
            if column == 0:
                return QtCore.QVariant(self.header)
            if column == 1:
                return QtCore.QVariant("")                
        else:
            if column == 0:
                return QtCore.QVariant(self.person.principal)
            if column == 1:
                return QtCore.QVariant(self.person.descripcion)
        return QtCore.QVariant()

    def parent(self):
        return self.parentItem
    
    def row(self):
        if self.parentItem:
            return self.parentItem.childItems.index(self)
        return 0
    