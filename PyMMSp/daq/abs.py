#! encoding = utf-8

""" Lockin scanning routine in JPL style """


from PyQt6 import QtCore, QtWidgets
import numpy as np
from math import ceil
import datetime
import os

from PyMMSp.ui import ui_shared
from PyMMSp.inst import lockin as api_lia
from PyMMSp.inst import validator as api_val
from PyMMSp.inst import synthesizer as api_syn
from PyMMSp.inst.lockin import MODU_MODE, _SENS_VAL, TAU_VAL
from PyMMSp.libs import lwa

# 3 imports for type hinting
from PyMMSp.config.config import Prefs
from PyMMSp.ui.ui_main import MainUI
from PyMMSp.inst.base import Handles


class CtrlAbsBBScan(QtWidgets.QWidget):
    """ Controller of the absorption broadband scan """

    next_batch_entry_signal = QtCore.pyqtSignal()

    def __init__(self, prefs: Prefs, ui: MainUI, handles: Handles, parent=None):
        super().__init__(parent)

        self.prefs = prefs
        self.ui = ui
        self.handles = handles

        # Initialize ui_shared settings
        # self.multiplier = self.handles.info_syn.vdiBandMultiplication

        # Initialize scan entry settings
        self.start_rf_freq = 0
        self.stop_rf_freq = 0
        self.current_rf_freq = 0
        self.acquired_avg = 0
        self.step = 0
        self.sens_index = 0
        self.wait_time = 60
        self.batch_time_taken = 0
        self.current_x_index = 0
        self.current_entry_index = 0
        self.list_settings = []
        self.x = np.array([])
        self.x_min = 0
        self.target_avg = 0
        self.tc_index = 0
        self.current_comment = ''
        self.y = np.array([])
        self.y_sum = np.array([])
        self.pts_taken = 0

        self.waitTimer = QtCore.QTimer()
        self.waitTimer.setInterval(self.wait_time)
        self.waitTimer.setSingleShot(True)
        self.waitTimer.timeout.connect(self.query_lockin)

        # connect quick scan button signals
        self.ui.dAbsScan.btnPause.clicked[bool].connect(self.pause_current)
        self.ui.dAbsScan.btnStart.clicked[bool].connect(self.quick_scan_start)
        self.ui.dAbsScan.btnAbort.clicked[bool].connect(self.abort_scan)

        # connect batch scan button signals
        self.ui.dAbsScan.btnBatchSetup.clicked[bool].connect(self.ui.dAbsConfig.exec)
        self.ui.dAbsConfig.accepted.connect(self.on_setup_accepted)
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
        self.list_settings = [item.get_setting() for item in self.ui.dAbsConfig.ListSetupItem]
        self.ui.dAbsScan.batchListWidget.add_entries(self.list_settings)

    def open_data_folder(self):
        directory = self.ui.dAbsConfig.lblDir.text()
        os.startfile(directory)

    def quick_scan_start(self):
        """ Start a quick scan. It is equivalent to put a single item into the batch job queue and then start it. """
        # get settings from quick scan setup
        scan_setting = self.ui.dAbsScan.get_quick_scan_settings()
        # write this to the batch job queue
        self.ui.dAbsConfig.add_setting_list([scan_setting, ])
        self.ui.dAbsScan.batchListWidget.add_entries(self.list_settings)

    def batch_start(self):
        """ Start a batch scan """
        # Initiate progress bar
        total_time = ceil(ui_shared.jpl_scan_time(self.list_settings))
        self.ui.dAbsScan.totalProgBar.setRange(0, total_time)
        self.ui.dAbsScan.totalProgBar.setValue(0)
        self.batch_time_taken = 0
        # Start scan
        self.next_batch_entry_signal.connect(self.scan_batch_entry)
        # this makes sure batch starts at index 0
        self.current_entry_index = -1
        self.next_batch_entry_signal.emit()

    def _estimate_time(self, list_scan_settings):
        if list_scan_settings:
            total_time = ui_shared.jpl_scan_time(list_scan_settings)
            now = datetime.datetime.today()
            length = datetime.timedelta(seconds=total_time)
            then = now + length
            text = 'This batch job is estimated to take {:s}.\nIt is expected to finish at {:s}.'.format(
                str(length), then.strftime('%I:%M %p, %m-%d-%Y (%a)'))
            q = ui_shared.MsgInfo(self, 'Time Estimation', text)
            q.addButton(QtWidgets.QMessageBox.StandardButton.Cancel)
            qres = q.exec()
            if qres == QtWidgets.QMessageBox.StandardButton.Ok:
                dconfig_result = True
            else:
                dconfig_result = self.ui.dAbsConfig.exec()
        else:
            dconfig_result = self.ui.dAbsConfig.exec()

    def set_file_directory(self):

        self.filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, 'Save Data', '', 'SMAP File (*.lwa)')
        self.ui.dAbsScan.lblDir.setText('Data save to: {:s}'.format(self.filename))

    def get_settings(self):
        """ Read batch settings from entries and proceed.
            Returns a list of seting tuples in the format of
            (comment, start_freq <MHz>, stop_freq <MHz>, step <MHz>,
             averages [int], sens_index [int], timeConst [int],
             wait_time <ms>, mod Mode index [int], mod freq <Hz>, mod Amp [float], harmonics [int], phase [float])
        """

        entry_settings = []
        no_error = True

        if self.filename == '':
            no_error = False
        else:
            # get settings from entry
            for entry in self.ui.dAbsScan.ListSetupItem:
                # if all validation status in this entry are True
                if not list(entry.status.values()).count(False):
                    no_error *= True
                    # read settings
                    entry_setting = (entry.commentFill.text(),
                                     entry.startFreq, entry.stopFreq, entry.step,
                                     entry.avg, entry.comboSens.currentIndex(),
                                     entry.comboTau.currentIndex(), entry.wait_time,
                                     entry.modModeSel.currentIndex(),
                                     entry.modFreq, entry.modAmp, entry.refHarm,
                                     entry.refPhase)
                    # put the setting tuple into a list
                    entry_settings.append(entry_setting)
                else:
                    no_error *= False
        if no_error:
            return entry_settings, self.filename
        else:
            msg = ui_shared.MsgError(self, 'Invalid input!', 'Please fix invalid inputs before proceeding.')
            msg.exec()
            return None, None

    def update_setting(self, entry_setting):
        """ Update scan entry setting. Starts a scan after setting update.
            entry = (comment, start_freq <MHz>, stop_freq <MHz>, step <MHz>,
             averages [int], sens_index [int], timeConst [int],
             wait_time <ms>, mod Mode index [int], mod freq <Hz>, mod Amp [float], harmonics [int], phase [float])
        """

        self.x = ui_shared.gen_x_array(*entry_setting[1:4])
        self.x_min = min(entry_setting[1], entry_setting[2])
        self.step = entry_setting[3]
        self.current_x_index = 0
        self.target_avg = entry_setting[4]
        self.acquired_avg = 0
        self.sens_index = entry_setting[5]
        self.tc_index = entry_setting[6]
        self.wait_time = entry_setting[7]
        self.waitTimer.setInterval(self.wait_time)
        self.current_comment = entry_setting[0]
        self.y = np.zeros_like(self.x)
        self.y_sum = np.zeros_like(self.x)
        self.ui.dAbsScan.ySumCurve.setData(self.x, self.y_sum)
        total_pts =  len(self.x) * self.target_avg
        self.pts_taken = 0
        self.ui.dAbsScan.currentProgBar.setRange(0, ceil(total_pts * self.wait_time * 1e-3))
        self.ui.dAbsScan.currentProgBar.setValue(ceil(self.pts_taken * self.wait_time * 1e-3))

        # tune instrument
        self.tune_inst(entry_setting)

        # refresh [inst]Status Panels
        # self.main.synStatus.print_info()
        # self.main.liaStatus.print_info()

        # start daq timer
        self.waitTimer.start()

    def tune_inst(self, entry_setting):
        """ Tune instrument """

        self.handles.info_syn.modModeIndex = entry_setting[8]
        self.handles.info_syn.modModeText = MODU_MODE[entry_setting[8]]
        self.handles.info_syn.modFreq = entry_setting[9]
        self.handles.info_syn.modAmp = entry_setting[10]

        if self.prefs.is_test:
            self.handles.info_syn.probFreq = self.x[self.current_x_index] * 1e6
            self.handles.info_syn.synFreq = self.handles.info_syn.probFreq/self.handles.info_syn.harm
            if self.handles.info_syn.modModeIndex == 1:
                self.handles.info_syn.modToggle = True
                self.handles.info_syn.AM1Freq = entry_setting[9]
                self.handles.info_syn.AM1DepthPercent = entry_setting[10]
            elif self.handles.info_syn.modModeIndex == 1:
                self.handles.info_syn.modToggle = True
                self.handles.info_syn.FM1Freq = entry_setting[9]
                self.handles.info_syn.FM1Dev = entry_setting[10]
            else:
                self.handles.info_syn.modToggle = False
            self.handles.info_lockin.sensIndex = self.sens_index
            self.handles.info_lockin.sensText = _SENS_VAL[self.sens_index]
            self.handles.info_lockin.tcIndex = self.tc_index
            self.handles.info_lockin.tcText = TAU_VAL[self.tc_index]
            self.handles.info_lockin.refHarm = entry_setting[11]
            self.handles.info_lockin.refHarmText = str(entry_setting[11])
            self.handles.info_lockin.refPhase = entry_setting[12]
        else:
            api_syn.set_syn_freq(self.handles.h_syn, self.x[self.current_x_index] / self.handles.info_syn.harm)
            api_syn.set_mod_mode(self.handles.h_syn, entry_setting[8])
            if self.handles.info_syn.modModeIndex == 1:
                api_syn.set_am(self.handles.h_syn, entry_setting[9], entry_setting[10], True)
            elif self.handles.info_syn.modModeIndex == 2:
                api_syn.set_fm(self.handles.h_syn, entry_setting[9], entry_setting[10], True)
            else:
                pass
            api_lia.set_sens(self.handles.h_lockin, self.sens_index)
            api_lia.set_tc(self.handles.h_lockin, self.tc_index)
            api_lia.set_harm(self.handles.h_lockin, entry_setting[11])
            api_lia.set_phase(self.handles.h_lockin, entry_setting[12])

            self.handles.info_syn.full_info_query(self.handles.h_syn)
            self.handles.info_lockin.full_info_query(self.handles.h_lockin)

    def tune_syn_freq(self):
            """ Simply tune synthesizer frequency """

            self.handles.info_syn.probFreq = self.x[self.current_x_index] * 1e6
            self.handles.info_syn.synFreq = self.handles.info_syn.probFreq / self.handles.info_syn.harm
            #self.main.synStatus.print_info()

            if self.prefs.is_test:
                pass
            else:
                api_syn.set_syn_freq(self.handles.h_syn, self.handles.info_syn.synFreq)

            self.waitTimer.start()

    def query_lockin(self):
        """ Query lockin data. Triggered by waitTimer.timeout() """

        # append data to data list
        if self.prefs.is_test:
            self.y[self.current_x_index] = np.random.random_sample()
        else:
            self.y[self.current_x_index] = self.handles.api_lockin.query_single_x(self.handles.h_lockin)
        # update plot
        self.ui.dAbsScan.yCurve.setData(self.x, self.y)
        # move to the next frequency, update freq index and average counter
        self.next_freq()
        # if done
        if self.acquired_avg == self.target_avg:
            self.save_data()
            self.batch_time_taken += ceil(len(self.x) * self.target_avg * self.wait_time * 1e-3)
            self.next_batch_entry_signal.emit()
        else:
            # tune syn to the next freq
            self.tune_syn_freq()

    def next_freq(self):
        """ move to the next frequency point """

        # current sweep is even average, decrease index (sweep backward)
        if self.acquired_avg % 2:
            self.pts_taken = (self.acquired_avg+1)*len(self.x) - self.current_x_index
            if self.current_x_index > 0:
                self.current_x_index -= 1
            else:
                self.acquired_avg += 1
                self.update_ysum()
                self.y = np.zeros_like(self.x)
        # current sweep is odd average, increase index (sweep forward)
        else:
            self.pts_taken = self.acquired_avg*len(self.x) + self.current_x_index
            if self.current_x_index < len(self.x)-1:
                self.current_x_index += 1
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
        entry = self.ui.dAbsScan.batchListWidget.entryList[self.current_entry_index]

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
            self.waitTimer.stop()
        else:
            self.ui.dAbsScan.btnPause.setText('Pause')
            self.waitTimer.start()

    def redo_current(self):
        """ Erase current y array and restart a scan """

        #print('redo current')
        self.waitTimer.stop()
        if self.ui.dAbsScan.btnPause.isChecked():
            self.ui.dAbsScan.btnPause.click()
        else:
            pass

        if self.acquired_avg % 2:   # even sweep, sweep down
            self.current_x_index = len(self.x) - 1
        else:                       # odd sweep, sweep up
            self.current_x_index = 0

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
            self.waitTimer.stop()
            self.acquired_avg = 0
            self.current_x_index = 0
            self.y = np.zeros_like(self.x)
            self.y_sum = np.zeros_like(self.x)
            self.ui.dAbsScan.ySumCurve.setData(self.x, self.y_sum)
            self.tune_syn_freq()
        else:
            pass

    def save_current(self):
        """ Save what's got so far and continue """

        self.waitTimer.stop()
        self.save_data()
        self.waitTimer.start()

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
            self.waitTimer.stop()
            self.batch_time_taken += ceil(len(self.x) * self.target_avg * self.wait_time * 1e-3)
            self.save_data()
            self.next_batch_entry_signal.emit()
        elif q == QtWidgets.QMessageBox.StandardButton.No:
            #print('abort current')
            self.waitTimer.stop()
            self.batch_time_taken += ceil(len(self.x) * self.target_avg * self.wait_time * 1e-3)
            self.next_batch_entry_signal.emit()
        else:
            pass

    def scan_batch_entry(self):

        self.current_entry_index += 1
        if self.current_entry_index < len(self.list_settings):
            self.ui.dAbsScan.batchListWidget.set_active_entry(self.current_entry_index)
            self.waitTimer.start()
        else:
            self.finish()

    def finish(self):

        self.ui.dAbsScan.currentProgBar.setValue(self.ui.dAbsScan.currentProgBar.maximum())
        self.ui.dAbsScan.totalProgBar.setValue(self.ui.dAbsScan.totalProgBar.maximum())

        msg = ui_shared.MsgInfo(
            self, 'Job Finished!','Congratulations! Now it is time to grab some coffee.')
        msg.exec()
        self.waitTimer.stop()
        self.ui.dAbsScan.accept()

    def abort_scan(self):

        q = QtWidgets.QMessageBox.question(
            self, 'Scan In Progress!',
            'The batch scan is still in progress. '
            'Aborting the project will discard all unsaved data! \n Are you SURE to proceed?',
            QtWidgets.QMessageBox.StandardButton.Yes |
            QtWidgets.QMessageBox.StandardButton.No,
            QtWidgets.QMessageBox.StandardButton.No)

        if q == QtWidgets.QMessageBox.StandardButton.Yes:
            self.waitTimer.stop()
        else:
            pass
