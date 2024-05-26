#! encoding = utf-8
''' GUI Panels. '''

import numpy as np
import pyqtgraph as pg
import pyvisa
# import standard libraries
from PyQt6 import QtGui, QtCore, QtWidgets

# import instrument inst
from PyMMSp.inst import lockin as api_lia
from PyMMSp.inst import pci as api_pci
from PyMMSp.inst import synthesizer as api_syn
from PyMMSp.inst import validator as api_val
# import shared ui widgets
from PyMMSp.ui import Dialogs
from PyMMSp.ui import SharedWidgets as Shared


class SynStatus(QtWidgets.QGroupBox):
    """
        Synthesizer status display
    """

    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self, parent)
        self.parent = parent

        self.setTitle('Synthesizer Status')
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self.setCheckable(True)
        self.setChecked(False)

        ## -- Define synthesizer status elements --
        refreshButton = QtWidgets.QPushButton('Manual Refresh')
        moreInfoButton = QtWidgets.QPushButton('More Info')
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
        errMsgBtn = QtWidgets.QPushButton('Pop Err Msg')

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
        mainLayout.addWidget(refreshButton, 0, 0, 1, 2)
        mainLayout.addWidget(moreInfoButton, 0, 2, 1, 2)
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
        mainLayout.addWidget(errMsgBtn, 9, 0)
        mainLayout.addWidget(self.errMsgLabel, 9, 1, 1, 3)
        self.setLayout(mainLayout)

        ## -- Trigger status updates
        refreshButton.clicked.connect(self.manual_refresh)
        moreInfoButton.clicked.connect(self.show_info_dialog)
        errMsgBtn.clicked.connect(self.pop_err_msg)
        # initial status
        self.print_info()

        # Trigger groupbox check_state
        self.clicked.connect(self.check)

    def check(self):
        """ Enable/disable this groupbox """

        if (self.parent.testModeAction.isChecked() or self.parent.synHandle):
            self.setChecked(True)
        else:
            msg = Shared.MsgError(self, 'No Instrument!', 'No synthesizer is connected!')
            msg.exec()
            self.setChecked(False)

    def print_info(self):
        """ Print instrument information in this panel """

        self.addressText.setText(self.parent.synInfo.instName)
        self.synRF.setText('On' if self.parent.synInfo.rfToggle else 'Off')
        self.synPower.setText('{:.1f} dbm'.format(self.parent.synInfo.synPower))
        self.synFreq.setText(pg.siFormat(self.parent.synInfo.synFreq, suffix='Hz', precision=12))
        self.synMod.setText('On' if self.parent.synInfo.modToggle else 'Off')
        self.synAMStat.setText('On' if self.parent.synInfo.AM1Toggle else 'Off')
        self.synFMStat.setText('On' if self.parent.synInfo.FM1Toggle else 'Off')
        self.synAMDepth.setText('{:.1f}%'.format(self.parent.synInfo.AM1DepthPercent))
        self.synAMFreq.setText(pg.siFormat(self.parent.synInfo.AM1Freq, suffix='Hz', precision=4))
        self.synFMDev.setText(pg.siFormat(self.parent.synInfo.FM1Dev, suffix='Hz', precision=4))
        self.synFMFreq.setText(pg.siFormat(self.parent.synInfo.FM1Freq, suffix='Hz', precision=4))
        self.synLF.setText('On' if self.parent.synInfo.LFToggle else 'Off')
        self.synLFV.setText(pg.siFormat(self.parent.synInfo.LFVoltage, suffix='V'))
        self.errMsgLabel.setText(self.parent.synInfo.errMsg)

    def manual_refresh(self):
        """ Manually refresh status. Also update the SynCtrl widgets,
        which will in turn trigger the refresh function
        """

        if self.parent.testModeAction.isChecked() or (not self.parent.synHandle):
            pass
        else:
            self.parent.synInfo.full_info_query(self.parent.synHandle)
            self.parent.synCtrl.synPowerSwitchBtn.setChecked(self.parent.synInfo.rfToggle)
            self.parent.synCtrl.probFreqFill.setText('{:.9f}'.format(self.parent.synInfo.probFreq * 1e-6))
            self.parent.synCtrl.modSwitchBtn.setChecked(self.parent.synInfo.modToggle)
            self.parent.synCtrl.modSwitchBtn.setText('ON' if self.parent.synInfo.modToggle else 'OFF')
            if self.parent.synInfo.AM1Toggle and (not self.parent.synInfo.FM1Toggle):
                self.parent.synCtrl.modModeSel.setCurrentIndex(1)
                self.parent.synCtrl.modFreqFill.setText('{:.1f}'.format(self.parent.synInfo.AM1Freq * 1e-3))
                self.parent.synCtrl.modFreqUnitSel.setCurrentIndex(1)
                self.parent.synCtrl.modAmpFill.setText('{:.1f}'.format(self.parent.synInfo.AM1DepthPercent))
                self.parent.synCtrl.modAmpAMUnitSel.setCurrentIndex(0)
            elif (not self.parent.synInfo.AM1Toggle) and self.parent.synInfo.FM1Toggle:
                self.parent.synCtrl.modModeSel.setCurrentIndex(2)
                self.parent.synCtrl.modFreqFill.setText('{:.1f}'.format(self.parent.synInfo.FM1Freq * 1e-3))
                self.parent.synCtrl.modFreqUnitSel.setCurrentIndex(1)
                self.parent.synCtrl.modAmpFill.setText('{:.1f}'.format(self.parent.synInfo.FM1Dev * 1e-3))
                self.parent.synCtrl.modAmpFMUnitSel.setCurrentIndex(1)
            else:
                self.parent.synCtrl.modModeSel.setCurrentIndex(0)
            self.parent.synCtrl.lfSwitchBtn.setChecked(self.parent.synInfo.LFToggle)
            self.parent.synCtrl.lfSwitchBtn.setText('ON' if self.parent.synInfo.LFToggle else 'OFF')
            self.parent.synCtrl.lfVolFill.setText('{:.3f}'.format(self.parent.synInfo.LFVoltage))

    def show_info_dialog(self):

        self.parent.synInfoDialog.display()

    def pop_err_msg(self):
        """ Pop error message """
        if self.parent.synHandle:
            self.parent.synInfo.errMsg = api_syn.query_err_msg(self.parent.synHandle)
            self.errMsgLabel.setText(self.parent.synInfo.errMsg)
        else:
            pass


