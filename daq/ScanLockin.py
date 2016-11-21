#! encoding = utf-8

''' Lockin scanning routine in JPL style '''


from PyQt4 import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
from gui import SharedWidgets as Shared
from api import general as apigen
from api import validator as apival
from api import lockin as apilc
from api import synthesizer as apisyn
from data import save


class JPLScanConfig(QtGui.QDialog):
    '''
        Configuration window preparing for the scan
    '''

    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.parent = parent
        self.setWindowTitle('Lockin scan configuration (JPL style)')
        self.setMinimumSize(800, 350)

        # Add shared setting panel
        self.itgTimeFill = QtGui.QLineEdit()
        self.itgTimeUnit = QtGui.QComboBox()
        self.itgTimeUnit.addItems(['ms', 's'])
        self.waitTimeFill = QtGui.QLineEdit()
        self.waitTimeFill.setText('10')

        sharedSetting = QtGui.QWidget()
        sharedSettingLayout = QtGui.QHBoxLayout()
        sharedSettingLayout.setSpacing(0)
        sharedSettingLayout.addWidget(QtGui.QLabel('Integration Time (> 2pi * time constant)'))
        sharedSettingLayout.addWidget(self.itgTimeFill)
        sharedSettingLayout.addWidget(self.itgTimeUnit)
        sharedSettingLayout.addWidget(QtGui.QLabel('Wait Time'))
        sharedSettingLayout.addWidget(self.waitTimeFill)
        sharedSettingLayout.addWidget(QtGui.QLabel('ms'))
        sharedSetting.setLayout(sharedSettingLayout)

        # Add top buttons
        addBatchButton = QtGui.QPushButton('Add batch')
        removeBatchButton = QtGui.QPushButton('Remove last batch')
        saveButton = QtGui.QPushButton('Save File Destination')
        self.fileLabel = QtGui.QLabel('Save Data to: ')
        topButtonLayout = QtGui.QGridLayout()
        topButtonLayout.addWidget(addBatchButton, 0, 0)
        topButtonLayout.addWidget(removeBatchButton, 0, 1)
        topButtonLayout.addWidget(saveButton, 0, 2)
        topButtonLayout.addWidget(self.fileLabel, 1, 0, 1, 3)
        topButtons = QtGui.QWidget()
        topButtons.setLayout(topButtonLayout)

        # Add bottom buttons
        cancelButton = QtGui.QPushButton('Cancel')
        acceptButton = QtGui.QPushButton('Do it!')
        acceptButton.setDefault(True)
        bottomButtonLayout = QtGui.QHBoxLayout()
        bottomButtonLayout.addWidget(cancelButton)
        bottomButtonLayout.addWidget(acceptButton)
        bottomButtons = QtGui.QWidget()
        bottomButtons.setLayout(bottomButtonLayout)

        # Add freq config entries
        self.entryList = []
        self.entryList.append(Shared.FreqWinEntryCaption(self.parent))

        self.entryLayout = QtGui.QVBoxLayout()
        self.entryLayout.setSpacing(0)
        self.entryLayout.addWidget(sharedSetting)
        for freqEntry in self.entryList:
            self.entryLayout.addWidget(freqEntry)

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
        acceptButton.clicked.connect(self.get_settings)
        saveButton.clicked.connect(self.set_file_directory)
        addBatchButton.clicked.connect(self.add_entry)
        removeBatchButton.clicked.connect(self.remove_entry)

    def add_entry(self):
        ''' Add batch entry to this dialog window '''

        # generate a new batch entry
        entry = Shared.FreqWinEntryNoCaption(self.parent)
        # add this entry to the layout and to the entry list
        self.entryList.append(entry)
        self.entryLayout.addWidget(entry)

    def remove_entry(self):
        ''' Remove last batch entry in this dialog window '''

        # if there is only one entry, skip and pop up warning
        if len(self.entryList) == 1:
            msg = Shared.MsgWarning(self.parent, 'Cannot remove batch!',
                             'At least one batch entry is required!')
            msg.exec_()
        else:
            # remove this entry
            entry = self.entryList.pop()
            self.entryLayout.removeWidget(entry)
            entry.deleteLater()

    def set_file_directory(self):

        d = QtGui.QFileDialog(self)
        d.setAcceptMode(QtGui.QFileDialog.AcceptSave)
        d.setFileMode(QtGui.QFileDialog.AnyFile)
        d.setNameFilter("SMAP File (*.lwa)")
        d.setDefaultSuffix("lwa")
        d.exec_()
        self.filename = d.selectedFiles()[0]
        self.fileLabel.setText('Save Data to: {:s}'.format(self.filename))

    def get_settings(self):
        ''' Read batch settings from entries and proceed.
            Returns a list of seting tuples in the format of
            (start_freq MHz, stop_freq MHz, step MHz, averages, lockin sens_index)
        '''

        vdi_index = self.parent.synCtrl.bandSelect.currentIndex()
        tc_index = apilc.read_tc(self.parent.lcHandle)
        entry_settings = []

        no_error = True

        # get shared settings from shared panel
        status, itgtime = apival.val_lc_itgtime(self.itgTimeFill.text(),
                                                self.itgTimeUnit.currentText(),
                                                tc_index)
        self.itgTimeFill.setStyleSheet('border: 1px solid {:s}'.format(Shared.msgcolor(status)))

        if status:
            no_error *= False
        else:
            pass

        status, waittime = apival.val_float(self.waitTimeFill.text())
        self.waitTimeFill.setStyleSheet('border: 1px solid {:s}'.format(Shared.msgcolor(status)))
        if status:
            no_error *= False
        else:
            pass

        # get settings from entry
        for entry in self.entryList:
            # read settings
            status1, start_freq = apival.val_prob_freq(entry.startFreqFill.text(), vdi_index)
            status2, stop_freq = apival.val_prob_freq(entry.stopFreqFill.text(), vdi_index)
            status3, step = apival.val_float(entry.stepFill.text())
            status4, average = apival.val_int(entry.avgFill.text())
            sens_index = entry.sensSel.currentIndex()
            # put them into a setting tuple
            if not (status1 or status2 or status3 or status4):
                no_error *= True
                setting_entry = (start_freq, stop_freq, step, average, sens_index)
                # put the setting tuple into a list
                entry_settings.append(setting_entry)
            else:
                no_error *= False

        if no_error:
            self.accept()
            return (itgtime, waittime), entry_settings, self.filename
        else:
            msg = Shared.MsgError(self.parent, 'Invalid input!', 'Please fix invalid inputs before proceeding.')
            msg.exec_()


