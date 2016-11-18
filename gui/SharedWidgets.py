#! encoding = utf-8

from PyQt4 import QtGui, QtCore
from api import validator as apival


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


class InstStatus(QtGui.QMessageBox):
    ''' Message box of instrument communication status. Silent if communication
        is successful. Pop up error message in pyvisa.constants.StatusCode
    '''

    def __init__(self, parent, code):
        QtGui.QWidget.__init__(self, parent)

        self.setIcon(QtGui.QMessageBox.Warning)
        self.addButton(QtGui.QMessageBox.Ok)
        self.setText(str(code))


class MsgError(QtGui.QMessageBox):
    ''' Message box of instrument communication status. Silent if communication
        is successful. Pop up error message in pyvisa.constants.StatusCode
    '''

    def __init__(self, parent, text, moretext=''):
        QtGui.QWidget.__init__(self, parent)

        self.setIcon(QtGui.QMessageBox.Critical)
        self.addButton(QtGui.QMessageBox.Ok)
        self.setText(text)
        self.setInformativeText(moretext)


class MsgWarning(QtGui.QMessageBox):
    ''' Message box of instrument communication status. Silent if communication
        is successful. Pop up error message in pyvisa.constants.StatusCode
    '''

    def __init__(self, parent, text, moretext=''):
        QtGui.QWidget.__init__(self, parent)

        self.setIcon(QtGui.QMessageBox.Warning)
        self.addButton(QtGui.QMessageBox.Ok)
        self.setText(text)
        self.setInformativeText(moretext)


class VDIBandComboBox(QtGui.QComboBox):
    ''' Selection box for VDI multiplier chain '''

    def __init__(self):
        QtGui.QWidget.__init__(self)

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

        self.addItems(bandList)
        self.setCurrentIndex(4)


class lcSensBox(QtGui.QComboBox):
    ''' Lockin sensitivity selection box '''

    def __init__(self):
        QtGui.QWidget.__init__(self)

        self.addItems(LIASENSLIST)
        self.setCurrentIndex(26)


class lcTcBox(QtGui.QComboBox):
    ''' Lockin time constant selection box '''

    def __init__(self):
        QtGui.QWidget.__init__(self)

        self.addItems(LIATCLIST)
        self.setCurrentIndex(5)


