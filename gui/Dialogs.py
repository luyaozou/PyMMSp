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
        mainLayout.addWidget(self.availableInst)
        mainLayout.addWidget(selInst)
        mainLayout.addWidget(refreshButton)
        mainLayout.addWidget(acceptButton)

        self.setLayout(mainLayout)

        refreshButton.clicked.connect(self.refresh)
        acceptButton.clicked.connect(self.accept)

    def refresh(self):
        ''' Refresh instrument list '''

        # refresh avaiable instrument list
        self.availableInst = QtGui.QLabel()
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

        self.close()


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
        synToggle = QtGui.QCheckBox()
        lcToggle = QtGui.QCheckBox()
        pciToggle = QtGui.QCheckBox()
        motorToggle = QtGui.QCheckBox()

        instLayout = QtGui.QFormLayout()
        instLayout.addRow(QtGui.QLabel('Instrument'), QtGui.QLabel('Status'))
        # only list currently connected instruments
        if self.parent.synHandle:
            synToggle.setCheckState(True)
            instLayout.addRow(QtGui.QLabel('Synthesizer'), synToggle)
        else:
            pass
        if self.parent.lcHandle:
            lcToggle.setCheckState(True)
            instLayout.addRow(QtGui.QLabel('Lockin'), lcToggle)
        else:
            pass
        if self.parent.pciHandle:
            pciToggle.setCheckState(True)
            instLayout.addRow(QtGui.QLabel('Oscilloscope'), pciToggle)
        else:
            pass
        if self.parent.motorHandle:
            motorToggle.setCheckState(True)
            instLayout.addRow(QtGui.QLabel('Motor'), motorToggle)
        else:
            pass
        inst.setLayout(instLayout)

        okButton = QtGui.QPushButton(Shared.btn_label('complete'))
        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(inst)
        mainLayout.addWidget(okButton)
        self.setLayout(mainLayout)

        synToggle.clicked["bool"].connect(self.close_syn)
        lcToggle.clicked["bool"].connect(self.close_lc)
        pciToggle.clicked["bool"].connect(self.close_scope)
        motorToggle.clicked["bool"].connect(self.close_motor)
        okButton.clicked.connect(self.accept)

    def close_syn(self, check_state):
        if check_state:
            pass
        else:
            status = apigen.close_inst(self.parent.synHandle)
            self.parent.synHandle = None

    def close_lc(self, check_state):
        if check_state:
            pass
        else:
            status = apigen.close_inst(self.parent.lcHandle)
            self.parent.lcHandle = None

    def close_scope(self, check_state):
        if check_state:
            pass
        else:
            status = apigen.close_inst(self.parent.pciHandle)
            self.parent.pciHandle = None

    def close_motor(self, check_state):
        if check_state:
            pass
        else:
            status = apigen.close_inst(self.parent.motorHandle)
            self.parent.motorHandle = None
