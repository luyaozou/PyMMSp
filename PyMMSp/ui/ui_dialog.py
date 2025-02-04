#! encoding = utf-8
""" Dialog windows for system menus """


from PyQt6 import QtGui, QtCore, QtWidgets
from PyMMSp.inst.base import CONNECTION_TYPES
from PyMMSp.inst import flow as api_flow
from PyMMSp.libs import lwa
from PyMMSp.ui import ui_shared
from pyqtgraph import siFormat
import pyqtgraph as pg


class DialogConfigIndvInst(QtWidgets.QDialog):
    """ Configure an individual instrument """

    def __init__(self, parent=None):
        super().__init__(parent)

        thisLayout = QtWidgets.QFormLayout()
        self.comboConnectionType = QtWidgets.QComboBox()
        self.comboConnectionType.addItems(list(CONNECTION_TYPES))
        self.editInstAddr = QtWidgets.QLineEdit()
        self.comboInstModel = QtWidgets.QComboBox()
        self.btnAccept = QtWidgets.QPushButton('Ok')
        self.btnCancel = QtWidgets.QPushButton('Cancel')
        thisLayout.addRow(QtWidgets.QLabel('Connection Type'), self.comboConnectionType)
        thisLayout.addRow(QtWidgets.QLabel('Address'), self.editInstAddr)
        thisLayout.addRow(QtWidgets.QLabel('Model'), self.comboInstModel)
        thisLayout.addRow(self.btnCancel, self.btnAccept)
        self.setLayout(thisLayout)

        self.btnAccept.clicked.connect(self.accept)
        self.btnCancel.clicked.connect(self.reject)

        # set input mask according to coonection type
        self.comboConnectionType.currentTextChanged.connect(self.set_input_mask)
        # initialize input mask
        self.set_input_mask(self.comboConnectionType.currentText())

    def set_input_mask(self, text):
        if text == 'GPIB VISA':
            self.editInstAddr.setInputMask("GPIB0::000;_::000;_::INSTR")
        elif text == 'COM':
            self.editInstAddr.setInputMask('COM0;0')
        elif text == 'Ethernet':
            self.editInstAddr.setInputMask('000.000.000.000:_')


class DialogConnInst(QtWidgets.QDialog):
    """ Dialog window for instrument selection. """

    def __init__(self, parent=None): 
        super().__init__(parent)
        self.setMinimumWidth(400)
        self.setMinimumHeight(400)
        self.setWindowTitle('Select Instrument')
        self.dIndvInst = DialogConfigIndvInst(self)

        refreshButton = QtWidgets.QPushButton('Refresh Available Instrument List')
        acceptButton = QtWidgets.QPushButton(ui_shared.btn_label('confirm'))
        cancelButton = QtWidgets.QPushButton(ui_shared.btn_label('reject'))

        self.gpBtnInst = QtWidgets.QGroupBox('Select Instrument')

        self.btnSyn = QtWidgets.QPushButton('Synthesizer')
        self.btnLockin = QtWidgets.QPushButton('Lock-in')
        self.btnAWG = QtWidgets.QPushButton('AWG')
        self.btnOscillo = QtWidgets.QPushButton('Oscilloscope')
        self.btnUCA = QtWidgets.QPushButton('UCA Power Supply')
        self.btnFlow = QtWidgets.QPushButton('Flow Controller')
        self.btnGauge1 = QtWidgets.QPushButton('Gauge1')
        self.btnGauge2 = QtWidgets.QPushButton('Gauge2')

        btnInstLayout = QtWidgets.QGridLayout()
        btnInstLayout.addWidget(self.btnSyn, 0, 0)
        btnInstLayout.addWidget(self.btnLockin, 0, 1)
        btnInstLayout.addWidget(self.btnAWG, 1, 0)
        btnInstLayout.addWidget(self.btnOscillo, 1, 1)
        btnInstLayout.addWidget(self.btnUCA, 2, 0)
        btnInstLayout.addWidget(self.btnFlow, 2, 1)
        btnInstLayout.addWidget(self.btnGauge1, 3, 0)
        btnInstLayout.addWidget(self.btnGauge2, 3, 1)
        self.gpBtnInst.setLayout(btnInstLayout)

        self.lblConnSyn = QtWidgets.QLabel('N.A')
        self.statusSyn = ui_shared.CommStatusBulb(-1)
        self.lblConnLockin = QtWidgets.QLabel('N.A')
        self.statusLockin = ui_shared.CommStatusBulb(-1)
        self.lblConnAWG = QtWidgets.QLabel('N.A')
        self.statusAWG = ui_shared.CommStatusBulb(-1)
        self.lblConnScope = QtWidgets.QLabel('N.A')
        self.statusScope = ui_shared.CommStatusBulb(-1)
        self.lblConnUCA = QtWidgets.QLabel('N.A')
        self.statusUCA = ui_shared.CommStatusBulb(-1)
        self.lblConnFlow = QtWidgets.QLabel('N.A')
        self.statusFlow = ui_shared.CommStatusBulb(-1)
        self.lblConnGauge1 = QtWidgets.QLabel('N.A')
        self.statusGauge1 = ui_shared.CommStatusBulb(-1)
        self.lblConnGauge2 = QtWidgets.QLabel('N.A')
        self.statusGauge2 = ui_shared.CommStatusBulb(-1)

        instListLayout = QtWidgets.QGridLayout()
        instListLayout.addWidget(QtWidgets.QLabel('Instrument'), 0, 0)
        instListLayout.addWidget(QtWidgets.QLabel('Connection'), 0, 1)
        instListLayout.addWidget(QtWidgets.QLabel('Status'), 0, 2)

        instListLayout.addWidget(QtWidgets.QLabel('Synthesizer'), 1, 0)
        instListLayout.addWidget(self.lblConnSyn, 1, 1)
        instListLayout.addWidget(self.statusSyn, 1, 2)
        instListLayout.addWidget(QtWidgets.QLabel('Lock-in'), 2, 0)
        instListLayout.addWidget(self.lblConnLockin, 2, 1)
        instListLayout.addWidget(self.statusLockin, 2, 2)
        instListLayout.addWidget(QtWidgets.QLabel('AWG'), 3, 0)
        instListLayout.addWidget(self.lblConnAWG, 3, 1)
        instListLayout.addWidget(self.statusAWG, 3, 2)
        instListLayout.addWidget(QtWidgets.QLabel('Oscilloscope'), 4, 0)
        instListLayout.addWidget(self.lblConnScope, 4, 1)
        instListLayout.addWidget(self.statusScope, 4, 2)
        instListLayout.addWidget(QtWidgets.QLabel('UCA Power Supply'), 5, 0)
        instListLayout.addWidget(self.lblConnUCA, 5, 1)
        instListLayout.addWidget(self.statusUCA, 5, 2)
        instListLayout.addWidget(QtWidgets.QLabel('Flow Meter'), 6, 0)
        instListLayout.addWidget(self.lblConnFlow, 6, 1)
        instListLayout.addWidget(self.statusFlow, 6, 2)
        instListLayout.addWidget(QtWidgets.QLabel('Gauge1'), 7, 0)
        instListLayout.addWidget(self.lblConnGauge1, 7, 1)
        instListLayout.addWidget(self.statusGauge1, 7, 2)
        instListLayout.addWidget(QtWidgets.QLabel('Gauge2'), 8, 0)
        instListLayout.addWidget(self.lblConnGauge2, 8, 1)
        instListLayout.addWidget(self.statusGauge2, 8, 2)

        btnLayout = QtWidgets.QHBoxLayout()
        btnLayout.addWidget(cancelButton)
        btnLayout.addWidget(acceptButton)
        btnLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)

        thisLayout = QtWidgets.QVBoxLayout()
        thisLayout.addWidget(self.gpBtnInst)
        thisLayout.addLayout(instListLayout)
        thisLayout.addLayout(btnLayout)
        self.setLayout(thisLayout)

        cancelButton.clicked.connect(self.reject)
        acceptButton.clicked.connect(self.accept)


