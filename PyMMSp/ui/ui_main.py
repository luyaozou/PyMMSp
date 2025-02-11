#! encoding = utf-8
""" GUI Panels. """

import numpy as np
import pyqtgraph as pg
# import standard libraries
from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import Qt

# import instrument inst
from PyMMSp.inst import lockin as api_lia
from PyMMSp.inst import oscillo as api_oscillo
from PyMMSp.inst import synthesizer as api_syn
from PyMMSp.inst import validator as api_val
# import shared ui widgets
from PyMMSp.ui import ui_dialog
from PyMMSp.ui import ui_shared
from PyMMSp.ui import ui_daq


NUM_MONITORS = 6        # number of monitors. later this should be moved to config file


class MainUI(QtWidgets.QWidget):
    """ Main UI Widget """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.synPanel = SynPanel(self)
        # self.lockinPanel = LockinPanel(self)
        # self.oscilloPanel = OscilloPanel(self)
        # self.awgPanel = AWGPanel(self)
        # self.powerPanel = PowerSupplyPanel(self)
        # self.flowPanel = FlowCtrlPanel(self)
        # self.gaugePanel = GaugePanel(self)
        # self.motorPanel = MotorPanel(self)
        self.lockinPanel = GeneralCtrlPanel('Lock-in Control', parent=self)
        self.oscilloPanel = GeneralCtrlPanel('Oscilloscope Control', parent=self)
        self.awgPanel = GeneralCtrlPanel('AWG Control', parent=self)
        self.dcPanel = GeneralCtrlPanel('Power Supply Control', parent=self)
        self.flowPanel = GeneralCtrlPanel('Gas Flow Control', parent=self)
        self.gaugePanel = GeneralCtrlPanel('Gauge Control', parent=self)
        self.motorPanel = GeneralCtrlPanel('Motor Control', parent=self)

        self._monitors = tuple(Monitor(self) for _ in range(NUM_MONITORS))

        self.dAbsScan = ui_daq.DialogAbsScan(self)
        self.dAbsConfig = ui_daq.DialogAbsConfig(self)

        panelLayout = QtWidgets.QVBoxLayout()
        panelLayout.setSpacing(3)
        panelLayout.addWidget(self.synPanel)
        panelLayout.addWidget(self.lockinPanel)
        panelLayout.addWidget(self.oscilloPanel)
        panelLayout.addWidget(self.awgPanel)
        panelLayout.addWidget(self.dcPanel)
        panelLayout.addWidget(self.flowPanel)
        panelLayout.addWidget(self.gaugePanel)
        panelLayout.addWidget(self.motorPanel)

        canvasLayout = QtWidgets.QGridLayout()
        canvasLayout.setSpacing(3)
        canvasLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        for i, monitor in enumerate(self._monitors):
            canvasLayout.addWidget(monitor, i // 2, i % 2)

        mainLayout = QtWidgets.QHBoxLayout()
        mainLayout.setSpacing(6)
        mainLayout.addLayout(panelLayout)
        mainLayout.addLayout(canvasLayout)

        self.setLayout(mainLayout)

        self.msgErr = ui_shared.MsgError(self, 'Error')
        self.msgWarn = ui_shared.MsgWarning(self, 'Warning')
        self.msgInfo = ui_shared.MsgInfo(self, 'Info')

        self.dConnInst = ui_dialog.DialogConnInst(self)
        self.dSyn = ui_dialog.DialogSyn(self)
        self.dLockin = ui_dialog.DialogLockin(self)
        self.dOscillo = ui_dialog.DialogOscillo(self)
        self.dGauge = ui_dialog.DialogGauge(self)
        self.dFlow = ui_dialog.DialogFlow(self)
        self.dGCF = ui_dialog.DialogGCF(self)
        self.dAWG = ui_dialog.DialogAWG(self)
        self.dPowerSupp = ui_dialog.DialogPowerSupp(self)
        self.dCloseInst = ui_dialog.DialogCloseInst(self)

        self.synPanel.btnConfig.clicked.connect(self.dSyn.show)
        self.lockinPanel.btnConfig.clicked.connect(self.dLockin.show)
        self.oscilloPanel.btnConfig.clicked.connect(self.dOscillo.show)
        self.awgPanel.btnConfig.clicked.connect(self.dAWG.show)
        self.dcPanel.btnConfig.clicked.connect(self.dPowerSupp.show)
        self.flowPanel.btnConfig.clicked.connect(self.dFlow.show)
        self.gaugePanel.btnConfig.clicked.connect(self.dGauge.show)


    def get_monitor(self, i):
        # return the i-th monitor
        return self._monitors[i]


class SynStatus(QtWidgets.QGroupBox):
    """
        Synthesizer status display
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle('Synthesizer Status')
        self.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.setCheckable(True)
        self.setChecked(False)

        ## -- Define synthesizer status elements --
        self.refreshButton = QtWidgets.QPushButton('Manual Refresh')
        self.moreInfoButton = QtWidgets.QPushButton('More Info')
        self.addressText = QtWidgets.QLabel()
        self.synRF = QtWidgets.QLabel()
        self.synPower = QtWidgets.QLabel()
        self.synFreq = QtWidgets.QLabel()
        self.synMod = QtWidgets.QLabel()
        self.synAMStat = QtWidgets.QLabel()
        self.synFMStat = QtWidgets.QLabel()
        self.synAMDepth = QtWidgets.QLabel()
        self.synAMFreq = QtWidgets.QLabel()
        self.synFMDev = QtWidgets.QLabel()
        self.synFMFreq = QtWidgets.QLabel()
        self.synLF = QtWidgets.QLabel()
        self.synLFV = QtWidgets.QLabel()
        self.errMsgLabel = QtWidgets.QLabel()
        self.errMsgBtn = QtWidgets.QPushButton('Pop Err Msg')

        # put modulation settings in a groupbox
        modGroup = QtWidgets.QGroupBox()
        modGroup.setTitle('Modulation Settings')
        modGroup.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        modGroup.setCheckable(False)
        modGroupLayout = QtWidgets.QGridLayout()
        modGroupLayout.addWidget(QtWidgets.QLabel('AM1'), 0, 1)
        modGroupLayout.addWidget(QtWidgets.QLabel('FM1'), 0, 2)
        modGroupLayout.addWidget(QtWidgets.QLabel('Status'), 1, 0)
        modGroupLayout.addWidget(self.synAMStat, 1, 1)
        modGroupLayout.addWidget(self.synFMStat, 1, 2)
        modGroupLayout.addWidget(QtWidgets.QLabel('Freq'), 2, 0)
        modGroupLayout.addWidget(self.synAMFreq, 2, 1)
        modGroupLayout.addWidget(self.synFMFreq, 2, 2)
        modGroupLayout.addWidget(QtWidgets.QLabel('Depth|Dev'), 3, 0)
        modGroupLayout.addWidget(self.synAMDepth, 3, 1)
        modGroupLayout.addWidget(self.synFMDev, 3, 2)
        modGroup.setLayout(modGroupLayout)

        ## -- Set layout and add GUI elements
        mainLayout = QtWidgets.QGridLayout()
        mainLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        # top buttons
        mainLayout.addWidget(self.refreshButton, 0, 0, 1, 2)
        mainLayout.addWidget(self.moreInfoButton, 0, 2, 1, 2)
        mainLayout.addWidget(QtWidgets.QLabel('Inst. Name'), 1, 0)
        mainLayout.addWidget(self.addressText, 1, 1, 1, 3)
        # RF & LF settings
        mainLayout.addWidget(QtWidgets.QLabel('RF Freq'), 2, 0)
        mainLayout.addWidget(self.synFreq, 2, 1, 1, 3)
        mainLayout.addWidget(QtWidgets.QLabel('RF Output'), 3, 0)
        mainLayout.addWidget(self.synRF, 3, 1)
        mainLayout.addWidget(QtWidgets.QLabel('Power'), 3, 2)
        mainLayout.addWidget(self.synPower, 3, 3)
        mainLayout.addWidget(QtWidgets.QLabel('LF Output'), 4, 0)
        mainLayout.addWidget(self.synLF, 4, 1)
        mainLayout.addWidget(QtWidgets.QLabel('LF Voltage'), 4, 2)
        mainLayout.addWidget(self.synLFV, 4, 3)
        mainLayout.addWidget(QtWidgets.QLabel('Modulation'), 5, 0)
        mainLayout.addWidget(self.synMod, 5, 1)
        # Modulation setting group
        mainLayout.addWidget(modGroup, 6, 0, 3, 4)
        mainLayout.addWidget(self.errMsgBtn, 9, 0)
        mainLayout.addWidget(self.errMsgLabel, 9, 1, 1, 3)
        self.setLayout(mainLayout)

        # initial status
        # self.print_info()

    def print_info(self, syn_info):
        """ Print instrument information in this panel """

        self.addressText.setText(syn_info.inst_name)
        self.synRF.setText('On' if syn_info.pow_stat else 'Off')
        self.synPower.setText('{:.1f} dbm'.format(syn_info.syn_power))
        self.synFreq.setText(pg.siFormat(syn_info.syn_freq, suffix='Hz', precision=12))
        self.synMod.setText('On' if syn_info.modu_toggle else 'Off')
        self.synAMStat.setText('On' if syn_info.am1_toggle else 'Off')
        self.synFMStat.setText('On' if syn_info.fm1_toggle else 'Off')
        self.synAMDepth.setText('{:.1f}%'.format(syn_info.am1_depth_pct))
        self.synAMFreq.setText(pg.siFormat(syn_info.am1_freq, suffix='Hz', precision=4))
        self.synFMDev.setText(pg.siFormat(syn_info.fm1_dev, suffix='Hz', precision=4))
        self.synFMFreq.setText(pg.siFormat(syn_info.fm1_freq, suffix='Hz', precision=4))
        self.synLF.setText('On' if syn_info.lf_toggle else 'Off')
        self.synLFV.setText(pg.siFormat(syn_info.lf_vol, suffix='V'))
        self.errMsgLabel.setText(syn_info.err_msg)


class LiaStatus(QtWidgets.QGroupBox):
    """
        Lockin status display
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle('Lockin Status')
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self.setCheckable(True)
        self.setChecked(False)

        ## -- Define synthesizer status elements --
        self.refreshButton = QtWidgets.QPushButton('Manual Refresh')
        self.moreInfoButton = QtWidgets.QPushButton('More Info')
        self.errMsgBtn = QtWidgets.QPushButton('Pop Err Msg')
        self.addressText = QtWidgets.QLabel()
        self.liaHarmLabel = QtWidgets.QLabel()
        self.liaPhaseLabel = QtWidgets.QLabel()
        self.liaFreqLabel = QtWidgets.QLabel()
        self.liaSensLabel = QtWidgets.QLabel()
        self.liaTCLabel = QtWidgets.QLabel()
        self.liaCoupleLabel = QtWidgets.QLabel()
        self.liaReserveLabel = QtWidgets.QLabel()
        self.liaGroundingLabel = QtWidgets.QLabel()
        self.liaFilterLabel = QtWidgets.QLabel()
        self.liaRefSrcLabel = QtWidgets.QLabel()
        self.errMsgLabel = QtWidgets.QLabel('N.A.')

        ## -- Set layout and add GUI elements
        mainLayout = QtWidgets.QGridLayout()
        mainLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        # first column
        mainLayout.addWidget(self.refreshButton, 0, 0, 1, 2)
        mainLayout.addWidget(self.moreInfoButton, 0, 2, 1, 2)
        mainLayout.addWidget(QtWidgets.QLabel('Inst. Name'), 1, 0)
        mainLayout.addWidget(self.addressText, 1, 1, 1, 3)
        mainLayout.addWidget(QtWidgets.QLabel('Harmonics'), 2, 0)
        mainLayout.addWidget(self.liaHarmLabel, 2, 1)
        mainLayout.addWidget(QtWidgets.QLabel('Phase (Deg)'), 3, 0)
        mainLayout.addWidget(self.liaPhaseLabel, 3, 1)
        mainLayout.addWidget(QtWidgets.QLabel('Sensitivity'), 4, 0)
        mainLayout.addWidget(self.liaSensLabel, 4, 1)
        mainLayout.addWidget(QtWidgets.QLabel('Time Const'), 5, 0)
        mainLayout.addWidget(self.liaTCLabel, 5, 1)
        mainLayout.addWidget(QtWidgets.QLabel('Ref Source'), 6, 0)
        mainLayout.addWidget(self.liaRefSrcLabel, 6, 1)
        mainLayout.addWidget(self.errMsgBtn, 7, 0)
        mainLayout.addWidget(self.errMsgLabel, 7, 1, 1, 3)
        # second column
        mainLayout.addWidget(QtWidgets.QLabel('Couple'), 2, 2)
        mainLayout.addWidget(self.liaCoupleLabel, 2, 3)
        mainLayout.addWidget(QtWidgets.QLabel('Reserve'), 3, 2)
        mainLayout.addWidget(self.liaReserveLabel, 3, 3)
        mainLayout.addWidget(QtWidgets.QLabel('Grouding'), 4, 2)
        mainLayout.addWidget(self.liaGroundingLabel, 4, 3)
        mainLayout.addWidget(QtWidgets.QLabel('Filter'), 5, 2)
        mainLayout.addWidget(self.liaFilterLabel, 5, 3)
        mainLayout.addWidget(QtWidgets.QLabel('Locked Freq'), 6, 2)
        mainLayout.addWidget(self.liaFreqLabel, 6, 3)
        self.setLayout(mainLayout)

    def print_info(self, info):
        """ Print instrument information in this panel """

        self.addressText.setText(info.inst_name)
        self.liaHarmLabel.setText(info.ref_harm_txt)
        self.liaPhaseLabel.setText('{:.2f}'.format(info.ref_phase))
        self.liaSensLabel.setText(info.sens_txt)
        self.liaTCLabel.setText(info.tau_txt)
        self.liaFreqLabel.setText(pg.siFormat(info.ref_freq, suffix='Hz'))
        self.liaCoupleLabel.setText(info.couple_txt)
        self.liaReserveLabel.setText(info.reserve_txt)
        self.liaGroundingLabel.setText(info.gnd_txt)
        self.liaFilterLabel.setText(info.input_filter_txt)
        self.liaRefSrcLabel.setText(info.ref_src_txt)


class ScopeStatus(QtWidgets.QGroupBox):
    """
        Oscilloscope (PCI card) status display
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle('Oscilloscope Status')
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self.setCheckable(True)
        self.setChecked(False)

        ## -- Define synthesizer status elements --
        self.refreshButton = QtWidgets.QPushButton('Manual Refresh')
        self.moreInfoButton = QtWidgets.QPushButton('More Info')
        self.addressText = QtWidgets.QLabel()

        ## -- Set layout and add GUI elements
        mainLayout = QtWidgets.QGridLayout()
        mainLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        mainLayout.addWidget(self.refreshButton, 0, 0, 1, 2)
        mainLayout.addWidget(self.moreInfoButton, 0, 2, 1, 2)
        mainLayout.addWidget(QtWidgets.QLabel('Inst. Name'), 1, 0)
        mainLayout.addWidget(self.addressText, 1, 1)
        self.setLayout(mainLayout)

    def print_info(self, info):
        self.addressText.setText(info.inst_name)


class SynPanel(QtWidgets.QGroupBox):
    """
        Synthesizer control panel
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle('Synthesizer Control')
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)  # align left

        self.inpHarm = ui_shared.create_int_spin_box(1, 1, 108)
        self.inpFreq = ui_shared.create_double_spin_box(1e5, 0, dec=3)
        self.lblRFFreq = QtWidgets.QLabel()

        # -- Set up basic synthesizer info layout --
        synLayout = QtWidgets.QGridLayout()
        synLayout.addWidget(QtWidgets.QLabel('Harmonics'), 0, 0)
        synLayout.addWidget(self.inpHarm, 0, 1, 1, 2)
        synLayout.addWidget(QtWidgets.QLabel('Frequency'), 1, 0)
        synLayout.addWidget(self.inpFreq, 1, 1, 1, 2)
        synLayout.addWidget(QtWidgets.QLabel('RF Freq'), 2, 0)
        synLayout.addWidget(self.lblRFFreq, 2, 1, 1, 2)

        # -- Define synthesizer power switch --
        self.synPowerSwitchBtn = QtWidgets.QPushButton('OFF')
        self.synPowerSwitchBtn.setCheckable(True)
        self.synPowerManualInput = QtWidgets.QPushButton('Set Power')

        synPowerLayout = QtWidgets.QHBoxLayout()
        synPowerLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        synPowerLayout.addWidget(self.synPowerManualInput)
        synPowerLayout.addWidget(QtWidgets.QLabel('RF Switch'))
        synPowerLayout.addWidget(self.synPowerSwitchBtn)

        # -- Define buttons --
        self.statusBulb = ui_shared.CommStatusBulb()
        self.btnConfig = QtWidgets.QPushButton('Configure')
        self.comboMonitor = QtWidgets.QComboBox()
        self.comboMonitor.addItems(list(f'Monitor {i+1}' for i in range(NUM_MONITORS)))
        btnLayout = QtWidgets.QHBoxLayout()
        btnLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        btnLayout.addWidget(self.statusBulb)
        btnLayout.addWidget(QtWidgets.QLabel('Connect to '))
        btnLayout.addWidget(self.comboMonitor)
        btnLayout.addWidget(self.btnConfig)

        # -- Set up main layout
        thisLayout = QtWidgets.QVBoxLayout()
        thisLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        thisLayout.addLayout(synPowerLayout)
        thisLayout.addLayout(synLayout)
        thisLayout.addLayout(btnLayout)
        self.setLayout(thisLayout)

        ## -- depreciate codes below ---

        ## -- Define synthesizer control elements --
        self.probFreqFill = QtWidgets.QLineEdit()
        self.probFreqFill.setText('180000')
        self.bandSel = QtWidgets.QComboBox()
        self.bandSel.addItems(list(txt for txt in api_syn.yield_band_str()))

        # Set up modulation child widget
        modGBox = QtWidgets.QGroupBox()
        modGBox.setTitle('Modulation Control')
        modGBox.setFlat(True)
        modGBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        modLayout = QtWidgets.QGridLayout()
        modLayout.setSpacing(0)

        self.modModeSel = QtWidgets.QComboBox()
        self.modModeSel.addItems(list(api_syn.MODU_MODE))

        self.modFreq = QtWidgets.QWidget()
        self.modFreqFill = QtWidgets.QLineEdit('0')
        self.modFreqUnitSel = QtWidgets.QComboBox()
        self.modFreqUnitSel.addItems(['Hz', 'kHz'])
        self.modFreqUnitSel.setCurrentIndex(1)
        modFreqLayout = QtWidgets.QHBoxLayout()
        modFreqLayout.addWidget(QtWidgets.QLabel('Mod Freq'))
        modFreqLayout.addWidget(self.modFreqFill)
        modFreqLayout.addWidget(self.modFreqUnitSel)
        self.modFreq.setLayout(modFreqLayout)

        self.modAmp = QtWidgets.QWidget()
        self.modAmpLabel = QtWidgets.QLabel()
        self.modAmpFill = QtWidgets.QLineEdit('0')
        self.modAmpAMUnitSel = QtWidgets.QComboBox()
        self.modAmpAMUnitSel.addItems(['%'])
        self.modAmpFMUnitSel = QtWidgets.QComboBox()
        self.modAmpFMUnitSel.addItems(['Hz', 'kHz', 'MHz'])
        self.modAmpFMUnitSel.setCurrentIndex(1)
        modAmpLayout = QtWidgets.QHBoxLayout()
        modAmpLayout.addWidget(self.modAmpLabel)
        modAmpLayout.addWidget(self.modAmpFill)
        modAmpLayout.addWidget(self.modAmpAMUnitSel)
        modAmpLayout.addWidget(self.modAmpFMUnitSel)
        self.modAmp.setLayout(modAmpLayout)

        self.lfVol = QtWidgets.QWidget()
        self.lfVolFill = QtWidgets.QLineEdit('0')
        lfLayout = QtWidgets.QHBoxLayout()
        lfLayout.addWidget(QtWidgets.QLabel('LF Voltage'))
        lfLayout.addWidget(self.lfVolFill)
        lfLayout.addWidget(QtWidgets.QLabel('V'))
        self.lfVol.setLayout(lfLayout)

        self.modSwitchBtn = QtWidgets.QPushButton('OFF')
        self.modSwitchBtn.setCheckable(True)
        self.lfSwitchBtn = QtWidgets.QPushButton('OFF')
        self.lfSwitchBtn.setCheckable(True)

        modLayout.addWidget(QtWidgets.QLabel('Mod Mode'), 0, 0)
        modLayout.addWidget(QtWidgets.QLabel('Mod Switch'), 1, 0)
        modLayout.addWidget(QtWidgets.QLabel('LF Switch'), 2, 0)
        modLayout.addWidget(self.modModeSel, 0, 1)
        modLayout.addWidget(self.modSwitchBtn, 1, 1)
        modLayout.addWidget(self.lfSwitchBtn, 2, 1)
        modLayout.addWidget(self.modFreq, 0, 2, 1, 3)
        modLayout.addWidget(self.modAmp, 1, 2, 1, 3)
        modLayout.addWidget(self.lfVol, 2, 2, 1, 3)
        modGBox.setLayout(modLayout)
        self.modFreq.hide()
        self.modAmp.hide()
        self.lfVol.hide()

    def print_info(self, info):
        self.synPowerSwitchBtn.setChecked(info.pow_stat)
        self.probFreqFill.setText(f'{info.freq * 1e-6:.9f}')
        self.modSwitchBtn.setChecked(info.modu_toggle)
        self.modSwitchBtn.setText('ON' if info.modu_toggle else 'OFF')
        if info.am1_toggle and (not info.fm1_toggle):
            self.modModeSel.setCurrentIndex(1)
            self.modFreqFill.setText(f'{info.am1_freq * 1e-3:.1f}')
            self.modFreqUnitSel.setCurrentIndex(1)
            self.modAmpFill.setText(f'{info.am1_depth_pct:.1f}')
            self.modAmpAMUnitSel.setCurrentIndex(0)
        elif (not info.am1_toggle) and info.FM1Toggle:
            self.modModeSel.setCurrentIndex(2)
            self.modFreqFill.setText(f'{info.fm1_toggle * 1e-3:.1f}')
            self.modFreqUnitSel.setCurrentIndex(1)
            self.modAmpFill.setText(f'{info.fm1_dev * 1e-3:.1f}')
            self.modAmpFMUnitSel.setCurrentIndex(1)
        else:
            self.modModeSel.setCurrentIndex(0)
        self.lfSwitchBtn.setChecked(info.lf_toggle)
        self.lfSwitchBtn.setText('ON' if info.lf_toggle else 'OFF')
        self.lfVolFill.setText(f'{info.lf_vol:.3f}')


