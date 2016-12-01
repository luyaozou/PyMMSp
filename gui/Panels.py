#! encoding = utf-8
''' GUI Panels. '''

# import standard libraries
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import QObject
import pyqtgraph as pg
import pyvisa
import numpy as np
# import shared gui widgets
from gui import SharedWidgets as Shared
from gui import Dialogs
# import instrument api
from api import synthesizer as apisyn
from api import lockin as apilc
from api import pci as apipci
from api import validator as apival


class SynStatus(QtGui.QGroupBox):
    '''
        Synthesizer status display
    '''

    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.parent = parent

        self.setTitle('Synthesizer Status')
        self.setAlignment(QtCore.Qt.AlignLeft)
        self.setCheckable(False)

        ## -- Define synthesizer status elements --
        refreshButton = QtGui.QPushButton('Refresh')
        moreInfoButton = QtGui.QPushButton('More Info')
        self.addressText = QtGui.QLabel()
        self.synRF = QtGui.QLabel()
        self.synPower = QtGui.QLabel()
        self.synFreq = QtGui.QLabel()
        self.synMod = QtGui.QLabel()
        self.synAMStat = QtGui.QLabel()
        self.synFMStat = QtGui.QLabel()
        self.synAMDepth = QtGui.QLabel()
        self.synAMFreq = QtGui.QLabel()
        self.synFMDev = QtGui.QLabel()
        self.synFMFreq = QtGui.QLabel()
        self.synLF = QtGui.QLabel()
        self.synLFV = QtGui.QLabel()
        self.errMsgLabel = QtGui.QLabel()
        errMsgBtn = QtGui.QPushButton('Pop Err Msg')

        # put modulation settings in a groupbox
        modGroup = QtGui.QGroupBox()
        modGroup.setTitle('Mod Settings')
        modGroup.setAlignment(QtCore.Qt.AlignLeft)
        modGroup.setCheckable(False)
        modGroupLayout = QtGui.QGridLayout()
        modGroupLayout.addWidget(QtGui.QLabel('AM1'), 0, 1)
        modGroupLayout.addWidget(QtGui.QLabel('FM1'), 0, 2)
        modGroupLayout.addWidget(QtGui.QLabel('Status'), 1, 0)
        modGroupLayout.addWidget(self.synAMStat, 1, 1)
        modGroupLayout.addWidget(self.synFMStat, 1, 2)
        modGroupLayout.addWidget(QtGui.QLabel('Freq'), 2, 0)
        modGroupLayout.addWidget(self.synAMFreq, 2, 1)
        modGroupLayout.addWidget(self.synFMFreq, 2, 2)
        modGroupLayout.addWidget(QtGui.QLabel('Amp'), 3, 0)
        modGroupLayout.addWidget(self.synAMDepth, 3, 1)
        modGroupLayout.addWidget(self.synFMDev, 3, 2)
        modGroup.setLayout(modGroupLayout)

        ## -- Set layout and add GUI elements
        mainLayout = QtGui.QGridLayout()
        mainLayout.setAlignment(QtCore.Qt.AlignTop)
        # first column
        mainLayout.addWidget(refreshButton, 0, 0, 1, 2)
        mainLayout.addWidget(moreInfoButton, 0, 2, 1, 2)
        mainLayout.addWidget(QtGui.QLabel('Inst. Name'), 1, 0)
        mainLayout.addWidget(self.addressText, 1, 1, 1, 3)
        mainLayout.addWidget(QtGui.QLabel('Frequency'), 2, 0)
        mainLayout.addWidget(self.synFreq, 2, 1, 1, 3)
        mainLayout.addWidget(QtGui.QLabel('RF Output'), 3, 0)
        mainLayout.addWidget(self.synRF, 3, 1)
        mainLayout.addWidget(QtGui.QLabel('Power'), 4, 0)
        mainLayout.addWidget(self.synPower, 4, 1)
        mainLayout.addWidget(QtGui.QLabel('Modulation'), 5, 0)
        mainLayout.addWidget(self.synMod, 5, 1)
        mainLayout.addWidget(QtGui.QLabel('LF Output'), 6, 0)
        mainLayout.addWidget(self.synLF, 6, 1)
        mainLayout.addWidget(QtGui.QLabel('LF Voltage'), 7, 0)
        mainLayout.addWidget(self.synLFV, 7, 1)
        self.setLayout(mainLayout)
        # second column
        mainLayout.addWidget(modGroup, 3, 2, 5, 2)
        mainLayout.addWidget(errMsgBtn, 8, 0)
        mainLayout.addWidget(self.errMsgLabel, 8, 1, 1, 3)

        # this dialog is a child class of the main window
        self.infoDialog = Dialogs.SynInfoDialog(self.parent)
        ## -- Trigger status updates
        refreshButton.clicked.connect(self.update)
        moreInfoButton.clicked.connect(self.show_info_dialog)
        errMsgBtn.clicked.connect(self.pop_err_msg)
        # initial status
        self.update()

    def update(self):
        ''' Update instrument information '''
        if self.parent.synHandle:
            self.addressText.setText(self.parent.synHandle.resource_name)
            self.synRF.setText('On' if apisyn.read_power_toggle(self.parent.synHandle) else 'Off')
            self.synPower.setText('{:.1f} dbm'.format(apisyn.read_syn_power(self.parent.synHandle)))
            self.synFreq.setText(pg.siFormat(apisyn.read_syn_freq(self.parent.synHandle), suffix='Hz', precision=12))
            self.synMod.setText('On' if apisyn.read_mod_toggle(self.parent.synHandle) else 'Off')
            amfreq, amdepth, amstat = apisyn.read_am_par(self.parent.synHandle)
            fmfreq, fmdev, fmstat = apisyn.read_fm_par(self.parent.synHandle)
            self.synAMStat.setText('On' if amstat else 'Off')
            self.synFMStat.setText('On' if fmstat else 'Off')
            self.synAMDepth.setText('{:.1f} %'.format(amdepth))
            self.synAMFreq.setText(pg.siFormat(amfreq, suffix='Hz', precision=4))
            self.synFMDev.setText(pg.siFormat(fmdev, suffix='Hz', precision=4))
            self.synFMFreq.setText(pg.siFormat(fmfreq, suffix='Hz', precision=4))
            lf_vol, lf_status = apisyn.read_lf(self.parent.synHandle)
            self.synLF.setText('On' if lf_status else 'Off')
            self.synLFV.setText(pg.siFormat(lf_vol, suffix='V'))
            self.errMsgLabel.setText(apisyn.query_err_msg(self.parent.synHandle))
        else:
            self.addressText.setText('N.A.')
            self.synRF.setText('N.A.')
            self.synPower.setText('N.A.')
            self.synFreq.setText('N.A.')
            self.synMod.setText('N.A.')
            self.synAMStat.setText('N.A.')
            self.synFMStat.setText('N.A.')
            self.synAMDepth.setText('N.A.')
            self.synAMFreq.setText('N.A.')
            self.synFMDev.setText('N.A.')
            self.synFMFreq.setText('N.A.')
            self.synLF.setText('N.A.')
            self.synLFV.setText('N.A.')
            self.errMsgLabel.setText('N.A.')

    def show_info_dialog(self):

        self.infoDialog.display()

    def pop_err_msg(self):
        ''' Pop error message '''
        if self.parent.synHandle:
            self.errMsgLabel.setText(apisyn.query_err_msg(self.parent.synHandle))
        else:
            pass


