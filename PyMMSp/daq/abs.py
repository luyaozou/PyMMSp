#! encoding = utf-8

""" Lockin scanning routine in JPL style """


from PyQt6 import QtCore, QtWidgets
import numpy as np
from math import ceil
import datetime
import os
from time import sleep

from PyMMSp.ui import ui_shared
from PyMMSp.inst import lockin as api_lia
from PyMMSp.inst import validator as api_val
from PyMMSp.inst import synthesizer as api_syn
from PyMMSp.inst.lockin import MODU_MODE, _SENS_VAL, TAU_VAL
from PyMMSp.libs import lwa
from PyMMSp.libs import common

# 3 imports for type hinting
from PyMMSp.config.config import Prefs, AbsScanSetting
from PyMMSp.ui.ui_main import MainUI
from PyMMSp.inst.base import Handles, Threads


class CtrlAbsBBScan(QtWidgets.QWidget):
    """ Controller of the absorption broadband scan """

    _next_batch_entry_signal = QtCore.pyqtSignal()
    _timer = QtCore.QTimer()
    _timer.setSingleShot(True)

    def __init__(self, prefs: Prefs, ui: MainUI, handles: Handles,
                 threads: Threads, parent=None):
        super().__init__(parent)

        self.prefs = prefs
        self.ui = ui
        self.handles = handles
        self.threads = threads

        # Initialize ui_shared settings
        # self.multiplier = self.handles.info_syn.vdiBandMultiplication

        # Initialize scan entry settings
        # self.start_rf_freq = 0
        # self.stop_rf_freq = 0
        # self.current_rf_freq = 0
        # self.acquired_avg = 0
        # self.step = 0
        # self.sens_index = 0
        # self.wait_time = 60
        self.batch_time_taken = 0
        self.this_x_idx = 0
        self.this_entry_idx = -1    # this makes sure batch starts at index 0
        self.list_settings = []
        self.x = np.array([])
        # self.x_min = 0
        # self.target_avg = 0
        # self.tc_index = 0
        # self.current_comment = ''
        self.y = np.array([])
        self.y_sum = np.array([])
        # self.pts_taken = 0

        # connect quick scan button signals
        self.ui.dAbsScan.btnPause.clicked[bool].connect(self.pause_current)
        self.ui.dAbsScan.btnStart.clicked[bool].connect(self.quick_scan_start)
        self.ui.dAbsScan.btnAbort.clicked[bool].connect(self.abort_scan)

        # connect batch scan button signals
        self.ui.dAbsScan.btnBatchSetup.clicked[bool].connect(self.ui.dAbsConfig.exec)
        self.ui.dAbsConfig.accepted.connect(self.on_setup_accepted)
        self.ui.dAbsConfig.btnEstimate.clicked[bool].connect(self._estimate_time)
        self.ui.dAbsScan.btnAccessData.clicked[bool].connect(self.open_data_folder)
        self.ui.dAbsScan.btnBatchStart.clicked[bool].connect(self.batch_start)
        self.ui.dAbsScan.btnBatchAbort.clicked[bool].connect(self.abort_scan)

        #self.ui.dAbsBBScan.redoButton.clicked.connect(self.redo_current)
        #self.ui.dAbsBBScan.restartWinButton.clicked.connect(self.restart_avg)
        #self.ui.dAbsBBScan.saveButton.clicked.connect(self.save_current)
        #self.ui.dAbsBBScan.btnSkip.clicked.connect(self.jump)
        #self.ui.dAbsBBScan.abortAllButton.clicked.connect(self.abort_all)

        #self.ui.dAbsBBScan.rejected.connect(self.abort_scan)
        #self.ui.dAbsBBScan.saveButton.clicked.connect(self.set_file_directory)
        #self.ui.dAbsBBScan.addBatchButton.clicked.connect(self.add_entry)
        #self.ui.dAbsBBScan.removeBatchButton.clicked.connect(self.remove_entry)


    def on_setup_accepted(self):
        self.list_settings = self.ui.dAbsConfig.get_list_settings()
        self.ui.dAbsScan.batchListWidget.add_entries(self.list_settings)

    def open_data_folder(self):
        directory = self.ui.dAbsConfig.lblDir.text()
        os.startfile(directory)

    def quick_scan_start(self):
        """ Start a quick scan. It is equivalent to put a single item into the batch job queue and then start it. """
        # get settings from quick scan setup
        scan_setting = self.ui.dAbsScan.get_quick_scan_settings()
        self.list_settings = [scan_setting, ]
        # write this to the batch job queue
        self.ui.dAbsConfig.add_setting_list(self.list_settings)
        self.ui.dAbsConfig.ckPress.setChecked(scan_setting.is_press)
        self.ui.dAbsScan.batchListWidget.add_entries(self.list_settings)
        # start batch job
        self.batch_start()

    def batch_start(self):
        """ Start a batch scan """
        try:
            # Initiate progress bar
            total_time = ceil(estimate_job_time(self.list_settings))
            self.ui.dAbsScan.totalProgBar.setRange(0, total_time)
            self.ui.dAbsScan.totalProgBar.setValue(0)
            self.batch_time_taken = 0
            # Start scan
            t = ThreadBatchScan(self.prefs, self.handles, self.threads, self.list_settings, parent=self)
            t.sig_total_progress.connect(self.ui.dAbsScan.totalProgBar.setValue)
            t.sig_this_progress.connect(self.ui.dAbsScan.currentProgBar.setValue)
            t.sig_this_n.connect(self.ui.dAbsScan.currentProgBar.setMaximum)
            t.sig_data_ready.connect(self.ui.dAbsScan.plot_this)
            t.start()
        except ZeroDivisionError:
            q = ui_shared.MsgError(self, 'Zero step', 'Step cannot be 0.')
            q.exec()

    def _estimate_time(self):
        try:
            total_time = estimate_job_time(self.ui.dAbsConfig.get_list_settings())
            now = datetime.datetime.today()
            length = datetime.timedelta(seconds=total_time)
            time_finish = now + length
            str_duration = common.format_timedelta(length)
            str_finish = time_finish.strftime('%I:%M %p, %m-%d-%Y (%a)')
            text = (f'This batch job is estimated to take {str_duration:s}.\n'
                    f'It is expected to finish at {str_finish:s}.')
            q = ui_shared.MsgInfo(self, 'Time Estimation', text)
            q.exec()
        except ZeroDivisionError:
            q = ui_shared.MsgError(self, 'Zero step', 'Step cannot be 0.')
            q.exec()

    def set_file_directory(self):

        self.filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, 'Save Data', '', 'SMAP File (*.lwa)')
        self.ui.dAbsScan.lblDir.setText('Data save to: {:s}'.format(self.filename))

    def tune_syn_freq(self):
            """ Simply tune synthesizer frequency """

            self.handles.info_syn.probFreq = self.x[self.this_x_idx] * 1e6
            self.handles.info_syn.synFreq = self.handles.info_syn.probFreq / self.handles.info_syn.harm
            #self.main.synStatus.print_info()

            if self.prefs.is_test:
                pass
            else:
                api_syn.set_syn_freq(self.handles.h_syn, self.handles.info_syn.synFreq)
            self._timer.start()

    def query_lockin(self):
        """ Query lock-in data. Triggered by self._timer.timeout() """

        # append data to data list
        if self.prefs.is_test:
            self.y[self.this_x_idx] = np.random.random_sample()
        else:
            self.y[self.current_x_index] = self.handles.api_lockin.query_single_x(self.handles.h_lockin)
        # update plot
        self.ui.dAbsScan.plot_this(self.x, self.y)
        # move to the next frequency, update freq index and average counter
        self.next_freq()
        # if done
        if self.acquired_avg == self.target_avg:
            self.save_data()
            self.batch_time_taken += ceil(len(self.x) * self.target_avg * self.wait_time * 1e-3)
            self._next_batch_entry_signal.emit()
        else:
            # tune syn to the next freq
            self.tune_syn_freq()

    def next_freq(self):
        """ move to the next frequency point """

        # current sweep is even average, decrease index (sweep backward)
        if self.acquired_avg % 2:
            self.pts_taken = (self.acquired_avg+1)*len(self.x) - self.this_x_idx
            if self.this_x_idx > 0:
                self.this_x_idx -= 1
            else:
                self.acquired_avg += 1
                self.update_ysum()
                self.y = np.zeros_like(self.x)
        # current sweep is odd average, increase index (sweep forward)
        else:
            self.pts_taken = self.acquired_avg*len(self.x) + self.this_x_idx
            if self.this_x_idx < len(self.x)-1:
                self.this_x_idx += 1
            else:
                self.acquired_avg += 1
                self.update_ysum()
                self.y = np.zeros_like(self.x)

        # update progress bar
        self.ui.dAbsScan.currentProgBar.setValue(ceil(self.pts_taken * self.wait_time * 1e-3))
        self.ui.dAbsScan.totalProgBar.setValue(
            self.batch_time_taken + ceil(self.pts_taken * self.wait_time * 1e-3))

    def update_ysum(self):
        """ Update sum plot """

        # add current y array to y_sum
        self.y_sum += self.y
        # update plot
        self.ui.dAbsScan.ySumCurve.setData(self.x, self.y_sum)

    def save_data(self):
        """ Save data array """

        # Grab current comment (in case edited during the scan) before saving data
        entry = self.ui.dAbsScan.batchListWidget.entryList[self.this_entry_idx]

        if self.handles.info_syn.modModeIndex == 2:
            mod_amp = self.handles.info_syn.modAmp * 1e-3
        elif self.handles.info_syn.modModeIndex == 1:
            mod_amp = self.handles.info_syn.modAmp
        else:
            mod_amp = 0

        # prepare header
        h_info = (self.handles.info_syn.harm, self.wait_time,
                  _SENS_VAL[self.sens_index],
                  TAU_VAL[self.tc_index]*1e-3,
                  self.handles.info_syn.modFreq * 1e-3, mod_amp,
                  self.handles.info_syn.modModeText,
                  self.handles.info_lockin.refHarm, self.handles.info_lockin.refPhase,
                  self.x_min, self.step, self.acquired_avg,
                  entry.commentFill.text())

        # if already finishes at least one sweep
        if self.acquired_avg > 0:
            lwa.save_lwa(self.filename, self.y_sum / self.acquired_avg, h_info)
        else:
            lwa.save_lwa(self.filename, self.y, h_info)

    def pause_current(self, btn_pressed):
        """ Pause/resume data acquisition """

        if btn_pressed:
            self.ui.dAbsScan.btnPause.setText('Continue')
            self._timer.stop()
        else:
            self.ui.dAbsScan.btnPause.setText('Pause')
            self._timer.start()

    def redo_current(self):
        """ Erase current y array and restart a scan """

        #print('redo current')
        self._timer.stop()
        if self.ui.dAbsScan.btnPause.isChecked():
            self.ui.dAbsScan.btnPause.click()
        else:
            pass

        if self.acquired_avg % 2:   # even sweep, sweep down
            self.this_x_idx = len(self.x) - 1
        else:                       # odd sweep, sweep up
            self.this_x_idx = 0

        self.y = np.zeros_like(self.x)
        self.tune_syn_freq()

    def restart_avg(self):
        """ Erase all current averages and start over """

        q = QtWidgets.QMessageBox.question(
            self, 'Scan In Progress!',
                    'Restart will erase all cached averages.\n Are you sure to proceed?',
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
            QtWidgets.QMessageBox.StandardButton.No)

        if q == QtWidgets.QMessageBox.StandardButton.Yes:
            #print('restart average')
            self._timer.stop()
            self.acquired_avg = 0
            self.this_x_idx = 0
            self.y = np.zeros_like(self.x)
            self.y_sum = np.zeros_like(self.x)
            self.ui.dAbsScan.ySumCurve.setData(self.x, self.y_sum)
            self.tune_syn_freq()
        else:
            pass

    def save_current(self):
        """ Save what's got so far and continue """

        self._timer.stop()
        self.save_data()
        self._timer.start()

    def jump(self):
        """ Jump to next batch item """

        q = QtWidgets.QMessageBox.question(
            self, 'Jump To Next',
            'Save aquired data for the current scan window?',
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No |
            QtWidgets.QMessageBox.StandardButton.Cancel,
            QtWidgets.QMessageBox.StandardButton.Yes)

        if q == QtWidgets.QMessageBox.StandardButton.Yes:
            #print('abort current')
            self._timer.stop()
            self.batch_time_taken += ceil(len(self.x) * self.target_avg * self.wait_time * 1e-3)
            self.save_data()
            self._next_batch_entry_signal.emit()
        elif q == QtWidgets.QMessageBox.StandardButton.No:
            #print('abort current')
            self._timer.stop()
            self.batch_time_taken += ceil(len(self.x) * self.target_avg * self.wait_time * 1e-3)
            self._next_batch_entry_signal.emit()
        else:
            pass

    def _go_to_next_batch_entry(self):

        # the index update must be done first because otherwise
        # there will be no chance to do it after the timer signal is emitted
        self.this_entry_idx += 1
        if self.this_entry_idx < len(self.list_settings):
            self.ui.dAbsScan.batchListWidget.set_active_entry(self.this_entry_idx)

            self._timer.start()
        else:
            self.finish()

    def finish(self):

        self.ui.dAbsScan.currentProgBar.setValue(self.ui.dAbsScan.currentProgBar.maximum())
        self.ui.dAbsScan.totalProgBar.setValue(self.ui.dAbsScan.totalProgBar.maximum())
        self._timer.stop()
        msg = ui_shared.MsgInfo(
            self, 'Job Finished!',
            'Congratulations! Now it is time to grab some coffee.')
        msg.exec()

    def abort_scan(self):

        q = QtWidgets.QMessageBox.question(
            self, 'Scan In Progress!',
            'The batch scan is still in progress. '
            'Aborting the project will discard all unsaved data! \n Are you SURE to proceed?',
            QtWidgets.QMessageBox.StandardButton.Yes |
            QtWidgets.QMessageBox.StandardButton.No,
            QtWidgets.QMessageBox.StandardButton.No)

        if q == QtWidgets.QMessageBox.StandardButton.Yes:
            self._timer.stop()
        else:
            pass


