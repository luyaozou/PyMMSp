#! encoding = utf-8
''' Dialog windows for system menues '''


from PyQt6 import QtGui, QtCore, QtWidgets
from PyMMSp.inst import general as api_gen
from PyMMSp.data import lwaparser
from PyMMSp.ui import SharedWidgets as Shared
from pyqtgraph import siFormat
import pyqtgraph as pg


class SelInstDialog(QtWidgets.QDialog):
    '''
        Dialog window for instrument selection.
    '''

    def __init__(self, parent):
        QtWidgets.QDialog.__init__(self, parent)
        self.parent = parent
        self.setMinimumWidth(400)
        self.setMinimumHeight(400)
        self.setWindowTitle('Select Instrument')

        refreshButton = QtWidgets.QPushButton('Refresh Available Instrument List')
        acceptButton = QtWidgets.QPushButton(Shared.btn_label('confirm'))
        cancelButton = QtWidgets.QPushButton(Shared.btn_label('reject'))

        self.availableInst = QtWidgets.QLabel()
        instList, instStr = api_gen.list_inst()
        self.availableInst.setText(instStr)

        selInst = QtWidgets.QWidget()
        selInstLayout = QtWidgets.QFormLayout()
        self.selSyn = QtWidgets.QComboBox()
        self.selSyn.addItems(['N.A.'])
        self.selSyn.addItems(instList)
        self.selLockin = QtWidgets.QComboBox()
        self.selLockin.addItems(['N.A.'])
        self.selLockin.addItems(instList)
        self.selScope = QtWidgets.QComboBox()
        self.selScope.addItems(['N.A.'])
        self.selScope.addItems(instList)
        self.selMotor = QtWidgets.QComboBox()
        self.selMotor.addItems(['N.A.'])
        self.selMotor.addItems(instList)
        self.selPressure = QtWidgets.QComboBox()
        self.selPressure.addItems(['N.A.'])
        self.selPressure.addItems(instList)
        selInstLayout.addRow(QtWidgets.QLabel('Synthesizer'), self.selSyn)
        selInstLayout.addRow(QtWidgets.QLabel('Lock-in'), self.selLockin)
        selInstLayout.addRow(QtWidgets.QLabel('Oscilloscope'), self.selScope)
        selInstLayout.addRow(QtWidgets.QLabel('Step Motor'), self.selMotor)
        selInstLayout.addRow(QtWidgets.QLabel('CENTER TWO Pressure Readout'), self.selPressure)
        selInst.setLayout(selInstLayout)

        # Set main layout
        mainLayout = QtWidgets.QGridLayout()
        mainLayout.addWidget(self.availableInst, 0, 0, 1, 2)
        mainLayout.addWidget(refreshButton, 1, 0, 1, 2)
        mainLayout.addWidget(selInst, 2, 0, 1, 2)
        mainLayout.addWidget(cancelButton, 3, 0)
        mainLayout.addWidget(acceptButton, 3, 1)

        self.setLayout(mainLayout)

        refreshButton.clicked.connect(self.refresh)
        cancelButton.clicked.connect(self.reject)
        acceptButton.clicked.connect(self.accept)

    def refresh(self):
        ''' Refresh instrument list '''

        # refresh avaiable instrument list
        instList, instStr = api_gen.list_inst()
        self.availableInst.setText(instStr)

        # refresh QComboBoxes
        item_count = self.selSyn.count()
        # remove all items but the first one
        for i in range(item_count-1):
            # Because Qt automatically update the index, this loop needs to
            # keep deleting the 'second' item, whose index is 1
            self.selSyn.removeItem(1)
            self.selLockin.removeItem(1)
            self.selScope.removeItem(1)
            self.selMotor.removeItem(1)
            self.selPressure.removeItem(1)
        self.selSyn.addItems(instList)
        self.selLockin.addItems(instList)
        self.selScope.addItems(instList)
        self.selMotor.addItems(instList)
        self.selPressure.addItems(instList)

    def accept(self):

        # close old instrument handles
        api_gen.close_inst(self.parent.synHandle,
                           self.parent.liaHandle,
                           self.parent.pciHandle,
                           self.parent.motorHandle,
                           self.parent.pressureHandle)

        # open new instrument handles
        self.parent.synHandle = api_gen.open_inst(self.selSyn.currentText())
        self.parent.liaHandle = api_gen.open_inst(self.selLockin.currentText())
        self.parent.pciHandle = api_gen.open_inst(self.selScope.currentText())
        self.parent.motorHandle = api_gen.open_inst(self.selMotor.currentText())
        self.parent.pressureHandle = api_gen.open_inst(self.selPressure.currentText())

        self.done(True)


class ViewInstDialog(QtWidgets.QDialog):
    '''
        Dialog window for instrument status view
    '''

    def __init__(self, parent):
        QtWidgets.QDialog.__init__(self, parent)

        self.setMinimumWidth(400)
        self.setMinimumHeight(400)
        self.setWindowTitle('View Instrument Status')


