#! encoding = utf-8

from PyQt6 import QtWidgets, QtCore
from PyQt6.QtGui import QFont
import pyqtgraph as pg
from PyMMSp.ui import ui_shared
from PyMMSp.config.config import AbsScanSetting
from PyMMSp.inst.lockin import SENS_STR, TAU_STR, MODU_MODE


class DialogAbsConfig(QtWidgets.QDialog):
    """ Absorption broadband scan """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Absorption Scan Configuration')
        self.setMinimumSize(1280, 600)
        self.setWindowFlags(QtCore.Qt.WindowType.Window)

        # Add top buttons
        self.btnDir = QtWidgets.QPushButton('Save data to directory: ')
        self.lblDir = QtWidgets.QLabel()
        self.ckPress = QtWidgets.QCheckBox('Regulate pressure')
        topButtonLayout = QtWidgets.QHBoxLayout()
        topButtonLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        topButtonLayout.addWidget(self.btnDir)
        topButtonLayout.addWidget(self.lblDir)
        topButtons = QtWidgets.QWidget()
        topButtons.setLayout(topButtonLayout)

        top2Layout = QtWidgets.QHBoxLayout()
        top2Layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        top2Layout.addWidget(self.ckPress)

        # Add bottom buttons
        cancelButton = QtWidgets.QPushButton(ui_shared.btn_label('reject'))
        acceptButton = QtWidgets.QPushButton(ui_shared.btn_label('confirm'))
        acceptButton.setDefault(True)
        self.btnEstimate = QtWidgets.QPushButton('Estimate Time')
        bottomButtonLayout = QtWidgets.QHBoxLayout()
        bottomButtonLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        bottomButtonLayout.addWidget(self.btnEstimate)
        bottomButtonLayout.addWidget(cancelButton)
        bottomButtonLayout.addWidget(acceptButton)
        bottomButtons = QtWidgets.QWidget()
        bottomButtons.setLayout(bottomButtonLayout)

        # Add freq config entries
        self.ListSetupItem = []
        self.setupItemLayout = QtWidgets.QGridLayout()
        self.setupItemLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        # add entries
        self.btnAddItem = QtWidgets.QPushButton('+')
        self.btnAddItem.setFixedWidth(30)
        self.setupItemLayout.addWidget(self.btnAddItem, 0, 0)
        self.setupItemLayout.addWidget(QtWidgets.QLabel('Start (MHz)'), 0, 1)
        self.setupItemLayout.addWidget(QtWidgets.QLabel('Stop (MHz)'), 0, 2)
        self.setupItemLayout.addWidget(QtWidgets.QLabel('Step (kHz)'), 0, 3)
        self.setupItemLayout.addWidget(QtWidgets.QLabel('Averages'), 0, 4)
        self.setupItemLayout.addWidget(QtWidgets.QLabel('Sensitivity'), 0, 5)
        self.setupItemLayout.addWidget(QtWidgets.QLabel('Time Const'), 0, 6)
        self.setupItemLayout.addWidget(QtWidgets.QLabel('Dwell time (ms)'), 0, 7)
        self.setupItemLayout.addWidget(QtWidgets.QLabel('Buffer Length'), 0, 8)
        self.setupItemLayout.addWidget(QtWidgets.QLabel('Modulation'), 0, 9)
        self.setupItemLayout.addWidget(QtWidgets.QLabel('Mod Freq (kHz)'), 0, 10)
        self.setupItemLayout.addWidget(QtWidgets.QLabel('Mod Depth/Dev (%/kHz)'), 0, 11)
        self.setupItemLayout.addWidget(QtWidgets.QLabel('AC Gain (dB)'), 0, 12)
        self.setupItemLayout.addWidget(QtWidgets.QLabel('Target p (μBar)'), 0, 13)
        self.setupItemLayout.addWidget(QtWidgets.QLabel('p Tolerance (μBar)'), 0, 14)
        self._delBtnGroup = QtWidgets.QButtonGroup()
        # self.add_entry()

        entryWidgets = QtWidgets.QWidget()
        entryWidgets.setLayout(self.setupItemLayout)

        entryArea = QtWidgets.QScrollArea()
        entryArea.setWidgetResizable(True)
        entryArea.setWidget(entryWidgets)

        # Set up main layout
        mainLayout = QtWidgets.QVBoxLayout(self)
        mainLayout.addWidget(topButtons)
        mainLayout.addLayout(top2Layout)
        mainLayout.addWidget(entryArea)
        mainLayout.addWidget(bottomButtons)
        self.setLayout(mainLayout)

        cancelButton.clicked[bool].connect(self.reject)
        acceptButton.clicked[bool].connect(self.accept)
        self.btnAddItem.clicked[bool].connect(self.add_item)
        self._delBtnGroup.buttonClicked.connect(self.remove_item)
        self.btnDir.clicked[bool].connect(self.set_dir)

    def set_dir(self):
        # pop up a dialog to select the directory
        dir_ = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select the directory to save data')
        self.lblDir.setText(dir_)

    def add_setting_list(self, list_scan_settings: [AbsScanSetting,]):
        """ Add a list of scan settings """
        # verify the length of the setting list and the current item list
        n_setting = len(list_scan_settings)
        n_item = len(self.ListSetupItem)
        if n_setting < n_item:
            # load new values for the first n_setting items,
            # and then remove all extra items
            for item, setting in zip(self.ListSetupItem[:n_setting], list_scan_settings):
                item.set_item(setting)
            for i in range(n_setting, n_item):
                item = self.ListSetupItem.pop()
                self._remove_item_from_widget(item)
        else:
            # load new values for all _BatchSetupItems in the ListSetupItem
            # and then create new items
            for item, setting in zip(self.ListSetupItem, list_scan_settings):
                item.set_item(setting)
            for i, setting in enumerate(list_scan_settings[n_item:]):
                item = _BatchSetupItem(parent=self)
                item.set_item(setting)
                self._add_item_to_widget(item)

    def get_list_settings(self):
        a_list = [item.get_setting() for item in self.ListSetupItem]
        # also need to check if the pressure regulation is checked
        for setting in a_list:
            setting.is_press = self.ckPress.isChecked()
        return a_list

    def add_item(self):
        """ Add batch item to this dialog window """
        item = _BatchSetupItem(parent=self)
        # get the current last entry
        if self.ListSetupItem:
            last_item = self.ListSetupItem[-1]
            # set default values to be the same as the last one
            item.set_item(last_item.get_setting())
        else:
            pass
        # add this entry to the layout and to the entry list
        self._add_item_to_widget(item)

    def remove_item(self, clicked_btn):
        # remove this entry
        idx = self._delBtnGroup.id(clicked_btn)
        item = self.ListSetupItem.pop(idx)
        # remove the widget from the layout
        self._remove_item_from_widget(item)
        for i, next_item in enumerate(self.ListSetupItem[idx:]):
            # modify the index of other items after idx 1
            self._delBtnGroup.removeButton(next_item.btnDel)
            self._delBtnGroup.addButton(next_item.btnDel, id=idx + i)

    def _add_item_to_widget(self, item):
        self.ListSetupItem.append(item)
        row = len(self.ListSetupItem)
        self.setupItemLayout.addWidget(item.btnDel, row, 0)
        self.setupItemLayout.addWidget(item.inpFreqStart, row, 1)
        self.setupItemLayout.addWidget(item.inpFreqStop, row, 2)
        self.setupItemLayout.addWidget(item.inpFreqStep, row, 3)
        self.setupItemLayout.addWidget(item.inpAvg, row, 4)
        self.setupItemLayout.addWidget(item.comboSens, row, 5)
        self.setupItemLayout.addWidget(item.comboTau, row, 6)
        self.setupItemLayout.addWidget(item.inpDwellTime, row, 7)
        self.setupItemLayout.addWidget(item.inpBufferLen, row, 8)
        self.setupItemLayout.addWidget(item.comboMod, row, 9)
        self.setupItemLayout.addWidget(item.inpModFreq, row, 10)
        self.setupItemLayout.addWidget(item.inpModAmp, row, 11)
        self.setupItemLayout.addWidget(item.inpACGain, row, 12)
        self.setupItemLayout.addWidget(item.inpPress, row, 13)
        self.setupItemLayout.addWidget(item.inpPressTol, row, 14)
        # note that the row starts with 1 (because of the header)
        # while list / button index starts with 0
        self._delBtnGroup.addButton(item.btnDel, row - 1)

    def _remove_item_from_widget(self, item):
        self.setupItemLayout.removeWidget(item.btnDel)
        self.setupItemLayout.removeWidget(item.inpFreqStart)
        self.setupItemLayout.removeWidget(item.inpFreqStop)
        self.setupItemLayout.removeWidget(item.inpFreqStep)
        self.setupItemLayout.removeWidget(item.inpAvg)
        self.setupItemLayout.removeWidget(item.comboSens)
        self.setupItemLayout.removeWidget(item.comboTau)
        self.setupItemLayout.removeWidget(item.inpDwellTime)
        self.setupItemLayout.removeWidget(item.inpBufferLen)
        self.setupItemLayout.removeWidget(item.comboMod)
        self.setupItemLayout.removeWidget(item.inpModFreq)
        self.setupItemLayout.removeWidget(item.inpModAmp)
        self.setupItemLayout.removeWidget(item.inpACGain)
        self.setupItemLayout.removeWidget(item.inpPress)
        self.setupItemLayout.removeWidget(item.inpPressTol)
        self._delBtnGroup.removeButton(item.btnDel)
        item.delete()


