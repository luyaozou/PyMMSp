#! encoding = utf-8

from PyQt4 import QtGui, QtCore


class InstStatus(QtGui.QMessageBox):
    ''' Message box of instrument communication status. Silent if communication
        is successful. Pop up error message in pyvisa.constants.StatusCode
    '''

    def __init__(self, parent, code):
        QtGui.QWidget.__init__(self, parent)

        self.setIcon(QtGui.QMessageBox.Warning)
        self.addButton(QtGui.QMessageBox.Ok)
        self.setText(str(code))


class MsgError(QtGui.QMessageBox):
    ''' Message box of instrument communication status. Silent if communication
        is successful. Pop up error message in pyvisa.constants.StatusCode
    '''

    def __init__(self, parent, text, moretext=''):
        QtGui.QWidget.__init__(self, parent)

        self.setIcon(QtGui.QMessageBox.Critical)
        self.addButton(QtGui.QMessageBox.Ok)
        self.setText(text)
        self.setInformativeText(moretext)


class MsgWarning(QtGui.QMessageBox):
    ''' Message box of instrument communication status. Silent if communication
        is successful. Pop up error message in pyvisa.constants.StatusCode
    '''

    def __init__(self, parent, text, moretext=''):
        QtGui.QWidget.__init__(self, parent)

        self.setIcon(QtGui.QMessageBox.Warning)
        self.addButton(QtGui.QMessageBox.Ok)
        self.setText(text)
        self.setInformativeText(moretext)
