#! encoding = utf-8
''' Dialog windows for system menues '''


from PyQt5 import QtGui, QtCore
from api import general as api_gen
from api import synthesizer as api_syn
from api import lockin as api_lia
from gui import SharedWidgets as Shared
from pyqtgraph import siFormat


class SelInstDialog(QtGui.QDialog):
    '''
        Dialog window for instrument selection.
    '''

    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.parent = parent
        self.setMinimumWidth(400)
        self.setMinimumHeight(400)
        self.setWindowTitle('Select Instrument')

        refreshButton = QtGui.QPushButton('Refresh Available Instrument List')
        acceptButton = QtGui.QPushButton(Shared.btn_label('confirm'))
        cancelButton = QtGui.QPushButton(Shared.btn_label('reject'))

        self.availableInst = QtGui.QLabel()
        instList, instStr = api_gen.list_inst()
        self.availableInst.setText(instStr)

        selInst = QtGui.QWidget()
        selInstLayout = QtGui.QFormLayout()
        self.selSyn = QtGui.QComboBox()
        self.selSyn.addItems(['N.A.'])
        self.selSyn.addItems(instList)
        self.selLockin = QtGui.QComboBox()
        self.selLockin.addItems(['N.A.'])
        self.selLockin.addItems(instList)
        self.selScope = QtGui.QComboBox()
        self.selScope.addItems(['N.A.'])
        self.selScope.addItems(instList)
        self.selMotor = QtGui.QComboBox()
        self.selMotor.addItems(['N.A.'])
        self.selMotor.addItems(instList)
        self.selPressure = QtGui.QComboBox()
        self.selPressure.addItems(['N.A.'])
        self.selPressure.addItems(instList)
        selInstLayout.addRow(QtGui.QLabel('Synthesizer'), self.selSyn)
        selInstLayout.addRow(QtGui.QLabel('Lock-in'), self.selLockin)
        selInstLayout.addRow(QtGui.QLabel('Oscilloscope'), self.selScope)
        selInstLayout.addRow(QtGui.QLabel('Step Motor'), self.selMotor)
        selInstLayout.addRow(QtGui.QLabel('CENTER TWO Pressure Readout'), self.selPressure)
        selInst.setLayout(selInstLayout)

        # Set main layout
        mainLayout = QtGui.QGridLayout()
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


class ViewInstDialog(QtGui.QDialog):
    '''
        Dialog window for instrument status view
    '''

    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)

        self.setMinimumWidth(400)
        self.setMinimumHeight(400)
        self.setWindowTitle('View Instrument Status')


class CloseSelInstDialog(QtGui.QDialog):
    '''
        Dialog window for closing selected instrument.
    '''

    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.parent = parent
        self.setMinimumWidth(400)
        self.setMinimumHeight(400)
        self.setWindowTitle('Close Instrument')

        inst = QtGui.QWidget()
        self.synToggle = QtGui.QCheckBox()
        self.liaToggle = QtGui.QCheckBox()
        self.pciToggle = QtGui.QCheckBox()
        self.motorToggle = QtGui.QCheckBox()
        self.pressureToggle = QtGui.QCheckBox()

        instLayout = QtGui.QFormLayout()
        instLayout.addRow(QtGui.QLabel('Instrument'), QtGui.QLabel('Status'))
        # only list currently connected instruments
        if self.parent.synHandle:
            self.synToggle.setCheckState(True)
            instLayout.addRow(QtGui.QLabel('Synthesizer'), self.synToggle)
        else:
            self.synToggle.setCheckState(False)

        if self.parent.liaHandle:
            self.liaToggle.setCheckState(True)
            instLayout.addRow(QtGui.QLabel('Lockin'), self.liaToggle)
        else:
            self.liaToggle.setCheckState(False)

        if self.parent.pciHandle:
            self.pciToggle.setCheckState(True)
            instLayout.addRow(QtGui.QLabel('Oscilloscope'), self.pciToggle)
        else:
            self.pciToggle.setCheckState(False)

        if self.parent.motorHandle:
            self.motorToggle.setCheckState(True)
            instLayout.addRow(QtGui.QLabel('Motor'), self.motorToggle)
        else:
            self.motorToggle.setCheckState(False)

        if self.parent.pressureHandle:
            self.pressureToggle.setCheckState(True)
            instLayout.addRow(QtGui.QLabel('Pressure Readout'), self.pressureToggle)
        else:
            self.pressureToggle.setCheckState(False)

        inst.setLayout(instLayout)

        okButton = QtGui.QPushButton(Shared.btn_label('complete'))
        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(inst)
        mainLayout.addWidget(QtGui.QLabel('No command will be sent before you hit the accept button'))
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


