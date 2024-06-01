#! encoding = utf-8

from PyQt6 import QtWidgets, QtCore
import pyvisa
from PyMMSp.ui import ui_shared
from PyMMSp.inst import synthesizer as api_syn
from PyMMSp.inst import validator as api_val


class CtrlSyn(QtWidgets.QWidget):

    def __init__(self, prefs, ui, info, handle, parent=None):
        super().__init__(parent)

        self.prefs = prefs
        self.ui = ui
        self.info = info
        self.handle = handle

        # Trigger frequency refresh and communication
        self.ui.synPanel.probFreqFill.textChanged.connect(self.tune_freq)
        self.ui.synPanel.bandSel.currentIndexChanged.connect(self.tune_freq)

        # Trigger modulation status refresh and communication
        self.ui.synPanel.modModeSel.currentIndexChanged[int].connect(self.switch_modu_widgets)
        self.ui.synPanel.modFreqFill.textChanged.connect(self.tune_mod_parameter)
        self.ui.synPanel.modFreqUnitSel.currentIndexChanged.connect(self.tune_mod_parameter)
        self.ui.synPanel.modAmpFill.textChanged.connect(self.tune_mod_parameter)
        self.ui.synPanel.modAmpAMUnitSel.currentIndexChanged.connect(self.tune_mod_parameter)
        self.ui.synPanel.modAmpFMUnitSel.currentIndexChanged.connect(self.tune_mod_parameter)
        self.ui.synPanel.modSwitchBtn.clicked.connect(self.switch_modulation)
        self.ui.synPanel.lfSwitchBtn.clicked.connect(self.switch_lf)
        self.ui.synPanel.lfVolFill.textChanged.connect(self.tune_lf)

        # Trigger synthesizer power toggle and communication
        self.ui.synPanel.synPowerSwitchBtn.toggled.connect(self.set_syn_power_switch_btn_label)

        # Trigger groupbox check_state
        self.ui.synPanel.clicked.connect(self.check)
        self.ui.synStatus.clicked.connect(self.check)
        ## -- Trigger status updates
        self.ui.synStatus.refreshButton.clicked.connect(self.manual_refresh)
        self.ui.synStatus.moreInfoButton.clicked.connect(self.ui.synInfoDialog.display)
        self.ui.synStatus.errMsgBtn.clicked.connect(self.pop_err_msg)

        self.ui.synPanel.synPowerSwitchBtn.toggled.connect(self.set_syn_power_switch_btn_label)

    def set_syn_power_switch_btn_label(self, toggle_state):
        """
            Set power switch button text
        """

        if toggle_state:
            self.ui.synPanel.synPowerSwitchBtn.setText('ON')
        else:
            self.ui.synPanel.synPowerSwitchBtn.setText('OFF')

    def check(self):
        """ Enable/disable this groupbox """

        if (self.info.inst_name and self.handle) or self.prefs.is_test:
            self.ui.synPanel.setChecked(True)
            self.ui.synStatus.setChecked(True)
        else:
            self.ui.synPanel.setChecked(False)
            self.ui.synStatus.setChecked(False)
            self.ui.msgErr.setText('No synthesizer is connected!')
            self.ui.msgErr.exec()
        self.ui.synStatus.print_info(self.info)

    def manual_refresh(self):
        """ Manually refresh status. Also update the SynCtrl widgets,
        which will in turn trigger the refresh function
        """

        if self.prefs.is_test or (not self.handle):
            pass
        else:
            api_syn.full_info_query_(self.info, self.handle)
            self.ui.synPanel.synPowerSwitchBtn.setChecked(self.info.rf_toggle)
            self.ui.synPanel.probFreqFill.setText(f'{self.info.freq * 1e-6:.9f}')
            self.ui.synPanel.modSwitchBtn.setChecked(self.info.modu_toggle)
            self.ui.synPanel.modSwitchBtn.setText('ON' if self.info.modu_toggle else 'OFF')
            if self.ui.synInfo.AM1Toggle and (not self.info.fm1_toggle):
                self.ui.synPanel.modModeSel.setCurrentIndex(1)
                self.ui.synPanel.modFreqFill.setText(f'{self.info.am1_freq * 1e-3:.1f}')
                self.ui.synPanel.modFreqUnitSel.setCurrentIndex(1)
                self.ui.synPanel.modAmpFill.setText(f'{self.info.am1_depth_pct:.1f}')
                self.ui.synPanel.modAmpAMUnitSel.setCurrentIndex(0)
            elif (not self.info.am1_toggle) and self.info.FM1Toggle:
                self.ui.synPanel.modModeSel.setCurrentIndex(2)
                self.ui.synPanel.modFreqFill.setText(f'{self.info.fm1_toggle * 1e-3:.1f}')
                self.ui.synPanel.modFreqUnitSel.setCurrentIndex(1)
                self.ui.synPanel.modAmpFill.setText(f'{self.info.fm1_dev * 1e-3:.1f}')
                self.ui.synPanel.modAmpFMUnitSel.setCurrentIndex(1)
            else:
                self.ui.synPanel.modModeSel.setCurrentIndex(0)
            self.ui.synPanel.lfSwitchBtn.setChecked(self.info.lf_toggle)
            self.ui.synPanel.lfSwitchBtn.setText('ON' if self.info.lf_toggle else 'OFF')
            self.ui.synPanel.lfVolFill.setText(f'{self.info.lf_vol:.3f}')

    def pop_err_msg(self):
        """ Pop error message """
        if self.handle:
            self.info.err_msg = api_syn.query_err_msg(self.handle)
            self.ui.synStatus.errMsgLabel.setText(self.info.err_msg)
        else:
            pass

    def tune_freq(self):
        """
            Communicate with the synthesizer and refresh frequency setting.
        """

        # validate input
        status, synfreq = api_val.val_prob_freq(self.ui.synPanel.probFreqFill.text(),
                                                self.ui.synPanel.bandSel.currentIndex())
        # set sheet border color by syn_stat
        self.ui.synPanel.probFreqFill.setStyleSheet(f'border: 1px solid {ui_shared.msgcolor(status)}')

        if status:  # if status is not fatal
            if self.prefs.is_test:
                # fake a successful communication on test mode
                vCode = pyvisa.constants.StatusCode.success
            else:
                # call syn inst and return communication status
                vCode = api_syn.set_syn_freq(self.handle, synfreq)

            if vCode == pyvisa.constants.StatusCode.success:
                # communication successful, update synInfo
                self.info.syn_freq = synfreq
                self.info.band_idx = self.ui.synPanel.bandSel.currentIndex()
                self.info.freq = synfreq * self.info.band_multi
            else:
                msg = ui_shared.InstStatus(self, vCode)
                msg.exec()
            # refresh synthesizer status
            self.ui.synStatus.print_info(self.info)
            self.ui.synPanel.synFreqLabel.setText('{:.9f}'.format(synfreq * 1e-6))
        else:  # else ignore change
            pass

    def switch_modu_widgets(self, modu_idx):
        """
            Switch modulation setting widgets
        """

        self.info.modu_mode_idx = modu_idx
        self.tune_mod_mode(modu_idx)

        if modu_idx:  # Modulation selected. Show modulation widget
            self.ui.synPanel.modFreq.show()
            self.ui.synPanel.modAmp.show()
            self.ui.synPanel.lfVol.show()
            if modu_idx == 1:
                self.ui.synPanel.modAmpLabel.setText('Mod Depth')
                self.ui.synPanel.modAmpAMUnitSel.show()
                self.ui.synPanel.modAmpFMUnitSel.hide()
            elif modu_idx == 2:
                self.ui.synPanel.modAmpLabel.setText('Mod Dev')
                self.ui.synPanel.modAmpAMUnitSel.hide()
                self.ui.synPanel.modAmpFMUnitSel.show()
            self.tune_mod_parameter()
        else:  # No modulation. Hide modulation widget
            self.info.modu_freq = 0
            self.info.modu_amp = 0
            self.ui.synPanel.modFreq.hide()
            self.ui.synPanel.modAmp.hide()
            self.ui.synPanel.lfVol.hide()

    def tune_mod_mode(self, mod_index):
        """
            Communicate with the synthesizer and refresh modulation mode.
        """

        if self.parent.testModeAction.isChecked():
            # fake a successful communication on test mode
            if mod_index == 1:
                self.info.AM1Toggle = True
                self.info.FM1Toggle = False
            elif mod_index == 2:
                self.info.AM1Toggle = False
                self.info.FM1Toggle = True
            else:
                self.info.AM1Toggle = False
                self.info.FM1Toggle = False
        else:
            vCode = api_syn.set_mod_mode(self.handle, mod_index)
            if vCode == pyvisa.constants.StatusCode.success:
                # update synInfo
                self.info.AM1Toggle = api_syn.read_am_state(self.handle, 1)
                self.info.FM1Toggle = api_syn.read_fm_state(self.handle, 1)
            else:
                msg = ui_shared.InstStatus(self, vCode)
                msg.exec()

        self.ui.synStatus.print_info()

    def tune_mod_parameter(self):
        """
            Communicate with the synthesizer and automatically refresh modulation parameters
        """

        modu_idx = self.ui.synPanel.modModeSel.currentIndex()
        toggle_state = self.ui.synPanel.modSwitchBtn.isChecked()

        # convert input and set sheet border color by status
        freq_status, modu_freq = api_val.val_syn_mod_freq(self.ui.synPanel.modFreqFill.text(),
                                                         self.ui.synPanel.modFreqUnitSel.currentText())
        self.ui.synPanel.modFreqFill.setStyleSheet(f'border: 1px solid {ui_shared.msgcolor(freq_status)}')

        if modu_idx == 1:  # AM
            depth_status, modu_amp = api_val.val_syn_am_amp(self.ui.synPanel.modAmpFill.text(),
                                                            self.ui.synPanel.modAmpAMUnitSel.currentText())
        elif modu_idx == 2:  # FM
            depth_status, modu_amp = api_val.val_syn_fm_amp(self.ui.synPanel.modAmpFill.text(),
                                                            self.ui.synPanel.modAmpFMUnitSel.currentText())
        else:
            depth_status = 2
            modu_amp = 0
        self.ui.synPanel.modAmpFill.setStyleSheet(f'border: 1px solid {ui_shared.msgcolor(depth_status)}')

        if freq_status and depth_status and (not self.prefs.is_test):
            if modu_idx == 1:  # AM
                vCode = api_syn.set_am(self.handle, modu_freq, modu_amp, toggle_state)
            elif modu_idx == 2:  # FM
                vCode = api_syn.set_fm(self.handle, modu_freq, modu_amp, toggle_state)
            else:
                vCode = pyvisa.constants.StatusCode.success

            if vCode == pyvisa.constants.StatusCode.success:
                self.info.modu_freq = modu_freq
                self.info.modu_amp = modu_amp
                self.info.am1_freq = api_syn.read_am_freq(self.handle, 1)
                self.info.am1_depth_pct, self.info.am1_depth_db = api_syn.read_am_depth(
                    self.handle, 1)
                self.info.fm1_freq = api_syn.read_fm_freq(self.handle, 1)
                self.info.fm1_dev = api_syn.read_fm_dev(self.handle, 1)
                self.ui.synStatus.print_info(self.info)
            else:
                msg = ui_shared.InstStatus(self, vCode)
                msg.exec()
        else:
            self.info.modu_freq = modu_freq
            self.info.modu_amp = modu_amp
            self.ui.synStatus.print_info(self.info)

    def switch_modulation(self, btn_pressed):
        """
            Communicate with the synthesizer and refresh modulation on/off toggle
        """

        if self.prefs.is_test:
            # fake a successful communication on test mode
            self.info.modu_toggle = btn_pressed
        else:
            vCode = api_syn.set_mod_toggle(self.handle, btn_pressed)
            if vCode == pyvisa.constants.StatusCode.success:
                self.info.modu_toggle = api_syn.read_mod_toggle(self.handle)
            else:
                msg = ui_shared.InstStatus(self, vCode)
                msg.exec()

        if btn_pressed:
            self.ui.synPanel.modSwitchBtn.setText('ON')
        else:
            self.ui.synPanel.modSwitchBtn.setText('OFF')

        self.ui.synStatus.print_info()

    def switch_lf(self, btn_pressed):
        """
            Communicate with the synthesizer and refresh LF on/off toggle
        """

        if self.prefs.is_test:
            # fake a successful communication on test mode
            self.info.lf_toggle = btn_pressed
        else:
            vCode = api_syn.set_lf_toggle(self.handle, btn_pressed)
            if vCode == pyvisa.constants.StatusCode.success:
                self.info.lf_toggle = api_syn.read_lf_toggle(self.handle)
                self.info.lf_vol = api_syn.read_lf_voltage(self.handle)
            else:
                msg = ui_shared.InstStatus(self, vCode)
                msg.exec()

        self.ui.synPanel.lfVolFill.setText(f'{self.info.lf_vol:.3f}')

        if btn_pressed:
            self.ui.synPanel.lfSwitchBtn.setText('ON')
        else:
            self.ui.synPanel.lfSwitchBtn.setText('OFF')

        self.ui.synStatus.print_info(self.info)

    def tune_lf(self, vol_txt):
        """
            Communicate with the synthesizer and refresh LF voltage
        """

        status, lf_vol = api_val.val_syn_lf_vol(vol_txt)
        self.ui.synPanel.lfVolFill.setStyleSheet(f'border: 1px solid {ui_shared.msgcolor(status)}')

        if status:
            if self.prefs.is_test:
                # fake a successful communication on test mode
                self.info.lf_vol = lf_vol
            else:
                vCode = api_syn.set_lf_amp(self.handle, lf_vol)
                if vCode == pyvisa.constants.StatusCode.success:
                    self.info.lf_vol = api_syn.read_lf_voltage(self.handle)
                else:
                    msg = ui_shared.InstStatus(self, vCode)
                    msg.exec()

            self.ui.synStatus.print_info(self.info)
        else:
            pass