class LockinStatus(QtGui.QGroupBox):
    '''
        Lockin status display
    '''

    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.parent = parent

        self.setTitle('Lockin Status')
        self.setAlignment(QtCore.Qt.AlignLeft)
        self.setCheckable(False)

        ## -- Define synthesizer status elements --
        refreshButton = QtGui.QPushButton('Refresh')
        moreInfoButton = QtGui.QPushButton('More Info')
        errMsgBtn = QtGui.QPushButton('Pop Err Msg')
        self.addressText = QtGui.QLabel()
        self.lcHarmLabel = QtGui.QLabel()
        self.lcPhaseLabel = QtGui.QLabel()
        self.lcFreqLabel = QtGui.QLabel()
        self.lcSensLabel = QtGui.QLabel()
        self.lcTCLabel = QtGui.QLabel()
        self.lcCoupleLabel = QtGui.QLabel()
        self.lcReserveLabel = QtGui.QLabel()
        self.lcGroundingLabel = QtGui.QLabel()
        self.lcFilterLabel = QtGui.QLabel()
        self.errMsgLabel = QtGui.QLabel('N.A.')

        ## -- Set layout and add GUI elements
        mainLayout = QtGui.QGridLayout()
        mainLayout.setAlignment(QtCore.Qt.AlignTop)
        # first column
        mainLayout.addWidget(refreshButton, 0, 0, 1, 2)
        mainLayout.addWidget(moreInfoButton, 0, 2, 1, 2)
        mainLayout.addWidget(QtGui.QLabel('Inst. Name'), 1, 0)
        mainLayout.addWidget(self.addressText, 1, 1, 1, 3)
        mainLayout.addWidget(QtGui.QLabel('Harmonics'), 2, 0)
        mainLayout.addWidget(self.lcHarmLabel, 2, 1)
        mainLayout.addWidget(QtGui.QLabel('Phase'), 3, 0)
        mainLayout.addWidget(self.lcPhaseLabel, 3, 1)
        mainLayout.addWidget(QtGui.QLabel('Sensitivity'), 4, 0)
        mainLayout.addWidget(self.lcSensLabel, 4, 1)
        mainLayout.addWidget(QtGui.QLabel('Time Constant'), 5, 0)
        mainLayout.addWidget(self.lcTCLabel, 5, 1)
        mainLayout.addWidget(QtGui.QLabel('Locked Freq'), 6, 0)
        mainLayout.addWidget(self.lcFreqLabel, 6, 1)
        mainLayout.addWidget(errMsgBtn, 7, 0)
        mainLayout.addWidget(self.errMsgLabel, 7, 1, 1, 3)
        # second column
        mainLayout.addWidget(QtGui.QLabel('Couple'), 2, 2)
        mainLayout.addWidget(self.lcCoupleLabel, 2, 3)
        mainLayout.addWidget(QtGui.QLabel('Reserve'), 3, 2)
        mainLayout.addWidget(self.lcReserveLabel, 3, 3)
        mainLayout.addWidget(QtGui.QLabel('Grouding'), 4, 2)
        mainLayout.addWidget(self.lcGroundingLabel, 4, 3)
        mainLayout.addWidget(QtGui.QLabel('Filter'), 5, 2)
        mainLayout.addWidget(self.lcFilterLabel, 5, 3)
        self.setLayout(mainLayout)

        # this dialog is a child class of the main window
        self.infoDialog = Dialogs.LockinInfoDialog(self.parent)
        ## -- Trigger status updates
        errMsgBtn.clicked.connect(self.pop_err_msg)
        refreshButton.clicked.connect(self.update)
        moreInfoButton.clicked.connect(self.show_info_dialog)
        # initial status
        self.update()

    def update(self):
        ''' Update instrument information '''
        if self.parent.lcHandle:
            self.addressText.setText(self.parent.lcHandle.resource_name)
            self.lcHarmLabel.setText('{:d}'.format(apilc.read_harm(self.parent.lcHandle)))
            self.lcPhaseLabel.setText('{:.2f} deg'.format(apilc.read_phase(self.parent.lcHandle)))
            self.lcFreqLabel.setText(pg.siFormat(apilc.read_freq(self.parent.lcHandle), suffix='Hz'))
            self.lcSensLabel.setText(Shared.LIASENSLIST[apilc.read_sens(self.parent.lcHandle)])
            self.lcTCLabel.setText(Shared.LIATCLIST[apilc.read_tc(self.parent.lcHandle)])
            self.lcCoupleLabel.setText(apilc.read_couple(self.parent.lcHandle))
            self.lcReserveLabel.setText(apilc.read_reserve(self.parent.lcHandle))
            self.lcGroundingLabel.setText(apilc.read_input_grounding(self.parent.lcHandle))
            self.lcFilterLabel.setText(apilc.read_input_filter(self.parent.lcHandle))
        else:
            self.addressText.setText('N.A.')
            self.lcHarmLabel.setText('N.A.')
            self.lcPhaseLabel.setText('N.A.')
            self.lcFreqLabel.setText('N.A.')
            self.lcSensLabel.setText('N.A.')
            self.lcTCLabel.setText('N.A.')
            self.lcCoupleLabel.setText('N.A.')
            self.lcReserveLabel.setText('N.A.')
            self.lcGroundingLabel.setText('N.A.')
            self.lcFilterLabel.setText('N.A.')

    def show_info_dialog(self):

        self.infoDialog.display()

    def pop_err_msg(self):
        ''' Pop error message '''
        if self.parent.lcHandle:
            self.errMsgBtn.setText(apilc.query_err_msg(self.parent.lcHandle))
        else:
            pass

