#! encoding = utf-8

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import QObject
import pyqtgraph as pg
from gui.SharedWidgets import *
from api import synthesizer as synapi

# Define GLOBAL Constants
SAFE_GREEN = '#00A352'
WARNING_GOLD = '#FF9933'
FATAL_RED = '#D63333'
MULTIPLIER = [1, 3, 3, 6, 9, 12, 18, 27, 27]    # VDI multiplication factor


class SynCtrl(QtGui.QWidget):
    '''
        Synthesizer control panel
    '''

    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)

        self.setWindowTitle('Synthesizer Control')

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
        self.modSelect = QtGui.QComboBox()
        self.modSelect.addItems(['None', 'AM', 'FM'])

        ## -- Set up synthesizer control layout --
        synLayout = QtGui.QFormLayout()
        synLayout.addRow(QtGui.QLabel('Synthesizer Frequency (MHz)'), self.synfreq)
        synLayout.addRow(QtGui.QLabel('Probing Frequency (MHz)'), self.probfreqFill)
        synLayout.addRow(QtGui.QLabel('VDI Band'), self.bandSelect)
        synLayout.addRow(QtGui.QLabel('Modulation'), self.modSelect)
        syn.setLayout(synLayout)

        # Set up modulation sublayout
        self.mod = QtGui.QWidget()
        modLayout = QtGui.QGridLayout()
        self.modfreqFill = QtGui.QLineEdit()
        self.modfreqUnit = QtGui.QComboBox()
        self.moddepthFill = QtGui.QLineEdit()
        self.moddepthUnit = QtGui.QComboBox()
        self.modSwitch = QtGui.QCheckBox()
        self.modSwitch.setCheckState(False)

        modLayout.addWidget(QtGui.QLabel('Mod Frequency'), 0, 0)
        modLayout.addWidget(self.modfreqFill, 0, 1)
        modLayout.addWidget(QtGui.QLabel('kHz'), 0, 2)
        modLayout.addWidget(QtGui.QLabel('Mod Depth'), 1, 0)
        modLayout.addWidget(self.moddepthFill, 1, 1)
        modLayout.addWidget(self.moddepthUnit, 1, 2)
        modLayout.addWidget(QtGui.QLabel('Mod On'), 2, 0, 1, 2)
        modLayout.addWidget(self.modSwitch)
        self.mod.setLayout(modLayout)
        self.mod.hide()

        ## -- Define synthesizer power switch
        synPowerSwitch = QtGui.QCheckBox()
        synPowerManualInput = QtGui.QPushButton('Manual Power')
        synPowerLayout = QtGui.QHBoxLayout()
        synpower = synapi.read_syn_power()
        synPowerLayout.addWidget(QtGui.QLabel('Synthesizer On'))
        synPowerLayout.addWidget(synPowerSwitch)
        synPowerLayout.addWidget(QtGui.QLabel('Current Power'))
        synPowerLayout.addWidget(QtGui.QLabel(synpower))
        synPowerLayout.addWidget(synPowerManualInput)
        synPowerCtrl = QtGui.QWidget()
        synPowerCtrl.setLayout(synPowerLayout)

        ## -- Set up main layout
        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(synPowerCtrl)
        mainLayout.addWidget(syn)
        mainLayout.addWidget(self.mod)
        self.setLayout(mainLayout)

        # Trigger frequency update and communication
        QObject.connect(self.probfreqFill, QtCore.SIGNAL("textChanged(const QString)"), self.freqComm)
        QObject.connect(self.bandSelect, QtCore.SIGNAL("currentIndexChanged(int)"), self.freqComm)

        # Trigger modulation status update and communication
        QObject.connect(self.modSelect, QtCore.SIGNAL("currentIndexChanged(int)"), self.modComm)
        QObject.connect(self.modfreqFill, QtCore.SIGNAL("textChanged(const QString)"), self.modComm)
        QObject.connect(self.moddepthFill, QtCore.SIGNAL("textChanged(const QString)"), self.modComm)
        QObject.connect(self.moddepthUnit, QtCore.SIGNAL("currentIndexChanged(int)"), self.modComm)
        QObject.connect(self.modSwitch, QtCore.SIGNAL("stateChanged(int)"), self.modSimpleSwitch)

    def freqComm(self):
        '''
            Update synthesizer frequency from new input prob frequency,
            validate it, and communicate with the synthesizer if input is valid.
        '''

        text = self.probfreqFill.text()
        band_index = self.bandSelect.currentIndex()
        try:
            probfreq = float(text)
            synfreq = probfreq / MULTIPLIER[band_index]
            if synfreq > 0 and synfreq < 50000:
                color = SAFE_GREEN
                self.synfreq.setText('{:.12f}'.format(synfreq))
                synapi.set_syn_freq(synfreq)
            else:
                color = FATAL_RED
        except ValueError:
            color = FATAL_RED

        self.probfreqFill.setStyleSheet('border: 2px solid %s' % color)

    def modComm(self):
        '''
            Update synthesizer modulation mode, and change the GUI accordingly
        '''

        mod_index = self.modSelect.currentIndex()

        if not mod_index:           # None, no need to grab widget status
            self.mod.hide()         # hide modulation widget
            synapi.set_nomod()

        elif mod_index == 1:        # Amplitude modulation
            self.mod.show()
            switch = self.modSwitch.isChecked()
            valid = True
            #self.moddepthUnit.clear()
            #self.moddepthUnit.addItems(['%'])
            try:
                modfreq = float(self.modfreqFill.text())
                if modfreq > 100 or modfreq > 0:    # invalid
                    self.modfreqFill.setStyleSheet('border: 2px solid %s' % WARNING_GOLD)
                    valid = False
            except ValueError:
                self.modfreqFill.setStyleSheet('border: 2px solid %s' % FATAL_RED)
                valid = False

            try:
                depth = float(self.moddepthFill.text())
                if depth > 75 or depth < 0:
                    self.modfreqFill.setStyleSheet('border: 2px solid %s' % WARNING_GOLD)
                    valid = False
            except ValueError:
                self.modfreqFill.setStyleSheet('border: 2px solid %s' % FATAL_RED)
                valid = False

            if valid:       # communicate with synthesizer with valid settings
                synapi.set_am(modfreq, depth)
                synapi.mod_on(switch)
            else:
                pass

        else:                       # Frequency modulation
            self.mod.show()
            switch = self.modSwitch.isChecked()
            valid = True
            #self.moddepthUnit.clear()
            #self.moddepthUnit.addItems(['kHz', 'MHz'])
            unit = [1000, 1e6]

            try:
                modfreq = float(self.modfreqFill.text())
                if modfreq > 100 or modfreq > 0:    # invalid
                    self.modfreqFill.setStyleSheet('border: 2px solid %s' % WARNING_GOLD)
                    valid = False
            except ValueError:
                self.modfreqFill.setStyleSheet('border: 2px solid %s' % FATAL_RED)
                valid = False

            try:
                depth = float(self.moddepthFill.text())
                if depth > 75 or depth < 0:
                    self.modfreqFill.setStyleSheet('border: 2px solid %s' % WARNING_GOLD)
                    valid = False
            except ValueError:
                self.modfreqFill.setStyleSheet('border: 2px solid %s' % FATAL_RED)
                valid = False

            if valid:       # communicate with synthesizer with valid settings
                synapi.set_fm(modfreq, depth * unit[self.moddepthUnit.currentIndex()])
                synapi.mod_on(switch)
            else:
                pass

    def modSimpleSwitch(self):
        ''' Simply turn on/off modulation '''

        synapi.mod_on(self.modSwitch.isChecked())


