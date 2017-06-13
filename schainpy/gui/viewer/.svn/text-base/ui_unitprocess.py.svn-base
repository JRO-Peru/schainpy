# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/alex/ui/unitProcess4.ui'
#
# Created: Fri May 24 05:23:03 2013
#      by: PyQt4 UI code generator 4.10
#
# WARNING! All changes made in this file will be lost!

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

class Ui_UnitProcess(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(312, 195)
        self.centralWidget = QtGui.QWidget(MainWindow)
        self.centralWidget.setObjectName(_fromUtf8("centralWidget"))
        self.gridLayout = QtGui.QGridLayout(self.centralWidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.inputLabel = QtGui.QLabel(self.centralWidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)
        self.inputLabel.setFont(font)
        self.inputLabel.setObjectName(_fromUtf8("inputLabel"))
        self.gridLayout.addWidget(self.inputLabel, 2, 0, 1, 1)
        self.unitPcancelbut = QtGui.QPushButton(self.centralWidget)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.unitPcancelbut.setFont(font)
        self.unitPcancelbut.setObjectName(_fromUtf8("unitPcancelbut"))
        self.gridLayout.addWidget(self.unitPcancelbut, 5, 2, 1, 2)
        self.unitPokbut = QtGui.QPushButton(self.centralWidget)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.unitPokbut.setFont(font)
        self.unitPokbut.setObjectName(_fromUtf8("unitPokbut"))
        self.gridLayout.addWidget(self.unitPokbut, 5, 0, 1, 2)
        self.typeLabel = QtGui.QLabel(self.centralWidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)
        self.typeLabel.setFont(font)
        self.typeLabel.setObjectName(_fromUtf8("typeLabel"))
        self.gridLayout.addWidget(self.typeLabel, 3, 0, 1, 1)
        self.nameUP = QtGui.QLabel(self.centralWidget)
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(False)
        font.setWeight(50)
        self.nameUP.setFont(font)
        self.nameUP.setObjectName(_fromUtf8("nameUP"))
        self.gridLayout.addWidget(self.nameUP, 0, 1, 1, 2)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 3, 1, 1)
        self.comboInputBox = QtGui.QComboBox(self.centralWidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.comboInputBox.setFont(font)
        self.comboInputBox.setObjectName(_fromUtf8("comboInputBox"))
        self.gridLayout.addWidget(self.comboInputBox, 2, 1, 1, 3)
        self.comboTypeBox = QtGui.QComboBox(self.centralWidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.comboTypeBox.setFont(font)
        self.comboTypeBox.setObjectName(_fromUtf8("comboTypeBox"))
        self.comboTypeBox.addItem(_fromUtf8(""))
        self.comboTypeBox.addItem(_fromUtf8(""))
        self.comboTypeBox.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.comboTypeBox, 3, 1, 1, 3)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 0, 0, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem2, 4, 0, 1, 1)
        self.line = QtGui.QFrame(self.centralWidget)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.gridLayout.addWidget(self.line, 1, 0, 1, 4)
        MainWindow.setCentralWidget(self.centralWidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.inputLabel.setText(_translate("MainWindow", "Input:", None))
        self.unitPcancelbut.setText(_translate("MainWindow", "Cancel", None))
        self.unitPokbut.setText(_translate("MainWindow", "Ok", None))
        self.typeLabel.setText(_translate("MainWindow", "Type:", None))
        self.nameUP.setText(_translate("MainWindow", "Processing Unit", None))
        self.comboTypeBox.setItemText(0, _translate("MainWindow", "Voltage", None))
        self.comboTypeBox.setItemText(1, _translate("MainWindow", "Spectra", None))
        self.comboTypeBox.setItemText(2, _translate("MainWindow", "Correlation", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()
    ui = Ui_UnitProcess()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

