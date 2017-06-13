
from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)
    
class Ui_CorrelationTab(object):
    
    def setupUi(self):

        self.tabCorrelation = QtGui.QWidget()
        self.tabCorrelation.setObjectName(_fromUtf8("tabCorrelation"))
        self.gridLayout_13 = QtGui.QGridLayout(self.tabCorrelation)
        self.gridLayout_13.setObjectName(_fromUtf8("gridLayout_13"))
        self.tabWidgetCorrelation = QtGui.QTabWidget(self.tabCorrelation)
        self.tabWidgetCorrelation.setObjectName(_fromUtf8("tabWidgetCorrelation"))
        self.tabopCorrelation = QtGui.QWidget()
        self.tabopCorrelation.setObjectName(_fromUtf8("tabopCorrelation"))
        self.tabWidgetCorrelation.addTab(self.tabopCorrelation, _fromUtf8(""))
        self.tabopCorrelation1 = QtGui.QWidget()
        self.tabopCorrelation1.setObjectName(_fromUtf8("tabopCorrelation1"))
        self.tabWidgetCorrelation.addTab(self.tabopCorrelation1, _fromUtf8(""))
        self.gridLayout_13.addWidget(self.tabWidgetCorrelation, 0, 0, 1, 1)
        
        self.tabWidgetProject.addTab(self.tabCorrelation, _fromUtf8(""))
        
        self.tabWidgetCorrelation.setCurrentIndex(0)
        
    def retranslateUi(self):
        
        self.tabWidgetCorrelation.setTabText(self.tabWidgetCorrelation.indexOf(self.tabopCorrelation), _translate("MainWindow", "Operation", None))
        self.tabWidgetCorrelation.setTabText(self.tabWidgetCorrelation.indexOf(self.tabopCorrelation1), _translate("MainWindow", "Graphics", None))
        self.tabWidgetProject.setTabText(self.tabWidgetProject.indexOf(self.tabCorrelation), _translate("MainWindow", "Correlation", None))
        