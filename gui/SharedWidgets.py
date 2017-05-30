#! encoding = utf-8

from PyQt5 import QtGui, QtCore
import random
from math import ceil
import numpy as np
from pyqtgraph import siFormat, siEval
from api import validator as api_val
from api import synthesizer as api_syn
from api import lockin as api_lia
from api import pci as api_pci


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

        bandList = []

        for key in api_val.VDIBANDNAME:
            msg = 'Band {:s} (x{:d}): {:d}-{:d} GHz'.format(
                  api_val.VDIBANDNAME[key], api_val.VDIBANDMULTI[key],
                  *api_val.VDIBANDRANGE[key])
            bandList.append(msg)

        self.addItems(bandList)
        self.setCurrentIndex(4)


class LIASensBox(QtGui.QComboBox):
    ''' Lockin sensitivity selection box '''

    def __init__(self):
        QtGui.QWidget.__init__(self)

        self.addItems(api_lia.SENS_LIST)
        self.setCurrentIndex(26)


class LIATCBox(QtGui.QComboBox):
    ''' Lockin time constant selection box '''

    def __init__(self):
        QtGui.QWidget.__init__(self)

        self.addItems(api_lia.TC_LIST)
        self.setCurrentIndex(5)


class SynInfo():
    ''' Synthesizer info '''

    def __init__(self):

        self.instName = ''
        self.instInterface = ''
        self.instInterfaceNum = 0
        self.instRemoteDisp = False
        self.rfToggle = False
        self.synPower = -20
        self.synFreq = 3*1e10      # Hz
        self.vdiBandIndex = 4
        self.vdiBandMultiplication = api_val.VDIBANDMULTI[self.vdiBandIndex]
        self.probFreq = self.synFreq * self.vdiBandMultiplication
        self.modToggle = False
        self.modModeIndex = 0
        self.modModeText = ''     # ['NONE', 'AM', 'FM']
        self.modFreq = 0          # update according to modMode
        self.modAmp = 0           # update according to modMode
        self.AM1Toggle = False
        self.AM1Freq = 0          # Hz
        self.AM1DepthPercent = 0  # float, percent
        self.AM1DepthDbm = -20    # dbm
        self.AM1Src = ''
        self.AM1Wave = ''
        self.AM2Toggle = False
        self.AM2Freq = 0          # Hz
        self.AM2DepthPercent = 0  # float, percent
        self.AM2DepthDbm = -20    # dbm
        self.AM2Src = ''
        self.AM2Wave = ''
        self.FM1Toggle = False
        self.FM1Freq = 0          # Hz
        self.FM1Dev = 0           # Hz
        self.FM1Src = ''
        self.FM1Wave = ''
        self.FM2Toggle = False
        self.FM2Freq = 0          # Hz
        self.FM2Dev = 0           # Hz
        self.FM2Src = ''
        self.FM2Wave = ''
        self.PM1Toggle = False
        self.PM1Freq = 0          # Hz
        self.PM1Dev = 0           # Hz
        self.PM1Src = ''
        self.PM1Wave = ''
        self.PM2Toggle = False
        self.PM2Freq = 0          # Hz
        self.PM2Dev = 0           # Hz
        self.PM2Src = ''
        self.PM2Wave = ''
        self.LFToggle = False
        self.LFVoltage = 0
        self.LFSrc = ''
        self.errMsg = ''

    def full_info_query(self, synHandle):
        ''' Query all information '''

        if synHandle:
            self.instName = synHandle.resource_name
            self.instInterface = str(synHandle.interface_type)
            self.instInterfaceNum = synHandle.interface_number
            self.instRemoteDisp = api_syn.read_remote_disp(synHandle)
            self.rfToggle = api_syn.read_power_toggle(synHandle)
            self.synPower = api_syn.read_syn_power(synHandle)
            self.synFreq = api_syn.read_syn_freq(synHandle)
            self.probFreq = self.synFreq * self.vdiBandMultiplication
            self.modToggle = api_syn.read_mod_toggle(synHandle)
            self.AM1Toggle = api_syn.read_am_state(synHandle, 1)
            self.AM1Freq = api_syn.read_am_freq(synHandle, 1)
            self.AM1DepthPercent, self.AM1DepthDbm = api_syn.read_am_depth(synHandle, 1)
            self.AM1Src = api_syn.read_am_source(synHandle, 1)
            self.AM1Wave = api_syn.read_am_waveform(synHandle, 1)
            self.AM2Toggle = api_syn.read_am_state(synHandle, 2)
            self.AM2Freq = api_syn.read_am_freq(synHandle, 2)
            self.AM2DepthPercent, self.AM2DepthDbm = api_syn.read_am_depth(synHandle, 2)
            self.AM2Src = api_syn.read_am_source(synHandle, 2)
            self.AM2Wave = api_syn.read_am_waveform(synHandle, 2)
            self.FM1Toggle = api_syn.read_fm_state(synHandle, 1)
            self.FM1Freq = api_syn.read_fm_freq(synHandle, 1)
            self.FM1Dev = api_syn.read_fm_dev(synHandle, 1)
            self.FM1Src = api_syn.read_fm_source(synHandle, 1)
            self.FM1Wave = api_syn.read_fm_waveform(synHandle, 1)
            self.FM2Toggle = api_syn.read_fm_state(synHandle, 2)
            self.FM2Freq = api_syn.read_fm_freq(synHandle, 2)
            self.FM2Dev = api_syn.read_fm_dev(synHandle, 2)
            self.FM2Src = api_syn.read_fm_source(synHandle, 2)
            self.FM2Wave = api_syn.read_fm_waveform(synHandle, 2)
            self.PM1Toggle = api_syn.read_pm_state(synHandle, 1)
            self.PM1Freq = api_syn.read_pm_freq(synHandle, 1)
            self.PM1Dev = api_syn.read_pm_dev(synHandle, 1)
            self.PM1Src = api_syn.read_pm_source(synHandle, 1)
            self.PM1Wave = api_syn.read_pm_waveform(synHandle, 1)
            self.PM2Toggle = api_syn.read_pm_state(synHandle, 2)
            self.PM2Freq = api_syn.read_pm_freq(synHandle, 2)
            self.PM2Dev = api_syn.read_pm_dev(synHandle, 2)
            self.PM2Src = api_syn.read_pm_source(synHandle, 2)
            self.PM2Wave = api_syn.read_pm_waveform(synHandle, 2)
            self.LFToggle = api_syn.read_lf_toggle(synHandle)
            self.LFVoltage = api_syn.read_lf_voltage(synHandle)
            self.LFSrc = api_syn.read_lf_source(synHandle)
            self.errMsg = ''
        else:
            self.instName = 'No Instrument'