class DialogAbsScan(QtWidgets.QDialog):
    """ Scanning window """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Absorption Scan -- Broadband')
        self.setMinimumSize(1280, 800)
        self.setWindowFlags(QtCore.Qt.WindowType.Window)
#        self.entry_settings = entry_settings

        # Create the QTabWidget
        self.tabWidget = QtWidgets.QTabWidget()
        # Create the first tab and its layout
        self.inpFStart = ui_shared.create_double_spin_box(0, minimum=50000, maximum=1500000, dec=2)
        self.inpFStop = ui_shared.create_double_spin_box(0, minimum=50000, maximum=1500000, dec=2)
        self.inpFCenter = ui_shared.create_double_spin_box(0, minimum=50000, maximum=1500000, dec=2)
        self.inpFRange = ui_shared.create_double_spin_box(0, minimum=0, dec=1)
        tab1 = QtWidgets.QWidget()
        tab1Layout = QtWidgets.QFormLayout()
        tab1Layout.addRow(QtWidgets.QLabel('Start (MHz)'), self.inpFStart)
        tab1Layout.addRow(QtWidgets.QLabel('Stop (MHz)'), self.inpFStop)
        tab1.setLayout(tab1Layout)
        # Create the second tab and its layout
        tab2 = QtWidgets.QWidget()
        tab2Layout = QtWidgets.QFormLayout()
        tab2Layout.addRow(QtWidgets.QLabel('Center (MHz)'), self.inpFCenter)
        tab2Layout.addRow(QtWidgets.QLabel('Range (MHz)'), self.inpFRange)
        tab2.setLayout(tab2Layout)
        # Add tabs to the QTabWidget
        self.tabWidget.addTab(tab1, 'Start-Stop')
        self.tabWidget.addTab(tab2, 'Center-Range')
        self.tabWidget.setSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum,
                                     QtWidgets.QSizePolicy.Policy.Minimum)

        self.inpFStep = ui_shared.create_double_spin_box(0, minimum=0, dec=1, width=125)
        self.inpAvg = ui_shared.create_int_spin_box(1, minimum=1)
        self.comboSens = QtWidgets.QComboBox()
        self.comboSens.addItems(SENS_STR)
        self.comboTau = QtWidgets.QComboBox()
        self.comboTau.addItems(TAU_STR)
        self.inpDwellTime = ui_shared.create_double_spin_box(0, minimum=0, dec=0, width=125)
        self.inpBufferLen = ui_shared.create_int_spin_box(1, minimum=1)
        self.comboMod = QtWidgets.QComboBox()
        self.comboMod.addItems(MODU_MODE)
        self.inpModFreq = ui_shared.create_double_spin_box(0, minimum=0, dec=3)
        self.inpModAmp = ui_shared.create_double_spin_box(0, minimum=0, dec=2)
        self.inpACGain = ui_shared.create_int_spin_box(0, minimum=0, maximum=72)
        self.boxPress = QtWidgets.QGroupBox('Regulate Pressure')
        self.boxPress.setCheckable(True)
        boxPressLayout = QtWidgets.QFormLayout()
        self.inpPress = ui_shared.create_double_spin_box(0, minimum=0, dec=1)
        self.inpPressTol = ui_shared.create_double_spin_box(0, minimum=0, dec=1)
        boxPressLayout.addRow(QtWidgets.QLabel('Target p (μBar)'), self.inpPress)
        boxPressLayout.addRow(QtWidgets.QLabel('p Tolerance (μBar)'), self.inpPressTol)
        self.boxPress.setLayout(boxPressLayout)

        commonWidgetLayout = QtWidgets.QGridLayout()
        commonWidgetLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        commonWidgetLayout.addWidget(QtWidgets.QLabel('Step (kHz)'), 0, 0)
        commonWidgetLayout.addWidget(self.inpFStep, 0, 1)
        commonWidgetLayout.addWidget(QtWidgets.QLabel('Dwell time (ms)'), 0, 2)
        commonWidgetLayout.addWidget(self.inpDwellTime, 0, 3)
        commonWidgetLayout.addWidget(QtWidgets.QLabel('Averages'), 1, 0)
        commonWidgetLayout.addWidget(self.inpAvg, 1, 1)
        commonWidgetLayout.addWidget(QtWidgets.QLabel('Buffer Length'), 1, 2)
        commonWidgetLayout.addWidget(self.inpBufferLen, 1, 3)
        commonWidgetLayout.addWidget(QtWidgets.QLabel('Sensitivity'), 2, 0)
        commonWidgetLayout.addWidget(self.comboSens, 2, 1)
        commonWidgetLayout.addWidget(QtWidgets.QLabel('Time Const'), 2, 2)
        commonWidgetLayout.addWidget(self.comboTau, 2, 3)
        commonWidgetLayout.addWidget(QtWidgets.QLabel('Modulation'), 3, 0, 1, 2)
        commonWidgetLayout.addWidget(self.comboMod, 3, 2, 1, 2)
        commonWidgetLayout.addWidget(QtWidgets.QLabel('Mod Freq (kHz)'), 4, 0, 1, 2)
        commonWidgetLayout.addWidget(self.inpModFreq, 4, 2, 1, 2)
        commonWidgetLayout.addWidget(QtWidgets.QLabel('Mod Depth/Dev (%/kHz)'), 5, 0, 1, 2)
        commonWidgetLayout.addWidget(self.inpModAmp, 5, 2, 1, 2)
        commonWidgetLayout.addWidget(QtWidgets.QLabel('AC Gain (dB)'), 6, 0, 1, 2)
        commonWidgetLayout.addWidget(self.inpACGain, 6, 2, 1, 2)
        commonWidgetLayout.addWidget(self.boxPress, 7, 0, 1, 4)

        quickConfigBtnLayout = QtWidgets.QHBoxLayout()
        self.btnStart = QtWidgets.QPushButton('Start')
        self.btnStart.setToolTip('Start data acquisition')
        self.btnPause = QtWidgets.QPushButton('Pause')
        self.btnPause.setToolTip('Pause data acquisition')
        self.btnPause.setCheckable(True)
        self.btnAbort = QtWidgets.QPushButton('Abort')
        self.btnAbort.setToolTip('Abort current scan')
        quickConfigBtnLayout.addWidget(self.btnStart)
        quickConfigBtnLayout.addWidget(self.btnPause)
        quickConfigBtnLayout.addWidget(self.btnAbort)
        quickConfigBtnLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        # Add the QTabWidget to the quickConfig group box
        quickConfig = QtWidgets.QGroupBox('Quick Scan Setup ')
        quickConfigLayout = QtWidgets.QVBoxLayout()
        quickConfigLayout.addWidget(self.tabWidget)
        quickConfigLayout.addLayout(commonWidgetLayout)
        quickConfigLayout.addLayout(quickConfigBtnLayout)
        quickConfig.setLayout(quickConfigLayout)

        # set up batch list display
        self.batchListWidget = BatchListWidget()
        batchArea = QtWidgets.QScrollArea()
        batchArea.setWidgetResizable(True)
        batchArea.setSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum,
                                QtWidgets.QSizePolicy.Policy.Expanding)
        batchArea.setWidget(self.batchListWidget)

        self.btnBatchSetup = QtWidgets.QPushButton('Batch Setup')
        self.btnBatchSetup.setToolTip('Set up the batch scan parameters')
        self.btnBatchStart = QtWidgets.QPushButton('Start')
        self.btnBatchStart.setToolTip('Start the batch scan')
        self.btnBatchPause = QtWidgets.QPushButton('Pause')
        self.btnBatchPause.setToolTip('Pause data acquisition')
        self.btnBatchPause.setCheckable(True)
        self.btnBatchAbort = QtWidgets.QPushButton('Abort')
        self.btnBatchAbort.setToolTip('Abort the batch scan')
        self.btnBatchSkip = QtWidgets.QPushButton('Skip Current')
        self.btnBatchSkip.setToolTip('Drop the current sweep and jump directly to the next one')
        self.btnBatchRedo = QtWidgets.QPushButton('Redo Current')
        self.btnBatchRedo.setToolTip('Redo the current sweep')
        self.btnAccessData = QtWidgets.QPushButton('Access Data')
        self.btnAccessData.setToolTip('Access the data folder')

        btnLayout = QtWidgets.QGridLayout()
        btnLayout.addWidget(self.btnBatchSetup, 0, 0)
        btnLayout.addWidget(self.btnAccessData, 0, 1)
        btnLayout.addWidget(self.btnBatchStart, 1, 0)
        btnLayout.addWidget(self.btnBatchPause, 1, 1)
        btnLayout.addWidget(self.btnBatchSkip, 2, 0)
        btnLayout.addWidget(self.btnBatchRedo, 2, 1)
        btnLayout.addWidget(self.btnBatchAbort, 3, 1)

        batchDisplay = QtWidgets.QGroupBox()
        batchDisplay.setTitle('Batch Task')
        batchLayout = QtWidgets.QVBoxLayout()
        batchLayout.addWidget(batchArea)
        batchLayout.addLayout(btnLayout)
        batchDisplay.setLayout(batchLayout)

        # set up buttons in the left column
        self.comboSumOverride = QtWidgets.QComboBox()
        self.comboSumOverride.addItems(['Sum', 'Override'])
        self.ckAutoRangeX = QtWidgets.QCheckBox('Auto Range X')
        self.ckAutoRangeY = QtWidgets.QCheckBox('Auto Range Y')
        self.ckLinkX = QtWidgets.QCheckBox('Link X')
        self.ckLinkY = QtWidgets.QCheckBox('Link Y')
        leftBtnsLayout = QtWidgets.QHBoxLayout()
        leftBtnsLayout.addWidget(self.comboSumOverride)
        leftBtnsLayout.addWidget(self.ckAutoRangeX)
        leftBtnsLayout.addWidget(self.ckAutoRangeY)
        leftBtnsLayout.addWidget(self.ckLinkX)
        leftBtnsLayout.addWidget(self.ckLinkY)

        # set up progress bar
        self.currentProgBar = QtWidgets.QProgressBar()
        self.totalProgBar = QtWidgets.QProgressBar()
        progressLayout = QtWidgets.QGridLayout()
        progressLayout.addWidget(QtWidgets.QLabel('Total progress'), 0, 0)
        progressLayout.addWidget(self.totalProgBar, 0, 1)
        progressLayout.addWidget(QtWidgets.QLabel('Current Progress'), 1, 0)
        progressLayout.addWidget(self.currentProgBar, 1, 1)

        self._canvasTotal = pg.PlotWidget()
        self._canvasThis = pg.PlotWidget()
        self._curveTotal = pg.PlotCurveItem()
        self._curveTotal.setPen(pg.mkPen(255, 255, 255))
        self._curveThisInTotal = pg.PlotCurveItem()
        self._curveThisInTotal.setPen(pg.mkPen(255, 182, 47))
        self._curveThis = pg.PlotCurveItem()
        self._curveThis.setPen(pg.mkPen(255, 182, 47))
        canvasPress = pg.PlotWidget()
        self._curvePress = pg.PlotCurveItem()
        self._curvePress.setPen(pg.mkPen(175, 205, 255))
        self._canvasTotal.addItem(self._curveTotal)
        self._canvasTotal.addItem(self._curveThisInTotal)
        self._canvasThis.addItem(self._curveThis)
        canvasPress.addItem(self._curvePress)
        self._canvasTotal.getPlotItem().setTitle('Overall Scan')
        self._canvasTotal.getPlotItem().setLabels(left='Intensity', bottom='Frequency (MHz)')
        self._canvasThis.getPlotItem().setTitle('Current Scan')
        self._canvasThis.getPlotItem().setLabels(left='Intensity', bottom='Frequency (MHz)')
        canvasPress.getPlotItem().setTitle('Pressure')
        canvasPress.getPlotItem().setLabels(left='Pressure (mbar)', bottom='Time (s)')
        canvasPress.setFixedHeight(150)

        leftLayout = QtWidgets.QVBoxLayout()
        leftLayout.addWidget(self._canvasTotal)
        leftLayout.addWidget(self._canvasThis)
        leftLayout.addLayout(leftBtnsLayout)
        leftLayout.addLayout(progressLayout)
        rightWidget = QtWidgets.QWidget()
        rightWidget.setFixedWidth(450)
        rightLayout = QtWidgets.QVBoxLayout()
        rightLayout.addWidget(canvasPress)
        rightLayout.addWidget(quickConfig)
        rightLayout.addWidget(batchDisplay)
        rightLayout.addLayout(btnLayout)
        rightWidget.setLayout(rightLayout)
        mainLayout = QtWidgets.QHBoxLayout()
        mainLayout.addLayout(leftLayout)
        mainLayout.addWidget(rightWidget)
        self.setLayout(mainLayout)

        self.ckLinkX.clicked[bool].connect(self._link_x)
        self.ckLinkY.clicked[bool].connect(self._link_y)
        self.ckAutoRangeX.clicked[bool].connect(self._auto_range_x)
        self.ckAutoRangeY.clicked[bool].connect(self._auto_range_y)

    def get_quick_scan_settings(self):
        """ Get the quick scan settings """
        if self.tabWidget.currentIndex() == 0:
            # the first tab is selected
            freq_start = self.inpFStart.value()
            freq_stop = self.inpFStop.value()
        else:
            # the second tab is selected
            freq_center = self.inpFCenter.value()
            freq_range = self.inpFRange.value()
            freq_start = freq_center - freq_range / 2
            freq_stop = freq_center + freq_range / 2

        return AbsScanSetting(
            freq_start=freq_start,
            freq_stop=freq_stop,
            freq_step=self.inpFStep.value() * 1e-3,
            avg=self.inpAvg.value(),
            sens_idx=self.comboSens.currentIndex(),
            tau_idx=self.comboTau.currentIndex(),
            dwell_time=self.inpDwellTime.value() * 1e-3,
            buffer_len=self.inpBufferLen.value(),
            modu_mode_idx=self.comboMod.currentIndex(),
            modu_freq=self.inpModFreq.value() * 1e3,
            modu_amp=self.inpModAmp.value(),
            is_press=self.boxPress.isChecked(),
            press=self.inpPress.value(),
            press_tol=self.inpPressTol.value()
        )

    def plot_this(self, x, y):
        self._curveThis.setData(x, y)

    def plot_total(self, x, y):
        self._curveTotal.setData(x, y)

    def plot_press(self, x, y):
        self._curvePress.setData(x, y)

    def _link_x(self, checked):
        if checked:
            self._canvasThis.setXLink(self._canvasTotal)
        else:
            self._canvasThis.setXLink(None)

    def _link_y(self, checked):
        if checked:
            self._canvasThis.setYLink(self._canvasTotal)
        else:
            self._canvasThis.setYLink(None)

    def _auto_range_x(self, checked):
        if checked:
            self._canvasThis.enableAutoRange(axis=pg.AxisItem.AxisOrientation.Horizontal)
        else:
            self._canvasThis.disableAutoRange(axis=pg.AxisItem.AxisOrientation.Horizontal)

    def _auto_range_y(self, checked):
        if checked:
            self._canvasThis.enableAutoRange(axis=pg.AxisItem.AxisOrientation.Vertical)
        else:
            self._canvasThis.disableAutoRange(axis=pg.AxisItem.AxisOrientation.Vertical)


