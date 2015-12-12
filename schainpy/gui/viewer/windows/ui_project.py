
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
    
class Ui_ProjectTab(object):
    
    def setupUi(self):
        
        self.tabProject = QtGui.QWidget()
        self.tabProject.setObjectName(_fromUtf8("tabProject"))
        self.gridLayout_15 = QtGui.QGridLayout(self.tabProject)
        self.gridLayout_15.setObjectName(_fromUtf8("gridLayout_15"))
        
        self.frame = QtGui.QFrame(self.tabProject)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName(_fromUtf8("frame"))
        
        self.gridLayout_2 = QtGui.QGridLayout(self.frame)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        
        self.label = QtGui.QLabel(self.frame)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)
        
        self.proName = QtGui.QLineEdit(self.frame)
        self.proName.setObjectName(_fromUtf8("proName"))
        self.gridLayout_2.addWidget(self.proName, 0, 1, 1, 8)
        
        self.labDatatype = QtGui.QLabel(self.frame)
        self.labDatatype.setObjectName(_fromUtf8("labDatatype"))
        self.gridLayout_2.addWidget(self.labDatatype, 1, 0, 1, 1)
        
        self.proComDataType = QtGui.QComboBox(self.frame)
        self.proComDataType.setObjectName(_fromUtf8("proComDataType"))
        self.proComDataType.addItem(_fromUtf8(""))
        self.proComDataType.addItem(_fromUtf8(""))
        self.proComDataType.addItem(_fromUtf8(""))
        self.proComDataType.addItem(_fromUtf8(""))
        self.gridLayout_2.addWidget(self.proComDataType, 1, 1, 1, 6)
        
        self.proDataType = QtGui.QLineEdit(self.frame)
        self.proDataType.setObjectName(_fromUtf8("proDataType"))
        self.gridLayout_2.addWidget(self.proDataType, 1, 7, 1, 2)
        
        self.labDatapath = QtGui.QLabel(self.frame)
        self.labDatapath.setObjectName(_fromUtf8("labDatapath"))
        self.gridLayout_2.addWidget(self.labDatapath, 2, 0, 1, 1)
        
        self.proToolPath = QtGui.QToolButton(self.frame)
        self.proToolPath.setObjectName(_fromUtf8("proToolPath"))
        self.gridLayout_2.addWidget(self.proToolPath, 2, 1, 1, 1)
        
        self.proDataPath = QtGui.QLineEdit(self.frame)
        self.proDataPath.setObjectName(_fromUtf8("proDataPath"))
        self.gridLayout_2.addWidget(self.proDataPath, 2, 2, 1, 7)

        self.labelWalk = QtGui.QLabel(self.frame)
        self.labelWalk.setObjectName(_fromUtf8("labelWalk"))
        self.gridLayout_2.addWidget(self.labelWalk, 3, 0, 1, 1)
        
        self.proComWalk = QtGui.QComboBox(self.frame)
        self.proComWalk.setObjectName(_fromUtf8("proComWalk"))
        self.proComWalk.addItem(_fromUtf8(""))
        self.proComWalk.addItem(_fromUtf8(""))
        self.gridLayout_2.addWidget(self.proComWalk, 3, 1, 1, 4)
        
        self.labExpLabel = QtGui.QLabel(self.frame)
        self.labExpLabel.setObjectName(_fromUtf8("labExpLabel"))
        self.gridLayout_2.addWidget(self.labExpLabel, 3, 5, 1, 1)
        
        self.proExpLabel = QtGui.QLineEdit(self.frame)
        self.proExpLabel.setObjectName(_fromUtf8("proExpLabel"))
        self.gridLayout_2.addWidget(self.proExpLabel, 3, 6, 1, 1)
        
        self.labReadMode = QtGui.QLabel(self.frame)
        self.labReadMode.setObjectName(_fromUtf8("labReadMode"))
        self.gridLayout_2.addWidget(self.labReadMode, 4, 0, 1, 1)
        
        self.proComReadMode = QtGui.QComboBox(self.frame)
        self.proComReadMode.setObjectName(_fromUtf8("proComReadMode"))
        self.proComReadMode.addItem(_fromUtf8(""))
        self.proComReadMode.addItem(_fromUtf8(""))
        self.gridLayout_2.addWidget(self.proComReadMode, 4, 1, 1, 4)
        
        self.labDelay = QtGui.QLabel(self.frame)
        self.labDelay.setObjectName(_fromUtf8("labDelay"))
        self.gridLayout_2.addWidget(self.labDelay, 4, 5, 1, 1)
        
        self.proDelay = QtGui.QLineEdit(self.frame)
        self.proDelay.setObjectName(_fromUtf8("proDelay"))
        self.gridLayout_2.addWidget(self.proDelay, 4, 6, 1, 1)
        
        self.labelSet = QtGui.QLabel(self.frame)
        self.labelSet.setObjectName(_fromUtf8("labelSet"))
        self.gridLayout_2.addWidget(self.labelSet, 4, 7, 1, 1)
        
        self.proSet = QtGui.QLineEdit(self.frame)
        self.proSet.setObjectName(_fromUtf8("proSet"))
        self.gridLayout_2.addWidget(self.proSet, 4, 8, 1, 1)
        

        self.proLoadButton = QtGui.QPushButton(self.frame)
        self.proLoadButton.setObjectName(_fromUtf8("proLoadButton"))
        self.gridLayout_2.addWidget(self.proLoadButton, 5, 0, 1, 9)
        
        self.frame_data = QtGui.QFrame(self.tabProject)
        self.frame_data.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame_data.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_data.setObjectName(_fromUtf8("frame_data"))
          
        self.gridLayout_data = QtGui.QGridLayout(self.frame_data)
        self.gridLayout_data.setObjectName(_fromUtf8("gridLayout_data"))
        
        self.labelIPPKm = QtGui.QLabel(self.frame_data)
        self.labelIPPKm.setObjectName(_fromUtf8("labelIPPKm"))
        self.gridLayout_data.addWidget(self.labelIPPKm, 6, 0, 1, 1)
        
        self.proIPPKm = QtGui.QLineEdit(self.frame_data)
        self.proIPPKm.setObjectName(_fromUtf8("proIPPKm"))
        self.gridLayout_data.addWidget(self.proIPPKm, 6, 1, 1, 6)

        self.labnTxs = QtGui.QLabel(self.frame_data)
        self.labnTxs.setObjectName(_fromUtf8("labnTxs"))
        self.gridLayout_data.addWidget(self.labnTxs, 6, 0, 1, 1)
        
        self.pronTxs = QtGui.QLineEdit(self.frame_data)
        self.pronTxs.setObjectName(_fromUtf8("pronTxs"))
        self.gridLayout_data.addWidget(self.pronTxs, 6, 1, 1, 6)
        
        self.labByBlock = QtGui.QLabel(self.frame_data)
        self.labByBlock.setObjectName(_fromUtf8("labByBlock"))
        self.gridLayout_data.addWidget(self.labByBlock, 6, 7, 1, 1)
        
        self.proComByBlock = QtGui.QComboBox(self.frame_data)
        self.proComByBlock.setObjectName(_fromUtf8("proComByBlock"))
        self.proComByBlock.addItem(_fromUtf8(""))
        self.proComByBlock.addItem(_fromUtf8(""))
        self.gridLayout_data.addWidget(self.proComByBlock, 6, 8, 1, 1)
        
        
        self.frame_2 = QtGui.QFrame(self.tabProject)
        self.frame_2.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_2.setObjectName(_fromUtf8("frame_2"))
        
        self.gridLayout_10 = QtGui.QGridLayout(self.frame_2)
        self.gridLayout_10.setObjectName(_fromUtf8("gridLayout_10"))
        
        self.label_27 = QtGui.QLabel(self.frame_2)
        self.label_27.setObjectName(_fromUtf8("label_27"))
        self.gridLayout_10.addWidget(self.label_27, 0, 0, 1, 1)
        self.proComStartDate = QtGui.QComboBox(self.frame_2)
        self.proComStartDate.setObjectName(_fromUtf8("proComStartDate"))
        self.gridLayout_10.addWidget(self.proComStartDate, 0, 1, 1, 1)
        self.label_28 = QtGui.QLabel(self.frame_2)
        self.label_28.setObjectName(_fromUtf8("label_28"))
        self.gridLayout_10.addWidget(self.label_28, 1, 0, 1, 1)
        self.proComEndDate = QtGui.QComboBox(self.frame_2)
        self.proComEndDate.setObjectName(_fromUtf8("proComEndDate"))
        self.gridLayout_10.addWidget(self.proComEndDate, 1, 1, 1, 1)
        self.label_2 = QtGui.QLabel(self.frame_2)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout_10.addWidget(self.label_2, 2, 0, 1, 1)
        self.proStartTime = QtGui.QTimeEdit(self.frame_2)
        self.proStartTime.setObjectName(_fromUtf8("proStartTime"))
        self.gridLayout_10.addWidget(self.proStartTime, 2, 1, 1, 1)
        self.label_3 = QtGui.QLabel(self.frame_2)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout_10.addWidget(self.label_3, 3, 0, 1, 1)
        self.proEndTime = QtGui.QTimeEdit(self.frame_2)
        self.proEndTime.setObjectName(_fromUtf8("proEndTime"))
        self.gridLayout_10.addWidget(self.proEndTime, 3, 1, 1, 1)
        self.label_30 = QtGui.QLabel(self.frame_2)
        self.label_30.setObjectName(_fromUtf8("label_30"))
        self.gridLayout_10.addWidget(self.label_30, 4, 0, 1, 1)
        self.proDescription = QtGui.QTextEdit(self.frame_2)
        self.proDescription.setObjectName(_fromUtf8("proDescription"))
        self.gridLayout_10.addWidget(self.proDescription, 4, 1, 1, 1)
        
        self.frame_3 = QtGui.QFrame(self.tabProject)
        self.frame_3.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_3.setObjectName(_fromUtf8("frame_3"))
        self.gridLayout_14 = QtGui.QGridLayout(self.frame_3)
        self.gridLayout_14.setObjectName(_fromUtf8("gridLayout_14"))
        self.proOk = QtGui.QPushButton(self.frame_3)
        self.proOk.setObjectName(_fromUtf8("proOk"))
        self.gridLayout_14.addWidget(self.proOk, 0, 0, 1, 1)
        self.proClear = QtGui.QPushButton(self.frame_3)
        self.proClear.setObjectName(_fromUtf8("proClear"))
        self.gridLayout_14.addWidget(self.proClear, 0, 1, 1, 1)
        
        self.gridLayout_15.addWidget(self.frame, 0, 0, 8, 1)
        self.gridLayout_15.addWidget(self.frame_data, 8, 0, 2, 1)
        self.gridLayout_15.addWidget(self.frame_2, 10, 0, 7, 1)
        self.gridLayout_15.addWidget(self.frame_3, 17, 0, 2, 1)
        
        self.tabWidgetProject.addTab(self.tabProject, _fromUtf8(""))
        
    def retranslateUi(self):
        
        self.label.setText(_translate("MainWindow", "Project Name :", None))
        self.labDatatype.setText(_translate("MainWindow", "Data type :", None))
        self.proComDataType.setItemText(0, _translate("MainWindow", "Voltage", None))
        self.proComDataType.setItemText(1, _translate("MainWindow", "Spectra", None))
        self.proComDataType.setItemText(2, _translate("MainWindow", "Fits", None))
        self.proComDataType.setItemText(3, _translate("MainWindow", "USRP", None))
        self.labDatapath.setText(_translate("MainWindow", "Data path :", None))
        self.proToolPath.setText(_translate("MainWindow", "...", None))
        self.labReadMode.setText(_translate("MainWindow", "Read mode:", None))
        self.proComReadMode.setItemText(0, _translate("MainWindow", "Offline", None))
        self.proComReadMode.setItemText(1, _translate("MainWindow", "Online", None))
        self.labDelay.setText(_translate("MainWindow", "Delay:", None))
        self.labExpLabel.setText(_translate("MainWindow", "Exp. Label:", None))
        self.labelWalk.setText(_translate("MainWindow", "Search data :", None))
        self.proComWalk.setItemText(0, _translate("MainWindow", "On files", None))
        self.proComWalk.setItemText(1, _translate("MainWindow", "On sub-folders", None))
        self.proComByBlock.setItemText(0, _translate("MainWindow", "By profile", None))
        self.proComByBlock.setItemText(1, _translate("MainWindow", "By block", None))
        self.labByBlock.setText(_translate("MainWindow", "Get data:", None))
        
        
        self.proLoadButton.setText(_translate("MainWindow", "Load", None))
        self.labelSet.setText(_translate("MainWindow", "File set:", None))
        self.labelIPPKm.setText(_translate("MainWindow", "IPP (km):", None))
        self.labnTxs.setText(_translate("MainWindow", "Number of Txs:", None))
        
        self.label_27.setText(_translate("MainWindow", "Star Date:", None))
        self.label_28.setText(_translate("MainWindow", "End Date:", None))
        self.label_2.setText(_translate("MainWindow", "Start Time:", None))
        self.label_3.setText(_translate("MainWindow", "End Time:", None))
        self.label_30.setText(_translate("MainWindow", "Description:", None))
        self.proOk.setText(_translate("MainWindow", "Ok", None))
        self.proClear.setText(_translate("MainWindow", "Clear", None))   

        self.tabWidgetProject.setTabText(self.tabWidgetProject.indexOf(self.tabProject), _translate("MainWindow", "Project", None))
    
        self.__setToolTip()
        
    def __setToolTip(self):
        
        self.proComWalk.setToolTip('<b>On Files</b>:<i>Search file in format .r or pdata</i> <b>On Folders</b>:<i>Search file in a directory DYYYYDOY</i>')
        