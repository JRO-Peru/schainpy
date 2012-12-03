# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\alex\ericworkspace\GUIV1\Pantalla.ui'
#
# Created: Tue Aug 28 15:10:06 2012
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
        font.setPointSize(21)
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
        self.label_2.setPixmap(QtGui.QPixmap(_fromUtf8("../../Downloads/IMAGENES/w.jpg")))
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
        self.pushButton_2 = QtGui.QPushButton(self.centralWidget)
        self.pushButton_2.setObjectName(_fromUtf8("pushButton_2"))
        self.horizontalLayout.addWidget(self.pushButton_2)
        self.pushButton = QtGui.QPushButton(self.centralWidget)
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.horizontalLayout.addWidget(self.pushButton)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.horizontalLayout_2.addLayout(self.horizontalLayout)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.gridLayout.addLayout(self.verticalLayout_2, 0, 0, 1, 1)
        form.setCentralWidget(self.centralWidget)
        self.statusBar = QtGui.QStatusBar(form)
        self.statusBar.setObjectName(_fromUtf8("statusBar"))
        form.setStatusBar(self.statusBar)
        self.actionImage = QtGui.QAction(form)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/newPrefix/Imagui/ROJ.jpg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionImage.setIcon(icon)
        self.actionImage.setObjectName(_fromUtf8("actionImage"))
        self.actionOpen = QtGui.QAction(form)
        self.actionOpen.setObjectName(_fromUtf8("actionOpen"))
        self.actionClose = QtGui.QAction(form)
        self.actionClose.setObjectName(_fromUtf8("actionClose"))
        self.actionOpen_2 = QtGui.QAction(form)
        self.actionOpen_2.setObjectName(_fromUtf8("actionOpen_2"))

        self.retranslateUi(form)
        QtCore.QObject.connect(self.pushButton_2, QtCore.SIGNAL(_fromUtf8("clicked()")), form.close)
        QtCore.QObject.connect(self.pushButton, QtCore.SIGNAL(_fromUtf8("clicked()")), form.show)
        QtCore.QMetaObject.connectSlotsByName(form)

    def retranslateUi(self, form):
        form.setWindowTitle(QtGui.QApplication.translate("form", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("form", "Interfaz Grafica -REV. 1.0", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_2.setText(QtGui.QApplication.translate("form", "Exit", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("form", "Continue", None, QtGui.QApplication.UnicodeUTF8))
        self.actionImage.setText(QtGui.QApplication.translate("form", "image", None, QtGui.QApplication.UnicodeUTF8))
        self.actionImage.setToolTip(QtGui.QApplication.translate("form", "show Image", None, QtGui.QApplication.UnicodeUTF8))
        self.actionOpen.setText(QtGui.QApplication.translate("form", "Open", None, QtGui.QApplication.UnicodeUTF8))
        self.actionClose.setText(QtGui.QApplication.translate("form", "Close", None, QtGui.QApplication.UnicodeUTF8))
        self.actionOpen_2.setText(QtGui.QApplication.translate("form", "Open", None, QtGui.QApplication.UnicodeUTF8))

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    form = QtGui.QMainWindow()
    ui = Ui_InitWindow()
    ui.setupUi(form)
    form.show()
    sys.exit(app.exec_())

