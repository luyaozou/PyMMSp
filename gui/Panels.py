#! encoding = utf-8

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import QObject
import pyqtgraph as pg
from gui.SharedWidgets import *
from api import synthesizer as apisyn
from api import lockin as apilc
from api import pci as apipci
from api import validator as apival

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

    def __init__(self, parent, synHandle):
        QtGui.QWidget.__init__(self, parent)
        self.synHandle = synHandle
        self.parent = parent

        self.setTitle('Synthesizer Status')
        self.setAlignment(1)
        self.setCheckable(False)

        ## -- Define synthesizer status elements --
        self.synUpdate = QtGui.QPushButton('Refresh')
        self.synAddress = QtGui.QLabel()
        self.synFreq = QtGui.QLabel()
        self.synMod = QtGui.QLabel()
        self.synModDepth = QtGui.QLabel()
        self.synModFreq = QtGui.QLabel()
        self.synLF = QtGui.QLabel()
        self.synLFV = QtGui.QLabel()

        ## -- Set layout and add GUI elements
        mainLayout = QtGui.QFormLayout()
        mainLayout.addRow(QtGui.QLabel(''), self.synUpdate)
        mainLayout.addRow(QtGui.QLabel('GPIB Address'), self.synAddress)
        mainLayout.addRow(QtGui.QLabel('Frequency'), self.synFreq)
        mainLayout.addRow(QtGui.QLabel('Modulation'), self.synMod)
        mainLayout.addRow(QtGui.QLabel('Mod Amp'), self.synModDepth)
        mainLayout.addRow(QtGui.QLabel('Mod Freq'), self.synModFreq)
        mainLayout.addRow(QtGui.QLabel('LF Output'), self.synLF)
        mainLayout.addRow(QtGui.QLabel('LF Voltage'), self.synLFV)
        self.setLayout(mainLayout)

        ## -- Trigger status updates

    def update(self):
        pass


class LockinStatus(QtGui.QGroupBox):
    '''
        Lockin status display
    '''

    def __init__(self, parent, lcHandle):
        QtGui.QWidget.__init__(self, parent)
        self.lcHandle = lcHandle
        self.parent = parent

        self.setTitle('Lockin Status')
        self.setAlignment(1)
        self.setCheckable(False)

        ## -- Define synthesizer status elements --
        self.lcUpdate = QtGui.QPushButton('Refresh')
        self.lcAddress = QtGui.QLabel()
        self.lcHarm = QtGui.QLabel()
        self.lcPhase = QtGui.QLabel()
        self.lcFreq = QtGui.QLabel()
        self.lcSens = QtGui.QLabel()
        self.lcTC = QtGui.QLabel()
        self.lcCouple = QtGui.QLabel()
        self.lcReserve = QtGui.QLabel()
        self.lcOutput = QtGui.QLabel()

        ## -- Set layout and add GUI elements
        mainLayout = QtGui.QFormLayout()
        mainLayout.addRow(QtGui.QLabel(''), self.lcUpdate)
        mainLayout.addRow(QtGui.QLabel('GPIB Address'), self.lcAddress)
        mainLayout.addRow(QtGui.QLabel('Harmonics'), self.lcHarm)
        mainLayout.addRow(QtGui.QLabel('Phase'), self.lcPhase)
        mainLayout.addRow(QtGui.QLabel('Locked Freq'), self.lcFreq)
        mainLayout.addRow(QtGui.QLabel('Sensitivity'), self.lcSens)
        mainLayout.addRow(QtGui.QLabel('Time Constant'), self.lcTC)
        mainLayout.addRow(QtGui.QLabel('Couple'), self.lcCouple)
        mainLayout.addRow(QtGui.QLabel('Reserve'), self.lcReserve)
        mainLayout.addRow(QtGui.QLabel('Output'), self.lcOutput)
        self.setLayout(mainLayout)

        ## -- Trigger status updates
        self.update()

    def update(self):

        self.lcHarm.setText(apilc.read_harm(self.lcHandle))
        self.lcPhase.setText(apilc.read_phase(self.lcHandle))
        self.lcFreq.setText(apilc.read_freq(self.lcHandle))
        self.lcSens.setText(apilc.read_sens(self.lcHandle))


