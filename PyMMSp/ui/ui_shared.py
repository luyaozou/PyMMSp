#! encoding = utf-8

from PyQt6 import QtWidgets
import random
from math import ceil, floor, log10
import numpy as np
from pyqtgraph import siFormat
from PyMMSp.inst import lockin as api_lia
from PyMMSp.inst import validator as api_val
from PyMMSp.inst import synthesizer as api_syn
from PyMMSp.libs.consts import BUTTONLABEL


# QPushButton label dictionary


def btn_label(btn_type):
    """ Randomly generate a QPushButton label.
        Arguments
            btn_type: str
        Returns
            label: str
    """

    try:
        a_list = BUTTONLABEL[btn_type]
        return a_list[random.randint(0, len(a_list)-1)]
    except KeyError:
        return 'A Button'


class InstStatus(QtWidgets.QMessageBox):
    """ Message box of instrument communication status. Silent if communication
        is successful. Pop up error message in pyvisa.constants.StatusCode
    """

    def __init__(self, parent, code):
        QtWidgets.QWidget.__init__(self, parent)

        self.setIcon(QtWidgets.QMessageBox.Icon.Critical)
        self.addButton(QtWidgets.QMessageBox.StandardButton.Ok)
        self.setText(str(code))
        self.setWindowTitle('Instrument Communication Failure!')


class MsgError(QtWidgets.QMessageBox):
    """ Error message box """

    def __init__(self, parent, title_text, moretext=''):
        QtWidgets.QWidget.__init__(self, parent)

        self.setIcon(QtWidgets.QMessageBox.Icon.Critical)
        self.addButton(QtWidgets.QMessageBox.StandardButton.Ok)
        self.setWindowTitle(title_text)
        self.setText(moretext)


class MsgWarning(QtWidgets.QMessageBox):
    """ Warning message box """

    def __init__(self, parent, title_text, moretext=''):
        QtWidgets.QWidget.__init__(self, parent)

        self.setIcon(QtWidgets.QMessageBox.Icon.Warning)
        self.addButton(QtWidgets.QMessageBox.StandardButton.Ok)
        self.setWindowTitle(title_text)
        self.setText(moretext)


class MsgInfo(QtWidgets.QMessageBox):
    """ Information message box """

    def __init__(self, parent, title_text, moretext=''):
        QtWidgets.QWidget.__init__(self, parent)

        self.setIcon(QtWidgets.QMessageBox.Icon.Information)
        self.addButton(QtWidgets.QMessageBox.StandardButton.Ok)
        self.setWindowTitle(title_text)
        self.setText(moretext)


