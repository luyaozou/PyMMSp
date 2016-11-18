#! encoding = utf-8

''' Lockin scanning routine in JPL style '''


from PyQt4 import QtGui, QtCore
import pyqtgraph as pg
from gui import SharedWidgets as Shared
from api import general as apigen
from api import validator as apival
from api import lockin as apilc


class JPLScanConfig(QtGui.QDialog):
    '''
        Configuration window preparing for the scan
    '''

    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.parent = parent
        self.setWindowTitle('Lockin scan configuration (JPL style)')
        self.setMinimumSize(800, 300)

        # Add shared setting panel
        self.itgTimeFill = QtGui.QLineEdit()
        self.itgTimeUnit = QtGui.QComboBox()
        self.itgTimeUnit.addItems(['ms', 's'])
        self.waitTimeFill = QtGui.QLineEdit()
        self.waitTimeFill.setText('10')

        itgTime = QtGui.QWidget()
        itgTimeLayout = QtGui.QHBoxLayout()
        itgTimeLayout.addWidget(QtGui.QLabel('Integration Time (> 2pi * time constant)'))
        itgTimeLayout.addWidget(self.itgTimeFill)
        itgTimeLayout.addWidget(self.itgTimeUnit)
        waitTime = QtGui.QWidget()
        waitTimeLayout = QtGui.QHBoxLayout()
        waitTime = QtGui.QWidget()
        waitTimeLayout.addWidget(QtGui.QLabel('Wait Time'))
        waitTimeLayout.addWidget(self.waitTimeFill)
        waitTimeLayout.addWidget(QtGui.QLabel('ms'))
        itgTime.setLayout(itgTimeLayout)
        waitTime.setLayout(waitTimeLayout)

        sharedSetting = QtGui.QWidget()
        sharedSettingLayout = QtGui.QHBoxLayout()
        sharedSettingLayout.addWidget(itgTime)
        sharedSettingLayout.addWidget(waitTime)
        sharedSetting.setLayout(sharedSettingLayout)

        # Add top buttons
        addBatchButton = QtGui.QPushButton('Add batch')
        removeBatchButton = QtGui.QPushButton('Remove last batch')
        saveButton = QtGui.QPushButton('File Destination')
        topButtonLayout = QtGui.QHBoxLayout()
        topButtonLayout.addWidget(addBatchButton)
        topButtonLayout.addWidget(removeBatchButton)
        topButtonLayout.addWidget(saveButton)
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
        mainLayout.addWidget(sharedSetting)
        mainLayout.addWidget(topButtons)
        mainLayout.addWidget(entryArea)
        mainLayout.addWidget(bottomButtons)
        self.setLayout(mainLayout)

        cancelButton.clicked.connect(self.reject)
        acceptButton.clicked.connect(self.get_settings)
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

    def get_settings(self):
        ''' Read batch settings from entries and proceed.
            Returns a list of seting tuples in the format of
            (start_rf_freq MHz, stop_rf_freq MHz, step MHz, averages, lockin sens_index)
        '''

        vdi_index = self.parent.synCtrl.bandSelect.currentIndex()
        tc_index = apilc.read_tc(self.parent.lcHandle)
        entry_settings = []

        no_error = True

        # get shared settings from shared panel
        status, itgtime = apival.val_lc_itg_time(self.itgTimeFill.text(),
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
            status1, start_rf_freq = apival.val_syn_freq(entry.startFreqFill.text(), vdi_index)
            status2, stop_rf_freq = apival.val_syn_freq(entry.stopFreqFill.text(), vdi_index)
            status3, step = apival.val_float(entry.stepFill.text())
            status4, average = apival.val_int(entry.avgFill.text())
            sens_index = entry.sensSel.currentIndex()
            # put them into a setting tuple
            if not (status1 or status2 or status3 or status4):
                no_error *= True
                setting_entry = (start_rf_freq, stop_rf_freq, step, average, sens_index)
                # put the setting tuple into a list
                entry_settings.append(setting_entry)
            else:
                no_error *= False

        if no_error:
            self.accept()
            return (itgtime, waittime), entry_settings
        else:
            msg = Shared.MsgError(self.parent, 'Invalid input!', 'Please fix invalid inputs before proceeding.')
            msg.exec_()


class JPLScanWindow(QtGui.QDialog):
    ''' Scanning window '''

    def __init__(self, parent, shared_settings, entry_settings):
        QtGui.QWidget.__init__(self, parent)
        self.parent = parent
        self.setWindowTitle('Lockin scan monitor')

        self.pgPlot = pg.PlotWidget(title='Live Monitor')
        mainLayout = QtGui.QGridLayout()
        mainLayout.addWidget(self.pgPlot)
        self.setLayout(mainLayout)

    def scan(self, shared_settings, entry_settings):
        pass