class LockinStatus(QtWidgets.QGroupBox):
    '''
        Lockin status display
    '''

    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self, parent)
        self.parent = parent

        self.setTitle('Lockin Status')
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self.setCheckable(True)
        self.setChecked(False)

        ## -- Define synthesizer status elements --
        refreshButton = QtWidgets.QPushButton('Manual Refresh')
        moreInfoButton = QtWidgets.QPushButton('More Info')
        errMsgBtn = QtWidgets.QPushButton('Pop Err Msg')
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
        mainLayout.addWidget(refreshButton, 0, 0, 1, 2)
        mainLayout.addWidget(moreInfoButton, 0, 2, 1, 2)
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
        mainLayout.addWidget(errMsgBtn, 7, 0)
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

        # this dialog is a child class of the main window
        self.infoDialog = Dialogs.LockinInfoDialog(self.parent)
        ## -- Trigger status updates
        errMsgBtn.clicked.connect(self.pop_err_msg)
        refreshButton.clicked.connect(self.manual_refresh)
        moreInfoButton.clicked.connect(self.show_info_dialog)
        # initial status
        self.print_info()

        # Trigger groupbox check_state
        self.clicked.connect(self.check)

    def check(self):
        ''' Enable/disable this groupbox '''

        if (self.parent.testModeAction.isChecked() or self.parent.liaHandle):
            self.setChecked(True)
        else:
            msg = Shared.MsgError(self, 'No Instrument!', 'No lockin amplifier is connected!')
            msg.exec()
            self.setChecked(False)

    def print_info(self):
        ''' Print instrument information in this panel '''

        self.addressText.setText(self.parent.liaInfo.instName)
        self.liaHarmLabel.setText(self.parent.liaInfo.refHarmText)
        self.liaPhaseLabel.setText('{:.2f}'.format(self.parent.liaInfo.refPhase))
        self.liaSensLabel.setText(self.parent.liaInfo.sensText)
        self.liaTCLabel.setText(self.parent.liaInfo.tcText)
        self.liaFreqLabel.setText(pg.siFormat(self.parent.liaInfo.refFreq, suffix='Hz'))
        self.liaCoupleLabel.setText(self.parent.liaInfo.coupleText)
        self.liaReserveLabel.setText(self.parent.liaInfo.reserveText)
        self.liaGroundingLabel.setText(self.parent.liaInfo.groundingText)
        self.liaFilterLabel.setText(self.parent.liaInfo.inputFilterText)
        self.liaRefSrcLabel.setText(self.parent.liaInfo.refSrcText)

    def manual_refresh(self):
        ''' Manually refresh status. Also update the LIACtrl widgets,
        which will in turn trigger the refresh function.
        '''

        if self.parent.testModeAction.isChecked() or (not self.parent.liaHandle):
            pass
        else:
            self.parent.liaInfo.full_info_query(self.parent.liaHandle)
            self.parent.liaCtrl.harmSel.setCurrentIndex(self.parent.liaInfo.refHarmIndex)
            self.parent.liaCtrl.phaseFill.setText('{:.2f}'.format(self.parent.liaInfo.refPhase))
            self.parent.liaCtrl.sensSel.setCurrentIndex(self.parent.liaInfo.sensIndex)
            self.parent.liaCtrl.tcSel.setCurrentIndex(self.parent.liaInfo.tcIndex)
            self.parent.liaCtrl.coupleSel.setCurrentIndex(self.parent.liaInfo.coupleIndex)
            self.parent.liaCtrl.reserveSel.setCurrentIndex(self.parent.liaInfo.reserveIndex)
            self.parent.liaMonitor.set_waittime()

    def show_info_dialog(self):

        self.parent.liaInfoDialog.display()

    def pop_err_msg(self):
        ''' Pop error message '''
        if self.parent.liaHandle:
            self.errMsgLabel.setText(api_lia.query_err_msg(self.parent.liaHandle))
        else:
            pass


class ScopeStatus(QtWidgets.QGroupBox):
    '''
        Oscilloscope (PCI card) status display
    '''

    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self, parent)
        self.parent = parent

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

        ## -- Trigger status updates
        self.refreshButton.clicked.connect(self.manual_refresh)
        # initial status
        self.print_info()

        # Trigger groupbox check_state
        self.clicked.connect(self.check)

    def check(self):
        ''' Enable/disable this groupbox '''

        if (self.parent.testModeAction.isChecked() or self.parent.pciHandle):
            self.setChecked(True)
        else:
            msg = Shared.MsgError(self, 'No Instrument!', 'No PCI card is connected!')
            msg.exec()
            self.setChecked(False)

    def print_info(self):
        self.addressText.setText(self.parent.scopeInfo.instName)

    def manual_refresh(self):
        ''' refresh instrument information '''

        if self.parent.pciHandle:
            self.addressText.setText(self.parent.pciHandle.resource_name)
        else:
            self.addressText.setText('N.A.')


