#! encoding = utf-8

from math import ceil
from PyQt6 import QtWidgets, QtCore
import pyqtgraph as pg
from PyMMSp.ui import ui_shared


class DialogAbsConfig(QtWidgets.QDialog):
    """ Absorption broadband scan """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Absorption Scan Configuration')
        self.setMinimumSize(1200, 600)

        # Add top buttons
        addBatchButton = QtWidgets.QPushButton('Add batch')
        removeBatchButton = QtWidgets.QPushButton('Remove last batch')
        self.saveButton = QtWidgets.QPushButton('Set File Directory')
        self.filename = 'default.lwa'
        self.fileLabel = QtWidgets.QLabel('Save Data to: {:s}'.format(self.filename))
        self.fileLabel.setStyleSheet('QLabel {color: #003366}')
        topButtonLayout = QtWidgets.QGridLayout()
        topButtonLayout.addWidget(self.saveButton, 0, 0)
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

        # self.add_entry()

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

        cancelButton.clicked[bool].connect(self.reject)
        acceptButton.clicked[bool].connect(self.accept)

    def add_entry(self):
        """ Add batch entry to this dialog window """

        # generate a new batch entry
        # default_setting = ('default', self.main.synInfo.probFreq*1e-6,
        #                     self.main.synInfo.probFreq*1e-6+10.000, 0.1, 1,
        #                     self.main.liaInfo.sensIndex,
        #                     self.main.liaInfo.tcIndex, 60,
        #                     self.main.synInfo.modModeIndex,
        #                     self.main.synInfo.modFreq,
        #                     self.main.synInfo.modAmp,
        #                     self.main.liaInfo.refHarm,
        #                     self.main.liaInfo.refPhase)
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
            entry.sensSel.setCurrentIndex(last_entry.comboSens.currentIndex())
            entry.tauSel.setCurrentIndex(last_entry.comboTau.currentIndex())
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
            self.entryLayout.removeWidget(entry.comboSens)
            entry.comboSens.deleteLater()
            self.entryLayout.removeWidget(entry.comboTau)
            entry.comboTau.deleteLater()
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


class DialogAbsSearchScan(QtWidgets.QDialog):
    """ Absorption broadband scan """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Absorption Scan -- Targeted Search')
        self.setMinimumSize(1200, 600)


class DialogAbsBBScan(QtWidgets.QDialog):
    """ Scanning window """

    # define a pyqt signal to control batch scans
    next_entry_signal = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Absorption Scan -- Broadband')
        self.setMinimumSize(1200, 600)
#        self.entry_settings = entry_settings

        # set up batch list display
#        self.batchListWidget = BatchListWidget(entry_settings)
        batchArea = QtWidgets.QScrollArea()
        batchArea.setWidgetResizable(True)
        #batchArea.setWidget(self.batchListWidget)

        batchDisplay = QtWidgets.QGroupBox()
        batchDisplay.setTitle('Batch List')
        batchLayout = QtWidgets.QVBoxLayout()
        batchLayout.addWidget(batchArea)
        batchDisplay.setLayout(batchLayout)

        # set up single scan monitor + daq class
        self.singleScan = SingleScan(self)

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


class SingleScan(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        # set up main layout
        buttons = QtWidgets.QWidget()
        self.jumpButton = QtWidgets.QPushButton('Jump to Next Batch')
        self.abortAllButton = QtWidgets.QPushButton('Abort Batch Project')
        self.pauseButton = QtWidgets.QPushButton('Pause')
        self.pauseButton.setCheckable(True)
        self.redoButton = QtWidgets.QPushButton('Redo Current Sweep')
        self.restartWinButton = QtWidgets.QPushButton('Restart Current Batch')
        self.saveButton = QtWidgets.QPushButton('Save and Continue')
        buttonLayout = QtWidgets.QGridLayout()
        buttonLayout.addWidget(self.pauseButton, 0, 0)
        buttonLayout.addWidget(self.redoButton, 0, 1)
        buttonLayout.addWidget(self.restartWinButton, 0, 2)
        buttonLayout.addWidget(self.saveButton, 1, 0)
        buttonLayout.addWidget(self.jumpButton, 1, 1)
        buttonLayout.addWidget(self.abortAllButton, 1, 2)
        buttons.setLayout(buttonLayout)

        pgWin = pg.GraphicsView()
        pgLayout = pg.GraphicsLayout()
        pgWin.setCentralItem(pgLayout)
        self.yPlot = pgLayout.addPlot(1, 0, title='Current sweep')
        self.yPlot.setLabel('left', text='Intensity', units='V')
        self.yPlot.setLabel('bottom', text='Frequency (MHz)')
        self.ySumPlot = pgLayout.addPlot(0, 0, title='Sum sweep')
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

class BatchListWidget(QtWidgets.QWidget):
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