class GeneralCtrlPanel(QtWidgets.QGroupBox):

    def __init__(self, title, parent=None):
        super().__init__(parent)

        self.setTitle(title)
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)  # align left

        self.statusBulb = ui_shared.CommStatusBulb()
        self.btnConfig = QtWidgets.QPushButton('Configure')
        self.comboMonitor = QtWidgets.QComboBox()
        self.comboMonitor.addItems(list(f'Monitor {i + 1}' for i in range(NUM_MONITORS)))
        btnLayout = QtWidgets.QHBoxLayout()
        btnLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        btnLayout.addWidget(self.statusBulb)
        btnLayout.addWidget(QtWidgets.QLabel('Connect to '))
        btnLayout.addWidget(self.comboMonitor)
        btnLayout.addWidget(self.btnConfig)

        thisLayout = QtWidgets.QVBoxLayout()
        thisLayout.addLayout(btnLayout)
        self.setLayout(thisLayout)


class LockinPanel(QtWidgets.QGroupBox):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle('Lockin Control')
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)  # align left
        self.setCheckable(True)
        self.setChecked(False)

        self.comboSens = QtWidgets.QComboBox()
        self.comboSens.addItems(api_lia.SENS_STR)
        self.comboTau = QtWidgets.QComboBox()
        self.comboTau.addItems(api_lia.TAU_STR)
        widgetLayout = QtWidgets.QHBoxLayout()
        widgetLayout.addWidget(QtWidgets.QLabel('Sensitivity'))
        widgetLayout.addWidget(self.comboSens)
        widgetLayout.addWidget(QtWidgets.QLabel('Time Const'))
        widgetLayout.addWidget(self.comboTau)

        # -- Define buttons --
        self.btnConfig = QtWidgets.QPushButton('Configure')
        self.comboMonitor = QtWidgets.QComboBox()
        self.comboMonitor.addItems(list(f'Monitor {i + 1}' for i in range(NUM_MONITORS)))
        btnLayout = QtWidgets.QHBoxLayout()
        btnLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        btnLayout.addWidget(QtWidgets.QLabel('Connect to '))
        btnLayout.addWidget(self.comboMonitor)
        btnLayout.addWidget(self.btnConfig)

        thisLayout = QtWidgets.QVBoxLayout()
        thisLayout.addLayout(widgetLayout)
        thisLayout.addLayout(btnLayout)
        self.setLayout(thisLayout)

        # depreciate codes below
        ## -- Define layout elements --
        self.harmSel = QtWidgets.QComboBox()
        self.harmSel.addItems(['1', '2', '3', '4'])
        self.harmSel.setCurrentIndex(0)
        self.phaseFill = QtWidgets.QLineEdit('0')
        self.coupleSel = QtWidgets.QComboBox()
        self.coupleSel.addItems(list(api_lia.COUPLE))
        self.coupleSel.setCurrentIndex(1)
        self.reserveSel = QtWidgets.QComboBox()
        self.reserveSel.addItems(list(api_lia.RESERVE))
        self.reserveSel.setCurrentIndex(1)
        self.groundingSel = QtWidgets.QComboBox()
        self.groundingSel.addItems(list(api_lia.GND))
        self.groundingSel.setCurrentIndex(1)
        self.filterSel = QtWidgets.QComboBox()
        self.filterSel.addItems(list(api_lia.FILTER))
        self.filterSel.setCurrentIndex(1)
        self.autoPhaseBtn = QtWidgets.QPushButton('Auto Phase')
        self.resetBtn = QtWidgets.QPushButton('Reset')


