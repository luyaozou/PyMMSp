#! encoding = utf-8

''' Lockin scanning routine in JPL style '''


from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import QObject
import pyqtgraph as pg
from gui.SharedWidgets import FreqWinEntryCaption, FreqWinEntryNoCaption, MsgWarning
from api import general as apigen


class JPLScanConfig(QtGui.QDialog):
    '''
        Configuration window preparing for the scan
    '''

    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.parent = parent
        self.setMinimumSize(600, 600)
        
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
        self.entryList.append(FreqWinEntryCaption())

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
        entry = FreqWinEntryNoCaption()
        # add this entry to the layout and to the filler list
        self.entryList.append(entry)
        self.entryLayout.addWidget(entry)

    def remove_entry(self):
        ''' Remove last batch entry in this dialog window '''

        # if there is only one entry, skip and pop up warning
        if len(self.entryList) == 1:
            msg = MsgWarning(self.parent, 'Cannot remove batch!',
                             'At least one batch entry is required!')
            msg.exec_()
        else:
            # remove this entry
            entry = self.entryList.pop()
            self.entryLayout.removeWidget(entry)
            entry.deleteLater()


class JPLScanWindow(QtGui.QDialog):
    ''' Scanning window '''

    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.parent = parent

        self.pgPlot = pg.PlotWidget(title='Live Monitor')
        mainLayout = QtGui.QGridLayout()
        mainLayout.addWidget(self.pgPlot)
        self.setLayout(mainLayout)
