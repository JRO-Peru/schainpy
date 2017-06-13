# -*- coding: utf-8 -*-
"""
This module contains every model class to create, modify and show a property tree on a GUI. 
"""

from PyQt4 import QtCore
import itertools

HORIZONTAL_HEADERS = ("Property","Value " )
    
HORIZONTAL = ("RAMA :",)

class PropertyBuffer():
    
    def __init__(self):
        
        self.clear()
        
    def clear(self):
        
        self.headerList = []
        self.parmList = []
        self.valueList = []
    
    def append(self, header, parm, value):
        
        self.headerList.append(header)
        self.parmList.append(parm)
        self.valueList.append(value)
        
        return
    
    def get(self):
        
        return self.headerList, self.parmList, self.valueList
    
    def getPropertyModel(self):
        
        propertiesModel = TreeModel()
        propertiesModel.showProperties(self.headerList, self.parmList, self.valueList)
        
        return propertiesModel
        
        
class TreeModel(QtCore.QAbstractItemModel):
    '''
    a model to display a few names, ordered by encabezado
    
    '''
    def __init__(self ,parent=None):
        super(TreeModel, self).__init__(parent)
        self.people = []

    def initProjectView(self):
        """
        Reemplazo del método showtree
        """
        HORIZONTAL_HEADERS = ("Property","Value " )
        HORIZONTAL = ("RAMA :",)
        self.rootItem = TreeItem(None, "ALL", None)
        self.parents = {0 : self.rootItem}
        self.__setupModelData()
    
    def initPUVoltageView(self):
        HORIZONTAL_HEADERS = ("Operation"," Parameter Value " )
        HORIZONTAL = ("RAMA :",)
        self.rootItem = TreeItem(None, "ALL", None)
        self.parents = {0 : self.rootItem}
        self.__setupModelData()
        
    def showProperties(self,headerList, parmList, valueList):
        """
        set2Obje
        """   
        for header, parameter, value in  itertools.izip(headerList, parmList, valueList):     
            person = person_class(header, parameter, value)
            self.people.append(person)
            
        self.rootItem = TreeItem(None, "ALL", None)
        self.parents = {0 : self.rootItem}
        self.__setupModelData()
    
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
    
    def __setupModelData(self):
        for person in self.people:
            if person.value:
                encabezado = person.header
            
            if not self.parents.has_key(encabezado):                
                newparent = TreeItem(None, encabezado, self.rootItem)
                self.rootItem.appendChild(newparent)

                self.parents[encabezado] = newparent

            parentItem = self.parents[encabezado]
            newItem = TreeItem(person, "", parentItem)
            parentItem.appendChild(newItem)

class person_class(object):
    '''
    a trivial custom data object
    '''
    def __init__(self, header, parameter, value):
        self.header = header
        self.parameter = parameter
        self.value = value

    def __repr__(self):
        return "PERSON - %s %s"% (self.parameter, self.header)
    
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
                return QtCore.QVariant(self.person.parameter)
            if column == 1:
                return QtCore.QVariant(self.person.value)
        return QtCore.QVariant()

    def parent(self):
        return self.parentItem
    
    def row(self):
        if self.parentItem:
            return self.parentItem.childItems.index(self)
        return 0
    