class OscilloPanel(QtWidgets.QGroupBox):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle('Oscilloscope Control')
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self.setCheckable(True)
        self.setChecked(False)

        self.comboSens = QtWidgets.QComboBox()
        self.comboSens.addItems(api_lia.SENS_STR)
        self.inpRate = ui_shared.create_double_spin_box(1, dec=3, suffix=' kHz')
        widgetLayout = QtWidgets.QHBoxLayout()
        widgetLayout.addWidget(QtWidgets.QLabel('Sensitivity'))
        widgetLayout.addWidget(self.comboSens)
        widgetLayout.addWidget(QtWidgets.QLabel('Sample Rate'))
        widgetLayout.addWidget(self.inpRate)

        # -- Define buttons --
        self.btnConfig = QtWidgets.QPushButton('Configure')
        self.comboMonitor = QtWidgets.QComboBox()
        self.comboMonitor.addItems(list(f'Monitor {i + 1}' for i in range(NUM_MONITORS)))
        btnLayout = QtWidgets.QHBoxLayout()
        btnLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        btnLayout.addWidget(QtWidgets.QLabel('Connect to '))
        btnLayout.addWidget(self.comboMonitor)
        btnLayout.addWidget(self.btnConfig)

        thisLayout = QtWidgets.QVBoxLayout()
        thisLayout.addLayout(widgetLayout)
        thisLayout.addLayout(btnLayout)
        self.setLayout(thisLayout)


