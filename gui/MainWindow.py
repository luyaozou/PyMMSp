#! encoding = utf-8

from PyQt4 import QtCore, QtGui
from gui.Panels import *

class MainWindow(QtGui.QMainWindow):
    """
        Implements the main window
    """
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self)

        self.title_text = 'Yo!'

        # Set global window properties
        self.setWindowTitle(self.title_text)
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)

        # Set main window layout
        self.mainLayout = QtGui.QGridLayout()
        self.mainLayout.setSpacing(6)
        self.mainLayout.addWidget(SynCtrl(self), 0, 0)
        self.mainLayout.addWidget(LockinCtrl(self), 1, 0)
        self.mainLayout.addWidget(ScopeCtrl(self), 2, 0)
        self.mainLayout.addWidget(CavityCtrl(self), 3, 0)
        self.mainLayout.addWidget(ScopeMonitor(self), 0, 1)
        self.mainLayout.addWidget(PowerMonitor(self), 0, 2)
        self.mainLayout.addWidget(SpectrumMonitor(self), 0, 3)

        # Enable main window
        self.mainWidget = QtGui.QWidget()
        self.mainWidget.setLayout(self.mainLayout)
        self.setCentralWidget(self.mainWidget)
