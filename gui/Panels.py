#! encoding = utf-8
''' GUI Panels. '''

# import standard libraries
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import QObject
import pyqtgraph as pg
import pyvisa
import numpy as np
# import shared gui widgets
from gui.SharedWidgets import *
# import instrument api
from api import synthesizer as apisyn
from api import lockin as apilc
from api import pci as apipci
from api import validator as apival
# import data acquisition module
from daq import lockin as daqlc


# LOCKIN AMPLIFIER SENSTIVITY LIST
LIASENSLIST = ['2 nV', '5 nV', '10 nV', '20 nV', '50 nV', '100 nV',
               '200 nV', '500 nV', '1 uV', '2 uV', '5 uV', '10 uV',
               '20 uV', '50 uV', '100 uV', '200 uV', '500 uV', '1 mV',
               '2 mV', '5 mV', '10 mV', '20 mV', '50 mV', '100 mV',
               '200 mV', '500 mV', '1 V'
               ]

# LOCKIN AMPLIFIER TIME CONSTANT LIST
LIATCLIST = ['10 us', '30 us', '100 us', '300 us', '1 ms', '3 ms', '10 ms',
             '30 ms', '100 ms', '300 ms', '1 s', '3 s', '10 s', '30 s'
             ]


def msgcolor(status_code):
    ''' Return message color based on status_code.
        0: safe, green
        1: fatal, red
        2: warning, gold
        else: black
    '''

    if not status_code:
        return '#00A352'
    elif status_code == 1:
        return '#D63333'
    elif status_code == 2:
        return '#FF9933'
    else:
        return '#000000'


class SynStatus(QtGui.QGroupBox):
    '''
        Synthesizer status display
    '''

    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.parent = parent

        self.setTitle('Synthesizer Status')
        self.setAlignment(1)
        self.setCheckable(False)

        ## -- Define synthesizer status elements --
        self.refreshButton = QtGui.QPushButton('Refresh')
        self.fullInfoButton = QtGui.QPushButton('Full Info')
        self.addressText = QtGui.QLabel()
        self.synRF = QtGui.QLabel()
        self.synPower = QtGui.QLabel()
        self.synFreq = QtGui.QLabel()
        self.synMod = QtGui.QLabel()
        self.synModMode = QtGui.QLabel()
        self.synModDepth = QtGui.QLabel()
        self.synModFreq = QtGui.QLabel()
        self.synLF = QtGui.QLabel()
        self.synLFV = QtGui.QLabel()

        ## -- Set layout and add GUI elements
        mainLayout = QtGui.QGridLayout()
        # first column
        mainLayout.addWidget(self.refreshButton, 0, 0, 1, 2)
        mainLayout.addWidget(self.fullInfoButton, 0, 2, 1, 2)
        mainLayout.addWidget(QtGui.QLabel('Inst. Address'), 1, 0)
        mainLayout.addWidget(self.addressText, 1, 1, 1, 3)
        mainLayout.addWidget(QtGui.QLabel('Frequency'), 2, 0)
        mainLayout.addWidget(self.synFreq, 2, 1, 1, 3)
        mainLayout.addWidget(QtGui.QLabel('RF Output'), 3, 0)
        mainLayout.addWidget(self.synRF, 3, 1)
        mainLayout.addWidget(QtGui.QLabel('Power'), 4, 0)
        mainLayout.addWidget(self.synPower, 4, 1)
        mainLayout.addWidget(QtGui.QLabel('LF Output'), 5, 0)
        mainLayout.addWidget(self.synLF, 5, 1)
        mainLayout.addWidget(QtGui.QLabel('LF Voltage'), 6, 0)
        mainLayout.addWidget(self.synLFV, 6, 1)
        self.setLayout(mainLayout)
        # second column
        mainLayout.addWidget(QtGui.QLabel('Modulation'), 3, 2)
        mainLayout.addWidget(self.synMod, 3, 3)
        mainLayout.addWidget(QtGui.QLabel('Mod Mode'), 4, 2)
        mainLayout.addWidget(self.synModMode, 4, 3)
        mainLayout.addWidget(QtGui.QLabel('Mod Freq'), 5, 2)
        mainLayout.addWidget(self.synModFreq, 5, 3)
        mainLayout.addWidget(QtGui.QLabel('Mod Amp'), 6, 2)
        mainLayout.addWidget(self.synModDepth, 6, 3)

        ## -- Trigger status updates
        QObject.connect(self.refreshButton, QtCore.SIGNAL("clicked()"), self.update)
        # initial status
        self.update()

    def update(self):
        ''' Update instrument information '''
        if self.parent.synHandle:
            self.addressText.setText(str(self.parent.synHandle.primary_address))
            self.synRF.setText('On' if apisyn.read_power_toggle(self.parent.synHandle) else 'Off')
            self.synPower.setText('{:.1f} dbm'.format(apisyn.read_syn_power(self.parent.synHandle)))
            self.synFreq.setText('{:.9f} MHz'.format(apisyn.read_syn_freq(self.parent.synHandle)))
            self.synMod.setText('On' if apisyn.read_mod_toggle(self.parent.synHandle) else 'Off')
            lf_vol, lf_status = apisyn.read_lf(self.parent.synHandle)
            self.synLF.setText('On' if lf_status else 'Off')
            self.synLFV.setText('{:.3f} V'.format(lf_vol))
        else:
            self.addressText.setText('N.A.')
            self.synRF.setText('N.A.')
            self.synPower.setText('N.A.')
            self.synFreq.setText('N.A.')
            self.synMod.setText('N.A.')
            self.synLF.setText('N.A.')
            self.synLFV.setText('N.A.')



