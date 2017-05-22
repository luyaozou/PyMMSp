#! encoding = utf-8

''' Lockin scanning routine in JPL style '''


from PyQt5 import QtGui, QtCore
import numpy as np
from math import ceil
import pyqtgraph as pg
from gui import SharedWidgets as Shared
from api import general as api_gen
from api import validator as api_val
from api import lockin as api_lia
from api import synthesizer as api_syn
from data import save


class JPLScanConfig(QtGui.QDialog):
    '''
        Configuration window preparing for the scan
    '''

    def __init__(self, main=None):
        QtGui.QDialog.__init__(self, main)
        self.main = main
        self.setWindowTitle('Lockin scan configuration (JPL style)')
        self.setMinimumSize(900, 600)

        # Add top buttons
        addBatchButton = QtGui.QPushButton('Add batch')
        removeBatchButton = QtGui.QPushButton('Remove last batch')
        saveButton = QtGui.QPushButton('Set File Directory')
        self.filename = 'default.lwa'
        self.fileLabel = QtGui.QLabel('Save Data to: {:s}'.format(self.filename))
        self.fileLabel.setStyleSheet('QLabel {color: #003366}')
        topButtonLayout = QtGui.QGridLayout()
        topButtonLayout.addWidget(saveButton, 0, 0)
        topButtonLayout.addWidget(addBatchButton, 0, 1)
        topButtonLayout.addWidget(removeBatchButton, 0, 2)
        topButtonLayout.addWidget(self.fileLabel, 1, 0, 1, 3)
        topButtons = QtGui.QWidget()
        topButtons.setLayout(topButtonLayout)

        # Add bottom buttons
        cancelButton = QtGui.QPushButton(Shared.btn_label('reject'))
        acceptButton = QtGui.QPushButton(Shared.btn_label('confirm'))
        acceptButton.setDefault(True)
        bottomButtonLayout = QtGui.QHBoxLayout()
        bottomButtonLayout.addWidget(cancelButton)
        bottomButtonLayout.addWidget(acceptButton)
        bottomButtons = QtGui.QWidget()
        bottomButtons.setLayout(bottomButtonLayout)

        # Add freq config entries
        self.entryWidgetList = []
        self.entryLayout = QtGui.QGridLayout()
        self.entryLayout.setAlignment(QtCore.Qt.AlignTop)
        # add entries
        self.entryLayout.addWidget(QtGui.QLabel('Start Freq (MHz)'), 0, 0)
        self.entryLayout.addWidget(QtGui.QLabel('Stop Freq (MHz)'), 0, 1)
        self.entryLayout.addWidget(QtGui.QLabel('Step (MHz)'), 0, 2)
        self.entryLayout.addWidget(QtGui.QLabel('Averages'), 0, 3)
        self.entryLayout.addWidget(QtGui.QLabel('Sensitivity'), 0, 4)
        self.entryLayout.addWidget(QtGui.QLabel('Time Constant'), 0, 5)
        self.entryLayout.addWidget(QtGui.QLabel('Wait time (ms)'), 0, 6)
        self.entryLayout.addWidget(QtGui.QLabel('Comment'), 0, 7)

        self.add_entry()

        entryWidgets = QtGui.QWidget()
        entryWidgets.setLayout(self.entryLayout)

        entryArea = QtGui.QScrollArea()
        entryArea.setWidgetResizable(True)
        entryArea.setWidget(entryWidgets)

        # Set up main layout
        mainLayout = QtGui.QVBoxLayout(self)
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
        ''' Add batch entry to this dialog window '''

        # generate a new batch entry
        if self.main.testModeAction.isChecked():
            entry = Shared.JPLLIAScanEntry(self.main, init_setting=(6, 120, 1, 1, 0, 0, 1000, 'default'))
        else:
            entry = Shared.JPLLIAScanEntry(self.main)

        # get the current last entry
        if self.entryWidgetList:
            last_entry = self.entryWidgetList[-1]
            # set default values to be the same as the last one
            entry.stepFill.setText(last_entry.stepFill.text())
            entry.avgFill.setText(last_entry.avgFill.text())
            entry.sensSel.setCurrentIndex(last_entry.sensSel.currentIndex())
            entry.tcSel.setCurrentIndex(last_entry.tcSel.currentIndex())
            entry.waitTimeFill.setText(last_entry.waitTimeFill.text())
            entry.commentFill.setText(last_entry.commentFill.text())
        else:
            pass
        # add this entry to the layout and to the entry list
        self.entryWidgetList.append(entry)
        row = len(self.entryWidgetList)
        self.entryLayout.addWidget(entry.startFreqFill, row, 0)
        self.entryLayout.addWidget(entry.stopFreqFill, row, 1)
        self.entryLayout.addWidget(entry.stepFill, row, 2)
        self.entryLayout.addWidget(entry.avgFill, row, 3)
        self.entryLayout.addWidget(entry.sensSel, row, 4)
        self.entryLayout.addWidget(entry.tcSel, row, 5)
        self.entryLayout.addWidget(entry.waitTimeFill, row, 6)
        self.entryLayout.addWidget(entry.commentFill, row, 7)

    def remove_entry(self):
        ''' Remove last batch entry in this dialog window '''

        # if there is only one entry, skip and pop up warning
        if len(self.entryWidgetList) == 1:
            msg = Shared.MsgWarning(self.main, 'Cannot remove batch!',
                             'At least one batch entry is required!')
            msg.exec_()
        else:
            # remove this entry
            entry = self.entryWidgetList.pop()
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
            self.entryLayout.removeWidget(entry.tcSel)
            entry.tcSel.deleteLater()
            self.entryLayout.removeWidget(entry.waitTimeFill)
            entry.waitTimeFill.deleteLater()
            self.entryLayout.removeWidget(entry.commentFill)
            entry.commentFill.deleteLater()
            entry.deleteLater()

    def set_file_directory(self):

        self.filename, _ = QtGui.QFileDialog.getSaveFileName(self, 'Save Data', '', 'SMAP File (*.lwa)')
        self.fileLabel.setText('Data save to: {:s}'.format(self.filename))

    def get_settings(self):
        ''' Read batch settings from entries and proceed.
            Returns a list of seting tuples in the format of
            (start_freq <MHz>, stop_freq <MHz>, step <MHz>, averages <int>,
             itgtime <ms>, waittime <ms>, lockin sens_index <int>)
        '''

        vdi_index = self.main.synCtrl.bandSel.currentIndex()
        if self.main.testModeAction.isChecked():
            tc_index = self.main.liaInfo.tcIndex
        else:
            tc_index = api_lia.read_tc(self.main.liaHandle)

        entry_settings = []
        no_error = True

        if self.filename == '':
            no_error = False
        else:
            # get settings from entry
            for entry in self.entryWidgetList:
                # read settings
                status1, start_freq = api_val.val_prob_freq(entry.startFreqFill.text(), vdi_index)
                status2, stop_freq = api_val.val_prob_freq(entry.stopFreqFill.text(), vdi_index)
                status3, step = api_val.val_float(entry.stepFill.text())
                status4, average = api_val.val_int(entry.avgFill.text())
                sens_index = entry.sensSel.currentIndex()
                tc_index = entry.tcSel.currentIndex()
                status5, waittime = api_val.val_lia_waittime(entry.waitTimeFill.text(), tc_index)
                comment = entry.commentFill.text()
                # put them into a setting tuple
                if status1 and status2 and status3 and status4 and status5:
                    no_error *= True
                    setting_entry = (start_freq, stop_freq, step, average,
                                     sens_index, tc_index, waittime, comment)
                    # put the setting tuple into a list
                    entry_settings.append(setting_entry)
                else:
                    no_error *= False

        if no_error:
            return entry_settings, self.filename
        else:
            msg = Shared.MsgError(self.main, 'Invalid input!', 'Please fix invalid inputs before proceeding.')
            msg.exec_()
            return None, None


