#! encoding = utf-8
''' Dialog windows for system menues '''


from PyQt4 import QtGui, QtCore
from api import general as apigen
from gui import SharedWidgets as Shared


class SelInstDialog(QtGui.QDialog):
    '''
        Dialog window for instrument selection.
    '''

    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.parent = parent
        self.setMinimumWidth(400)
        self.setMinimumHeight(400)

        refreshButton = QtGui.QPushButton('Refresh')
        acceptButton = QtGui.QPushButton('Ok')
        cancelButton = QtGui.QPushButton('Cancel')

        self.availableInst = QtGui.QLabel()
        instList, instStr = apigen.list_inst()
        self.availableInst.setText(instStr)

        selInst = QtGui.QWidget()
        selInstLayout = QtGui.QFormLayout()
        self.selSyn = QtGui.QComboBox()
        self.selSyn.addItems(['N.A.'])
        self.selSyn.addItems(instList)
        self.selLockin = QtGui.QComboBox()
        self.selLockin.addItems(['N.A.'])
        self.selLockin.addItems(instList)
        self.selScope = QtGui.QComboBox()
        self.selScope.addItems(['N.A.'])
        self.selScope.addItems(instList)
        self.selMotor = QtGui.QComboBox()
        self.selMotor.addItems(['N.A.'])
        self.selMotor.addItems(instList)
        selInstLayout.addRow(QtGui.QLabel('Synthesizer'), self.selSyn)
        selInstLayout.addRow(QtGui.QLabel('Lock-in'), self.selLockin)
        selInstLayout.addRow(QtGui.QLabel('Oscilloscope'), self.selScope)
        selInstLayout.addRow(QtGui.QLabel('Step Motor'), self.selMotor)
        selInst.setLayout(selInstLayout)

        # Set main layout
        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(QtGui.QLabel('Reselecting instrument will reset instrument settings to default values.'))
        mainLayout.addWidget(self.availableInst)
        mainLayout.addWidget(refreshButton)
        mainLayout.addWidget(selInst)
        mainLayout.addWidget(cancelButton)
        mainLayout.addWidget(acceptButton)

        self.setLayout(mainLayout)

        refreshButton.clicked.connect(self.refresh)
        cancelButton.clicked.connect(self.reject)
        acceptButton.clicked.connect(self.accept)

    def refresh(self):
        ''' Refresh instrument list '''

        # refresh avaiable instrument list
        instList, instStr = apigen.list_inst()
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
        self.selSyn.addItems(instList)
        self.selLockin.addItems(instList)
        self.selScope.addItems(instList)
        self.selMotor.addItems(instList)

    def accept(self):

        # close old instrument handles
        apigen.close_inst(self.parent.synHandle,
                          self.parent.lcHandle,
                          self.parent.pciHandle,
                          self.parent.motorHandle)

        # open new instrument handles
        self.parent.synHandle = apigen.open_inst(self.selSyn.currentText())
        self.parent.lcHandle = apigen.open_inst(self.selLockin.currentText())
        self.parent.pciHandle = apigen.open_inst(self.selScope.currentText())
        self.parent.motorHandle = apigen.open_inst(self.selMotor.currentText())

        self.done(True)


class ViewInstDialog(QtGui.QDialog):
    '''
        Dialog window for instrument status view
    '''

    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)

        self.setMinimumWidth(400)
        self.setMinimumHeight(400)


class CloseSelInstDialog(QtGui.QDialog):
    '''
        Dialog window for closing selected instrument.
    '''

    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.parent = parent
        self.setMinimumWidth(400)
        self.setMinimumHeight(400)

        inst = QtGui.QWidget()
        self.synToggle = QtGui.QCheckBox()
        self.lcToggle = QtGui.QCheckBox()
        self.pciToggle = QtGui.QCheckBox()
        self.motorToggle = QtGui.QCheckBox()

        instLayout = QtGui.QFormLayout()
        instLayout.addRow(QtGui.QLabel('Instrument'), QtGui.QLabel('Status'))
        # only list currently connected instruments
        if self.parent.synHandle:
            self.synToggle.setCheckState(True)
            instLayout.addRow(QtGui.QLabel('Synthesizer'), self.synToggle)
        else:
            self.synToggle.setCheckState(False)

        if self.parent.lcHandle:
            self.lcToggle.setCheckState(True)
            instLayout.addRow(QtGui.QLabel('Lockin'), self.lcToggle)
        else:
            self.lcToggle.setCheckState(False)

        if self.parent.pciHandle:
            self.pciToggle.setCheckState(True)
            instLayout.addRow(QtGui.QLabel('Oscilloscope'), self.pciToggle)
        else:
            self.pciToggle.setCheckState(False)

        if self.parent.motorHandle:
            self.motorToggle.setCheckState(True)
            instLayout.addRow(QtGui.QLabel('Motor'), self.motorToggle)
        else:
            self.motorToggle.setCheckState(False)

        inst.setLayout(instLayout)

        okButton = QtGui.QPushButton(Shared.btn_label('complete'))
        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(inst)
        mainLayout.addWidget(okButton)
        self.setLayout(mainLayout)

        okButton.clicked.connect(self.accept)

    def accept(self):

        self.close_syn(self.synToggle.isChecked())
        self.close_lc(self.lcToggle.isChecked())
        self.close_scope(self.pciToggle.isChecked())
        self.close_motor(self.motorToggle.isChecked())

        self.close()

    def close_syn(self, check_state):

        if (not check_state) and self.parent.synHandle:
            apigen.close_inst(self.parent.synHandle)
            self.parent.synHandle = None
        else:
            pass

    def close_lc(self, check_state):

        if (not check_state) and self.parent.lcHandle:
            apigen.close_inst(self.parent.lcHandle)
            self.parent.lcHandle = None
        else:
            pass

    def close_scope(self, check_state):

        if (not check_state) and self.parent.pciHandle:
            apigen.close_inst(self.parent.pciHandle)
            self.parent.pciHandle = None
        else:
            pass


    def close_motor(self, check_state):

        if (not check_state) and self.parent.motorHandle:
            apigen.close_inst(self.parent.motorHandle)
            self.parent.motorHandle = None
        else:
            pass