class MotorPanel(QtWidgets.QGroupBox):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle('Motor Control')
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self.setCheckable(True)
        self.setChecked(False)

        thisLayout = QtWidgets.QHBoxLayout()
        self.setLayout(thisLayout)


class AWGPanel(QtWidgets.QGroupBox):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle('AWG Control')
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self.setCheckable(True)
        self.setChecked(False)

        widgetLayout = QtWidgets.QHBoxLayout()

        # -- Define buttons --
        self.btnConfig = QtWidgets.QPushButton('Configure')
        self.comboMonitor = QtWidgets.QComboBox()
        self.comboMonitor.addItems(list(f'Monitor {i + 1}' for i in range(NUM_MONITORS)))
        btnLayout = QtWidgets.QHBoxLayout()
        btnLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        btnLayout.addWidget(QtWidgets.QLabel('Connect to '))
        btnLayout.addWidget(self.comboMonitor)
        btnLayout.addWidget(self.btnConfig)

        thisLayout = QtWidgets.QVBoxLayout()
        thisLayout.addLayout(widgetLayout)
        thisLayout.addLayout(btnLayout)
        self.setLayout(thisLayout)


class PowerSupplyPanel(QtWidgets.QGroupBox):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle('Power Supply Control')
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self.setCheckable(True)
        self.setChecked(False)

        widgetLayout = QtWidgets.QHBoxLayout()

        # -- Define buttons --
        self.btnConfig = QtWidgets.QPushButton('Configure')
        self.comboMonitor = QtWidgets.QComboBox()
        self.comboMonitor.addItems(list(f'Monitor {i + 1}' for i in range(NUM_MONITORS)))
        btnLayout = QtWidgets.QHBoxLayout()
        btnLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        btnLayout.addWidget(QtWidgets.QLabel('Connect to '))
        btnLayout.addWidget(self.comboMonitor)
        btnLayout.addWidget(self.btnConfig)

        thisLayout = QtWidgets.QVBoxLayout()
        thisLayout.addLayout(widgetLayout)
        thisLayout.addLayout(btnLayout)
        self.setLayout(thisLayout)