class JPLScanWindow(QtGui.QDialog):
    ''' Scanning window '''

    # define a pyqt signal to control batch scans
    move_to_next_entry = QtCore.pyqtSignal()

    def __init__(self, parent, shared_settings, entry_settings, filename):
        QtGui.QWidget.__init__(self, parent)
        self.parent = parent
        self.setWindowTitle('Lockin scan monitor')
        self.setMinimumSize(800, 600)

        # set up batch list display
        self.entry_settings = entry_settings
        entry_setting_list = []
        for entry in entry_settings:
            entry_str = '{:.3f} -- {:.3f} MHz;\n    step={:.3f} MHz; avg={:d}; '.format(*entry)
            entry_str += 'sens={:s}'.format(Shared.LIASENSLIST[entry[-1]])
            entry_setting_list.append(entry_str)

        self.batchList = QtGui.QListWidget()
        self.batchList.addItems(entry_setting_list)
        self.batchList.setSelectionMode(1)
        self.batchList.setCurrentRow(0)
        batchArea = QtGui.QScrollArea()
        batchArea.setWidgetResizable(True)
        batchArea.setWidget(self.batchList)

        batchDisplay = QtGui.QGroupBox()
        batchDisplay.setTitle('Batch List')
        batchLayout = QtGui.QVBoxLayout()
        batchLayout.addWidget(batchArea)
        batchDisplay.setLayout(batchLayout)

        # set up single scan monitor + daq class
        self.singleScan = SingleScan(self, parent, shared_settings, filename)

        # set up progress bar
        currentProgress = QtGui.QLabel('Current Progress')
        totalProgress = QtGui.QLabel('Total Progress')
        progressDisplay = QtGui.QWidget()
        progressLayout = QtGui.QVBoxLayout()
        progressLayout.addWidget(currentProgress)
        progressLayout.addWidget(totalProgress)
        progressDisplay.setLayout(progressLayout)

        mainLayout = QtGui.QGridLayout()
        mainLayout.addWidget(batchDisplay, 0, 0)
        mainLayout.addWidget(self.singleScan, 0, 1, 1, 2)
        mainLayout.addWidget(progressDisplay, 1, 0, 1, 3)
        self.setLayout(mainLayout)


        self.move_to_next_entry.connect(self.next_entry)
        self.current_entry_index = -1   # make sure batch starts at index 0
        self.move_to_next_entry.emit()

    def next_entry(self):

        self.current_entry_index += 1
        if self.current_entry_index < len(self.batchList):
            self.batchList.setCurrentRow(self.current_entry_index)
            self.singleScan.update_setting(self.entry_settings[self.current_entry_index])
        else:
            self.finish()

    def finish(self):
        msg = Shared.MsgInfo(self, 'Job Finished!',
                             'Congratulations! Now it is time to grab some coffee.')
        msg.exec_()
        self.accept()


