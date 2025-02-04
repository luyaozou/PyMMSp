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
        # instrument actions
        self.instSelAction = QAction('Select Instrument', self)
        self.instSelAction.setShortcut('Ctrl+Shift+I')
        self.instSelAction.setStatusTip('Select instrument')

        self.instCloseAction = QAction('Close Instrument', self)
        self.instCloseAction.setStatusTip('Close individual instrument')

        # scan actions
        self.scanConfigAction = QAction('Scan Configuration', self)
        self.scanConfigAction.setShortcut('Ctrl+Shift+C')
        self.scanConfigAction.setStatusTip('Configure scan parameters')

        self.scanAbsBBAction = QAction('Absorption Scan - Broadband Mode', self)
        self.scanAbsBBAction.setShortcut('Ctrl+Shift+B')
        self.scanAbsBBAction.setStatusTip('Absorption broadband scan mode using lock-in amplifier')

        self.scanAbsSearchAction = QAction('Absorption Scan - Search Mode', self)
        self.scanAbsSearchAction.setShortcut('Ctrl+Shift+S')
        self.scanAbsSearchAction.setStatusTip('Absorption targeted search mode using lock-in amplifier')

        self.scanCPAction = QAction('Chirp', self)
        self.scanCPAction.setShortcut('Ctrl+Shift+P')
        self.scanCPAction.setStatusTip('Chirped-pulse mode')

        self.scanCEAction = QAction('Cavity Enhanced', self)
        self.scanCEAction.setShortcut('Ctrl+Shift+E')
        self.scanCEAction.setStatusTip('Cavity enhanced spectroscopy mode')

        self.scanCRDSAction = QAction('Cavity-Ringdown',self)
        self.scanCRDSAction.setShortcut('Ctrl+Shift+R')
        self.scanCRDSAction.setStatusTip('Cavity ringdown spectroscopy mode')

        # data process actions
        self.lwaParserAction = QAction('.lwa preview and export', self)
        self.lwaParserAction.setStatusTip('Preview JPL .lwa file and export subset of scans')

        self.testModeAction = QAction('Test Mode', self)
        self.testModeAction.setCheckable(True)
        self.testModeAction.setShortcut('Ctrl+T')
        self.testModeAction.setWhatsThis(
            'Toggle the test mode to bypass all instrument communication for GUI development.')

        menuInst = self.addMenu('&Instrument')
        menuInst.addAction(self.instSelAction)
        menuInst.addAction(self.instCloseAction)
        menuScan = self.addMenu('&Scan')
        menuScan.addAction(self.scanConfigAction)
        menuScan.addAction(self.scanAbsBBAction)
        menuScan.addAction(self.scanAbsSearchAction)
        menuScan.addAction(self.scanCPAction)
        menuScan.addAction(self.scanCEAction)
        menuScan.addAction(self.scanCRDSAction)
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
