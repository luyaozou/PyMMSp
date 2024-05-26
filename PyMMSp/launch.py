#! encoding = utf-8

import sys
from PyQt6 import QtWidgets
from PyMMSp.ui import MainWindow


if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow.MainWindow()
    window.show()

    sys.exit(app.exec())