class SingleScan(QtGui.QWidget):
    ''' Take a scan in a single freq window '''

    def __init__(self, parent, main, shared_settings, filename):
        ''' parent is the JPL scan dialog window. It contains shared settings.
            main is the main GUI window. It containts instrument handles
            shared_settings contains shared setting tuple (itgtime, waittime)
        '''
        QtGui.QWidget.__init__(self, parent)
        self.main = main
        self.parent = parent
        self.filename = filename

        # Initialize shared settings
        self.itgtime, self.waittime = shared_settings
        self.multiplier = apival.MULTIPLIER[self.main.synCtrl.bandSelect.currentIndex()]

        # Initialize scan entry settings
        self.start_rf_freq = 0
        self.stop_rf_freq = 0
        self.current_rf_freq = 0
        self.current_avg = 0
        self.step = 0
        self.sens_index = 0

        # Set up timers
        self.itgTimer = QtCore.QTimer()
        self.itgTimer.setInterval(self.itgtime)
        self.itgTimer.setSingleShot(True)
        self.itgTimer.timeout.connect(self.query_lockin)

        self.waitTimer = QtCore.QTimer()
        self.waitTimer.setInterval(self.waittime)
        self.waitTimer.setSingleShot(False)
        self.waitTimer.timeout.connect(self.tune_lockin)

        # set up main layout
        buttons = QtGui.QWidget()
        self.abortCurrentButton = QtGui.QPushButton('Abort Current Scan')
        self.abortAllButton = QtGui.QPushButton('Abort Batch Project')
        self.pauseButton = QtGui.QPushButton('Pause Current Scan')
        self.redoButton = QtGui.QPushButton('Redo Current Scan')
        buttonLayout = QtGui.QHBoxLayout()
        buttonLayout.addWidget(self.abortCurrentButton)
        buttonLayout.addWidget(self.abortAllButton)
        buttonLayout.addWidget(self.pauseButton)
        buttonLayout.addWidget(self.redoButton)
        buttons.setLayout(buttonLayout)

        self.pgPlot = pg.PlotWidget(title='Live Monitor')
        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(self.pgPlot)
        mainLayout.addWidget(buttons)
        self.setLayout(mainLayout)

    def update_setting(self, entry_setting):
        ''' Update scan entry setting. Starts a scan after setting update.
            entry = (start_freq, stop_freq, step, average, sens_index)
        '''

        self.x = Shared.gen_x_array(self.multiplier, *entry_setting[0:3])
        self.current_x_index = 0
        self.avg = entry_setting[3]
        self.current_avg = 0
        self.sens_index = entry_setting[4]
        self.y = np.empty_like(self.x)
        self.y_sum = np.zeros_like(self.x)
        self.tune_syn()

    def tune_syn(self):
        ''' Tune synthesizer frequency '''

        apisyn.set_syn_freq(self.main.synHandle, self.x[self.current_x_index])
        self.waitTimer.start()

    def tune_lockin(self):
        ''' Set up lockin to be ready. Triggered by waitTimer.timeout() '''

        # set lockin sensitivity
        apilc.set_sens(self.main.lcHandle, self.sens_index)
        # clear buffer
        self.main.lcHandle.write('REST')
        # set update rate to be 512 Hz
        self.main.lcHandle.write('SRAT13')
        # set buffer to single shot
        self.main.lcHandle.write('SEND0')
        # start buffer and timer
        self.main.lcHandle.write('STRT')
        self.itgTimer.start()

    def query_lockin(self):
        ''' Query lockin data. Triggered by itgTimer.timeout() '''

        # pause buffer
        lcHandle.write('PAUS')
        # get buffer length
        n = lcHandle.query('SPTS?')
        buffer_data = lcHandle.query('TRCA1,0,{:d}'.format(int(n.strip())-1))
        # parse buffer_data
        y = np.array(buffer_data.split(','), dtype=float)
        y_avg = np.average(y)
        # append data to data list
        self.y[self.current_x_index] = y_avg
        # free memory
        del y
        del buffer_data
        # update plot
        self.pgPlot.plot(self.x[self.current_x_index] * self.multiplier, y_avg)
        # move to the next frequency
        if self.current_x_index < len(self.x):
            self.current_x_index += 1
            self.tune_syn()
        else:   # start another average
            self.current_x_index = 0
            self.current_avg += 1
            # add current y array to y_sum
            self.y_sum += self.y
            # update plot
            self.pgPlot.plot(self.x * self.multiplier, self.y_sum, pen='r')
            # free y array
            self.y = np.empty_like(self.x)
            # do more averages
            if self.current_avg < self.avg:
                self.tune_syn()
            else:   # finish scan
                self.save_data()

    def save_data(self):
        ''' Save data array '''

        tc = apilc.read_tc(self.main.lcHandle)

        h_info = (self.itgtime, apival.LIASENSLIST[self.sens_index],
                  apival.LIATCLIST[tc]*1e-3, 15, 75)

        save.save_lwa(self.filename, self.y_sum / self.current_avg, h_info)
        # clear plot
        self.pgPlot.clear()
        self.parent.move_to_next_entry.emit()