class LiaInfo():
    ''' Lockin amplifier info '''

    def __init__(self):

        self.instName = ''
        self.instInterface = ''
        self.instInterfaceNum = 0
        self.refSrcIndex = 0
        self.refSrcText = ''
        self.refFreq = 1
        self.refPhase = 0
        self.refHarm = 1
        self.refHarmText = str(self.refHarm)
        self.refHarmIndex = self.refHarm - 1
        self.configIndex = 1
        self.configText = api_lia.INPUT_CONFIG_LIST[self.configIndex]
        self.groundingIndex = 1
        self.groundingText = api_lia.INPUT_GND_LIST[self.groundingIndex]
        self.coupleIndex = 1
        self.coupleText = api_lia.COUPLE_LIST[self.coupleIndex]
        self.inputFilterIndex = 1
        self.inputFilterText = api_lia.INPUT_FILTER_LIST[self.inputFilterIndex]
        self.sensIndex = 26
        self.sensText = api_lia.SENS_LIST[self.sensIndex]
        self.tcIndex = 5
        self.tcText = api_lia.TC_LIST[self.tcIndex]
        self.reserveIndex = 1
        self.reserveText = api_lia.RESERVE_LIST[self.reserveIndex]
        self.lpSlopeIndex = 0
        self.lpSlopeText = api_lia.LPSLOPE_LIST[self.lpSlopeIndex]
        self.disp1Text = ''
        self.disp2Text = ''
        self.front1Text = ''
        self.front2Text = ''
        self.sampleRateIndex = 0
        self.sampleRateText = api_lia.SAMPLE_RATE_LIST[self.sampleRateIndex]

    def full_info_query(self, liaHandle):
        ''' Query all information '''

        if liaHandle:
            self.instName = liaHandle.resource_name
            self.instInterface = str(liaHandle.interface_type)
            self.instInterfaceNum = liaHandle.interface_number
            self.refSrcIndex = api_lia.read_ref_source(liaHandle)
            self.refSrcText = api_lia.REF_SRC_LIST[self.refSrcIndex]
            self.refFreq = api_lia.read_freq(liaHandle)
            self.refPhase = api_lia.read_phase(liaHandle)
            self.refHarm = api_lia.read_harm(liaHandle)
            self.refHarmText = str(self.refHarm)
            self.refHarmIndex = self.refHarm - 1
            self.configIndex = api_lia.read_input_config(liaHandle)
            self.configText = api_lia.INPUT_CONFIG_LIST[self.configIndex]
            self.groundingIndex = api_lia.read_input_grounding(liaHandle)
            self.groundingText = api_lia.INPUT_GND_LIST[self.groundingIndex]
            self.coupleIndex = api_lia.read_couple(liaHandle)
            self.coupleText = api_lia.COUPLE_LIST[self.coupleIndex]
            self.inputFilterIndex = api_lia.read_input_filter(liaHandle)
            self.inputFilterText = api_lia.INPUT_FILTER_LIST[self.inputFilterIndex]
            self.sensIndex = api_lia.read_sens(liaHandle)
            self.sensText = api_lia.SENS_LIST[self.sensIndex]
            self.tcIndex = api_lia.read_tc(liaHandle)
            self.tcText = api_lia.TC_LIST[self.tcIndex]
            self.reserveIndex = api_lia.read_reserve(liaHandle)
            self.reserveText = api_lia.RESERVE_LIST[self.reserveIndex]
            self.lpSlopeIndex = api_lia.read_lp_slope(liaHandle)
            self.lpSlopeText = api_lia.LPSLOPE_LIST[self.lpSlopeIndex]
            self.disp1Text, self.disp2Text = api_lia.read_disp(liaHandle)
            self.front1Text, self.front2Text = api_lia.read_front_panel(liaHandle)
            self.sampleRateIndex = api_lia.read_sample_rate(liaHandle)
            self.sampleRateText = api_lia.SAMPLE_RATE_LIST[self.sampleRateIndex]
        else:
            self.instName = 'No Instrument'


