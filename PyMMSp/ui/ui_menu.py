#! encoding = utf-8

""" Collection of menubar, toolbar and status bar """

from PyQt6.QtWidgets import QMenuBar
from PyQt6.QtWidgets import QStatusBar
from PyQt6.QtGui import QAction


class MenuBar(QMenuBar):

    def __init__(self, parent=None):
        super().__init__(parent)


        # Set menu bar actions
        self.exitAction = QAction('Exit', self)
        self.exitAction.setShortcuts(['Ctrl+Q', 'Esc'])
        self.exitAction.setStatusTip('Exit program')

        # instrument actions
        self.instSelAction = QAction('Select Instrument', self)
        self.instSelAction.setShortcut('Ctrl+Shift+I')
        self.instSelAction.setStatusTip('Select instrument')

        self.instStatViewAction = QAction('View Instrument Status', self)
        self.instStatViewAction.setShortcut('Ctrl+Shift+V')
        self.instStatViewAction.setStatusTip('View status of currently connected instrument')

        self.instCloseAction = QAction('Close Instrument', self)
        self.instCloseAction.setStatusTip('Close individual instrument')

        # scan actions
        self.scanJPLAction = QAction('JPL Scanning Routine', self)
        self.scanJPLAction.setShortcut('Ctrl+Shift+J')
        self.scanJPLAction.setStatusTip('Use the scanning style of the JPL scanning routine')

        self.scanPCIAction = QAction('PCI Oscilloscope', self)
        self.scanPCIAction.setShortcut('Ctrl+Shift+S')
        self.scanPCIAction.setStatusTip("Use the scanning style of Brian's NIPCI card routine")

        self.scanCavityAction = QAction('Cavity Enhanced', self)
        self.scanCavityAction.setShortcut('Ctrl+Shift+C')
        self.scanCavityAction.setStatusTip('Use cavity enhanced spectroscopy')

        self.presReaderAction = QAction('Pressure Reader', self)
        self.presReaderAction.setShortcut('Ctrl+Shift+P')
        self.presReaderAction.setStatusTip('Record pressure measurements using the CENTER TWO pressure readout')

        # data process actions
        self.lwaParserAction = QAction('.lwa preview and export', self)
        self.lwaParserAction.setStatusTip('Preview JPL .lwa file and export subset of scans')

        self.testModeAction = QAction('Test Mode', self)
        self.testModeAction.setCheckable(True)
        self.testModeAction.setShortcut('Ctrl+T')
        self.testModeAction.setWhatsThis(
            'Toggle the test mode to bypass all instrument communication for GUI development.')

        menuFile = self.addMenu('&File')
        menuFile.addAction(self.exitAction)
        menuInst = self.addMenu('&Instrument')
        menuInst.addAction(self.instSelAction)
        menuInst.addAction(self.instStatViewAction)
        menuInst.addAction(self.instCloseAction)
        menuScan = self.addMenu('&Scan')
        menuScan.addAction(self.scanJPLAction)
        menuScan.addAction(self.scanPCIAction)
        menuScan.addAction(self.scanCavityAction)
        menuScan.addAction(self.presReaderAction)
        menuData = self.addMenu('&Data')
        menuData.addAction(self.lwaParserAction)
        menuTest = self.addMenu('&Test')
        menuTest.addAction(self.testModeAction)


class StatusBar(QStatusBar):

    def __init__(self, parent=None):
        super().__init__(parent)

