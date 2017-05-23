#! encoding = utf-8
''' Main GUI Window '''

from PyQt5 import QtCore, QtGui
import datetime
from gui import SharedWidgets as Shared
from gui import Panels
from gui import Dialogs
from daq import ScanLockin
from daq import PresReader
from api import general as api_gen
from api import synthesizer as api_syn
from api import lockin as api_lia


class MainWindow(QtGui.QMainWindow):
    '''
        Implements the main window
    '''
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self)

        # Set global window properties
        self.setWindowTitle('Yo! Go PySpec!')
        self.setMinimumWidth(1500)
        self.setMinimumHeight(840)
        self.testModeSignLabel = QtGui.QLabel('[TEST MODE ACTIVE -- NOTHING IS REAL]!')
        self.testModeSignLabel.setStyleSheet('color: {:s}'.format(Shared.msgcolor(0)))
        self.testModeSignLabel.setAlignment(QtCore.Qt.AlignCenter)

        # Initiate pyvisa instrument objects
        self.synHandle = None
        self.liaHandle = None
        self.pciHandle = None
        self.motorHandle = None
        self.pressureHandle = None

        # Set menu bar actions
        exitAction = QtGui.QAction('Exit', self)
        exitAction.setShortcuts(['Ctrl+Q', 'Esc'])
        exitAction.setStatusTip('Exit program')
        exitAction.triggered.connect(self.on_exit)

        # instrument actions
        instSelAction = QtGui.QAction('Select Instrument', self)
        instSelAction.setShortcut('Ctrl+Shift+I')
        instSelAction.setStatusTip('Select instrument')
        instSelAction.triggered.connect(self.on_sel_inst)

        instStatViewAction = QtGui.QAction('View Instrument Status', self)
        instStatViewAction.setShortcut('Ctrl+Shift+V')
        instStatViewAction.setStatusTip('View status of currently connected instrument')
        instStatViewAction.triggered.connect(self.on_view_inst_stat)

        instCloseAction = QtGui.QAction('Close Instrument', self)
        instCloseAction.setStatusTip('Close individual instrument')
        instCloseAction.triggered.connect(self.on_close_sel_inst)

        # scan actions
        scanJPLAction = QtGui.QAction('JPL Scanning Routine', self)
        scanJPLAction.setShortcut('Ctrl+Shift+J')
        scanJPLAction.setStatusTip('Use the scanning style of the JPL scanning routine')
        scanJPLAction.triggered.connect(self.on_scan_jpl)

        scanPCIAction = QtGui.QAction('PCI Oscilloscope', self)
        scanPCIAction.setShortcut('Ctrl+Shift+S')
        scanPCIAction.setStatusTip("Use the scanning style of Brian's NIPCI card routine")
        scanPCIAction.triggered.connect(self.on_scan_pci)

        scanCavityAction = QtGui.QAction('Cavity Enhanced', self)
        scanCavityAction.setShortcut('Ctrl+Shift+C')
        scanCavityAction.setStatusTip('Use cavity enhanced spectroscopy')
        scanCavityAction.triggered.connect(self.on_scan_cavity)

        presReaderAction = QtGui.QAction('Pressure Reader', self)
        presReaderAction.setShortcut('Ctrl+Shift+P')
        presReaderAction.setStatusTip('Record pressure measurements using the CENTER TWO pressure readout')
        presReaderAction.triggered.connect(self.on_pres_reader)

        # data process actions
        lwaParserAction = QtGui.QAction('.lwa preview and export', self)
        lwaParserAction.setStatusTip('Preview JPL .lwa file and export subset of scans')
        lwaParserAction.triggered.connect(self.on_lwa_parser)

        self.testModeAction = QtGui.QAction('Test Mode', self)
        self.testModeAction.setCheckable(True)
        self.testModeAction.setShortcut('Ctrl+T')
        self.testModeAction.setWhatsThis('Toggle the test mode to bypass all instrument communication for GUI development.')

        # Set menu bar
        self.statusBar()

        menuFile = self.menuBar().addMenu('&File')
        menuFile.addAction(exitAction)
        menuInst = self.menuBar().addMenu('&Instrument')
        menuInst.addAction(instSelAction)
        menuInst.addAction(instStatViewAction)
        menuInst.addAction(instCloseAction)
        menuScan = self.menuBar().addMenu('&Scan')
        menuScan.addAction(scanJPLAction)
        menuScan.addAction(scanPCIAction)
        menuScan.addAction(scanCavityAction)
        menuScan.addAction(presReaderAction)
        menuData = self.menuBar().addMenu('&Data')
        menuData.addAction(lwaParserAction)
        menuTest = self.menuBar().addMenu('&Test')
        menuTest.addAction(self.testModeAction)

        # Set classes to store all instrument info
        self.synInfo = Shared.SynInfo()
        self.liaInfo = Shared.LiaInfo()
        self.scopeInfo = Shared.ScopeInfo()
        self.motorInfo = Shared.MotorInfo()

        # Set main window widgets
        self.synStatus = Panels.SynStatus(self)
        self.liaStatus = Panels.LockinStatus(self)
        self.scopeStatus = Panels.ScopeStatus(self)
        self.synCtrl = Panels.SynCtrl(self)
        self.liaCtrl = Panels.LockinCtrl(self)
        self.scopeCtrl = Panels.ScopeCtrl(self)
        self.motorCtrl = Panels.MotorCtrl(self)
        self.scopeMonitor = Panels.ScopeMonitor(self)
        self.liaMonitor = Panels.LockinMonitor(self)
        self.specMonitor = Panels.SpectrumMonitor(self)

        # Set main window layout
        self.mainLayout = QtGui.QGridLayout()
        self.mainLayout.setSpacing(6)
        self.mainLayout.addWidget(self.synStatus, 0, 0, 3, 2)
        self.mainLayout.addWidget(self.liaStatus, 3, 0, 3, 2)
        self.mainLayout.addWidget(self.scopeStatus, 6, 0, 1, 2)
        self.mainLayout.addWidget(self.testModeSignLabel, 7, 0, 1, 2)
        self.mainLayout.addWidget(self.synCtrl, 0, 2, 3, 3)
        self.mainLayout.addWidget(self.liaCtrl, 3, 2, 2, 3)
        self.mainLayout.addWidget(self.scopeCtrl, 5, 2, 2, 3)
        self.mainLayout.addWidget(self.motorCtrl, 7, 2, 1, 3)
        self.mainLayout.addWidget(self.scopeMonitor, 0, 5, 2, 4)
        self.mainLayout.addWidget(self.liaMonitor, 2, 5, 4, 4)
        self.mainLayout.addWidget(self.specMonitor, 6, 5, 2, 4)

        # Enable main window
        self.mainWidget = QtGui.QWidget()
        self.mainWidget.setLayout(self.mainLayout)
        self.setCentralWidget(self.mainWidget)

        # Preload system dialog widgets
        self.load_dialogs()
        self.refresh_inst()
        self.testModeAction.toggled.connect(self.refresh_inst)

    def refresh_inst(self):

        if self.testModeAction.isChecked():
            self.setWindowTitle('Yo! Go PySpec! [TEST MODE]')
            self.testModeSignLabel.show()
            self.synCtrl.setChecked(True)
            self.liaCtrl.setChecked(True)
            self.scopeCtrl.setChecked(True)
            self.motorCtrl.setChecked(True)
            self.synStatus.setChecked(True)
            self.liaStatus.setChecked(True)
            self.scopeStatus.setChecked(True)
        else:
            self.setWindowTitle('Yo! Go PySpec!')
            self.testModeSignLabel.hide()
            self.synCtrl.setChecked(not(self.synHandle is None))
            self.liaCtrl.setChecked(not(self.liaHandle is None))
            self.scopeCtrl.setChecked(not(self.pciHandle is None))
            self.motorCtrl.setChecked(not(self.motorHandle is None))
            self.synStatus.setChecked(not(self.synHandle is None))
            self.liaStatus.setChecked(not(self.liaHandle is None))
            self.scopeStatus.setChecked(not(self.pciHandle is None))

        self.synStatus.manual_refresh()
        self.liaStatus.manual_refresh()
        self.scopeStatus.manual_refresh()

    def load_dialogs(self):
        ''' Load dialog widgets without showing them '''

        self.selInstDialog = Dialogs.SelInstDialog(self)
        self.viewInstDialog = Dialogs.ViewInstDialog(self)
        self.synInfoDialog = Dialogs.SynInfoDialog(self)
        self.liaInfoDialog = Dialogs.LockinInfoDialog(self)

    def on_exit(self):
        self.close()

    def on_sel_inst(self):
        result = self.selInstDialog.exec_()

        if result:
            # simply uncheck panels to prevent the warning dialog
            if self.synHandle:
                api_syn.init_syn(self.synHandle)
                # check RF toggle state
                toggle_state = api_syn.read_power_toggle(self.synHandle)
                self.synCtrl.synPowerSwitchBtn.setChecked(toggle_state)
            else:
                pass
            if self.liaHandle:
                api_lia.init_lia(self.liaHandle)
            else:
                pass
            self.refresh_inst()
        else:
            pass

    def on_view_inst_stat(self):

        self.viewInstDialog.show()

    def on_close_sel_inst(self):

        d = Dialogs.CloseSelInstDialog(self)
        d.exec_()

        # simply uncheck panels to prevent the warning dialog
        self.refresh_inst()

    def on_scan_jpl(self):

        # when invoke this dialog, pause live lockin monitor in the main panel
        self.liaMonitor.stop()

        # if it is test mode, or real-run mode with instrument correctly connected
        if self.testModeAction.isChecked() or (self.synHandle and self.liaHandle):
            dconfig = ScanLockin.JPLScanConfig(main=self)
            entry_settings = None
            dconfig_result = dconfig.exec_()
        else:
            # instrument handle is None, pop up error
            msg = Shared.MsgError(self, 'Instrument Offline!', 'Connect to the synthesizer and lockin first before proceed.')
            msg.exec_()
            return None

        # this loop makes sure the config dialog does not disappear
        # unless the settings are all valid / or user hits cancel
        while dconfig_result:  # if dialog accepted
            entry_settings, filename = dconfig.get_settings()
            if entry_settings:
                total_time = Shared.jpl_scan_time(entry_settings)
                now = datetime.datetime.today()
                length = datetime.timedelta(seconds=total_time)
                then = now + length
                text = 'This batch job is estimated to take {:s}.\nIt is expected to finish at {:s}.'.format(str(length), then.strftime('%I:%M %p, %m-%d-%Y (%a)'))
                q = Shared.MsgInfo(self, 'Time Estimation', text)
                q.addButton(QtGui.QMessageBox.Cancel)
                qres = q.exec_()
                if qres == QtGui.QMessageBox.Ok:
                    break
                else:
                    dconfig_result = dconfig.exec_()
            else:
                dconfig_result = dconfig.exec_()

        if entry_settings and dconfig_result:
            dscan = ScanLockin.JPLScanWindow(entry_settings, filename, main=self)
            dscan.exec_()
        else:
            pass

    def on_scan_pci(self):
        d = Dialogs.ViewPG(self)
        d.exec_()

    def on_scan_cavity(self):
        pass

    def on_pres_reader(self):
        # this is a modaless window, save this attribute to the main class for reuse
        if hasattr(self, 'p_reader_win'):       # if window already activated
            self.p_reader_win.timer.start()     # restart reading
        else:   # initiate window instance
            self.p_reader_win = PresReader.PresReaderWindow(main=self)
        self.p_reader_win.show()

    def on_lwa_parser(self):
        ''' Launch lwa parser dialog window '''

        filename, _ = QtGui.QFileDialog.getOpenFileName(self, 'Open LWA File',
                                './default.lwa', 'SMAP Data File (*.lwa)')

        d = Dialogs.LWAParserDialog(self, filename)
        d.exec_()

    def closeEvent(self, event):
        q = QtGui.QMessageBox.question(self, 'Quit?',
                       'Are you sure to quit?', QtGui.QMessageBox.Yes |
                       QtGui.QMessageBox.No, QtGui.QMessageBox.Yes)
        if q == QtGui.QMessageBox.Yes:
            status = api_gen.close_inst(self.synHandle, self.liaHandle,
                                       self.pciHandle, self.motorHandle)
            if not status:    # safe to close
                self.close()
            else:
                qq = QtGui.QMessageBox.question(self, 'Error',
                        '''Error in disconnecting instruments.
                        Are you sure to force quit?''', QtGui.QMessageBox.Yes |
                        QtGui.QMessageBox.No, QtGui.QMessageBox.No)
                if qq == QtGui.QMessageBox.Yes:
                    self.close()
                else:
                    event.ignore()
        else:
            event.ignore()
