from PyQt6 import QtWidgets, QtCore
from PyMMSp.inst.base import INST_TYPES, INST_MODEL_DICT


class CtrlInsts(QtWidgets.QWidget):

    def __init__(self, prefs, ui, inst_handles, parent=None):
        super().__init__(parent)

        self.prefs = prefs
        self.ui = ui
        self.inst_handles = inst_handles

        # define and link instrument selection & configuration dialog behavior
        self.ui.selInstDialog.dIndvInst.accepted.connect(self.on_config_indv_inst_accepted)
        self.ui.selInstDialog.accepted.connect(self.on_sel_inst_dialog_accepted)
        # the linked names should agree with the names in the INST_MODEL_DICT
        self.ui.selInstDialog.btnSyn.clicked.connect(lambda: self.on_inst_btn_clicked('Synthesizer'))
        self.ui.selInstDialog.btnLockin.clicked.connect(lambda: self.on_inst_btn_clicked('Lock-in'))
        self.ui.selInstDialog.btnAWG.clicked.connect(lambda: self.on_inst_btn_clicked('AWG'))
        self.ui.selInstDialog.btnOscillo.clicked.connect(lambda: self.on_inst_btn_clicked('Oscilloscope'))
        self.ui.selInstDialog.btnUCA.clicked.connect(lambda: self.on_inst_btn_clicked('Power Supply'))
        self.ui.selInstDialog.btnFlow.clicked.connect(lambda: self.on_inst_btn_clicked('Flow Controller'))
        self.ui.selInstDialog.btnGauge1.clicked.connect(lambda: self.on_inst_btn_clicked('Gauge Controller 1'))
        self.ui.selInstDialog.btnGauge2.clicked.connect(lambda: self.on_inst_btn_clicked('Gauge Controller 2'))

    def on_inst_btn_clicked(self, inst_name):
        self.ui.selInstDialog.dIndvInst.setWindowTitle('Configure ' + inst_name)
        self.ui.selInstDialog.dIndvInst.comboInstModel.clear()
        self.ui.selInstDialog.dIndvInst.comboInstModel.addItems(INST_MODEL_DICT[inst_name])
        self.ui.selInstDialog.dIndvInst.exec()

    @QtCore.pyqtSlot()
    def on_config_indv_inst_accepted(self):
        """ Configure instrument """
        inst_type = self.ui.selInstDialog.dIndvInst.windowTitle()
        connection_type = self.ui.selInstDialog.dIndvInst.comboConnectionType.currentText()
        inst_addr = self.ui.selInstDialog.dIndvInst.editInstAddr.text()
        inst_model = self.ui.selInstDialog.dIndvInst.comboInstModel.currentText()
        print(inst_type, connection_type, inst_addr, inst_model)
        try:
            self.inst_handles.connect(inst_type, connection_type, inst_addr, inst_model)
        except (ValueError, ConnectionError) as e:
            self.ui.msgErr.setText(str(e))
            self.ui.msgErr.exec()
        self.ui.selInstDialog.dIndvInst.accept()
        self.refresh(inst_type)

    @QtCore.pyqtSlot()
    def on_sel_inst_dialog_accepted(self):
        """ Select instrument """
        self.ui.selInstDialog.close()

    def refresh_all_inst(self):
        """ Refresh the connection status of all instruments """
        self.inst_handles.refresh('Synthesizer')
        self.ui.selInstDialog.lblConnSyn.setText(self.inst_handles.h_syn.addr)
        self.ui.selInstDialog.statusSyn.setStatus(self.inst_handles.info_syn.conn_status)
        self.inst_handles.refresh('Lock-in')
        self.ui.selInstDialog.lblConnLockin.setText(self.inst_handles.h_lockin.addr)
        self.ui.selInstDialog.statusLockin.setStatus(self.inst_handles.info_lockin.conn_status)
        self.inst_handles.refresh('AWG')
        self.ui.selInstDialog.lblConnAWG.setText(self.inst_handles.h_awg.addr)
        self.ui.selInstDialog.statusAWG.setStatus(self.inst_handles.info_awg.conn_status)
        self.inst_handles.refresh('Oscilloscope')
        self.ui.selInstDialog.lblConnOscillo.setText(self.inst_handles.h_oscillo.addr)
        self.ui.selInstDialog.statusOscillo.setStatus(self.inst_handles.info_oscillo.conn_status)
        self.inst_handles.refresh('Power Supply')
        self.ui.selInstDialog.lblConnUCA.setText(self.inst_handles.h_uca.addr)
        self.ui.selInstDialog.statusUCA.setStatus(self.inst_handles.info_uca.conn_status)
        self.inst_handles.refresh('Flow Controller')
        self.ui.selInstDialog.lblConnFlow.setText(self.inst_handles.h_flow.addr)
        self.ui.selInstDialog.statusFlow.setStatus(self.inst_handles.info_flow.conn_status)
        self.inst_handles.refresh('Gauge Controller 1')
        self.ui.selInstDialog.lblConnGauge1.setText(self.inst_handles.h_gauge1.addr)
        self.ui.selInstDialog.statusGauge1.setStatus(self.inst_handles.info_gauge1.conn_status)
        self.inst_handles.refresh('Gauge Controller 2')
        self.ui.selInstDialog.lblConnGauge2.setText(self.inst_handles.h_gauge2.addr)
        self.ui.selInstDialog.statusGauge2.setStatus(self.inst_handles.info_gauge2.conn_status)

    def refresh(self, inst_type):
        """ Refresh the connection status of a particular instrument type """
        # communicate with instrument and write info into inst_info objects
        self.inst_handles.refresh(inst_type)
        # refresh the GUI components in the dialog window
        if inst_type == 'Synthesizer':
            self.ui.selInstDialog.lblConnSyn.setText(self.inst_handles.h_syn.addr)
            self.ui.selInstDialog.statusSyn.setStatus(self.inst_handles.info_syn.conn_status)
        elif inst_type == 'Lock-in':
            self.ui.selInstDialog.lblConnLockin.setText(self.inst_handles.h_lockin.addr)
            self.ui.selInstDialog.statusLockin.setStatus(self.inst_handles.info_lockin.conn_status)
        elif inst_type == 'AWG':
            self.ui.selInstDialog.lblConnAWG.setText(self.inst_handles.h_awg.addr)
            self.ui.selInstDialog.statusAWG.setStatus(self.inst_handles.info_awg.conn_status)
        elif inst_type == 'Oscilloscope':
            self.ui.selInstDialog.lblConnOscillo.setText(self.inst_handles.h_oscillo.addr)
            self.ui.selInstDialog.statusOscillo.setStatus(self.inst_handles.info_oscillo.conn_status)
        elif inst_type == 'Power Supply':
            self.ui.selInstDialog.lblConnUCA.setText(self.inst_handles.h_uca.addr)
            self.ui.selInstDialog.statusUCA.setStatus(self.inst_handles.info_uca.conn_status)
        elif inst_type == 'Flow Controller':
            self.ui.selInstDialog.lblConnFlow.setText(self.inst_handles.h_flow.addr)
            self.ui.selInstDialog.statusFlow.setStatus(self.inst_handles.info_flow.conn_status)
        elif inst_type == 'Gauge Controller 1':
            self.ui.selInstDialog.lblConnGauge1.setText(self.inst_handles.h_gauge1.addr)
            self.ui.selInstDialog.statusGauge1.setStatus(self.inst_handles.info_gauge1.conn_status)
        elif inst_type == 'Gauge Controller 2':
            self.ui.selInstDialog.lblConnGauge2.setText(self.inst_handles.h_gauge2.addr)
            self.ui.selInstDialog.statusGauge2.setStatus(self.inst_handles.info_gauge2.conn_status)