class JPLLIAScanEntry(QtWidgets.QWidget):
    """ Frequency window entry for scanning job configuration with captions """

    def __init__(self, main, default=()):
        QtWidgets.QWidget.__init__(self)
        self.main = main
        self.status = {'startFreq': True,
                       'stopFreq': True,
                       'step': True,
                       'avg': True,
                       'wait_time': True,
                       'modFreq': True,
                       'modAmp': True,
                       'refHarm': True,
                       'refPhase': True}      # overall validator status

        self.commentFill = QtWidgets.QLineEdit()
        self.startFreqFill = QtWidgets.QLineEdit()
        self.stopFreqFill = QtWidgets.QLineEdit()
        self.stepFill = QtWidgets.QLineEdit()
        self.avgFill = QtWidgets.QLineEdit()
        self.sensSel = QtWidgets.QComboBox()
        self.sensSel.addItems(api_lia.SENS_STR)
        self.tauSel = QtWidgets.QComboBox()
        self.tauSel.addItems(api_lia.TAU_STR)
        self.waitTimeFill = QtWidgets.QLineEdit()
        self.modModeSel = QtWidgets.QComboBox()
        self.modModeSel.addItems(api_syn.MODU_MODE)
        self.modFreqFill = QtWidgets.QLineEdit()
        self.modAmpFill = QtWidgets.QLineEdit()
        self.modAmpUnitLabel = QtWidgets.QLabel()

        self.harmSel = QtWidgets.QComboBox()
        self.harmSel.addItems(['1', '2', '3', '4'])
        self.refPhaseFill = QtWidgets.QLineEdit()

        self.startFreqFill.textChanged.connect(self.val_start_freq)
        self.stopFreqFill.textChanged.connect(self.val_stop_freq)
        self.startFreqFill.textChanged.connect(self.val_step)
        self.stopFreqFill.textChanged.connect(self.val_step)
        self.stepFill.textChanged.connect(self.val_step)
        self.avgFill.textChanged.connect(self.val_avg)
        self.tauSel.currentIndexChanged.connect(self.val_wait_time)
        self.waitTimeFill.textChanged.connect(self.val_wait_time)
        self.modModeSel.currentIndexChanged.connect(self.set_mod_mode)
        self.modFreqFill.textChanged.connect(self.val_syn_mod_freq)
        self.modAmpFill.textChanged.connect(self.val_syn_amp)
        self.harmSel.currentIndexChanged[str].connect(self.update_lia_harm)
        self.refPhaseFill.textChanged.connect(self.val_lia_phase)

        # set up default values
        self.commentStr = str(default[0])
        self.commentFill.setText(self.commentStr)
        self.startFreq = default[1]
        self.stopFreq = default[2]
        # the value assign for self.stopFreq has to proceed first
        # because once self.startFreqFill is set, it triggers the val_step
        # which will need self.stopFreq
        self.startFreqFill.setText('{:.3f}'.format(self.startFreq))
        self.stopFreqFill.setText('{:.3f}'.format(self.stopFreq))
        self.step = default[3]
        self.stepFill.setText('{:.3f}'.format(self.step))
        self.avg = default[4]
        self.avgFill.setText(str(self.avg))
        self.sensSel.setCurrentIndex(default[5])
        self.tauSel.setCurrentIndex(default[6])
        self.wait_time = default[7]
        self.waitTimeFill.setText('{:g}'.format(self.wait_time))
        self.modFreq = default[9]
        self.modFreqFill.setText('{:g}'.format(self.modFreq))
        self.modAmp = default[10]
        self.modAmpFill.setText('{:g}'.format(self.modAmp))
        self.refHarm = default[11]
        self.harmSel.setCurrentIndex(self.refHarm-1 if self.refHarm < 5 else 0)
        self.refPhase = default[12]
        self.refPhaseFill.setText('{:.2f}'.format(self.refPhase))
        self.modModeSel.setCurrentIndex(default[8])
        self.set_mod_mode(default[8])

    def set_mod_mode(self, index):

        if (not index):     # no modulation, turn off mod freq edits
            self.modFreqFill.setReadOnly(True)
            self.modAmpFill.setReadOnly(True)
            self.modFreqFill.setStyleSheet('color: grey')
            self.modAmpFill.setStyleSheet('color: grey')
            # bypass mod & harmonics validation status
            self.status['refHarm'] = True
            self.status['modFreq'] = True
            self.status['modAmp'] = True
            self.modAmpUnitLabel.setText('')
        else:
            self.modFreqFill.setReadOnly(False)
            self.modAmpFill.setReadOnly(False)
            self.modFreqFill.setStyleSheet('color: black')
            self.modAmpFill.setStyleSheet('color: black')
            if index == 1:
                self.modAmpUnitLabel.setText('%')
            elif index == 2:
                self.modAmpUnitLabel.setText('Hz')
            else:
                pass
            # recheck the values
            self.val_syn_mod_freq(self.modFreqFill.text())
            self.val_syn_amp(self.modAmpFill.text())


    def val_start_freq(self, text):

        vdi_index = self.main.synPanel.bandSel.currentIndex()
        status, _temp = api_val.val_prob_freq(text, vdi_index)
        self.startFreqFill.setStyleSheet('border: 1px solid {:s}'.format(msg_color(status)))
        self.status['startFreq'] = bool(status)
        self.startFreq = _temp * self.main.synInfo.vdiBandMultiplication * 1e-6

    def val_stop_freq(self, text):

        vdi_index = self.main.synPanel.bandSel.currentIndex()
        status, _temp = api_val.val_prob_freq(text, vdi_index)
        self.stopFreqFill.setStyleSheet('border: 1px solid {:s}'.format(msg_color(status)))
        self.status['stopFreq'] = bool(status)
        self.stopFreq = _temp * self.main.synInfo.vdiBandMultiplication * 1e-6

    def val_step(self):

        win = abs(self.startFreq - self.stopFreq)
        text = self.stepFill.text()
        status, self.step = api_val.val_float(text, safe=[('>=', 0.01), ('<', win)],
                                              warning=[('>', 0), ('<', win)])
        self.stepFill.setStyleSheet('border: 1px solid {:s}'.format(msg_color(status)))
        self.status['step'] = bool(status)

    def val_avg(self, text):

        band_idx = self.main.synPanel.bandSel.currentIndex()
        status, self.avg = api_val.val_int(text, safe=[('>', 0)])
        self.avgFill.setStyleSheet('border: 1px solid {:s}'.format(msg_color(status)))
        self.status['avg'] = bool(status)

    def val_wait_time(self):

        txt = self.waitTimeFill.text()
        tau_idx = self.tauSel.currentIndex()
        status, self.wait_time = api_val.val_lia_wait_time(txt, tau_idx)
        self.waitTimeFill.setStyleSheet('border: 1px solid {:s}'.format(msg_color(status)))
        self.status['wait_time'] = bool(status)

    def val_syn_mod_freq(self, text):

        try:
            status1, self.modFreq = api_val.val_syn_mod_freq(text, 'Hz')
        except:
            status1, self.modFreq = 0, 0

        try:
            status2, self.refHarm = api_val.val_lia_harm(self.harmSel.currentText(), self.modFreq)
        except:
            status2, self.refHarm = 0, 1

        # if no modulation, move forward
        if self.modModeSel.currentIndex():
            # this ceil(status1 * status2 /2) trick makes sure
            # only safe (2) if both status are 2, warning (1) if one is warning, and fatal (0) if any of the two is 0
            status = ceil(status1 * status2 / 2)
        else:
            status = 2

        self.modFreqFill.setStyleSheet('border: 1px solid {:s}'.format(msg_color(status)))
        self.harmSel.setStyleSheet('border: 1px solid {:s}'.format(msg_color(status)))

        self.status['modFreq'] = bool(status1)
        self.status['refHarm'] = bool(status2)

    def val_syn_amp(self, text):

        if self.modModeSel.currentIndex() == 1:     # AM
            status, self.modAmp = api_val.val_syn_am_amp(text, '%')
        elif self.modModeSel.currentIndex() == 2:   # FM
            status, self.modAmp = api_val.val_syn_fm_amp(text, 'Hz')
        else:
            status = 2

        self.modAmpFill.setStyleSheet('border: 1px solid {:s}'.format(msg_color(status)))
        self.status['modAmp'] = bool(status)

    def val_lia_phase(self, text):

        status, self.refPhase = api_val.val_lia_phase(text)
        self.refPhaseFill.setStyleSheet('border: 1px solid {:s}'.format(msg_color(status)))
        self.status['refPhase'] = bool(status)

    def update_lia_harm(self, text):

        self.refHarm = int(text)

