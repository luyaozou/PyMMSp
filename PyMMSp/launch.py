#! encoding = utf-8

import sys
import platform
import ctypes
from PyQt6.QtWidgets import QApplication
from PyMMSp.ctrl.main import MainWindow

if __name__ == '__main__':

    # fix the bug of bad scaling on screens of different DPI
    if platform.system() == 'Windows':
        if int(platform.release()) >= 8:
            ctypes.windll.shcore.SetProcessDpiAwareness(True)

    app = QApplication(sys.argv)

    win = MainWindow()
    win.show()

    sys.exit(app.exec())
