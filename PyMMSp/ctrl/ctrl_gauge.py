#! encoding = utf-8

from PyQt6 import QtWidgets, QtCore
import numpy as np
import datetime
import pyvisa
from PyMMSp.ui import ui_shared
from PyMMSp.inst import gauge as api_gauge
from PyMMSp.inst import validator as api_val


class CtrlGauge(QtWidgets.QWidget):

    # multiplication factor for time unit conversion.
    # 0: unity, seconds; 1: 60, minite; 2: 3600, hour.
    _TIMEUNIT = {0: 1, 1: 60, 2: 3600}

    def __init__(self, prefs, ui, info, handle, parent=None):
        super().__init__(parent)

        self.prefs = prefs
        self.ui = ui
        self.info = info
        self.handle = handle

        # set up timer & default value
        self.wait_time = 1
        self.timer = QtCore.QTimer()
        self.timer.setInterval(1000)
        self.timer.start()

        # trigger settings
        self.ui.dGauge.channelSel.activated.connect(self.set_channel)
        self.ui.dGauge.updateRate.textChanged.connect(self.set_update_period)
        self.ui.dGauge.updateRateUnitSel.activated.connect(self.protect_update_period)
        self.ui.dGauge.pUnitSel.activated.connect(self.protect_p_unit)
        self.ui.dGauge.startButton.clicked.connect(self.start)
        self.ui.dGauge.stopButton.clicked.connect(self.stop)
        self.ui.dGauge.saveButton.clicked.connect(self.save)
        self.ui.dGauge.savepButton.clicked.connect(self.save_and_continue)
        self.ui.dGauge.finished.connect(self.timer.stop)
        self.timer.timeout.connect(self.daq)
        self._data_collecting = False
        self._counter = 0
        self._data = np.array([0, 0])
        self._msg_code = 2
        self._data_start_time = datetime.datetime.today()
        self._current_unit_idx = 0
        self._current_chn_idx = 0
        self._current_p_unit_idx = 0
        self._current_p = 0
        # set default unit
        self.set_p_unit()

    def start(self):

        # avoid connecting to the timer multiple times
        self.stop()
        # check if update period is legal. Won't start if illegal
        if self._msg_code == 2:
            # turn data collection status on
            self._data_collecting = True
            # disable update rate QLineEdit
            self.ui.dGauge.updateRate.setReadOnly(True)
            self.ui.dGauge.updateRate.setStyleSheet('color: grey')
            # store start time (for file saving)
            self._data_start_time = datetime.datetime.today()
            # restart QtTimer
            self.timer.start()
            # initiate data array
            self._data = np.array([0, self._current_p])
            self._counter = 0
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
        self._data_collecting = False  # turn data collection status off
        # enable update rate QLineEdit
        self.ui.dGauge.updateRate.setReadOnly(False)
        self.ui.dGauge.updateRate.setStyleSheet(
            f'color: black; border: 1px solid {ui_shared.msg_color(self._msg_code)}')

    def save(self):

        self.stop()
        self.save_data()

    def save_and_continue(self):

        self.save_data()

    def protect_update_period(self, idx):
        """ Protect update period unit change if data is under collection """

        if idx == self._current_unit_idx:
            # ignore if unit index is not changed
            pass
        else:
            if self._data_collecting:
                q = QtWidgets.QMessageBox.question(
                    self, 'Change Time Unit?',
                    'Data under collection. Change time unit will cause data lost!',
                    QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
                    QtWidgets.QMessageBox.StandardButton.Yes)
                if q == QtWidgets.QMessageBox.StandardButton.Yes:
                    # update index
                    self._current_unit_idx = idx
                    self.set_update_period()
                else:
                    # change the index back to what it was before
                    self.ui.dGauge.updateRateUnitSel.setCurrentIndex(self._current_unit_idx)
            else:
                # update index
                self._current_unit_idx = idx
                self.set_update_period()

    def set_update_period(self):
        """ Set wait time according to self.updateRate """

        # stop data collection and re-enable update rate QLineEdit
        self.stop()
        self.ui.dGauge.updateRate.setReadOnly(False)
        self.ui.dGauge.updateRate.setStyleSheet('color: black')

        tau_scalar = self._TIMEUNIT[self.ui.dGauge.updateRateUnitSel.currentIndex()]

        self._msg_code, self.wait_time = api_val.val_float(
            self.ui.dGauge.updateRate.text(), safe=[('>=', 0.1 / tau_scalar)])
        self.ui.dGauge.updateRate.setStyleSheet(f'border: 1px solid {ui_shared.msg_color(self._msg_code)}')
        if self._msg_code == 2:
            self.ui.dGauge.set_label(
                'bottom', text='Time', units=self.ui.dGauge.updateRateUnitSel.currentText())
            self.timer.setInterval(self.wait_time * tau_scalar * 1000)
        else:
            pass

    def protect_p_unit(self, idx):
        """ Protect pressure unit change if data is under collection """

        if idx == self._current_p_unit_idx:
            # ignore if unit index is not changed
            pass
        else:
            if self._data_collecting:
                q = QtWidgets.QMessageBox.question(
                    self, 'Change Pressure Unit?',
                    'Data under collection. Change pressure unit will cause data lost!',
                    QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
                    QtWidgets.QMessageBox.StandardButton.Yes)
                if q == QtWidgets.QMessageBox.StandardButton.Yes:
                    # update pressure unit index
                    self._current_p_unit_idx = idx
                    self.set_p_unit()
                else:
                    # change the index back to what it was before
                    self.ui.dGauge.pUnitSel.setCurrentIndex(self._current_p_unit_idx)
            else:
                # update pressure unit index
                self._current_p_unit_idx = idx
                self.set_p_unit()

    def set_p_unit(self):
        """ Set pressure unit """

        if self.prefs.is_test:
            unit_txt = self.ui.dGauge.pUnitSel.currentText()
        else:
            _, unit_txt = api_gauge.set_query_p_unit(
                self.handle, self.ui.dGauge.pUnitSel.currentIndex())
        # update real time monitor panel
        self.ui.dGauge.currentUnit.setText(unit_txt)
        # update plot label
        self.ui.dGauge.set_label('left', 'Pressure', unit_txt)
        if self._data_collecting:
            # restart data collection
            self.start()
        else:
            pass

    def set_channel(self, idx):
        """ Set channel """

        if idx == self._current_chn_idx:
            # ignore if channel is not changed
            pass
        else:
            if self._data_collecting:
                q = QtWidgets.QMessageBox.question(
                    self, 'Change Channel?',
                    'Data under collection. Change channel will cause data lost!',
                    QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
                    QtWidgets.QMessageBox.StandardButton.Yes)
                if q == QtWidgets.QMessageBox.StandardButton.Yes:
                    self._current_chn_idx = idx
                    self.ui.dGauge.currentChannel.setText(self.ui.dGauge.channelSel.currentText())
                    # restart data collection
                    self.start()
                else:
                    # change the index back to what it was before
                    self.ui.dGauge.channelSel.setCurrentIndex(self._current_chn_idx)
            else:
                self._current_chn_idx = idx
                self.ui.dGauge.currentChannel.setText(self.ui.dGauge.channelSel.currentText())
                # restart daq
                self.timer.start()

    def daq(self):

        if self.prefs.is_test:
            self._current_p = np.random.rand()
            msg_code = 2
            status_txt = 'Okay'
        else:
            msg_code, status_txt, self._current_p = api_gauge.query_p(
                self.handle, self.ui.dGauge.channelSel.currentText())
        self.ui.dGauge.currentP.setText('{:.3e}'.format(self._current_p))
        self.ui.dGauge.currentStatus.setText(status_txt)
        self.ui.dGauge.currentStatus.setStyleSheet(f'color: {ui_shared.msg_color(msg_code)}')

        if not msg_code:  # if fatal, stop daq
            self.timer.stop()
        else:
            pass

    def update_plot(self):
        self._counter += 1
        t = self._counter * self.wait_time
        self._data = np.row_stack((self._data, np.array([t, self._current_p])))
        self.ui.dGauge.plot(self._data)

    def save_data(self):
        try:
            filename, _ = QtWidgets.QFileDialog.getSaveFileName(
                self, 'Save Data','./test_pressure.txt', 'Data File (*.txt)')
            if filename:
                np.savetxt(filename, self._data, comments='#', fmt=['%g', '%.3e'],
                           header='Data collection starts at {:s} \ntime({:s}) pressure({:s})'.format(
                               self._data_start_time.strftime('%I:%M:%S %p, %m-%d-%Y (%a)'),
                               self.ui.dGauge.updateRateUnitSel.currentText(),
                               self.ui.dGauge.currentUnit.text()))
            else:
                pass
        except AttributeError:
            msg = ui_shared.MsgError(self, ui_shared.btn_label('error'), 'No data has been collected!')
            msg.exec()

    def eventFilter(self, obj, ev):
        """ Override eventFilter to close the dialog when ESC is pressed """
        if obj == self.ui.dGauge and ev.type() == QtCore.QEvent.Type.KeyPress:
            if ev.key() == QtCore.Qt.Key.Key_Escape:
                self.ui.dGauge.close()
                return True
        return super().eventFilter(obj, ev)