class ScopeStatus(QtGui.QGroupBox):
    '''
        Oscilloscope (PCI card) status display
    '''

    def __init__(self, parent, synHandle):
        QtGui.QWidget.__init__(self, parent)
        self.synHandle = synHandle
        self.parent = parent

        self.setTitle('Oscilloscope Status')
        self.setAlignment(1)
        self.setCheckable(False)

        ## -- Define synthesizer status elements --
        self.scopeUpdate = QtGui.QPushButton('Refresh')
        self.scopeAddress = QtGui.QLabel()

        ## -- Set layout and add GUI elements
        mainLayout = QtGui.QFormLayout()
        mainLayout.addRow(QtGui.QLabel(''), self.scopeUpdate)
        mainLayout.addRow(QtGui.QLabel('GPIB Address'), self.scopeAddress)
        self.setLayout(mainLayout)

        ## -- Trigger status updates

    def update(self):
        pass


class SynCtrl(QtGui.QGroupBox):
    '''
        Synthesizer control panel
    '''

    def __init__(self, parent, synHandle):
        QtGui.QWidget.__init__(self, parent)
        self.parent = parent
        self.synHandle = synHandle

        self.setTitle('Synthesizer Control')
        self.setAlignment(1)    # align left
        self.setCheckable(True)
        if self.synHandle:
            self.setChecked(True)
        else:
            self.setChecked(False)

        ## -- Define synthesizer control elements --
        syn = QtGui.QWidget()
        self.synfreq = QtGui.QLabel('30000')
        self.probfreqFill = QtGui.QLineEdit()
        self.probfreqFill.setText('30000')
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

        self.modToggle = QtGui.QCheckBox()
        self.modToggle.setCheckState(False)

        modLayout.addWidget(QtGui.QLabel('Mod On'), 0, 0, 1, 1)
        modLayout.addWidget(self.modToggle, 0, 1, 1, 1)
        modLayout.addWidget(QtGui.QLabel('Mode'), 0, 2, 1, 1)
        modLayout.addWidget(self.modModeSelect, 0, 3, 1, 1)
        modLayout.addWidget(self.modFreq, 1, 0, 1, 4)
        modLayout.addWidget(self.modDepth, 2, 0, 1, 4)
        modGBox.setLayout(modLayout)
        self.modFreq.hide()
        self.modDepth.hide()

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

        # Trigger synthesizer power toggle and communication
        QObject.connect(synPowerManualInput, QtCore.SIGNAL("clicked()"), self.synPowerComm)
        QObject.connect(self.synPowerToggle, QtCore.SIGNAL("stateChanged(int)"), self.synPowerDialog)

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
            status = apisyn.set_syn_freq(self.synHandle, synfreq)

        # update synthesizer frequency
        self.synfreq.setText('{:.12f}'.format(apisyn.read_syn_freq()))


    def synPowerComm(self):
        '''
            Communicate with the synthesizer and set up RF power
            (automatically turn RF on)
        '''

        # Get current syn power
        current_power = apisyn.read_syn_power()
        # Grab manual input power
        set_power, stat = QtGui.QInputDialog.getInt(self, 'Synthesizer RF Power',
                                'Manual Input (-20 to 0)', current_power, -20, 0, 1)
        stat = apisyn.set_syn_power(set_power)
        if not stat:    # hopefully no error occurs
            self.synPowerToggle.setCheckState(True)
        else:
            QtGui.QMessageBox.warning(self, 'Dangerous Input!', 'Input power exceed safety range!', QtGui.QMessageBox.Ok)

    def synPowerDialog(self, toggle_stat):
        '''
            Pop-up warning window when user trigger the synthesizer toggle
        '''

        stat = apisyn.syn_power_toggle(toggle_stat)
        self.synPowerToggle.setCheckState(stat)

    def modModeComm(self):
        '''
            Communicate with the synthesizer and update modulation mode.
        '''

        mod_index = self.modModeSelect.currentIndex()

        if mod_index:
            self.modFreq.show()     # Modulation selected. Show modulation widget
            self.modDepth.show()
        else:
            self.modFreq.hide()     # No modulation. Hide modulation widget
            self.modDepth.hide()

        comm_stat = apisyn.set_mod_mode(mod_index)

        if mod_index == 1:
            if self.modDepthUnit.count() == 1:  # it is set to AM
                pass
            else:
                for i in range(self.modDepthUnit.count()): # remove all items
                    self.modDepthUnit.removeItem(0)
                self.modDepthUnit.addItems(['%'])
        elif mod_index == 2:
            if self.modDepthUnit.count() == 2:  # it is set to AM
                pass
            else:
                for i in range(self.modDepthUnit.count()): # remove all items
                    self.modDepthUnit.removeItem(0)
                self.modDepthUnit.addItems(['kHz', 'MHz'])
        else:
            pass

        # update parameters
        freq, depth = apisyn.read_mod_par()
        self.modFreqFill.setText(freq)
        self.modDepthFill.setText(depth)

    def modParComm(self):
        '''
            Communicate with the synthesizer and update modulation parameters
        '''

        mod_index = self.modModeSelect.currentIndex()
        toggle = self.modToggle.isChecked()

        # convert input and set sheet border color by status
        freq_status, mod_freq = apival.val_syn_mod_freq(self.modFreqFill.text(),
                                       self.modFreqUnit.currentText())
        self.modFreqFill.setStyleSheet('border: 1px solid {:s}'.format(msgcolor(freq_stat)))
        depth_status, mod_depth = apival.val_syn_mod_depth(self.modDepthFill.text(),
                                         self.modDepthUnit.currentText())
        self.modDepthFill.setStyleSheet('border: 1px solid {:s}'.format(msgcolor(depth_stat)))

        if mod_index == 1:      # AM
            status = apisyn.set_am(self.synHandle, mod_freq, mod_depth, toggle)
        elif mod_index == 2:    # FM
            status = apisyn.set_fm(self.synHandle, mod_freq, mod_depth, toggle)
        else:
            pass


    def modToggleComm(self):
        '''
            Communicate with the synthesizer and update modulation on/off toggle
        '''

        apisyn.mod_toggle(self.modToggle.isChecked())


