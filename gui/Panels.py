#! encoding = utf-8

from PyQt4 import QtGui, QtCore
from gui.SharedWidgets import *

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

        layout = QtGui.QGridLayout()

        # Add labels
        layout.addWidget(QtGui.QLabel('Synthesizer Control'), 0, 0, 1, 2)
        layout.addWidget(QtGui.QLabel('Synthesizer Frequency (MHz)'), 1, 0)
        layout.addWidget(QtGui.QLabel('Probing Frequency (MHz)'), 2, 0)
        layout.addWidget(QtGui.QLabel('VDI Band'), 3, 0)
        layout.addWidget(QtGui.QLabel('Modulation'), 4, 0)

        # Define and add control boxes
        synfreqFill = QtGui.QLineEdit()
        probfreqFill = QtGui.QLineEdit()
        bandChoise = QtGui.QComboBox()
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
        bandChoise.addItems(bandList)

        layout.addWidget(synfreqFill, 1, 1)
        layout.addWidget(probfreqFill, 2, 1)
        layout.addWidget(bandChoise, 3, 1)

        self.setLayout(layout)

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

        sender.setStyleSheet('border: 3px solid %s' % color)


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

        sender.setStyleSheet('border: 3px solid %s' % color)


class LockinCtrl(QtGui.QWidget):

    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)

        layout = QtGui.QGridLayout()

        self.setLayout(layout)


class ScopeCtrl(QtGui.QWidget):

    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)

        layout = QtGui.QGridLayout()

        self.setLayout(layout)


class CavityCtrl(QtGui.QWidget):

    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)

        layout = QtGui.QGridLayout()

        self.setLayout(layout)


class ScopeMonitor(QtGui.QWidget):

    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)

        layout = QtGui.QGridLayout()

        self.setLayout(layout)


class PowerMonitor(QtGui.QWidget):

    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)

        layout = QtGui.QGridLayout()

        self.setLayout(layout)


class SpectrumMonitor(QtGui.QWidget):

    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)

        layout = QtGui.QGridLayout()

        self.setLayout(layout)
