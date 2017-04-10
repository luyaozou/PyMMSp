#! encoding = utf-8

from PyQt5 import QtGui, QtCore
import random
from math import ceil
import numpy as np
from api import validator as api_val


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

# QPushButton label dictionary
BUTTONLABEL = {'confirm':['Lets do it', 'Go forth and conquer', 'Ready to go',
                          'Looks good', 'Sounds about right'],
               'complete':['Nice job', 'Sweet', 'Well done', 'Mission complete'],
               'accept':['I see', 'Gotcha', 'Okay', 'Yes master'],
               'reject':['Never mind', 'I changed my mind', 'Cancel', 'I refuse'],
               'error':['Oopsy!', 'Something got messed up', 'Bad']
                }

def btn_label(btn_type):
    ''' Randomly generate a QPushButton label.
        Arguments
            btn_type: str
        Returns
            label: str
    '''

    try:
        a_list = BUTTONLABEL[btn_type]
        return a_list[random.randint(0, len(a_list)-1)]
    except KeyError:
        return 'A Button'


class InstStatus(QtGui.QMessageBox):
    ''' Message box of instrument communication status. Silent if communication
        is successful. Pop up error message in pyvisa.constants.StatusCode
    '''

    def __init__(self, parent, code):
        QtGui.QWidget.__init__(self, parent)

        self.setIcon(QtGui.QMessageBox.Critical)
        self.addButton(QtGui.QMessageBox.Ok)
        self.setText(str(code))
        self.setWindowTitle('Instrument Communication Failure!')


class MsgError(QtGui.QMessageBox):
    ''' Error message box '''

    def __init__(self, parent, title_text, moretext=''):
        QtGui.QWidget.__init__(self, parent)

        self.setIcon(QtGui.QMessageBox.Critical)
        self.addButton(QtGui.QMessageBox.Ok)
        self.setWindowTitle(title_text)
        self.setText(moretext)


class MsgWarning(QtGui.QMessageBox):
    ''' Warning message box '''

    def __init__(self, parent, title_text, moretext=''):
        QtGui.QWidget.__init__(self, parent)

        self.setIcon(QtGui.QMessageBox.Warning)
        self.addButton(QtGui.QMessageBox.Ok)
        self.setWindowTitle(title_text)
        self.setText(moretext)


class MsgInfo(QtGui.QMessageBox):
    ''' Information message box '''

    def __init__(self, parent, title_text, moretext=''):
        QtGui.QWidget.__init__(self, parent)

        self.setIcon(QtGui.QMessageBox.Information)
        self.addButton(QtGui.QMessageBox.Ok)
        self.setWindowTitle(title_text)
        self.setText(moretext)
        self.setWindowModality(0)


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


class liaSensBox(QtGui.QComboBox):
    ''' Lockin sensitivity selection box '''

    def __init__(self):
        QtGui.QWidget.__init__(self)

        self.addItems(LIASENSLIST)
        self.setCurrentIndex(26)


class liaTCBox(QtGui.QComboBox):
    ''' Lockin time constant selection box '''

    def __init__(self):
        QtGui.QWidget.__init__(self)

        self.addItems(LIATCLIST)
        self.setCurrentIndex(5)


class ScanEntry(QtGui.QWidget):
    ''' Frequency window entry for scanning job configuration with captions '''

    def __init__(self, main, init_setting=()):
        QtGui.QWidget.__init__(self, parent=None)
        self.main = main

        self.startFreqFill = QtGui.QLineEdit()
        self.stopFreqFill = QtGui.QLineEdit()
        self.stepFill = QtGui.QLineEdit()
        self.avgFill = QtGui.QLineEdit()
        self.sensSel = liaSensBox()
        self.tcSel = liaTCBox()
        self.waitTimeFill = QtGui.QLineEdit()
        # validate default values
        self.val_waittime()

        self.startFreqFill.textChanged.connect(self.val_start_freq)
        self.stopFreqFill.textChanged.connect(self.val_stop_freq)
        self.stepFill.textChanged.connect(self.val_step)
        self.avgFill.textChanged.connect(self.val_avg)
        self.tcSel.currentIndexChanged.connect(self.val_waittime)
        self.waitTimeFill.textChanged.connect(self.val_waittime)

        if init_setting:
            self.startFreqFill.setText(str(init_setting[0]))
            self.stopFreqFill.setText(str(init_setting[1]))
            self.stepFill.setText(str(init_setting[2]))
            self.avgFill.setText(str(init_setting[3]))
            self.sensSel.setCurrentIndex(int(init_setting[4]))
            self.tcSel.setCurrentIndex(int(init_setting[5]))
            self.waitTimeFill.setText(str(init_setting[6]))
        else:
            pass

    def val_start_freq(self, text):

        vdi_index = self.main.synCtrl.bandSelect.currentIndex()
        status, freq = api_val.val_syn_freq(text, vdi_index)
        self.startFreqFill.setStyleSheet('border: 1px solid {:s}'.format(msgcolor(status)))

    def val_stop_freq(self, text):

        vdi_index = self.main.synCtrl.bandSelect.currentIndex()
        status, freq = api_val.val_syn_freq(text, vdi_index)
        self.stopFreqFill.setStyleSheet('border: 1px solid {:s}'.format(msgcolor(status)))

    def val_step(self, text):

        status, number = api_val.val_float(text, safe=[('>=', 0.01)], warning=[('>', 0)])
        self.stepFill.setStyleSheet('border: 1px solid {:s}'.format(msgcolor(status)))

    def val_avg(self, text):

        vdi_index = self.main.synCtrl.bandSelect.currentIndex()
        status, number = api_val.val_int(text, safe=[('>', 0)])
        self.avgFill.setStyleSheet('border: 1px solid {:s}'.format(msgcolor(status)))

    def val_waittime(self):

        text = self.waitTimeFill.text()
        tc_index = self.tcSel.currentIndex()
        status, waittime = api_val.val_lia_waittime(text, tc_index)
        self.waitTimeFill.setStyleSheet('border: 1px solid {:s}'.format(msgcolor(status)))


def msgcolor(status_code):
    ''' Return message color based on status_code.
        0: fatal, red
        1: warning, gold
        2: safe, green
        else: black
    '''

    if not status_code:
        return '#D63333'
    elif status_code == 1:
        return '#FF9933'
    elif status_code == 2:
        return '#00A352'
    else:
        return '#000000'


def gen_x_array(start, stop, step):
    ''' Generate an mm freq array for DAQ.
        Arguments
            start: start mm frequency (MHz), float
            stop: stop mm frequency (MHz), float
            step: step size (MHz), float
        Returns
            x: synthesizer RF frequency array, np.array
    '''

    # if start freq > stop freq, switch
    if start > stop:
        stop, start = start, stop
        sweep_down = True
    else:
        sweep_down = False

    # make the last point to include stop
    x = np.arange(start, stop+step, step, dtype=float)

    # if sweep down, flip x array
    if sweep_down:
        return np.flipud(x)
    else:
        return x


def jpl_scan_time(jpl_entry_settings):
    ''' Estimate the time expense of batch scan JPL style '''

    if isinstance(jpl_entry_settings, list):
        pass
    else:
        jpl_entry_settings = [jpl_entry_settings]

    total_time = 0
    for entry in jpl_entry_settings:
        start, stop, step = entry[0:3]
        # estimate total data points to be taken
        data_points = ceil((abs(stop - start) + step) / step) * entry[3]
        # time expense for this entry in seconds
        total_time += data_points * entry[6] * 1e-3

    return total_time