class SynCtrl(QtWidgets.QGroupBox):
    '''
        Synthesizer control panel
    '''

    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self, parent)
        self.parent = parent

        self.setTitle('Synthesizer Control')
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)  # align left
        self.setCheckable(True)
        self.setChecked(False)

        ## -- Define synthesizer control elements --
        synWidget = QtWidgets.QWidget()
        self.synFreqLabel = QtWidgets.QLabel('{:.9f}'.format(30000))
        self.probFreqFill = QtWidgets.QLineEdit()
        self.probFreqFill.setText('180000')
        self.bandSel = Shared.VDIBandComboBox()

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
        synWidget.setLayout(synLayout)

        # Set up modulation child widget
        modGBox = QtWidgets.QGroupBox()
        modGBox.setTitle('Modulation Control')
        modGBox.setFlat(True)
        modGBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        modLayout = QtWidgets.QGridLayout()
        modLayout.setSpacing(0)

        self.modModeSel = QtWidgets.QComboBox()
        self.modModeSel.addItems(api_syn.MOD_MODE_LIST)

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
        synPowerManualInput = QtWidgets.QPushButton('Set Power')

        synPowerLayout = QtWidgets.QHBoxLayout()
        synPowerLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        synPowerLayout.addWidget(synPowerManualInput)
        synPowerLayout.addWidget(QtWidgets.QLabel('RF Switch'))
        synPowerLayout.addWidget(self.synPowerSwitchBtn)
        synPowerCtrl = QtWidgets.QWidget()
        synPowerCtrl.setLayout(synPowerLayout)

        self.powerSwitchTimer = QtCore.QTimer()
        self.powerSwitchTimer.setInterval(500)
        self.powerSwitchTimer.setSingleShot(True)
        self.powerSwitchProgBar = QtWidgets.QProgressBar()
        self.progDialog = QtWidgets.QDialog()
        self.progDialog.setWindowTitle('RF Ramp')
        progDialogLayout = QtWidgets.QVBoxLayout()
        progDialogLayout.addWidget(self.powerSwitchProgBar)
        self.progDialog.setLayout(progDialogLayout)

        ## -- Set up main layout
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        mainLayout.addWidget(synPowerCtrl)
        mainLayout.addWidget(synWidget)
        mainLayout.addWidget(modGBox)
        self.setLayout(mainLayout)

        # Trigger frequency refresh and communication
        self.probFreqFill.textChanged.connect(self.tune_freq)
        self.bandSel.currentIndexChanged.connect(self.tune_freq)

        # Trigger modulation status refresh and communication
        self.modModeSel.currentIndexChanged[int].connect(self.switch_modWidgets)
        self.modFreqFill.textChanged.connect(self.tune_mod_parameter)
        self.modFreqUnitSel.currentIndexChanged.connect(self.tune_mod_parameter)
        self.modAmpFill.textChanged.connect(self.tune_mod_parameter)
        self.modAmpAMUnitSel.currentIndexChanged.connect(self.tune_mod_parameter)
        self.modAmpFMUnitSel.currentIndexChanged.connect(self.tune_mod_parameter)
        self.modSwitchBtn.clicked.connect(self.switch_modulation)
        self.lfSwitchBtn.clicked.connect(self.switch_lf)
        self.lfVolFill.textChanged.connect(self.tune_lf)

        # Trigger synthesizer power toggle and communication
        synPowerManualInput.clicked.connect(self.synRFPower_manual)
        self.synPowerSwitchBtn.clicked.connect(self.synRFPower_auto)
        self.synPowerSwitchBtn.toggled.connect(self.set_synPowerSwitchBtn_label)
        self.powerSwitchTimer.timeout.connect(self.ramp_synRFPower)

        # Trigger groupbox check_state
        self.clicked.connect(self.check)

    def check(self):
        ''' Enable/disable this groupbox '''

        if (self.parent.testModeAction.isChecked() or self.parent.synHandle):
            self.setChecked(True)
            self.parent.synStatus.setChecked(True)
        else:
            msg = Shared.MsgError(self, 'No Instrument!', 'No synthesizer is connected!')
            msg.exec()
            self.setChecked(False)
            self.parent.synStatus.setChecked(False)

        self.parent.synStatus.print_info()

    def tune_freq(self):
        '''
            Communicate with the synthesizer and refresh frequency setting.
        '''

        # validate input
        status, synfreq = api_val.val_prob_freq(self.probFreqFill.text(),
                                                self.bandSel.currentIndex())
        # set sheet border color by syn_stat
        self.probFreqFill.setStyleSheet('border: 1px solid {:s}'.format(Shared.msgcolor(status)))

        if status:  # if status is not fatal
            if self.parent.testModeAction.isChecked():
                # fake a successful communication on test mode
                vCode = pyvisa.constants.StatusCode.success
            else:
                # call syn inst and return communication status
                vCode = api_syn.set_syn_freq(self.parent.synHandle, synfreq)

            if vCode == pyvisa.constants.StatusCode.success:
                # communication successful, update synInfo
                self.parent.synInfo.synFreq = synfreq
                self.parent.synInfo.vdiBandIndex = self.bandSel.currentIndex()
                self.parent.synInfo.vdiBandMultiplication = api_val.VDIBANDMULTI[self.bandSel.currentIndex()]
                self.parent.synInfo.probFreq = synfreq * api_val.VDIBANDMULTI[self.bandSel.currentIndex()]
            else:
                msg = Shared.InstStatus(self, vCode)
                msg.exec()
            # refresh synthesizer status
            self.parent.synStatus.print_info()
            self.synFreqLabel.setText('{:.9f}'.format(synfreq * 1e-6))
        else:  # else ignore change
            pass

    def ramp_synRFPower(self):
        '''
            The actual synthesizer inst command.
            Triggered by self.powerSwitchTimer.timeout
            Returns successful status
        '''

        try:
            this_power = next(self.ramper)
            if self.parent.testModeAction.isChecked():
                # fake a successful communication on test mode
                vCode = pyvisa.constants.StatusCode.success
            else:
                vCode = api_syn.set_syn_power(self.parent.synHandle, this_power)

            if vCode == pyvisa.constants.StatusCode.success:
                self.parent.synInfo.synPower = api_syn.read_syn_power(self.parent.synHandle)
                self.parent.synStatus.print_info()
                self.powerSwitchProgBar.setValue(self.powerSwitchProgBar.value() + 1)
                # start timer
                self.powerSwitchTimer.start()
            else:
                self.powerSwitchTimer.stop()
                msg = Shared.InstStatus(self, vCode)
                msg.exec()
        except StopIteration:
            self.powerSwitchTimer.stop()
            self.progDialog.accept()

    def synRFPower_manual(self):
        '''
            Communicate with the synthesizer and set up RF power
            (automatically turn RF on)
        '''

        # Get current syn power
        if self.parent.testModeAction.isChecked():
            # fake a power
            self.parent.synInfo.synPower = -20
        else:
            self.parent.synInfo.synPower = api_syn.read_syn_power(self.parent.synHandle)

        # Grab manual input power from QInputDialog
        target_power, okay = QtWidgets.QInputDialog.getInt(self, 'RF Power',
                                                       'Manual Input (-20 to 0)', self.parent.synInfo.synPower, -20, 0,
                                                       1)

        if okay:  # hopefully no error occurs
            if self.parent.testModeAction.isChecked():
                pass
            else:
                # turn on RF toggle first
                api_syn.set_power_toggle(self.parent.synHandle, True)
            self.synPowerSwitchBtn.setChecked(True)
            self.powerSwitchProgBar.setRange(0, abs(self.parent.synInfo.synPower - target_power))
            self.powerSwitchProgBar.setValue(0)
            if self.parent.synInfo.synPower > target_power:
                self.ramper = api_syn.ramp_down(self.parent.synInfo.synPower, target_power)
            else:
                self.ramper = api_syn.ramp_up(self.parent.synInfo.synPower, target_power)
            self.ramp_synRFPower()
            self.progDialog.exec()
        else:
            pass

    def synRFPower_auto(self, btn_pressed):
        '''
            Automatically switch synthesizer RF on/off
        '''

        # Get current syn power
        if self.parent.testModeAction.isChecked():
            # fake a power
            self.parent.synInfo.synPower = -20
        else:
            self.parent.synInfo.synPower = api_syn.read_syn_power(self.parent.synHandle)

        if btn_pressed:  # user wants to turn on
            if self.parent.testModeAction.isChecked():
                pass
            else:
                api_syn.set_power_toggle(self.parent.synHandle, True)
            self.ramper = api_syn.ramp_up(self.parent.synInfo.synPower, 0)
            self.powerSwitchProgBar.setRange(0, abs(self.parent.synInfo.synPower))
            self.powerSwitchProgBar.setValue(0)
            self.ramp_synRFPower()
            self.progDialog.exec()
        elif self.parent.synInfo.synPower > -20:  # user wants to turn off, needs ramp down
            self.ramper = api_syn.ramp_down(self.parent.synInfo.synPower, -20)
            self.powerSwitchProgBar.setRange(0, abs(self.parent.synInfo.synPower + 20))
            self.powerSwitchProgBar.setValue(0)
            self.ramp_synRFPower()
            result = self.progDialog.exec()
            if self.parent.testModeAction.isChecked():
                self.synPowerSwitchBtn.setChecked(False)
            else:
                # RF protection before turn off
                self.parent.synInfo.synPower = api_syn.read_syn_power(self.parent.synHandle)
                if result and (self.parent.synInfo.synPower <= -20):
                    # safely turn off RF
                    api_syn.set_power_toggle(self.parent.synHandle, False)
                    self.synPowerSwitchBtn.setChecked(False)
                else:
                    self.synPowerSwitchBtn.setChecked(True)
        else:  # user wants to turn off, power is already -20
            # safely turn off RF
            if self.parent.testModeAction.isChecked():
                pass
            else:
                api_syn.set_power_toggle(self.parent.synHandle, False)
            self.synPowerSwitchBtn.setChecked(False)

        self.parent.synStatus.print_info()

    def set_synPowerSwitchBtn_label(self, toggle_state):
        '''
            Set power switch button text
        '''

        if toggle_state:
            self.synPowerSwitchBtn.setText('ON')
        else:
            self.synPowerSwitchBtn.setText('OFF')

    def switch_modWidgets(self, mod_index):
        '''
            Switch modulation setting widgets
        '''

        self.parent.synInfo.modModeIndex = mod_index
        self.parent.synInfo.modModeText = self.modModeSel.currentText()
        self.tune_mod_mode(mod_index)

        if mod_index:  # Modulation selected. Show modulation widget
            self.modFreq.show()
            self.modAmp.show()
            self.lfVol.show()
            if mod_index == 1:
                self.modAmpLabel.setText('Mod Depth')
                self.modAmpAMUnitSel.show()
                self.modAmpFMUnitSel.hide()
            elif mod_index == 2:
                self.modAmpLabel.setText('Mod Dev')
                self.modAmpAMUnitSel.hide()
                self.modAmpFMUnitSel.show()
            self.tune_mod_parameter()
        else:  # No modulation. Hide modulation widget
            self.parent.synInfo.modFreq = 0
            self.parent.synInfo.modAmp = 0
            self.modFreq.hide()
            self.modAmp.hide()
            self.lfVol.hide()

    def tune_mod_mode(self, mod_index):
        '''
            Communicate with the synthesizer and refresh modulation mode.
        '''

        if self.parent.testModeAction.isChecked():
            # fake a successful communication on test mode
            if mod_index == 1:
                self.parent.synInfo.AM1Toggle = True
                self.parent.synInfo.FM1Toggle = False
            elif mod_index == 2:
                self.parent.synInfo.AM1Toggle = False
                self.parent.synInfo.FM1Toggle = True
            else:
                self.parent.synInfo.AM1Toggle = False
                self.parent.synInfo.FM1Toggle = False
        else:
            vCode = api_syn.set_mod_mode(self.parent.synHandle, mod_index)
            if vCode == pyvisa.constants.StatusCode.success:
                # update synInfo
                self.parent.synInfo.AM1Toggle = api_syn.read_am_state(self.parent.synHandle, 1)
                self.parent.synInfo.FM1Toggle = api_syn.read_fm_state(self.parent.synHandle, 1)
            else:
                msg = Shared.InstStatus(self, vCode)
                msg.exec()

        self.parent.synStatus.print_info()

    def tune_mod_parameter(self):
        '''
            Communicate with the synthesizer and automatically refresh modulation parameters
        '''

        mod_index = self.modModeSel.currentIndex()
        toggle_state = self.modSwitchBtn.isChecked()

        # convert input and set sheet border color by status
        freq_status, mod_freq = api_val.val_syn_mod_freq(self.modFreqFill.text(),
                                                         self.modFreqUnitSel.currentText())
        self.modFreqFill.setStyleSheet('border: 1px solid {:s}'.format(Shared.msgcolor(freq_status)))

        if mod_index == 1:  # AM
            depth_status, mod_depth = api_val.val_syn_am_depth(self.modAmpFill.text(),
                                                               self.modAmpAMUnitSel.currentText())
        elif mod_index == 2:  # FM
            depth_status, mod_depth = api_val.val_syn_fm_depth(self.modAmpFill.text(),
                                                               self.modAmpFMUnitSel.currentText())
        else:
            depth_status = 2
        self.modAmpFill.setStyleSheet('border: 1px solid {:s}'.format(Shared.msgcolor(depth_status)))

        if freq_status and depth_status and (not self.parent.testModeAction.isChecked()):
            if mod_index == 1:  # AM
                vCode = api_syn.set_am(self.parent.synHandle, mod_freq,
                                       mod_depth, toggle_state)
            elif mod_index == 2:  # FM
                vCode = api_syn.set_fm(self.parent.synHandle, mod_freq,
                                       mod_depth, toggle_state)
            else:
                vCode = pyvisa.constants.StatusCode.success

            if vCode == pyvisa.constants.StatusCode.success:
                self.parent.synInfo.modFreq = mod_freq
                self.parent.synInfo.modAmp = mod_depth
                self.parent.synInfo.AM1Freq = api_syn.read_am_freq(self.parent.synHandle, 1)
                self.parent.synInfo.AM1DepthPercent, self.parent.synInfo.AM1DepthDbm = api_syn.read_am_depth(
                    self.parent.synHandle, 1)
                self.parent.synInfo.FM1Freq = api_syn.read_fm_freq(self.parent.synHandle, 1)
                self.parent.synInfo.FM1Dev = api_syn.read_fm_dev(self.parent.synHandle, 1)
                self.parent.synStatus.print_info()
            else:
                msg = Shared.InstStatus(self, vCode)
                msg.exec()
        else:
            self.parent.synInfo.modFreq = mod_freq
            self.parent.synInfo.modAmp = mod_depth
            self.parent.synStatus.print_info()

    def switch_modulation(self, btn_pressed):
        '''
            Communicate with the synthesizer and refresh modulation on/off toggle
        '''

        if self.parent.testModeAction.isChecked():
            # fake a successful communication on test mode
            self.parent.synInfo.modToggle = btn_pressed
        else:
            vCode = api_syn.set_mod_toggle(self.parent.synHandle, btn_pressed)
            if vCode == pyvisa.constants.StatusCode.success:
                self.parent.synInfo.modToggle = api_syn.read_mod_toggle(self.parent.synHandle)
            else:
                msg = Shared.InstStatus(self, vCode)
                msg.exec()

        if btn_pressed:
            self.modSwitchBtn.setText('ON')
        else:
            self.modSwitchBtn.setText('OFF')

        self.parent.synStatus.print_info()

    def switch_lf(self, btn_pressed):
        '''
            Communicate with the synthesizer and refresh LF on/off toggle
        '''

        if self.parent.testModeAction.isChecked():
            # fake a successful communication on test mode
            self.parent.synInfo.LFToggle = btn_pressed
        else:
            vCode = api_syn.set_lf_toggle(self.parent.synHandle, btn_pressed)
            if vCode == pyvisa.constants.StatusCode.success:
                self.parent.synInfo.LFToggle = api_syn.read_lf_toggle(self.parent.synHandle)
                self.parent.synInfo.LFVoltage = api_syn.read_lf_voltage(self.parent.synHandle)
            else:
                msg = Shared.InstStatus(self, vCode)
                msg.exec()

        self.lfVolFill.setText('{:.3f}'.format(self.parent.synInfo.LFVoltage))

        if btn_pressed:
            self.lfSwitchBtn.setText('ON')
        else:
            self.lfSwitchBtn.setText('OFF')

        self.parent.synStatus.print_info()

    def tune_lf(self, vol_text):
        '''
            Communicate with the synthesizer and refresh LF voltage
        '''

        status, lf_vol = api_val.val_syn_lf_vol(vol_text)
        self.lfVolFill.setStyleSheet('border: 1px solid {:s}'.format(Shared.msgcolor(status)))

        if status:
            if self.parent.testModeAction.isChecked():
                # fake a successful communication on test mode
                self.parent.synInfo.LFVoltage = lf_vol
            else:
                vCode = api_syn.set_lf_amp(self.parent.synHandle, lf_vol)
                if vCode == pyvisa.constants.StatusCode.success:
                    self.parent.synInfo.LFVoltage = api_syn.read_lf_voltage(self.parent.synHandle)
                else:
                    msg = Shared.InstStatus(self, vCode)
                    msg.exec()

            self.parent.synStatus.print_info()
        else:
            pass


