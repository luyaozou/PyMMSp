#! encoding = utf-8

''' Lockin scanning routine in JPL style '''


from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import QObject
from api import general as apigen


class JPLScanConfig(QtGui.QDialog):
    '''
        Configuration window preparing for the scan
    '''

    def __init__(self, parent, main):
        QtGui.QDialog.__init__(self, parent)
        self.parent = parent
        self.setMinimumWidth(400)
        self.setMinimumHeight(600)

        self.sglWinConfigPanel = QtGui.QGroupBox()
        self.sglWinConfigPanel.setTitle('Single Window Mode')
        self.sglWinConfigPanel.setCheckable(True)
        self.sglWinConfigPanel.setChecked(True)
        sglWinLayout = QtGui.QFormLayout()
        startFreqFill = QtGui.QLineEdit()
        stopFreqFill = QtGui.QLineEdit()
        stepSizeFill = QtGui.QLineEdit()
        avgFill = QtGui.QLineEdit()
        sglWinLayout.addRow('Start Freq (MHz)', startFreqFill)
        sglWinLayout.addRow('Stop Freq (MHz)', stopFreqFill)
        sglWinLayout.addRow('Step Size (kHz)', stepSizeFill)
        sglWinLayout.addRow('Average', avgFill)
        self.sglWinConfigPanel.setLayout(sglWinLayout)


        self.batchConfigPanel = QtGui.QGroupBox()
        self.batchConfigPanel.setTitle('Batch Mode')
        self.batchConfigPanel.setCheckable(True)
        self.batchConfigPanel.setChecked(False)
        batchLayout = QtGui.QGridLayout()
        addBatchButton = QtGui.QPushButton('Add batch')
        batchLayout.addWidget(addBatchButton, 0, 0)
        batchLayout.addWidget(QtGui.QLabel('Windown (MHz)'), 1, 0)
        batchLayout.addWidget(QtGui.QLineEdit(), 1, 1)
        batchLayout.addWidget(QtGui.QLabel(' to '), 1, 2)
        batchLayout.addWidget(QtGui.QLineEdit(), 1, 3)
        self.batchConfigPanel.setLayout(batchLayout)

        #scanModeGButtons = QtGui.QButtonGroup(self)
        #scanModeGButtons.setExclusive(True)
        #scanModeGButtons.addButton(self.sglWinConfigPanel, 0)
        #scanModeGButtons.addButton(self.batchConfigPanel, 1)

        cancelButton = QtGui.QPushButton('Cancel')
        acceptButton = QtGui.QPushButton('Do it!')

        self.mainLayout = QtGui.QGridLayout()
        self.mainLayout.addWidget(self.sglWinConfigPanel, 0, 0, 1, 2)
        self.mainLayout.addWidget(self.batchConfigPanel, 1, 0, 1, 2)
        self.mainLayout.addWidget(cancelButton, 2, 0)
        self.mainLayout.addWidget(acceptButton, 2, 1)
        self.setLayout(self.mainLayout)

        QObject.connect(cancelButton, QtCore.SIGNAL("clicked()"), self.close)
