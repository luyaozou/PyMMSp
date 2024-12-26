#! encoding: UTF-8

from PyQt6 import QtWidgets
from PyMMSp.ui import ui_shared
from PyMMSp.inst import oscillo as api_oscillo


class CtrlOscillo(QtWidgets.QWidget):

    def __init__(self, prefs, ui, info, handle, parent=None):
        super().__init__(parent)

        self.prefs = prefs
        self.ui = ui
        self.info = info
        self.handle = handle

        ## -- Trigger setting status and communication
        # self.ui.oscilloPanel.srateFill.textChanged[str].connect(self.rate_comm)
        # self.ui.oscilloPanel.slenFill.textChanged[str].connect(self.len_comm)
        # self.ui.oscilloPanel.sensSel.currentIndexChanged[int].connect(self.tune_sensitivity)
        # self.ui.oscilloPanel.avgFill.textChanged[str].connect(self.avg_comm)
        # self.ui.oscilloPanel.clicked.connect(self.check)

    def check(self):
        """ Enable/disable this groupbox """

        if self.prefs.is_test or self.handle:
            self.ui.oscilloPanel.setChecked(True)
            self.ui.scopeStatus.setChecked(True)
        else:
            msg = ui_shared.MsgError(self, 'No Instrument!', 'No PCI card is connected!')
            msg.exec()
            self.ui.oscilloPanel.setChecked(False)
            self.ui.scopeStatus.setChecked(False)

    def manual_refresh(self):
        """ refresh instrument information """

        if self.handle:
            self.info.inst_name = api_oscillo.query_inst_name(self.handle)
        else:
            self.info.inst_name = 'N.A.'
        self.ui.scopeStatus.print_info(self.info)

    def rate_comm(self, rate_txt):

        status = api_oscillo.set_sampling_rate(rate_txt)
        self.ui.oscilloPanel.srateFill.setStyleSheet(f'border: 1px solid {ui_shared.msg_color(status)}')

    def len_comm(self, len_txt):

        status = api_oscillo.set_sampling_len(len_txt)
        self.ui.oscilloPanel.slenFill.setStyleSheet(f'border: 1px solid {ui_shared.msg_color(status)}')

    def tune_sensitivity(self, sens_idx):

        status = api_oscillo.set_sensitivity(sens_idx)
        self.ui.oscilloPanel.comboSens.setStyleSheet(f'border: 1px solid {ui_shared.msg_color(status)}')

    def avg_comm(self, avg_txt):

        status = api_oscillo.set_osc_avg(avg_txt)
        self.ui.oscilloPanel.avgFill.setStyleSheet(f'border: 1px solid {ui_shared.msg_color(status)}')