class FreqWinEntryCaption(QtGui.QWidget):
    ''' Frequency window entry for scanning job configuration with captions '''

    def __init__(self, main):
        QtGui.QWidget.__init__(self, parent=None)
        self.main = main

        self.startFreqFill = QtGui.QLineEdit()
        self.stopFreqFill = QtGui.QLineEdit()
        self.stepFill = QtGui.QLineEdit()
        self.avgFill = QtGui.QLineEdit()
        self.sensSel = lcSensBox()

        startFreq = QtGui.QWidget()
        startFreqLayout = QtGui.QFormLayout()
        startFreqLayout.setRowWrapPolicy(2)
        startFreqLayout.addRow(QtGui.QLabel('Start Freq (MHz)'), self.startFreqFill)
        startFreq.setLayout(startFreqLayout)

        stopFreq = QtGui.QWidget()
        stopFreqLayout = QtGui.QFormLayout()
        stopFreqLayout.setRowWrapPolicy(2)
        stopFreqLayout.addRow(QtGui.QLabel('Stop Freq (MHz)'), self.stopFreqFill)
        stopFreq.setLayout(stopFreqLayout)

        step = QtGui.QWidget()
        stepLayout = QtGui.QFormLayout()
        stepLayout.setRowWrapPolicy(2)
        stepLayout.addRow(QtGui.QLabel('Step Size (MHz)'), self.stepFill)
        step.setLayout(stepLayout)

        avg = QtGui.QWidget()
        avgLayout = QtGui.QFormLayout()
        avgLayout.setRowWrapPolicy(2)
        avgLayout.addRow(QtGui.QLabel('Average'), self.avgFill)
        avg.setLayout(avgLayout)

        sens = QtGui.QWidget()
        sensLayout = QtGui.QFormLayout()
        sensLayout.setRowWrapPolicy(2)
        sensLayout.addRow(QtGui.QLabel('Sensitivity'), self.sensSel)
        sens.setLayout(sensLayout)

        mainLayout = QtGui.QHBoxLayout()
        mainLayout.addWidget(startFreq)
        mainLayout.addWidget(stopFreq)
        mainLayout.addWidget(step)
        mainLayout.addWidget(avg)
        mainLayout.addWidget(sens)
        self.setLayout(mainLayout)

        self.startFreqFill.textChanged.connect(self.val_start_freq)
        self.stopFreqFill.textChanged.connect(self.val_stop_freq)
        self.stepFill.textChanged.connect(self.val_step)
        self.avgFill.textChanged.connect(self.val_avg)

    def val_start_freq(self, text):

        vdi_index = self.main.synCtrl.bandSelect.currentIndex()
        status, freq = apival.val_syn_freq(text, vdi_index)
        self.startFreqFill.setStyleSheet('border: 1px solid {:s}'.format(msgcolor(status)))

    def val_stop_freq(self, text):

        vdi_index = self.main.synCtrl.bandSelect.currentIndex()
        status, freq = apival.val_syn_freq(text, vdi_index)
        self.stopFreqFill.setStyleSheet('border: 1px solid {:s}'.format(msgcolor(status)))

    def val_step(self, text):

        vdi_index = self.main.synCtrl.bandSelect.currentIndex()
        status, number = apival.val_float(text)
        self.stepFill.setStyleSheet('border: 1px solid {:s}'.format(msgcolor(status)))

    def val_avg(self, text):

        vdi_index = self.main.synCtrl.bandSelect.currentIndex()
        status, number = apival.val_int(text)
        self.avgFill.setStyleSheet('border: 1px solid {:s}'.format(msgcolor(status)))


class FreqWinEntryNoCaption(QtGui.QWidget):
    ''' Frequency window entry for scanning job configuration without captions '''

    def __init__(self, main):
        QtGui.QWidget.__init__(self, parent=None)
        self.main = main

        self.startFreqFill = QtGui.QLineEdit()
        self.stopFreqFill = QtGui.QLineEdit()
        self.stepFill = QtGui.QLineEdit()
        self.avgFill = QtGui.QLineEdit()
        self.sensSel = lcSensBox()

        mainLayout = QtGui.QHBoxLayout()
        mainLayout.setSpacing(25)
        mainLayout.addWidget(self.startFreqFill)
        mainLayout.addWidget(self.stopFreqFill)
        mainLayout.addWidget(self.stepFill)
        mainLayout.addWidget(self.avgFill)
        mainLayout.addWidget(self.sensSel)
        self.setLayout(mainLayout)

        self.startFreqFill.textChanged.connect(self.val_start_freq)
        self.stopFreqFill.textChanged.connect(self.val_stop_freq)
        self.stepFill.textChanged.connect(self.val_step)
        self.avgFill.textChanged.connect(self.val_avg)

    def val_start_freq(self, text):

        vdi_index = self.main.synCtrl.bandSelect.currentIndex()
        status, freq = apival.val_syn_freq(text, vdi_index)
        self.startFreqFill.setStyleSheet('border: 1px solid {:s}'.format(msgcolor(status)))

    def val_stop_freq(self, text):

        vdi_index = self.main.synCtrl.bandSelect.currentIndex()
        status, freq = apival.val_syn_freq(text, vdi_index)
        self.stopFreqFill.setStyleSheet('border: 1px solid {:s}'.format(msgcolor(status)))

    def val_step(self, text):

        vdi_index = self.main.synCtrl.bandSelect.currentIndex()
        status, number = apival.val_float(text)
        self.stepFill.setStyleSheet('border: 1px solid {:s}'.format(msgcolor(status)))

    def val_avg(self, text):

        vdi_index = self.main.synCtrl.bandSelect.currentIndex()
        status, number = apival.val_int(text)
        self.avgFill.setStyleSheet('border: 1px solid {:s}'.format(msgcolor(status)))


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