class SynInfoDialog(QtGui.QDialog):
    '''
        Dialog window for displaying full synthesizer settings.
    '''

    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.parent = parent
        self.setMinimumWidth(800)
        self.setMinimumHeight(400)
        self.setWindowTitle('Synthesizer Settings')

        self.instGroup = QtGui.QGroupBox()
        self.rfGroup = QtGui.QGroupBox()
        self.modGroup = QtGui.QGroupBox()

        self.instGroup.setTitle('Instrument Session')
        self.instNameLabel = QtGui.QLabel()
        self.instInterfaceLabel = QtGui.QLabel()
        self.instInterfaceNumLabel = QtGui.QLabel()
        self.instRemoteDispLabel = QtGui.QLabel()
        instGroupLayout = QtGui.QFormLayout()
        instGroupLayout.addRow(QtGui.QLabel('Instrument Name'), self.instNameLabel)
        instGroupLayout.addRow(QtGui.QLabel('Interface Type'), self.instInterfaceLabel)
        instGroupLayout.addRow(QtGui.QLabel('Interface Number'), self.instInterfaceNumLabel)
        instGroupLayout.addRow(QtGui.QLabel('Remote Display'), self.instRemoteDispLabel)
        self.instGroup.setLayout(instGroupLayout)

        self.rfGroup.setTitle('RF Settings')
        self.rfOutputLabel = QtGui.QLabel()
        self.modOutputLabel = QtGui.QLabel()
        self.synFreqLabel = QtGui.QLabel()
        rfGroupLayout = QtGui.QGridLayout()
        rfGroupLayout.addWidget(QtGui.QLabel('RF Output'), 0, 0)
        rfGroupLayout.addWidget(self.rfOutputLabel, 0, 1)
        rfGroupLayout.addWidget(QtGui.QLabel('Synth Frequency'), 0, 2)
        rfGroupLayout.addWidget(self.synFreqLabel, 0, 3)
        rfGroupLayout.addWidget(QtGui.QLabel('Modulation Output'), 0, 4)
        rfGroupLayout.addWidget(self.modOutputLabel, 0, 5)
        self.rfGroup.setLayout(rfGroupLayout)

        self.modGroup.setTitle('Modulation Settings')
        self.am1StateLabel = QtGui.QLabel()
        self.am2StateLabel = QtGui.QLabel()
        self.fm1StateLabel = QtGui.QLabel()
        self.fm2StateLabel = QtGui.QLabel()
        self.pm1StateLabel = QtGui.QLabel()
        self.pm2StateLabel = QtGui.QLabel()
        self.lfStateLabel = QtGui.QLabel()
        self.am1DepthLabel = QtGui.QLabel()
        self.am2DepthLabel = QtGui.QLabel()
        self.fm1DevLabel = QtGui.QLabel()
        self.fm2DevLabel = QtGui.QLabel()
        self.pm1DevLabel = QtGui.QLabel()
        self.pm2DevLabel = QtGui.QLabel()
        self.lfVolLabel = QtGui.QLabel()
        self.am1SrcLabel = QtGui.QLabel()
        self.am2SrcLabel = QtGui.QLabel()
        self.fm1SrcLabel = QtGui.QLabel()
        self.fm2SrcLabel = QtGui.QLabel()
        self.pm1SrcLabel = QtGui.QLabel()
        self.pm2SrcLabel = QtGui.QLabel()
        self.lfSrcLabel = QtGui.QLabel()
        self.am1FreqLabel = QtGui.QLabel()
        self.am2FreqLabel = QtGui.QLabel()
        self.fm1FreqLabel = QtGui.QLabel()
        self.fm2FreqLabel = QtGui.QLabel()
        self.pm1FreqLabel = QtGui.QLabel()
        self.pm2FreqLabel = QtGui.QLabel()
        self.am1WaveLabel = QtGui.QLabel()
        self.am2WaveLabel = QtGui.QLabel()
        self.fm1WaveLabel = QtGui.QLabel()
        self.fm2WaveLabel = QtGui.QLabel()
        self.pm1WaveLabel = QtGui.QLabel()
        self.pm2WaveLabel = QtGui.QLabel()

        modGroupLayout = QtGui.QGridLayout()
        modGroupLayout.addWidget(QtGui.QLabel('Channel'), 0, 0)
        modGroupLayout.addWidget(QtGui.QLabel('Source'), 0, 1)
        modGroupLayout.addWidget(QtGui.QLabel('State'), 0, 2)
        modGroupLayout.addWidget(QtGui.QLabel('Depth/Dev'), 0, 3)
        modGroupLayout.addWidget(QtGui.QLabel('Rate'), 0, 4)
        modGroupLayout.addWidget(QtGui.QLabel('Waveform'), 0, 5)
        modGroupLayout.addWidget(QtGui.QLabel('AM1'), 1, 0)
        modGroupLayout.addWidget(self.am1StateLabel, 1, 1)
        modGroupLayout.addWidget(self.am1SrcLabel, 1, 2)
        modGroupLayout.addWidget(self.am1DepthLabel, 1, 3)
        modGroupLayout.addWidget(self.am1FreqLabel, 1, 4)
        modGroupLayout.addWidget(self.am1WaveLabel, 1, 5)
        modGroupLayout.addWidget(QtGui.QLabel('AM2'), 2, 0)
        modGroupLayout.addWidget(self.am2StateLabel, 2, 1)
        modGroupLayout.addWidget(self.am2SrcLabel, 2, 2)
        modGroupLayout.addWidget(self.am2DepthLabel, 2, 3)
        modGroupLayout.addWidget(self.am2FreqLabel, 2, 4)
        modGroupLayout.addWidget(self.am2WaveLabel, 2, 5)
        modGroupLayout.addWidget(QtGui.QLabel('FM1'), 3, 0)
        modGroupLayout.addWidget(self.fm1StateLabel, 3, 1)
        modGroupLayout.addWidget(self.fm1SrcLabel, 3, 2)
        modGroupLayout.addWidget(self.fm1DevLabel, 3, 3)
        modGroupLayout.addWidget(self.fm1FreqLabel, 3, 4)
        modGroupLayout.addWidget(self.fm1WaveLabel, 3, 5)
        modGroupLayout.addWidget(QtGui.QLabel('FM2'), 4, 0)
        modGroupLayout.addWidget(self.fm2StateLabel, 4, 1)
        modGroupLayout.addWidget(self.fm2SrcLabel, 4, 2)
        modGroupLayout.addWidget(self.fm2DevLabel, 4, 3)
        modGroupLayout.addWidget(self.fm2FreqLabel, 4, 4)
        modGroupLayout.addWidget(self.fm2WaveLabel, 4, 5)
        modGroupLayout.addWidget(QtGui.QLabel('φM1'), 5, 0)
        modGroupLayout.addWidget(self.pm1StateLabel, 5, 1)
        modGroupLayout.addWidget(self.pm1SrcLabel, 5, 2)
        modGroupLayout.addWidget(self.pm1DevLabel, 5, 3)
        modGroupLayout.addWidget(self.pm1FreqLabel, 5, 4)
        modGroupLayout.addWidget(self.pm1WaveLabel, 5, 5)
        modGroupLayout.addWidget(QtGui.QLabel('φM2'), 6, 0)
        modGroupLayout.addWidget(self.pm2StateLabel, 6, 1)
        modGroupLayout.addWidget(self.pm2SrcLabel, 6, 2)
        modGroupLayout.addWidget(self.pm2DevLabel, 6, 3)
        modGroupLayout.addWidget(self.pm2FreqLabel, 6, 4)
        modGroupLayout.addWidget(self.pm2WaveLabel, 6, 5)
        modGroupLayout.addWidget(QtGui.QLabel('LF OUT'), 7, 0)
        modGroupLayout.addWidget(self.lfStateLabel, 7, 1)
        modGroupLayout.addWidget(self.lfSrcLabel, 7, 2)
        modGroupLayout.addWidget(self.lfVolLabel, 7, 3)
        self.modGroup.setLayout(modGroupLayout)

        self.refreshButton = QtGui.QPushButton('Manual Refresh')
        self.acceptButton = QtGui.QPushButton(Shared.btn_label('accept'))

        mainLayout = QtGui.QGridLayout()
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

        self.exec_()

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
        self.synFreqLabel.setText('{:.9f} MHz'.format(self.parent.synInfo.synFreqLabel * 1e-6))

        # update modulation setting panel
        self.am1StateLabel.setText('ON' if self.parent.synInfo.AM1Toggle else 'OFF')
        self.am1SrcLabel.setText(self.parent.synInfo.AM1Src)
        self.am1DepthLabel.setText('{:.1%} ({:.0f} dB)'.format(self.parent.synInfo.AM1DepthPercent, self.parent.synInfo.AM1DepthDbm))
        self.am1FreqLabel.setText(siFormat(self.parent.synInfo.AM1Freq, suffix='Hz'))
        self.am1WaveLabel.setText(self.parent.synInfo.AM1Wave)

        self.am2StateLabel.setText('ON' if self.parent.synInfo.AM2Toggle else 'OFF')
        self.am2SrcLabel.setText(self.parent.synInfo.AM2Src)
        self.am2DepthLabel.setText('{:.1%} ({:.0f} dB)'.format(self.parent.synInfo.AM2DepthPercent, self.parent.synInfo.AM2DepthDbm))
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


