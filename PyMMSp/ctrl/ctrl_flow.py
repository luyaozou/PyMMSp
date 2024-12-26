#! utf-8

from PyQt6 import QtWidgets, QtCore
from PyMMSp.ui.ui_shared import msg
from PyMMSp.inst import flow as api_flow


class CtrlFlow(QtWidgets.QWidget):
    """ Controller for gas flow, mainly MKS flow controller
    The setting & synchronization is complicated, so we take it out alone and
    not put it together with other handle control
    """

    _timer = QtCore.QTimer()
    _timer.setInterval(1000)
    _timer.setSingleShot(False)

    def __init__(self, panel_cfg, ui, h, parent=None):
        super().__init__(parent)

        self.ui = ui
        self.h = h
        self.panel_cfg = panel_cfg

        ui.dFlow.btnGroup.idClicked[int].connect(self._commit_mks_general)
        ui.dFlow.boxChn1.btnGroup.idClicked[int].connect(self._commit_mks_chn1)
        ui.dFlow.boxChn2.btnGroup.idClicked[int].connect(self._commit_mks_chn2)
        ui.dFlow.btnRefresh.clicked.connect(self._refresh_all_mks_setting)
        ui.dFlow.boxChn1.btnZero.clicked.connect(lambda: self._zero_mks_chn(1))
        ui.dFlow.boxChn2.btnZero.clicked.connect(lambda: self._zero_mks_chn(2))
        ui.dFlow.btnGCF.clicked.connect(ui.dGCF.show)
        ui.dFlow.btnGCF.clicked.connect(ui.dGCF.raise_)
        ui.dGCF.sig_calc_gcf.connect(self._calc_gcf)

    def closeEvent(self, ev):
        self._timer.stop()

    def _switch_flow_mode(self):
        if self.ui.boxPulsedValve.ckBubbler.isChecked():
            self.ui.boxPulsedValve.gasBoxBubbler.show()
            self.ui.boxPulsedValve.gasBoxFlow.hide()
            self.ui.boxPulsedValve.inpPbk.setDisabled(True)
            self._timer.stop()
        else:
            self.ui.boxPulsedValve.gasBoxBubbler.hide()
            self.ui.boxPulsedValve.gasBoxFlow.show()
            self.ui.boxPulsedValve.inpPbk.setDisabled(False)
            self._timer.start()

    def _switch_jet_mode(self):
        """ Stop updating flow reading if jet mode is disabled """
        if self.ui.boxPulsedValve.isChecked():
            self._switch_flow_mode()
        else:
            self._timer.stop()

    def _update_pbk(self):
        self.ui.boxPulsedValve.inpPbk.setValue(self.ui.boxPulsedValve.gasBoxBubbler.get_pbk())

    def _refresh_all_mks_setting(self):
        self._timer.stop()
        for cmd, lbl in self.ui.dFlow.yield_all():
            if lbl:
                lbl.setText(self.h.query(cmd))
        for cmd, lbl in self.ui.dFlow.boxChn1.yield_all():
            lbl.setText(self.h.query(cmd))
        for cmd, lbl in self.ui.dFlow.boxChn2.yield_all():
            lbl.setText(self.h.query(cmd))
        self._timer.start()

    def _commit_mks_general(self, btn_id):
        self._timer.stop()
        cmd, param = self.ui.dFlow.mks_cmd(btn_id)
        ans = self.h.set(cmd, param)
        self.ui.dFlow.update_current(btn_id, ans)
        self._timer.start()

    def _commit_mks_chn1(self, btn_id):
        self._timer.stop()
        cmd, param = self.ui.dFlow.boxChn1.mks_cmd(btn_id)
        ans = self.h.set(cmd, param)
        self.ui.dFlow.boxChn1.update_current(btn_id, ans)
        self._timer.start()

    def _commit_mks_chn2(self, btn_id):
        self._timer.stop()
        cmd, param = self.ui.dFlow.boxChn2.mks_cmd(btn_id)
        ans = self.h.set(cmd, param)
        self.ui.dFlow.boxChn2.update_current(btn_id, ans)
        self._timer.start()

    def _zero_mks_chn(self, chn_id):
        self._timer.stop()
        # check if flow reading is less than 5% of full scale
        flow = self.h.query('FR{:d}'.format(chn_id))
        full = self.h.query('QSF{:d}'.format(chn_id))
        try:
            if float(flow) < 0.05 * float(full):
                self.h.set('QZ{:d}'.format(chn_id), '')
            else:
                msg(title='Cannot Zero', style='critical',
                    context='Current flow reading exceeds 5% of full scale')
        except ValueError:
            pass
        self._timer.start()

    def _commit_mks_flow_mode(self, btn):
        """ Commit the MKS flow mode for all channels
        :argument
            mode: str       flow mode:
                'Open'      fully open the valve
                'Close'     fully close the valve
                'SetPoint'     set point mode
        """
        self._timer.stop()
        mode = btn.text()
        for i in range(self.ui.boxPulsedValve.gasBoxFlow.chn):
            self.h.set('QMD{:d}'.format(i+1), mode)    # channel starts at 1
        self._timer.start()

    def _read_flow(self):
        try:
            fr1 = self.h.query('FR1')
        except AttributeError as err:
            fr1 = str(err)
        try:
            fr2 = self.h.query('FR2')
        except AttributeError as err:
            fr2 = str(err)
        self.ui.boxPulsedValve.gasBoxFlow.update_flow_reading((fr1, fr2))
        self.ui.dFlow.update_flow_reading((fr1, fr2))

    def _calc_gcf(self):
        """ Calculate GCF flow scaling factor """
        t = self.ui.dGCF.inpTemperature.value()
        frac_s = 0
        frac_rho_cp = 0
        for struc, frac, rho, cp in self.ui.dGCF.yield_entry_params():
            frac_s += frac * struc
            frac_rho_cp += frac * rho * cp
        try:
            gcf = 0.3016 * frac_s / frac_rho_cp * t / 273
        except ZeroDivisionError:
            gcf = float('nan')
        self.ui.dGCF.lblGCF.setText('{:.2f}'.format(gcf))