class DialogOscillo(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle('Configure Oscilloscope')

        btnLayout = QtWidgets.QHBoxLayout()
        btnLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.btnOk = QtWidgets.QPushButton('OK')
        btnLayout.addWidget(self.btnOk)

        thisLayout = QtWidgets.QVBoxLayout()
        thisLayout.addLayout(btnLayout)
        self.setLayout(thisLayout)

        self.btnOk.clicked.connect(self.accept)


class DialogFlow(QtWidgets.QDialog):
    """ Dialog window to configure MKS flow controller """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle('Configure MKS Flow Controller')
        self.setMinimumWidth(1350)
        self.setWindowFlags(QtCore.Qt.WindowType.Window)

        self.lblScreenSavor = QtWidgets.QLabel()
        self.lblMsg = QtWidgets.QLabel()
        self.inpScreenSavor = ui_shared.create_int_spin_box(0, minimum=0, maximum=240)
        self.btnScreenSavor = QtWidgets.QPushButton('Commit')
        self.btnRefresh = QtWidgets.QPushButton('Refresh All Setting')
        self.btnGCF = QtWidgets.QPushButton('Scale Factor Calculator')
        box1 = QtWidgets.QGroupBox()
        box1.setTitle('General Setting')
        box1Layout = QtWidgets.QGridLayout()
        box1Layout.addWidget(QtWidgets.QLabel('Current Setting'), 0, 1)
        box1Layout.addWidget(QtWidgets.QLabel('New Setting'), 0, 2)
        box1Layout.addWidget(QtWidgets.QLabel('Screen Savor'), 1, 0)
        box1Layout.addWidget(self.lblScreenSavor, 1, 1)
        box1Layout.addWidget(self.inpScreenSavor, 1, 2)
        box1Layout.addWidget(self.btnScreenSavor, 1, 3)
        box1Layout.addWidget(self.btnGCF, 2, 0)
        box1Layout.addWidget(self.lblMsg, 2, 1, 1, 2)
        box1Layout.addWidget(self.btnRefresh, 2, 3)
        box1.setLayout(box1Layout)

        self.boxChn1 = _MKSChannel(1, parent=self)
        self.boxChn2 = _MKSChannel(2, parent=self)

        thisLayout = QtWidgets.QVBoxLayout()
        thisLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        thisLayout.addWidget(box1)
        thisLayout.addWidget(self.boxChn1)
        thisLayout.addWidget(self.boxChn2)
        self.setLayout(thisLayout)
        self.adjustSize()

        self.btnGroup = QtWidgets.QButtonGroup()
        self.btnGroup.addButton(self.btnScreenSavor, 0)
        self._btnMap = (
            ('SST', '{:d}', 'int', self.lblScreenSavor, self.inpScreenSavor),
        )

    def update_flow_reading(self, tuple_flow):
        for chn, f in zip([self.boxChn1, self.boxChn2], tuple_flow):
            try:
                chn.lblFlow.setText('{:.2f}'.format(float(f)))
            except ValueError:
                chn.lblFlow.setText(f)

    def mks_cmd(self, btn_id):
        """ Get the MKS command associated with btn_id """
        cmd, pfmt, dtype, lbl, cfg = self._btnMap[btn_id]
        # get setted value
        if dtype in ['int', 'float']:
            param = pfmt.format(cfg.value())
        elif dtype == 'str':
            if isinstance(cfg, QtWidgets.QLabel):
                param = pfmt.format(cfg.text())
            else:
                param = pfmt.format(cfg.currentText())
        else:
            raise ValueError
        return cmd, param

    def update_current(self, btn_id, ans):
        """ Update the MKS setting value associated with btn_id """
        cmd, pfmt, dtype, lbl, cfg = self._btnMap[btn_id]
        # write new value to current value label
        lbl.setText(ans)

    def yield_all(self):
        """ yield all command & label corresponding to the button group buttons """
        for btn_tuple in self._btnMap:
            cmd, pfmt, dtype, lbl, cfg = btn_tuple
            yield cmd, lbl


class _MKSChannel(QtWidgets.QGroupBox):
    """ Subclass to configure MKS channel setting """

    def __init__(self, chn, parent=None):
        super().__init__(parent)
        self.chn = chn      # channal id
        self.setTitle('Channel {:d} Setting'.format(chn))

        self.lblFlow = QtWidgets.QLabel()
        self.btnZero = QtWidgets.QPushButton('Zero')
        self.lblScale = QtWidgets.QLabel()
        self.inpScale = ui_shared.create_double_spin_box(1.0, minimum=0.01, maximum=10,
                                                         dec=2, step=0.01)
        self.btnScale = QtWidgets.QPushButton('Commit')
        self.lblRange = QtWidgets.QLabel()
        self.comboRange = QtWidgets.QComboBox()
        self.comboRange.addItems(['1', '2', '5', '10', '20', '50', '100', '200',
                                  '500', '1000', '2000', '5000', '10000', '20000',
                                  '50000', '100000'])
        self.btnRange = QtWidgets.QPushButton('Commit')
        self.lblSP = QtWidgets.QLabel()
        self.inpSP = ui_shared.create_double_spin_box(1.00, minimum=0.01, maximum=1e6,
                                                      dec=2, stepType=1)
        self.btnSP = QtWidgets.QPushButton('Commit')
        self.lblOpMode = QtWidgets.QLabel()
        self.comboOpMode = QtWidgets.QComboBox()
        self.comboOpMode.addItems(['Open', 'Close', 'SetPoint', 'Ratio', 'PCTRL', 'Preset'])
        self.btnOpMode = QtWidgets.QPushButton('Commit')

        col1Layout = QtWidgets.QGridLayout()
        col1Layout.setHorizontalSpacing(4)
        col1Layout.setVerticalSpacing(2)
        col1Layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        col1Layout.addWidget(QtWidgets.QLabel('Current'), 0, 1)
        col1Layout.addWidget(QtWidgets.QLabel('Target'), 0, 2)
        col1Layout.addWidget(QtWidgets.QLabel('Flow (sccm)'), 1, 0)
        col1Layout.addWidget(self.lblFlow, 1, 1)
        col1Layout.addWidget(self.btnZero, 1, 3)
        col1Layout.addWidget(QtWidgets.QLabel('Full Norminal Range'), 2, 0)
        col1Layout.addWidget(self.lblRange, 2, 1)
        col1Layout.addWidget(self.comboRange, 2, 2)
        col1Layout.addWidget(self.btnRange, 2, 3)
        col1Layout.addWidget(QtWidgets.QLabel('Scale Factor'), 3, 0)
        col1Layout.addWidget(self.lblScale, 3, 1)
        col1Layout.addWidget(self.inpScale, 3, 2)
        col1Layout.addWidget(self.btnScale, 3, 3)
        col1Layout.addWidget(QtWidgets.QLabel('Set Point'), 4, 0)
        col1Layout.addWidget(self.lblSP, 4, 1)
        col1Layout.addWidget(self.inpSP, 4, 2)
        col1Layout.addWidget(self.btnSP, 4, 3)
        col1Layout.addWidget(QtWidgets.QLabel('Operation Mode'), 5, 0)
        col1Layout.addWidget(self.lblOpMode, 5, 1)
        col1Layout.addWidget(self.comboOpMode, 5, 2)
        col1Layout.addWidget(self.btnOpMode, 5, 3)

        self.lblRelaySP1 = QtWidgets.QLabel()
        self.lblRelaySP2 = QtWidgets.QLabel()
        self.inpRelaySP1 = ui_shared.create_double_spin_box(1.0, minimum=0, dec=2, stepType=1)
        self.inpRelaySP2 = ui_shared.create_double_spin_box(1.0, minimum=0, dec=2, stepType=1)
        self.btnRelaySP1 = QtWidgets.QPushButton('Commit')
        self.btnRelaySP2 = QtWidgets.QPushButton('Commit')
        self.lblRelayHys1 = QtWidgets.QLabel()
        self.lblRelayHys2 = QtWidgets.QLabel()
        self.inpRelayHys1 = ui_shared.create_double_spin_box(1.0, minimum=0, dec=2, stepType=1)
        self.inpRelayHys2 = ui_shared.create_double_spin_box(1.0, minimum=0, dec=2, stepType=1)
        self.btnRelayHys1 = QtWidgets.QPushButton('Commit')
        self.btnRelayHys2 = QtWidgets.QPushButton('Commit')
        self.lblRelayDir1 = QtWidgets.QLabel()
        self.lblRelayDir2 = QtWidgets.QLabel()
        self.comboRelayDir1 = QtWidgets.QComboBox()
        self.comboRelayDir1.addItems(['Above', 'Below'])
        self.comboRelayDir2 = QtWidgets.QComboBox()
        self.comboRelayDir2.addItems(['Above', 'Below'])
        self.btnRelayDir1 = QtWidgets.QPushButton('Commit')
        self.btnRelayDir2 = QtWidgets.QPushButton('Commit')
        self.lblRelayStat1 = QtWidgets.QLabel()
        self.lblRelayStat2 = QtWidgets.QLabel()
        self.comboRelayStat1 = QtWidgets.QComboBox()
        self.comboRelayStat1.addItems(['Set', 'Enable', 'Clear'])
        self.comboRelayStat2 = QtWidgets.QComboBox()
        self.comboRelayStat2.addItems(['Set', 'Enable', 'Clear'])
        self.btnRelayStat1 = QtWidgets.QPushButton('Commit')
        self.btnRelayStat2 = QtWidgets.QPushButton('Commit')

        col2Layout = QtWidgets.QGridLayout()
        col2Layout.setHorizontalSpacing(4)
        col2Layout.setVerticalSpacing(2)
        col2Layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        col2Layout.addWidget(QtWidgets.QLabel('Current'), 0, 1)
        col2Layout.addWidget(QtWidgets.QLabel('Target'), 0, 2)
        col2Layout.addWidget(QtWidgets.QLabel('Current'), 0, 4)
        col2Layout.addWidget(QtWidgets.QLabel('Target'), 0, 5)
        col2Layout.addWidget(QtWidgets.QLabel('Relay {:d}'.format(chn*2-1)), 1, 1, 1, 3)
        col2Layout.addWidget(QtWidgets.QLabel('Relay {:d}'.format(chn*2)), 1, 4, 1, 3)
        col2Layout.addWidget(QtWidgets.QLabel('Set Point'), 2, 0)
        col2Layout.addWidget(self.lblRelaySP1, 2, 1)
        col2Layout.addWidget(self.inpRelaySP1, 2, 2)
        col2Layout.addWidget(self.btnRelaySP1, 2, 3)
        col2Layout.addWidget(self.lblRelaySP2, 2, 4)
        col2Layout.addWidget(self.inpRelaySP2, 2, 5)
        col2Layout.addWidget(self.btnRelaySP2, 2, 6)
        col2Layout.addWidget(QtWidgets.QLabel('Hysteris'), 3, 0)
        col2Layout.addWidget(self.lblRelayHys1, 3, 1)
        col2Layout.addWidget(self.inpRelayHys1, 3, 2)
        col2Layout.addWidget(self.btnRelayHys1, 3, 3)
        col2Layout.addWidget(self.lblRelayHys2, 3, 4)
        col2Layout.addWidget(self.inpRelayHys2, 3, 5)
        col2Layout.addWidget(self.btnRelayHys2, 3, 6)
        col2Layout.addWidget(QtWidgets.QLabel('Direction'), 4, 0)
        col2Layout.addWidget(self.lblRelayDir1, 4, 1)
        col2Layout.addWidget(self.comboRelayDir1, 4, 2)
        col2Layout.addWidget(self.btnRelayDir1, 4, 3)
        col2Layout.addWidget(self.lblRelayDir2, 4, 4)
        col2Layout.addWidget(self.comboRelayDir2, 4, 5)
        col2Layout.addWidget(self.btnRelayDir2, 4, 6)
        col2Layout.addWidget(QtWidgets.QLabel('Status'), 5, 0)
        col2Layout.addWidget(self.lblRelayStat1, 5, 1)
        col2Layout.addWidget(self.comboRelayStat1, 5, 2)
        col2Layout.addWidget(self.btnRelayStat1, 5, 3)
        col2Layout.addWidget(self.lblRelayStat2, 5, 4)
        col2Layout.addWidget(self.comboRelayStat2, 5, 5)
        col2Layout.addWidget(self.btnRelayStat2, 5, 6)

        thisLayout = QtWidgets.QGridLayout()
        thisLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        thisLayout.setHorizontalSpacing(20)
        thisLayout.addLayout(col1Layout, 0, 0)
        thisLayout.addLayout(col2Layout, 0, 1)
        thisLayout.setColumnStretch(0, 1)
        thisLayout.setColumnStretch(1, 2)
        self.setLayout(thisLayout)

        self.btnGroup = QtWidgets.QButtonGroup()
        self.btnGroup.addButton(self.btnRange, 0)
        self.btnGroup.addButton(self.btnScale, 1)
        self.btnGroup.addButton(self.btnSP, 2)
        self.btnGroup.addButton(self.btnOpMode, 3)
        self.btnGroup.addButton(self.btnRelaySP1, 4)
        self.btnGroup.addButton(self.btnRelaySP2, 5)
        self.btnGroup.addButton(self.btnRelayHys1, 6)
        self.btnGroup.addButton(self.btnRelayHys2, 7)
        self.btnGroup.addButton(self.btnRelayDir1, 8)
        self.btnGroup.addButton(self.btnRelayDir2, 9)
        self.btnGroup.addButton(self.btnRelayStat1, 10)
        self.btnGroup.addButton(self.btnRelayStat2, 11)

        self._btnMap = (
            ('RNG'+str(chn), '{:.2E}', 'float', self.lblRange, self.comboRange),
            ('QSF'+str(chn), '{:.2E}', 'float', self.lblScale, self.inpScale),
            ('QSP'+str(chn), '{:.2E}', 'float', self.lblSP, self.inpSP),
            ('QMD'+str(chn), '{:s}', 'str', self.lblOpMode, self.comboOpMode),
            ('SP'+str(2*chn-1), '{:.2E}', 'float', self.lblRelaySP1, self.inpRelaySP1),
            ('SP'+str(2*chn), '{:.2E}', 'float', self.lblRelaySP2, self.inpRelaySP2),
            ('SH'+str(2*chn-1), '{:.2E}', 'float', self.lblRelayHys1, self.inpRelayHys1),
            ('SH'+str(2*chn), '{:.2E}', 'float', self.lblRelayHys2, self.inpRelayHys2),
            ('SD'+str(2*chn-1), '{:s}', 'str', self.lblRelayDir1, self.comboRelayDir1),
            ('SD'+str(2*chn), '{:s}', 'str', self.lblRelayDir2, self.comboRelayDir2),
            ('EN'+str(2*chn-1), '{:s}', 'str', self.lblRelayStat1, self.comboRelayStat1),
            ('EN'+str(2*chn), '{:s}', 'str', self.lblRelayStat2, self.comboRelayStat2),
        )

    def mks_cmd(self, btn_id):
        """ Get the MKS command associated with btn_id """
        cmd, pfmt, dtype, lbl, cfg = self._btnMap[btn_id]
        # get setted value
        if dtype == 'float':
            if isinstance(cfg, QtWidgets.QComboBox):
                param = pfmt.format(float(cfg.currentText()))
            else:
                param = pfmt.format(cfg.value())
        elif dtype == 'str':
            param = pfmt.format(cfg.currentText())
        else:
            raise ValueError
        return cmd, param

    def update_current(self, btn_id, ans):
        """ Update the MKS setting value associated with btn_id """
        cmd, pfmt, dtype, lbl, cfg = self._btnMap[btn_id]
        # write new value to current value label
        lbl.setText(ans)

    def yield_all(self):
        for btn_tuple in self._btnMap:
            cmd, pfmt, dtype, lbl, cfg = btn_tuple
            yield cmd, lbl


class DialogGCF(QtWidgets.QDialog):
    """ MKS GCF scaling factor calculator """

    sig_calc_gcf = QtCore.pyqtSignal()

    STRUC_CORRECTION = {
        'Monoatomic': 1.030,
        'Diatomic': 1.000,
        'Triatomic': 0.941,
        'Polyatomic': 0.880,
    }

    # scaling factor for density unit (-> g L-1)
    UNIT_DENSITY = {
        'g L-1': 1.0,
        'g cm-3': 1e-3,
        'kg m-3': 1.0,
    }

    # scaling factor for heat capacity unit (-> cal g-1 K-1)
    UNIT_CP = {
        'cal g-1 K-1': 1.0,
        'J g-1 K-1': 1.0 / 4.184,
    }

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle('MKS GCF Scaling Factor Calculator')
        self.setMinimumWidth(800)
        self.setWindowFlags(QtCore.Qt.WindowType.Window)

        self.btnAddGas = QtWidgets.QPushButton('+')
        self.btnAddGas.setFixedWidth(25)
        self._gas_entries = {}  # {id: entry}
        self._dGasSel = DialogGCFGasSel(parent=self)

        self._layout = QtWidgets.QGridLayout()
        self._layout.addWidget(self.btnAddGas, 0, 0)
        self._layout.addWidget(QtWidgets.QLabel('Gas'), 0, 1, 1, 2)
        self._layout.addWidget(QtWidgets.QLabel('Structure'), 0, 3)
        self._layout.addWidget(QtWidgets.QLabel('Fraction'), 0, 4)
        self._layout.addWidget(QtWidgets.QLabel('Density'), 0, 5, 1, 2)
        self._layout.addWidget(QtWidgets.QLabel('Specific Heat Capacity Cp'),
                               0, 7, 1, 2)
        self.inpTemperature = ui_shared.create_double_spin_box(293, minimum=0, dec=1,
                                                               suffix=' K', step=1)
        self.inpTemperature.setFixedWidth(100)
        self.lblGCF = QtWidgets.QLabel()
        self.lblGCF.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextSelectableByMouse)
        box1 = QtWidgets.QGroupBox()
        box1Layout = QtWidgets.QHBoxLayout()
        box1Layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        box1Layout.addWidget(QtWidgets.QLabel('Temperature'))
        box1Layout.addWidget(self.inpTemperature)
        box1Layout.addWidget(QtWidgets.QLabel('GCF Scaling Factor'))
        box1Layout.addWidget(self.lblGCF)
        box1.setLayout(box1Layout)

        box2 = QtWidgets.QGroupBox()
        box2.setLayout(self._layout)
        thisLayout = QtWidgets.QVBoxLayout()
        thisLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        thisLayout.addWidget(box1)
        thisLayout.addWidget(box2)
        self.setLayout(thisLayout)

        self.btnAddGas.clicked.connect(self._add_entry)
        self.delBtnGroup = QtWidgets.QButtonGroup()
        self.delBtnGroup.buttonClicked.connect(self._del_entry)
        self.gasBtnGroup = QtWidgets.QButtonGroup()
        self.gasBtnGroup.buttonClicked.connect(self._sel_gas)
        self.inpTemperature.valueChanged.connect(self.sig_calc_gcf.emit)
        self._add_entry()

    def _add_entry(self):
        newEntry = _GCFGasEntry(parent=self)
        if self._gas_entries:
            n = max(self._gas_entries.keys()) + 1
        else:
            n = 1
        self._gas_entries[n] = newEntry
        r = self._layout.rowCount()
        self._layout.addWidget(newEntry.btnDel, r, 0)
        self._layout.addWidget(newEntry.btnSelGas, r, 1)
        self._layout.addWidget(newEntry.inpGas, r, 2)
        self._layout.addWidget(newEntry.comboGeom, r, 3)
        self._layout.addWidget(newEntry.inpFraction, r, 4)
        self._layout.addWidget(newEntry.inpDensity, r, 5)
        self._layout.addWidget(newEntry.unitDensity, r, 6)
        self._layout.addWidget(newEntry.inpCP, r, 7)
        self._layout.addWidget(newEntry.unitCP, r, 8)
        self.adjustSize()
        self.delBtnGroup.addButton(newEntry.btnDel, n)
        self.gasBtnGroup.addButton(newEntry.btnSelGas, n)
        newEntry.comboGeom.currentIndexChanged.connect(self.sig_calc_gcf.emit)
        newEntry.inpFraction.valueChanged.connect(self.sig_calc_gcf.emit)
        newEntry.inpCP.valueChanged.connect(self.sig_calc_gcf.emit)
        newEntry.unitCP.currentIndexChanged.connect(self.sig_calc_gcf.emit)
        newEntry.inpDensity.valueChanged.connect(self.sig_calc_gcf.emit)
        newEntry.unitDensity.currentIndexChanged.connect(self.sig_calc_gcf.emit)

    def _del_entry(self, btn):

        entry_id = self.delBtnGroup.id(btn)
        entry = self._gas_entries[entry_id]
        self.delBtnGroup.removeButton(entry.btnDel)
        self.gasBtnGroup.removeButton(entry.btnSelGas)
        self._layout.removeWidget(entry.btnDel)
        self._layout.removeWidget(entry.btnSelGas)
        self._layout.removeWidget(entry.inpGas)
        self._layout.removeWidget(entry.comboGeom)
        self._layout.removeWidget(entry.inpFraction)
        self._layout.removeWidget(entry.inpDensity)
        self._layout.removeWidget(entry.unitDensity)
        self._layout.removeWidget(entry.inpCP)
        self._layout.removeWidget(entry.unitCP)
        del self._gas_entries[entry_id]
        entry.deleteLater()
        self.adjustSize()

    def _sel_gas(self, btn):
        entry_id = self.gasBtnGroup.id(btn)
        self._dGasSel.exec()
        if self._dGasSel.result() == QtWidgets.QDialog.DialogCode.Accepted:
            gas, mass, name, struc, rho, cp = self._dGasSel.current_gas_params()
            entry = self._gas_entries[entry_id]
            entry.update_gas_params(gas, struc, rho, cp)

    def yield_entry_params(self):
        for entry in self._gas_entries.values():
            yield (self.STRUC_CORRECTION[entry.comboGeom.currentText()],
                   entry.inpFraction.value(),
                   entry.inpDensity.value() * self.UNIT_DENSITY[entry.unitDensity.currentText()],
                   entry.inpCP.value() * self.UNIT_CP[entry.unitCP.currentText()])