class JPLScanWindow(QtGui.QDialog):
    ''' Scanning window '''

    # define a pyqt signal to control batch scans
    next_entry_signal = QtCore.pyqtSignal()

    def __init__(self, entry_settings, filename, main=None):
        QtGui.QWidget.__init__(self, main)
        self.main = main
        self.setWindowTitle('Lockin scan monitor')
        self.setMinimumSize(800, 600)
        self.entry_settings = entry_settings

        # set up batch list display
        self.batchListWidget = JPLBatchListWidget(entry_settings)
        batchArea = QtGui.QScrollArea()
        batchArea.setWidgetResizable(True)
        batchArea.setWidget(self.batchListWidget)

        batchDisplay = QtGui.QGroupBox()
        batchDisplay.setTitle('Batch List')
        batchLayout = QtGui.QVBoxLayout()
        batchLayout.addWidget(batchArea)
        batchDisplay.setLayout(batchLayout)

        # set up single scan monitor + daq class
        self.singleScan = SingleScan(filename, parent=self, main=self.main)

        # set up progress bar
        self.currentProgBar = QtGui.QProgressBar()
        self.totalProgBar = QtGui.QProgressBar()

        progressDisplay = QtGui.QWidget()
        progressLayout = QtGui.QGridLayout()
        progressLayout.addWidget(QtGui.QLabel('Current Progress'), 0, 0)
        progressLayout.addWidget(self.currentProgBar, 0, 1)
        progressLayout.addWidget(QtGui.QLabel('Total progress'), 1, 0)
        progressLayout.addWidget(self.totalProgBar, 1, 1)
        progressDisplay.setLayout(progressLayout)

        mainLayout = QtGui.QGridLayout()
        mainLayout.addWidget(batchDisplay, 0, 0, 1, 2)
        mainLayout.addWidget(self.singleScan, 0, 2, 1, 3)
        mainLayout.addWidget(progressDisplay, 1, 0, 1, 5)
        self.setLayout(mainLayout)

        # Initiate progress bar
        total_time = ceil(Shared.jpl_scan_time(entry_settings))
        self.totalProgBar.setRange(0, total_time)
        self.totalProgBar.setValue(0)
        self.batch_pts_taken = 0

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

        msg = Shared.MsgInfo(self, 'Job Finished!',
                             'Congratulations! Now it is time to grab some coffee.')
        msg.exec_()
        self.stop_timers()
        self.accept()

    def reject(self):

        q = QtGui.QMessageBox.question(self, 'Scan In Progress!',
                       'The batch scan is still in progress. Aborting the project will discard all unsaved data! \n Are you SURE to proceed?', QtGui.QMessageBox.Yes |
                       QtGui.QMessageBox.No, QtGui.QMessageBox.No)

        if q == QtGui.QMessageBox.Yes:
            self.stop_timers()
            self.accept()
        else:
            pass