class LockinCtrl(QtGui.QGroupBox):

    def __init__(self, parent, lcHandle):
        QtGui.QWidget.__init__(self, parent)
        self.parent = parent
        self.lcHandle = lcHandle

        self.setTitle('Lockin Control')
        self.setAlignment(1)        # align left
        self.setCheckable(True)
        if self.lcHandle:
            self.setChecked(True)
        else:
            self.setChecked(False)

        ## -- Define layout elements --
        harmSelect = QtGui.QComboBox()
        harmSelect.addItems(['1', '2', '3', '4'])
        self.phaseFill = QtGui.QLineEdit()
        sensSelect = QtGui.QComboBox()
        sensList = ['2 nV', '5 nV', '10 nV', '20 nV', '50 nV', '100 nV',
                    '200 nV', '500 nV', '1 uV', '2 uV', '5 uV', '10 uV',
                    '20 uV', '50 uV', '100 uV', '200 uV', '500 uV', '1 mV',
                    '2 mV', '5 mV', '10 mV', '20 mV', '50 mV', '100 mV',
                    '200 mV', '500 mV', '1 V'
                    ]
        sensSelect.addItems(sensList)
        tcSelect = QtGui.QComboBox()
        tcList = ['10 us', '30 us', '100 us', '300 us', '1 ms', '3 ms', '10 ms',
                  '30 ms', '100 ms', '300 ms', '1 s', '3 s', '10 s', '30 s'
                  ]
        tcSelect.addItems(tcList)
        coupleSelect = QtGui.QComboBox()
        coupleSelect.addItems(['AC', 'DC'])
        reserveSelect = QtGui.QComboBox()
        reserveSelect.addItems(['High Reserve', 'Normal', 'Low Noise'])

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

    def phaseComm(self, phase_text):
        '''
            Communicate with the lockin and set phase
        '''

        status, phase = apival.val_lc_phase(phase_text)
        self.phaseFill.setStyleSheet('border: 1px solid {:s}'.format(msgcolor(status)))
        apilc.set_phase(self.lcHandle, phase)

    def harmComm(self, harm_text):
        '''
            Communicate with the lockin and set Harmonics
        '''

        lc_freq = apilc.read_freq(self.lcHandle)
        status, harm = apival.val_lc_harm(harm_text, lc_freq)

        if status:
            QtGui.QMessageBox.warning(self, 'Out of Range!', 'Input harmonics exceed legal range!', QtGui.QMessageBox.Ok)
        else:
            apilc.set_harm(self.lcHandle, harm)

    def sensComm(self, sens_index):
        '''
            Communicate with the lockin and set sensitivity
        '''

        stat = apilc.set_sensitivity(self.lcHandle, sens_index)

        if stat:
            QtGui.QMessageBox.warning(self, 'Out of Range!', 'Input sensitivity exceed legal range!', QtGui.QMessageBox.Ok)
        else:
            pass

    def tcComm(self, tc_index):
        '''
            Communicate with the lockin and set sensitivity
        '''

        stat = apilc.set_tc(self.lcHandle, tc_index)

        if stat:
            QtGui.QMessageBox.warning(self, 'Out of Range!', 'Input time constant exceed legal range!', QtGui.QMessageBox.Ok)
        else:
            pass

    def coupleComm(self, couple_text):
        '''
            Communicate with the lockin and set couple mode
        '''

        stat = apilc.set_couple(self.lcHandle, couple_text)

        if stat:
            QtGui.QMessageBox.critical(self, 'Invalid Input!', 'Input couple unrecognized!', QtGui.QMessageBox.Ok)
        else:
            pass

    def reserveComm(self, reserve_text):
        '''
            Communicate with the lockin and set reserve
        '''

        stat = apilc.set_reserve(self.lcHandle, reserve_text)

        if stat:
            QtGui.QMessageBox.critical(self, 'Invalid Input!', 'Input reserve mode unrecognized!', QtGui.QMessageBox.Ok)
        else:
            pass


