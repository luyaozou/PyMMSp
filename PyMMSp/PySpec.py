#! /usr/bin/env python
#-*- coding: utf-8 -*-

"""
  Integrated Python GUI for spectral analysis.
  Designed functionalities:
    > Plot spectra (x,y) file
    > Fit spectral lines to common lineshape functions (Gaussian/Lorentzian/Voigt)
    > Baseline removal
    > Peak selection
    > Catalog simulation (JPL/CDMS)

  Package Requirments:
    > numpy 1.8+
    > scipy 0.16+
    > PyQt6
    > matplotlib

  Written by Luyao Zou @ https://github.com/luyaozou
"""

__author__ = 'Luyao Zou, zouluyao@hotmail.com'
__version__ = 'Beta 0.1'
__date__ = 'Date: 07/22/2016'

from PyQt6 import QtWidgets, QtCore, QtGui
import sys
import os
import numpy as np
import matplotlib as mpl
mpl.use('Qt5Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
# custom module
import sflib


class FitParameter:
    ''' Store Fit Parameters '''
    def __init__(self, peak):
        self.ftype = 0      # function type
        self.der = 0        # order of derivative (up to 4)
        self.peak = peak    # number of peaks
        self.par_per_peak = 3   # number of parameters per peak
        self.boxwin = 1     # boxcar smooth window
        self.rescale = 1    # y intensity rescaler
        self.deg = 0        # degree of polynomial baseline
        self.par_name = self.get_par_name(0)     # parameter name list
        self.par = np.empty(self.par_per_peak*peak)     # parameter vector
        self.smooth_edge = False

    def get_par_name(self, ftype):
        if not ftype:           # Gaussian type
            return ['mu', 'sigma', 'A']
        elif ftype == 1:    # Lorentzian type
            return ['mu', 'gamma', 'A']

    def get_function(self):
        return sflib.Function(self.ftype, self.der, self.peak)


class FitStatus:
    ''' Store Fit Status '''
    def __init__(self):
        self.stat = 2
        self.input_valid = True
        self.stat_dict = {0:'Fit successful',
                          1:'Fit failed',
                          2:'File not found',
                          3:'Unsupported file format',
                          4:'Baseline removal failed',
                          5:'Input Invalid'}
        self.file_idx = 0

    def print_stat(self):
        return self.stat_dict[self.stat]


class FitMainGui(QtWidgets.QMainWindow):
    # define main GUI window of the simulator
    def __init__(self, parent=None):       # initialize GUI
        super().__init__()

        # initialize fit parameter & fit status instance
        self.fit_par = FitParameter(1)
        self.fit_stat = FitStatus()
        # initialize input validity tracker
        self.fit_stat.input_valid = True
        # get log directory (local directory of the script)
        self.log_dir = os.getcwd()
        # get file directory (read last directory from .cfg file)
        self.current_dir = self.get_file_dir()

        # add aborted and successful file list
        self.list_aborted_file = []
        self.list_success_file = []

        # add menubar
        openAction = QtWidgets.QAction('Open', self)
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('Open Spectra')
        openAction.triggered.connect(self.open_file)
        self.menu = self.menuBar()
        self.menu.setNativeMenuBar(False)
        self.menu.addAction(openAction)

        # add status bar
        self.statusbar = self.statusBar()

        # set GUI layout
        self.set_main_grid()
        self.widget_main = QtWidgets.QWidget()
        self.widget_main.setLayout(self.layout_main)
        self.setCentralWidget(self.widget_main)

        # set program title
        self.setWindowTitle('Fit Spectra!')

        # show program window
        self.show()

    def set_main_grid(self):
        self.layout_main = QtWidgets.QGridLayout()
        self.layout_main.setSpacing(6)

        # add current_file label
        self.label_current_file = QtWidgets.QLabel()
        self.layout_main.addWidget(QtWidgets.QLabel('Current File:'), 0, 0)
        self.layout_main.addWidget(self.label_current_file, 0, 1, 1, 2)

        # add matplotlib canvas
        self.fig = plt.figure()
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setFocus()
        self.mpl_toolbar = NavigationToolbar(self.canvas, self)
        self.click_counter = 0      # initialize click counter
        # connect the canvas to matplotlib standard key press events
        self.canvas.mpl_connect('key_press_event', self.mpl_key_press)
        # connect the canvas to mouse click events
        self.canvas.mpl_connect('button_press_event', self.mpl_click)
        self.layout_main.addWidget(self.mpl_toolbar, 1, 0, 1, 3)
        self.layout_main.addWidget(self.canvas, 2, 0, 1, 3)

        # add fit option layout
        self.layout_setting = QtWidgets.QGridLayout()
        # select lineshape
        self.combo_ftype = QtWidgets.QComboBox()
        self.combo_ftype.addItems(['Gaussian', 'Lorentzian'])
        # select number of derivatives
        self.combo_der = QtWidgets.QComboBox()
        self.combo_der.addItems(['0', '1', '2', '3', '4'])
        self.check_boxcar = QtWidgets.QCheckBox('Boxcar Smooth?')
        self.check_rescale = QtWidgets.QCheckBox('Rescale Intensity?')
        self.edit_boxcar = QtWidgets.QLineEdit('1')
        self.edit_rescale = QtWidgets.QLineEdit('1')
        self.edit_deg = QtWidgets.QLineEdit('0')
        self.edit_num_peak = QtWidgets.QLineEdit('1')
        self.layout_setting.addWidget(QtWidgets.QLabel('Lineshape Function'), 0, 0)
        self.layout_setting.addWidget(self.combo_ftype, 1, 0)
        self.layout_setting.addWidget(QtWidgets.QLabel('Derivative'), 0, 1)
        self.layout_setting.addWidget(self.combo_der, 1, 1)
        self.layout_setting.addWidget(self.check_boxcar, 2, 0)
        self.layout_setting.addWidget(self.edit_boxcar, 2, 1)
        self.layout_setting.addWidget(self.check_rescale, 3, 0)
        self.layout_setting.addWidget(self.edit_rescale, 3, 1)
        self.layout_setting.addWidget(QtWidgets.QLabel('PolyBaseline Degree'), 4, 0)
        self.layout_setting.addWidget(self.edit_deg, 4, 1)
        self.layout_setting.addWidget(QtWidgets.QLabel('Number of Peaks'), 5, 0)
        self.layout_setting.addWidget(self.edit_num_peak, 5, 1)
        self.layout_setting.addWidget(QtWidgets.QLabel('<<< Initial Guess >>>'), 6, 0, 2, 2)
        # connect signals
        # select combo box items
        self.combo_ftype.currentIndexChanged.connect(self.get_ftype)
        self.combo_der.currentIndexChanged.connect(self.get_der)
        # display/hide checked edit box
        self.edit_boxcar.hide()
        self.edit_rescale.hide()
        self.check_boxcar.stateChanged.connect(self.show_boxcar)
        self.check_rescale.stateChanged.connect(self.show_rescale)
        # check input validity
        self.edit_boxcar.textChanged.connect(self.check_int_validity)
        self.edit_rescale.textChanged.connect(self.check_double_validity)
        self.edit_deg.textChanged.connect(self.check_int_validity)
        self.edit_num_peak.textChanged.connect(self.set_par_layout)

        # add fit parameter layout for initial guess
        self.widget_par = QtWidgets.QWidget()
        self.layout_par = QtWidgets.QGridLayout()
        self.edit_par = []
        self.set_par_layout()
        self.widget_par.setLayout(self.layout_par)
        self.scroll_par = QtWidgets.QScrollArea()
        self.scroll_par.setWidget(self.widget_par)
        self.scroll_par.setWidgetResizable(True)
        self.scroll_par.setMaximumHeight(600)
        self.layout_setting.addWidget(self.scroll_par, 8, 0, 1, 2)

        self.layout_main.addLayout(self.layout_setting, 2, 3)

        # add fit & Quit button
        btn_fit = QtWidgets.QPushButton('Fit Spectrum', self)
        btn_quit = QtWidgets.QPushButton('Quit', self)
        btn_quit.setShortcut('Ctrl+Q')
        self.layout_main.addWidget(btn_fit, 0, 3)
        self.layout_main.addWidget(btn_quit, 3, 3)
        btn_fit.clicked.connect(self.fit_routine)
        btn_quit.clicked.connect(self.close)

    def set_par_layout(self):
        text = self.edit_num_peak.text()
        try:
            self.fit_par.peak = abs(int(text))
            green = '#00A352'
            self.edit_num_peak.setStyleSheet('border: 3px solid %s' % green)
        except ValueError:
            red = '#D63333'
            self.edit_num_peak.setStyleSheet('border: 3px solid %s' % red)
            self.fit_par.peak = 0
        # set initial guess layout
        # clear previous parameters
        self.fit_par.par = np.zeros(self.fit_par.peak * self.fit_par.par_per_peak)
        self.edit_par = []          # clear previous widgets
        self.clear_item(self.layout_par)   # clear layout
        self.click_counter = 0      # reset click counter
        # add widgets
        for i in range(self.fit_par.par_per_peak * self.fit_par.peak):
            peak_index = i // self.fit_par.par_per_peak + 1
            par_index = i % self.fit_par.par_per_peak
            self.edit_par.append(QtWidgets.QLineEdit())
            if par_index:   # starting of a new peak
                self.layout_par.addWidget(QtWidgets.QLabel(
                                    '--- Peak {:d} ---'.format(peak_index)),
                                     4*(peak_index-1), 0, 1, 2)
            self.layout_par.addWidget(QtWidgets.QLabel(
                                    self.fit_par.par_name[par_index]), i+peak_index, 0)
            self.layout_par.addWidget(self.edit_par[i], i+peak_index, 1)
            self.edit_par[i].setText('0.5')     # set default value
            self.edit_par[i].textChanged.connect(self.check_double_validity)

    # --------- get all fitting options ---------

    def get_ftype(self, ftype):
        self.fit_par.ftype = ftype
        self.fit_par.par_name = self.fit_par.get_par_name(ftype)
        # refresh parameter layout
        self.set_par_layout()

    def get_der(self, der):
        self.fit_par.der = der

    def get_par(self):
        # if input is valid
        if self.fit_stat.input_valid == 2:
            for i in range(self.fit_par.par_per_peak * self.fit_par.peak):
                self.fit_par.par[i] = float(self.edit_par[i].text())
            self.fit_par.boxwin = abs(int(self.edit_boxcar.text()))
            self.fit_par.rescale = abs(float(self.edit_rescale.text()))
            self.fit_par.deg = abs(int(self.edit_deg.text()))
        else:
            self.fit_stat.stat = 5

    # --------- fit routine ---------

    def fit_routine(self):
        # if data loaded successfully
        if not self.fit_stat.stat:
            data_table, popt, uncertainty, ppoly = self.fit_try()

        # if fit failed, print information
        if self.fit_stat.stat:
            failure = QtWidgets.QMessageBox.information(self, 'Failure',
                      self.fit_stat.print_stat(), QtWidgets.QMessageBox.Retry |
                      QtWidgets.QMessageBox.Abort, QtWidgets.QMessageBox.Retry)
            # choose retry or ignore
            if failure ==  QtWidgets.QMessageBox.Retry:
                pass
            elif failure == QtWidgets.QMessageBox.Abort:
                self.pass_file()
        # if fit successful, ask user for save|retry option
        else:
            success = QtWidgets.QMessageBox.question(self, 'Save?',
                      'Save the fit if it looks good. \n ' +
                      'Otherwise retry a fit or abort this file ',
                      QtWidgets.QMessageBox.Save | QtWidgets.QMessageBox.Retry |
                      QtWidgets.QMessageBox.Abort, QtWidgets.QMessageBox.Save)
            if success == QtWidgets.QMessageBox.Save:
                # save file
                self.save_file(data_table, popt, uncertainty, ppoly)
                # go to next spectrum
                self.next_file()
            elif success == QtWidgets.QMessageBox.Retry:
                pass
            elif success == QtWidgets.QMessageBox.Abort:
                self.pass_file()

    def fit_try(self):
        # get fitting parameters
        self.get_par()

        if not self.fit_stat.stat:
            if self.fit_par.peak:
                # get fit function
                f = self.fit_par.get_function()
                # re-load data with boxcar win and rescale
                xdata, ydata = self.load_data()
                popt, uncertainty, noise, ppoly, self.fit_stat.stat = sflib.fit_spectrum(f,
                                                                                         xdata, ydata, self.fit_par.par, self.fit_par.deg, self.fit_par.smooth_edge)
            else:    # if no peak, fit baseline
                xdata, ydata = self.load_data()
                popt, uncertainty, noise, ppoly, self.fit_stat.stat = sflib.fit_baseline(xdata, ydata, self.fit_par.deg)

        # if fit successful, plot fit
        if not self.fit_stat.stat and self.fit_par.peak:
            # Make plot for successful fit
            fit = f.get_func()(xdata, *popt)
            baseline = np.polyval(ppoly, xdata - np.median(xdata))
            residual = ydata - fit - baseline
            self.statusbar.showMessage('Noise {:.4f}'.format(noise))
            self.plot_spect(xdata, ydata, fit, baseline)
            # concatenate data table
            data_table = np.column_stack((xdata, ydata, fit, baseline))
            return data_table, popt, uncertainty, ppoly
        elif not self.fit_stat.stat:
            baseline = np.polyval(ppoly, xdata - np.median(xdata))
            residual = ydata - baseline
            fit = np.zeros_like(ydata)
            self.statusbar.showMessage('Noise {:.4f}'.format(noise))
            self.plot_spect(xdata, ydata, fit, baseline)
            data_table = np.column_stack((xdata, ydata, fit, baseline))
            return data_table, popt, uncertainty, ppoly
        else:
            return None, None, None, None

    def load_data(self):        # load data
        # check if there is a file name
        try:
            filename = '/'.join([self.current_dir, self.current_file])
        except AttributeError:
            select_file = QtWidgets.QMessageBox.warning(self, 'No File!',
                'No spectrum file has been selected. Do you want to select now?',
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                QtWidgets.QMessageBox.Yes)
            if select_file == QtWidgets.QMessageBox.Yes:
                self.open_file()
            else:
                self.fit_stat.stat = 2  # exception: file not found
                return None, None
        # try load data
        xdata, ydata, self.fit_stat.stat = sflib.read_file(filename,
                                                           self.fit_par.boxwin, self.fit_par.rescale)
        # if file is readable, plot raw data and return xy data
        if not self.fit_stat.stat:
            self.plot_data(xdata, ydata)
            return xdata, ydata
        else:
            return None, None

    def plot_data(self, xdata, ydata):        # plot raw data file before fit
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.hold(False)
        ax.plot(xdata, ydata, 'k-')
        ax.set_xlabel('Frequency (MHz)')
        ax.set_ylabel('Intensity (a.u.)')
        self.canvas.draw()

    def plot_spect(self, xdata, ydata, fit, baseline):       # plot fitted spectra
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.plot(xdata, ydata, 'k-', xdata, fit+baseline, 'r-',
                xdata, baseline, 'b--')
        ax.set_xlabel('Frequency (MHz)')
        ax.set_ylabel('Intensity (a.u.)')
        self.canvas.draw()

    # --------- file handling ---------
    def open_file(self):
        # get all file names
        QFileHandle = QtWidgets.QFileDialog()
        QFileHandle.setDirectory(self.current_dir)
        filelist = QFileHandle.getOpenFileNames(self, 'Open Spectra')[0]
        # if list is not empty, proceed
        if filelist:
            # sort file name
            filelist.sort()
            # seperate directory name and file name
            self.list_dir, self.list_file = sflib.separate_dir(filelist)
            # get the first directory and file name
            self.current_dir = self.list_dir[0]
            self.current_file = self.list_file[0]
            self.fit_stat.file_idx = 0
            # update label
            self.label_current_file.setText(self.current_file)
            # launch fit routine
            self.load_data()
        else:
            self.fit_stat.stat = 2

    def pass_file(self):
        try:
            self.list_aborted_file.append('/'.join([self.current_dir, self.current_file]))
        except AttributeError:
            pass
        self.next_file()

    def save_file(self, data_table, popt, uncertainty, ppoly):
        default_fitname = sflib.out_name_gen(self.current_file) + '.csv'
        default_logname = sflib.out_name_gen(self.current_file) + '.log'
        fitname = QtWidgets.QFileDialog.getSaveFileName(self,
                  'Save Current Fit Spectrum', '/'.join([self.current_dir, default_fitname]))[0]
        if fitname:
            sflib.save_fit(fitname, data_table, popt,
                           self.fit_par.ftype, self.fit_par.der, self.fit_par.peak)
        logname = QtWidgets.QFileDialog.getSaveFileName(self,
                   'Save Current Fit Log', '/'.join([self.current_dir, default_logname]))[0]
        if logname:
            sflib.save_log(logname, popt, uncertainty, ppoly,
                           self.fit_par.ftype, self.fit_par.der,
                           self.fit_par.peak, self.fit_par.par_name)
        self.list_success_file.append('/'.join([self.current_dir, self.current_file]))

    def next_file(self):
        # refresh current file index, fit status and click counter
        self.fit_stat.file_idx += 1
        self.fit_stat.stat = 0
        self.click_counter = 0

        try:
            self.current_file = self.list_file[self.fit_stat.file_idx]
            self.current_dir = self.list_dir[self.fit_stat.file_idx]
            # update label text
            self.label_current_file.setText(self.current_file)
            # repeat fit routine
            self.load_data()
        except (IndexError, AttributeError):
            eof = QtWidgets.QMessageBox.information(self, 'End of File',
                    'No more files to fit. Do you want to select new files?',
                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.Close,
                    QtWidgets.QMessageBox.Yes)
            if eof == QtWidgets.QMessageBox.Yes:
                self.open_file()
            else:
                self.close()

    def get_file_dir(self):
        try:
            f = open('.prev_dir.log', 'r')
            last_dir = f.readline()
            f.close()
            return last_dir
        except FileNotFoundError:
            return self.log_dir

    def save_log(self):
        log = QtWidgets.QFileDialog()
        log.setNameFilter('Log files (*.log)')
        logname = log.getSaveFileName(self, 'Save Fit Log',
                            '/'.join([self.current_dir, 'FitJob.log']))[0]
        # if name is not empty
        if logname:
            pass
        else:
            logname = '/'.join([self.log_dir, 'FitJob.log'])

        with open(logname, 'w') as a_log:
            for file_name in self.list_success_file:
                a_log.write('Successful  --- {0:s}\n'.format(file_name))
            for file_name in self.list_aborted_file:
                a_log.write('Aborted     --- {0:s}\n'.format(file_name))

    def save_last_dir(self):
        with open('.prev_dir.log', 'w') as a_file:
            a_file.write(self.current_dir)

    # --------- some useful little tools -----------

    def show_boxcar(self, state):
        if state == QtCore.Qt.Checked:
            self.edit_boxcar.show()
        else:
            # make sure no boxcar (in case)
            self.edit_boxcar.setText('1')
            self.edit_boxcar.hide()

    def show_rescale(self, state):
        if state == QtCore.Qt.Checked:
            self.edit_rescale.show()
        else:
            # no rescale
            self.edit_rescale.setText('1')
            self.edit_rescale.hide()

    def check_double_validity(self, *args):
        sender = self.sender()
        validator = QtGui.QDoubleValidator()
        state = validator.validate(sender.text(), 0)[0]
        if state == QtGui.QValidator.Acceptable and sender.text():
            color = '#00A352'       # green
            self.fit_stat.input_valid = 2    # valid entry
        elif not sender.text():
            color = '#FF9933'       # yellow
            self.fit_stat.input_valid = 1    # empty entry
        else:
            color = '#D63333'       # red
            self.fit_stat.input_valid = 0    # invalid entry
        sender.setStyleSheet('border: 3px solid %s' % color)

    def check_int_validity(self, *args):
        sender = self.sender()
        validator = QtGui.QIntValidator()
        state = validator.validate(sender.text(), 0)[0]
        if state == QtGui.QValidator.Acceptable and sender.text():
            color = '#00A352'       # green
            self.fit_stat.input_valid = 2    # valid entry
        elif not sender.text():
            color = '#FF9933'       # yellow
            self.fit_stat.input_valid = 1    # empty entry
        else:
            color = '#D63333'       # red
            self.fit_stat.input_valid = 0    # invalid entry
        sender.setStyleSheet('border: 3px solid %s' % color)

    def clear_item(self, layout):        # clears all elements in the layout
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                w = item.widget()
                if w is not None:
                    w.deleteLater()
                else:
                    self.clear_item(item.layout())

    def mpl_key_press(self, event):
        # matplotlib standard key press event
        key_press_handler(event, self.canvas, self.mpl_toolbar)

    def mpl_click(self, event):
        # if can still pick peak position
        if (self.click_counter < self.fit_par.peak) and (self.click_counter >= 0):
            # update counter
            self.click_counter += 1
            # retrieve cooridate upon mouse click
            mu = event.xdata    # peak center
            a = event.ydata*0.1   # peak intensity
            # locate parameter index in the parameter list
            mu_idx = self.fit_par.par_per_peak * (self.click_counter-1)
            a_idx = mu_idx + self.fit_par.par_per_peak - 1
            self.edit_par[mu_idx].setText(str(mu))
            self.edit_par[a_idx].setText(str(a))
        elif self.click_counter >= self.fit_par.peak:
            # click number overloads. As user to reset
            reset = QtWidgets.QMessageBox.question(self, 'Reset?',
                       'Do you want to reset clicks to override peak selection?',
                       QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                       QtWidgets.QMessageBox.No)
            if reset == QtWidgets.QMessageBox.Yes:
                self.click_counter = 0
            elif reset == QtWidgets.QMessageBox.No:
                self.click_counter = -1     # no longer bother in this session
        else:
            event.ignore()

    def closeEvent(self, event):   # exit warning
        quit_confirm = QtWidgets.QMessageBox.question(self, 'Quit?',
                       'Are you sure to quit?', QtWidgets.QMessageBox.Yes |
                       QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.Yes)
        if quit_confirm == QtWidgets.QMessageBox.Yes:
            #try:
                # save fit job log file
            self.save_log()
            self.save_last_dir()
            #except:
            #    pass
            event.accept()
        else:
            event.ignore()

    def keyPressEvent(self, event): # press ESC to exit
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()


# ------ run script ------
if __name__ == '__main__':
    args = sys.argv
    # get around the gtk error on linux systems (sacrifice the ui appearance)
    #if sys.platform == 'linux':
    #    args.append('-style')
    #    args.append('Cleanlooks')

    app = QtWidgets.QApplication(args)
    launch = FitMainGui()
    sys.exit(app.exec_())
