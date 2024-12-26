from PyQt6 import QtWidgets, QtCore
from PyMMSp.inst.base import INST_TYPES, INST_MODEL_DICT


class CtrlInsts(QtWidgets.QWidget):

    def __init__(self, prefs, ui, inst_handles, parent=None):
        super().__init__(parent)

        self.prefs = prefs
        self.ui = ui
        self.inst_handles = inst_handles

        # define and link instrument selection & configuration dialog behavior
        self.ui.dConnInst.dIndvInst.accepted.connect(self.on_config_indv_inst_accepted)
        self.ui.dConnInst.accepted.connect(self.on_sel_inst_dialog_accepted)
        # the linked names should agree with the names in the INST_MODEL_DICT
        self.ui.dConnInst.btnSyn.clicked.connect(lambda: self.on_inst_btn_clicked('Synthesizer'))
        self.ui.dConnInst.btnLockin.clicked.connect(lambda: self.on_inst_btn_clicked('Lock-in'))
        self.ui.dConnInst.btnAWG.clicked.connect(lambda: self.on_inst_btn_clicked('AWG'))
        self.ui.dConnInst.btnOscillo.clicked.connect(lambda: self.on_inst_btn_clicked('Oscilloscope'))
        self.ui.dConnInst.btnUCA.clicked.connect(lambda: self.on_inst_btn_clicked('Power Supply'))
        self.ui.dConnInst.btnFlow.clicked.connect(lambda: self.on_inst_btn_clicked('Flow Controller'))
        self.ui.dConnInst.btnGauge1.clicked.connect(lambda: self.on_inst_btn_clicked('Gauge Controller 1'))
        self.ui.dConnInst.btnGauge2.clicked.connect(lambda: self.on_inst_btn_clicked('Gauge Controller 2'))

    def on_inst_btn_clicked(self, inst_name):
        self.ui.dConnInst.dIndvInst.setWindowTitle('Configure ' + inst_name)
        self.ui.dConnInst.dIndvInst.comboInstModel.clear()
        self.ui.dConnInst.dIndvInst.comboInstModel.addItems(INST_MODEL_DICT[inst_name])
        self.ui.dConnInst.dIndvInst.exec()

    @QtCore.pyqtSlot()
    def on_config_indv_inst_accepted(self):
        """ Configure instrument """
        inst_type = self.ui.dConnInst.dIndvInst.windowTitle()
        connection_type = self.ui.dConnInst.dIndvInst.comboConnectionType.currentText()
        inst_addr = self.ui.dConnInst.dIndvInst.editInstAddr.text()
        inst_model = self.ui.dConnInst.dIndvInst.comboInstModel.currentText()
        print(inst_type, connection_type, inst_addr, inst_model)
        try:
            self.inst_handles.connect(inst_type, connection_type, inst_addr, inst_model)
        except (ValueError, ConnectionError) as e:
            self.ui.msgErr.setText(str(e))
            self.ui.msgErr.exec()
        self.ui.dConnInst.dIndvInst.accept()
        self.refresh(inst_type)

    @QtCore.pyqtSlot()
    def on_sel_inst_dialog_accepted(self):
        """ Select instrument """
        self.ui.dConnInst.close()

    def refresh_all_inst(self):
        """ Refresh the connection status of all instruments """
        self.inst_handles.refresh('Synthesizer')
        self.ui.dConnInst.lblConnSyn.setText(self.inst_handles.h_syn.addr)
        self.ui.dConnInst.statusSyn.setStatus(self.inst_handles.info_syn.conn_status)
        self.inst_handles.refresh('Lock-in')
        self.ui.dConnInst.lblConnLockin.setText(self.inst_handles.h_lockin.addr)
        self.ui.dConnInst.statusLockin.setStatus(self.inst_handles.info_lockin.conn_status)
        self.inst_handles.refresh('AWG')
        self.ui.dConnInst.lblConnAWG.setText(self.inst_handles.h_awg.addr)
        self.ui.dConnInst.statusAWG.setStatus(self.inst_handles.info_awg.conn_status)
        self.inst_handles.refresh('Oscilloscope')
        self.ui.dConnInst.lblConnOscillo.setText(self.inst_handles.h_oscillo.addr)
        self.ui.dConnInst.statusOscillo.setStatus(self.inst_handles.info_oscillo.conn_status)
        self.inst_handles.refresh('Power Supply')
        self.ui.dConnInst.lblConnUCA.setText(self.inst_handles.h_uca.addr)
        self.ui.dConnInst.statusUCA.setStatus(self.inst_handles.info_uca.conn_status)
        self.inst_handles.refresh('Flow Controller')
        self.ui.dConnInst.lblConnFlow.setText(self.inst_handles.h_flow.addr)
        self.ui.dConnInst.statusFlow.setStatus(self.inst_handles.info_flow.conn_status)
        self.inst_handles.refresh('Gauge Controller 1')
        self.ui.dConnInst.lblConnGauge1.setText(self.inst_handles.h_gauge1.addr)
        self.ui.dConnInst.statusGauge1.setStatus(self.inst_handles.info_gauge1.conn_status)
        self.inst_handles.refresh('Gauge Controller 2')
        self.ui.dConnInst.lblConnGauge2.setText(self.inst_handles.h_gauge2.addr)
        self.ui.dConnInst.statusGauge2.setStatus(self.inst_handles.info_gauge2.conn_status)

    def refresh(self, inst_type):
        """ Refresh the connection status of a particular instrument type """
        # communicate with instrument and write info into inst_info objects
        self.inst_handles.refresh(inst_type)
        # refresh the GUI components in the dialog window
        if inst_type == 'Synthesizer':
            self.ui.dConnInst.lblConnSyn.setText(self.inst_handles.h_syn.addr)
            self.ui.dConnInst.statusSyn.setStatus(self.inst_handles.info_syn.conn_status)
        elif inst_type == 'Lock-in':
            self.ui.dConnInst.lblConnLockin.setText(self.inst_handles.h_lockin.addr)
            self.ui.dConnInst.statusLockin.setStatus(self.inst_handles.info_lockin.conn_status)
        elif inst_type == 'AWG':
            self.ui.dConnInst.lblConnAWG.setText(self.inst_handles.h_awg.addr)
            self.ui.dConnInst.statusAWG.setStatus(self.inst_handles.info_awg.conn_status)
        elif inst_type == 'Oscilloscope':
            self.ui.dConnInst.lblConnOscillo.setText(self.inst_handles.h_oscillo.addr)
            self.ui.dConnInst.statusOscillo.setStatus(self.inst_handles.info_oscillo.conn_status)
        elif inst_type == 'Power Supply':
            self.ui.dConnInst.lblConnUCA.setText(self.inst_handles.h_uca.addr)
            self.ui.dConnInst.statusUCA.setStatus(self.inst_handles.info_uca.conn_status)
        elif inst_type == 'Flow Controller':
            self.ui.dConnInst.lblConnFlow.setText(self.inst_handles.h_flow.addr)
            self.ui.dConnInst.statusFlow.setStatus(self.inst_handles.info_flow.conn_status)
        elif inst_type == 'Gauge Controller 1':
            self.ui.dConnInst.lblConnGauge1.setText(self.inst_handles.h_gauge1.addr)
            self.ui.dConnInst.statusGauge1.setStatus(self.inst_handles.info_gauge1.conn_status)
        elif inst_type == 'Gauge Controller 2':
            self.ui.dConnInst.lblConnGauge2.setText(self.inst_handles.h_gauge2.addr)
            self.ui.dConnInst.statusGauge2.setStatus(self.inst_handles.info_gauge2.conn_status)

