#! encoding = utf-8
""" Main GUI Window """
import queue
import datetime
from os.path import isfile

from PyQt6 import QtCore, QtWidgets
from importlib.resources import files

import PyMMSp.ui.ui_daq
from PyMMSp.ui import ui_daq
from PyMMSp.ui import ui_main
from PyMMSp.ui import ui_dialog
from PyMMSp.ui import ui_menu
from PyMMSp.ui import ui_shared
from PyMMSp.daq import abs
from PyMMSp.inst.base import Handles, Threads
from PyMMSp.inst import lockin as api_lia
from PyMMSp.inst import base as api_gen
from PyMMSp.inst import synthesizer as api_syn
from PyMMSp.inst import oscillo as api_oscillo
from PyMMSp.inst import motor as api_motor
from PyMMSp.inst import gauge as api_gauge
from PyMMSp.ctrl import (ctrl_syn,
                         ctrl_lockin,
                         ctrl_oscillo,
                         ctrl_motor,
                         ctrl_gauge,
                         ctrl_insts,
                         ctrl_flow,
                         )
from PyMMSp.daq import (abs,
                        )
from PyMMSp.config import config


class MainWindow(QtWidgets.QMainWindow):
    """ Implements the main window """

    def __init__(self):
        super().__init__()

        # Set global window properties
        self.setWindowTitle('Yo! Go PyMMSp!')
        self.setMinimumWidth(1500)
        self.setMinimumHeight(840)
        self.prefs = config.Prefs()
        # Initiate instrument objects
        self.inst_handles = Handles()
        # initialise working threads for each instrument.
        # each instrument has its own working thread so that all communications
        # to this instrument is not blocked by other communications
        self.threads = Threads()

        # set default geometry
        screen = QtWidgets.QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        # Check screen resolution
        if screen_geometry.width() > 1600 and screen_geometry.height() > 900:
            # Set window size to 1600x900
            self.setGeometry(0, 0, 1600, 900)
        else:
            # Set window to full screen size
            self.setGeometry(screen_geometry)
        # Center the window
        qr = self.frameGeometry()
        cp = screen_geometry.center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

        f = files('PyMMSp.config').joinpath('prefs.json')
        if f.is_file():
            config.from_json_(self.prefs, f)
        self.setGeometry(QtCore.QRect(*self.prefs.geometry))

        # Set menu bar
        self.menuBar = ui_menu.MenuBar(self)
        self.setMenuBar(self.menuBar)

        # Set main window widgets
        self.ui = ui_main.MainUI(self)
        self.setCentralWidget(self.ui)

        # controller of instruments
        self.ctrl_insts = ctrl_insts.CtrlInsts(
            self.prefs, self.ui, self.inst_handles, parent=self)
        self.ctrl_syn = ctrl_syn.CtrlSyn(
            self.prefs, self.ui, self.inst_handles.info_syn, self.inst_handles.h_syn, parent=self)
        self.ctrl_syn_pow = ctrl_syn.CtrlSynPower(
            self.prefs, self.ui, self.inst_handles.info_syn, self.inst_handles.h_syn, parent=self)
        #self.ctrl_lockin = ctrl_lockin.CtrlLockin(
        #    self.prefs, self.ui, self.inst_handles.info_lockin, self.inst_handles.h_lockin, parent=self)
        self.ctrl_oscillo = ctrl_oscillo.CtrlOscillo(
            self.prefs, self.ui, self.inst_handles.info_oscillo, self.inst_handles.h_oscillo, parent=self)
        #self.ctrl_motor = ctrl_motor.CtrlMotor(
        #    self.prefs, self.ui, self.inst_handles.info_mo, self.motor_handle, parent=self)
        self.ctrl_gauge = ctrl_gauge.CtrlGauge(
            self.prefs, self.ui, self.inst_handles.info_gauge1, self.inst_handles.h_gauge1, parent=self)
        self.ctrl_flow = ctrl_flow.CtrlFlow(
            self.prefs, self.ui, self.inst_handles.h_flow, parent=self)
        # controller of scanning routines
        self.ctrl_abs_bb = abs.CtrlAbsBBScan(
            self.prefs, self.ui, self.inst_handles, self.threads, parent=self)

        # connect menubar signals
        self.menuBar.instSelAction.triggered.connect(self.on_sel_inst)
        self.menuBar.instCloseAction.triggered.connect(self.on_close_sel_inst)
        self.menuBar.scanAbsAction.triggered.connect(self.ui.dAbsScan.exec)
        self.menuBar.scanCEAction.triggered.connect(self.on_scan_cavity)
        self.menuBar.lwaParserAction.triggered.connect(self.on_lwa_parser)

        self.ui.synPanel.comboMonitor.currentIndexChanged[int].connect(self.connect2monitor_syn)
        self.ui.lockinPanel.comboMonitor.currentIndexChanged[int].connect(self.connect2monitor_lockin)
        self.ui.oscilloPanel.comboMonitor.currentIndexChanged[int].connect(self.connect2monitor_oscillo)
        self.ui.motorPanel.comboMonitor.currentIndexChanged[int].connect(self.connect2monitor_motor)
        self.ui.gaugePanel.comboMonitor.currentIndexChanged[int].connect(self.connect2monitor_gauge)
        self.ui.flowPanel.comboMonitor.currentIndexChanged[int].connect(self.connect2monitor_flow)
        self.ui.dcPanel.comboMonitor.currentIndexChanged[int].connect(self.connect2monitor_dc)
        self.ui.awgPanel.comboMonitor.currentIndexChanged[int].connect(self.connect2monitor_awg)

    def refresh_inst(self):

        if self.menuBar.testModeAction.isChecked():
            self.setWindowTitle('Yo! Go PyMMSp! [TEST MODE]')
            # self.statusBar.testModeLabel.show()
            self.ui.synPanel.setChecked(True)
            self.ui.lockinPanel.setChecked(True)
            self.ui.oscilloPanel.setChecked(True)
            self.ui.motorPanel.setChecked(True)
        else:
            self.setWindowTitle('Yo! Go PyMMSp!')
            self.statusBar.testModeLabel.hide()
            self.ui.synPanel.setChecked(not (self.syn_handle is None))
            self.ui.lockinPanel.setChecked(not (self.lockin_handle is None))
            self.ui.oscilloPanel.setChecked(not (self.oscillo_handle is None))
            self.ui.motorPanel.setChecked(not (self.motor_handle is None))
            self.ui.synStatus.setChecked(not (self.syn_handle is None))
            self.ui.liaStatus.setChecked(not (self.lockin_handle is None))
            self.ui.scopeStatus.setChecked(not (self.oscillo_handle is None))

        self.ctrl_syn.refresh()
        self.ctrl_lockin.manual_refresh()
        self.ctrl_oscillo.manual_refresh()

    def on_sel_inst(self):
        result = self.ui.dConnInst.exec()
        if result:
            # simply uncheck main to prevent the warning dialog
            if self.inst_handles.h_syn:
                api_syn.init_syn(self.inst_handles.h_syn)
                # check RF toggle state
                toggle_state = api_syn.read_power_toggle(self.inst_handles.h_syn)
                self.ui.synPanel.synPowerSwitchBtn.setChecked(toggle_state)
            else:
                pass
            if self.inst_handles.h_lockin:
                api_lia.init_lia(self.inst_handles.h_lockin)
            else:
                pass
            self.refresh_inst()
        else:
            pass

    def on_close_sel_inst(self):

        self.ui.dCloseInst.exec()
        # simply uncheck main to prevent the warning dialog
        self.refresh_inst()

    def on_scan_pci(self):
        d = ui_dialog.DialogOscillo(self)
        d.exec()

    def on_scan_cavity(self):
        pass

    def on_lwa_parser(self):
        """ Launch lwa parser dialog window """

        filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, 'Open LWA File', './default.lwa', 'SMAP Data File (*.lwa)')

        d = ui_dialog.LWAParserDialog(self, filename)
        d.exec()

    def closeEvent(self, ev):
        # q = QtWidgets.QMessageBox.question(
        #     self, 'Quit?', 'Are you sure to quit?',
        #     QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
        #     QtWidgets.QMessageBox.StandardButton.Yes)
        # if q == QtWidgets.QMessageBox.StandardButton.Yes:
        #     # save settings
        #     self.prefs.geometry = self.geometry().getRect()
        #     f = files('PyMMSp.config').joinpath('prefs.json')
        #     config.to_json(self.prefs, f)
        #     self.inst_handles.close_all()
        # else:
        #     ev.ignore()
        self.prefs.geometry = self.geometry().getRect()
        f = files('PyMMSp.config').joinpath('prefs.json')
        config.to_json(self.prefs, f)
        # close working threads
        self.threads.join_all()
        self.inst_handles.close_all()

    def connect2monitor_syn(self, id_):
        pass

    def connect2monitor_lockin(self, id_):
        pass

    def connect2monitor_oscillo(self, id_):
        pass

    def connect2monitor_motor(self, id_):
        pass

    def connect2monitor_gauge(self, id_):
        pass

    def connect2monitor_flow(self, id_):
        pass

    def connect2monitor_dc(self, id_):
        pass

    def connect2monitor_awg(self, id_):
        pass
