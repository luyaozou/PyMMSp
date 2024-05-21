#! encoding = utf-8

import sys
from PyQt6 import QtGui
from PyMMSp

import PyMMSp.ui.MainWindow

if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)

    window = PyMMSp.gui.MainWindow.MainWindow()
    window.show()

    sys.exit(app.exec_())