class LockinCtrl(QtGui.QWidget):

    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)

        self.setWindowTitle('Lockin Control')

        ## -- Define layout elements --
        harmSelect = QtGui.QComboBox()
        harmSelect.addItems(['1', '2', '3', '4'])
        phaseFill = QtGui.QLineEdit()
        sensSelect = QtGui.QComboBox()
        sensList = ['1 V', '500 mV', '200 mV', '100 mV', '50 mV', '20 mV',
                    '10 mV', '1 mV', '500 uV', '200 uV', '100 uV', '50 uV',
                    '20 uV', '10 uV', '5 uV', '2 uV', '1 uV'
                    ]
        sensSelect.addItems(sensList)
        tcSelect = QtGui.QComboBox()
        tcList = ['30 us', '100 us', '300 us', '1 ms', '3 ms', '10 ms',
                  '30 ms', '100 ms', '300 ms', '1 s', '3 s', '10 s'
                  ]
        tcSelect.addItems(tcList)
        coupleSelect = QtGui.QComboBox()
        coupleSelect.addItems(['AC', 'DC'])
        reserveSelect = QtGui.QComboBox()
        reserveSelect.addItems(['High Reserve', 'Normal', 'Low Noise'])

        ## -- Set up main layout --
        mainLayout = QtGui.QFormLayout()
        mainLayout.addRow(QtGui.QLabel('Harmonics'), harmSelect)
        mainLayout.addRow(QtGui.QLabel('Phase'), phaseFill)
        mainLayout.addRow(QtGui.QLabel('Sensitivity'), sensSelect)
        mainLayout.addRow(QtGui.QLabel('Time Constant'), tcSelect)
        mainLayout.addRow(QtGui.QLabel('Couple'), coupleSelect)
        mainLayout.addRow(QtGui.QLabel('Reserve'), reserveSelect)
        self.setLayout(mainLayout)

        # Validate input status
        phaseFill.textChanged.connect(self.phaseVal)

    def phaseVal(self):
        '''
            Validate phase input. Must between 0-360.
        '''

        sender = self.sender()
        text = sender.text()
        validator = QtGui.QDoubleValidator()
        status = ((validator.validate(text, 0)[0] == QtGui.QValidator.Acceptable)
                   and (float(text) < 360)
                   and (float(text) >= 0))

        if status:
            color = SAFE_GREEN
        else:
            color = FATAL_RED

        sender.setStyleSheet('border: 2px solid %s' % color)


class ScopeCtrl(QtGui.QWidget):

    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)

        self.setWindowTitle('Scope Control')

        ## -- Define layout elements --
        srateFill = QtGui.QLineEdit()
        slenFill = QtGui.QLineEdit()
        sensSelect = QtGui.QComboBox()
        sensList = ['20 V', '5 V', '1 V', '0.5 V', '0.2 V']
        sensSelect.addItems(sensList)
        avgFill = QtGui.QLineEdit()

        ## -- Set up main layout --
        mainLayout = QtGui.QFormLayout()
        mainLayout.addRow(QtGui.QLabel('Sample Rate'), srateFill)
        mainLayout.addRow(QtGui.QLabel('Sample Length'), slenFill)
        mainLayout.addRow(QtGui.QLabel('Sensitivity'), sensSelect)
        mainLayout.addRow(QtGui.QLabel('Oscilloscope Average'), avgFill)
        self.setLayout(mainLayout)


class CavityCtrl(QtGui.QWidget):

    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)

        self.setWindowTitle('Cavity Control')

        mainLayout = QtGui.QHBoxLayout()
        mainLayout.addWidget(QtGui.QPushButton('Tune Cavity'))
        self.setLayout(mainLayout)


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