class LockinStatus(QtGui.QGroupBox):
    '''
        Lockin status display
    '''

    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.parent = parent

        self.setTitle('Lockin Status')
        self.setAlignment(1)
        self.setCheckable(False)

        ## -- Define synthesizer status elements --
        self.refreshButton = QtGui.QPushButton('Refresh')
        self.fullInfoButton = QtGui.QPushButton('Full Info')
        self.addressText = QtGui.QLabel()
        self.lcHarm = QtGui.QLabel()
        self.lcPhase = QtGui.QLabel()
        self.lcFreq = QtGui.QLabel()
        self.lcSens = QtGui.QLabel()
        self.lcTC = QtGui.QLabel()
        self.lcCouple = QtGui.QLabel()
        self.lcReserve = QtGui.QLabel()

        ## -- Set layout and add GUI elements
        mainLayout = QtGui.QGridLayout()
        # first column
        mainLayout.addWidget(self.refreshButton, 0, 0, 1, 2)
        mainLayout.addWidget(self.fullInfoButton, 0, 2, 1, 2)
        mainLayout.addWidget(QtGui.QLabel('Inst. Address'), 1, 0)
        mainLayout.addWidget(self.addressText, 1, 1, 1, 3)
        mainLayout.addWidget(QtGui.QLabel('Harmonics'), 2, 0)
        mainLayout.addWidget(self.lcHarm, 2, 1)
        mainLayout.addWidget(QtGui.QLabel('Phase'), 3, 0)
        mainLayout.addWidget(self.lcPhase, 3, 1)
        mainLayout.addWidget(QtGui.QLabel('Couple'), 4, 0)
        mainLayout.addWidget(self.lcCouple, 4, 1)
        # second column
        mainLayout.addWidget(QtGui.QLabel('Locked Freq'), 2, 2)
        mainLayout.addWidget(self.lcFreq, 2, 3)
        mainLayout.addWidget(QtGui.QLabel('Sensitivity'), 3, 2)
        mainLayout.addWidget(self.lcSens, 3, 3)
        mainLayout.addWidget(QtGui.QLabel('Time Constant'), 4, 2)
        mainLayout.addWidget(self.lcTC, 4, 3)
        mainLayout.addWidget(QtGui.QLabel('Reserve'), 5, 2)
        mainLayout.addWidget(self.lcReserve, 5, 3)
        self.setLayout(mainLayout)

        ## -- Trigger status updates
        QObject.connect(self.refreshButton, QtCore.SIGNAL("clicked()"), self.update)
        # initial status
        self.update()

    def update(self):
        ''' Update instrument information '''
        if self.parent.lcHandle:
            self.addressText.setText(str(self.parent.lcHandle.primary_address))
            self.lcHarm.setText(apilc.read_harm(self.parent.lcHandle))
            self.lcPhase.setText('{:s} deg'.format(apilc.read_phase(self.parent.lcHandle)))
            self.lcFreq.setText('{:.3f} kHz'.format(apilc.read_freq(self.parent.lcHandle)))
            self.lcSens.setText(LIASENSLIST[apilc.read_sens(self.parent.lcHandle)])
            self.lcTC.setText(LIATCLIST[apilc.read_tc(self.parent.lcHandle)])
            self.lcCouple.setText(apilc.read_couple(self.parent.lcHandle))
            self.lcReserve.setText(apilc.read_reserve(self.parent.lcHandle))
        else:
            self.addressText.setText('N.A.')
            self.lcHarm.setText('N.A.')
            self.lcPhase.setText('N.A.')
            self.lcFreq.setText('N.A.')
            self.lcSens.setText('N.A.')
            self.lcTC.setText('N.A.')
            self.lcCouple.setText('N.A.')
            self.lcReserve.setText('N.A.')