class _GCFGasEntry(QtWidgets.QWidget):
    """ MKS gas entry, include gas properties:
        fractional flow
        structure: mono, diatomic, polyatomic
        density
        heat capacity
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        thisLayout = QtWidgets.QHBoxLayout()
        self.btnDel = QtWidgets.QPushButton('-')
        self.btnDel.setFixedWidth(25)
        self.btnSelGas = QtWidgets.QPushButton('🔍')
        self.btnSelGas.setFixedWidth(35)
        self.inpGas = QtWidgets.QLineEdit()
        self.inpFraction = ui_shared.create_double_spin_box(100.0, minimum=0., maximum=100.,
                                                            dec=2, suffix=' %', stepType=1)
        self.inpFraction.setFixedWidth(125)
        self.inpDensity = ui_shared.create_double_spin_box(1, minimum=0, dec=4)
        self.inpDensity.setFixedWidth(120)
        self.comboGeom = QtWidgets.QComboBox()
        self.comboGeom.addItems(['Monoatomic', 'Diatomic', 'Triatomic', 'Polyatomic'])
        self.inpCP = ui_shared.create_double_spin_box(1, minimum=0, dec=4)
        self.inpCP.setFixedWidth(120)
        self.unitDensity = QtWidgets.QComboBox()
        self.unitDensity.addItems(['g L-1', 'g cm-3', 'kg m-3'])
        self.unitCP = QtWidgets.QComboBox()
        self.unitCP.addItems(['cal g-1 K-1', 'J g-1 K-1'])
        thisLayout.addWidget(self.btnDel)
        thisLayout.addWidget(self.btnSelGas)
        thisLayout.addWidget(self.inpGas)
        thisLayout.addWidget(self.comboGeom)
        thisLayout.addWidget(self.inpFraction)
        thisLayout.addWidget(self.inpDensity)
        thisLayout.addWidget(self.unitDensity)
        thisLayout.addWidget(self.inpCP)
        thisLayout.addWidget(self.unitCP)
        self.setLayout(thisLayout)
        self.btnDel.clicked.connect(self.deleteLater)

    def update_gas_params(self, gas, struc, rho, cp):

        self.inpGas.setText(gas)
        self.comboGeom.setCurrentText(struc)
        self.inpDensity.setValue(rho)
        self.inpCP.setValue(cp)
        self.unitDensity.setCurrentIndex(0)
        self.unitCP.setCurrentIndex(0)


class DialogGCFGasSel(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Select a pre-defined gas')
        self.setMinimumWidth(500)
        self.gcf_gases = api_flow.load_gcf_gases()
        self.gcf_gas_formulae = tuple(x[0] for x in self.gcf_gases)
        self._sort_idx = {'name': 2, 'formula': 0, 'mass': 1}
        box1 = QtWidgets.QGroupBox()
        box1.setTitle('Sort by')
        box1Layout = QtWidgets.QHBoxLayout()
        self.btnSortByName = QtWidgets.QPushButton('Name')
        self.btnSortByFormula = QtWidgets.QPushButton('Formula')
        self.btnSortByMass = QtWidgets.QPushButton('Mass')
        box1Layout.addWidget(self.btnSortByName)
        box1Layout.addWidget(self.btnSortByFormula)
        box1Layout.addWidget(self.btnSortByMass)
        box1.setLayout(box1Layout)

        monoFont = QtGui.QFont()
        monoFont.setStyleHint(QtGui.QFont.StyleHint.Monospace)
        self.gasList = QtWidgets.QListWidget()
        self.gasList.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.MultiSelection)
        self.gasList.setFont(monoFont)
        self.gasList.setStyleSheet('font-family: Monospace')
        for params in self.gcf_gases:
            txt = '{:<12s} {:>3d} {:<24s}'.format(*params[:3])
            self.gasList.addItem(QtWidgets.QListWidgetItem(txt))
        area = QtWidgets.QScrollArea()
        area.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        area.setWidget(self.gasList)
        area.setWidgetResizable(True)

        self.btnOk = QtWidgets.QPushButton('Ok')
        self.btnCancel = QtWidgets.QPushButton('Cancel')
        box2Layout = QtWidgets.QHBoxLayout()
        box2Layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        box2Layout.addWidget(self.btnCancel)
        box2Layout.addWidget(self.btnOk)
        self.btnOk.clicked.connect(self.accept)
        self.btnCancel.clicked.connect(self.reject)

        thisLayout = QtWidgets.QVBoxLayout()
        thisLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        thisLayout.addWidget(box1)
        thisLayout.addWidget(area)
        thisLayout.addLayout(box2Layout)
        self.setLayout(thisLayout)

        self.btnSortByName.clicked.connect(lambda: self.sortby('name'))
        self.btnSortByFormula.clicked.connect(lambda: self.sortby('formula'))
        self.btnSortByMass.clicked.connect(lambda: self.sortby('mass'))
        self.gasList.itemDoubleClicked.connect(self.accept)

    def current_gas_params(self):
        """ Return the current selected gas parameter """
        row = self.gasList.currentRow()
        txt = self.gasList.item(row).text()
        formula = txt.split()[0]
        i = self.gcf_gas_formulae.index(formula)
        return self.gcf_gases[i]

    def sortby(self, order):

        newlist = sorted(self.gcf_gases, key=lambda x: x[self._sort_idx[order]])
        self.gasList.clear()
        for params in newlist:
            txt = '{:<12s} {:>3d} {:<24s}'.format(*params[:3])
            self.gasList.addItem(QtWidgets.QListWidgetItem(txt))
        self.gasList.setCurrentRow(0)


class DialogAWG(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle('Configure AWG')

        btnLayout = QtWidgets.QHBoxLayout()
        btnLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.btnOk = QtWidgets.QPushButton('OK')
        btnLayout.addWidget(self.btnOk)

        thisLayout = QtWidgets.QVBoxLayout()
        thisLayout.addLayout(btnLayout)
        self.setLayout(thisLayout)

        self.btnOk.clicked.connect(self.accept)


class DialogPowerSupp(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle('Configure Power Supply')

        btnLayout = QtWidgets.QHBoxLayout()
        btnLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.btnOk = QtWidgets.QPushButton('OK')
        btnLayout.addWidget(self.btnOk)

        thisLayout = QtWidgets.QVBoxLayout()
        thisLayout.addLayout(btnLayout)
        self.setLayout(thisLayout)

        self.btnOk.clicked.connect(self.accept)



class DialogCloseInst(QtWidgets.QDialog):
    """ Dialog window for closing selected instrument. """

    def __init__(self, parent=None): 
        super().__init__(parent)
        self.setMinimumWidth(400)
        self.setMinimumHeight(400)
        self.setWindowTitle('Close Instrument')

        inst = QtWidgets.QWidget()
        self.synToggle = QtWidgets.QCheckBox()
        self.liaToggle = QtWidgets.QCheckBox()
        self.pciToggle = QtWidgets.QCheckBox()
        self.motorToggle = QtWidgets.QCheckBox()
        self.pressureToggle = QtWidgets.QCheckBox()

        instLayout = QtWidgets.QFormLayout()
        instLayout.addRow(QtWidgets.QLabel('Instrument'), QtWidgets.QLabel('Status'))
        instLayout.addRow(QtWidgets.QLabel('Synthesizer'), self.synToggle)
        instLayout.addRow(QtWidgets.QLabel('Lockin'), self.liaToggle)
        instLayout.addRow(QtWidgets.QLabel('Oscilloscope'), self.pciToggle)
        instLayout.addRow(QtWidgets.QLabel('Motor'), self.motorToggle)
        instLayout.addRow(QtWidgets.QLabel('Pressure Gauge'), self.pressureToggle)
        inst.setLayout(instLayout)

        okButton = QtWidgets.QPushButton(ui_shared.btn_label('complete'))
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(inst)
        mainLayout.addWidget(QtWidgets.QLabel('No command will be sent before you hit the accept button'))
        mainLayout.addWidget(okButton)
        self.setLayout(mainLayout)

        okButton.clicked.connect(self.accept)


class DialogSyn(QtWidgets.QDialog):
    """ Dialog window for displaying full synthesizer settings. """

    def __init__(self, parent=None): 
        super().__init__(parent)

        self.setMinimumWidth(800)
        self.setMinimumHeight(400)
        self.setWindowTitle('Configure Synthesizer')
        self.setWindowFlag(QtCore.Qt.WindowType.Window)

        self.instGroup = QtWidgets.QGroupBox()
        self.rfGroup = QtWidgets.QGroupBox()
        self.modGroup = QtWidgets.QGroupBox()

        self.instGroup.setTitle('Instrument Session')
        self.instNameLabel = QtWidgets.QLabel()
        self.instInterfaceLabel = QtWidgets.QLabel()
        self.instInterfaceNumLabel = QtWidgets.QLabel()
        self.instRemoteDispLabel = QtWidgets.QLabel()
        instGroupLayout = QtWidgets.QFormLayout()
        instGroupLayout.addRow(QtWidgets.QLabel('Instrument Name'), self.instNameLabel)
        instGroupLayout.addRow(QtWidgets.QLabel('Interface Type'), self.instInterfaceLabel)
        instGroupLayout.addRow(QtWidgets.QLabel('Interface Number'), self.instInterfaceNumLabel)
        instGroupLayout.addRow(QtWidgets.QLabel('Remote Display'), self.instRemoteDispLabel)
        self.instGroup.setLayout(instGroupLayout)

        self.rfGroup.setTitle('RF Settings')
        self.rfOutputLabel = QtWidgets.QLabel()
        self.modOutputLabel = QtWidgets.QLabel()
        self.synFreqLabel = QtWidgets.QLabel()
        rfGroupLayout = QtWidgets.QGridLayout()
        rfGroupLayout.addWidget(QtWidgets.QLabel('RF Output'), 0, 0)
        rfGroupLayout.addWidget(self.rfOutputLabel, 0, 1)
        rfGroupLayout.addWidget(QtWidgets.QLabel('Synth Frequency'), 0, 2)
        rfGroupLayout.addWidget(self.synFreqLabel, 0, 3)
        rfGroupLayout.addWidget(QtWidgets.QLabel('Modulation Output'), 0, 4)
        rfGroupLayout.addWidget(self.modOutputLabel, 0, 5)
        self.rfGroup.setLayout(rfGroupLayout)

        self.modGroup.setTitle('Modulation Settings')
        self.am1StateLabel = QtWidgets.QLabel()
        self.am2StateLabel = QtWidgets.QLabel()
        self.fm1StateLabel = QtWidgets.QLabel()
        self.fm2StateLabel = QtWidgets.QLabel()
        self.pm1StateLabel = QtWidgets.QLabel()
        self.pm2StateLabel = QtWidgets.QLabel()
        self.lfStateLabel = QtWidgets.QLabel()
        self.am1DepthLabel = QtWidgets.QLabel()
        self.am2DepthLabel = QtWidgets.QLabel()
        self.fm1DevLabel = QtWidgets.QLabel()
        self.fm2DevLabel = QtWidgets.QLabel()
        self.pm1DevLabel = QtWidgets.QLabel()
        self.pm2DevLabel = QtWidgets.QLabel()
        self.lfVolLabel = QtWidgets.QLabel()
        self.am1SrcLabel = QtWidgets.QLabel()
        self.am2SrcLabel = QtWidgets.QLabel()
        self.fm1SrcLabel = QtWidgets.QLabel()
        self.fm2SrcLabel = QtWidgets.QLabel()
        self.pm1SrcLabel = QtWidgets.QLabel()
        self.pm2SrcLabel = QtWidgets.QLabel()
        self.lfSrcLabel = QtWidgets.QLabel()
        self.am1FreqLabel = QtWidgets.QLabel()
        self.am2FreqLabel = QtWidgets.QLabel()
        self.fm1FreqLabel = QtWidgets.QLabel()
        self.fm2FreqLabel = QtWidgets.QLabel()
        self.pm1FreqLabel = QtWidgets.QLabel()
        self.pm2FreqLabel = QtWidgets.QLabel()
        self.am1WaveLabel = QtWidgets.QLabel()
        self.am2WaveLabel = QtWidgets.QLabel()
        self.fm1WaveLabel = QtWidgets.QLabel()
        self.fm2WaveLabel = QtWidgets.QLabel()
        self.pm1WaveLabel = QtWidgets.QLabel()
        self.pm2WaveLabel = QtWidgets.QLabel()

        modGroupLayout = QtWidgets.QGridLayout()
        modGroupLayout.addWidget(QtWidgets.QLabel('Channel'), 0, 0)
        modGroupLayout.addWidget(QtWidgets.QLabel('Source'), 0, 1)
        modGroupLayout.addWidget(QtWidgets.QLabel('State'), 0, 2)
        modGroupLayout.addWidget(QtWidgets.QLabel('Depth/Dev'), 0, 3)
        modGroupLayout.addWidget(QtWidgets.QLabel('Rate'), 0, 4)
        modGroupLayout.addWidget(QtWidgets.QLabel('Waveform'), 0, 5)
        modGroupLayout.addWidget(QtWidgets.QLabel('AM1'), 1, 0)
        modGroupLayout.addWidget(self.am1StateLabel, 1, 1)
        modGroupLayout.addWidget(self.am1SrcLabel, 1, 2)
        modGroupLayout.addWidget(self.am1DepthLabel, 1, 3)
        modGroupLayout.addWidget(self.am1FreqLabel, 1, 4)
        modGroupLayout.addWidget(self.am1WaveLabel, 1, 5)
        modGroupLayout.addWidget(QtWidgets.QLabel('AM2'), 2, 0)
        modGroupLayout.addWidget(self.am2StateLabel, 2, 1)
        modGroupLayout.addWidget(self.am2SrcLabel, 2, 2)
        modGroupLayout.addWidget(self.am2DepthLabel, 2, 3)
        modGroupLayout.addWidget(self.am2FreqLabel, 2, 4)
        modGroupLayout.addWidget(self.am2WaveLabel, 2, 5)
        modGroupLayout.addWidget(QtWidgets.QLabel('FM1'), 3, 0)
        modGroupLayout.addWidget(self.fm1StateLabel, 3, 1)
        modGroupLayout.addWidget(self.fm1SrcLabel, 3, 2)
        modGroupLayout.addWidget(self.fm1DevLabel, 3, 3)
        modGroupLayout.addWidget(self.fm1FreqLabel, 3, 4)
        modGroupLayout.addWidget(self.fm1WaveLabel, 3, 5)
        modGroupLayout.addWidget(QtWidgets.QLabel('FM2'), 4, 0)
        modGroupLayout.addWidget(self.fm2StateLabel, 4, 1)
        modGroupLayout.addWidget(self.fm2SrcLabel, 4, 2)
        modGroupLayout.addWidget(self.fm2DevLabel, 4, 3)
        modGroupLayout.addWidget(self.fm2FreqLabel, 4, 4)
        modGroupLayout.addWidget(self.fm2WaveLabel, 4, 5)
        modGroupLayout.addWidget(QtWidgets.QLabel('φM1'), 5, 0)
        modGroupLayout.addWidget(self.pm1StateLabel, 5, 1)
        modGroupLayout.addWidget(self.pm1SrcLabel, 5, 2)
        modGroupLayout.addWidget(self.pm1DevLabel, 5, 3)
        modGroupLayout.addWidget(self.pm1FreqLabel, 5, 4)
        modGroupLayout.addWidget(self.pm1WaveLabel, 5, 5)
        modGroupLayout.addWidget(QtWidgets.QLabel('φM2'), 6, 0)
        modGroupLayout.addWidget(self.pm2StateLabel, 6, 1)
        modGroupLayout.addWidget(self.pm2SrcLabel, 6, 2)
        modGroupLayout.addWidget(self.pm2DevLabel, 6, 3)
        modGroupLayout.addWidget(self.pm2FreqLabel, 6, 4)
        modGroupLayout.addWidget(self.pm2WaveLabel, 6, 5)
        modGroupLayout.addWidget(QtWidgets.QLabel('LF OUT'), 7, 0)
        modGroupLayout.addWidget(self.lfStateLabel, 7, 1)
        modGroupLayout.addWidget(self.lfSrcLabel, 7, 2)
        modGroupLayout.addWidget(self.lfVolLabel, 7, 3)
        self.modGroup.setLayout(modGroupLayout)

        self.refreshButton = QtWidgets.QPushButton('Manual Refresh')
        self.acceptButton = QtWidgets.QPushButton('OK')
        mainLayout = QtWidgets.QGridLayout()
        mainLayout.addWidget(self.instGroup, 0, 0, 1, 5)
        mainLayout.addWidget(self.rfGroup, 1, 0, 1, 5)
        mainLayout.addWidget(self.modGroup, 2, 0, 1, 5)
        mainLayout.addWidget(self.acceptButton, 3, 2, 1, 1)
        self.setLayout(mainLayout)
        self.acceptButton.clicked.connect(self.accept)

    def print_info(self, info):

        # update instrument panel
        self.instNameLabel.setText(info.instName)
        self.instInterfaceLabel.setText(info.instInterface)
        self.instInterfaceNumLabel.setText(str(info.instInterfaceNum))
        self.instRemoteDispLabel.setText('ON' if info.instRemoteDisp else 'OFF')

        # update RF setting panel
        self.rfOutputLabel.setText('ON' if info.rfToggle else 'OFF')
        self.modOutputLabel.setText('ON' if info.modToggle else 'OFF')
        self.synFreqLabel.setText('{:.9f} MHz'.format(info.synFreq * 1e-6))

        # update modulation setting panel
        self.am1StateLabel.setText('ON' if info.AM1Toggle else 'OFF')
        self.am1SrcLabel.setText(info.AM1Src)
        self.am1DepthLabel.setText('{:.1f}% ({:.0f} dB)'.format(info.AM1DepthPercent, info.AM1DepthDbm))
        self.am1FreqLabel.setText(siFormat(info.AM1Freq, suffix='Hz'))
        self.am1WaveLabel.setText(info.AM1Wave)

        self.am2StateLabel.setText('ON' if info.AM2Toggle else 'OFF')
        self.am2SrcLabel.setText(info.AM2Src)
        self.am2DepthLabel.setText('{:.1f}% ({:.0f} dB)'.format(info.AM2DepthPercent, info.AM2DepthDbm))
        self.am2FreqLabel.setText(siFormat(info.AM2Freq, suffix='Hz'))
        self.am2WaveLabel.setText(info.AM2Wave)

        self.fm1StateLabel.setText('ON' if info.FM1Toggle else 'OFF')
        self.fm1SrcLabel.setText(info.FM1Src)
        self.fm1DevLabel.setText(siFormat(info.FM1Dev, suffix='Hz'))
        self.fm1FreqLabel.setText(siFormat(info.FM1Freq, suffix='Hz'))
        self.fm1WaveLabel.setText(info.FM1Wave)

        self.fm2StateLabel.setText('ON' if info.FM2Toggle else 'OFF')
        self.fm2SrcLabel.setText(info.FM2Src)
        self.fm2DevLabel.setText(siFormat(info.FM2Dev, suffix='Hz'))
        self.fm2FreqLabel.setText(siFormat(info.FM2Freq, suffix='Hz'))
        self.fm2WaveLabel.setText(info.FM2Wave)

        self.pm1StateLabel.setText('ON' if info.PM1Toggle else 'OFF')
        self.pm1SrcLabel.setText(info.PM1Src)
        self.pm1DevLabel.setText(siFormat(info.PM1Dev, suffix='rad'))
        self.pm1FreqLabel.setText(siFormat(info.PM1Freq, suffix='Hz'))
        self.pm1WaveLabel.setText(info.PM1Wave)

        self.pm2StateLabel.setText('ON' if info.PM2Toggle else 'OFF')
        self.pm2SrcLabel.setText(info.PM2Src)
        self.pm2DevLabel.setText(siFormat(info.PM2Dev, suffix='rad'))
        self.pm2FreqLabel.setText(siFormat(info.PM2Freq,  suffix='Hz'))
        self.pm2WaveLabel.setText(info.PM2Wave)

        self.lfStateLabel.setText('ON' if info.LFToggle else 'OFF')
        self.lfSrcLabel.setText(info.LFSrc)
        self.lfVolLabel.setText(siFormat(info.LFVoltage, suffix='V'))


class DialogLockin(QtWidgets.QDialog):
    """ Dialog window for displaying full lockin settings. """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        self.setWindowTitle('Lockin Amplifier Settings')

        self.instGroup = QtWidgets.QGroupBox()
        self.refGroup = QtWidgets.QGroupBox()
        self.inputGroup = QtWidgets.QGroupBox()
        self.gainGroup = QtWidgets.QGroupBox()
        self.outputGroup = QtWidgets.QGroupBox()

        self.instGroup.setTitle('Instrument Session')
        self.instNameLabel = QtWidgets.QLabel()
        self.instInterfaceLabel = QtWidgets.QLabel()
        self.instInterfaceNumLabel = QtWidgets.QLabel()
        instGroupLayout = QtWidgets.QFormLayout()
        instGroupLayout.addRow(QtWidgets.QLabel('Instrument Name'), self.instNameLabel)
        instGroupLayout.addRow(QtWidgets.QLabel('Interface Type'), self.instInterfaceLabel)
        instGroupLayout.addRow(QtWidgets.QLabel('Interface Number'), self.instInterfaceNumLabel)
        self.instGroup.setLayout(instGroupLayout)

        self.refGroup.setTitle('Reference and Phase')
        self.refSrcLabel = QtWidgets.QLabel()
        self.refFreqLabel = QtWidgets.QLabel()
        self.refHarmLabel = QtWidgets.QLabel()
        self.refPhaseLabel = QtWidgets.QLabel()
        refGroupLayout = QtWidgets.QFormLayout()
        refGroupLayout.addRow(QtWidgets.QLabel('Reference Source'), self.refSrcLabel)
        refGroupLayout.addRow(QtWidgets.QLabel('Reference Freq'), self.refFreqLabel)
        refGroupLayout.addRow(QtWidgets.QLabel('Harmonics'), self.refHarmLabel)
        refGroupLayout.addRow(QtWidgets.QLabel('Phase'), self.refPhaseLabel)
        self.refGroup.setLayout(refGroupLayout)

        self.inputGroup.setTitle('Input and Filter')
        self.inputConfigLabel = QtWidgets.QLabel()
        self.inputGroundingLabel = QtWidgets.QLabel()
        self.inputCoupleLabel = QtWidgets.QLabel()
        self.inputFilterLabel = QtWidgets.QLabel()
        inputGroupLayout = QtWidgets.QFormLayout()
        inputGroupLayout.addRow(QtWidgets.QLabel('Input Config'), self.inputConfigLabel)
        inputGroupLayout.addRow(QtWidgets.QLabel('Input Grounding'), self.inputGroundingLabel)
        inputGroupLayout.addRow(QtWidgets.QLabel('Input Coupling'), self.inputCoupleLabel)
        inputGroupLayout.addRow(QtWidgets.QLabel('Input Filter'), self.inputFilterLabel)
        self.inputGroup.setLayout(inputGroupLayout)

        self.gainGroup.setTitle('Gain')
        self.gainSensLabel = QtWidgets.QLabel()
        self.gainReserveLabel = QtWidgets.QLabel()
        self.gainTCLabel = QtWidgets.QLabel()
        self.lpSlopeLabel = QtWidgets.QLabel()
        gainGroupLayout = QtWidgets.QFormLayout()
        gainGroupLayout.addRow(QtWidgets.QLabel('Sensitivity'), self.gainSensLabel)
        gainGroupLayout.addRow(QtWidgets.QLabel('Time Constant'), self.gainTCLabel)
        gainGroupLayout.addRow(QtWidgets.QLabel('Reserve'), self.gainReserveLabel)
        gainGroupLayout.addRow(QtWidgets.QLabel('Low-pass Filter Slope'), self.lpSlopeLabel)
        self.gainGroup.setLayout(gainGroupLayout)

        self.outputGroup.setTitle('Display and Output')
        self.outputDisp1Label = QtWidgets.QLabel()
        self.outputDisp2Label = QtWidgets.QLabel()
        self.outputFront1Label = QtWidgets.QLabel()
        self.outputFront2Label = QtWidgets.QLabel()
        self.outputSRateLabel = QtWidgets.QLabel()
        outputGroupLayout = QtWidgets.QGridLayout()
        outputGroupLayout.addWidget(QtWidgets.QLabel('Chanel 1'), 0, 1)
        outputGroupLayout.addWidget(QtWidgets.QLabel('Chanel 2'), 0, 2)
        outputGroupLayout.addWidget(QtWidgets.QLabel('Display Output'), 1, 0)
        outputGroupLayout.addWidget(self.outputDisp1Label, 1, 1)
        outputGroupLayout.addWidget(self.outputDisp2Label, 1, 2)
        outputGroupLayout.addWidget(QtWidgets.QLabel('Front Panel Output'), 2, 0)
        outputGroupLayout.addWidget(self.outputFront1Label, 2, 1)
        outputGroupLayout.addWidget(self.outputFront2Label, 2, 2)
        outputGroupLayout.addWidget(QtWidgets.QLabel('Sampling Rate'), 3, 0)
        outputGroupLayout.addWidget(self.outputSRateLabel, 3, 1, 1, 2)
        self.outputGroup.setLayout(outputGroupLayout)

        self.refreshButton = QtWidgets.QPushButton('Manual Refresh')
        self.acceptButton = QtWidgets.QPushButton(ui_shared.btn_label('accept'))

        mainLayout = QtWidgets.QGridLayout()
        mainLayout.addWidget(self.instGroup, 0, 0, 1, 6)
        mainLayout.addWidget(self.inputGroup, 1, 0, 1, 3)
        mainLayout.addWidget(self.outputGroup, 1, 3, 1, 3)
        mainLayout.addWidget(self.refGroup, 2, 0, 1, 3)
        mainLayout.addWidget(self.gainGroup, 2, 3, 1, 3)
        mainLayout.addWidget(self.acceptButton, 3, 2, 1, 2)
        self.setLayout(mainLayout)

        self.acceptButton.clicked.connect(self.accept)

    def print_info(self, info):

        # update instrument panel
        self.instNameLabel.setText(info.inst_name)
        self.instInterfaceLabel.setText(info.inst_interface)
        self.instInterfaceNumLabel.setText(str(info.inst_interface_num))

        # update ref group
        self.refSrcLabel.setText(info.ref_src_txt)
        self.refFreqLabel.setText(siFormat(info.ref_freq, suffix='Hz'))
        self.refHarmLabel.setText('{:d}'.format(info.ref_harm))
        self.refPhaseLabel.setText('{:.2f} deg'.format(info.ref_phase))

        # update input group
        self.inputConfigLabel.setText(info.config_txt)
        self.inputGroundingLabel.setText(info.gnd_txt)
        self.inputCoupleLabel.setText(info.couple_txt)
        self.inputFilterLabel.setText(info.input_filter_txt)

        # update gain group
        self.gainSensLabel.setText(info.sens_txt)
        self.gainTCLabel.setText(info.tau_txt)
        self.gainReserveLabel.setText(info.reserve_txt)
        self.lpSlopeLabel.setText(info.octave_txt)

        # update output group
        self.outputDisp1Label.setText(info.disp1_txt)
        self.outputDisp2Label.setText(info.disp2_txt)
        self.outputFront1Label.setText(info.front1_txt)
        self.outputFront2Label.setText(info.front2_txt)
        self.outputSRateLabel.setText(info.sample_rate_txt)


class LWAParserDialog(QtWidgets.QDialog):
    """ Dialog window for the LWA file previewer & parser. """

    def __init__(self, parent, filename):
        QtWidgets.QDialog.__init__(self, parent)
        self.parent = parent
        self.filename = filename
        self.setMinimumWidth(1200)
        self.setMinimumHeight(600)
        self.setWindowTitle('LWA Preview & Parser')
        self.entry_id_to_export = []
        self.preview_win = PrevSpectrumDialog(self)

        self.mainLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.mainLayout.addWidget(QtWidgets.QLabel('Source file: {:s}'.format(filename)))

        # read lwa batch scan entry from file
        self.entry_settings, self.hd_line_num = lwa.scan_header(filename)

        if self.entry_settings:
            # set top buttons
            topButtons = QtWidgets.QWidget()
            self.exportLWAButton = QtWidgets.QPushButton('Export (LWA Format)')
            self.exportLWAButton.clicked.connect(self.export_lwa)
            self.exportXYButton = QtWidgets.QPushButton('Export (XY Format)')
            self.exportXYButton.clicked.connect(self.export_xy)
            self.openFileButton = QtWidgets.QPushButton('Open New File')
            self.openFileButton.clicked.connect(self.open_new_file)
            topButtonLayout = QtWidgets.QHBoxLayout()
            topButtonLayout.addWidget(self.exportLWAButton)
            topButtonLayout.addWidget(self.exportXYButton)
            topButtonLayout.addWidget(self.openFileButton)
            topButtons.setLayout(topButtonLayout)
            self.mainLayout.addWidget(topButtons)

            # set up QButtonGroup to manage checkboxes
            self.previewButtonGroup = QtGui.QButtonGroup()
            self.previewButtonGroup.setExclusive(True)
            self.exportLWAButtonGroup = QtGui.QButtonGroup()
            self.exportLWAButtonGroup.setExclusive(False)
            # set up the batch list area
            self.batchListWidget = QtWidgets.QWidget()
            batchArea = QtWidgets.QScrollArea()
            batchArea.setWidgetResizable(True)
            batchArea.setWidget(self.batchListWidget)

            self.batchLayout = QtWidgets.QGridLayout()
            self.batchLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
            # row of names
            self.batchLayout.addWidget(QtWidgets.QLabel('Preview'), 0, 0)
            self.batchLayout.addWidget(QtWidgets.QLabel('Export'), 0, 1)
            self.batchLayout.addWidget(QtWidgets.QLabel('Scan #'), 0, 2)
            self.batchLayout.addWidget(QtWidgets.QLabel('Comment'), 0, 3)
            self.batchLayout.addWidget(QtWidgets.QLabel('Date'), 0, 4)
            self.batchLayout.addWidget(QtWidgets.QLabel('Time'), 0, 5)
            self.batchLayout.addWidget(QtWidgets.QLabel('Start Freq (MHz)'), 0, 6)
            self.batchLayout.addWidget(QtWidgets.QLabel('Stop Freq (MHz)'), 0, 7)
            self.batchLayout.addWidget(QtWidgets.QLabel('Step Freq'), 0, 8)
            self.batchLayout.addWidget(QtWidgets.QLabel('Points'), 0, 9)
            self.batchLayout.addWidget(QtWidgets.QLabel('Average'), 0, 10)
            self.batchLayout.addWidget(QtWidgets.QLabel('Sensitivity'), 0, 11)
            self.batchLayout.addWidget(QtWidgets.QLabel('Time Const'), 0, 12)
            self.batchLayout.addWidget(QtWidgets.QLabel('Wait Time'), 0, 13)
            self.batchLayout.addWidget(QtWidgets.QLabel('Modulation'), 0, 14)
            self.batchLayout.addWidget(QtWidgets.QLabel('Harmonics'), 0, 15)
            self.batchLayout.addWidget(QtWidgets.QLabel('Mod Freq'), 0, 16)
            self.batchLayout.addWidget(QtWidgets.QLabel('Mod Amp'), 0, 17)
            self.batchLayout.addWidget(QtWidgets.QLabel('Phase'), 0, 18)

            for row in range(len(self.entry_settings)):
                current_setting = self.entry_settings[row]
                entry = ui_shared.LWAScanHdEntry(self, entry_setting=current_setting)
                # add entry number checkbox to the button group
                self.previewButtonGroup.addButton(entry.previewCheck, row)
                self.exportLWAButtonGroup.addButton(entry.exportCheck, row)
                # add widgets to the dispaly panel layout
                self.batchLayout.addWidget(entry.previewCheck, row+1, 0)
                self.batchLayout.addWidget(entry.exportCheck, row+1, 1)
                self.batchLayout.addWidget(entry.scanNumLabel, row+1, 2)
                self.batchLayout.addWidget(entry.commentLabel, row+1, 3)
                self.batchLayout.addWidget(entry.dateLabel, row+1, 4)
                self.batchLayout.addWidget(entry.timeLabel, row+1, 5)
                self.batchLayout.addWidget(entry.startFreqLabel, row+1, 6)
                self.batchLayout.addWidget(entry.stopFreqLabel, row+1, 7)
                self.batchLayout.addWidget(entry.stepLabel, row+1, 8)
                self.batchLayout.addWidget(entry.ptsLabel, row+1, 9)
                self.batchLayout.addWidget(entry.avgLabel, row+1, 10)
                self.batchLayout.addWidget(entry.sensLabel, row+1, 11)
                self.batchLayout.addWidget(entry.tcLabel, row+1, 12)
                self.batchLayout.addWidget(entry.itLabel, row+1, 13)
                self.batchLayout.addWidget(entry.modModeLabel, row+1, 14)
                self.batchLayout.addWidget(entry.harmLabel, row+1, 15)
                self.batchLayout.addWidget(entry.modFreqLabel, row+1, 16)
                self.batchLayout.addWidget(entry.modAmpLabel, row+1, 17)
                self.batchLayout.addWidget(entry.phaseLabel, row+1, 18)

            self.batchListWidget.setLayout(self.batchLayout)
            self.mainLayout.addWidget(batchArea)
            self.previewButtonGroup.buttonToggled.connect(self.preview_entry)
            self.exportLWAButtonGroup.buttonClicked[int].connect(self.add_to_export_list)
        else:
            self.mainLayout.addWidget(QtWidgets.QLabel('Invalid file! No scans found.'))

        self.setLayout(self.mainLayout)

    def preview_entry(self):
        """ Preview single scan """

        id_ = self.previewButtonGroup.checkedId()
        preview_data = lwaparser.preview(id_, self.hd_line_num, src=self.filename)
        self.preview_win.setData(preview_data)
        self.preview_win.show()

    def add_to_export_list(self, id_):
        """ Add checked buttons to export list. id_ starts at 0 """

        # if the button is checked, add to export list
        if self.exportLWAButtonGroup.button(id_).isChecked():
            # check if id is already in the list
            if id_ in self.entry_id_to_export:
                pass
            else:
                self.entry_id_to_export.append(id_)
        # if the button is unchecked, remove from export list
        else:
            # check if id is already in the list
            if id_ in self.entry_id_to_export:
                self.entry_id_to_export.remove(id_)
            else:
                pass

    def export_lwa(self):
        """ Export to new lwa file """

        # check if entry_id_to_export list is not empty
        if self.entry_id_to_export:
            output_file, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'Save lwa file', '', 'SMAP File (*.lwa)')
        else:
            d = ui_shared.MsgError(self, 'Empty List!', 'No scan is selected!')
            d.exec()
            output_file = None

        # prevent from overwriting
        if output_file == self.filename:
            msg = ui_shared.MsgError(self, 'Cannot save!',
                             'Output file shall not overwrite source file')
            msg.exec()
        elif output_file:
            lwaparser.export_lwa(list(set(self.entry_id_to_export)), self.hd_line_num, src=self.filename, output=output_file)
        else:
            pass

    def export_xy(self):
        """ Export to xy text file. User can select delimiter """

        # check if entry_id_to_export list is not empty
        if self.entry_id_to_export:
            output_dir = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select directory to save xy files')
        else:
            d = ui_shared.MsgError(self, 'Empty List!', 'No scan is selected!')
            d.exec()
            output_dir = None

        # prevent from overwriting
        if output_dir == self.filename:
            msg = ui_shared.MsgError(self, 'Cannot save!',
                             'Output file shall not overwrite source file')
            msg.exec()
        elif output_dir:
            lwaparser.export_xy(list(set(self.entry_id_to_export)), self.hd_line_num, src=self.filename, output_dir=output_dir)
        else:
            pass

    def open_new_file(self):

        # close this window and delete this instance
        self.close()
        self.deleteLater()
        # launch a new dialog window
        self.parent.on_lwa_parser()

    def reject(self):
        self.preview_win.close()
        self.preview_win.deleteLater()
        self.close()
        self.deleteLater()


class PrevSpectrumDialog(QtWidgets.QDialog):
    """ Preview dialog window for spectrum """

    def __init__(self, parent, data=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.parent = parent
        self._data = data
        self.setWindowTitle('Spectrum Preview')
        self.setMinimumWidth(750)
        self.setMinimumHeight(450)

        self.pgPlot = pg.PlotWidget(self, title='Spectrum Preview')
        self.pgPlot.setLabel('left', text='Intensity', units='V')
        self.pgPlot.setLabel('bottom', text='Frequency', units='Hz')
        self.curve = self.pgPlot.plot()

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        mainLayout.addWidget(self.pgPlot)
        self.setLayout(mainLayout)

    def setData(self, data):
        self._data = data
        self.curve.setData(self._data[:,0], self._data[:,1])


class DialogGauge(QtWidgets.QDialog):
    """
        Pressure reader window
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle('CENTER TWO pressure reader')
        self.setMinimumSize(900, 600)
        self.setModal(False)

        # add left column widigets
        # this is a monitor panel for realtime readings
        rtMonitor = QtWidgets.QGroupBox(self)
        rtMonitor.setTitle('Readtime Monitor')
        self.currentP = QtWidgets.QLabel()
        self.currentUnit = QtWidgets.QLabel()
        self.currentChannel = QtWidgets.QLabel('1')
        self.currentStatus = QtWidgets.QLabel()
        monitorLayout = QtWidgets.QGridLayout()
        monitorLayout.addWidget(QtWidgets.QLabel('Channel'), 0, 0)
        monitorLayout.addWidget(QtWidgets.QLabel('Status'), 0, 1)
        monitorLayout.addWidget(QtWidgets.QLabel('Pressure'), 2, 0)
        monitorLayout.addWidget(QtWidgets.QLabel('Unit'), 2, 1)
        monitorLayout.addWidget(self.currentChannel, 1, 0)
        monitorLayout.addWidget(self.currentStatus, 1, 1)
        monitorLayout.addWidget(self.currentP, 3, 0)
        monitorLayout.addWidget(self.currentUnit, 3, 1)
        rtMonitor.setLayout(monitorLayout)

        # this is a mini control panel for the readout
        rdCtrl = QtWidgets.QGroupBox(self)
        rdCtrl.setTitle('Readout Control')
        self.channelSel = QtWidgets.QComboBox()
        self.channelSel.addItems(['1', '2'])
        self.current_chn_index = 0
        self.pUnitSel = QtWidgets.QComboBox()
        self.pUnitSel.addItems(['mBar', 'Torr', 'Pascal', 'μmHg'])
        self.pUnitSel.setCurrentIndex(1)    # default unit Torr
        self.currentUnit.setText('Torr')    # default unit Torr
        self.current_p_unit_index = 1       # store this for unit protection
        rdCtrlLayout = QtWidgets.QFormLayout()
        rdCtrlLayout.addRow(QtWidgets.QLabel('Select Channel'), self.channelSel)
        rdCtrlLayout.addRow(QtWidgets.QLabel('Select Pressure Unit'), self.pUnitSel)
        rdCtrl.setLayout(rdCtrlLayout)

        # this is to select the data update rate, cannot be quicker than /0.1 s
        rateSelect = QtWidgets.QWidget()
        self.updateRate = QtWidgets.QLineEdit()
        self.updateRate.setText('1')
        self.updateRateUnitSel = QtWidgets.QComboBox()
        self.updateRateUnitSel.addItems(['sec', 'min', 'h'])
        self.updateRateUnitSel.setCurrentIndex(0)
        self.current_update_unit_index = 0      # store this for unit protection
        rateSelectLayout = QtWidgets.QHBoxLayout(self)
        rateSelectLayout.addWidget(QtWidgets.QLabel('Update Rate'))
        rateSelectLayout.addWidget(self.updateRate)
        rateSelectLayout.addWidget(QtWidgets.QLabel(' per '))
        rateSelectLayout.addWidget(self.updateRateUnitSel)
        rateSelect.setLayout(rateSelectLayout)

        # putting stuff together in the left column
        leftColumnLayout = QtWidgets.QVBoxLayout(self)
        leftColumnLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        leftColumnLayout.addWidget(rtMonitor)
        leftColumnLayout.addWidget(rdCtrl)
        leftColumnLayout.addWidget(rateSelect)

        # add right colun widgets
        self.startButton = QtWidgets.QPushButton('(Re)Start')
        self.stopButton = QtWidgets.QPushButton('Stop')
        self.saveButton = QtWidgets.QPushButton('Save')
        self.savepButton = QtWidgets.QPushButton('Save and Continue')
        panelLayout = QtWidgets.QHBoxLayout()
        panelLayout.addWidget(self.startButton)
        panelLayout.addWidget(self.stopButton)
        panelLayout.addWidget(self.saveButton)
        panelLayout.addWidget(self.savepButton)

        # initiate pyqtgraph widget
        self.pgPlot = pg.PlotWidget(title='Pressure Monitor')
        self.pgPlot.setLabel('left', text='Pressure', units='Torr')
        self.pgPlot.setLabel('bottom', text='Time', units='sec')
        self.pgPlot.setLogMode(x=None, y=True)
        self.pgPlot.showGrid(x=True, y=True, alpha=0.5)
        self.curve = pg.PlotCurveItem()
        self.pgPlot.addItem(self.curve)
        rightColumnLayout = QtWidgets.QVBoxLayout()
        rightColumnLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        rightColumnLayout.addWidget(self.pgPlot)
        rightColumnLayout.addLayout(panelLayout)

        # Set up main layout
        mainLayout = QtWidgets.QHBoxLayout(self)
        mainLayout.setSpacing(0)
        mainLayout.addLayout(leftColumnLayout)
        mainLayout.addLayout(rightColumnLayout)
        self.setLayout(mainLayout)

    def set_label(self, axis, name, unit):
        self.pgPlot.setLabel(axis, text=name, units=unit)

    def plot(self, data):
        self.curve.setData(data)
