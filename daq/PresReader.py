#! encoding = utf-8

''' CENTER TWO pressure reader routine '''


from PyQt5 import QtGui, QtCore
import numpy as np
from math import ceil
import pyqtgraph as pg
from gui import SharedWidgets as Shared
from api import validator as api_val
from api import pressure as api_pres

class PresReaderWindow(QtGui.QDialog):
    '''
        Pressure reader window
    '''

    def __init__(self, main=None):
        QtGui.QDialog.__init__(self, main)
        self.main = main
        self.setWindowTitle('CENTER TWO pressure reader')
        self.setMinimumSize(900, 600)

        # add left column widigets
        self.currentP = QtGui.QLabel()
        rateSelect = QtGui.QWidget()
        self.updateRate = QtGui.QLineEdit()
        self.updateRate.setText('1')
        rateSelectLayout = QtGui.QHBoxLayout(self)
        rateSelectLayout.addWidget(QtGui.QLabel('Update Period'))
        rateSelectLayout.addWidget(self.updateRate)
        rateSelectLayout.addWidget(QtGui.QLabel('sec'))
        rateSelect.setLayout(rateSelectLayout)

        leftColumn = QtGui.QWidget()
        leftColumnLayout = QtGui.QVBoxLayout(self)
        leftColumnLayout.setAlignment(QtCore.Qt.AlignTop)
        leftColumnLayout.addWidget(QtGui.QLabel('Current Pressure'))
        leftColumnLayout.addWidget(self.currentP)
        leftColumnLayout.addWidget(rateSelect)
        leftColumn.setLayout(leftColumnLayout)

        # add right colun widgets
        settingPanel = QtGui.QWidget()
        self.startButton = QtGui.QPushButton('(Re)Start')
        self.stopButton = QtGui.QPushButton('Stop')
        self.saveButton = QtGui.QPushButton('Save')
        self.savepButton = QtGui.QPushButton('Save and Continue')
        panelLayout = QtGui.QHBoxLayout()
        panelLayout.addWidget(self.startButton)
        panelLayout.addWidget(self.stopButton)
        panelLayout.addWidget(self.saveButton)
        panelLayout.addWidget(self.savepButton)
        settingPanel = QtGui.QWidget()
        settingPanel.setLayout(panelLayout)

        rightColumn = QtGui.QWidget()
        self.pgPlot = pg.PlotWidget(title='Pressure Monitor',
                                    labels={'left': 'Pressure', 'bottom': 'time (sec)'})
        self.curve = self.pgPlot.plot()
        rightColumnLayout = QtGui.QVBoxLayout()
        rightColumnLayout.setAlignment(QtCore.Qt.AlignTop)
        rightColumnLayout.addWidget(self.pgPlot)
        rightColumnLayout.addWidget(settingPanel)
        rightColumn.setLayout(rightColumnLayout)

        # Set up main layout
        mainLayout = QtGui.QHBoxLayout(self)
        mainLayout.setSpacing(0)
        mainLayout.addWidget(leftColumn)
        mainLayout.addWidget(rightColumn)
        self.setLayout(mainLayout)

        # set up timer & default value
        self.waittime = 1
        self.timer = QtCore.QTimer()
        self.timer.setInterval(1000)
        self.timer.start()

        # trigger settings
        self.startButton.clicked.connect(self.start)
        self.stopButton.clicked.connect(self.stop)
        self.saveButton.clicked.connect(self.save)
        self.savepButton.clicked.connect(self.save_and_continue)
        self.updateRate.textChanged.connect(self.set_update_period)
        self.timer.timeout.connect(self.daq)

    def start(self):

        self.timer.start()
        self.data = np.array([0, self.current_p])
        self.counter = 0
        self.timer.timeout.connect(self.update_plot)

    def stop(self):

        # can't find the correct way to check if the timer is connected,
        # this is a cheat
        try:
            self.timer.timeout.disconnect(self.update_plot)
        except TypeError:
            pass

    def save(self):

        try:
            self.timer.timeout.disconnect(self.update_plot)
        except TypeError:
            pass
        self.save_data()

    def save_and_continue(self):

        self.save_data()
        self.timer.timeout.connect(self.update_plot)

    def set_update_period(self):
        ''' Set wait time according to self.updateRate '''

        status, self.waittime = api_val.val_float(self.updateRate.text(),
                                                  safe=[('>=', 0.1)])
        self.updateRate.setStyleSheet('border: 1px solid {:s}'.format(Shared.msgcolor(status)))
        if status==2:
            self.timer.setInterval(self.waittime*1000)
            self.data = np.array([0, self.current_p])
            self.counter = 0
            self.timer.start()
        else:
            pass

    def daq(self):

        if self.main.testModeAction.isChecked():
            self.current_p = np.random.rand()
        else:
            self.current_p = api_pres.read_pressure(self.main.pressureHandle)

        self.currentP.setText('{:.3f}'.format(self.current_p))

    def update_plot(self):
        self.counter += 1
        t = self.counter*self.waittime
        self.data = np.row_stack((self.data,
                                 np.array([t, self.current_p])))
        self.curve.setData(self.data)

    def save_data(self):
        try:
            filename, _ = QtGui.QFileDialog.getSaveFileName(self, 'Save Data', './test_pressure.txt', 'Data File (*.txt)')
            np.savetxt(filename, self.data, comment='#time(sec) pressure(unit)', fmt=['%.1f', '%.3g'])
        except AttributeError:
            msg = Shared.MsgError(self, Shared.btn_label('error'), 'No data has been collected!')
            msg.exec_()
