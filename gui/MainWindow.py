#! encoding = utf-8

from PyQt4 import QtCore, QtGui
import time
from gui import Panels
from gui import Dialogs
from api import general as apigen

class MainWindow(QtGui.QMainWindow):
    '''
        Implements the main window
    '''
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self)

        self.title_text = 'Yo!'

        # Set global window properties
        self.setWindowTitle(self.title_text)
        self.setMinimumWidth(1200)
        self.setMinimumHeight(800)

        # Initiate pyvisa instrument objects
        self.synHandle = None
        self.lcHandle = None
        self.pciHandle = None
        self.motorHandle = None

        # Set menu bar actions
        exitAction = QtGui.QAction('Exit', self)
        exitAction.setShortcuts(['Ctrl+Q', 'Esc'])
        exitAction.setStatusTip('Exit program')
        exitAction.triggered.connect(self.on_exit)

        instSelAction = QtGui.QAction('Select Instrument', self)
        instSelAction.setShortcut('Ctrl+Shift+I')
        instSelAction.setStatusTip('Select Instrument')
        instSelAction.triggered.connect(self.on_sel_inst)

        instStatViewAction = QtGui.QAction('View Instrument Status', self)
        instStatViewAction.setShortcut('Ctrl+Shift+V')
        instStatViewAction.setStatusTip('View status of currently connected instrument')
        instStatViewAction.triggered.connect(self.on_view_inst_stat)

        scanJPLAction = QtGui.QAction('JPL Scanning Routine', self)
        scanJPLAction.setShortcut('Ctrl+Shift+J')
        scanJPLAction.setStatusTip('Use the scanning style of the JPL scanning routine')
        scanJPLAction.triggered.connect(self.on_scan_jpl)

        scanPCIAction = QtGui.QAction('PCI Oscilloscope', self)
        scanPCIAction.setShortcut('Ctrl+Shift+P')
        scanPCIAction.setStatusTip("Use the scanning style of Brian's NIPCI card routine")
        scanPCIAction.triggered.connect(self.on_scan_pci)

        scanCavityAction = QtGui.QAction('Cavity Enhanced', self)
        scanCavityAction.setShortcut('Ctrl+Shift+C')
        scanCavityAction.setStatusTip('Use cavity enhanced spectroscopy')
        scanCavityAction.triggered.connect(self.on_scan_cavity)

        # Set menu bar
        self.statusBar()

        menuFile = self.menuBar().addMenu('&File')
        menuFile.addAction(exitAction)
        menuInst = self.menuBar().addMenu('&Instrument')
        menuInst.addAction(instSelAction)
        menuInst.addAction(instStatViewAction)
        menuScan = self.menuBar().addMenu('&Scan')
        menuScan.addAction(scanJPLAction)
        menuScan.addAction(scanPCIAction)
        menuScan.addAction(scanCavityAction)

        # Set main window widgets
        self.synStatus = Panels.SynStatus(self)
        self.lcStatus = Panels.LockinStatus(self)
        self.scopeStatus = Panels.ScopeStatus(self)
        self.synCtrl = Panels.SynCtrl(self)
        self.lcCtrl = Panels.LockinCtrl(self)
        self.scopeCtrl = Panels.ScopeCtrl(self)
        self.motorCtrl = Panels.MotorCtrl(self)

        # Set main window layout
        self.mainLayout = QtGui.QGridLayout()
        self.mainLayout.setSpacing(6)
        self.mainLayout.addWidget(self.synStatus, 0, 0, 1, 2)
        self.mainLayout.addWidget(self.lcStatus, 1, 0, 1, 2)
        self.mainLayout.addWidget(self.scopeStatus, 2, 0, 1, 2)
        self.mainLayout.addWidget(self.synCtrl, 0, 2, 1, 2)
        self.mainLayout.addWidget(self.lcCtrl, 1, 2, 1, 2)
        self.mainLayout.addWidget(self.scopeCtrl, 2, 2, 1, 2)
        self.mainLayout.addWidget(self.motorCtrl, 3, 2, 1, 2)
        self.mainLayout.addWidget(Panels.ScopeMonitor(self), 0, 4, 1, 4)
        self.mainLayout.addWidget(Panels.LockinMonitor(self), 1, 4, 1, 4)
        self.mainLayout.addWidget(Panels.SpectrumMonitor(self), 2, 4, 1, 4)

        # Enable main window
        self.mainWidget = QtGui.QWidget()
        self.mainWidget.setLayout(self.mainLayout)
        self.setCentralWidget(self.mainWidget)

    def refresh_syn(self):
        self.synStatus.update()
        self.synCtrl.check()

    def refresh_lockin(self):
        self.lcStatus.update()
        self.lcCtrl.check()

    def refresh_scope(self):
        self.scopeStatus.update()
        self.scopeCtrl.check()

    def refresh_motor(self):
        self.motorCtrl.check()

    def on_exit(self):
        q = QtGui.QMessageBox.question(self, 'Quit?',
                       'Are you sure to quit?', QtGui.QMessageBox.Yes |
                       QtGui.QMessageBox.No, QtGui.QMessageBox.Yes)
        if q == QtGui.QMessageBox.Yes:
            status = apigen.close_inst(self.synHandle, self.lcHandle, self.pciHandle, self.motorHandle)
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
                    pass
        else:
            pass

    def on_sel_inst(self):
        d = Dialogs.SelInstDialog(self, self)
        d.exec_()

        self.refresh_syn()
        self.refresh_lockin()
        self.refresh_scope()
        self.refresh_motor()

    def on_view_inst_stat(self):
        d = Dialogs.ViewInstDialog(self, self)
        d.show()

    def on_scan_jpl(self):
        pass

    def on_scan_pci(self):
        pass

    def on_scan_cavity(self):
        pass

    def closeEvent(self, event):
        self.on_exit()