class ScopeStatus(QtGui.QGroupBox):
    '''
        Oscilloscope (PCI card) status display
    '''

    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.parent = parent

        self.setTitle('Oscilloscope Status')
        self.setAlignment(QtCore.Qt.AlignLeft)
        self.setCheckable(False)

        ## -- Define synthesizer status elements --
        self.refreshButton = QtGui.QPushButton('Refresh')
        self.moreInfoButton = QtGui.QPushButton('More Info')
        self.addressText = QtGui.QLabel()

        ## -- Set layout and add GUI elements
        mainLayout = QtGui.QGridLayout()
        mainLayout.setAlignment(QtCore.Qt.AlignTop)
        mainLayout.addWidget(self.refreshButton, 0, 0, 1, 2)
        mainLayout.addWidget(self.moreInfoButton, 0, 2, 1, 2)
        mainLayout.addWidget(QtGui.QLabel('Inst. Name'), 1, 0)
        mainLayout.addWidget(self.addressText, 1, 1)
        self.setLayout(mainLayout)

        ## -- Trigger status updates
        self.refreshButton.clicked.connect(self.update)
        # initial status
        self.update()

    def update(self):
        ''' Update instrument information '''

        if self.parent.pciHandle:
            self.addressText.setText(self.parent.pciHandle.resource_name)
        else:
            self.addressText.setText('N.A.')