class ScopeStatus(QtGui.QGroupBox):
    '''
        Oscilloscope (PCI card) status display
    '''

    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.parent = parent

        self.setTitle('Oscilloscope Status')
        self.setAlignment(1)
        self.setCheckable(False)

        ## -- Define synthesizer status elements --
        self.refreshButton = QtGui.QPushButton('Refresh')
        self.fullInfoButton = QtGui.QPushButton('Full Info')
        self.addressText = QtGui.QLabel()

        ## -- Set layout and add GUI elements
        mainLayout = QtGui.QGridLayout()
        mainLayout.addWidget(self.refreshButton, 0, 0, 1, 2)
        mainLayout.addWidget(self.fullInfoButton, 0, 2, 1, 2)
        mainLayout.addWidget(QtGui.QLabel('Inst. Address'), 1, 0)
        mainLayout.addWidget(self.addressText, 1, 1)
        self.setLayout(mainLayout)

        ## -- Trigger status updates
        QObject.connect(self.refreshButton, QtCore.SIGNAL("clicked()"), self.update)
        # initial status
        self.update()

    def update(self):
        pass


class SynCtrl(QtGui.QGroupBox):
    '''
        Synthesizer control panel
    '''

    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.parent = parent

        self.setTitle('Synthesizer Control')
        self.setAlignment(1)    # align left
        self.setCheckable(True)
        self.check()

        ## -- Define synthesizer control elements --
        syn = QtGui.QWidget()
        self.synfreq = QtGui.QLabel('30000')
        self.probfreqFill = QtGui.QLineEdit()
        self.probfreqFill.setText('180000')
        self.bandSelect = QtGui.QComboBox()
        bandList = ['1 (x1): 0-50 GHz',
                    '2 (x2): GHz',
                    '3 (x3): 70-110 GHz',
                    '4 (x3): 110-140 GHz',
                    '5 (x6): 140-220 GHz',
                    '6 (x9): 220-330 GHz',
                    '7 (x12): 325-430 GHz',
                    '8a (x18): 430-700 GHz',
                    '8b (x27): 600-850 GHz',
                    '9 (x27): 700-1000 GHz']
        self.bandSelect.addItems(bandList)
        self.bandSelect.setCurrentIndex(4)

        ## -- Set up synthesizer control layout --
        synLayout = QtGui.QGridLayout()
        synLayout.addWidget(QtGui.QLabel('Synthesizer Frequency'), 0, 0)
        synLayout.addWidget(self.synfreq, 0, 1)
        synLayout.addWidget(QtGui.QLabel('MHz'), 0, 2)
        synLayout.addWidget(QtGui.QLabel('Probing Frequency'), 1, 0)
        synLayout.addWidget(self.probfreqFill, 1, 1)
        synLayout.addWidget(QtGui.QLabel('MHz'), 1, 2)
        synLayout.addWidget(QtGui.QLabel('VDI Band'), 2, 0)
        synLayout.addWidget(self.bandSelect, 2, 1)
        syn.setLayout(synLayout)

        # Set up modulation child widget
        modGBox = QtGui.QGroupBox()
        modGBox.setTitle('Modulation')
        modGBox.setFlat(True)
        modGBox.setAlignment(1)
        modLayout = QtGui.QGridLayout()
        modLayout.setSpacing(0)

        self.modModeSelect = QtGui.QComboBox()
        self.modModeSelect.addItems(['None', 'AM', 'FM'])

        self.modFreq = QtGui.QWidget()
        self.modFreqFill = QtGui.QLineEdit()
        self.modFreqUnit = QtGui.QComboBox()
        self.modFreqUnit.addItems(['Hz', 'kHz', 'MHz'])
        self.modFreqUnit.setCurrentIndex(1)
        modFreqLayout = QtGui.QHBoxLayout()
        modFreqLayout.addWidget(QtGui.QLabel('Mod Frequency'))
        modFreqLayout.addWidget(self.modFreqFill)
        modFreqLayout.addWidget(self.modFreqUnit)
        self.modFreq.setLayout(modFreqLayout)

        self.modDepth = QtGui.QWidget()
        self.modDepthFill = QtGui.QLineEdit()
        self.modDepthUnit = QtGui.QComboBox()
        self.modDepthUnit.addItems('')
        modDepthLayout = QtGui.QHBoxLayout()
        modDepthLayout.addWidget(QtGui.QLabel('Mod Depth'))
        modDepthLayout.addWidget(self.modDepthFill)
        modDepthLayout.addWidget(self.modDepthUnit)
        self.modDepth.setLayout(modDepthLayout)

        self.lfVol = QtGui.QWidget()
        self.lfVolFill = QtGui.QLineEdit()
        lfLayout = QtGui.QHBoxLayout()
        lfLayout.addWidget(QtGui.QLabel('LF Voltage'))
        lfLayout.addWidget(self.lfVolFill)
        lfLayout.addWidget(QtGui.QLabel('V'))
        self.lfVol.setLayout(lfLayout)

        self.modToggle = QtGui.QCheckBox()
        self.modToggle.setCheckState(False)
        self.modLFToggle = QtGui.QCheckBox()
        self.modLFToggle.setCheckState(False)

        modLayout.addWidget(QtGui.QLabel('LF On'), 0, 0, 1, 1)
        modLayout.addWidget(self.modLFToggle, 0, 1, 1, 1)
        modLayout.addWidget(QtGui.QLabel('Mod On'), 0, 2, 1, 1)
        modLayout.addWidget(self.modToggle, 0, 3, 1, 1)
        modLayout.addWidget(QtGui.QLabel('Mode'), 0, 4, 1, 1)
        modLayout.addWidget(self.modModeSelect, 0, 5, 1, 1)
        modLayout.addWidget(self.modFreq, 1, 0, 1, 6)
        modLayout.addWidget(self.modDepth, 2, 0, 1, 6)
        modLayout.addWidget(self.lfVol, 3, 0, 1, 6)
        modGBox.setLayout(modLayout)
        self.modFreq.hide()
        self.modDepth.hide()
        self.lfVol.hide()

        ## -- Define synthesizer power switch
        self.synPowerToggle = QtGui.QCheckBox()
        self.synPowerToggle.setCheckState(False)
        synPowerManualInput = QtGui.QPushButton('Set Power')

        synPowerLayout = QtGui.QHBoxLayout()
        synPowerLayout.addWidget(QtGui.QLabel('Synthesizer On'))
        synPowerLayout.addWidget(self.synPowerToggle)
        synPowerLayout.addWidget(synPowerManualInput)
        synPowerCtrl = QtGui.QWidget()
        synPowerCtrl.setLayout(synPowerLayout)

        ## -- Set up main layout
        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(synPowerCtrl)
        mainLayout.addWidget(syn)
        mainLayout.addWidget(modGBox)
        self.setLayout(mainLayout)

        # Trigger frequency update and communication
        QObject.connect(self.probfreqFill, QtCore.SIGNAL("textChanged(const QString)"), self.freqComm)
        QObject.connect(self.bandSelect, QtCore.SIGNAL("currentIndexChanged(int)"), self.freqComm)

        # Trigger modulation status update and communication
        QObject.connect(self.modModeSelect, QtCore.SIGNAL("currentIndexChanged(int)"), self.modModeComm)
        QObject.connect(self.modFreqFill, QtCore.SIGNAL("textChanged(const QString)"), self.modParComm)
        QObject.connect(self.modFreqUnit, QtCore.SIGNAL("currentIndexChanged(int)"), self.modParComm)
        QObject.connect(self.modDepthFill, QtCore.SIGNAL("textChanged(const QString)"), self.modParComm)
        QObject.connect(self.modToggle, QtCore.SIGNAL("stateChanged(int)"), self.modToggleComm)
        QObject.connect(self.modLFToggle, QtCore.SIGNAL("stateChanged(int)"), self.modLFToggleComm)
        QObject.connect(self.lfVolFill, QtCore.SIGNAL("textChanged(const QString)"), self.modLFVolComm)

        # Trigger synthesizer power toggle and communication
        QObject.connect(synPowerManualInput, QtCore.SIGNAL("clicked()"), self.synPowerComm)
        QObject.connect(self.synPowerToggle, QtCore.SIGNAL("stateChanged(int)"), self.synPowerDialog)

    def check(self):
        ''' Enable/disable this groupbox '''
        if self.parent.synHandle:
            self.setChecked(True)
        else:
            self.setChecked(False)

    def freqComm(self):
        '''
            Communicate with the synthesizer and update frequency setting.
        '''

        # validate input
        status, synfreq = apival.val_syn_freq(self.probfreqFill.text(),
                                              self.bandSelect.currentIndex())
        # set sheet border color by syn_stat
        self.probfreqFill.setStyleSheet('border: 1px solid {:s}'.format(msgcolor(status)))

        if not status:  # if status is safe
            # call syn api and return communication status
            vCode = apisyn.set_syn_freq(self.parent.synHandle, synfreq)
            if vCode == pyvisa.constants.StatusCode.success:
                self.parent.synStatus.update()
            else:
                msg = InstStatus(self, vCode)
                msg.exec_()
        # update synthesizer frequency
        self.synfreq.setText('{:.12f}'.format(apisyn.read_syn_freq(self.parent.synHandle)))


    def synPowerComm(self):
        '''
            Communicate with the synthesizer and set up RF power
            (automatically turn RF on)
        '''

        # Get current syn power
        current_power = apisyn.read_syn_power(self.parent.synHandle)
        # Grab manual input power
        set_power, status = QtGui.QInputDialog.getInt(self, 'Synthesizer RF Power',
                                'Manual Input (-20 to 0)', current_power, -20, 0, 1)
        if not status:    # hopefully no error occurs
            vCode = apisyn.set_syn_power(set_power)
            if vCode == pyvisa.constants.StatusCode.success:
                self.parent.synStatus.update()
                self.synPowerToggle.setCheckState(True)
            else:
                msg = InstStatus(self, vCode)
                msg.exec_()
        else:
            MsgWarning(self, 'Dangerous Input!', 'Input power exceed safety range!')

    def synPowerDialog(self, toggle_stat):
        '''
            Pop-up warning window when user trigger the synthesizer toggle
        '''

        vCode = apisyn.set_power_toggle(self.parent.synHandle, toggle_stat)
        if vCode == pyvisa.constants.StatusCode.success:
            self.synPowerToggle.setCheckState(toggle_stat)
            self.parent.synStatus.update()
        else:
            msg = InstStatus(self, vCode)
            msg.exec_()


    def modModeComm(self):
        '''
            Communicate with the synthesizer and update modulation mode.
        '''

        mod_index = self.modModeSelect.currentIndex()

        if mod_index:
            self.modFreq.show()     # Modulation selected. Show modulation widget
            self.modDepth.show()
            self.lfVol.show()
        else:
            self.modFreq.hide()     # No modulation. Hide modulation widget
            self.modDepth.hide()
            self.lfVol.hide()

        vCode = apisyn.set_mod_mode(self.parent.synHandle, mod_index)
        if vCode == pyvisa.constants.StatusCode.success:
            self.parent.synStatus.update()
        else:
            msg = InstStatus(self, vCode)
            msg.exec_()

        if mod_index == 1:
            if self.modDepthUnit.count() == 1:  # it is set to AM
                pass
            else:
                for i in range(self.modDepthUnit.count()): # remove all items
                    self.modDepthUnit.removeItem(0)
                self.modDepthUnit.addItems(['%'])
            freq, depth, status = apisyn.read_am_par(self.parent.synHandle)
            # update parameters
            self.modFreqFill.setText('{:.3f}'.format(freq))
            self.modDepthFill.setText('{:.1f}'.format(depth))
        elif mod_index == 2:
            if self.modDepthUnit.count() == 2:  # it is set to AM
                pass
            else:
                for i in range(self.modDepthUnit.count()): # remove all items
                    self.modDepthUnit.removeItem(0)
                self.modDepthUnit.addItems(['kHz', 'MHz'])
            freq, depth, status = apisyn.read_fm_par(self.parent.synHandle)
            # update parameters
            self.modFreqFill.setText('{:.3f}'.format(freq))
            self.modDepthFill.setText('{:.3f}'.format(depth))
        else:
            pass


    def modParComm(self):
        '''
            Communicate with the synthesizer and update modulation parameters
        '''

        mod_index = self.modModeSelect.currentIndex()
        toggle = self.modToggle.isChecked()

        # convert input and set sheet border color by status
        freq_status, mod_freq = apival.val_syn_mod_freq(self.modFreqFill.text(),
                                       self.modFreqUnit.currentText())
        self.modFreqFill.setStyleSheet('border: 1px solid {:s}'.format(msgcolor(freq_status)))
        depth_status, mod_depth = apival.val_syn_mod_depth(self.modDepthFill.text(),
                                         self.modDepthUnit.currentText())
        self.modDepthFill.setStyleSheet('border: 1px solid {:s}'.format(msgcolor(depth_status)))

        if mod_index == 1:      # AM
            vCode = apisyn.set_am(self.parent.synHandle, mod_freq, mod_depth, toggle)
        elif mod_index == 2:    # FM
            vCode = apisyn.set_fm(self.parent.synHandle, mod_freq, mod_depth, toggle)
        else:
            pass

        if vCode == pyvisa.constants.StatusCode.success:
            self.parent.synStatus.update()
        else:
            msg = InstStatus(self, vCode)
            msg.exec_()

    def modToggleComm(self):
        '''
            Communicate with the synthesizer and update modulation on/off toggle
        '''

        vCode = apisyn.set_mod_toggle(self.parent.synHandle, self.modToggle.isChecked())
        if vCode == pyvisa.constants.StatusCode.success:
            self.parent.synStatus.update()
        else:
            msg = InstStatus(self, vCode)
            msg.exec_()


    def modLFToggleComm(self):
        '''
            Communicate with the synthesizer and update LF on/off toggle
        '''

        vCode = apisyn.set_lf_toggle(self.parent.synHandle, self.modLFToggle.isChecked())
        if vCode == pyvisa.constants.StatusCode.success:
            self.parent.synStatus.update()
        else:
            msg = InstStatus(self, vCode)
            msg.exec_()

    def modLFVolComm(self, vol_text):
        '''
            Communicate with the synthesizer and update LF voltage
        '''

        if self.modLFToggle.isChecked():
            status, lf_vol = api.val_syn_lf_vol(vol_text)
            self.lfVolFill.setStyleSheet('border: 1px solid {:s}'.format(msgcolor(status)))
            if status:
                vCode = apisyn.set_lf_amp(self.parent.synHandle, lf_vol)
                if vCode == pyvisa.constants.StatusCode.success:
                    self.parent.synStatus.update()
                else:
                    msg = InstStatus(self, vCode)
                    msg.exec_()
            else:
                pass
        else:
            pass