class JPLLIABatchListEntry(QtWidgets.QWidget):
    """ Single batch list entry in display mode.
    entry = (comment [str], start [float, MHz], stop [float, MHz],
             step [float, MHz], avg [int], sens_idx [int], tc_idx [int],
             mod mode index [int], harmonics [int]) """

    def __init__(self, parent, entry_setting=()):
        QtWidgets.QWidget.__init__(self, parent=None)
        self.parent = parent

        # add labels
        self.numberLabel = QtWidgets.QLabel()
        self.commentFill = QtWidgets.QLineEdit()
        self.startFreqLabel = QtWidgets.QLabel()
        self.stopFreqLabel = QtWidgets.QLabel()
        self.stepLabel = QtWidgets.QLabel()
        self.avgLabel = QtWidgets.QLabel()
        self.sensLabel = QtWidgets.QLabel()
        self.tcLabel = QtWidgets.QLabel()
        self.modModeLabel = QtWidgets.QLabel()
        self.refHarmLabel = QtWidgets.QLabel()

        # set label text
        self.commentFill.setText(entry_setting[0])
        self.startFreqLabel.setText('{:.3f}'.format(entry_setting[1]))
        self.stopFreqLabel.setText('{:.3f}'.format(entry_setting[2]))
        self.stepLabel.setText('{:.3f}'.format(entry_setting[3]))
        self.avgLabel.setText('{:d}'.format(entry_setting[4]))
        self.sensLabel.setText(api_lia.SENS_LIST[entry_setting[5]])
        self.tcLabel.setText(api_lia.TC_LIST[entry_setting[6]])
        self.modModeLabel.setText(api_syn.MOD_MODE_LIST[entry_setting[8]])
        self.refHarmLabel.setText('{:d}'.format(entry_setting[11]))

        # set text color to grey
        self.set_color_grey()

    def set_color_grey(self):
        """ set text color to grey """
        self.numberLabel.setStyleSheet('color: grey')
        self.startFreqLabel.setStyleSheet('color: grey')
        self.stopFreqLabel.setStyleSheet('color: grey')
        self.stepLabel.setStyleSheet('color: grey')
        self.avgLabel.setStyleSheet('color: grey')
        self.sensLabel.setStyleSheet('color: grey')
        self.tcLabel.setStyleSheet('color: grey')
        self.modModeLabel.setStyleSheet('color: grey')
        self.refHarmLabel.setStyleSheet('color: grey')

    def set_color_black(self):
        """ Set text color to black """

        # set texts to grey
        self.numberLabel.setStyleSheet('color: black')
        self.startFreqLabel.setStyleSheet('color: black')
        self.stopFreqLabel.setStyleSheet('color: black')
        self.stepLabel.setStyleSheet('color: black')
        self.avgLabel.setStyleSheet('color: black')
        self.sensLabel.setStyleSheet('color: black')
        self.tcLabel.setStyleSheet('color: black')
        self.modModeLabel.setStyleSheet('color: black')
        self.refHarmLabel.setStyleSheet('color: black')


