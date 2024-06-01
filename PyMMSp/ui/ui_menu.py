#! encoding = utf-8

""" Collection of menubar, toolbar and status bar """

from PyQt6.QtWidgets import QMenuBar, QLabel
from PyQt6.QtWidgets import QStatusBar
from PyQt6.QtGui import QAction
from PyQt6 import QtCore
from PyMMSp.ui.ui_shared import CommStatusBulb, msg_color


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

        self.viewOscilloAction = QAction('View Oscilloscope', self)
        self.viewOscilloAction.setShortcut('Ctrl+Shift+S')
        self.viewOscilloAction.setStatusTip("View the oscilloscope")

        self.scanCavityAction = QAction('Cavity Enhanced', self)
        self.scanCavityAction.setShortcut('Ctrl+Shift+C')
        self.scanCavityAction.setStatusTip('Use cavity enhanced spectroscopy')

        self.gaugeAction = QAction('Pressure Gauge', self)
        self.gaugeAction.setShortcut('Ctrl+Shift+P')
        self.gaugeAction.setStatusTip('Open pressure gauge controller')

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
        menuScan.addAction(self.viewOscilloAction)
        menuScan.addAction(self.scanCavityAction)
        menuScan.addAction(self.gaugeAction)
        menuData = self.addMenu('&Data')
        menuData.addAction(self.lwaParserAction)
        menuTest = self.addMenu('&Test')
        menuTest.addAction(self.testModeAction)


class StatusBar(QStatusBar):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.synBulb = CommStatusBulb()
        self.liaBulb = CommStatusBulb()
        self.oscilloBulb = CommStatusBulb()
        self.gaugeBulb = CommStatusBulb()

        self.testModeLabel = QLabel('[TEST MODE ACTIVE -- NOTHING IS REAL]!')
        self.testModeLabel.setStyleSheet(f'color: {msg_color(0)}')
        self.testModeLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self.labelInst = QLabel()
        self.addPermanentWidget(self.testModeLabel)
        self.addPermanentWidget(self.labelInst)
        self.addPermanentWidget(QLabel('Synthesizer'))
        self.addPermanentWidget(self.synBulb)
        self.addPermanentWidget(QLabel('Lockin'))
        self.addPermanentWidget(self.liaBulb)
        self.addPermanentWidget(QLabel('Oscilloscope'))
        self.addPermanentWidget(self.oscilloBulb)
        self.addPermanentWidget(QLabel('Gauge'))
        self.addPermanentWidget(self.gaugeBulb)

        self._inst_map = {
            'syn': self.synBulb,
            'lia': self.liaBulb,
            'oscillo': self.oscilloBulb,
            'gauge': self.gaugeBulb
        }

    @QtCore.pyqtSlot(str, bool)
    def update_inst_state(self, inst, b):
        self._inst_map[inst].setStatus(b)

    def set_sim(self, b):
        if b:
            self.labelInst.setText('Simulator: ')
        else:
            self.labelInst.setText('Real: ')
