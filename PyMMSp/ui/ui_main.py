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


class MainUI(QtWidgets.QWidget):
    """ Main UI Widget """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.synStatus = SynStatus(self)
        self.liaStatus = LiaStatus(self)
        self.scopeStatus = ScopeStatus(self)
        self.synPanel = SynPanel(self)
        self.lockinPanel = LockinPanel(self)
        self.oscilloPanel = OscilloPanel(self)
        self.motorPanel = MotorPanel(self)
        self.scopeMonitor = ScopeMonitor(self)
        self.liaMonitor = LockinMonitor(self)
        self.specMonitor = SpectrumMonitor(self)

        self.mainLayout = QtWidgets.QGridLayout()
        self.mainLayout.setSpacing(6)
        self.mainLayout.addWidget(self.synStatus, 0, 0, 3, 2)
        self.mainLayout.addWidget(self.liaStatus, 3, 0, 3, 2)
        self.mainLayout.addWidget(self.scopeStatus, 6, 0, 1, 2)
        # self.mainLayout.addWidget(self.testModeSignLabel, 7, 0, 1, 2)
        self.mainLayout.addWidget(self.synPanel, 0, 2, 3, 3)
        self.mainLayout.addWidget(self.lockinPanel, 3, 2, 2, 3)
        self.mainLayout.addWidget(self.oscilloPanel, 5, 2, 2, 3)
        self.mainLayout.addWidget(self.motorPanel, 7, 2, 1, 3)
        self.mainLayout.addWidget(self.liaMonitor, 0, 5, 4, 4)
        self.mainLayout.addWidget(self.scopeMonitor, 4, 5, 2, 4)
        self.mainLayout.addWidget(self.specMonitor, 6, 5, 2, 4)
        self.setLayout(self.mainLayout)

        self.msgErr = ui_shared.MsgError(self, 'Error')
        self.msgWarn = ui_shared.MsgWarning(self, 'Warning')
        self.msgInfo = ui_shared.MsgInfo(self, 'Info')

        self.selInstDialog = ui_dialog.SelInstDialog(self)
        self.viewInstDialog = ui_dialog.ViewInstDialog(self)
        self.synInfoDialog = ui_dialog.SynInfoDialog(self)
        self.liaInfoDialog = ui_dialog.LockinInfoDialog(self)
        self.oscilloDialog = ui_dialog.OscilloscopeDialog(self)
        self.closeSelInstDialog = ui_dialog.CloseSelInstDialog(self)
        self.gaugeDialog = ui_dialog.GaugeDialog(self)


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
        self.synRF.setText('On' if syn_info.rf_toggle else 'Off')
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
        self.setCheckable(True)
        self.setChecked(False)

        ## -- Define synthesizer control elements --
        self.synFreqLabel = QtWidgets.QLabel('{:.9f}'.format(30000))
        self.probFreqFill = QtWidgets.QLineEdit()
        self.probFreqFill.setText('180000')
        self.bandSel = QtWidgets.QComboBox()
        self.bandSel.addItems(list(txt for txt in api_syn.yield_band_str()))

        ## -- Set up synthesizer control layout --
        synLayout = QtWidgets.QGridLayout()
        synLayout.addWidget(QtWidgets.QLabel('Synthesizer Frequency'), 0, 0)
        synLayout.addWidget(self.synFreqLabel, 0, 1)
        synLayout.addWidget(QtWidgets.QLabel('MHz'), 0, 2)
        synLayout.addWidget(QtWidgets.QLabel('Probing Frequency'), 1, 0)
        synLayout.addWidget(self.probFreqFill, 1, 1)
        synLayout.addWidget(QtWidgets.QLabel('MHz'), 1, 2)
        synLayout.addWidget(QtWidgets.QLabel('VDI Band'), 2, 0)
        synLayout.addWidget(self.bandSel, 2, 1, 1, 3)

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

        ## -- Define synthesizer power switch
        self.synPowerSwitchBtn = QtWidgets.QPushButton('OFF')
        self.synPowerSwitchBtn.setCheckable(True)
        self.synPowerManualInput = QtWidgets.QPushButton('Set Power')

        synPowerLayout = QtWidgets.QHBoxLayout()
        synPowerLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        synPowerLayout.addWidget(self.synPowerManualInput)
        synPowerLayout.addWidget(QtWidgets.QLabel('RF Switch'))
        synPowerLayout.addWidget(self.synPowerSwitchBtn)

        ## -- Set up main layout
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        mainLayout.addLayout(synPowerLayout)
        mainLayout.addLayout(synLayout)
        mainLayout.addWidget(modGBox)
        self.setLayout(mainLayout)

    def print_info(self, info):
        self.synPowerSwitchBtn.setChecked(info.rf_toggle)
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