class LockinCtrl(QtWidgets.QGroupBox):

    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self, parent)
        self.parent = parent

        self.setTitle('Lockin Control')
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)  # align left
        self.setCheckable(True)
        self.setChecked(False)

        ## -- Define layout elements --
        self.harmSel = QtWidgets.QComboBox()
        self.harmSel.addItems(['1', '2', '3', '4'])
        self.harmSel.setCurrentIndex(0)
        self.phaseFill = QtWidgets.QLineEdit('0')
        self.sensSel = Shared.LIASensBox()
        self.tcSel = Shared.LIATCBox()
        self.coupleSel = QtWidgets.QComboBox()
        self.coupleSel.addItems(api_lia.COUPLE_LIST)
        self.coupleSel.setCurrentIndex(1)
        self.reserveSel = QtWidgets.QComboBox()
        self.reserveSel.addItems(api_lia.RESERVE_LIST)
        self.reserveSel.setCurrentIndex(1)
        self.groundingSel = QtWidgets.QComboBox()
        self.groundingSel.addItems(api_lia.INPUT_GND_LIST)
        self.groundingSel.setCurrentIndex(1)
        self.filterSel = QtWidgets.QComboBox()
        self.filterSel.addItems(api_lia.INPUT_FILTER_LIST)
        self.filterSel.setCurrentIndex(1)
        autoPhaseBtn = QtWidgets.QPushButton('Auto Phase')
        resetBtn = QtWidgets.QPushButton('Reset')

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
        mainLayout.addWidget(self.tcSel, 3, 1)
        mainLayout.addWidget(QtWidgets.QLabel('Couple'), 0, 2)
        mainLayout.addWidget(self.coupleSel, 0, 3)
        mainLayout.addWidget(QtWidgets.QLabel('Reserve'), 1, 2)
        mainLayout.addWidget(self.reserveSel, 1, 3)
        mainLayout.addWidget(QtWidgets.QLabel('Grouding'), 2, 2)
        mainLayout.addWidget(self.groundingSel, 2, 3)
        mainLayout.addWidget(QtWidgets.QLabel('Input Filter'), 3, 2)
        mainLayout.addWidget(self.filterSel, 3, 3)
        mainLayout.addWidget(autoPhaseBtn, 4, 2)
        mainLayout.addWidget(resetBtn, 4, 3)
        self.setLayout(mainLayout)

        ## -- Trigger setting status and communication
        self.phaseFill.textChanged.connect(self.tune_phase)
        self.harmSel.currentTextChanged[str].connect(self.tune_harmonics)
        self.tcSel.currentIndexChanged[int].connect(self.tune_time_const)
        self.sensSel.currentIndexChanged[int].connect(self.tune_sensitivity)
        self.coupleSel.currentIndexChanged[int].connect(self.tune_couple)
        self.reserveSel.currentIndexChanged[int].connect(self.tune_reserve)
        self.groundingSel.currentIndexChanged[int].connect(self.tune_grounding)
        self.filterSel.currentIndexChanged[int].connect(self.tune_filter)
        autoPhaseBtn.clicked.connect(self.auto_phase)
        resetBtn.clicked.connect(self.reset)
        self.clicked.connect(self.check)

    def check(self):
        ''' Enable/disable this groupbox '''

        if (self.parent.testModeAction.isChecked() or self.parent.liaHandle):
            api_lia.init_lia(self.parent.liaHandle)
            self.setChecked(True)
        else:
            msg = Shared.MsgError(self, 'No Instrument!', 'No lockin amplifier is connected!')
            msg.exec()
            self.setChecked(False)

        self.parent.liaStatus.print_info()

    def tune_phase(self, phase_text):
        '''
            Communicate with the lockin and set phase
        '''

        status, phase = api_val.val_lia_phase(phase_text)
        self.phaseFill.setStyleSheet('border: 1px solid {:s}'.format(Shared.msgcolor(status)))

        if status:
            if self.parent.testModeAction.isChecked():
                # fake a successful communication on test mode
                self.parent.liaInfo.refPhase = phase
            else:
                vCode = api_lia.set_phase(self.parent.liaHandle, phase)
                if vCode == pyvisa.constants.StatusCode.success:
                    self.parent.liaInfo.refPhase = api_lia.read_phase(self.parent.liaHandle)
                else:
                    msg = Shared.InstStatus(self, vCode)
                    msg.exec()
        else:
            pass

        self.parent.liaStatus.print_info()  # auto refresh status panel

    def tune_harmonics(self, harm_text):
        '''
            Communicate with the lockin and set Harmonics
        '''

        if self.parent.testModeAction.isChecked():
            lia_freq = self.parent.liaInfo.refFreq
        else:
            lia_freq = api_lia.read_freq(self.parent.liaHandle)
        status, harm = api_val.val_lia_harm(harm_text, lia_freq)

        if status:
            if self.parent.testModeAction.isChecked():
                # fake a successful communication on test mode
                self.parent.liaInfo.refHarm = harm
                self.parent.liaInfo.refHarmText = str(harm)
            else:
                vCode = api_lia.set_harm(self.parent.liaHandle, harm)
                if vCode == pyvisa.constants.StatusCode.success:
                    self.parent.liaInfo.refHarm = api_lia.read_harm(self.parent.liaHandle)
                    self.parent.liaInfo.refHarmText = str(self.parent.liaInfo.refHarm)
                else:
                    msg = Shared.InstStatus(self, vCode)
                    msg.exec()
        else:
            msg = Shared.MsgError(self, 'Out of Range!', 'Input harmonics exceed legal range!')
            msg.exec()

        self.parent.liaStatus.print_info()  # auto refresh status panel

    def tune_sensitivity(self, idx):
        '''
            Communicate with the lockin and set sensitivity
        '''

        if self.parent.testModeAction.isChecked():
            # fake a successful communication on test mode
            self.parent.liaInfo.sensIndex = idx
            self.parent.liaInfo.sensText = api_lia.SENS_LIST[idx]
        else:
            vCode = api_lia.set_sens(self.parent.liaHandle, idx)
            if vCode == pyvisa.constants.StatusCode.success:
                self.parent.liaInfo.sensIndex = api_lia.read_sens(self.parent.liaHandle)
                self.parent.liaInfo.sensText = api_lia.SENS_LIST[self.parent.liaInfo.sensIndex]
            else:
                msg = Shared.InstStatus(self, vCode)
                msg.exec()

        self.parent.liaStatus.print_info()  # auto refresh status panel

    def tune_time_const(self, idx):
        '''
            Communicate with the lockin and set sensitivity
        '''

        if self.parent.testModeAction.isChecked():
            # fake a successful communication on test mode
            self.parent.liaInfo.tcIndex = idx
            self.parent.liaInfo.tcText = api_lia.TC_LIST[idx]
        else:
            vCode = api_lia.set_tc(self.parent.liaHandle, idx)
            if vCode == pyvisa.constants.StatusCode.success:
                self.parent.liaInfo.tcIndex = api_lia.read_tc(self.parent.liaHandle)
                self.parent.liaInfo.tcText = api_lia.TC_LIST[self.parent.liaInfo.tcIndex]
            else:
                msg = Shared.InstStatus(self, vCode)
                msg.exec()

        self.parent.liaStatus.print_info()  # auto refresh status panel
        self.parent.liaMonitor.set_waittime()

    def tune_couple(self, idx):
        '''
            Communicate with the lockin and set couple mode
        '''

        if self.parent.testModeAction.isChecked():
            # fake a successful communication on test mode
            self.parent.liaInfo.coupleIndex = idx
            self.parent.liaInfo.coupleText = api_lia.COUPLE_LIST[idx]
        else:
            vCode = api_lia.set_couple(self.parent.liaHandle, idx)
            if vCode == pyvisa.constants.StatusCode.success:
                self.parent.liaInfo.coupleIndex = api_lia.read_couple(self.parent.liaHandle)
                self.parent.liaInfo.coupleText = api_lia.COUPLE_LIST[self.parent.liaInfo.coupleIndex]
            else:
                msg = Shared.InstStatus(self, vCode)
                msg.exec()

        self.parent.liaStatus.print_info()  # auto refresh status panel

    def tune_reserve(self, idx):
        '''
            Communicate with the lockin and set reserve
        '''

        if self.parent.testModeAction.isChecked():
            # fake a successful communication on test mode
            self.parent.liaInfo.reserveIndex = idx
            self.parent.liaInfo.reserveText = api_lia.RESERVE_LIST[idx]
        else:
            vCode = api_lia.set_reserve(self.parent.liaHandle, idx)
            if vCode == pyvisa.constants.StatusCode.success:
                self.parent.liaInfo.reserveIndex = api_lia.read_reserve(self.parent.liaHandle)
                self.parent.liaInfo.reserveText = api_lia.RESERVE_LIST[self.parent.liaInfo.reserveIndex]
            else:
                msg = Shared.InstStatus(self, vCode)
                msg.exec()

        self.parent.liaStatus.print_info()  # auto refresh status panel

    def tune_grounding(self, idx):
        '''
            Communicate with the lockin and set input grounding
        '''

        if self.parent.testModeAction.isChecked():
            # fake a successful communication on test mode
            self.parent.liaInfo.groundingIndex = idx
            self.parent.liaInfo.groundingText = api_lia.INPUT_GND_LIST[idx]
        else:
            vCode = api_lia.set_input_grounding(self.parent.liaHandle, idx)
            if vCode == pyvisa.constants.StatusCode.success:
                self.parent.liaInfo.groundingIndex = api_lia.read_input_grounding(self.parent.liaHandle)
                self.parent.liaInfo.groundingText = api_lia.INPUT_GND_LIST[self.parent.liaInfo.groundingIndex]
            else:
                msg = Shared.InstStatus(self, vCode)
                msg.exec()

        self.parent.liaStatus.print_info()  # auto refresh status panel

    def tune_filter(self, idx):
        '''
            Communicate with the lockin and set input notch filter
        '''

        if self.parent.testModeAction.isChecked():
            # fake a successful communication on test mode
            self.parent.liaInfo.inputFilterIndex = idx
            self.parent.liaInfo.inputFilterText = api_lia.INPUT_FILTER_LIST[idx]
        else:
            vCode = api_lia.set_input_filter(self.parent.liaHandle, idx)
            if vCode == pyvisa.constants.StatusCode.success:
                self.parent.liaInfo.inputFilterIndex = api_lia.read_input_filter(self.parent.liaHandle)
                self.parent.liaInfo.inputFilterText = api_lia.INPUT_FILTER_LIST[self.parent.liaInfo.inputFilterIndex]
            else:
                msg = Shared.InstStatus(self, vCode)
                msg.exec()

        self.parent.liaStatus.print_info()  # auto refresh status panel

    def auto_phase(self):

        if self.parent.testModeAction.isChecked():
            # fake a successful communication on test mode
            print('auto (random) phase (test)')
            self.parent.liaInfo.refPhase = np.random.randint(-180, 180)
            self.phaseFill.setText('{:.2f}'.format(self.parent.liaInfo.refPhase))
        else:
            vCode = api_lia.auto_phase(self.parent.liaHandle)
            if vCode == pyvisa.constants.StatusCode.success:
                self.parent.liaInfo.refPhase = api_lia.read_phase(self.parent.liaHandle)
                self.phaseFill.setText('{:.2f}'.format(self.parent.liaInfo.refPhase))
            else:
                msg = Shared.InstStatus(self, vCode)
                msg.exec()

        self.parent.liaStatus.print_info()  # auto refresh status panel

    def reset(self):

        if self.parent.testModeAction.isChecked():
            # fake a successful communication on test mode
            vCode = pyvisa.constants.StatusCode.success
        else:
            vCode = api_lia.reset(self.parent.liaHandle)

        if vCode == pyvisa.constants.StatusCode.success:
            self.parent.liaStatus.manual_refresh()
        else:
            msg = Shared.InstStatus(self, vCode)
            msg.exec()


