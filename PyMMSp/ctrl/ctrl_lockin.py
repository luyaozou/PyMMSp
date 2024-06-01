#! encoding = utf-8

from PyQt6 import QtWidgets
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

        ## -- Trigger setting status and communication
        self.ui.lockinPanel.phaseFill.textChanged.connect(self.tune_phase)
        self.ui.lockinPanel.harmSel.currentTextChanged[str].connect(self.tune_harmonics)
        self.ui.lockinPanel.tcSel.currentIndexChanged[int].connect(self.tune_time_const)
        self.ui.lockinPanel.sensSel.currentIndexChanged[int].connect(self.tune_sensitivity)
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
        self.ui.liaStatus.moreInfoButton.clicked.connect(self.ui.liaInfoDialog.show)
        self.ui.liaInfoDialog.refreshButton.clicked.connect(self.dialog_manual_refresh)

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
        self.ui.lockinPanel.phaseFill.setStyleSheet(f'border: 1px solid {ui_shared.msgcolor(status)}')

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
        self.ui.liaMonitor.set_waittime()

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
            self.ui.lockinPanel.sensSel.setCurrentIndex(self.info.sens_idx)
            self.ui.lockinPanel.tcSel.setCurrentIndex(self.info.tau_idx)
            self.ui.lockinPanel.coupleSel.setCurrentIndex(self.info.couple_idx)
            self.ui.lockinPanel.reserveSel.setCurrentIndex(self.info.reserve_idx)
            self.ui.liaMonitor.set_waittime()

    def pop_err_msg(self):
        """ Pop error message """
        if self.handle:
            self.ui.liaStatus.errMsgLabel.setText(api_lia.query_err_msg(self.handle))
        else:
            pass

    def dialog_manual_refresh(self):

        api_lia.full_info_query_(self.info, self.handle)
        self.ui.liaInfoDialog.print_info(self.info)
