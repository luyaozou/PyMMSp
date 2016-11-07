#! encoding = utf-8

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import QObject
from api import general as apigen

class SelInstDialog(QtGui.QDialog):
    '''
        Dialog window for instrument selection.
    '''

    def __init__(self, parent, main):
        QtGui.QDialog.__init__(self, parent)

        self.setMinimumWidth(400)
        self.setMinimumHeight(400)

        refreshButton = QtGui.QPushButton('Refresh')
        acceptButton = QtGui.QPushButton('Ok')

        self.availableInst = QtGui.QLabel()
        instDict, instStr = apigen.list_inst()
        self.availableInst.setText(instStr)

        selInst = QtGui.QWidget()
        selInstLayout = QtGui.QFormLayout()
        self.selSyn = QtGui.QComboBox()
        self.selSyn.addItems(['N.A.'])
        self.selSyn.addItems(list(instDict.keys()))
        self.selLockin = QtGui.QComboBox()
        self.selLockin.addItems(['N.A.'])
        self.selLockin.addItems(list(instDict.keys()))
        self.selScope = QtGui.QComboBox()
        self.selScope.addItems(['N.A.'])
        self.selScope.addItems(list(instDict.keys()))
        self.selMotor = QtGui.QComboBox()
        self.selMotor.addItems(['N.A.'])
        self.selMotor.addItems(list(instDict.keys()))
        selInstLayout.addRow(QtGui.QLabel('Synthesizer'), self.selSyn)
        selInstLayout.addRow(QtGui.QLabel('Lock-in'), self.selLockin)
        selInstLayout.addRow(QtGui.QLabel('Oscilloscope'), self.selScope)
        selInstLayout.addRow(QtGui.QLabel('Step Motor'), self.selMotor)
        selInst.setLayout(selInstLayout)

        # Set main layout
        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(self.availableInst)
        mainLayout.addWidget(selInst)
        mainLayout.addWidget(refreshButton)
        mainLayout.addWidget(acceptButton)

        self.setLayout(mainLayout)

        QObject.connect(refreshButton, QtCore.SIGNAL("clicked()"), self.refresh)
        QObject.connect(acceptButton, QtCore.SIGNAL("clicked()"), self.accept)

    def refresh(self):
        ''' Refresh instrument list '''

        # refresh avaiable instrument list
        self.availableInst = QtGui.QLabel()
        instDict, instStr = apigen.list_inst()
        self.availableInst.setText(instStr)

        # refresh QComboBoxes
        item_count = self.selSyn.count()
        # remove all items but the first one
        for i in range(item_count-1):
            # Because Qt automatically update the index, this loop needs to
            # keep deleting the 'second' item, whose index is 1
            self.selSyn.removeItem(1)
            self.selLockin.removeItem(1)
            self.selScope.removeItem(1)
            self.selMotor.removeItem(1)
        self.selSyn.addItems(list(instDict.keys()))
        self.selLockin.addItems(list(instDict.keys()))
        self.selScope.addItems(list(instDict.keys()))
        self.selMotor.addItems(list(instDict.keys()))

    def accept(self):

        with open('api/inst.cfg', 'w') as f:
            f.write(self.selSyn.currentText() + '\n')
            f.write(self.selLockin.currentText() + '\n')
            f.write(self.selScope.currentText() + '\n')
            f.write(self.selMotor.currentText() + '\n')

        self.close()


class ViewInstDialog(QtGui.QDialog):
    '''
        Dialog window for instrument status view
    '''

    def __init__(self, parent, main):
        QtGui.QDialog.__init__(self, parent)

        self.setMinimumWidth(400)
        self.setMinimumHeight(400)