class ScopeCtrl(QtWidgets.QGroupBox):

    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self, parent)
        self.parent = parent

        self.setTitle('Oscilloscope Control')
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self.setCheckable(True)
        self.setChecked(False)

        ## -- Define layout elements --
        self.srateFill = QtWidgets.QLineEdit()
        self.slenFill = QtWidgets.QLineEdit()
        sensSel = QtWidgets.QComboBox()
        sensList = ['20 V', '5 V', '1 V', '0.5 V', '0.2 V']
        sensSel.addItems(sensList)
        self.avgFill = QtWidgets.QLineEdit()

        ## -- Set up main layout --
        mainLayout = QtWidgets.QFormLayout()
        mainLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        mainLayout.addRow(QtWidgets.QLabel('Sample Rate (MHz)'), self.srateFill)
        mainLayout.addRow(QtWidgets.QLabel('Sample Length'), self.slenFill)
        mainLayout.addRow(QtWidgets.QLabel('Sensitivity'), sensSel)
        mainLayout.addRow(QtWidgets.QLabel('Oscilloscope Average'), self.avgFill)
        self.setLayout(mainLayout)

        ## -- Trigger setting status and communication
        self.srateFill.textChanged.connect(self.rateComm)
        self.slenFill.textChanged.connect(self.lenComm)
        sensSel.currentIndexChanged.connect(self.tune_sensitivity)
        self.avgFill.textChanged.connect(self.avgComm)
        self.clicked.connect(self.check)

    def check(self):
        ''' Enable/disable this groupbox '''
        if (self.parent.testModeAction.isChecked() or self.parent.pciHandle):
            self.setChecked(True)
        else:
            msg = Shared.MsgError(self, 'No Instrument!', 'No oscilloscope is connected!')
            msg.exec()
            self.setChecked(False)

    def rateComm(self, rate_text):

        status = api_pci.set_sampling_rate(rate_text)
        self.srateFill.setStyleSheet('border: 1px solid {:s}'.format(Shared.msgcolor(status)))

    def lenComm(self, len_text):

        status = api_pci.set_sampling_len(len_text)
        self.slenFill.setStyleSheet('border: 1px solid {:s}'.format(Shared.msgcolor(status)))

    def tune_sensitivity(self, sens_index):

        status = api_pci.set_sens(sens_index)

    def avgComm(self, avg_text):

        status = api_pci.set_osc_avg(avg_text)
        self.avgFill.setStyleSheet('border: 1px solid {:s}'.format(Shared.msgcolor(status)))