class ScopeInfo():
    ''' PCI card Oscilloscope info '''

    def __init__(self):

        self.instName = ''


class MotorInfo():
    ''' Step motor info '''

    def __init__(self):

        self.instName = ''


class JPLLIAScanEntry(QtGui.QWidget):
    ''' Frequency window entry for scanning job configuration with captions '''

    def __init__(self, main, default=()):
        QtGui.QWidget.__init__(self)
        self.main = main
        self.status = {'startFreq': True,
                       'stopFreq': True,
                       'step': True,
                       'avg': True,
                       'waittime': True,
                       'modFreq': True,
                       'modAmp': True,
                       'refHarm': True,
                       'refPhase': True}      # overall validator status

        self.commentFill = QtGui.QLineEdit()
        self.startFreqFill = QtGui.QLineEdit()
        self.stopFreqFill = QtGui.QLineEdit()
        self.stepFill = QtGui.QLineEdit()
        self.avgFill = QtGui.QLineEdit()
        self.sensSel = LIASensBox()
        self.tcSel = LIATCBox()
        self.waitTimeFill = QtGui.QLineEdit()
        self.modModeSel = QtGui.QComboBox()
        self.modModeSel.addItems(api_syn.MOD_MODE_LIST)
        self.modFreqFill = QtGui.QLineEdit()
        self.modAmpFill = QtGui.QLineEdit()
        self.modAmpUnitLabel = QtGui.QLabel()

        self.harmSel = QtGui.QComboBox()
        self.harmSel.addItems(['1', '2', '3', '4'])
        self.refPhaseFill = QtGui.QLineEdit()

        self.startFreqFill.textChanged.connect(self.val_start_freq)
        self.stopFreqFill.textChanged.connect(self.val_stop_freq)
        self.startFreqFill.textChanged.connect(self.val_step)
        self.stopFreqFill.textChanged.connect(self.val_step)
        self.stepFill.textChanged.connect(self.val_step)
        self.avgFill.textChanged.connect(self.val_avg)
        self.tcSel.currentIndexChanged.connect(self.val_waittime)
        self.waitTimeFill.textChanged.connect(self.val_waittime)
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
        self.tcSel.setCurrentIndex(default[6])
        self.waittime = default[7]
        self.waitTimeFill.setText('{:g}'.format(self.waittime))
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

        vdi_index = self.main.synCtrl.bandSel.currentIndex()
        status, _temp = api_val.val_prob_freq(text, vdi_index)
        self.startFreqFill.setStyleSheet('border: 1px solid {:s}'.format(msgcolor(status)))
        self.status['startFreq'] = bool(status)
        self.startFreq = _temp * self.main.synInfo.vdiBandMultiplication * 1e-6

    def val_stop_freq(self, text):

        vdi_index = self.main.synCtrl.bandSel.currentIndex()
        status, _temp = api_val.val_prob_freq(text, vdi_index)
        self.stopFreqFill.setStyleSheet('border: 1px solid {:s}'.format(msgcolor(status)))
        self.status['stopFreq'] = bool(status)
        self.stopFreq = _temp * self.main.synInfo.vdiBandMultiplication * 1e-6

    def val_step(self):

        win = abs(self.startFreq - self.stopFreq)
        text = self.stepFill.text()
        status, self.step = api_val.val_float(text, safe=[('>=', 0.01), ('<', win)],
                                              warning=[('>', 0), ('<', win)])
        self.stepFill.setStyleSheet('border: 1px solid {:s}'.format(msgcolor(status)))
        self.status['step'] = bool(status)

    def val_avg(self, text):

        vdi_index = self.main.synCtrl.bandSel.currentIndex()
        status, self.avg = api_val.val_int(text, safe=[('>', 0)])
        self.avgFill.setStyleSheet('border: 1px solid {:s}'.format(msgcolor(status)))
        self.status['avg'] = bool(status)

    def val_waittime(self):

        text = self.waitTimeFill.text()
        tc_index = self.tcSel.currentIndex()
        status, self.waittime = api_val.val_lia_waittime(text, tc_index)
        self.waitTimeFill.setStyleSheet('border: 1px solid {:s}'.format(msgcolor(status)))
        self.status['waittime'] = bool(status)

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

        self.modFreqFill.setStyleSheet('border: 1px solid {:s}'.format(msgcolor(status)))
        self.harmSel.setStyleSheet('border: 1px solid {:s}'.format(msgcolor(status)))

        self.status['modFreq'] = bool(status1)
        self.status['refHarm'] = bool(status2)

    def val_syn_amp(self, text):

        if self.modModeSel.currentIndex() == 1:     # AM
            status, self.modAmp = api_val.val_syn_am_depth(text, '%')
        elif self.modModeSel.currentIndex() == 2:   # FM
            status, self.modAmp = api_val.val_syn_fm_depth(text, 'Hz')
        else:
            status = 2

        self.modAmpFill.setStyleSheet('border: 1px solid {:s}'.format(msgcolor(status)))
        self.status['modAmp'] = bool(status)

    def val_lia_phase(self, text):

        status, self.refPhase = api_val.val_lia_phase(text)
        self.refPhaseFill.setStyleSheet('border: 1px solid {:s}'.format(msgcolor(status)))
        self.status['refPhase'] = bool(status)

    def update_lia_harm(self, text):

        self.refHarm = int(text)