class LWAScanHdEntry(QtWidgets.QWidget):
    """ Display lwa scan header settings.
    entry = (SCAN# [int],
             COMMENT [str],
             DATE [str],
             TIME [str],
             IT [float, ms],
             SENS [float, V],
             TAU [float, s],
             MMODE [str],
             MFREQ [float, kHz],
             MAMP [float, kHz],
             START [float, MHz],
             STOP [float, MHz],
             STEP [float, MHz],
             PTS [int],
             AVG [int],
             HARM [int],
             PHASE [float, degree]
             ) """

    def __init__(self, parent, entry_setting=()):
        QtWidgets.QWidget.__init__(self, parent=None)
        self.parent = parent

        # add labels
        self.previewCheck = QtWidgets.QCheckBox()
        self.exportCheck = QtWidgets.QCheckBox()
        self.scanNumLabel = QtWidgets.QLabel()
        self.commentLabel = QtWidgets.QLabel()
        self.dateLabel = QtWidgets.QLabel()
        self.timeLabel = QtWidgets.QLabel()
        self.itLabel = QtWidgets.QLabel()
        self.sensLabel = QtWidgets.QLabel()
        self.tcLabel = QtWidgets.QLabel()
        self.modModeLabel = QtWidgets.QLabel()
        self.modFreqLabel = QtWidgets.QLabel()
        self.modAmpLabel = QtWidgets.QLabel()
        self.startFreqLabel = QtWidgets.QLabel()
        self.stopFreqLabel = QtWidgets.QLabel()
        self.stepLabel = QtWidgets.QLabel()
        self.ptsLabel = QtWidgets.QLabel()
        self.avgLabel = QtWidgets.QLabel()
        self.harmLabel = QtWidgets.QLabel()
        self.phaseLabel = QtWidgets.QLabel()

        # set label text
        self.scanNumLabel.setText(str(entry_setting[0]))
        self.commentLabel.setText(entry_setting[1])
        self.dateLabel.setText(entry_setting[2])
        self.timeLabel.setText(entry_setting[3])
        self.itLabel.setText(siFormat(entry_setting[4]*1e-3, suffix='s'))
        self.sensLabel.setText(siFormat(entry_setting[5], suffix='V'))
        self.tcLabel.setText(siFormat(entry_setting[6], suffix='s'))
        self.modModeLabel.setText(entry_setting[7])
        self.modFreqLabel.setText(siFormat(entry_setting[8]*1e3, suffix='Hz'))
        self.modAmpLabel.setText(siFormat(entry_setting[9]*1e3, suffix='Hz'))
        self.startFreqLabel.setText('{:.3f}'.format(entry_setting[10]))
        self.stopFreqLabel.setText('{:.3f}'.format(entry_setting[11]))
        self.stepLabel.setText(siFormat(entry_setting[12]*1e6, suffix='Hz'))
        self.ptsLabel.setText(str(entry_setting[13]))
        self.avgLabel.setText(str(entry_setting[14]))
        self.harmLabel.setText(str(entry_setting[15]))
        self.phaseLabel.setText('{:.2f} deg'.format(entry_setting[16]))