class LockinCtrl(QtGui.QGroupBox):

    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.parent = parent

        self.setTitle('Lockin Control')
        self.setAlignment(1)        # align left
        self.setCheckable(True)
        self.check()

        ## -- Define layout elements --
        harmSelect = QtGui.QComboBox()
        harmSelect.addItems(['1', '2', '3', '4'])
        harmSelect.setCurrentIndex(1)
        self.phaseFill = QtGui.QLineEdit()
        sensSelect = QtGui.QComboBox()
        sensSelect.addItems(LIASENSLIST)
        sensSelect.setCurrentIndex(26)
        tcSelect = QtGui.QComboBox()
        tcSelect.addItems(LIATCLIST)
        tcSelect.setCurrentIndex(5)
        coupleSelect = QtGui.QComboBox()
        coupleSelect.addItems(['AC', 'DC'])
        coupleSelect.setCurrentIndex(1)
        reserveSelect = QtGui.QComboBox()
        reserveSelect.addItems(['High Reserve', 'Normal', 'Low Noise'])
        reserveSelect.setCurrentIndex(1)

        ## -- Set up main layout --
        mainLayout = QtGui.QGridLayout()
        mainLayout.addWidget(QtGui.QLabel('Harmonics'), 0, 0)
        mainLayout.addWidget(harmSelect, 0, 1)
        mainLayout.addWidget(QtGui.QLabel('Phase'), 1, 0)
        mainLayout.addWidget(self.phaseFill, 1, 1)
        mainLayout.addWidget(QtGui.QLabel('Sensitivity'), 2, 0)
        mainLayout.addWidget(sensSelect, 2, 1)
        mainLayout.addWidget(QtGui.QLabel('Time Constant'), 0, 2)
        mainLayout.addWidget(tcSelect, 0, 3)
        mainLayout.addWidget(QtGui.QLabel('Couple'), 1, 2)
        mainLayout.addWidget(coupleSelect, 1, 3)
        mainLayout.addWidget(QtGui.QLabel('Reserve'), 2, 2)
        mainLayout.addWidget(reserveSelect, 2, 3)
        self.setLayout(mainLayout)

        ## -- Trigger setting status and communication
        QObject.connect(self.phaseFill, QtCore.SIGNAL("textChanged(const QString)"), self.phaseComm)
        QObject.connect(harmSelect, QtCore.SIGNAL("currentIndexChanged(const QString)"), self.harmComm)
        QObject.connect(tcSelect, QtCore.SIGNAL("currentIndexChanged(int)"), self.tcComm)
        QObject.connect(sensSelect, QtCore.SIGNAL("currentIndexChanged(int)"), self.sensComm)
        QObject.connect(coupleSelect, QtCore.SIGNAL("currentIndexChanged(const QString)"), self.coupleComm)
        QObject.connect(reserveSelect, QtCore.SIGNAL("currentIndexChanged(const QString)"), self.reserveComm)

    def check(self):
        ''' Enable/disable this groupbox '''
        if self.parent.lcHandle:
            self.setChecked(True)
        else:
            self.setChecked(False)

    def phaseComm(self, phase_text):
        '''
            Communicate with the lockin and set phase
        '''

        status, phase = apival.val_lc_phase(phase_text)
        self.phaseFill.setStyleSheet('border: 1px solid {:s}'.format(msgcolor(status)))
        if status!= 1:
            vCode = apilc.set_phase(self.parent.lcHandle, phase)
            if vCode == pyvisa.constants.StatusCode.success:
                self.parent.lcStatus.update()
            else:
                msg = InstStatus(self, vCode)
                msg.exec_()
        else:
            pass

    def harmComm(self, harm_text):
        '''
            Communicate with the lockin and set Harmonics
        '''

        lc_freq = apilc.read_freq(self.parent.lcHandle)
        status, harm = apival.val_lc_harm(harm_text, lc_freq)

        if not status:
            vCode = apilc.set_harm(self.parent.lcHandle, harm)
            if vCode == pyvisa.constants.StatusCode.success:
                self.parent.lcStatus.update()
            else:
                msg = InstStatus(self, vCode)
                msg.exec_()
        else:
            msg = MsgError(self, 'Out of Range!', 'Input harmonics exceed legal range!')
            msg.exec_()

    def sensComm(self, sens_index):
        '''
            Communicate with the lockin and set sensitivity
        '''

        vCode = apilc.set_sens(self.parent.lcHandle, sens_index)

        if vCode == pyvisa.constants.StatusCode.success:
            self.parent.lcStatus.update()
        else:
            msg = InstStatus(self, vCode)
            msg.exec_()

    def tcComm(self, tc_index):
        '''
            Communicate with the lockin and set sensitivity
        '''

        vCode = apilc.set_tc(self.parent.lcHandle, tc_index)

        if vCode == pyvisa.constants.StatusCode.success:
            self.parent.lcStatus.update()
        else:
            msg = InstStatus(self, vCode)
            msg.exec_()

    def coupleComm(self, couple_text):
        '''
            Communicate with the lockin and set couple mode
        '''

        vCode = apilc.set_couple(self.parent.lcHandle, couple_text)

        if vCode == pyvisa.constants.StatusCode.success:
            self.parent.lcStatus.update()
        else:
            msg = InstStatus(self, vCode)
            msg.exec_()

    def reserveComm(self, reserve_text):
        '''
            Communicate with the lockin and set reserve
        '''

        vCode = apilc.set_reserve(self.parent.lcHandle, reserve_text)

        if vCode == pyvisa.constants.StatusCode.success:
            self.parent.lcStatus.update()
        else:
            msg = InstStatus(self, vCode)
            msg.exec_()


