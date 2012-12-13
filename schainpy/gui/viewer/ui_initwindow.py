# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\alex\ericworkspace\GUIV1\WelcomeLast.ui'
#
# Created: Thu Dec 13 10:07:01 2012
#      by: PyQt4 UI code generator 4.9.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_InitWindow(object):
    def setupUi(self, form):
        form.setObjectName(_fromUtf8("form"))
        form.resize(622, 516)
        self.centralWidget = QtGui.QWidget(form)
        self.centralWidget.setObjectName(_fromUtf8("centralWidget"))
        self.gridLayout = QtGui.QGridLayout(self.centralWidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label = QtGui.QLabel(self.centralWidget)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Cambria"))
        font.setPointSize(22)
        font.setBold(False)
        font.setWeight(50)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.line = QtGui.QFrame(self.centralWidget)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.verticalLayout.addWidget(self.line)
        self.label_2 = QtGui.QLabel(self.centralWidget)
        self.label_2.setText(_fromUtf8(""))
        self.label_2.setPixmap(QtGui.QPixmap(_fromUtf8("figure/w.jpg")))
        self.label_2.setScaledContents(True)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout.addWidget(self.label_2)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.ExitBtn = QtGui.QPushButton(self.centralWidget)
        self.ExitBtn.setObjectName(_fromUtf8("ExitBtn"))
        self.horizontalLayout.addWidget(self.ExitBtn)
        self.ContinueBtn = QtGui.QPushButton(self.centralWidget)
        self.ContinueBtn.setObjectName(_fromUtf8("ContinueBtn"))
        self.horizontalLayout.addWidget(self.ContinueBtn)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.horizontalLayout_2.addLayout(self.horizontalLayout)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.gridLayout.addLayout(self.verticalLayout_2, 0, 0, 1, 1)
        form.setCentralWidget(self.centralWidget)
        self.statusBar = QtGui.QStatusBar(form)
        self.statusBar.setObjectName(_fromUtf8("statusBar"))
        form.setStatusBar(self.statusBar)

        self.retranslateUi(form)
        QtCore.QMetaObject.connectSlotsByName(form)

    def retranslateUi(self, form):
        form.setWindowTitle(QtGui.QApplication.translate("form", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("form", "Signal Chain - Ver. 1.0", None, QtGui.QApplication.UnicodeUTF8))
        self.ExitBtn.setText(QtGui.QApplication.translate("form", "Exit", None, QtGui.QApplication.UnicodeUTF8))
        self.ContinueBtn.setText(QtGui.QApplication.translate("form", "Continue", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    form = QtGui.QMainWindow()
    ui = Ui_InitWindow()
    ui.setupUi(form)
    form.show()
    sys.exit(app.exec_())

