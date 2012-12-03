from PyQt4 import QtCore

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
    