class ScopeCtrl(QtGui.QGroupBox):

    def __init__(self, parent, pciHandle):
        QtGui.QWidget.__init__(self, parent)
        self.parent = parent
        self.pciHandle = pciHandle

        self.setTitle('Oscilloscope Control')
        self.setAlignment(1)
        self.setCheckable(True)
        if self.pciHandle:
            self.setChecked(True)
        else:
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


    def rateComm(self, rate_text):

        stat = apipci.set_sampling_rate(rate_text)
        self.srateFill.setStyleSheet('border: 1px solid {:s}'.format(msgcolor(stat)))

    def lenComm(self, len_text):

        stat = apipci.set_sampling_len(len_text)
        self.slenFill.setStyleSheet('border: 1px solid {:s}'.format(msgcolor(stat)))

    def sensComm(self, sens_index):

        stat = apipci.set_sensitivity(sens_index)

    def avgComm(self, avg_text):

        stat = apipci.set_osc_avg(avg_text)
        self.avgFill.setStyleSheet('border: 1px solid {:s}'.format(msgcolor(stat)))



class MotorCtrl(QtGui.QGroupBox):

    def __init__(self, parent, motorHandle):
        QtGui.QWidget.__init__(self, parent)
        self.parent = parent
        self.motorHandle = motorHandle

        self.setTitle('Cavity Control')
        self.setAlignment(1)
        self.setCheckable(True)
        if self.motorHandle:
            self.setChecked(True)
        else:
            self.setChecked(False)

        tuneButton = QtGui.QPushButton('Tune Cavity')
        mainLayout = QtGui.QHBoxLayout()
        mainLayout.addWidget(tuneButton)
        self.setLayout(mainLayout)

        ## -- Trigger settings and motor communication
        QObject.connect(tuneButton, QtCore.SIGNAL("clicked()"), self.tune_cavity)

    def tune_cavity(self):

        stat = apimotor.move(self.motorHandle, 1)


class ScopeMonitor(pg.PlotWidget):

    def __init__(self, parent):
        pg.PlotWidget.__init__(self, parent, title='Oscilloscope Monitor')

        self.getPlotItem()



class LockinMonitor(pg.PlotWidget):

    def __init__(self, parent):
        pg.PlotWidget.__init__(self, parent, title='Lockin Monitor')

        self.getPlotItem()


class SpectrumMonitor(pg.PlotWidget):

    def __init__(self, parent):
        pg.PlotWidget.__init__(self, parent, title='Spectrum Plotter')

        self.getPlotItem()