class SynCtrl(QtGui.QGroupBox):
    '''
        Synthesizer control panel
    '''

    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.parent = parent

        self.setTitle('Synthesizer Control')
        self.setAlignment(QtCore.Qt.AlignLeft)    # align left
        self.setCheckable(True)
        self.setChecked(False)

        ## -- Define synthesizer control elements --
        syn = QtGui.QWidget()
        self.synfreqLabel = QtGui.QLabel('{:.9f} MHz'.format(30000))
        self.probfreqFill = QtGui.QLineEdit()
        self.probfreqFill.setText('180000')
        self.bandSelect = Shared.VDIBandComboBox()

        ## -- Set up synthesizer control layout --
        synLayout = QtGui.QGridLayout()
        synLayout.addWidget(QtGui.QLabel('Synthesizer Frequency'), 0, 0)
        synLayout.addWidget(self.synfreqLabel, 0, 1, 1, 2)
        synLayout.addWidget(QtGui.QLabel('Probing Frequency'), 1, 0)
        synLayout.addWidget(self.probfreqFill, 1, 1)
        synLayout.addWidget(QtGui.QLabel('MHz'), 1, 2)
        synLayout.addWidget(QtGui.QLabel('VDI Band'), 2, 0)
        synLayout.addWidget(self.bandSelect, 2, 1, 1, 3)
        syn.setLayout(synLayout)

        # Set up modulation child widget
        modGBox = QtGui.QGroupBox()
        modGBox.setTitle('Modulation Control')
        modGBox.setFlat(True)
        modGBox.setAlignment(QtCore.Qt.AlignLeft)
        modLayout = QtGui.QGridLayout()
        modLayout.setSpacing(0)

        self.modModeSel = QtGui.QComboBox()
        self.modModeSel.addItems(['None', 'AM', 'FM'])

        self.modFreq = QtGui.QWidget()
        self.modFreqFill = QtGui.QLineEdit()
        self.modFreqUnitSel = QtGui.QComboBox()
        self.modFreqUnitSel.addItems(['Hz', 'kHz'])
        self.modFreqUnitSel.setCurrentIndex(1)
        modFreqLayout = QtGui.QHBoxLayout()
        modFreqLayout.addWidget(QtGui.QLabel('Mod Freq'))
        modFreqLayout.addWidget(self.modFreqFill)
        modFreqLayout.addWidget(self.modFreqUnitSel)
        self.modFreq.setLayout(modFreqLayout)

        self.modDepth = QtGui.QWidget()
        self.modDepthFill = QtGui.QLineEdit()
        self.modDepthUnitSel = QtGui.QComboBox()
        self.modDepthUnitSel.addItems('')
        modDepthLayout = QtGui.QHBoxLayout()
        modDepthLayout.addWidget(QtGui.QLabel('Mod Amp'))
        modDepthLayout.addWidget(self.modDepthFill)
        modDepthLayout.addWidget(self.modDepthUnitSel)
        self.modDepth.setLayout(modDepthLayout)

        self.lfVol = QtGui.QWidget()
        self.lfVolFill = QtGui.QLineEdit()
        lfLayout = QtGui.QHBoxLayout()
        lfLayout.addWidget(QtGui.QLabel('LF Voltage'))
        lfLayout.addWidget(self.lfVolFill)
        lfLayout.addWidget(QtGui.QLabel('V'))
        self.lfVol.setLayout(lfLayout)

        self.modSwitchBtn = QtGui.QPushButton('OFF')
        self.modSwitchBtn.setCheckable(True)
        self.lfSwitchBtn = QtGui.QPushButton('OFF')
        self.lfSwitchBtn.setCheckable(True)

        modLayout.addWidget(QtGui.QLabel('Mod Mode'), 0, 0)
        modLayout.addWidget(QtGui.QLabel('Mod Switch'), 1, 0)
        modLayout.addWidget(QtGui.QLabel('LF Switch'), 2, 0)
        modLayout.addWidget(self.modModeSel, 0, 1)
        modLayout.addWidget(self.modSwitchBtn, 1, 1)
        modLayout.addWidget(self.lfSwitchBtn, 2, 1)
        modLayout.addWidget(self.modFreq, 0, 2, 1, 3)
        modLayout.addWidget(self.modDepth, 1, 2, 1, 3)
        modLayout.addWidget(self.lfVol, 2, 2, 1, 3)
        modGBox.setLayout(modLayout)
        self.modFreq.hide()
        self.modDepth.hide()
        self.lfVol.hide()

        ## -- Define synthesizer power switch
        self.synPowerSwitchBtn = QtGui.QPushButton('OFF')
        self.synPowerSwitchBtn.setCheckable(True)
        synPowerManualInput = QtGui.QPushButton('Set Power')

        synPowerLayout = QtGui.QHBoxLayout()
        synPowerLayout.setAlignment(QtCore.Qt.AlignLeft)
        synPowerLayout.addWidget(synPowerManualInput)
        synPowerLayout.addWidget(QtGui.QLabel('RF Switch'))
        synPowerLayout.addWidget(self.synPowerSwitchBtn)
        synPowerCtrl = QtGui.QWidget()
        synPowerCtrl.setLayout(synPowerLayout)

        self.powerSwitchTimer = QtCore.QTimer()
        self.powerSwitchTimer.setInterval(1000)
        self.powerSwitchTimer.setSingleShot(True)
        self.powerSwitchProgBar = QtGui.QProgressBar()
        self.progDialog = QtGui.QDialog()
        self.progDialog.setWindowTitle('RF Ramp')
        progDialogLayout = QtGui.QVBoxLayout()
        progDialogLayout.addWidget(self.powerSwitchProgBar)
        self.progDialog.setLayout(progDialogLayout)

        ## -- Set up main layout
        mainLayout = QtGui.QVBoxLayout()
        mainLayout.setAlignment(QtCore.Qt.AlignTop)
        mainLayout.addWidget(synPowerCtrl)
        mainLayout.addWidget(syn)
        mainLayout.addWidget(modGBox)
        self.setLayout(mainLayout)

        # Trigger frequency update and communication
        self.probfreqFill.textChanged.connect(self.tune_freq)
        self.bandSelect.currentIndexChanged.connect(self.tune_freq)

        # Trigger modulation status update and communication
        self.modModeSel.currentIndexChanged.connect(self.activate_modWidgets)
        self.modFreqFill.textChanged.connect(self.tune_mod_parameter)
        self.modFreqUnitSel.currentIndexChanged.connect(self.tune_mod_parameter)
        self.modDepthFill.textChanged.connect(self.tune_mod_parameter)
        self.modDepthUnitSel.currentIndexChanged.connect(self.tune_mod_parameter)
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

        if self.parent.synHandle:
            self.setChecked(True)
        else:
            msg = Shared.MsgError(self, 'No Instrument!', 'No synthesizer is connected!')
            msg.exec_()
            self.setChecked(False)

        self.parent.synStatus.update()

    def tune_freq(self):
        '''
            Communicate with the synthesizer and update frequency setting.
        '''

        # validate input
        status, synfreq = apival.val_syn_freq(self.probfreqFill.text(),
                                              self.bandSelect.currentIndex())
        # set sheet border color by syn_stat
        self.probfreqFill.setStyleSheet('border: 1px solid {:s}'.format(Shared.msgcolor(status)))

        if status:  # if status is not fatal
            # call syn api and return communication status
            vCode = apisyn.set_syn_freq(self.parent.synHandle, synfreq)
            if vCode == pyvisa.constants.StatusCode.success:
                pass
            else:
                msg = Shared.InstStatus(self, vCode)
                msg.exec_()
            # update synthesizer status
            self.parent.synStatus.update()
            self.synfreqLabel.setText('{:.9f} MHz'.format(synfreq))
        else:   # else ignore change
            pass

    def ramp_synRFPower(self):
        '''
            The actual synthesizer api command.
            Triggered by self.powerSwitchTimer.timeout
            Returns successful status
        '''

        try:
            this_power = next(self.ramper)
            vCode = apisyn.set_syn_power(self.parent.synHandle, this_power)
            if vCode == pyvisa.constants.StatusCode.success:
                self.parent.synStatus.update()
                self.powerSwitchProgBar.setValue(self.powerSwitchProgBar.value() + 1)
                # start timer
                self.powerSwitchTimer.start()
            else:
                self.powerSwitchTimer.stop()
                msg = Shared.InstStatus(self, vCode)
                msg.exec_()
        except StopIteration:
            self.powerSwitchTimer.stop()
            self.progDialog.accept()

    def synRFPower_manual(self):
        '''
            Communicate with the synthesizer and set up RF power
            (automatically turn RF on)
        '''

        # Get current syn power
        current_power = apisyn.read_syn_power(self.parent.synHandle)
        # Grab manual input power
        target_power, okay = QtGui.QInputDialog.getInt(self, 'RF Power',
                        'Manual Input (-20 to 0)', current_power, -20, 0, 1)

        if okay:    # hopefully no error occurs
            # turn on RF toggle first
            apisyn.set_power_toggle(self.parent.synHandle, True)
            self.synPowerSwitchBtn.setChecked(True)
            self.powerSwitchProgBar.setRange(0, abs(current_power - target_power))
            self.powerSwitchProgBar.setValue(0)
            if current_power > target_power:
                self.ramper = apisyn.ramp_down(current_power, target_power)
            else:
                self.ramper = apisyn.ramp_up(current_power, target_power)
            self.ramp_synRFPower()
            self.progDialog.exec_()
        else:
            pass

    def synRFPower_auto(self, btn_pressed):
        '''
            Automatically switch synthesizer RF on/off
        '''

        # Get current syn power
        current_power = apisyn.read_syn_power(self.parent.synHandle)

        if btn_pressed: # user wants to turn on
            apisyn.set_power_toggle(self.parent.synHandle, True)
            self.ramper = apisyn.ramp_up(current_power, 0)
            self.powerSwitchProgBar.setRange(0, abs(current_power))
            self.powerSwitchProgBar.setValue(0)
            self.ramp_synRFPower()
            self.progDialog.exec_()
        else:   # user wants to turn off
            self.ramper = apisyn.ramp_down(current_power, -20)
            self.powerSwitchProgBar.setRange(0, abs(current_power + 20))
            self.powerSwitchProgBar.setValue(0)
            self.ramp_synRFPower()
            result = self.progDialog.exec_()
            # RF protection before turn off
            current_power = apisyn.read_syn_power(self.parent.synHandle)
            if result and (current_power <= -20):
            # safely turn off RF
                apisyn.set_power_toggle(self.parent.synHandle, False)
                self.synPowerSwitchBtn.setChecked(False)
            else:
                self.synPowerSwitchBtn.setChecked(True)

        self.parent.synStatus.update()

    def set_synPowerSwitchBtn_label(self, toggle_state):
        '''
            Set power switch button text
        '''

        if toggle_state:
            self.synPowerSwitchBtn.setText('ON')
        else:
            self.synPowerSwitchBtn.setText('OFF')

    def activate_modWidgets(self):
        '''
            Activate/deactivate modulation setting widgets
        '''

        mod_index = self.modModeSel.currentIndex()
        self.tune_mod_mode(mod_index)

        if mod_index == 1:
            if self.modDepthUnitSel.count() == 1:  # it has been set to AM
                pass
            else:
                self.modFreqFill.setText('{:.3f}'.format(15))
                self.modDepthFill.setText('{:.1f}'.format(0))
                for i in range(self.modDepthUnitSel.count()): # remove all items
                    self.modDepthUnitSel.removeItem(0)
                self.modDepthUnitSel.addItems(['%'])
                # fill in default parameters
                self.modFreqUnitSel.setCurrentIndex(1)
                self.modDepthUnitSel.setCurrentIndex(0)
        elif mod_index == 2:
            if self.modDepthUnitSel.count() == 3:  # it has been set to FM
                pass
            else:
                self.modFreqFill.setText('{:.3f}'.format(15))
                self.modDepthFill.setText('{:.3f}'.format(75))
                for i in range(self.modDepthUnitSel.count()): # remove all items
                    self.modDepthUnitSel.removeItem(0)
                self.modDepthUnitSel.addItems(['Hz', 'kHz', 'MHz'])
                # update parameters
                self.modFreqUnitSel.setCurrentIndex(1)
                self.modDepthUnitSel.setCurrentIndex(1)
        else:
            pass

        if mod_index:
            self.modFreq.show()     # Modulation selected. Show modulation widget
            self.modDepth.show()
            self.lfSwitchBtn.show()
            self.lfVol.show()
        else:
            self.modFreq.hide()     # No modulation. Hide modulation widget
            self.modDepth.hide()
            self.lfSwitchBtn.hide()
            self.lfVol.hide()

    def tune_mod_mode(self, mod_index):
        '''
            Communicate with the synthesizer and update modulation mode.
        '''

        vCode = apisyn.set_mod_mode(self.parent.synHandle, mod_index)
        if vCode == pyvisa.constants.StatusCode.success:
            pass
        else:
            msg = Shared.InstStatus(self, vCode)
            msg.exec_()

        self.parent.synStatus.update()

    def tune_mod_parameter(self):
        '''
            Communicate with the synthesizer and update modulation parameters
        '''

        mod_index = self.modModeSel.currentIndex()
        toggle_state = self.modSwitchBtn.isChecked()

        # convert input and set sheet border color by status
        freq_status, mod_freq = apival.val_syn_mod_freq(self.modFreqFill.text(),
                                       self.modFreqUnitSel.currentText())
        self.modFreqFill.setStyleSheet('border: 1px solid {:s}'.format(Shared.msgcolor(freq_status)))

        depth_status, mod_depth = apival.val_syn_mod_depth(self.modDepthFill.text(),
                                         self.modDepthUnitSel.currentText())
        self.modDepthFill.setStyleSheet('border: 1px solid {:s}'.format(Shared.msgcolor(depth_status)))

        if freq_status and depth_status:
            if mod_index == 1:      # AM
                vCode = apisyn.set_am(self.parent.synHandle, mod_freq,
                                      mod_depth, toggle_state)
            elif mod_index == 2:    # FM
                vCode = apisyn.set_fm(self.parent.synHandle, mod_freq,
                                      mod_depth, toggle_state)
            else:
                vCode = pyvisa.constants.StatusCode.success

            if vCode == pyvisa.constants.StatusCode.success:
                self.parent.synStatus.update()
            else:
                msg = Shared.InstStatus(self, vCode)
                msg.exec_()
        else:
            pass

    def switch_modulation(self, btn_pressed):
        '''
            Communicate with the synthesizer and update modulation on/off toggle
        '''

        vCode = apisyn.set_mod_toggle(self.parent.synHandle, btn_pressed)

        if btn_pressed:
            self.modSwitchBtn.setText('ON')
        else:
            self.modSwitchBtn.setText('OFF')

        self.parent.synStatus.update()


    def switch_lf(self, btn_pressed):
        '''
            Communicate with the synthesizer and update LF on/off toggle
        '''

        vCode = apisyn.set_lf_toggle(self.parent.synHandle, btn_pressed)

        if btn_pressed:
            self.lfSwitchBtn.setText('ON')
            self.lfVolFill.setText('0.1')   # default value
        else:
            self.lfSwitchBtn.setText('OFF')
            self.lfVolFill.setText('0')

        self.parent.synStatus.update()

    def tune_lf(self, vol_text):
        '''
            Communicate with the synthesizer and update LF voltage
        '''

        status, lf_vol = apival.val_syn_lf_vol(vol_text)
        self.lfVolFill.setStyleSheet('border: 1px solid {:s}'.format(Shared.msgcolor(status)))

        if status:
            vCode = apisyn.set_lf_amp(self.parent.synHandle, lf_vol)
            if vCode == pyvisa.constants.StatusCode.success:
                pass
            else:
                msg = Shared.InstStatus(self, vCode)
                msg.exec_()
            self.parent.synStatus.update()
        else:
            pass