def msg_color(status_code):
    """ Return message color based on status_code.
        0: fatal, red
        1: warning, gold
        2: safe, green
        else: black
    """

    if not status_code:
        return '#D63333'
    elif status_code == 1:
        return '#FF9933'
    elif status_code == 2:
        return '#00A352'
    else:
        return '#000000'


def gen_x_array(start, stop, step):
    """ Generate an mm freq array for DAQ.
        Arguments
            start: start mm frequency (MHz), float
            stop: stop mm frequency (MHz), float
            step: step size (MHz), float
        Returns
            x: synthesizer RF frequency array, np.array
    """

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
    """ Estimate the time expense of batch scan JPL style """

    if isinstance(jpl_entry_settings, list):
        pass
    else:
        jpl_entry_settings = [jpl_entry_settings]

    total_time = 0
    for entry in jpl_entry_settings:
        start, stop, step = entry[1:4]
        # estimate total data points to be taken
        data_points = ceil((abs(stop - start) + step) / step) * entry[4]
        # time expense for this entry in seconds
        total_time += data_points * entry[7] * 1e-3

    return total_time


class CommStatusBulb(QtWidgets.QPushButton):
    """ Status bulb. Inherite from QPushButton, but display it
    as a round circle and cannot be pressed.
    -----
    Public methods
        setStatus(bool/int)
            Set bulb status, green(True) or red(False), or gray(-1)
    -----
    """

    def __init__(self, stat=False):
        super().__init__()

        self.setFlat(True)
        self.setStatus(stat)

    def setStatus(self, b):
        """ Set color by bool """

        if b:
            if int(b) > 0:  # green color
                self.setStyleSheet("""background-color: #6ec56e;
                                      border-style: solid;
                                      border-width:1px;
                                      border-radius:8px;
                                      border-color: #6ec56e;
                                      max-width:16px;
                                      max-height:16px;
                                      min-width:16px;
                                      min-height:16px """)
            else:           # gray color
                self.setStyleSheet("""background-color: #C0C0C0;
                                      border-style: solid;
                                      border-width:1px;
                                      border-radius:8px;
                                      border-color: #C0C0C0;
                                      max-width:16px;
                                      max-height:16px;
                                      min-width:16px;
                                      min-height:16px """)
        else:       # red color
            self.setStyleSheet("""background-color: #fe2e2e;
                                  border-style: solid;
                                  border-width:1px;
                                  border-radius:8px;
                                  border-color: #fe2e2e;
                                  max-width:16px;
                                  max-height:16px;
                                  min-width:16px;
                                  min-height:16px """)


class InstState(QtWidgets.QWidget):
    """ A packed widget to show the instrument connection state.
        Added to the pyDAQ GUI via its DialogInstState dialog window
    """

    def __init__(self, name='', addr='', port='', mask='', port_range=()):

        super().__init__()

        self._is_addr = bool(addr)
        self._is_port = isinstance(port, int)

        self.nameLabel = QtWidgets.QLabel(name)
        self.bulb = CommStatusBulb()
        self.msgLabel = QtWidgets.QLabel()
        self.msgLabel.setWordWrap(True)
        self.msgLabel.setMargin(2)
        self.msgLabel.setMinimumWidth(360)
        self.btn = QtWidgets.QPushButton('Test Connection')

        self.addrInput = QtWidgets.QLineEdit()
        if mask:
            self.addrInput.setInputMask(mask)
        else:
            pass
        self.addrInput.setMinimumWidth(90)
        self.addrInput.setMaximumWidth(120)

        if self._is_port:
            # if port is given, set the value to widget
            self.portInput = QtWidgets.QSpinBox()
            if port_range:
                self.portInput.setMinimum(port_range[0])
                self.portInput.setMaximum(port_range[1])
            else:
                pass
            self.portInput.setValue(port)
        else:
            # if no port is given, disable the widget
            self.portInput = QtWidgets.QLineEdit()
            self.portInput.setReadOnly(True)
            self.portInput.setStyleSheet('background-color: #E0E0E0')

        self.portInput.setMinimumWidth(60)
        self.portInput.setMaximumWidth(80)

    def update_state(self, is_active, addr='', port='', txt=''):
        """ Update information """
        # update connection status bulb
        self.bulb.setStatus(is_active)
        self.addrInput.setText(addr)
        if self._is_port:
            if isinstance(port, int):
                self.portInput.setValue(port)
            else:
                self.portInput.setValue(0)
        else:
            self.portInput.setText('' or port)
        # update message
        self.msgLabel.setText(txt)