class ThreadBatchScan(QtCore.QThread):
    """ Thread for batch scan """

    sig_total_progress = QtCore.pyqtSignal(int)
    sig_this_progress = QtCore.pyqtSignal(int)
    sig_this_n = QtCore.pyqtSignal(int)
    sig_data_ready = QtCore.pyqtSignal(np.ndarray, np.ndarray)
    sig_finish = QtCore.pyqtSignal()
    def __init__(self, prefs: Prefs, handles: Handles, threads: Threads,
                 list_settings: [AbsScanSetting], parent=None):
        super().__init__(parent)

        self.prefs = prefs
        self.handles = handles
        self.threads = threads
        self.list_settings = list_settings

    def run(self):

        for setting in self.list_settings:
            # tune instrument settings
            self._tune_inst(setting)
            x_arr = np.arange(setting.freq_start, setting.freq_stop, setting.freq_step)
            y_arr = np.zeros_like(x_arr)
            # calculate n to set to the current progress bar
            # it is equal to no. of points * no. of averages *
            this_n = len(x_arr) * setting.avg
            self.sig_this_n.emit(this_n)
            for idx, x in enumerate(x_arr):
                # tune synthesizer frequency
                if self.prefs.is_test:
                    self.handles.info_syn.freq_cw = x * 1e6
                else:
                    syn_f = x * 1e6 / self.handles.info_syn.harm
                    self.threads.t_syn.call(self.handles.api_syn.set_syn_freq, self.handles.h_syn, syn_f)
                # sleep in seconds to wait for the previous tau to relax
                sleep(setting.dwell_time * 1e-3)
                y = 0
                if self.prefs.is_test:
                    for i in range(setting.avg):
                        y += np.random.random_sample()
                        self.sig_this_progress.emit(idx * setting.avg + i + 1)
                else:
                    for i in range(setting.avg):
                        y += self.threads.t_lockin.call(self.handles.api_lockin.query_single_x,
                                                        self.handles.h_lockin, setting.buffer_len)
                        self.sig_this_progress.emit(idx * setting.avg + i + 1)
                y_arr[idx] = y / setting.avg
                self.sig_data_ready.emit(x, y)
            # auto save current data
            save_data(np.column_stack((x_arr, y_arr)), setting)
        self.sig_finish.emit()

    def _tune_inst(self, setting: AbsScanSetting):

        self.handles.info_syn.modu_mode_idx = setting.modu_mode_idx
        self.handles.info_syn.modu_freq = setting.modu_freq
        self.handles.info_syn.modu_amp = setting.modu_amp

        if self.handles.info_syn.modu_mode_txt == 'AM':
            self.threads.t_syn.call(self.handles.api_syn.set_am_stat, self.handles.h_syn, 1, True)
            self.threads.t_syn.call(self.handles.api_syn.set_fm_stat, self.handles.h_syn, 1, False)
            self.threads.t_syn.call(self.handles.api_syn.set_modu_stat, self.handles.h_syn, True)
            self.threads.t_syn.call(self.handles.api_syn.set_am_freq, self.handles.h_syn, setting.modu_freq)
            self.threads.t_syn.call(self.handles.api_syn.set_am_depth_pct, self.handles.h_syn, setting.modu_amp)
        elif self.handles.info_syn.modu_mode_txt == 'FM':
            self.threads.t_syn.call(self.handles.api_syn.set_am_stat, self.handles.h_syn, 1, False)
            self.threads.t_syn.call(self.handles.api_syn.set_fm_stat, self.handles.h_syn, 1, True)
            self.threads.t_syn.call(self.handles.api_syn.set_modu_stat, self.handles.h_syn, True)
            self.threads.t_syn.call(self.handles.api_syn.set_fm_freq, self.handles.h_syn, setting.modu_freq)
            self.threads.t_syn.call(self.handles.api_syn.set_fm_dev, self.handles.h_syn, setting.modu_amp)
        else:
            self.threads.t_syn.call(self.handles.api_syn.set_modu_stat, self.handles.h_syn, False)
            self.threads.t_syn.call(self.handles.api_syn.set_am_stat, self.handles.h_syn, 1, False)
            self.threads.t_syn.call(self.handles.api_syn.set_fm_stat, self.handles.h_syn, 1, False)
        self.threads.t_lockin.call(self.handles.api_lockin.set_sens, self.handles.h_lockin, setting.sens_idx)
        self.threads.t_lockin.call(self.handles.api_lockin.set_tau, self.handles.h_lockin, setting.tau_idx)