class LockinInfoDialog(QtGui.QDialog):
    '''
        Dialog window for displaying full lockin settings.
    '''

    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.parent = parent
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        self.setWindowTitle('Lockin Amplifier Settings')

        self.instGroup = QtGui.QGroupBox()
        self.refGroup = QtGui.QGroupBox()
        self.inputGroup = QtGui.QGroupBox()
        self.gainGroup = QtGui.QGroupBox()
        self.outputGroup = QtGui.QGroupBox()

        self.instGroup.setTitle('Instrument Session')
        self.instNameLabel = QtGui.QLabel()
        self.instInterfaceLabel = QtGui.QLabel()
        self.instInterfaceNumLabel = QtGui.QLabel()
        instGroupLayout = QtGui.QFormLayout()
        instGroupLayout.addRow(QtGui.QLabel('Instrument Name'), self.instNameLabel)
        instGroupLayout.addRow(QtGui.QLabel('Interface Type'), self.instInterfaceLabel)
        instGroupLayout.addRow(QtGui.QLabel('Interface Number'), self.instInterfaceNumLabel)
        self.instGroup.setLayout(instGroupLayout)

        self.refGroup.setTitle('Reference and Phase')
        self.refSrcLabel = QtGui.QLabel()
        self.refFreqLabel = QtGui.QLabel()
        self.refHarmLabel = QtGui.QLabel()
        self.refPhaseLabel = QtGui.QLabel()
        refGroupLayout =  QtGui.QFormLayout()
        refGroupLayout.addRow(QtGui.QLabel('Reference Source'), self.refSrcLabel)
        refGroupLayout.addRow(QtGui.QLabel('Reference Freq'), self.refFreqLabel)
        refGroupLayout.addRow(QtGui.QLabel('Harmonics'), self.refHarmLabel)
        refGroupLayout.addRow(QtGui.QLabel('Phase'), self.refPhaseLabel)
        self.refGroup.setLayout(refGroupLayout)

        self.inputGroup.setTitle('Input and Filter')
        self.inputConfigLabel = QtGui.QLabel()
        self.inputGroundingLabel = QtGui.QLabel()
        self.inputCoupleLabel = QtGui.QLabel()
        self.inputFilterLabel = QtGui.QLabel()
        inputGroupLayout = QtGui.QFormLayout()
        inputGroupLayout.addRow(QtGui.QLabel('Input Config'), self.inputConfigLabel)
        inputGroupLayout.addRow(QtGui.QLabel('Input Grounding'), self.inputGroundingLabel)
        inputGroupLayout.addRow(QtGui.QLabel('Input Coupling'), self.inputCoupleLabel)
        inputGroupLayout.addRow(QtGui.QLabel('Input Filter'), self.inputFilterLabel)
        self.inputGroup.setLayout(inputGroupLayout)

        self.gainGroup.setTitle('Gain')
        self.gainSensLabel = QtGui.QLabel()
        self.gainReserveLabel = QtGui.QLabel()
        self.gainTCLabel = QtGui.QLabel()
        self.lpSlopeLabel = QtGui.QLabel()
        gainGroupLayout = QtGui.QFormLayout()
        gainGroupLayout.addRow(QtGui.QLabel('Sensitivity'), self.gainSensLabel)
        gainGroupLayout.addRow(QtGui.QLabel('Time Constant'), self.gainTCLabel)
        gainGroupLayout.addRow(QtGui.QLabel('Reserve'), self.gainReserveLabel)
        gainGroupLayout.addRow(QtGui.QLabel('Low-pass Filter Slope'), self.lpSlopeLabel)
        self.gainGroup.setLayout(gainGroupLayout)

        self.outputGroup.setTitle('Display and Output')
        self.outputDisp1Label = QtGui.QLabel()
        self.outputDisp2Label = QtGui.QLabel()
        self.outputFront1Label = QtGui.QLabel()
        self.outputFront2Label = QtGui.QLabel()
        self.outputSRateLabel = QtGui.QLabel()
        outputGroupLayout = QtGui.QGridLayout()
        outputGroupLayout.addWidget(QtGui.QLabel('Chanel 1'), 0, 1)
        outputGroupLayout.addWidget(QtGui.QLabel('Chanel 2'), 0, 2)
        outputGroupLayout.addWidget(QtGui.QLabel('Display Output'), 1, 0)
        outputGroupLayout.addWidget(self.outputDisp1Label, 1, 1)
        outputGroupLayout.addWidget(self.outputDisp2Label, 1, 2)
        outputGroupLayout.addWidget(QtGui.QLabel('Front Panel Output'), 2, 0)
        outputGroupLayout.addWidget(self.outputFront1Label, 2, 1)
        outputGroupLayout.addWidget(self.outputFront2Label, 2, 2)
        outputGroupLayout.addWidget(QtGui.QLabel('Sampling Rate'), 3, 0)
        outputGroupLayout.addWidget(self.outputSRateLabel, 3, 1, 1, 2)
        self.outputGroup.setLayout(outputGroupLayout)

        self.refreshButton = QtGui.QPushButton('Manual Refresh')
        self.acceptButton = QtGui.QPushButton(Shared.btn_label('accept'))

        mainLayout = QtGui.QGridLayout()
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

        self.exec_()

    def manual_refresh(self):

        self.parent.synInfo.full_info_query(self.parent.liaHandle)
        self.print_info()

    def print_info(self):

        # update instrument panel
        self.instNameLabel.setText(self.parent.liaInfo.instName)
        self.instInterfaceLabel.setText(self.parent.liaInfo.instInterface)
        self.instInterfaceNumLabel.setText(str(self.parent.liaInfo.instInterfaceNum))

        # update ref group
        self.refSrcLabel.setText(self.parent.liaInfo.refSrc)
        self.refFreqLabel.setText(siFormat(self.parent.liaInfo.refFreq, suffix='Hz'))
        self.refHarmLabel.setText('{:d}'.format(self.parent.liaInfo.refHrefHarm))
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