class FlowCtrlPanel(QtWidgets.QGroupBox):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle('Flow Control')
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self.setCheckable(True)
        self.setChecked(False)

        widgetLayout = QtWidgets.QHBoxLayout()

        # -- Define buttons --
        self.btnConfig = QtWidgets.QPushButton('Configure')
        self.comboMonitor = QtWidgets.QComboBox()
        self.comboMonitor.addItems(list(f'Monitor {i + 1}' for i in range(NUM_MONITORS)))
        btnLayout = QtWidgets.QHBoxLayout()
        btnLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        btnLayout.addWidget(QtWidgets.QLabel('Connect to '))
        btnLayout.addWidget(self.comboMonitor)
        btnLayout.addWidget(self.btnConfig)

        thisLayout = QtWidgets.QVBoxLayout()
        thisLayout.addLayout(widgetLayout)
        thisLayout.addLayout(btnLayout)
        self.setLayout(thisLayout)


class GaugePanel(QtWidgets.QGroupBox):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle('Gauge Control')
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self.setCheckable(True)
        self.setChecked(False)

        widgetLayout = QtWidgets.QHBoxLayout()

        # -- Define buttons --
        self.btnConfig = QtWidgets.QPushButton('Configure')
        self.comboMonitor = QtWidgets.QComboBox()
        self.comboMonitor.addItems(list(f'Monitor {i + 1}' for i in range(NUM_MONITORS)))
        btnLayout = QtWidgets.QHBoxLayout()
        btnLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        btnLayout.addWidget(QtWidgets.QLabel('Connect to '))
        btnLayout.addWidget(self.comboMonitor)
        btnLayout.addWidget(self.btnConfig)

        thisLayout = QtWidgets.QVBoxLayout()
        thisLayout.addLayout(widgetLayout)
        thisLayout.addLayout(btnLayout)
        self.setLayout(thisLayout)