def estimate_job_time(list_settings: [AbsScanSetting]):
    """ Estimate the time expense of batch scan job """

    if isinstance(list_settings, list):
        pass
    else:
        list_settings = [list_settings]

    total_time = 0
    for setting in list_settings:
        # estimate total data points to be taken
        data_points = ceil((abs(setting.freq_stop - setting.freq_start) / setting.freq_step + 1) * setting.avg)
        # time expense for this entry in seconds, tau & dwell time all in ms
        total_time += data_points * (TAU_VAL[setting.tau_idx] * setting.buffer_len + setting.dwell_time) * 1e-3

    return total_time


def save_data(data: np.ndarray, setting: AbsScanSetting, filename=''):
    """ Save data array to a file """
    if filename:
        pass
    else:
        d = datetime.datetime.today().strftime('%Y%m%d')
        filename = f'{d:s}_{setting.freq_start:0.0f}_{setting.freq_stop:0.0f}_bf{setting.buffer_len:d}.dat'
        # check if this file already exists. if so, add numbering
        i = 0
        while os.path.exists(filename):
            i += 1
            filename = f'{d:s}_{setting.freq_start:0.0f}_{setting.freq_stop:0.0f}_bf{setting.buffer_len:d}_{i:d}.dat'
    np.savetxt(filename, data, comments='')