class MotorCtrl(QtWidgets.QGroupBox):

    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self, parent)
        self.parent = parent

        self.setTitle('Cavity Control')
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self.setCheckable(True)
        self.setChecked(False)

        tuneButton = QtWidgets.QPushButton('Tune Cavity')
        mainLayout = QtWidgets.QHBoxLayout()
        mainLayout.addWidget(tuneButton)
        self.setLayout(mainLayout)

        ## -- Trigger settings and motor communication
        tuneButton.clicked.connect(self.tune_cavity)
        self.clicked.connect(self.check)

    def check(self):
        ''' Enable/disable this groupbox '''
        if (self.parent.testModeAction.isChecked() or self.parent.motorHandle):
            self.setChecked(True)
        else:
            msg = Shared.MsgError(self, 'No Instrument!', 'No oscilloscope is connected!')
            msg.exec()
            self.setChecked(False)

    def tune_cavity(self):

        status = api_motor.move(self.parent.motorHandle, 1)


class ScopeMonitor(QtWidgets.QWidget):

    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self, parent)
        self.parent = parent

        self.pgPlot = pg.PlotWidget(title='Oscilloscope Monitor')
        mainLayout = QtWidgets.QGridLayout()
        mainLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        mainLayout.addWidget(self.pgPlot, 0, 0)
        self.setLayout(mainLayout)

    def plot(self):
        pass


