#! encoding = utf-8

import sys
from PyQt4 import QtGui

import gui.MainWindow

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    window = gui.MainWindow.MainWindow()
    window.show()

    sys.exit(app.exec_())