class JPLBatchListWidget(QtGui.QWidget):
    ''' Batch list display '''

    def __init__(self, entry_settings):

        QtGui.QWidget.__init__(self)

        self.batchLayout = QtGui.QGridLayout()
        self.batchLayout.setAlignment(QtCore.Qt.AlignTop)
        # set up batch list row header
        # put comment in the first column and make it editable
        self.batchLayout.addWidget(QtGui.QLabel('#'), 0, 0)
        self.batchLayout.addWidget(QtGui.QLabel('Comment'), 0, 1)
        self.batchLayout.addWidget(QtGui.QLabel('Start'), 0, 2)
        self.batchLayout.addWidget(QtGui.QLabel('Stop'), 0, 3)
        self.batchLayout.addWidget(QtGui.QLabel('Step'), 0, 4)
        self.batchLayout.addWidget(QtGui.QLabel('Avg'), 0, 5)
        self.batchLayout.addWidget(QtGui.QLabel('Sens'), 0, 6)
        self.batchLayout.addWidget(QtGui.QLabel('Time Const'), 0, 7)
        self.batchLayout.addWidget(QtGui.QLabel('Wait time'), 0, 8)
        self.batchLayout.addWidget(QtGui.QLabel('(MHz)'), 1, 2)
        self.batchLayout.addWidget(QtGui.QLabel('(MHz)'), 1, 3)
        self.batchLayout.addWidget(QtGui.QLabel('(MHz)'), 1, 4)
        self.batchLayout.addWidget(QtGui.QLabel('(ms)'), 1, 8)

        # add batch list entry
        self.entryList = []
        for row in range(len(entry_settings)):
            # entry = (start, stop, step, avg, sens_idx, tc_idx, waittime, comment)
            current_setting = entry_settings[row]
            entry = Shared.JPLLIABatchListEntry(self, entry_setting=current_setting)
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
            self.batchLayout.addWidget(entry.waitTimeLabel, row+2, 8)
            self.entryList.append(entry)

        self.setLayout(self.batchLayout)


