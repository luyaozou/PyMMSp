#! encoding = utf-8
""" Main GUI Window """

import datetime
from os.path import isfile

from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import Qt
from importlib.resources import files
from PyMMSp.ui import ui_main
from PyMMSp.ui import ui_dialog
from PyMMSp.ui import ui_menu
from PyMMSp.ui import ui_shared
from PyMMSp.daq import JPLScan
from PyMMSp.inst.base import Handles
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

        # Initiate pyvisa instrument objects
        self.syn_handle = None
        self.lockin_handle = None
        self.oscillo_handle = None
        self.motor_handle = None
        self.gauge_handle = None

        # Set menu bar
        self.menuBar = ui_menu.MenuBar(self)
        self.setMenuBar(self.menuBar)
        self.statusBar = ui_menu.StatusBar(self)
        self.setStatusBar(self.statusBar)

        # Set classes to store all instrument info
        self.syn_info = api_syn.Syn_Info()
        self.lockin_info = api_lia.Lockin_Info()
        self.oscillo_info = api_oscillo.Oscilloscope_Info()
        self.motor_info = api_motor.Motor_Info()
        self.gauge_info = api_gauge.Gauge_Info()

        # Set main window widgets
        self.ui = ui_main.MainUI(self)
        self.setCentralWidget(self.ui)

        self.ctrl_insts = ctrl_insts.CtrlInsts(
            self.prefs, self.ui, self.inst_handles, parent=self)
        self.ctrl_syn = ctrl_syn.CtrlSyn(
            self.prefs, self.ui, self.syn_info, self.syn_handle, parent=self)
        self.ctrl_syn_pow = ctrl_syn.CtrlSynPower(
            self.prefs, self.ui, self.syn_info, self.syn_handle, parent=self)
        self.ctrl_lockin = ctrl_lockin.CtrlLockin(
            self.prefs, self.ui, self.lockin_info, self.lockin_handle, parent=self)
        self.ctrl_oscillo = ctrl_oscillo.CtrlOscillo(
            self.prefs, self.ui, self.oscillo_info, self.oscillo_handle, parent=self)
        self.ctrl_motor = ctrl_motor.CtrlMotor(
            self.prefs, self.ui, self.motor_info, self.motor_handle, parent=self)
        self.ctrl_gauge = ctrl_gauge.CtrlGauge(
            self.prefs, self.ui, self.gauge_info, self.gauge_handle, parent=self)
        self.ctrl_insts = ctrl_insts.CtrlInsts(
            self.prefs, self.ui, self.inst_infos, self.inst_handles, parent=self)
        self.refresh_inst()

        # connect menubar signals
        self.menuBar.exitAction.triggered.connect(self.on_exit)
        self.menuBar.instSelAction.triggered.connect(self.on_sel_inst)
        self.menuBar.instStatViewAction.triggered.connect(self.ui.viewInstDialog.show)
        self.menuBar.instCloseAction.triggered.connect(self.on_close_sel_inst)
        self.menuBar.scanJPLAction.triggered.connect(self.on_scan_jpl)
        self.menuBar.viewOscilloAction.triggered.connect(self.ui.oscilloDialog.exec)
        self.menuBar.scanCavityAction.triggered.connect(self.on_scan_cavity)
        self.menuBar.gaugeAction.triggered.connect(self.ui.gaugeDialog.show)
        self.menuBar.lwaParserAction.triggered.connect(self.on_lwa_parser)
        self.menuBar.testModeAction.toggled.connect(self.refresh_inst)

    def refresh_inst(self):

        if self.menuBar.testModeAction.isChecked():
            self.setWindowTitle('Yo! Go PyMMSp! [TEST MODE]')
            self.statusBar.testModeLabel.show()
            self.ui.synPanel.setChecked(True)
            self.ui.lockinPanel.setChecked(True)
            self.ui.oscilloPanel.setChecked(True)
            self.ui.motorPanel.setChecked(True)
            self.ui.synStatus.setChecked(True)
            self.ui.liaStatus.setChecked(True)
            self.ui.scopeStatus.setChecked(True)
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
        result = self.ui.selInstDialog.exec()
        if result:
            # simply uncheck main to prevent the warning dialog
            if self.syn_handle:
                api_syn.init_syn(self.syn_handle)
                # check RF toggle state
                toggle_state = api_syn.read_power_toggle(self.syn_handle)
                self.ui.synPanel.synPowerSwitchBtn.setChecked(toggle_state)
            else:
                pass
            if self.lockin_handle:
                api_lia.init_lia(self.lockin_handle)
            else:
                pass
            self.refresh_inst()
        else:
            pass

    def on_close_sel_inst(self):

        self.ui.closeSelInstDialog.exec()
        # simply uncheck main to prevent the warning dialog
        self.refresh_inst()

    def on_scan_jpl(self):

        # when invoke this dialog, pause live lockin monitor in the main panel
        self.ui.liaMonitor.stop()

        # if it is test mode, or real-run mode with instrument correctly connected
        if self.menuBar.testModeAction.isChecked() or (self.syn_handle and self.lockin_handle):
            dconfig = JPLScan.JPLScanConfig(main=self)
            entry_settings = None
            dconfig_result = dconfig.exec()
        else:
            # instrument handle is None, pop up error
            msg = ui_shared.MsgError(self, 'Instrument Offline!',
                                  'Connect to the synthesizer and lockin first before proceed.')
            msg.exec()
            return None

        # this loop makes sure the config dialog does not disappear
        # unless the settings are all valid / or user hits cancel
        while dconfig_result:  # if dialog accepted
            entry_settings, filename = dconfig.get_settings()
            if entry_settings:
                total_time = ui_shared.jpl_scan_time(entry_settings)
                now = datetime.datetime.today()
                length = datetime.timedelta(seconds=total_time)
                then = now + length
                text = 'This batch job is estimated to take {:s}.\nIt is expected to finish at {:s}.'.format(
                    str(length), then.strftime('%I:%M %p, %m-%d-%Y (%a)'))
                q = ui_shared.MsgInfo(self, 'Time Estimation', text)
                q.addButton(QtWidgets.QMessageBox.StandardButton.Cancel)
                qres = q.exec()
                if qres == QtWidgets.QMessageBox.StandardButton.Ok:
                    break
                else:
                    dconfig_result = dconfig.exec()
            else:
                dconfig_result = dconfig.exec()

        if entry_settings and dconfig_result:
            dscan = JPLScan.JPLScanWindow(entry_settings, filename, main=self)
            dscan.exec()
        else:
            pass

    def on_scan_pci(self):
        d = ui_dialog.OscilloscopeDialog(self)
        d.exec()

    def on_scan_cavity(self):
        pass

    def on_lwa_parser(self):
        """ Launch lwa parser dialog window """

        filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, 'Open LWA File', './default.lwa', 'SMAP Data File (*.lwa)')

        d = ui_dialog.LWAParserDialog(self, filename)
        d.exec()

    def closeEvent(self, event):
        q = QtWidgets.QMessageBox.question(
            self, 'Quit?', 'Are you sure to quit?',
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
            QtWidgets.QMessageBox.StandardButton.Yes)
        if q == QtWidgets.QMessageBox.StandardButton.Yes:
            # save settings
            self.prefs.geometry = (self.x(), self.y(), self.width(), self.height())
            f = abs_path('PyMMSp.config', 'prefs.json')
            config.to_json(self.prefs, f)
            status = api_gen.close_inst(self.syn_handle, self.lockin_handle,
                                        self.oscillo_handle, self.motor_handle)
            if not status:  # safe to close
                self.close()
            else:
                qq = QtWidgets.QMessageBox.question(
                    self, 'Error', 'Error in disconnecting instruments. Are you sure to force quit?',
                    QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
                    QtWidgets.QMessageBox.StandardButton.No)
                if qq == QtWidgets.QMessageBox.StandardButton.Yes:
                    self.close()
                else:
                    event.ignore()
        else:
            event.ignore()

    def on_exit(self):
        self.close()

