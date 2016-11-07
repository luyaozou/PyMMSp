#! encoding = utf-8

from PyQt4 import QtCore, QtGui
from gui.Panels import *
from gui.Dialogs import *

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

        # Set menu bar actions
        exitAction = QtGui.QAction('Exit', self)
        exitAction.setShortcuts(['Ctrl+Q', 'Esc'])
        exitAction.setStatusTip('Exit program')
        exitAction.triggered.connect(self.on_exit)

        selInstAction = QtGui.QAction('Select Instrument', self)
        selInstAction.setShortcut('Ctrl+I')
        selInstAction.setStatusTip('Select Instrument')
        selInstAction.triggered.connect(self.on_sel_inst)

        viewInstStatAction = QtGui.QAction('View Instrument Status', self)
        viewInstStatAction.setStatusTip('View status of currently connected instrument')
        viewInstStatAction.triggered.connect(self.on_view_inst_stat)

        # Set menu bar
        self.statusBar()

        menuFile = self.menuBar().addMenu('&File')
        menuFile.addAction(exitAction)
        menuInst = self.menuBar().addMenu('&Instrument')
        menuInst.addAction(selInstAction)
        menuInst.addAction(viewInstStatAction)

        # Set main window layout
        self.mainLayout = QtGui.QGridLayout()
        self.mainLayout.setSpacing(6)
        self.mainLayout.addWidget(SynCtrl(self), 0, 0, 1, 2)
        self.mainLayout.addWidget(LockinCtrl(self), 1, 0, 1, 2)
        self.mainLayout.addWidget(ScopeCtrl(self), 2, 0, 1, 2)
        self.mainLayout.addWidget(CavityCtrl(self), 3, 0, 1, 2)
        self.mainLayout.addWidget(ScopeMonitor(self), 0, 2, 1, 4)
        self.mainLayout.addWidget(LockinMonitor(self), 1, 2, 1, 4)
        self.mainLayout.addWidget(SpectrumMonitor(self), 2, 2, 1, 4)

        # Enable main window
        self.mainWidget = QtGui.QWidget()
        self.mainWidget.setLayout(self.mainLayout)
        self.setCentralWidget(self.mainWidget)

    def on_exit(self):
        self.close()

    def on_sel_inst(self):
        d = SelInstDialog(self, self)
        d.show()

    def on_view_inst_stat(self):
        d = ViewInstDialog(self, self)
        d.show()