class Monitor(QtWidgets.QGroupBox):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.pgPlot = pg.PlotWidget()
        self.curve = pg.PlotCurveItem()
        self.pgPlot.addItem(self.curve)

        self.comboXRange = QtWidgets.QComboBox()
        self.comboXRange.addItems(['Auto', 'Fix'])
        self.comboYRange = QtWidgets.QComboBox()
        self.comboYRange.addItems(['Auto', 'Fix'])
        self.comboRate = QtWidgets.QComboBox()
        self.comboRate.addItems(['10 Hz', '5 Hz', '2 Hz', '1 Hz', '0.5 Hz', '0.2 Hz', '0.1 Hz'])
        self.comboRate.setCurrentIndex(3)
        self.inpXLen = ui_shared.create_int_spin_box(100, minimum=1)
        self.inpXLen.setFixedWidth(200)
        self.btnStart = QtWidgets.QPushButton('Start')
        self.btnStart.setCheckable(True)
        self.btnRestart = QtWidgets.QPushButton('Restart')
        self.btnStop = QtWidgets.QPushButton('Stop')
        panelLayout1 = QtWidgets.QHBoxLayout()
        panelLayout1.addWidget(QtWidgets.QLabel('X Range'))
        panelLayout1.addWidget(self.comboXRange)
        panelLayout1.addWidget(QtWidgets.QLabel('Y Range'))
        panelLayout1.addWidget(self.comboYRange)
        panelLayout1.addWidget(QtWidgets.QLabel('X Points'))
        panelLayout1.addWidget(self.inpXLen)
        panelLayout2 = QtWidgets.QHBoxLayout()
        panelLayout2.addWidget(QtWidgets.QLabel('Refresh Rate'))
        panelLayout2.addWidget(self.comboRate)
        panelLayout2.addWidget(self.btnStart)
        panelLayout2.addWidget(self.btnRestart)
        panelLayout2.addWidget(self.btnStop)

        thisLayout = QtWidgets.QVBoxLayout()
        thisLayout.addWidget(self.pgPlot)
        thisLayout.addLayout(panelLayout1)
        thisLayout.addLayout(panelLayout2)
        self.setLayout(thisLayout)

    def update_plot(self, data):
        self.curve.setData(data)