class JPLLIABatchListEntry(QtGui.QWidget):
    ''' Single batch list entry in display mode.
    entry = (comment [str], start [float, MHz], stop [float, MHz],
             step [float, MHz], avg [int], sens_idx [int], tc_idx [int],
             mod mode index [int], harmonics [int]) '''

    def __init__(self, parent, entry_setting=()):
        QtGui.QWidget.__init__(self, parent=None)
        self.parent = parent

        # add labels
        self.numberLabel = QtGui.QLabel()
        self.commentFill = QtGui.QLineEdit()
        self.startFreqLabel = QtGui.QLabel()
        self.stopFreqLabel = QtGui.QLabel()
        self.stepLabel = QtGui.QLabel()
        self.avgLabel = QtGui.QLabel()
        self.sensLabel = QtGui.QLabel()
        self.tcLabel = QtGui.QLabel()
        self.modModeLabel = QtGui.QLabel()
        self.refHarmLabel = QtGui.QLabel()

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
        ''' set text color to grey '''
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
        ''' Set text color to black '''

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


class LWAScanHdEntry(QtGui.QWidget):
    ''' Display lwa scan header settings.
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
             ) '''

    def __init__(self, parent, entry_setting=()):
        QtGui.QWidget.__init__(self, parent=None)
        self.parent = parent

        # add labels
        self.previewCheck = QtGui.QCheckBox()
        self.exportCheck = QtGui.QCheckBox()
        self.scanNumLabel = QtGui.QLabel()
        self.commentLabel = QtGui.QLabel()
        self.dateLabel = QtGui.QLabel()
        self.timeLabel = QtGui.QLabel()
        self.itLabel = QtGui.QLabel()
        self.sensLabel = QtGui.QLabel()
        self.tcLabel = QtGui.QLabel()
        self.modModeLabel = QtGui.QLabel()
        self.modFreqLabel = QtGui.QLabel()
        self.modAmpLabel = QtGui.QLabel()
        self.startFreqLabel = QtGui.QLabel()
        self.stopFreqLabel = QtGui.QLabel()
        self.stepLabel = QtGui.QLabel()
        self.ptsLabel = QtGui.QLabel()
        self.avgLabel = QtGui.QLabel()
        self.harmLabel = QtGui.QLabel()
        self.phaseLabel = QtGui.QLabel()

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
        start, stop, step = entry[1:4]
        # estimate total data points to be taken
        data_points = ceil((abs(stop - start) + step) / step) * entry[4]
        # time expense for this entry in seconds
        total_time += data_points * entry[7] * 1e-3

    return total_time