class ScopeCtrl(QtGui.QGroupBox):

    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.parent = parent

        self.setTitle('Oscilloscope Control')
        self.setAlignment(1)
        self.setCheckable(True)
        self.check()

        ## -- Define layout elements --
        self.srateFill = QtGui.QLineEdit()
        self.slenFill = QtGui.QLineEdit()
        sensSelect = QtGui.QComboBox()
        sensList = ['20 V', '5 V', '1 V', '0.5 V', '0.2 V']
        sensSelect.addItems(sensList)
        self.avgFill = QtGui.QLineEdit()

        ## -- Set up main layout --
        mainLayout = QtGui.QFormLayout()
        mainLayout.addRow(QtGui.QLabel('Sample Rate (MHz)'), self.srateFill)
        mainLayout.addRow(QtGui.QLabel('Sample Length'), self.slenFill)
        mainLayout.addRow(QtGui.QLabel('Sensitivity'), sensSelect)
        mainLayout.addRow(QtGui.QLabel('Oscilloscope Average'), self.avgFill)
        self.setLayout(mainLayout)

        ## -- Trigger setting status and communication
        QObject.connect(self.srateFill, QtCore.SIGNAL("textChanged(const QString)"), self.rateComm)
        QObject.connect(self.slenFill, QtCore.SIGNAL("textChanged(const QString)"), self.lenComm)
        QObject.connect(sensSelect, QtCore.SIGNAL("currentIndexChanged(int)"), self.sensComm)
        QObject.connect(self.avgFill, QtCore.SIGNAL("textChanged(const QString)"), self.avgComm)

    def check(self):
        ''' Enable/disable this groupbox '''
        if self.parent.lcHandle:
            self.setChecked(True)
        else:
            self.setChecked(False)

    def rateComm(self, rate_text):

        status = apipci.set_sampling_rate(rate_text)
        self.srateFill.setStyleSheet('border: 1px solid {:s}'.format(msgcolor(status)))

    def lenComm(self, len_text):

        status = apipci.set_sampling_len(len_text)
        self.slenFill.setStyleSheet('border: 1px solid {:s}'.format(msgcolor(status)))

    def sensComm(self, sens_index):

        status = apipci.set_sens(sens_index)

    def avgComm(self, avg_text):

        status = apipci.set_osc_avg(avg_text)
        self.avgFill.setStyleSheet('border: 1px solid {:s}'.format(msgcolor(status)))