class LockinCtrl(QtGui.QGroupBox):

    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.parent = parent

        self.setTitle('Lockin Control')
        self.setAlignment(QtCore.Qt.AlignLeft)        # align left
        self.setCheckable(True)
        self.setChecked(False)

        ## -- Define layout elements --
        harmSelect = QtGui.QComboBox()
        harmSelect.addItems(['1', '2', '3', '4'])
        harmSelect.setCurrentIndex(0)
        self.phaseFill = QtGui.QLineEdit('0')
        self.sensSelect = Shared.lcSensBox()
        tcSelect = Shared.lcTcBox()
        coupleSelect = QtGui.QComboBox()
        coupleSelect.addItems(['AC', 'DC'])
        coupleSelect.setCurrentIndex(1)
        reserveSelect = QtGui.QComboBox()
        reserveSelect.addItems(['High Reserve', 'Normal', 'Low Noise'])
        reserveSelect.setCurrentIndex(1)
        groundingSelect = QtGui.QComboBox()
        groundingSelect.addItems(['Float', 'Ground'])
        groundingSelect.setCurrentIndex(1)
        filterSelect = QtGui.QComboBox()
        filterSelect.addItems(['None', 'Line notch', '2× Line notch', 'Both'])
        filterSelect.setCurrentIndex(1)
        autoPhaseBtn = QtGui.QPushButton('Auto Phase')
        resetBtn = QtGui.QPushButton('Reset')

        ## -- Set up main layout --
        mainLayout = QtGui.QGridLayout()
        mainLayout.setAlignment(QtCore.Qt.AlignTop)
        mainLayout.addWidget(QtGui.QLabel('Harmonics'), 0, 0)
        mainLayout.addWidget(harmSelect, 0, 1)
        mainLayout.addWidget(QtGui.QLabel('Phase'), 1, 0)
        mainLayout.addWidget(self.phaseFill, 1, 1)
        mainLayout.addWidget(QtGui.QLabel('Sensitivity'), 2, 0)
        mainLayout.addWidget(self.sensSelect, 2, 1)
        mainLayout.addWidget(QtGui.QLabel('Time Constant'), 3, 0)
        mainLayout.addWidget(tcSelect, 3, 1)
        mainLayout.addWidget(QtGui.QLabel('Couple'), 0, 2)
        mainLayout.addWidget(coupleSelect, 0, 3)
        mainLayout.addWidget(QtGui.QLabel('Reserve'), 1, 2)
        mainLayout.addWidget(reserveSelect, 1, 3)
        mainLayout.addWidget(QtGui.QLabel('Grouding'), 2, 2)
        mainLayout.addWidget(groundingSelect, 2, 3)
        mainLayout.addWidget(QtGui.QLabel('Input Filter'), 3, 2)
        mainLayout.addWidget(filterSelect, 3, 3)
        mainLayout.addWidget(autoPhaseBtn, 4, 0)
        mainLayout.addWidget(resetBtn, 4, 2)
        self.setLayout(mainLayout)

        ## -- Trigger setting status and communication
        self.phaseFill.textChanged.connect(self.tune_phase)
        harmSelect.currentIndexChanged[str].connect(self.tune_harmonics)
        tcSelect.currentIndexChanged[int].connect(self.tune_time_const)
        self.sensSelect.currentIndexChanged[int].connect(self.tune_sensitivity)
        coupleSelect.currentIndexChanged[str].connect(self.tune_coupling)
        reserveSelect.currentIndexChanged[str].connect(self.tune_reserve)
        groundingSelect.currentIndexChanged[str].connect(self.tune_grounding)
        filterSelect.currentIndexChanged[int].connect(self.tune_filter)
        autoPhaseBtn.clicked.connect(self.auto_phase)
        resetBtn.clicked.connect(self.reset)
        self.clicked.connect(self.check)

    def check(self):
        ''' Enable/disable this groupbox '''

        if self.parent.lcHandle:
            apilc.init_lia(self.parent.lcHandle)
            self.setChecked(True)
        else:
            msg = Shared.MsgError(self, 'No Instrument!', 'No lockin amplifier is connected!')
            msg.exec_()
            self.setChecked(False)

        self.parent.lcStatus.update()

    def tune_phase(self, phase_text):
        '''
            Communicate with the lockin and set phase
        '''

        status, phase = apival.val_lc_phase(phase_text)
        self.phaseFill.setStyleSheet('border: 1px solid {:s}'.format(Shared.msgcolor(status)))
        if status:
            vCode = apilc.set_phase(self.parent.lcHandle, phase)
            if vCode == pyvisa.constants.StatusCode.success:
                self.parent.lcStatus.update()
            else:
                msg = Shared.InstStatus(self, vCode)
                msg.exec_()
        else:
            pass

    def tune_harmonics(self, harm_text):
        '''
            Communicate with the lockin and set Harmonics
        '''

        lc_freq = apilc.read_freq(self.parent.lcHandle)
        status, harm = apival.val_lc_harm(harm_text, lc_freq)

        if status:
            vCode = apilc.set_harm(self.parent.lcHandle, harm)
            if vCode == pyvisa.constants.StatusCode.success:
                self.parent.lcStatus.update()
            else:
                msg = Shared.InstStatus(self, vCode)
                msg.exec_()
        else:
            msg = Shared.MsgError(self, 'Out of Range!', 'Input harmonics exceed legal range!')
            msg.exec_()

    def tune_sensitivity(self, sens_index):
        '''
            Communicate with the lockin and set sensitivity
        '''

        vCode = apilc.set_sens(self.parent.lcHandle, sens_index)

        if vCode == pyvisa.constants.StatusCode.success:
            self.parent.lcStatus.update()
        else:
            msg = Shared.InstStatus(self, vCode)
            msg.exec_()

    def tune_time_const(self, tc_index):
        '''
            Communicate with the lockin and set sensitivity
        '''

        vCode = apilc.set_tc(self.parent.lcHandle, tc_index)

        if vCode == pyvisa.constants.StatusCode.success:
            self.parent.lcStatus.update()
        else:
            msg = Shared.InstStatus(self, vCode)
            msg.exec_()

    def tune_coupling(self, couple_text):
        '''
            Communicate with the lockin and set couple mode
        '''

        vCode = apilc.set_couple(self.parent.lcHandle, couple_text)

        if vCode == pyvisa.constants.StatusCode.success:
            self.parent.lcStatus.update()
        else:
            msg = Shared.InstStatus(self, vCode)
            msg.exec_()

    def tune_reserve(self, reserve_text):
        '''
            Communicate with the lockin and set reserve
        '''

        vCode = apilc.set_reserve(self.parent.lcHandle, reserve_text)

        if vCode == pyvisa.constants.StatusCode.success:
            self.parent.lcStatus.update()
        else:
            msg = Shared.InstStatus(self, vCode)
            msg.exec_()

    def tune_grounding(self, gnd_text):
        '''
            Communicate with the lockin and set input grounding
        '''

        vCode = apilc.set_input_grounding(self.parent.lcHandle, gnd_text)

        if vCode == pyvisa.constants.StatusCode.success:
            self.parent.lcStatus.update()
        else:
            msg = Shared.InstStatus(self, vCode)
            msg.exec_()

    def tune_filter(self, filter_int):
        '''
            Communicate with the lockin and set input notch filter
        '''

        vCode = apilc.set_input_filter(self.parent.lcHandle, filter_int)

        if vCode == pyvisa.constants.StatusCode.success:
            self.parent.lcStatus.update()
        else:
            msg = Shared.InstStatus(self, vCode)
            msg.exec_()


    def auto_phase(self):

        vCode = apilc.auto_phase(self.parent.lcHandle)
        if vCode == pyvisa.constants.StatusCode.success:
            self.parent.lcStatus.update()
            phase = apilc.read_phase(self.parent.lcHandle)
            self.phaseFill.setText('{:.2f}'.format(phase))
        else:
            msg = Shared.InstStatus(self, vCode)
            msg.exec_()


    def reset(self):

        vCode = apilc.reset(self.parent.lcHandle)
        if vCode == pyvisa.constants.StatusCode.success:
            self.parent.lcStatus.update()
        else:
            msg = Shared.InstStatus(self, vCode)
            msg.exec_()