class BtnSwitch(QtWidgets.QPushButton):
    """ A checkable switch button """

    def __init__(self, title='', ontxt='', offtxt=''):

        super().__init__()
        self._title = title
        self._ontxt = ontxt
        self._offtxt = offtxt
        self.setCheckable(True)
        self.setChecked(False)
        if offtxt:
            self.setText(offtxt)
        else:
            self.setText('{:s} OFF'.format(title))
        # don't add [int] because it throws keyError
        super().toggled.connect(self._change_label)

    def _change_label(self, toggle_state):

        if toggle_state:
            if self._ontxt:
                self.setText(self._ontxt)
            else:
                self.setText('{:s} ON'.format(self._title))
        else:
            if self._offtxt:
                self.setText(self._offtxt)
            else:
                self.setText('{:s} OFF'.format(self._title))



def create_double_spin_box(v, minimum=None, maximum=None, step=1., stepType=0,
                           dec=1, prefix=None, suffix=None):
    """ Create a QDoubleSpinBox with preset values """

    box = QtWidgets.QDoubleSpinBox()
    box.setSingleStep(step)
    if stepType == 0:
        box.setStepType(QtWidgets.QAbstractSpinBox.StepType.DefaultStepType)
    else:
        box.setStepType(QtWidgets.QAbstractSpinBox.StepType.AdaptiveDecimalStepType)
    box.setDecimals(dec)

    # the Pythonic convention "if minimum:" cannot be used here,
    # incase minimum / maximum actually has value zero.
    if isinstance(minimum, type(None)):
        box.setMinimum(float('-inf'))
    else:
        box.setMinimum(minimum)

    if isinstance(maximum, type(None)):
        box.setMaximum(float('inf'))
    else:
        box.setMaximum(maximum)

    if prefix:
        box.setPrefix(prefix)
    else:
        pass

    if suffix:
        box.setSuffix(suffix)
    else:
        pass

    # one needs to set the value at last so that the value
    # does not get clipped by default minimum and maximum
    box.setValue(v)

    return box


def create_int_spin_box(v, minimum=None, maximum=None, step=1, stepType=0,
                        prefix=None, suffix=None):
    """ Create a QSpinBox with preset values """

    box = QtWidgets.QSpinBox()
    if stepType == 0:
        box.setStepType(QtWidgets.QAbstractSpinBox.StepType.DefaultStepType)
    else:
        box.setStepType(QtWidgets.QAbstractSpinBox.StepType.AdaptiveDecimalStepType)
    box.setSingleStep(step)

    # the Pythonic convention "if minimum:" cannot be used here,
    # incase minimum / maximum actually has value zero.
    if isinstance(minimum, type(None)):
        box.setMinimum(-2147483648)
    else:
        box.setMinimum(floor(minimum))

    if isinstance(maximum, type(None)):
        box.setMaximum(2147483647)
    else:
        box.setMaximum(ceil(maximum))

    if prefix:
        box.setPrefix(prefix)
    else:
        pass

    if suffix:
        box.setSuffix(suffix)
    else:
        pass

    # one needs to set the value at last so that the value
    # does not get clipped by default minimum and maximum
    box.setValue(v)

    return box


def msg(title='', context='', style=''):
    """ Pop up a message dialog for information / warning
    :argument
        parent: QWiget          parent QWiget
        title: str              title string
        context: str            context string
        style: str              style of message box
            'info'              information box
            'warning'           warning box
            'critical'          critical box
    """

    if style == 'info':
        d = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, title, context)
    elif style == 'warning':
        d = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, title, context)
    elif style == 'critical':
        d = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Critical, title, context)
    else:
        d = QtWidgets.QMessageBox(QtWidgets.QMessageBox.NoIcon, title, context)
    d.exec_()
