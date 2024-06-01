#! encoding: UTF-8

from PyQt6 import QtWidgets
from PyMMSp.ui import ui_shared
from PyMMSp.inst import motor as api_motor


class CtrlMotor(QtWidgets.QWidget):

    def __init__(self, prefs, ui, info, handle, parent=None):
        super().__init__(parent)

        self.prefs = prefs
        self.ui = ui
        self.info = info
        self.handle = handle

        self.ui.motorPanel.clicked.connect(self.check)
        self.ui.motorPanel.tuneButton.clicked.connect(self.tune_cavity)

    def check(self):
        if self.prefs.is_test or self.handle:
            self.ui.motorPanel.setChecked(True)
        else:
            msg = ui_shared.MsgError(self, 'No Instrument!', 'No oscilloscope is connected!')
            msg.exec()
            self.ui.motorPanel.setChecked(False)

    def tune_cavity(self):

        pass