class ScopeCtrl(QtGui.QGroupBox):

    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.parent = parent

        self.setTitle('Oscilloscope Control')
        self.setAlignment(QtCore.Qt.AlignLeft)
        self.setCheckable(True)
        self.setChecked(False)

        ## -- Define layout elements --
        self.srateFill = QtGui.QLineEdit()
        self.slenFill = QtGui.QLineEdit()
        sensSelect = QtGui.QComboBox()
        sensList = ['20 V', '5 V', '1 V', '0.5 V', '0.2 V']
        sensSelect.addItems(sensList)
        self.avgFill = QtGui.QLineEdit()

        ## -- Set up main layout --
        mainLayout = QtGui.QFormLayout()
        mainLayout.setAlignment(QtCore.Qt.AlignTop)
        mainLayout.addRow(QtGui.QLabel('Sample Rate (MHz)'), self.srateFill)
        mainLayout.addRow(QtGui.QLabel('Sample Length'), self.slenFill)
        mainLayout.addRow(QtGui.QLabel('Sensitivity'), sensSelect)
        mainLayout.addRow(QtGui.QLabel('Oscilloscope Average'), self.avgFill)
        self.setLayout(mainLayout)

        ## -- Trigger setting status and communication
        self.srateFill.textChanged.connect(self.rateComm)
        self.slenFill.textChanged.connect(self.lenComm)
        sensSelect.currentIndexChanged.connect(self.tune_sensitivity)
        self.avgFill.textChanged.connect(self.avgComm)
        self.clicked.connect(self.check)

    def check(self):
        ''' Enable/disable this groupbox '''
        if self.parent.pciHandle:
            self.setChecked(True)
        else:
            msg = Shared.MsgError(self, 'No Instrument!', 'No oscilloscope is connected!')
            msg.exec_()
            self.setChecked(False)

    def rateComm(self, rate_text):

        status = apipci.set_sampling_rate(rate_text)
        self.srateFill.setStyleSheet('border: 1px solid {:s}'.format(Shared.msgcolor(status)))

    def lenComm(self, len_text):

        status = apipci.set_sampling_len(len_text)
        self.slenFill.setStyleSheet('border: 1px solid {:s}'.format(Shared.msgcolor(status)))

    def tune_sensitivity(self, sens_index):

        status = apipci.set_sens(sens_index)

    def avgComm(self, avg_text):

        status = apipci.set_osc_avg(avg_text)
        self.avgFill.setStyleSheet('border: 1px solid {:s}'.format(Shared.msgcolor(status)))



