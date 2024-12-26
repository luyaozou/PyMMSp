#! encoding = utf-8

from PyQt6 import QtWidgets, QtCore
import numpy as np
import pyvisa
from PyMMSp.ui import ui_shared
from PyMMSp.inst import lockin as api_lia
from PyMMSp.inst import validator as api_val


class CtrlLockin(QtWidgets.QWidget):

    def __init__(self, prefs, ui, info, handle, parent=None):
        super().__init__(parent)

        self.prefs = prefs
        self.ui = ui
        self.info = info
        self.handle = handle

        self._data = np.zeros(0)
        self._monitor_counter = 0
        # set up timer
        self.timer = QtCore.QTimer()
        self.monitor_set_wait_time()

        # -- Trigger setting status and communication
        self.ui.lockinPanel.phaseFill.textChanged.connect(self.tune_phase)
        self.ui.lockinPanel.harmSel.currentTextChanged[str].connect(self.tune_harmonics)
        self.ui.lockinPanel.comboTau.currentIndexChanged[int].connect(self.tune_time_const)
        self.ui.lockinPanel.comboSens.currentIndexChanged[int].connect(self.tune_sensitivity)
        self.ui.lockinPanel.coupleSel.currentIndexChanged[int].connect(self.tune_couple)
        self.ui.lockinPanel.reserveSel.currentIndexChanged[int].connect(self.tune_reserve)
        self.ui.lockinPanel.groundingSel.currentIndexChanged[int].connect(self.tune_grounding)
        self.ui.lockinPanel.filterSel.currentIndexChanged[int].connect(self.tune_filter)
        self.ui.lockinPanel.autoPhaseBtn.clicked.connect(self.auto_phase)
        self.ui.lockinPanel.resetBtn.clicked.connect(self.reset)
        self.ui.lockinPanel.clicked.connect(self.check)
        self.ui.liaStatus.clicked.connect(self.check)
        self.ui.liaStatus.errMsgBtn.clicked.connect(self.pop_err_msg)
        self.ui.liaStatus.refreshButton.clicked.connect(self.manual_refresh)
        self.ui.liaStatus.moreInfoButton.clicked.connect(self.ui.dLockin.show)
        self.ui.dLockin.refreshButton.clicked.connect(self.dialog_manual_refresh)
        self.timer.timeout.connect(self.monitor_daq)
        self.ui.liaMonitor.startButton.clicked.connect(self.monitor_start)
        self.ui.liaMonitor.restartButton.clicked.connect(self.monitor_restart)
        self.ui.liaMonitor.stopButton.clicked.connect(self.monitor_stop)
        self.ui.liaMonitor.updateRate.currentIndexChanged.connect(self.monitor_set_wait_time)
        self.ui.liaMonitor.slenFill.textChanged.connect(self.monitor_set_len)

    def check(self):
        """ Enable/disable this groupbox """

        if self.prefs.is_test or self.handle:
            api_lia.init_lia(self.handle)
            self.ui.lockinPanel.setChecked(True)
            self.ui.liaStatus.setChecked(True)
        else:
            msg = ui_shared.MsgError(self, 'No Instrument!', 'No lockin amplifier is connected!')
            msg.exec()
            self.ui.lockinPanel.setChecked(False)
            self.ui.liaStatus.setChecked(False)

        self.ui.liaStatus.print_info()

    def tune_phase(self, phase_text):
        """
            Communicate with the lockin and set phase
        """

        status, phase = api_val.val_lia_phase(phase_text)
        self.ui.lockinPanel.phaseFill.setStyleSheet(f'border: 1px solid {ui_shared.msg_color(status)}')

        if status:
            if self.prefs.is_test:
                # fake a successful communication on test mode
                self.info.ref_phase = phase
            else:
                vCode = api_lia.set_phase(self.handle, phase)
                if vCode == pyvisa.constants.StatusCode.success:
                    self.info.ref_phase = api_lia.read_phase(self.handle)
                else:
                    msg = ui_shared.InstStatus(self, vCode)
                    msg.exec()
        else:
            pass

        self.ui.liaStatus.print_info(self.info)  # auto refresh status panel

    def tune_harmonics(self, harm_text):
        """
            Communicate with the lockin and set Harmonics
        """

        if self.prefs.is_test:
            lia_freq = self.info.refFreq
        else:
            lia_freq = api_lia.read_freq(self.handle)
        status, harm = api_val.val_lia_harm(harm_text, lia_freq)

        if status:
            if self.prefs.is_test:
                # fake a successful communication on test mode
                self.info.ref_harm = harm
            else:
                vCode = api_lia.set_harm(self.handle, harm)
                if vCode == pyvisa.constants.StatusCode.success:
                    self.info.ref_harm = api_lia.read_harm(self.handle)
                else:
                    msg = ui_shared.InstStatus(self, vCode)
                    msg.exec()
        else:
            msg = ui_shared.MsgError(self, 'Out of Range!', 'Input harmonics exceed legal range!')
            msg.exec()

        self.ui.liaStatus.print_info(self.info)  # auto refresh status panel

    def tune_sensitivity(self, idx):
        """
            Communicate with the lockin and set sensitivity
        """

        if self.prefs.is_test:
            # fake a successful communication on test mode
            self.info.sens_idx = idx
        else:
            vCode = api_lia.set_sens(self.handle, idx)
            if vCode == pyvisa.constants.StatusCode.success:
                self.info.sens_idx = api_lia.read_sens(self.handle)
            else:
                msg = ui_shared.InstStatus(self, vCode)
                msg.exec()

        self.ui.liaStatus.print_info(self.info)  # auto refresh status panel

    def tune_time_const(self, idx):
        """
            Communicate with the lockin and set sensitivity
        """

        if self.prefs.is_test:
            # fake a successful communication on test mode
            self.info.tau_idx = idx
        else:
            vCode = api_lia.set_tc(self.handle, idx)
            if vCode == pyvisa.constants.StatusCode.success:
                self.info.tau_idx = api_lia.read_tc(self.handle)
            else:
                msg = ui_shared.InstStatus(self, vCode)
                msg.exec()

        self.ui.liaStatus.print_info(self.info)  # auto refresh status panel
        self.ui.liaMonitor.set_wait_time()

    def tune_couple(self, idx):
        """
            Communicate with the lockin and set couple mode
        """

        if self.prefs.is_test:
            # fake a successful communication on test mode
            self.info.couple_idx = idx
        else:
            vCode = api_lia.set_couple(self.handle, idx)
            if vCode == pyvisa.constants.StatusCode.success:
                self.info.couple_idx = api_lia.read_couple(self.handle)
            else:
                msg = ui_shared.InstStatus(self, vCode)
                msg.exec()

        self.ui.liaStatus.print_info(self.info)  # auto refresh status panel

    def tune_reserve(self, idx):
        """
            Communicate with the lockin and set reserve
        """

        if self.prefs.is_test:
            # fake a successful communication on test mode
            self.info.reserve_idx = idx
        else:
            vCode = api_lia.set_reserve(self.handle, idx)
            if vCode == pyvisa.constants.StatusCode.success:
                self.info.reserve_idx = api_lia.read_reserve(self.handle)
            else:
                msg = ui_shared.InstStatus(self, vCode)
                msg.exec()

        self.ui.liaStatus.print_info(self.info)  # auto refresh status panel

    def tune_grounding(self, idx):
        """
            Communicate with the lockin and set input grounding
        """

        if self.prefs.is_test:
            # fake a successful communication on test mode
            self.info.gnd_idx = idx
        else:
            vCode = api_lia.set_input_grounding(self.handle, idx)
            if vCode == pyvisa.constants.StatusCode.success:
                self.info.gnd_idx = api_lia.read_input_grounding(self.handle)
            else:
                msg = ui_shared.InstStatus(self, vCode)
                msg.exec()

        self.ui.liaStatus.print_info(self.info)  # auto refresh status panel

    def tune_filter(self, idx):
        """
            Communicate with the lockin and set input notch filter
        """

        if self.prefs.is_test:
            # fake a successful communication on test mode
            self.info.input_filter_idx = idx
        else:
            vCode = api_lia.set_input_filter(self.handle, idx)
            if vCode == pyvisa.constants.StatusCode.success:
                self.info.input_filter_idx = api_lia.read_input_filter(self.handle)
            else:
                msg = ui_shared.InstStatus(self, vCode)
                msg.exec()

        self.ui.liaStatus.print_info(self.info)  # auto refresh status panel

    def auto_phase(self):

        if self.prefs.is_test:
            # fake a successful communication on test mode
            print('auto (random) phase (test)')
            self.info.ref_phase = np.random.randint(-180, 180)
            self.ui.lockinPanel.phaseFill.setText(f'{self.info.ref_phase:.2f}')
        else:
            vCode = api_lia.auto_phase(self.handle)
            if vCode == pyvisa.constants.StatusCode.success:
                self.info.ref_phase = api_lia.read_phase(self.handle)
                self.ui.lockinPanel.phaseFill.setText(f'{self.info.ref_phase:.2f}')
            else:
                msg = ui_shared.InstStatus(self, vCode)
                msg.exec()

        self.ui.liaStatus.print_info()  # auto refresh status panel

    def reset(self):

        if self.prefs.is_test:
            # fake a successful communication on test mode
            vCode = pyvisa.constants.StatusCode.success
        else:
            vCode = api_lia.reset(self.handle)

        if vCode == pyvisa.constants.StatusCode.success:
            self.manual_refresh()
        else:
            msg = ui_shared.InstStatus(self, vCode)
            msg.exec()

    def manual_refresh(self):
        """ Manually refresh status. Also update the LIACtrl widgets,
        which will in turn trigger the refresh function.
        """

        if self.prefs.is_test or (not self.handle):
            pass
        else:
            api_lia.full_info_query_(self.info, self.handle)
            self.ui.lockinPanel.harmSel.setCurrentIndex(self.info.ref_harm_idx)
            self.ui.lockinPanel.phaseFill.setText('{:.2f}'.format(self.info.ref_phase))
            self.ui.lockinPanel.comboSens.setCurrentIndex(self.info.sens_idx)
            self.ui.lockinPanel.comboTau.setCurrentIndex(self.info.tau_idx)
            self.ui.lockinPanel.coupleSel.setCurrentIndex(self.info.couple_idx)
            self.ui.lockinPanel.reserveSel.setCurrentIndex(self.info.reserve_idx)
            self.ui.liaMonitor.set_wait_time()

    def pop_err_msg(self):
        """ Pop error message """
        if self.handle:
            self.ui.liaStatus.errMsgLabel.setText(api_lia.query_err_msg(self.handle))
        else:
            pass

    def dialog_manual_refresh(self):

        api_lia.full_info_query_(self.info, self.handle)
        self.ui.dLockin.print_info(self.info)

    def monitor_start(self, btn_pressed):

        if btn_pressed:
            self.ui.liaMonitor.startButton.setText('Pause')
            self.timer.start()
        else:
            self.ui.liaMonitor.startButton.setText('Continue')
            self.timer.stop()

    def monitor_restart(self):

        self._monitor_counter = 0  # reset counter
        self.ui.liaMonitor.startButton.setChecked(True)  # retrigger start button
        self.ui.liaMonitor.startButton.setText('Pause')
        self.timer.start()

    def monitor_stop(self):

        self.timer.stop()
        self._monitor_counter = 0
        self.ui.liaMonitor.startButton.setChecked(False)  # reset start button
        self.ui.liaMonitor.startButton.setText('Start')

    def monitor_set_wait_time(self):
        """ Set wait time according to self.updateRate """

        status, wait_time = api_val.val_lia_monitor_srate(
            self.ui.liaMonitor.updateRate.currentIndex(), self.info.tau_idx)
        self.timer.setInterval(int(wait_time))
        self.ui.liaMonitor.updateRate.setStyleSheet(f'border: 1px solid {ui_shared.msg_color(status)}')
        if status:
            pass
        else:
            msg = ui_shared.MsgWarning(self, 'Update speed warning!',
                                       """The picked update speed is faster than the lockin time constant.
                                    Automatically reset the update speed to 3pi * time_constant """)
            msg.exec()
            self.ui.liaMonitor.updateRate.setCurrentIndex(7)

    def monitor_set_len(self, text):
        status, slen = api_val.val_monitor_sample_len(text)
        self.ui.liaMonitor.slenFill.setStyleSheet(f'border: 1px solid {ui_shared.msg_color(status)}')
        if status:
            self._data = np.zeros(slen)
            self.monitor_restart()
        else:
            self.monitor_stop()

    def monitor_daq(self):
        """ If sampled points are less than the set length, fill up the array
            If sampled points are more than the set length, roll the array
            forward and fill the last array element with new data
        """

        if self._monitor_counter < len(self._data):
            self._data[self._monitor_counter] = api_lia.query_single_x(self.handle)
            self.ui.liaMonitor.update_plot(self._data[:self._monitor_counter])
            self._monitor_counter += 1
        else:
            self._data = np.roll(self._data, len(self._data) - 1)
            self._data[-1] = api_lia.query_single_x(self.handle)
            self.ui.liaMonitor.update_plot(self._data)
