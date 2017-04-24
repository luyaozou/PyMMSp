#! encoding = utf-8

''' CENTER TWO pressure reader routine '''


from PyQt5 import QtGui, QtCore
import numpy as np
from math import ceil
import pyqtgraph as pg
import datetime
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
        self.data = np.array([0, 0])    # initiate the data array
        self.data_collecting = False    # store data collection status
        self.msgcode = 2

        # add left column widigets
        # this is a monitor panel for realtime readings
        rtMonitor = QtGui.QGroupBox(self)
        rtMonitor.setTitle('Readtime Monitor')
        self.currentP = QtGui.QLabel()
        self.currentUnit = QtGui.QLabel()
        self.currentChannel = QtGui.QLabel('1')
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
        self.current_chn_index = 0
        self.pUnitSel = QtGui.QComboBox()
        self.pUnitSel.addItems(['mBar', 'Torr', 'Pascal', 'μmHg'])
        self.pUnitSel.setCurrentIndex(1)    # default unit Torr
        self.currentUnit.setText('Torr')    # default unit Torr
        self.current_p_unit_index = 1       # store this for unit protection
        rdCtrlLayout = QtGui.QFormLayout()
        rdCtrlLayout.addRow(QtGui.QLabel('Select Channel'), self.channelSel)
        rdCtrlLayout.addRow(QtGui.QLabel('Select Pressure Unit'), self.pUnitSel)
        rdCtrl.setLayout(rdCtrlLayout)

        # this is to select the data update rate, cannot be quicker than /0.1 s
        rateSelect = QtGui.QWidget()
        self.updateRate = QtGui.QLineEdit()
        self.updateRate.setText('1')
        self.updateRateUnitSel = QtGui.QComboBox()
        self.updateRateUnitSel.addItems(['sec', 'min', 'h'])
        self.updateRateUnitSel.setCurrentIndex(0)
        self.current_update_unit_index = 0      # store this for unit protection
        rateSelectLayout = QtGui.QHBoxLayout(self)
        rateSelectLayout.addWidget(QtGui.QLabel('Update Rate'))
        rateSelectLayout.addWidget(self.updateRate)
        rateSelectLayout.addWidget(QtGui.QLabel(' per '))
        rateSelectLayout.addWidget(self.updateRateUnitSel)
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
        # initiate pyqtgraph widget
        self.pgPlot = pg.PlotWidget(title='Pressure Monitor')
        self.pgPlot.setLabel('left', text='Pressure', units='Torr')
        self.pgPlot.setLabel('bottom', text='Time', units='sec')
        self.pgPlot.setLogMode(x=None, y=True)
        self.pgPlot.showGrid(x=True, y=True, alpha=0.5)
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
        self.channelSel.activated.connect(self.set_channel)
        self.updateRate.textChanged.connect(self.set_update_period)
        self.updateRateUnitSel.activated.connect(self.protect_update_period)
        self.pUnitSel.activated.connect(self.protect_p_unit)
        self.startButton.clicked.connect(self.start)
        self.stopButton.clicked.connect(self.stop)
        self.saveButton.clicked.connect(self.save)
        self.savepButton.clicked.connect(self.save_and_continue)
        self.timer.timeout.connect(self.daq)

        # set default unit to Torr on the read out
        self.set_p_unit()

    def start(self):

        # avoid connecting to the timer multiple times
        self.stop()
        # check if update period is legal. Won't start if illegal
        if self.msgcode == 2:
            # turn data collection status on
            self.data_collecting = True
            # disable update rate QLineEdit
            self.updateRate.setReadOnly(True)
            self.updateRate.setStyleSheet('color: grey')
            # store start time (for file saving)
            self.data_start_time = datetime.datetime.today()
            # restart QtTimer
            self.timer.start()
            # initiate data array
            self.data = np.array([0, self.current_p])
            self.counter = 0
            # connect QtTimer to update plot
            self.timer.timeout.connect(self.update_plot)
        else:
            pass

    def stop(self):

        # can't find the correct way to check if the timer is connected,
        # this is a cheat
        try:
            self.timer.timeout.disconnect(self.update_plot)
        except TypeError:
            pass
        self.data_collecting = False    # turn data collection status off
        # enable update rate QLineEdit
        self.updateRate.setReadOnly(False)
        self.updateRate.setStyleSheet('color: black; border:  1px solid {:s}'.format(Shared.msgcolor(self.msgcode)))

    def save(self):

        self.stop()
        self.save_data()

    def save_and_continue(self):

        self.save_data()

    def protect_update_period(self, idx):
        ''' Protect update period unit change if data is under collection '''

        if idx == self.current_update_unit_index:
            # ignore if unit index is not changed
            pass
        else:
            if self.data_collecting:
                q = QtGui.QMessageBox.question(self, 'Change Time Unit?',
                            'Data under collection. Change time unit will cause data lost!',
                            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.Yes)
                if q == QtGui.QMessageBox.Yes:
                    # update index
                    self.current_update_unit_index = idx
                    self.set_update_period()
                else:
                    # change the index back to what it was before
                    self.updateRateUnitSel.setCurrentIndex(self.current_update_unit_index)
            else:
                # update index
                self.current_update_unit_index = idx
                self.set_update_period()

    def set_update_period(self):
        ''' Set wait time according to self.updateRate '''

        # stop data collection and re-enable update rate QLineEdit
        self.stop()
        self.updateRate.setReadOnly(False)
        self.updateRate.setStyleSheet('color: black')

        tscalar = self._TIMEUNIT[self.updateRateUnitSel.currentIndex()]

        self.msgcode, self.waittime = api_val.val_float(self.updateRate.text(),
                                                  safe=[('>=', 0.1/tscalar)])
        self.updateRate.setStyleSheet('border: 1px solid {:s}'.format(Shared.msgcolor(self.msgcode)))
        if self.msgcode == 2:
            self.pgPlot.setLabel('bottom', text='Time',
                                 units=self.updateRateUnitSel.currentText())
            self.timer.setInterval(self.waittime*tscalar*1000)
        else:
            pass

    def protect_p_unit(self, idx):
        ''' Protect pressure unit change if data is under collection '''

        if idx == self.current_p_unit_index:
            # ignore if unit index is not changed
            pass
        else:
            if self.data_collecting:
                q = QtGui.QMessageBox.question(self, 'Change Pressure Unit?',
                            'Data under collection. Change pressure unit will cause data lost!',
                            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.Yes)
                if q == QtGui.QMessageBox.Yes:
                    # update pressure unit index
                    self.current_p_unit_index = idx
                    self.set_p_unit()
                else:
                    # change the index back to what it was before
                    self.pUnitSel.setCurrentIndex(self.current_p_unit_index)
            else:
                # update pressure unit index
                self.current_p_unit_index = idx
                self.set_p_unit()

    def set_p_unit(self):
        ''' Set pressure unit '''

        if self.main.testModeAction.isChecked():
            unit_txt = self.pUnitSel.currentText()
        else:
            _, unit_txt = api_pres.set_query_p_unit(self.main.pressureHandle,
                                                    self.pUnitSel.currentIndex())
        # update real time monitor panel
        self.currentUnit.setText(unit_txt)
        # update plot label
        self.pgPlot.setLabel('left', text='Pressure', units=unit_txt)
        if self.data_collecting:
            # restart data collection
            self.start()
        else:
            pass

    def set_channel(self, idx):
        ''' Set channel '''

        if idx == self.current_chn_index:
            # ignore if channel is not changed
            pass
        else:
            if self.data_collecting:
                q = QtGui.QMessageBox.question(self, 'Change Channel?',
                            'Data under collection. Change channel will cause data lost!',
                            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.Yes)
                if q == QtGui.QMessageBox.Yes:
                    self.current_chn_index = idx
                    self.currentChannel.setText(self.channelSel.currentText())
                    # restart data collection
                    self.start()
                else:
                    # change the index back to what it was before
                    self.channelSel.setCurrentIndex(self.current_chn_index)
            else:
                self.current_chn_index = idx
                self.currentChannel.setText(self.channelSel.currentText())
                # restart daq
                self.timer.start()

    def daq(self):

        if self.main.testModeAction.isChecked():
            self.current_p = np.random.rand()
            msgcode = 2
            status_txt = 'Okay'
        else:
            msgcode, status_txt, self.current_p = api_pres.query_p(self.main.pressureHandle,
                                                    self.channelSel.currentText())

        self.currentP.setText('{:.3e}'.format(self.current_p))
        self.currentStatus.setText(status_txt)
        self.currentStatus.setStyleSheet('color: {:s}'.format(Shared.msgcolor(msgcode)))

        if not msgcode: # if fatal, stop daq
            self.timer.stop()
        else:
            pass

    def update_plot(self):
        self.counter += 1
        t = self.counter * self.waittime
        self.data = np.row_stack((self.data, np.array([t, self.current_p])))
        self.curve.setData(self.data)

    def save_data(self):
        try:
            filename, _ = QtGui.QFileDialog.getSaveFileName(self, 'Save Data',
                                    './test_pressure.txt', 'Data File (*.txt)')
            if filename:
                np.savetxt(filename, self.data, comments='#', fmt=['%g', '%.3e'],
                           header='Data collection starts at {:s} \ntime({:s}) pressure({:s})'.format(
                           self.data_start_time.strftime('%I:%M:%S %p, %m-%d-%Y (%a)'),
                           self.updateRateUnitSel.currentText(), self.currentUnit.text()))
            else:
                pass
        except AttributeError:
            msg = Shared.MsgError(self, Shared.btn_label('error'),
                                  'No data has been collected!')
            msg.exec_()

    # stop timer before close
    def closeEvent(self, event):
        q = QtGui.QMessageBox.question(self, 'Exit Pressure Reader?',
                    'Pressure query will pause. Make sure you save your pressure readings!',
                    QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.Yes)
        if q == QtGui.QMessageBox.Yes:
            self.timer.stop()
            self.close()
        else:
            event.ignore()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.timer.stop()
            self.close()
        else:
            event.ignore()