class LockinMonitor(QtWidgets.QWidget):

    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self, parent)
        self.parent = parent
        self.counter = 0  # data points counter

        self.slenFill = QtWidgets.QLineEdit()
        self.slenFill.setText('100')
        self.slenFill.setStyleSheet('border: 1px solid {:s}'.format(Shared.msgcolor(2)))
        self.data = np.zeros(100)
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
        self.curve = self.pgPlot.plot(self.data)
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        mainLayout.addWidget(self.pgPlot)
        mainLayout.addWidget(settingPanel)
        self.setLayout(mainLayout)

        # set up timer
        self.timer = QtCore.QTimer()
        self.set_waittime()

        # trigger settings
        self.yMaxSel.currentIndexChanged.connect(self.rescale)
        self.slenFill.textChanged.connect(self.set_len)
        self.startButton.clicked.connect(self.start)
        self.restartButton.clicked.connect(self.restart)
        self.stopButton.clicked.connect(self.stop)
        self.updateRate.currentIndexChanged.connect(self.set_waittime)
        self.timer.timeout.connect(self.update_plot)

    def rescale(self, idx):

        self.pgPlot.setYRange(0, 10 ** (-idx))

    def start(self, btn_pressed):

        if btn_pressed:
            self.startButton.setText('Pause')
            self.timer.start()
        else:
            self.startButton.setText('Continue')
            self.timer.stop()

    def restart(self):

        self.counter = 0  # reset counter
        self.startButton.setChecked(True)  # retrigger start button
        self.startButton.setText('Pause')
        self.timer.start()

    def stop(self):

        self.timer.stop()
        self.counter = 0
        self.startButton.setChecked(False)  # reset start button
        self.startButton.setText('Start')

    def set_len(self, text):
        status, slen = api_val.val_monitor_sample_len(text)
        self.slenFill.setStyleSheet('border: 1px solid {:s}'.format(Shared.msgcolor(status)))
        if status:
            self.data = np.zeros(slen)
            self.restart()
        else:
            self.stop()

    def set_waittime(self):
        ''' Set wait time according to self.updateRate '''

        status, waittime = api_val.val_lia_monitor_srate(self.updateRate.currentIndex(), self.parent.liaInfo.tcIndex)
        self.timer.setInterval(int(waittime))
        self.updateRate.setStyleSheet('border: 1px solid {:s}'.format(Shared.msgcolor(status)))
        if status:
            pass
        else:
            msg = Shared.MsgWarning(self, 'Update speed warning!',
                                    '''The picked update speed is faster than the lockin time constant.
                                    Automatically reset the update speed to 3pi * time_constant ''')
            msg.exec()
            self.updateRate.setCurrentIndex(7)

    def daq(self):
        ''' If sampled points are less than the set length, fill up the array
            If sampled points are more than the set length, roll the array
            forward and fill the last array element with new data
        '''

        if self.counter < len(self.data):
            self.data[self.counter] = api_lia.query_single_x(self.parent.liaHandle)
            self.counter += 1
        else:
            self.data = np.roll(self.data, len(self.data) - 1)
            self.data[-1] = api_lia.query_single_x(self.parent.liaHandle)

    def update_plot(self):
        self.daq()
        if self.counter < len(self.data):
            self.curve.setData(self.data[0:self.counter])
        else:
            self.curve.setData(self.data)


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
