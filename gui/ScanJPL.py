#! encoding = utf-8

''' Lockin scanning routine in JPL style '''


from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import QObject
import pyqtgraph as pg
from gui import SharedWidgets as Shared
from api import general as apigen
from api import validator as apival


class JPLScanConfig(QtGui.QDialog):
    '''
        Configuration window preparing for the scan
    '''

    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.parent = parent
        self.setMinimumSize(800, 600)

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
        mainLayout.addWidget(topButtons)
        mainLayout.addWidget(entryArea)
        mainLayout.addWidget(bottomButtons)
        self.setLayout(mainLayout)

        QObject.connect(cancelButton, QtCore.SIGNAL("clicked()"), self.reject)
        QObject.connect(acceptButton, QtCore.SIGNAL("clicked()"), self.accept)
        QObject.connect(addBatchButton, QtCore.SIGNAL("clicked()"), self.add_entry)
        QObject.connect(removeBatchButton, QtCore.SIGNAL("clicked()"), self.remove_entry)

    def add_entry(self):
        ''' Add batch entry to this dialog window '''

        # generate a new batch entry
        entry = Shared.FreqWinEntryNoCaption()
        # add this entry to the layout and to the filler list
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

    # you need the static method that is not bound to the class object to return
    # variables.
    @staticmethod
    def proceed(parent):
        ''' Read batch settings from entries and proceed.
            Returns a list of seting tuples in the format of
            (start_rf_freq MHz, stop_rf_freq MHz, averages, lockin sens_index)
        '''

        d = JPLScanConfig(parent)
        result = d.exec_()

        vdi_index = d.parent.synCtrl.bandSelect.currentIndex()
        settings = []

        if result:
            for entry in d.entryList:
                # read settings
                status1, start_rf_freq = apival.val_syn_freq(entry.startFreqFill.text(), vdi_index)
                status2, stop_rf_freq = apival.val_syn_freq(entry.stopFreqFill.text(), vdi_index)
                status3, average = apival.val_int(entry.avgFill.text())
                sens_index = entry.sensSel.currentIndex()
            # put them into a setting tuple
            if not (status1 or status2 or status3):
                setting_entry = (start_rf_freq, stop_rf_freq, average, sens_index)
                # put the setting tuple into a list
                settings.append(setting_entry)
            else:
                msg = Shared.MsgError(d, 'Invalid input!', 'Please fix invalid inputs before proceed.')
                msg.exec_()
        else:
            pass

        return settings, result


class JPLScanWindow(QtGui.QDialog):
    ''' Scanning window '''

    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.parent = parent

        self.pgPlot = pg.PlotWidget(title='Live Monitor')
        mainLayout = QtGui.QGridLayout()
        mainLayout.addWidget(self.pgPlot)
        self.setLayout(mainLayout)