class BatchListWidget(QtWidgets.QWidget):
    """ Batch list display """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.batchLayout = QtWidgets.QGridLayout()
        self.batchLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignLeft)
        # set up batch list row header
        # put comment in the first column and make it editable
        self.batchLayout.addWidget(QtWidgets.QLabel('#'), 0, 0)
        self.batchLayout.addWidget(QtWidgets.QLabel('Start (MHz)'), 0, 1)
        self.batchLayout.addWidget(QtWidgets.QLabel('Stop (MHz)'), 0, 2)
        self.batchLayout.addWidget(QtWidgets.QLabel('Step'), 0, 3)
        self.batchLayout.addWidget(QtWidgets.QLabel('Buffer'), 0, 4)
        self.batchLayout.addWidget(QtWidgets.QLabel('Pressure'), 0, 5)
        self.setLayout(self.batchLayout)
        self._item_list = []

    def add_entries(self, list_scan_settings: [AbsScanSetting,]):
        n = len(self._item_list)
        # update existing entry items
        for setting, item in zip(list_scan_settings, self._item_list):
            item.set_item(setting)
        # add new entries
        if n < len(list_scan_settings):
            for i, setting in enumerate(list_scan_settings[n:]):
                row = i + n + 1
                item = _BatchDispItem(row, parent=self)
                item.set_item(setting)
                self.batchLayout.addWidget(item.lblNo, row, 0)
                self.batchLayout.addWidget(item.lblStartF, row, 1)
                self.batchLayout.addWidget(item.lblStopF, row, 2)
                self.batchLayout.addWidget(item.lblStep, row, 3)
                self.batchLayout.addWidget(item.lblBuffer, row, 4)
                self.batchLayout.addWidget(item.lblPress, row, 5)
                self._item_list.append(item)
        # if more items than needed, remove the extra ones
        elif n > len(list_scan_settings):
            for i in range(n - len(list_scan_settings)):
                item = self._item_list.pop()
                self.batchLayout.removeWidget(item.lblNo)
                self.batchLayout.removeWidget(item.lblStartF)
                self.batchLayout.removeWidget(item.lblStopF)
                self.batchLayout.removeWidget(item.lblStep)
                self.batchLayout.removeWidget(item.lblBuffer)
                self.batchLayout.removeWidget(item.lblPress)
                item.delete()

    def set_active_entry(self, idx):
        """ Set the active entry """
        for i, entry in enumerate(self._item_list):
            if i == idx:
                entry.set_color_black()
            else:
                entry.set_color_grey()