class MotorCtrl(QtGui.QGroupBox):

    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.parent = parent

        self.setTitle('Cavity Control')
        self.setAlignment(QtCore.Qt.AlignLeft)
        self.setCheckable(True)
        self.setChecked(False)

        tuneButton = QtGui.QPushButton('Tune Cavity')
        mainLayout = QtGui.QHBoxLayout()
        mainLayout.addWidget(tuneButton)
        self.setLayout(mainLayout)

        ## -- Trigger settings and motor communication
        tuneButton.clicked.connect(self.tune_cavity)
        self.clicked.connect(self.check)

    def check(self):
        ''' Enable/disable this groupbox '''
        if self.parent.motorHandle:
            self.setChecked(True)
        else:
            msg = Shared.MsgError(self, 'No Instrument!', 'No oscilloscope is connected!')
            msg.exec_()
            self.setChecked(False)

    def tune_cavity(self):

        status = apimotor.move(self.parent.motorHandle, 1)


class ScopeMonitor(QtGui.QWidget):

    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.parent = parent

        self.pgPlot = pg.PlotWidget(title='Oscilloscope Monitor')
        mainLayout = QtGui.QGridLayout()
        mainLayout.setAlignment(QtCore.Qt.AlignTop)
        mainLayout.addWidget(self.pgPlot, 0, 0)
        self.setLayout(mainLayout)

    def plot(self):
        pass