class ViewPG(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle('ViewPG PCI')


class CloseSelInstDialog(QtWidgets.QDialog):
    '''
        Dialog window for closing selected instrument.
    '''

    def __init__(self, parent):
        QtWidgets.QDialog.__init__(self, parent)
        self.parent = parent
        self.setMinimumWidth(400)
        self.setMinimumHeight(400)
        self.setWindowTitle('Close Instrument')

        inst = QtWidgets.QWidget()
        self.synToggle = QtWidgets.QCheckBox()
        self.liaToggle = QtWidgets.QCheckBox()
        self.pciToggle = QtWidgets.QCheckBox()
        self.motorToggle = QtWidgets.QCheckBox()
        self.pressureToggle = QtWidgets.QCheckBox()

        instLayout = QtWidgets.QFormLayout()
        instLayout.addRow(QtWidgets.QLabel('Instrument'), QtWidgets.QLabel('Status'))
        # only list currently connected instruments
        if self.parent.synHandle:
            self.synToggle.setCheckState(QtCore.Qt.CheckState.Checked)
            instLayout.addRow(QtWidgets.QLabel('Synthesizer'), self.synToggle)
        else:
            self.synToggle.setCheckState(QtCore.Qt.CheckState.Unchecked)

        if self.parent.liaHandle:
            self.liaToggle.setCheckState(QtCore.Qt.CheckState.Checked)
            instLayout.addRow(QtWidgets.QLabel('Lockin'), self.liaToggle)
        else:
            self.liaToggle.setCheckState(QtCore.Qt.CheckState.Unchecked)

        if self.parent.pciHandle:
            self.pciToggle.setCheckState(QtCore.Qt.CheckState.Checked)
            instLayout.addRow(QtWidgets.QLabel('Oscilloscope'), self.pciToggle)
        else:
            self.pciToggle.setCheckState(QtCore.Qt.CheckState.Unchecked)

        if self.parent.motorHandle:
            self.motorToggle.setCheckState(QtCore.Qt.CheckState.Checked)
            instLayout.addRow(QtWidgets.QLabel('Motor'), self.motorToggle)
        else:
            self.motorToggle.setCheckState(QtCore.Qt.CheckState.Unchecked)

        if self.parent.pressureHandle:
            self.pressureToggle.setCheckState(QtCore.Qt.CheckState.Checked)
            instLayout.addRow(QtWidgets.QLabel('Pressure Readout'), self.pressureToggle)
        else:
            self.pressureToggle.setCheckState(QtCore.Qt.CheckState.Unchecked)

        inst.setLayout(instLayout)

        okButton = QtWidgets.QPushButton(Shared.btn_label('complete'))
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(inst)
        mainLayout.addWidget(QtWidgets.QLabel('No command will be sent before you hit the accept button'))
        mainLayout.addWidget(okButton)
        self.setLayout(mainLayout)

        okButton.clicked.connect(self.accept)

    def close_inst_handle(self, inst_handle, check_state):

        if check_state and inst_handle:
            api_gen.close_inst(inst_handle)
            return None
        else:
            return inst_handle

    def accept(self):

        self.parent.synHandle = self.close_inst_handle(self.parent.synHandle,
                                                       self.synToggle.isChecked())
        self.parent.liaHandle = self.close_inst_handle(self.parent.liaHandle,
                                                       self.liaToggle.isChecked())
        self.parent.pciHandle = self.close_inst_handle(self.parent.pciHandle,
                                                       self.pciToggle.isChecked())
        self.parent.motorHandle = self.close_inst_handle(self.parent.motorHandle,
                                                         self.motorToggle.isChecked())
        self.parent.pressureHandle = self.close_inst_handle(self.parent.pressureHandle,
                                                            self.pressureToggle.isChecked())
        self.close()


class SynInfoDialog(QtWidgets.QDialog):
    '''
        Dialog window for displaying full synthesizer settings.
    '''

    def __init__(self, parent):
        QtWidgets.QDialog.__init__(self, parent)
        self.parent = parent
        self.setMinimumWidth(800)
        self.setMinimumHeight(400)
        self.setWindowTitle('Synthesizer Settings')

        self.instGroup = QtWidgets.QGroupBox()
        self.rfGroup = QtWidgets.QGroupBox()
        self.modGroup = QtWidgets.QGroupBox()

        self.instGroup.setTitle('Instrument Session')
        self.instNameLabel = QtWidgets.QLabel()
        self.instInterfaceLabel = QtWidgets.QLabel()
        self.instInterfaceNumLabel = QtWidgets.QLabel()
        self.instRemoteDispLabel = QtWidgets.QLabel()
        instGroupLayout = QtWidgets.QFormLayout()
        instGroupLayout.addRow(QtWidgets.QLabel('Instrument Name'), self.instNameLabel)
        instGroupLayout.addRow(QtWidgets.QLabel('Interface Type'), self.instInterfaceLabel)
        instGroupLayout.addRow(QtWidgets.QLabel('Interface Number'), self.instInterfaceNumLabel)
        instGroupLayout.addRow(QtWidgets.QLabel('Remote Display'), self.instRemoteDispLabel)
        self.instGroup.setLayout(instGroupLayout)

        self.rfGroup.setTitle('RF Settings')
        self.rfOutputLabel = QtWidgets.QLabel()
        self.modOutputLabel = QtWidgets.QLabel()
        self.synFreqLabel = QtWidgets.QLabel()
        rfGroupLayout = QtWidgets.QGridLayout()
        rfGroupLayout.addWidget(QtWidgets.QLabel('RF Output'), 0, 0)
        rfGroupLayout.addWidget(self.rfOutputLabel, 0, 1)
        rfGroupLayout.addWidget(QtWidgets.QLabel('Synth Frequency'), 0, 2)
        rfGroupLayout.addWidget(self.synFreqLabel, 0, 3)
        rfGroupLayout.addWidget(QtWidgets.QLabel('Modulation Output'), 0, 4)
        rfGroupLayout.addWidget(self.modOutputLabel, 0, 5)
        self.rfGroup.setLayout(rfGroupLayout)

        self.modGroup.setTitle('Modulation Settings')
        self.am1StateLabel = QtWidgets.QLabel()
        self.am2StateLabel = QtWidgets.QLabel()
        self.fm1StateLabel = QtWidgets.QLabel()
        self.fm2StateLabel = QtWidgets.QLabel()
        self.pm1StateLabel = QtWidgets.QLabel()
        self.pm2StateLabel = QtWidgets.QLabel()
        self.lfStateLabel = QtWidgets.QLabel()
        self.am1DepthLabel = QtWidgets.QLabel()
        self.am2DepthLabel = QtWidgets.QLabel()
        self.fm1DevLabel = QtWidgets.QLabel()
        self.fm2DevLabel = QtWidgets.QLabel()
        self.pm1DevLabel = QtWidgets.QLabel()
        self.pm2DevLabel = QtWidgets.QLabel()
        self.lfVolLabel = QtWidgets.QLabel()
        self.am1SrcLabel = QtWidgets.QLabel()
        self.am2SrcLabel = QtWidgets.QLabel()
        self.fm1SrcLabel = QtWidgets.QLabel()
        self.fm2SrcLabel = QtWidgets.QLabel()
        self.pm1SrcLabel = QtWidgets.QLabel()
        self.pm2SrcLabel = QtWidgets.QLabel()
        self.lfSrcLabel = QtWidgets.QLabel()
        self.am1FreqLabel = QtWidgets.QLabel()
        self.am2FreqLabel = QtWidgets.QLabel()
        self.fm1FreqLabel = QtWidgets.QLabel()
        self.fm2FreqLabel = QtWidgets.QLabel()
        self.pm1FreqLabel = QtWidgets.QLabel()
        self.pm2FreqLabel = QtWidgets.QLabel()
        self.am1WaveLabel = QtWidgets.QLabel()
        self.am2WaveLabel = QtWidgets.QLabel()
        self.fm1WaveLabel = QtWidgets.QLabel()
        self.fm2WaveLabel = QtWidgets.QLabel()
        self.pm1WaveLabel = QtWidgets.QLabel()
        self.pm2WaveLabel = QtWidgets.QLabel()

        modGroupLayout = QtWidgets.QGridLayout()
        modGroupLayout.addWidget(QtWidgets.QLabel('Channel'), 0, 0)
        modGroupLayout.addWidget(QtWidgets.QLabel('Source'), 0, 1)
        modGroupLayout.addWidget(QtWidgets.QLabel('State'), 0, 2)
        modGroupLayout.addWidget(QtWidgets.QLabel('Depth/Dev'), 0, 3)
        modGroupLayout.addWidget(QtWidgets.QLabel('Rate'), 0, 4)
        modGroupLayout.addWidget(QtWidgets.QLabel('Waveform'), 0, 5)
        modGroupLayout.addWidget(QtWidgets.QLabel('AM1'), 1, 0)
        modGroupLayout.addWidget(self.am1StateLabel, 1, 1)
        modGroupLayout.addWidget(self.am1SrcLabel, 1, 2)
        modGroupLayout.addWidget(self.am1DepthLabel, 1, 3)
        modGroupLayout.addWidget(self.am1FreqLabel, 1, 4)
        modGroupLayout.addWidget(self.am1WaveLabel, 1, 5)
        modGroupLayout.addWidget(QtWidgets.QLabel('AM2'), 2, 0)
        modGroupLayout.addWidget(self.am2StateLabel, 2, 1)
        modGroupLayout.addWidget(self.am2SrcLabel, 2, 2)
        modGroupLayout.addWidget(self.am2DepthLabel, 2, 3)
        modGroupLayout.addWidget(self.am2FreqLabel, 2, 4)
        modGroupLayout.addWidget(self.am2WaveLabel, 2, 5)
        modGroupLayout.addWidget(QtWidgets.QLabel('FM1'), 3, 0)
        modGroupLayout.addWidget(self.fm1StateLabel, 3, 1)
        modGroupLayout.addWidget(self.fm1SrcLabel, 3, 2)
        modGroupLayout.addWidget(self.fm1DevLabel, 3, 3)
        modGroupLayout.addWidget(self.fm1FreqLabel, 3, 4)
        modGroupLayout.addWidget(self.fm1WaveLabel, 3, 5)
        modGroupLayout.addWidget(QtWidgets.QLabel('FM2'), 4, 0)
        modGroupLayout.addWidget(self.fm2StateLabel, 4, 1)
        modGroupLayout.addWidget(self.fm2SrcLabel, 4, 2)
        modGroupLayout.addWidget(self.fm2DevLabel, 4, 3)
        modGroupLayout.addWidget(self.fm2FreqLabel, 4, 4)
        modGroupLayout.addWidget(self.fm2WaveLabel, 4, 5)
        modGroupLayout.addWidget(QtWidgets.QLabel('φM1'), 5, 0)
        modGroupLayout.addWidget(self.pm1StateLabel, 5, 1)
        modGroupLayout.addWidget(self.pm1SrcLabel, 5, 2)
        modGroupLayout.addWidget(self.pm1DevLabel, 5, 3)
        modGroupLayout.addWidget(self.pm1FreqLabel, 5, 4)
        modGroupLayout.addWidget(self.pm1WaveLabel, 5, 5)
        modGroupLayout.addWidget(QtWidgets.QLabel('φM2'), 6, 0)
        modGroupLayout.addWidget(self.pm2StateLabel, 6, 1)
        modGroupLayout.addWidget(self.pm2SrcLabel, 6, 2)
        modGroupLayout.addWidget(self.pm2DevLabel, 6, 3)
        modGroupLayout.addWidget(self.pm2FreqLabel, 6, 4)
        modGroupLayout.addWidget(self.pm2WaveLabel, 6, 5)
        modGroupLayout.addWidget(QtWidgets.QLabel('LF OUT'), 7, 0)
        modGroupLayout.addWidget(self.lfStateLabel, 7, 1)
        modGroupLayout.addWidget(self.lfSrcLabel, 7, 2)
        modGroupLayout.addWidget(self.lfVolLabel, 7, 3)
        self.modGroup.setLayout(modGroupLayout)

        self.refreshButton = QtWidgets.QPushButton('Manual Refresh')
        self.acceptButton = QtWidgets.QPushButton(Shared.btn_label('accept'))

        mainLayout = QtWidgets.QGridLayout()
        mainLayout.addWidget(self.instGroup, 0, 0, 1, 5)
        mainLayout.addWidget(self.rfGroup, 1, 0, 1, 5)
        mainLayout.addWidget(self.modGroup, 2, 0, 1, 5)
        mainLayout.addWidget(self.acceptButton, 3, 2, 1, 1)
        self.setLayout(mainLayout)

        self.refreshButton.clicked.connect(self.manual_refresh)
        self.acceptButton.clicked.connect(self.accept)

    def display(self):

        self.acceptButton.setText(Shared.btn_label('accept'))

        if self.parent.synHandle:
            self.print_info()
            self.instGroup.show()
            self.rfGroup.show()
            self.modGroup.show()
        else:
            self.instGroup.hide()
            self.rfGroup.hide()
            self.modGroup.hide()

        self.exec()

    def manual_refresh(self):

        self.parent.synInfo.full_info_query(self.parent.synHandle)
        self.print_info()

    def print_info(self):

        # update instrument panel
        self.instNameLabel.setText(self.parent.synInfo.instName)
        self.instInterfaceLabel.setText(self.parent.synInfo.instInterface)
        self.instInterfaceNumLabel.setText(str(self.parent.synInfo.instInterfaceNum))
        self.instRemoteDispLabel.setText('ON' if self.parent.synInfo.instRemoteDisp else 'OFF')

        # update RF setting panel
        self.rfOutputLabel.setText('ON' if self.parent.synInfo.rfToggle else 'OFF')
        self.modOutputLabel.setText('ON' if self.parent.synInfo.modToggle else 'OFF')
        self.synFreqLabel.setText('{:.9f} MHz'.format(self.parent.synInfo.synFreq * 1e-6))

        # update modulation setting panel
        self.am1StateLabel.setText('ON' if self.parent.synInfo.AM1Toggle else 'OFF')
        self.am1SrcLabel.setText(self.parent.synInfo.AM1Src)
        self.am1DepthLabel.setText('{:.1f}% ({:.0f} dB)'.format(self.parent.synInfo.AM1DepthPercent, self.parent.synInfo.AM1DepthDbm))
        self.am1FreqLabel.setText(siFormat(self.parent.synInfo.AM1Freq, suffix='Hz'))
        self.am1WaveLabel.setText(self.parent.synInfo.AM1Wave)

        self.am2StateLabel.setText('ON' if self.parent.synInfo.AM2Toggle else 'OFF')
        self.am2SrcLabel.setText(self.parent.synInfo.AM2Src)
        self.am2DepthLabel.setText('{:.1f}% ({:.0f} dB)'.format(self.parent.synInfo.AM2DepthPercent, self.parent.synInfo.AM2DepthDbm))
        self.am2FreqLabel.setText(siFormat(self.parent.synInfo.AM2Freq, suffix='Hz'))
        self.am2WaveLabel.setText(self.parent.synInfo.AM2Wave)

        self.fm1StateLabel.setText('ON' if self.parent.synInfo.FM1Toggle else 'OFF')
        self.fm1SrcLabel.setText(self.parent.synInfo.FM1Src)
        self.fm1DevLabel.setText(siFormat(self.parent.synInfo.FM1Dev, suffix='Hz'))
        self.fm1FreqLabel.setText(siFormat(self.parent.synInfo.FM1Freq, suffix='Hz'))
        self.fm1WaveLabel.setText(self.parent.synInfo.FM1Wave)

        self.fm2StateLabel.setText('ON' if self.parent.synInfo.FM2Toggle else 'OFF')
        self.fm2SrcLabel.setText(self.parent.synInfo.FM2Src)
        self.fm2DevLabel.setText(siFormat(self.parent.synInfo.FM2Dev, suffix='Hz'))
        self.fm2FreqLabel.setText(siFormat(self.parent.synInfo.FM2Freq, suffix='Hz'))
        self.fm2WaveLabel.setText(self.parent.synInfo.FM2Wave)

        self.pm1StateLabel.setText('ON' if self.parent.synInfo.PM1Toggle else 'OFF')
        self.pm1SrcLabel.setText(self.parent.synInfo.PM1Src)
        self.pm1DevLabel.setText(siFormat(self.parent.synInfo.PM1Dev, suffix='rad'))
        self.pm1FreqLabel.setText(siFormat(self.parent.synInfo.PM1Freq, suffix='Hz'))
        self.pm1WaveLabel.setText(self.parent.synInfo.PM1Wave)

        self.pm2StateLabel.setText('ON' if self.parent.synInfo.PM2Toggle else 'OFF')
        self.pm2SrcLabel.setText(self.parent.synInfo.PM2Src)
        self.pm2DevLabel.setText(siFormat(self.parent.synInfo.PM2Dev, suffix='rad'))
        self.pm2FreqLabel.setText(siFormat(self.parent.synInfo.PM2Freq,  suffix='Hz'))
        self.pm2WaveLabel.setText(self.parent.synInfo.PM2Wave)

        self.lfStateLabel.setText('ON' if self.parent.synInfo.LFToggle else 'OFF')
        self.lfSrcLabel.setText(self.parent.synInfo.LFSrc)
        self.lfVolLabel.setText(siFormat(self.parent.synInfo.LFVoltage, suffix='V'))


class LockinInfoDialog(QtWidgets.QDialog):
    '''
        Dialog window for displaying full lockin settings.
    '''

    def __init__(self, parent):
        QtWidgets.QDialog.__init__(self, parent)
        self.parent = parent
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        self.setWindowTitle('Lockin Amplifier Settings')

        self.instGroup = QtWidgets.QGroupBox()
        self.refGroup = QtWidgets.QGroupBox()
        self.inputGroup = QtWidgets.QGroupBox()
        self.gainGroup = QtWidgets.QGroupBox()
        self.outputGroup = QtWidgets.QGroupBox()

        self.instGroup.setTitle('Instrument Session')
        self.instNameLabel = QtWidgets.QLabel()
        self.instInterfaceLabel = QtWidgets.QLabel()
        self.instInterfaceNumLabel = QtWidgets.QLabel()
        instGroupLayout = QtWidgets.QFormLayout()
        instGroupLayout.addRow(QtWidgets.QLabel('Instrument Name'), self.instNameLabel)
        instGroupLayout.addRow(QtWidgets.QLabel('Interface Type'), self.instInterfaceLabel)
        instGroupLayout.addRow(QtWidgets.QLabel('Interface Number'), self.instInterfaceNumLabel)
        self.instGroup.setLayout(instGroupLayout)

        self.refGroup.setTitle('Reference and Phase')
        self.refSrcLabel = QtWidgets.QLabel()
        self.refFreqLabel = QtWidgets.QLabel()
        self.refHarmLabel = QtWidgets.QLabel()
        self.refPhaseLabel = QtWidgets.QLabel()
        refGroupLayout =  QtWidgets.QFormLayout()
        refGroupLayout.addRow(QtWidgets.QLabel('Reference Source'), self.refSrcLabel)
        refGroupLayout.addRow(QtWidgets.QLabel('Reference Freq'), self.refFreqLabel)
        refGroupLayout.addRow(QtWidgets.QLabel('Harmonics'), self.refHarmLabel)
        refGroupLayout.addRow(QtWidgets.QLabel('Phase'), self.refPhaseLabel)
        self.refGroup.setLayout(refGroupLayout)

        self.inputGroup.setTitle('Input and Filter')
        self.inputConfigLabel = QtWidgets.QLabel()
        self.inputGroundingLabel = QtWidgets.QLabel()
        self.inputCoupleLabel = QtWidgets.QLabel()
        self.inputFilterLabel = QtWidgets.QLabel()
        inputGroupLayout = QtWidgets.QFormLayout()
        inputGroupLayout.addRow(QtWidgets.QLabel('Input Config'), self.inputConfigLabel)
        inputGroupLayout.addRow(QtWidgets.QLabel('Input Grounding'), self.inputGroundingLabel)
        inputGroupLayout.addRow(QtWidgets.QLabel('Input Coupling'), self.inputCoupleLabel)
        inputGroupLayout.addRow(QtWidgets.QLabel('Input Filter'), self.inputFilterLabel)
        self.inputGroup.setLayout(inputGroupLayout)

        self.gainGroup.setTitle('Gain')
        self.gainSensLabel = QtWidgets.QLabel()
        self.gainReserveLabel = QtWidgets.QLabel()
        self.gainTCLabel = QtWidgets.QLabel()
        self.lpSlopeLabel = QtWidgets.QLabel()
        gainGroupLayout = QtWidgets.QFormLayout()
        gainGroupLayout.addRow(QtWidgets.QLabel('Sensitivity'), self.gainSensLabel)
        gainGroupLayout.addRow(QtWidgets.QLabel('Time Constant'), self.gainTCLabel)
        gainGroupLayout.addRow(QtWidgets.QLabel('Reserve'), self.gainReserveLabel)
        gainGroupLayout.addRow(QtWidgets.QLabel('Low-pass Filter Slope'), self.lpSlopeLabel)
        self.gainGroup.setLayout(gainGroupLayout)

        self.outputGroup.setTitle('Display and Output')
        self.outputDisp1Label = QtWidgets.QLabel()
        self.outputDisp2Label = QtWidgets.QLabel()
        self.outputFront1Label = QtWidgets.QLabel()
        self.outputFront2Label = QtWidgets.QLabel()
        self.outputSRateLabel = QtWidgets.QLabel()
        outputGroupLayout = QtWidgets.QGridLayout()
        outputGroupLayout.addWidget(QtWidgets.QLabel('Chanel 1'), 0, 1)
        outputGroupLayout.addWidget(QtWidgets.QLabel('Chanel 2'), 0, 2)
        outputGroupLayout.addWidget(QtWidgets.QLabel('Display Output'), 1, 0)
        outputGroupLayout.addWidget(self.outputDisp1Label, 1, 1)
        outputGroupLayout.addWidget(self.outputDisp2Label, 1, 2)
        outputGroupLayout.addWidget(QtWidgets.QLabel('Front Panel Output'), 2, 0)
        outputGroupLayout.addWidget(self.outputFront1Label, 2, 1)
        outputGroupLayout.addWidget(self.outputFront2Label, 2, 2)
        outputGroupLayout.addWidget(QtWidgets.QLabel('Sampling Rate'), 3, 0)
        outputGroupLayout.addWidget(self.outputSRateLabel, 3, 1, 1, 2)
        self.outputGroup.setLayout(outputGroupLayout)

        self.refreshButton = QtWidgets.QPushButton('Manual Refresh')
        self.acceptButton = QtWidgets.QPushButton(Shared.btn_label('accept'))

        mainLayout = QtWidgets.QGridLayout()
        mainLayout.addWidget(self.instGroup, 0, 0, 1, 6)
        mainLayout.addWidget(self.inputGroup, 1, 0, 1, 3)
        mainLayout.addWidget(self.outputGroup, 1, 3, 1, 3)
        mainLayout.addWidget(self.refGroup, 2, 0, 1, 3)
        mainLayout.addWidget(self.gainGroup, 2, 3, 1, 3)
        mainLayout.addWidget(self.acceptButton, 3, 2, 1, 2)
        self.setLayout(mainLayout)

        self.refreshButton.clicked.connect(self.manual_refresh)
        self.acceptButton.clicked.connect(self.accept)

    def display(self):

        self.acceptButton.setText(Shared.btn_label('accept'))

        if self.parent.liaHandle:
            self.print_info()
            self.instGroup.show()
            self.refGroup.show()
            self.gainGroup.show()
            self.inputGroup.show()
            self.outputGroup.show()
        else:
            self.instGroup.hide()
            self.refGroup.hide()
            self.gainGroup.hide()
            self.inputGroup.hide()
            self.outputGroup.hide()

        self.exec()

    def manual_refresh(self):

        self.parent.synInfo.full_info_query(self.parent.liaHandle)
        self.print_info()

    def print_info(self):

        # update instrument panel
        self.instNameLabel.setText(self.parent.liaInfo.instName)
        self.instInterfaceLabel.setText(self.parent.liaInfo.instInterface)
        self.instInterfaceNumLabel.setText(str(self.parent.liaInfo.instInterfaceNum))

        # update ref group
        self.refSrcLabel.setText(self.parent.liaInfo.refSrcText)
        self.refFreqLabel.setText(siFormat(self.parent.liaInfo.refFreq, suffix='Hz'))
        self.refHarmLabel.setText('{:d}'.format(self.parent.liaInfo.refHarm))
        self.refPhaseLabel.setText('{:.2f} deg'.format(self.parent.liaInfo.refPhase))

        # update input group
        self.inputConfigLabel.setText(self.parent.liaInfo.configText)
        self.inputGroundingLabel.setText(self.parent.liaInfo.groundingText)
        self.inputCoupleLabel.setText(self.parent.liaInfo.coupleText)
        self.inputFilterLabel.setText(self.parent.liaInfo.inputFilterText)

        # update gain group
        self.gainSensLabel.setText(self.parent.liaInfo.sensText)
        self.gainTCLabel.setText(self.parent.liaInfo.tcText)
        self.gainReserveLabel.setText(self.parent.liaInfo.reserveText)
        self.lpSlopeLabel.setText(self.parent.liaInfo.lpSlopeText)

        # update output group
        self.outputDisp1Label.setText(self.parent.liaInfo.disp1Text)
        self.outputDisp2Label.setText(self.parent.liaInfo.disp2Text)
        self.outputFront1Label.setText(self.parent.liaInfo.front1Text)
        self.outputFront2Label.setText(self.parent.liaInfo.front2Text)
        self.outputSRateLabel.setText(self.parent.liaInfo.sampleRateText)


class LWAParserDialog(QtWidgets.QDialog):
    '''
        Dialog window for the LWA file previewer & parser.
    '''

    def __init__(self, parent, filename):
        QtWidgets.QDialog.__init__(self, parent)
        self.parent = parent
        self.filename = filename
        self.setMinimumWidth(1200)
        self.setMinimumHeight(600)
        self.setWindowTitle('LWA Preview & Parser')
        self.entry_id_to_export = []
        self.preview_win = PrevSpectrumDialog(self)

        self.mainLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.mainLayout.addWidget(QtWidgets.QLabel('Source file: {:s}'.format(filename)))

        # read lwa batch scan entry from file
        self.entry_settings, self.hd_line_num = lwaparser.scan_header(filename)

        if self.entry_settings:
            # set top buttons
            topButtons = QtWidgets.QWidget()
            self.exportLWAButton = QtWidgets.QPushButton('Export (LWA Format)')
            self.exportLWAButton.clicked.connect(self.export_lwa)
            self.exportXYButton = QtWidgets.QPushButton('Export (XY Format)')
            self.exportXYButton.clicked.connect(self.export_xy)
            self.openFileButton = QtWidgets.QPushButton('Open New File')
            self.openFileButton.clicked.connect(self.open_new_file)
            topButtonLayout = QtWidgets.QHBoxLayout()
            topButtonLayout.addWidget(self.exportLWAButton)
            topButtonLayout.addWidget(self.exportXYButton)
            topButtonLayout.addWidget(self.openFileButton)
            topButtons.setLayout(topButtonLayout)
            self.mainLayout.addWidget(topButtons)

            # set up QButtonGroup to manage checkboxes
            self.previewButtonGroup = QtGui.QButtonGroup()
            self.previewButtonGroup.setExclusive(True)
            self.exportLWAButtonGroup = QtGui.QButtonGroup()
            self.exportLWAButtonGroup.setExclusive(False)
            # set up the batch list area
            self.batchListWidget = QtWidgets.QWidget()
            batchArea = QtGui.QScrollArea()
            batchArea.setWidgetResizable(True)
            batchArea.setWidget(self.batchListWidget)

            self.batchLayout = QtWidgets.QGridLayout()
            self.batchLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
            # row of names
            self.batchLayout.addWidget(QtWidgets.QLabel('Preview'), 0, 0)
            self.batchLayout.addWidget(QtWidgets.QLabel('Export'), 0, 1)
            self.batchLayout.addWidget(QtWidgets.QLabel('Scan #'), 0, 2)
            self.batchLayout.addWidget(QtWidgets.QLabel('Comment'), 0, 3)
            self.batchLayout.addWidget(QtWidgets.QLabel('Date'), 0, 4)
            self.batchLayout.addWidget(QtWidgets.QLabel('Time'), 0, 5)
            self.batchLayout.addWidget(QtWidgets.QLabel('Start Freq (MHz)'), 0, 6)
            self.batchLayout.addWidget(QtWidgets.QLabel('Stop Freq (MHz)'), 0, 7)
            self.batchLayout.addWidget(QtWidgets.QLabel('Step Freq'), 0, 8)
            self.batchLayout.addWidget(QtWidgets.QLabel('Points'), 0, 9)
            self.batchLayout.addWidget(QtWidgets.QLabel('Average'), 0, 10)
            self.batchLayout.addWidget(QtWidgets.QLabel('Sensitivity'), 0, 11)
            self.batchLayout.addWidget(QtWidgets.QLabel('Time Const'), 0, 12)
            self.batchLayout.addWidget(QtWidgets.QLabel('Wait Time'), 0, 13)
            self.batchLayout.addWidget(QtWidgets.QLabel('Modulation'), 0, 14)
            self.batchLayout.addWidget(QtWidgets.QLabel('Harmonics'), 0, 15)
            self.batchLayout.addWidget(QtWidgets.QLabel('Mod Freq'), 0, 16)
            self.batchLayout.addWidget(QtWidgets.QLabel('Mod Amp'), 0, 17)
            self.batchLayout.addWidget(QtWidgets.QLabel('Phase'), 0, 18)

            for row in range(len(self.entry_settings)):
                current_setting = self.entry_settings[row]
                entry = Shared.LWAScanHdEntry(self, entry_setting=current_setting)
                # add entry number checkbox to the button group
                self.previewButtonGroup.addButton(entry.previewCheck, row)
                self.exportLWAButtonGroup.addButton(entry.exportCheck, row)
                # add widgets to the dispaly panel layout
                self.batchLayout.addWidget(entry.previewCheck, row+1, 0)
                self.batchLayout.addWidget(entry.exportCheck, row+1, 1)
                self.batchLayout.addWidget(entry.scanNumLabel, row+1, 2)
                self.batchLayout.addWidget(entry.commentLabel, row+1, 3)
                self.batchLayout.addWidget(entry.dateLabel, row+1, 4)
                self.batchLayout.addWidget(entry.timeLabel, row+1, 5)
                self.batchLayout.addWidget(entry.startFreqLabel, row+1, 6)
                self.batchLayout.addWidget(entry.stopFreqLabel, row+1, 7)
                self.batchLayout.addWidget(entry.stepLabel, row+1, 8)
                self.batchLayout.addWidget(entry.ptsLabel, row+1, 9)
                self.batchLayout.addWidget(entry.avgLabel, row+1, 10)
                self.batchLayout.addWidget(entry.sensLabel, row+1, 11)
                self.batchLayout.addWidget(entry.tcLabel, row+1, 12)
                self.batchLayout.addWidget(entry.itLabel, row+1, 13)
                self.batchLayout.addWidget(entry.modModeLabel, row+1, 14)
                self.batchLayout.addWidget(entry.harmLabel, row+1, 15)
                self.batchLayout.addWidget(entry.modFreqLabel, row+1, 16)
                self.batchLayout.addWidget(entry.modAmpLabel, row+1, 17)
                self.batchLayout.addWidget(entry.phaseLabel, row+1, 18)

            self.batchListWidget.setLayout(self.batchLayout)
            self.mainLayout.addWidget(batchArea)
            self.previewButtonGroup.buttonToggled.connect(self.preview_entry)
            self.exportLWAButtonGroup.buttonClicked[int].connect(self.add_to_export_list)
        else:
            self.mainLayout.addWidget(QtWidgets.QLabel('Invalid file! No scans found.'))

        self.setLayout(self.mainLayout)

    def preview_entry(self):
        ''' Preview single scan '''

        id_ = self.previewButtonGroup.checkedId()
        preview_data = lwaparser.preview(id_, self.hd_line_num, src=self.filename)
        self.preview_win.setData(preview_data)
        self.preview_win.show()

    def add_to_export_list(self, id_):
        ''' Add checked buttons to export list. id_ starts at 0 '''

        # if the button is checked, add to export list
        if self.exportLWAButtonGroup.button(id_).isChecked():
            # check if id is already in the list
            if id_ in self.entry_id_to_export:
                pass
            else:
                self.entry_id_to_export.append(id_)
        # if the button is unchecked, remove from export list
        else:
            # check if id is already in the list
            if id_ in self.entry_id_to_export:
                self.entry_id_to_export.remove(id_)
            else:
                pass

    def export_lwa(self):
        ''' Export to new lwa file '''

        # check if entry_id_to_export list is not empty
        if self.entry_id_to_export:
            output_file, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'Save lwa file', '', 'SMAP File (*.lwa)')
        else:
            d = Shared.MsgError(self, 'Empty List!', 'No scan is selected!')
            d.exec()
            output_file = None

        # prevent from overwriting
        if output_file == self.filename:
            msg = Shared.MsgError(self, 'Cannot save!',
                             'Output file shall not overwrite source file')
            msg.exec()
        elif output_file:
            lwaparser.export_lwa(list(set(self.entry_id_to_export)), self.hd_line_num, src=self.filename, output=output_file)
        else:
            pass

    def export_xy(self):
        ''' Export to xy text file. User can select delimiter '''

        # check if entry_id_to_export list is not empty
        if self.entry_id_to_export:
            output_dir = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select directory to save xy files')
        else:
            d = Shared.MsgError(self, 'Empty List!', 'No scan is selected!')
            d.exec()
            output_dir = None

        # prevent from overwriting
        if output_dir == self.filename:
            msg = Shared.MsgError(self, 'Cannot save!',
                             'Output file shall not overwrite source file')
            msg.exec()
        elif output_dir:
            lwaparser.export_xy(list(set(self.entry_id_to_export)), self.hd_line_num, src=self.filename, output_dir=output_dir)
        else:
            pass

    def open_new_file(self):

        # close this window and delete this instance
        self.close()
        self.deleteLater()
        # launch a new dialog window
        self.parent.on_lwa_parser()

    def reject(self):
        self.preview_win.close()
        self.preview_win.deleteLater()
        self.close()
        self.deleteLater()


class PrevSpectrumDialog(QtWidgets.QDialog):
    '''
        Preview dialog window for spectrum
    '''

    def __init__(self, parent, data=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.parent = parent
        self._data = data
        self.setWindowTitle('Spectrum Preview')
        self.setMinimumWidth(750)
        self.setMinimumHeight(450)

        self.pgPlot = pg.PlotWidget(self, title='Spectrum Preview')
        self.pgPlot.setLabel('left', text='Intensity', units='V')
        self.pgPlot.setLabel('bottom', text='Frequency', units='Hz')
        self.curve = self.pgPlot.plot()

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        mainLayout.addWidget(self.pgPlot)
        self.setLayout(mainLayout)

    def setData(self, data):
        self._data = data
        self.curve.setData(self._data[:,0], self._data[:,1])
