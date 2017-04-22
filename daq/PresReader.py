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

    # multiplication factor for time unit conversion.
    # 0: unity, seconds; 1: 60, minite; 2: 3600, hour.
    _TIMEUNIT = {0: 1, 1:60, 2:3600}

    def __init__(self, main=None):
        QtGui.QDialog.__init__(self, main)
        self.main = main
        self.setWindowTitle('CENTER TWO pressure reader')
        self.setMinimumSize(900, 600)
        self.setModal(False)

        # add left column widigets
        # this is a monitor panel for realtime readings
        rtMonitor = QtGui.QGroupBox(self)
        rtMonitor.setTitle('Readtime Monitor')
        self.currentP = QtGui.QLabel()
        self.currentUnit = QtGui.QLabel()
        self.currentChannel = QtGui.QLabel()
        self.currentStatus = QtGui.QLabel()
        monitorLayout = QtGui.QGridLayout()
        monitorLayout.addWidget(QtGui.QLabel('Channel'), 0, 0)
        monitorLayout.addWidget(QtGui.QLabel('Status'), 0, 1)
        monitorLayout.addWidget(QtGui.QLabel('Pressure'), 2, 0)
        monitorLayout.addWidget(QtGui.QLabel('Unit'), 2, 1)
        monitorLayout.addWidget(self.currentChannel, 1, 0)
        monitorLayout.addWidget(self.currentStatus, 1, 1)
        monitorLayout.addWidget(self.currentP, 3, 0)
        monitorLayout.addWidget(self.currentUnit, 3, 1)
        rtMonitor.setLayout(monitorLayout)

        # this is a mini control panel for the readout
        rdCtrl = QtGui.QGroupBox(self)
        rdCtrl.setTitle('Readout Control')
        self.channelSel = QtGui.QComboBox()
        self.channelSel.addItems(['1', '2'])
        self.pUnitSel = QtGui.QComboBox()
        self.pUnitSel.addItems(['mBar', 'Torr', 'Pascal', 'μmHg'])
        self.pUnitSel.setCurrentIndex(1)
        rdCtrlLayout = QtGui.QFormLayout()
        rdCtrlLayout.addRow(QtGui.QLabel('Select Channel'), self.channelSel)
        rdCtrlLayout.addRow(QtGui.QLabel('Select Pressure Unit'), self.pUnitSel)
        rdCtrl.setLayout(rdCtrlLayout)

        # this is to select the data update rate, cannot be quicker than /0.1 s
        rateSelect = QtGui.QWidget()
        self.updateRate = QtGui.QLineEdit()
        self.updateRate.setText('1')
        self.updateRateUnit = QtGui.QComboBox()
        self.updateRateUnit.addItems(['sec', 'min', 'h'])
        self.updateRateUnit.setCurrentIndex(0)
        rateSelectLayout = QtGui.QHBoxLayout(self)
        rateSelectLayout.addWidget(QtGui.QLabel('Update Rate'))
        rateSelectLayout.addWidget(self.updateRate)
        rateSelectLayout.addWidget(QtGui.QLabel(' per '))
        rateSelectLayout.addWidget(self.updateRateUnit)
        rateSelect.setLayout(rateSelectLayout)

        # putting stuff together in the left column
        leftColumn = QtGui.QWidget()
        leftColumnLayout = QtGui.QVBoxLayout(self)
        leftColumnLayout.setAlignment(QtCore.Qt.AlignTop)
        leftColumnLayout.addWidget(rtMonitor)
        leftColumnLayout.addWidget(rdCtrl)
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
        self.channelSel.currentIndexChanged.connect(self.update_rt)
        self.updateRate.textChanged.connect(self.set_update_period)
        self.updateRateUnit.currentIndexChanged.connect(self.set_update_period)
        self.pUnitSel.currentIndexChanged.connect(self.set_unit)
        self.startButton.clicked.connect(self.start)
        self.stopButton.clicked.connect(self.stop)
        self.saveButton.clicked.connect(self.save)
        self.savepButton.clicked.connect(self.save_and_continue)
        self.timer.timeout.connect(self.daq)

        # set default unit to Torr on the read out
        self.set_unit(1)
        # start reading
        self.update_rt()

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

        tscalar = self._TIMEUNIT[self.updateRateUnit.currentIndex()]

        msgcode, self.waittime = api_val.val_float(self.updateRate.text(),
                                                  safe=[('>=', 0.1/tscalar)])
        self.updateRate.setStyleSheet('border: 1px solid {:s}'.format(Shared.msgcolor(msgcode)))
        self.waittime *= tscalar
        if status==2:
            self.timer.setInterval(self.waittime*1000)
            self.data = np.array([0, self.current_p])
            self.counter = 0
            self.timer.start()
        else:
            pass

    def set_unit(self, idx):
        ''' Set pressure unit '''

        if self.main.testModeAction.isChecked():
            pass
        else:
            api_pres.set_query_p_unit(self.main.pressureHandle, idx)

        self.update_rt()

    def update_rt(self):
        ''' Update real time monitor '''

        if self.main.testModeAction.isChecked():
            unit_txt = self.pUnitSel.currentText()
        else:
            _, unit_txt = api_pres.set_query_p_unit(self.main.pressureHandle)

        self.currentChannel.setText(self.channelSel.currentText())
        self.currentUnit.setText(unit_txt)

    def daq(self):

        if self.main.testModeAction.isChecked():
            self.current_p = np.random.rand()
            msgcode = 2
            status_txt = 'Okay'
        else:
            msgcode, status_txt, self.current_p = api_pres.query_p(self.main.pressureHandle,
                                                    self.channelSel.currentText())

        self.currentP.setText('{:.3f}'.format(self.current_p))
        self.currentStatus.setText(status_txt)
        self.currentStatus.setStyleSheet('color: {:s}'.format(Shared.msgcolor(msgcode)))

        if not msgcode: # if fatal, stop daq
            self.timer.stop()
        else:
            pass
        print('still update')

    def update_plot(self):
        self.counter += 1
        t = self.counter*self.waittime
        self.data = np.row_stack((self.data, np.array([t, self.current_p])))
        self.curve.setData(self.data)

    def save_data(self):
        try:
            filename, _ = QtGui.QFileDialog.getSaveFileName(self, 'Save Data', './test_pressure.txt', 'Data File (*.txt)')
            np.savetxt(filename, self.data, comments='#', fmt=['%.1f', '%.3e'],
                       header='time(sec) pressure({:s})'.format(self.currentUnit.text()))
        except AttributeError:
            msg = Shared.MsgError(self, Shared.btn_label('error'), 'No data has been collected!')
            msg.exec_()

    # stop timer before close 
    def closeEvent(self, event):
        self.timer.stop()
        self.close()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.timer.stop()
            self.close()
        else:
            pass