class CtrlSynPower(QtWidgets.QWidget):

    def __init__(self, prefs, ui, info, handle, parent=None):
        super().__init__(parent)
        self.prefs = prefs
        self.ui = ui
        self.info = info
        self.handle = handle

        self.powerSwitchTimer = QtCore.QTimer()
        self.powerSwitchTimer.setInterval(500)
        self.powerSwitchTimer.setSingleShot(True)
        self.powerSwitchProgBar = QtWidgets.QProgressBar()
        self.progDialog = QtWidgets.QDialog()
        self.progDialog.setWindowTitle('RF Ramp')
        progDialogLayout = QtWidgets.QVBoxLayout()
        progDialogLayout.addWidget(self.powerSwitchProgBar)
        self.progDialog.setLayout(progDialogLayout)

        self.ui.synPanel.synPowerManualInput.clicked.connect(self.syn_rf_power_manual)
        self.ui.synPanel.synPowerSwitchBtn.clicked.connect(self.syn_rf_power_auto)
        self.ui.synPanel.powerSwitchTimer.timeout.connect(self.syn_rf_power_manual)

    def ramp_syn_rf_power(self):
        """
            The actual synthesizer inst command.
            Triggered by self.powerSwitchTimer.timeout
            Returns successful status
        """

        try:
            this_power = next(self.ramper)
            if self.prefs.is_test:
                # fake a successful communication on test mode
                vCode = pyvisa.constants.StatusCode.success
            else:
                vCode = api_syn.set_syn_power(self.handle, this_power)

            if vCode == pyvisa.constants.StatusCode.success:
                self.info.syn_power = api_syn.read_syn_power(self.handle)
                self.ui.synStatus.print_info(self.info)
                self.powerSwitchProgBar.setValue(self.powerSwitchProgBar.value() + 1)
                # start timer
                self.powerSwitchTimer.start()
            else:
                self.powerSwitchTimer.stop()
                msg = ui_shared.InstStatus(self, vCode)
                msg.exec()
        except StopIteration:
            self.powerSwitchTimer.stop()
            self.progDialog.accept()

    def syn_rf_power_manual(self):
        """
            Communicate with the synthesizer and set up RF power
            (automatically turn RF on)
        """

        # Get current syn power
        if self.prefs.is_test:
            # fake a power
            self.info.syn_power = -20
        else:
            self.info.syn_power = api_syn.read_syn_power(self.handle)

        # Grab manual input power from QInputDialog
        target_power, okay = QtWidgets.QInputDialog.getInt(
            self, 'RF Power', 'Manual Input (-20 to 0)',
            self.info.syn_power, -20, 0, 1)

        if okay:  # hopefully no error occurs
            if self.prefs.is_test:
                pass
            else:
                # turn on RF toggle first
                api_syn.set_power_toggle(self.handle, True)
            self.ui.synPanel.synPowerSwitchBtn.setChecked(True)
            self.powerSwitchProgBar.setRange(0, abs(self.info.synPower - target_power))
            self.powerSwitchProgBar.setValue(0)
            if self.info.syn_power > target_power:
                self.ramper = api_syn.ramp_down(self.info.synPower, target_power)
            else:
                self.ramper = api_syn.ramp_up(self.info.synPower, target_power)
            self.ramp_syn_rf_power()
            self.progDialog.exec()
        else:
            pass

    def syn_rf_power_auto(self, btn_pressed):
        """
            Automatically switch synthesizer RF on/off
        """

        # Get current syn power
        if self.prefs.is_test:
            # fake a power
            self.info.syn_power = -20
        else:
            self.info.syn_power = api_syn.read_syn_power(self.handle)

        if btn_pressed:  # user wants to turn on
            if self.prefs.is_test:
                pass
            else:
                api_syn.set_power_toggle(self.handle, True)
            self.ramper = api_syn.ramp_up(self.info.synPower, 0)
            self.powerSwitchProgBar.setRange(0, abs(self.info.synPower))
            self.powerSwitchProgBar.setValue(0)
            self.ramp_syn_rf_power()
            self.progDialog.exec()
        elif self.info.syn_power > -20:  # user wants to turn off, needs ramp down
            self.ramper = api_syn.ramp_down(self.info.syn_power, -20)
            self.powerSwitchProgBar.setRange(0, abs(self.info.syn_power + 20))
            self.powerSwitchProgBar.setValue(0)
            self.ramp_syn_rf_power()
            result = self.progDialog.exec()
            if self.prefs.is_test:
                self.ui.synPanel.synPowerSwitchBtn.setChecked(False)
            else:
                # RF protection before turn off
                self.info.synPower = api_syn.read_syn_power(self.handle)
                if result and (self.info.syn_power <= -20):
                    # safely turn off RF
                    api_syn.set_power_toggle(self.handle, False)
                    self.ui.synPanel.synPowerSwitchBtn.setChecked(False)
                else:
                    self.ui.synPanel.synPowerSwitchBtn.setChecked(True)
        else:  # user wants to turn off, power is already -20
            # safely turn off RF
            if self.prefs.is_test:
                pass
            else:
                api_syn.set_power_toggle(self.handle, False)
            self.ui.synPanel.synPowerSwitchBtn.setChecked(QtCore.Qt.CheckState.Unchecked)

        self.ui.synStatus.print_info(self.info)