class _BatchSetupItem(QtWidgets.QWidget):
    """ Frequency window entry for scanning job configuration with captions """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.inpFreqStart = ui_shared.create_double_spin_box(0, minimum=50000, maximum=1500000, dec=2)
        self.inpFreqStop = ui_shared.create_double_spin_box(0, minimum=50000, maximum=1500000, dec=2)
        self.inpFreqStep = ui_shared.create_double_spin_box(0, minimum=0, dec=1)
        self.inpAvg = ui_shared.create_int_spin_box(1, minimum=1)
        self.comboSens = QtWidgets.QComboBox()
        self.comboSens.addItems(SENS_STR)
        self.comboTau = QtWidgets.QComboBox()
        self.comboTau.addItems(TAU_STR)
        self.inpDwellTime = ui_shared.create_double_spin_box(0, minimum=0, dec=0)
        self.inpBufferLen = ui_shared.create_int_spin_box(1, minimum=1)
        self.comboMod = QtWidgets.QComboBox()
        self.comboMod.addItems(MODU_MODE)
        self.inpModFreq = ui_shared.create_double_spin_box(0, minimum=0, dec=3)
        self.inpModAmp = ui_shared.create_double_spin_box(0, minimum=0, dec=2)
        self.inpACGain = ui_shared.create_int_spin_box(0, minimum=0, maximum=72)
        self.inpPress = ui_shared.create_double_spin_box(0, minimum=0, dec=1)
        self.inpPressTol = ui_shared.create_double_spin_box(0, minimum=0, dec=1)
        self.btnDel = QtWidgets.QPushButton('-')
        self.btnDel.setFixedWidth(30)

    def delete(self):
        """ Delete this entry """
        self.inpFreqStart.deleteLater()
        self.inpFreqStop.deleteLater()
        self.inpFreqStep.deleteLater()
        self.inpAvg.deleteLater()
        self.comboSens.deleteLater()
        self.comboTau.deleteLater()
        self.inpDwellTime.deleteLater()
        self.inpBufferLen.deleteLater()
        self.comboMod.deleteLater()
        self.inpModFreq.deleteLater()
        self.inpModAmp.deleteLater()
        self.inpACGain.deleteLater()
        self.inpPress.deleteLater()
        self.inpPressTol.deleteLater()
        self.btnDel.deleteLater()
        self.deleteLater()

    def get_setting(self):
        """ Get the entry setting """
        return AbsScanSetting(
            freq_start=self.inpFreqStart.value(),
            freq_stop=self.inpFreqStop.value(),
            freq_step=self.inpFreqStep.value() * 1e-3,
            avg=self.inpAvg.value(),
            sens_idx=self.comboSens.currentIndex(),
            tau_idx=self.comboTau.currentIndex(),
            dwell_time=self.inpDwellTime.value() * 1e-3,
            buffer_len=self.inpBufferLen.value(),
            modu_mode_idx=self.comboMod.currentIndex(),
            modu_freq=self.inpModFreq.value() * 1e3,
            modu_amp=self.inpModAmp.value(),
            ac_gain=self.inpACGain.value(),
            press=self.inpPress.value(),
            press_tol=self.inpPressTol.value()
        )

    def set_item(self, entry_setting: AbsScanSetting):
        """ Set the entry values """
        self.inpFreqStart.setValue(entry_setting.freq_start)
        self.inpFreqStop.setValue(entry_setting.freq_stop)
        self.inpFreqStep.setValue(entry_setting.freq_step * 1e3)
        self.inpAvg.setValue(entry_setting.avg)
        self.comboSens.setCurrentIndex(entry_setting.sens_idx)
        self.comboTau.setCurrentIndex(entry_setting.tau_idx)
        self.inpDwellTime.setValue(entry_setting.dwell_time * 1e3)
        self.inpBufferLen.setValue(entry_setting.buffer_len)
        self.comboMod.setCurrentIndex(entry_setting.modu_mode_idx)
        self.inpModFreq.setValue(entry_setting.modu_freq * 1e-3)
        self.inpModAmp.setValue(entry_setting.modu_amp)
        self.inpACGain.setValue(entry_setting.ac_gain)
        self.inpPress.setValue(entry_setting.press)
        self.inpPressTol.setValue(entry_setting.press_tol)