class LockinPanel(QtWidgets.QGroupBox):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle('Lockin Control')
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)  # align left
        self.setCheckable(True)
        self.setChecked(False)

        ## -- Define layout elements --
        self.harmSel = QtWidgets.QComboBox()
        self.harmSel.addItems(['1', '2', '3', '4'])
        self.harmSel.setCurrentIndex(0)
        self.phaseFill = QtWidgets.QLineEdit('0')
        self.sensSel = QtWidgets.QComboBox()
        self.sensSel.addItems(api_lia.SENS_STR)
        self.tauSel = QtWidgets.QComboBox()
        self.tauSel.addItems(api_lia.TAU_STR)
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

        ## -- Set up main layout --
        mainLayout = QtWidgets.QGridLayout()
        mainLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        mainLayout.addWidget(QtWidgets.QLabel('Harmonics'), 0, 0)
        mainLayout.addWidget(self.harmSel, 0, 1)
        mainLayout.addWidget(QtWidgets.QLabel('Phase'), 1, 0)
        mainLayout.addWidget(self.phaseFill, 1, 1)
        mainLayout.addWidget(QtWidgets.QLabel('Sensitivity'), 2, 0)
        mainLayout.addWidget(self.sensSel, 2, 1)
        mainLayout.addWidget(QtWidgets.QLabel('Time Const'), 3, 0)
        mainLayout.addWidget(self.tauSel, 3, 1)
        mainLayout.addWidget(QtWidgets.QLabel('Couple'), 0, 2)
        mainLayout.addWidget(self.coupleSel, 0, 3)
        mainLayout.addWidget(QtWidgets.QLabel('Reserve'), 1, 2)
        mainLayout.addWidget(self.reserveSel, 1, 3)
        mainLayout.addWidget(QtWidgets.QLabel('Grouding'), 2, 2)
        mainLayout.addWidget(self.groundingSel, 2, 3)
        mainLayout.addWidget(QtWidgets.QLabel('Input Filter'), 3, 2)
        mainLayout.addWidget(self.filterSel, 3, 3)
        mainLayout.addWidget(self.autoPhaseBtn, 4, 2)
        mainLayout.addWidget(self.resetBtn, 4, 3)
        self.setLayout(mainLayout)


class OscilloPanel(QtWidgets.QGroupBox):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle('Oscilloscope Control')
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self.setCheckable(True)
        self.setChecked(False)

        ## -- Define layout elements --
        self.srateFill = QtWidgets.QLineEdit()
        self.slenFill = QtWidgets.QLineEdit()
        self.sensSel = QtWidgets.QComboBox()
        self.sensSel.addItems(list(api_oscillo.SENS_STR))
        self.avgFill = QtWidgets.QLineEdit()

        ## -- Set up main layout --
        mainLayout = QtWidgets.QFormLayout()
        mainLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        mainLayout.addRow(QtWidgets.QLabel('Sample Rate (MHz)'), self.srateFill)
        mainLayout.addRow(QtWidgets.QLabel('Sample Length'), self.slenFill)
        mainLayout.addRow(QtWidgets.QLabel('Sensitivity'), self.sensSel)
        mainLayout.addRow(QtWidgets.QLabel('Oscilloscope Average'), self.avgFill)
        self.setLayout(mainLayout)

    def print_info(self, info):
        pass


class MotorPanel(QtWidgets.QGroupBox):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle('Cavity Control')
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self.setCheckable(True)
        self.setChecked(False)

        self.tuneButton = QtWidgets.QPushButton('Tune Cavity')
        mainLayout = QtWidgets.QHBoxLayout()
        mainLayout.addWidget(self.tuneButton)
        self.setLayout(mainLayout)


class ScopeMonitor(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.pgPlot = pg.PlotWidget(title='Oscilloscope Monitor')
        mainLayout = QtWidgets.QGridLayout()
        mainLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        mainLayout.addWidget(self.pgPlot, 0, 0)
        self.setLayout(mainLayout)

    def plot(self):
        pass


class LockinMonitor(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.counter = 0  # data points counter

        self.slenFill = QtWidgets.QLineEdit()
        self.slenFill.setText('100')
        self.slenFill.setStyleSheet(f'border: 1px solid {ui_shared.msg_color(2)}')
        self.yMaxSel = QtWidgets.QComboBox()
        self.yMaxSel.addItems(['1 V', '100 mV', '10 mV', '1 mV', '100 uV', '10 uV', '1 uV', '100 nV', '10 nV'])
        self.updateRate = QtWidgets.QComboBox()
        self.updateRate.addItems(['10 Hz', '5 Hz', '2 Hz', '1 Hz',
                                  '0.5 Hz', '0.2 Hz', '0.1 Hz', 'Auto'])
        self.updateRate.setCurrentIndex(2)  # default update rate 0.5s
        self.startButton = QtWidgets.QPushButton('Start')
        self.startButton.setCheckable(True)
        self.restartButton = QtWidgets.QPushButton('Restart')
        self.stopButton = QtWidgets.QPushButton('Stop')
        panelLayout = QtWidgets.QHBoxLayout()
        panelLayout.addWidget(QtWidgets.QLabel('Y Max'))
        panelLayout.addWidget(self.yMaxSel)
        panelLayout.addWidget(QtWidgets.QLabel('Length'))
        panelLayout.addWidget(self.slenFill)
        panelLayout.addWidget(QtWidgets.QLabel('Rate'))
        panelLayout.addWidget(self.updateRate)
        panelLayout.addWidget(self.startButton)
        panelLayout.addWidget(self.restartButton)
        panelLayout.addWidget(self.stopButton)
        settingPanel = QtWidgets.QWidget()
        settingPanel.setLayout(panelLayout)

        self.pgPlot = pg.PlotWidget(title='Lockin Monitor')
        self.pgPlot.setLabel('left', text='Lockin Signal', units='V')
        self.pgPlot.setYRange(0, 1)
        self.curve = pg.PlotCurveItem()
        self.pgPlot.addItem(self.curve)
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        mainLayout.addWidget(self.pgPlot)
        mainLayout.addWidget(settingPanel)
        self.setLayout(mainLayout)

        # trigger settings
        self.yMaxSel.currentIndexChanged.connect(self.rescale)

    def rescale(self, idx):

        self.pgPlot.setYRange(0, 10 ** (-idx))

    def update_plot(self, data):
        self.curve.setData(data)


class SpectrumMonitor(QtWidgets.QWidget):

    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self, parent)
        self.parent = parent

        self.pgPlot = pg.PlotWidget(title='Spectrum Monitor')
        mainLayout = QtWidgets.QGridLayout()
        mainLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        mainLayout.addWidget(self.pgPlot, 0, 0)
        self.setLayout(mainLayout)

    def plot(self):
        pass