class LockinMonitor(QtGui.QWidget):

    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.parent = parent
        self.counter = 0        # data points counter

        self.slenFill = QtGui.QLineEdit()
        self.slenFill.setText('100')
        self.slenFill.setStyleSheet('border: 1px solid {:s}'.format(Shared.msgcolor(2)))
        self.data = np.zeros(100)
        self.updateRate = QtGui.QComboBox()
        self.updateRate.addItems(['10 Hz', '5 Hz', '2 Hz', '1 Hz',
                                   '0.5 Hz', '0.2 Hz', '0.1 Hz'])
        self.updateRate.setCurrentIndex(3)  # default update rate 1s
        self.startButton = QtGui.QPushButton('Start')
        self.startButton.setCheckable(True)
        self.restartButton = QtGui.QPushButton('Restart')
        self.stopButton = QtGui.QPushButton('Stop')
        panelLayout = QtGui.QHBoxLayout()
        panelLayout.addWidget(QtGui.QLabel('Trace Length'))
        panelLayout.addWidget(self.slenFill)
        panelLayout.addWidget(QtGui.QLabel('Update Rate'))
        panelLayout.addWidget(self.updateRate)
        panelLayout.addWidget(self.startButton)
        panelLayout.addWidget(self.restartButton)
        panelLayout.addWidget(self.stopButton)
        settingPanel = QtGui.QWidget()
        settingPanel.setLayout(panelLayout)

        self.pgPlot = pg.PlotWidget(title='Lockin Monitor')
        self.curve = self.pgPlot.plot(self.data)
        mainLayout = QtGui.QVBoxLayout()
        mainLayout.setAlignment(QtCore.Qt.AlignTop)
        mainLayout.addWidget(self.pgPlot)
        mainLayout.addWidget(settingPanel)
        self.setLayout(mainLayout)

        # set up timer
        self.timer = QtCore.QTimer()
        self.timer.setInterval(1000)        # default interval 1 second

        # trigger settings
        self.slenFill.textChanged.connect(self.set_len)
        self.startButton.clicked.connect(self.start)
        self.restartButton.clicked.connect(self.restart)
        self.stopButton.clicked.connect(self.stop)
        self.updateRate.currentIndexChanged[int].connect(self.set_waittime)
        self.timer.timeout.connect(self.update_plot)

    def start(self, btn_pressed):

        if btn_pressed:
            self.startButton.setText('Pause')
            self.timer.start()
        else:
            self.startButton.setText('Continue')
            self.timer.stop()

    def restart(self):

        self.counter = 0    # reset counter
        self.startButton.setChecked(True)   # retrigger start button
        self.startButton.setText('Pause')
        self.timer.start()

    def stop(self):

        self.timer.stop()
        self.counter = 0
        self.startButton.setChecked(False)  # reset start button
        self.startButton.setText('Start')

    def set_len(self, text):
        status, slen = apival.val_monitor_sample_len(text)
        self.slenFill.setStyleSheet('border: 1px solid {:s}'.format(Shared.msgcolor(status)))
        if status:
            self.data = np.zeros(slen)
            self.restart()
        else:
            self.stop()

    def set_waittime(self, srate_index):
        ''' Set wait time according to self.updateRate '''

        status, waittime = apival.val_lc_monitor_srate(srate_index, apilc.read_tc(self.parent.lcHandle))
        self.timer.setInterval(waittime)
        if status:
            pass
        else:
            msg = Shared.MsgWarning('Update speed warning!',
            '''The picked update speed is faster than the lockin time constant.
            Automatically reset the update speed to 2pi * time_constant ''')
            msg.exec_()

    def daq(self):
        ''' If sampled points are less than the set length, fill up the array
            If sampled points are more than the set length, roll the array
            forward and fill the last array element with new data
        '''

        if self.counter < len(self.data):
            self.data[self.counter] = apilc.query_single_x(self.parent.lcHandle)
            self.counter += 1
        else:
            self.data = np.roll(self.data, len(self.data)-1)
            self.data[-1] = apilc.query_single_x(self.parent.lcHandle)

    def update_plot(self):
        self.daq()
        if self.counter < len(self.data):
            self.curve.setData(self.data[0:self.counter])
        else:
            self.curve.setData(self.data)


class SpectrumMonitor(QtGui.QWidget):

    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.parent = parent

        self.pgPlot = pg.PlotWidget(title='Spectrum Monitor')
        mainLayout = QtGui.QGridLayout()
        mainLayout.setAlignment(QtCore.Qt.AlignTop)
        mainLayout.addWidget(self.pgPlot, 0, 0)
        self.setLayout(mainLayout)

    def plot(self):
        pass