class _BatchDispItem(QtWidgets.QWidget):
    """ Single batch list entry in display mode.
    entry = (comment [str], start [float, MHz], stop [float, MHz],
             step [float, MHz], avg [int], sens_idx [int], tc_idx [int],
             mod mode index [int], harmonics [int]) """

    def __init__(self, id_, parent=None):
        super().__init__(parent)

        # add labels
        self.lblNo = QtWidgets.QLabel(str(id_))
        self.lblStartF = QtWidgets.QLabel()
        self.lblStartF.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
        self.lblStopF = QtWidgets.QLabel()
        self.lblStopF.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
        self.lblStep = QtWidgets.QLabel()
        self.lblStep.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
        self.lblBuffer = QtWidgets.QLabel()
        self.lblBuffer.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
        self.lblPress = QtWidgets.QLabel()
        self.lblPress.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
        # set text color to grey
        self.set_color_grey()

    def set_item(self, setting: AbsScanSetting):
        self.lblStartF.setText(f'{setting.freq_start:.1f}')
        self.lblStopF.setText(f'{setting.freq_stop:.1f}')
        if setting.freq_step >= 1:
            self.lblStep.setText(f'{setting.freq_step:.4f} MHz')
        else:
            self.lblStep.setText(f'{setting.freq_step:.1f} kHz')
        self.lblBuffer.setText(f'{setting.buffer_len}')
        self.lblPress.setText(f'{setting.press:.1f} μBar')
        # by default set text to grey
        self.set_color_grey()

    def set_color_grey(self):
        """ set text color to grey """
        self.lblNo.setStyleSheet('color: grey')
        self.lblStartF.setStyleSheet('color: grey')
        self.lblStopF.setStyleSheet('color: grey')
        self.lblStep.setStyleSheet('color: grey')
        self.lblBuffer.setStyleSheet('color: grey')
        self.lblPress.setStyleSheet('color: grey')

    def set_color_black(self):
        """ Set text color to black """

        # set texts to grey
        self.lblNo.setStyleSheet('color: black')
        self.lblStartF.setStyleSheet('color: black')
        self.lblStopF.setStyleSheet('color: black')
        self.lblStep.setStyleSheet('color: black')
        self.lblBuffer.setStyleSheet('color: black')
        self.lblPress.setStyleSheet('color: black')

    def delete(self):
        self.lblNo.deleteLater()
        self.lblStartF.deleteLater()
        self.lblStopF.deleteLater()
        self.lblStep.deleteLater()
        self.lblBuffer.deleteLater()
        self.lblPress.deleteLater()
        self.deleteLater()