class SingleScan(QtGui.QWidget):
    ''' Take a scan in a single freq window '''

    def __init__(self, filename, parent=None, main=None):
        ''' parent is the JPL scan dialog window. It contains shared settings.
            main is the main GUI window. It containts instrument handles
        '''
        QtGui.QWidget.__init__(self, parent)
        self.main = main
        self.parent = parent
        self.filename = filename

        # Initialize shared settings
        if self.main.testModeAction.isChecked():
            pass
        else:
            self.multiplier = api_val.MULTIPLIER[self.main.synCtrl.bandSel.currentIndex()]

        # Initialize scan entry settings
        self.start_rf_freq = 0
        self.stop_rf_freq = 0
        self.current_rf_freq = 0
        self.acquired_avg = 0
        self.step = 0
        self.sens_index = 0
        self.waittime = 30

        self.waitTimer = QtCore.QTimer()
        self.waitTimer.setInterval(self.waittime)
        self.waitTimer.setSingleShot(True)
        self.waitTimer.timeout.connect(self.query_lockin)

        # set up main layout
        buttons = QtGui.QWidget()
        jumpButton = QtGui.QPushButton('Jump to Next Window')
        abortAllButton = QtGui.QPushButton('Abort Batch Project')
        self.pauseButton = QtGui.QPushButton('Pause Current Scan')
        self.pauseButton.setCheckable(True)
        redoButton = QtGui.QPushButton('Redo Current Scan')
        restartWinButton = QtGui.QPushButton('Restart Current Window')
        saveButton = QtGui.QPushButton('Save and Continue')
        buttonLayout = QtGui.QGridLayout()
        buttonLayout.addWidget(self.pauseButton, 0, 0)
        buttonLayout.addWidget(redoButton, 0, 1)
        buttonLayout.addWidget(restartWinButton, 0, 2)
        buttonLayout.addWidget(saveButton, 1, 0)
        buttonLayout.addWidget(jumpButton, 1, 1)
        buttonLayout.addWidget(abortAllButton, 1, 2)
        buttons.setLayout(buttonLayout)

        pgWin = pg.GraphicsWindow(title='Live Monitor')
        self.yPlot = pgWin.addPlot(1, 0, title='Current sweep')
        self.yPlot.setLabels(left='Intensity', bottom='Frequency (MHz)')
        self.ySumPlot = pgWin.addPlot(0, 0, title='Sum sweep')
        self.ySumPlot.setLabels(left='Intensity')
        self.yCurve = self.yPlot.plot()
        self.yCurve.setDownsampling(auto=True, method='peak')
        self.yCurve.setPen(pg.mkPen(220, 220, 220))
        self.ySumCurve = self.ySumPlot.plot()
        self.ySumCurve.setDownsampling(auto=True, method='peak')
        self.ySumCurve.setPen(pg.mkPen(219, 112, 147))
        mainLayout = QtGui.QVBoxLayout()
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
        ''' Update scan entry setting. Starts a scan after setting update.
            entry = (start_freq <MHz>, stop_freq <MHz>, step <MHz>, averages <int>,
            lockin sens_index <int>, lockin tc_index <int>, itgtime <ms>, waittime <ms>)
        '''

        self.x = Shared.gen_x_array(*entry_setting[0:3])
        self.x_min = min(entry_setting[0], entry_setting[1])
        self.step = entry_setting[2]
        self.current_x_index = 0
        self.target_avg = entry_setting[3]
        self.acquired_avg = 0
        self.sens_index = entry_setting[4]
        self.tc_index = entry_setting[5]
        self.waittime = entry_setting[6]
        self.waitTimer.setInterval(self.waittime)
        self.current_comment = entry_setting[7]
        self.y = np.zeros_like(self.x)
        self.y_sum = np.zeros_like(self.x)
        self.ySumCurve.setData(self.x, self.y_sum)
        total_pts =  len(self.x) * self.target_avg
        self.pts_taken = 0
        self.parent.currentProgBar.setRange(0, ceil(total_pts*self.waittime*1e-3))
        self.parent.currentProgBar.setValue(ceil(self.pts_taken*self.waittime*1e-3))

        # set lockin properties
        if self.main.testModeAction.isChecked():
            pass
        else:
            api_lia.set_sens(self.main.liaHandle, self.sens_index)
            api_lia.set_tc(self.main.liaHandle, self.tc_index)

        self.tune_syn()

    def tune_syn(self):
        ''' Tune synthesizer frequency '''

        if self.main.testModeAction.isChecked():
            pass
        else:
            api_syn.set_syn_freq(self.main.synHandle, self.x[self.current_x_index]/self.multiplier)

        self.waitTimer.start()

    def query_lockin(self):
        ''' Query lockin data. Triggered by waitTimer.timeout() '''

        # append data to data list
        if self.main.testModeAction.isChecked():
            self.y[self.current_x_index] = np.random.random_sample()
        else:
            self.y[self.current_x_index] = api_lia.query_single_x(self.main.liaHandle)
        # update plot
        self.yCurve.setData(self.x, self.y)
        # move to the next frequency, update freq index and average counter
        self.next_freq()
        # if done
        if self.acquired_avg == self.target_avg:
            self.save_data()
            self.parent.batch_pts_taken += ceil(len(self.x)*self.target_avg*self.waittime*1e-3)
            self.parent.next_entry_signal.emit()
        else:
            self.tune_syn()

    def next_freq(self):
        ''' move to the next frequency point '''

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
        self.parent.currentProgBar.setValue(ceil(self.pts_taken*self.waittime*1e-3))
        self.parent.totalProgBar.setValue(self.parent.batch_pts_taken +
                                          ceil(self.pts_taken*self.waittime*1e-3))

    def update_ysum(self):
        ''' Update sum plot '''

        # add current y array to y_sum
        self.y_sum += self.y
        # update plot
        self.ySumCurve.setData(self.x, self.y_sum)

    def save_data(self):
        ''' Save data array '''

        # Grab current comment (in case edited during the scan) before saving data
        entry = self.parent.batchListWidget.entryList[self.parent.current_entry_index]
        self.current_comment = entry.commentFill.text()

        # grab lockin & synthesizer information
        if self.main.testModeAction.isChecked():
            tc = self.main.liaInfo.tcIndex
        else:
            tc = api_lia.read_tc(self.main.liaHandle)

        mod_stat = self.main.synCtrl.modModeSel.currentText()
        if mod_stat == 'AM':
            mod_freq = self.main.synInfo.AM1Freq * 1e-3
            mod_amp = self.main.synInfo.AM1DepthPercent * 1e2
        elif mod_stat == 'FM':
            mod_freq = self.main.synInfo.FM1Freq * 1e-3
            mod_amp = self.main.synInfo.FM1Dev * 1e-3
        else:
            mod_freq = 0
            mod_amp = 0

        # prepare header
        h_info = (self.main.synInfo.vdiBandMultiplication,
                  self.waittime, api_val.LIASENSLIST[self.sens_index],
                  api_val.LIATCLIST[tc]*1e-3, mod_freq, mod_amp, mod_stat,
                  self.main.liaInfo.refHarm, self.main.liaInfo.refPhase,
                  self.x_min, self.step, self.acquired_avg,
                  self.current_comment)

        # if already finishes at least one sweep
        if self.acquired_avg > 0:
            save.save_lwa(self.filename, self.y_sum / self.acquired_avg, h_info)
        else:
            save.save_lwa(self.filename, self.y, h_info)

    def pause_current(self, btn_pressed):
        ''' Pause/resume data acquisition '''

        if btn_pressed:
            self.pauseButton.setText('Resume Current Scan')
            #print('pause')
            self.waitTimer.stop()
        else:
            self.pauseButton.setText('Pause Current Scan')
            #print('resume')
            self.waitTimer.start()

    def redo_current(self):
        ''' Erase current y array and restart a scan '''

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
        self.tune_syn()

    def restart_avg(self):
        ''' Erase all current averages and start over '''

        q = QtGui.QMessageBox.question(self, 'Scan In Progress!',
                       'Restart will erase all cached averages.\n Are you sure to proceed?', QtGui.QMessageBox.Yes |
                       QtGui.QMessageBox.No, QtGui.QMessageBox.No)

        if q == QtGui.QMessageBox.Yes:
            #print('restart average')
            self.waitTimer.stop()
            self.acquired_avg = 0
            self.current_x_index = 0
            self.y = np.zeros_like(self.x)
            self.y_sum = np.zeros_like(self.x)
            self.ySumCurve.setData(self.x, self.y_sum)
            self.tune_syn()
        else:
            pass

    def save_current(self):
        ''' Save what's got so far and continue '''

        self.waitTimer.stop()
        self.save_data()
        self.waitTimer.start()

    def jump(self):
        ''' Jump to next batch item '''

        q = QtGui.QMessageBox.question(self, 'Jump To Next',
                       'Save aquired data for the current scan window?', QtGui.QMessageBox.Yes |
                       QtGui.QMessageBox.No | QtGui.QMessageBox.Cancel, QtGui.QMessageBox.Yes)

        if q == QtGui.QMessageBox.Yes:
            #print('abort current')
            self.waitTimer.stop()
            self.parent.batch_pts_taken += len(self.x)*self.target_avg
            self.save_data()
            self.parent.next_entry_signal.emit()
        elif q == QtGui.QMessageBox.No:
            #print('abort current')
            self.waitTimer.stop()
            self.parent.batch_pts_taken += len(self.x)*self.target_avg
            self.parent.next_entry_signal.emit()
        else:
            pass

    def abort_all(self):

        self.parent.reject()
