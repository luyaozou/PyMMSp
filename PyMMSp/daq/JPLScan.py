#! encoding = utf-8

""" Lockin scanning routine in JPL style """


from PyQt6 import QtCore, QtWidgets
import numpy as np
from math import ceil
import pyqtgraph as pg

from PyMMSp.ui import ui_shared
from PyMMSp.inst import lockin as api_lia
from PyMMSp.inst import validator as api_val
from PyMMSp.inst import synthesizer as api_syn
from PyMMSp.libs import lwa


class JPLScanConfig(QtWidgets.QDialog):
    """
        Configuration window preparing for the scan
    """

    def __init__(self, parent=None):
        super().__init__(self, parent)
        self.setWindowTitle('Lockin scan configuration (JPL style)')
        self.setMinimumSize(1200, 600)

        # Add top buttons
        addBatchButton = QtWidgets.QPushButton('Add batch')
        removeBatchButton = QtWidgets.QPushButton('Remove last batch')
        saveButton = QtWidgets.QPushButton('Set File Directory')
        self.filename = 'default.lwa'
        self.fileLabel = QtWidgets.QLabel('Save Data to: {:s}'.format(self.filename))
        self.fileLabel.setStyleSheet('QLabel {color: #003366}')
        topButtonLayout = QtWidgets.QGridLayout()
        topButtonLayout.addWidget(saveButton, 0, 0)
        topButtonLayout.addWidget(addBatchButton, 0, 1)
        topButtonLayout.addWidget(removeBatchButton, 0, 2)
        topButtonLayout.addWidget(self.fileLabel, 1, 0, 1, 3)
        topButtons = QtWidgets.QWidget()
        topButtons.setLayout(topButtonLayout)

        # Add bottom buttons
        cancelButton = QtWidgets.QPushButton(ui_shared.btn_label('reject'))
        acceptButton = QtWidgets.QPushButton(ui_shared.btn_label('confirm'))
        acceptButton.setDefault(True)
        bottomButtonLayout = QtWidgets.QHBoxLayout()
        bottomButtonLayout.addWidget(cancelButton)
        bottomButtonLayout.addWidget(acceptButton)
        bottomButtons = QtWidgets.QWidget()
        bottomButtons.setLayout(bottomButtonLayout)

        # Add freq config entries
        self.entryWidgetList = []
        self.entryLayout = QtWidgets.QGridLayout()
        self.entryLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        # add entries
        self.entryLayout.addWidget(QtWidgets.QLabel('Comment'), 0, 0)
        self.entryLayout.addWidget(QtWidgets.QLabel('Start Freq (MHz)'), 0, 1)
        self.entryLayout.addWidget(QtWidgets.QLabel('Stop Freq (MHz)'), 0, 2)
        self.entryLayout.addWidget(QtWidgets.QLabel('Step (MHz)'), 0, 3)
        self.entryLayout.addWidget(QtWidgets.QLabel('Averages'), 0, 4)
        self.entryLayout.addWidget(QtWidgets.QLabel('Sensitivity'), 0, 5)
        self.entryLayout.addWidget(QtWidgets.QLabel('Time Const'), 0, 6)
        self.entryLayout.addWidget(QtWidgets.QLabel('Wait time (ms)'), 0, 7)
        self.entryLayout.addWidget(QtWidgets.QLabel('Modulation'), 0, 8)
        self.entryLayout.addWidget(QtWidgets.QLabel('Mod Freq (Hz)'), 0, 9)
        self.entryLayout.addWidget(QtWidgets.QLabel('Mod Depth/Dev'), 0, 10, 1, 2)
        self.entryLayout.addWidget(QtWidgets.QLabel('Harmonics'), 0, 12)
        self.entryLayout.addWidget(QtWidgets.QLabel('Phase'), 0, 13)

        self.add_entry()

        entryWidgets = QtWidgets.QWidget()
        entryWidgets.setLayout(self.entryLayout)

        entryArea = QtWidgets.QScrollArea()
        entryArea.setWidgetResizable(True)
        entryArea.setWidget(entryWidgets)

        # Set up main layout
        mainLayout = QtWidgets.QVBoxLayout(self)
        mainLayout.setSpacing(0)
        mainLayout.addWidget(topButtons)
        mainLayout.addWidget(entryArea)
        mainLayout.addWidget(bottomButtons)
        self.setLayout(mainLayout)

        cancelButton.clicked.connect(self.reject)
        acceptButton.clicked.connect(self.accept)
        saveButton.clicked.connect(self.set_file_directory)
        addBatchButton.clicked.connect(self.add_entry)
        removeBatchButton.clicked.connect(self.remove_entry)

    def add_entry(self):
        """ Add batch entry to this dialog window """

        # generate a new batch entry
        default_setting = ('default', self.main.synInfo.probFreq*1e-6,
                            self.main.synInfo.probFreq*1e-6+10.000, 0.1, 1,
                            self.main.liaInfo.sensIndex,
                            self.main.liaInfo.tcIndex, 60,
                            self.main.synInfo.modModeIndex,
                            self.main.synInfo.modFreq,
                            self.main.synInfo.modAmp,
                            self.main.liaInfo.refHarm,
                            self.main.liaInfo.refPhase)
        entry = ui_shared.JPLLIAScanEntry(self.main, default=default_setting)

        # get the current last entry
        if self.entryWidgetList:
            last_entry = self.entryWidgetList[-1]
            # set default values to be the same as the last one
            entry.commentFill.setText(last_entry.commentFill.text())
            entry.startFreqFill.setText(last_entry.startFreqFill.text())
            entry.stopFreqFill.setText(last_entry.stopFreqFill.text())
            entry.stepFill.setText(last_entry.stepFill.text())
            entry.avgFill.setText(last_entry.avgFill.text())
            entry.sensSel.setCurrentIndex(last_entry.sensSel.currentIndex())
            entry.tauSel.setCurrentIndex(last_entry.tauSel.currentIndex())
            entry.waitTimeFill.setText(last_entry.waitTimeFill.text())
            entry.modModeSel.setCurrentIndex(last_entry.modModeSel.currentIndex())
            entry.modFreqFill.setText(last_entry.modFreqFill.text())
            entry.modAmpFill.setText(last_entry.modAmpFill.text())
            entry.harmSel.setCurrentIndex(last_entry.harmSel.currentIndex())
            entry.refPhaseFill.setText(last_entry.refPhaseFill.text())
        else:
            pass
        # add this entry to the layout and to the entry list
        self.entryWidgetList.append(entry)
        row = len(self.entryWidgetList)
        self.entryLayout.addWidget(entry.commentFill, row, 0)
        self.entryLayout.addWidget(entry.startFreqFill, row, 1)
        self.entryLayout.addWidget(entry.stopFreqFill, row, 2)
        self.entryLayout.addWidget(entry.stepFill, row, 3)
        self.entryLayout.addWidget(entry.avgFill, row, 4)
        self.entryLayout.addWidget(entry.sensSel, row, 5)
        self.entryLayout.addWidget(entry.tauSel, row, 6)
        self.entryLayout.addWidget(entry.waitTimeFill, row, 7)
        self.entryLayout.addWidget(entry.modModeSel, row, 8)
        self.entryLayout.addWidget(entry.modFreqFill, row, 9)
        self.entryLayout.addWidget(entry.modAmpFill, row, 10)
        self.entryLayout.addWidget(entry.modAmpUnitLabel, row, 11)
        self.entryLayout.addWidget(entry.harmSel, row, 12)
        self.entryLayout.addWidget(entry.refPhaseFill, row, 13)

    def remove_entry(self):
        """ Remove last batch entry in this dialog window """

        # if there is only one entry, skip and pop up warning
        if len(self.entryWidgetList) == 1:
            msg = ui_shared.MsgWarning(self.main, 'Cannot remove batch!',
                             'At least one batch entry is required!')
            msg.exec()
        else:
            # remove this entry
            entry = self.entryWidgetList.pop()
            self.entryLayout.removeWidget(entry.commentFill)
            entry.commentFill.deleteLater()
            self.entryLayout.removeWidget(entry.startFreqFill)
            entry.startFreqFill.deleteLater()
            self.entryLayout.removeWidget(entry.stopFreqFill)
            entry.stopFreqFill.deleteLater()
            self.entryLayout.removeWidget(entry.stepFill)
            entry.stepFill.deleteLater()
            self.entryLayout.removeWidget(entry.avgFill)
            entry.avgFill.deleteLater()
            self.entryLayout.removeWidget(entry.sensSel)
            entry.sensSel.deleteLater()
            self.entryLayout.removeWidget(entry.tauSel)
            entry.tauSel.deleteLater()
            self.entryLayout.removeWidget(entry.waitTimeFill)
            entry.waitTimeFill.deleteLater()
            self.entryLayout.removeWidget(entry.modModeSel)
            entry.modModeSel.deleteLater()
            self.entryLayout.removeWidget(entry.modFreqFill)
            entry.modFreqFill.deleteLater()
            self.entryLayout.removeWidget(entry.modAmpFill)
            entry.modAmpFill.deleteLater()
            self.entryLayout.removeWidget(entry.modAmpUnitLabel)
            entry.modAmpUnitLabel.deleteLater()
            self.entryLayout.removeWidget(entry.harmSel)
            entry.harmSel.deleteLater()
            self.entryLayout.removeWidget(entry.refPhaseFill)
            entry.refPhaseFill.deleteLater()
            entry.deleteLater()

    def set_file_directory(self):

        self.filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'Save Data', '', 'SMAP File (*.lwa)')
        self.fileLabel.setText('Data save to: {:s}'.format(self.filename))

    def get_settings(self):
        """ Read batch settings from entries and proceed.
            Returns a list of seting tuples in the format of
            (comment, start_freq <MHz>, stop_freq <MHz>, step <MHz>,
             averages [int], sens_index [int], timeConst [int],
             wait_time <ms>, mod Mode index [int], mod freq <Hz>, mod Amp [float], harmonics [int], phase [float])
        """

        vdi_index = self.main.synPanel.bandSel.currentIndex()

        entry_settings = []
        no_error = True

        if self.filename == '':
            no_error = False
        else:
            # get settings from entry
            for entry in self.entryWidgetList:
                # if all validation status in this entry are True
                if (not list(entry.status.values()).count(False)):
                    no_error *= True
                    # read settings
                    entry_setting = (entry.commentFill.text(),
                                     entry.startFreq, entry.stopFreq, entry.step,
                                     entry.avg, entry.sensSel.currentIndex(),
                                     entry.tauSel.currentIndex(), entry.wait_time,
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
            msg = ui_shared.MsgError(self.main, 'Invalid input!', 'Please fix invalid inputs before proceeding.')
            msg.exec()
            return None, None


class JPLScanWindow(QtWidgets.QDialog):
    """ Scanning window """

    # define a pyqt signal to control batch scans
    next_entry_signal = QtCore.pyqtSignal()

    def __init__(self, entry_settings, filename, main=None):
        QtWidgets.QWidget.__init__(self, main)
        self.main = main
        self.setWindowTitle('Lockin scan monitor')
        self.setMinimumSize(1200, 600)
        self.entry_settings = entry_settings

        # set up batch list display
        self.batchListWidget = JPLBatchListWidget(entry_settings)
        batchArea = QtWidgets.QScrollArea()
        batchArea.setWidgetResizable(True)
        batchArea.setWidget(self.batchListWidget)

        batchDisplay = QtWidgets.QGroupBox()
        batchDisplay.setTitle('Batch List')
        batchLayout = QtWidgets.QVBoxLayout()
        batchLayout.addWidget(batchArea)
        batchDisplay.setLayout(batchLayout)

        # set up single scan monitor + daq class
        self.singleScan = SingleScan(filename, parent=self, main=self.main)

        # set up progress bar
        self.currentProgBar = QtWidgets.QProgressBar()
        self.totalProgBar = QtWidgets.QProgressBar()

        progressDisplay = QtWidgets.QWidget()
        progressLayout = QtWidgets.QGridLayout()
        progressLayout.addWidget(QtWidgets.QLabel('Current Progress'), 0, 0)
        progressLayout.addWidget(self.currentProgBar, 0, 1)
        progressLayout.addWidget(QtWidgets.QLabel('Total progress'), 1, 0)
        progressLayout.addWidget(self.totalProgBar, 1, 1)
        progressDisplay.setLayout(progressLayout)

        mainLayout = QtWidgets.QGridLayout()
        mainLayout.addWidget(batchDisplay, 0, 0, 1, 2)
        mainLayout.addWidget(self.singleScan, 0, 2, 1, 3)
        mainLayout.addWidget(progressDisplay, 1, 0, 1, 5)
        self.setLayout(mainLayout)

        # Initiate progress bar
        total_time = ceil(ui_shared.jpl_scan_time(entry_settings))
        self.totalProgBar.setRange(0, total_time)
        self.totalProgBar.setValue(0)
        self.batch_time_taken = 0

        # Start scan
        self.next_entry_signal.connect(self.next_entry)
        # this makes sure batch starts at index 0
        self.current_entry_index = -1
        self.next_entry_signal.emit()

    def next_entry(self):

        self.current_entry_index += 1
        if self.current_entry_index < len(self.entry_settings):
            if self.current_entry_index:    # more than one entry
                prev_entry = self.batchListWidget.entryList[self.current_entry_index - 1]
                # make previous entry color grey and comment box read only
                prev_entry.set_color_grey()
                prev_entry.commentFill.setReadOnly(True)
                prev_entry.commentFill.setStyleSheet('color: grey')
            else:
                pass    # it's the first entry, no prev_entry
            current_entry = self.batchListWidget.entryList[self.current_entry_index]
            current_entry.set_color_black()
            self.singleScan.update_setting(self.entry_settings[self.current_entry_index])
        else:
            self.finish()

    def stop_timers(self):

        # stop timers
        self.singleScan.waitTimer.stop()

    def finish(self):

        self.currentProgBar.setValue(self.currentProgBar.maximum())
        self.totalProgBar.setValue(self.totalProgBar.maximum())

        msg = ui_shared.MsgInfo(self, 'Job Finished!',
                             'Congratulations! Now it is time to grab some coffee.')
        msg.exec()
        self.stop_timers()
        self.accept()

    def reject(self):

        q = QtWidgets.QMessageBox.question(self, 'Scan In Progress!',
                       'The batch scan is still in progress. Aborting the project will discard all unsaved data! \n Are you SURE to proceed?', QtWidgets.QMessageBox.Yes |
                       QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)

        if q == QtWidgets.QMessageBox.Yes:
            self.stop_timers()
            self.accept()
        else:
            pass


class JPLBatchListWidget(QtWidgets.QWidget):
    """ Batch list display """

    def __init__(self, entry_settings):

        QtWidgets.QWidget.__init__(self)

        self.batchLayout = QtWidgets.QGridLayout()
        self.batchLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        # set up batch list row header
        # put comment in the first column and make it editable
        self.batchLayout.addWidget(QtWidgets.QLabel('#'), 0, 0)
        self.batchLayout.addWidget(QtWidgets.QLabel('Comment'), 0, 1)
        self.batchLayout.addWidget(QtWidgets.QLabel('Start'), 0, 2)
        self.batchLayout.addWidget(QtWidgets.QLabel('Stop'), 0, 3)
        self.batchLayout.addWidget(QtWidgets.QLabel('Step'), 0, 4)
        self.batchLayout.addWidget(QtWidgets.QLabel('Avg'), 0, 5)
        self.batchLayout.addWidget(QtWidgets.QLabel('Sens'), 0, 6)
        self.batchLayout.addWidget(QtWidgets.QLabel('Time'), 0, 7)
        self.batchLayout.addWidget(QtWidgets.QLabel('Const'), 1, 7)
        self.batchLayout.addWidget(QtWidgets.QLabel('Modulation'), 0, 8)
        self.batchLayout.addWidget(QtWidgets.QLabel('Harmonics'), 0, 9)
        self.batchLayout.addWidget(QtWidgets.QLabel('(MHz)'), 1, 2)
        self.batchLayout.addWidget(QtWidgets.QLabel('(MHz)'), 1, 3)
        self.batchLayout.addWidget(QtWidgets.QLabel('(MHz)'), 1, 4)

        # add batch list entry
        self.entryList = []
        for row in range(len(entry_settings)):
            # entry = (start, stop, step, avg, sens_idx, tc_idx, wait_time, comment)
            current_setting = entry_settings[row]
            entry = ui_shared.JPLLIABatchListEntry(self, entry_setting=current_setting)
            # set up the batch number (row + 1)
            entry.numberLabel.setText(str(row+1))
            # add widgets to the dispaly panel layout
            self.batchLayout.addWidget(entry.numberLabel, row+2, 0)
            self.batchLayout.addWidget(entry.commentFill, row+2, 1)
            self.batchLayout.addWidget(entry.startFreqLabel, row+2, 2)
            self.batchLayout.addWidget(entry.stopFreqLabel, row+2, 3)
            self.batchLayout.addWidget(entry.stepLabel, row+2, 4)
            self.batchLayout.addWidget(entry.avgLabel, row+2, 5)
            self.batchLayout.addWidget(entry.sensLabel, row+2, 6)
            self.batchLayout.addWidget(entry.tcLabel, row+2, 7)
            self.batchLayout.addWidget(entry.modModeLabel, row+2, 8)
            self.batchLayout.addWidget(entry.refHarmLabel, row+2, 9)
            self.entryList.append(entry)

        self.setLayout(self.batchLayout)


class SingleScan(QtWidgets.QWidget):
    """ Take a scan in a single freq window """

    def __init__(self, filename, parent=None, main=None):
        """ parent is the JPL scan dialog window. It contains ui_shared settings.
            main is the main GUI window. It containts instrument handles
        """
        QtWidgets.QWidget.__init__(self, parent)
        self.main = main
        self.parent = parent
        self.filename = filename

        # Initialize ui_shared settings
        self.multiplier = self.main.synInfo.vdiBandMultiplication

        # Initialize scan entry settings
        self.start_rf_freq = 0
        self.stop_rf_freq = 0
        self.current_rf_freq = 0
        self.acquired_avg = 0
        self.step = 0
        self.sens_index = 0
        self.wait_time = 60

        self.waitTimer = QtCore.QTimer()
        self.waitTimer.setInterval(self.wait_time)
        self.waitTimer.setSingleShot(True)
        self.waitTimer.timeout.connect(self.query_lockin)

        # set up main layout
        buttons = QtWidgets.QWidget()
        jumpButton = QtWidgets.QPushButton('Jump to Next Batch')
        abortAllButton = QtWidgets.QPushButton('Abort Batch Project')
        self.pauseButton = QtWidgets.QPushButton('Pause')
        self.pauseButton.setCheckable(True)
        redoButton = QtWidgets.QPushButton('Redo Current Sweep')
        restartWinButton = QtWidgets.QPushButton('Restart Current Batch')
        saveButton = QtWidgets.QPushButton('Save and Continue')
        buttonLayout = QtWidgets.QGridLayout()
        buttonLayout.addWidget(self.pauseButton, 0, 0)
        buttonLayout.addWidget(redoButton, 0, 1)
        buttonLayout.addWidget(restartWinButton, 0, 2)
        buttonLayout.addWidget(saveButton, 1, 0)
        buttonLayout.addWidget(jumpButton, 1, 1)
        buttonLayout.addWidget(abortAllButton, 1, 2)
        buttons.setLayout(buttonLayout)

        pgWin = pg.GraphicsWindow(title='Live Monitor')
        self.yPlot = pgWin.addPlot(1, 0, title='Current sweep')
        self.yPlot.setLabel('left', text='Intensity', units='V')
        self.yPlot.setLabel('bottom', text='Frequency (MHz)')
        self.ySumPlot = pgWin.addPlot(0, 0, title='Sum sweep')
        self.ySumPlot.setLabel('left', text='Intensity', units='V')
        self.yCurve = self.yPlot.plot()
        self.yCurve.setDownsampling(auto=True, method='peak')
        self.yCurve.setPen(pg.mkPen(220, 220, 220))
        self.ySumCurve = self.ySumPlot.plot()
        self.ySumCurve.setDownsampling(auto=True, method='peak')
        self.ySumCurve.setPen(pg.mkPen(219, 112, 147))
        self.ySumPlot.setXLink(self.yPlot)
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(pgWin)
        mainLayout.addWidget(buttons)
        self.setLayout(mainLayout)

        self.pauseButton.clicked.connect(self.pause_current)
        redoButton.clicked.connect(self.redo_current)
        restartWinButton.clicked.connect(self.restart_avg)
        saveButton.clicked.connect(self.save_current)
        jumpButton.clicked.connect(self.jump)
        abortAllButton.clicked.connect(self.abort_all)


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
        self.ySumCurve.setData(self.x, self.y_sum)
        total_pts =  len(self.x) * self.target_avg
        self.pts_taken = 0
        self.parent.currentProgBar.setRange(0, ceil(total_pts * self.wait_time * 1e-3))
        self.parent.currentProgBar.setValue(ceil(self.pts_taken * self.wait_time * 1e-3))

        # tune instrument
        self.tune_inst(entry_setting)

        # refresh [inst]Status Panels
        self.main.synStatus.print_info()
        self.main.liaStatus.print_info()

        # start daq timer
        self.waitTimer.start()

    def tune_inst(self, entry_setting):
        """ Tune instrument """

        self.main.synInfo.modModeIndex = entry_setting[8]
        self.main.synInfo.modModeText = api_syn.MOD_MODE_LIST[entry_setting[8]]
        self.main.synInfo.modFreq = entry_setting[9]
        self.main.synInfo.modAmp = entry_setting[10]

        if self.main.testModeAction.isChecked():
            self.main.synInfo.probFreq = self.x[self.current_x_index] * 1e6
            self.main.synInfo.synFreq = self.main.synInfo.probFreq/self.multiplier
            if self.main.synInfo.modModeIndex == 1:
                self.main.synInfo.modToggle = True
                self.main.synInfo.AM1Freq = entry_setting[9]
                self.main.synInfo.AM1DepthPercent = entry_setting[10]
            elif self.main.synInfo.modModeIndex == 1:
                self.main.synInfo.modToggle = True
                self.main.synInfo.FM1Freq = entry_setting[9]
                self.main.synInfo.FM1Dev = entry_setting[10]
            else:
                self.main.synInfo.modToggle = False
            self.main.liaInfo.sensIndex = self.sens_index
            self.main.liaInfo.sensText = api_lia.SENS_LIST[self.sens_index]
            self.main.liaInfo.tcIndex = self.tc_index
            self.main.liaInfo.tcText = api_lia.TC_LIST[self.tc_index]
            self.main.liaInfo.refHarm = entry_setting[11]
            self.main.liaInfo.refHarmText = str(entry_setting[11])
            self.main.liaInfo.refPhase = entry_setting[12]
        else:
            api_syn.set_syn_freq(self.main.syn_handle, self.x[self.current_x_index] / self.multiplier)
            api_syn.set_mod_mode(self.main.syn_handle, entry_setting[8])
            if self.main.synInfo.modModeIndex == 1:
                api_syn.set_am(self.main.syn_handle, entry_setting[9], entry_setting[10], True)
            elif self.main.synInfo.modModeIndex == 2:
                api_syn.set_fm(self.main.syn_handle, entry_setting[9], entry_setting[10], True)
            else:
                pass
            api_lia.set_sens(self.main.lockin_handle, self.sens_index)
            api_lia.set_tc(self.main.lockin_handle, self.tc_index)
            api_lia.set_harm(self.main.lockin_handle, entry_setting[11])
            api_lia.set_phase(self.main.lockin_handle, entry_setting[12])

            self.main.synInfo.full_info_query(self.main.syn_handle)
            self.main.liaInfo.full_info_query(self.main.lockin_handle)

    def tune_syn_freq(self):
            """ Simply tune synthesizer frequency """

            self.main.synInfo.probFreq = self.x[self.current_x_index] * 1e6
            self.main.synInfo.synFreq = self.main.synInfo.probFreq / self.multiplier
            self.main.synStatus.print_info()

            if self.main.testModeAction.isChecked():
                pass
            else:
                api_syn.set_syn_freq(self.main.syn_handle, self.main.synInfo.synFreq)

            self.waitTimer.start()

    def query_lockin(self):
        """ Query lockin data. Triggered by waitTimer.timeout() """

        # append data to data list
        if self.main.testModeAction.isChecked():
            self.y[self.current_x_index] = np.random.random_sample()
        else:
            self.y[self.current_x_index] = api_lia.query_single_x(self.main.lockin_handle)
        # update plot
        self.yCurve.setData(self.x, self.y)
        # move to the next frequency, update freq index and average counter
        self.next_freq()
        # if done
        if self.acquired_avg == self.target_avg:
            self.save_data()
            self.parent.batch_time_taken += ceil(len(self.x) * self.target_avg * self.wait_time * 1e-3)
            self.parent.next_entry_signal.emit()
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
        self.parent.currentProgBar.setValue(ceil(self.pts_taken * self.wait_time * 1e-3))
        self.parent.totalProgBar.setValue(self.parent.batch_time_taken +
                                          ceil(self.pts_taken * self.wait_time * 1e-3))

    def update_ysum(self):
        """ Update sum plot """

        # add current y array to y_sum
        self.y_sum += self.y
        # update plot
        self.ySumCurve.setData(self.x, self.y_sum)

    def save_data(self):
        """ Save data array """

        # Grab current comment (in case edited during the scan) before saving data
        entry = self.parent.batchListWidget.entryList[self.parent.current_entry_index]

        if self.main.synInfo.modModeIndex == 2:
            mod_amp = self.main.synInfo.modAmp * 1e-3
        elif self.main.synInfo.modModeIndex == 1:
            mod_amp = self.main.synInfo.modAmp
        else:
            mod_amp = 0

        # prepare header
        h_info = (self.multiplier, self.wait_time,
                  api_val.LIASENSLIST[self.sens_index],
                  api_val.LIATCLIST[self.tc_index]*1e-3,
                  self.main.synInfo.modFreq * 1e-3, mod_amp,
                  self.main.synInfo.modModeText,
                  self.main.liaInfo.refHarm, self.main.liaInfo.refPhase,
                  self.x_min, self.step, self.acquired_avg,
                  entry.commentFill.text())

        # if already finishes at least one sweep
        if self.acquired_avg > 0:
            PyMMSp.libs.lwa.save_lwa(self.filename, self.y_sum / self.acquired_avg, h_info)
        else:
            PyMMSp.libs.lwa.save_lwa(self.filename, self.y, h_info)

    def pause_current(self, btn_pressed):
        """ Pause/resume data acquisition """

        if btn_pressed:
            self.pauseButton.setText('Resume')
            #print('pause')
            self.waitTimer.stop()
        else:
            self.pauseButton.setText('Pause')
            #print('resume')
            self.waitTimer.start()

    def redo_current(self):
        """ Erase current y array and restart a scan """

        #print('redo current')
        self.waitTimer.stop()
        if self.pauseButton.isChecked():
            self.pauseButton.click()
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

        q = QtWidgets.QMessageBox.question(self, 'Scan In Progress!',
                       'Restart will erase all cached averages.\n Are you sure to proceed?', QtWidgets.QMessageBox.Yes |
                       QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)

        if q == QtWidgets.QMessageBox.Yes:
            #print('restart average')
            self.waitTimer.stop()
            self.acquired_avg = 0
            self.current_x_index = 0
            self.y = np.zeros_like(self.x)
            self.y_sum = np.zeros_like(self.x)
            self.ySumCurve.setData(self.x, self.y_sum)
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

        q = QtWidgets.QMessageBox.question(self, 'Jump To Next',
                       'Save aquired data for the current scan window?', QtWidgets.QMessageBox.Yes |
                       QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Cancel, QtWidgets.QMessageBox.Yes)

        if q == QtWidgets.QMessageBox.Yes:
            #print('abort current')
            self.waitTimer.stop()
            self.parent.batch_time_taken += ceil(len(self.x) * self.target_avg * self.wait_time * 1e-3)
            self.save_data()
            self.parent.next_entry_signal.emit()
        elif q == QtWidgets.QMessageBox.No:
            #print('abort current')
            self.waitTimer.stop()
            self.parent.batch_time_taken += ceil(len(self.x) * self.target_avg * self.wait_time * 1e-3)
            self.parent.next_entry_signal.emit()
        else:
            pass

    def abort_all(self):

        self.parent.reject()
