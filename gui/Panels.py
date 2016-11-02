#! encoding = utf-8

from PyQt4 import QtGui, QtCore
import pyqtgraph as pg
from gui.SharedWidgets import *
from api import synthesizer as synapi

# Define status colors
SAFE_GREEN = '#00A352'
WARNING_GOLD = '#FF9933'
FATAL_RED = '#D63333'


class SynCtrl(QtGui.QWidget):
    '''
        Synthesizer control panel
    '''

    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)

        self.setWindowTitle('Synthesizer Control')

        ## -- Define synthesizer control elements --
        syn = QtGui.QWidget()
        synfreqFill = QtGui.QLineEdit()
        probfreqFill = QtGui.QLineEdit()
        bandSelect = QtGui.QComboBox()
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
        bandSelect.addItems(bandList)
        modSelect = QtGui.QComboBox()
        modSelect.addItems(['None', 'AM', 'FM'])

        ## -- Set up synthesizer control layout --
        synLayout = QtGui.QFormLayout()
        synLayout.addRow(QtGui.QLabel('Synthesizer Frequency (MHz)'), synfreqFill)
        synLayout.addRow(QtGui.QLabel('Probing Frequency (MHz)'), probfreqFill)
        synLayout.addRow(QtGui.QLabel('VDI Band'), bandSelect)
        synLayout.addRow(QtGui.QLabel('Modulation'), modSelect)
        syn.setLayout(synLayout)

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
        self.setLayout(mainLayout)

        # Validate input status
        synfreqFill.textChanged.connect(self.synfreqVal)
        probfreqFill.textChanged.connect(self.probfreqVal)

    def synfreqVal(self, *args):
        '''
            Validate synthesizer frequency. Must between 0-50000
        '''

        sender = self.sender()
        text = sender.text()
        validator = QtGui.QDoubleValidator()
        status = ((validator.validate(text, 0)[0] == QtGui.QValidator.Acceptable)
                   and (float(text) < 50000)
                   and (float(text) > 0))

        if status:
            color = SAFE_GREEN
        else:
            color = FATAL_RED

        sender.setStyleSheet('border: 2px solid %s' % color)


    def probfreqVal(self, *args):
        '''
            Validate probing frequency. Must be float number and stay in
            the synthesizer frequency range
        '''

        sender = self.sender()
        text = sender.text()
        validator = QtGui.QDoubleValidator()
        status = ((validator.validate(text, 0)[0] == QtGui.QValidator.Acceptable)
                   and (float(text) < 50000)
                   and (float(text) > 0))

        if status:
            color = SAFE_GREEN
        else:
            color = FATAL_RED

        sender.setStyleSheet('border: 2px solid %s' % color)


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

    def phaseVal(self, *args):
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