class MotorCtrl(QtGui.QGroupBox):

    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.parent = parent

        self.setTitle('Cavity Control')
        self.setAlignment(1)
        self.setCheckable(True)
        self.check()

        tuneButton = QtGui.QPushButton('Tune Cavity')
        mainLayout = QtGui.QHBoxLayout()
        mainLayout.addWidget(tuneButton)
        self.setLayout(mainLayout)

        ## -- Trigger settings and motor communication
        QObject.connect(tuneButton, QtCore.SIGNAL("clicked()"), self.tune_cavity)

    def check(self):
        ''' Enable/disable this groupbox '''
        if self.parent.lcHandle:
            self.setChecked(True)
        else:
            self.setChecked(False)

    def tune_cavity(self):

        status = apimotor.move(self.parent.motorHandle, 1)


class ScopeMonitor(QtGui.QWidget):

    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.parent = parent

        self.pgPlot = pg.PlotWidget(title='Oscilloscope Monitor')
        mainLayout = QtGui.QGridLayout()
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
        self.slenFill.setStyleSheet('border: 1px solid {:s}'.format(msgcolor(0)))
        self.data = np.empty(100)
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
        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(self.pgPlot)
        mainLayout.addWidget(settingPanel)
        self.setLayout(mainLayout)

        # set up timer
        self.timer = QtCore.QTimer()
        self.timer.setInterval(1000)        # default interval 1 second

        # trigger settings
        QObject.connect(self.slenFill, QtCore.SIGNAL("textChanged(const QString)"), self.set_len)
        QObject.connect(self.startButton, QtCore.SIGNAL("clicked(bool)"), self.start)
        QObject.connect(self.restartButton, QtCore.SIGNAL("clicked()"), self.restart)
        QObject.connect(self.stopButton, QtCore.SIGNAL("clicked()"), self.stop)
        QObject.connect(self.updateRate, QtCore.SIGNAL("currentIndexChanged(int)"), self.set_waittime)
        QObject.connect(self.timer, QtCore.SIGNAL("timeout()"), self.update_plot)

    def start(self, btn_pressed):

        if btn_pressed:
            self.startButton.setText('Pause')
        else:
            self.startButton.setText('Continue')

        self.timer.start()

    def restart(self):

        self.counter = 0    # reset counter
        self.startButton.setChecked(True)   # retrigger start button
        self.startButton.setText('Pause')
        self.pgPlot.clear()
        self.timer.start()

    def stop(self):

        self.timer.stop()
        self.pgPlot.clear()
        self.counter = 0
        self.startButton.setChecked(False)  # reset start button
        self.startButton.setText('Start')

    def set_len(self, text):
        status, slen = apival.val_monitor_sample_len(text)
        self.slenFill.setStyleSheet('border: 1px solid {:s}'.format(msgcolor(status)))
        if status == 1:
            self.stop()
        elif slen > 0:
            self.data = np.empty(slen)
            self.restart()
        else:
            self.stop()

    def set_waittime(self, srate_index):
        ''' Set wait time according to self.updateRate '''

        waittime_list = [100, 200, 500, 1000, 2000, 5000, 10000]    # milliseconds
        self.timer.setInterval(waittime_list[srate_index])

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
            self.curve = self.pgPlot.plot(self.data[0:self.counter])
        else:
            self.curve.setData(self.data)


class SpectrumMonitor(QtGui.QWidget):

    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.parent = parent

        self.pgPlot = pg.PlotWidget(title='Spectrum Monitor')
        mainLayout = QtGui.QGridLayout()
        mainLayout.addWidget(self.pgPlot, 0, 0)
        self.setLayout(mainLayout)

    def plot(self):
        pass
