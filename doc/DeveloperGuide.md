# Developer's Guide for `PySpec`
### Luyao Zou
### Widicus Weaver Group
### Department of Chemistry
### Emory University

# System Requirement

`PySpec` is developed in Python, and thus is supposed to be cross-platform.
Its behavior, however, does show small differences between Linux and Windows systems.
It is not tested in Os X, but the behavior is expected to be similar to Linux.

The following Python package and environments are required to run `PySpec`:

* Python 3
* PyQt 5: provides the GUI framework
* numpy: provides data array storage and manipulation functionality
* scipy: provides data manipulation functionality
* pyqtgraph: provides real time visualization. Built on PyQt
* PyVisa 1.8: provides API for VISA instruments. Requires National Instrument VISA C library.
* pyniscope from [Bernardo Kyotoku](https://github.com/bernardokyotoku/pyniscope "target=_blank"): provides API for National Instrument Digitizer Card. Requires National Instrument NISCOPE C library.

# File Architecture

* `./api/` contains instrumental commands. These commands need to be retrieved from the vendor's program guide for each instrument, and wrapped into Python functions.
`./api/validator.py` specifically contains validation functions for all user inputs.
`./api/general.py` specifically contains functions associated with `PyVisa` and `pyniscope` instrument handles.

* `./daq/` contains data acquisition dialog windows. Each DAQ window is a child class of `QtGui.QDialog`.

* `./data/` contains data manipulation and saving routines.

* `./doc/` contains `MarkDown` documentations and images.

* `./gui/` contains GUI classes and objects.
`./gui/Dialogs.py` contains pop-up dialog windows.
`./gui/MainWindow.py` is the main window instance.
`./gui/Panels.py` defines each panel displayed in the main window.
`./gui/SharedWidgets.py` contains shared widgets in `PySpec`, such as error message colors, and message pop-up dialogs, and lists of lockin sensitivities and time constants.

# Naming and Style Convention

Please follow the [Style Guide for Python Code](http://legacy.python.org/dev/peps/pep-0008/) for naming and style convention.

In general, function names are lower case and may be linked by underscores, e.g., `query_err_msg`.
Internal function names are led by an underscore, e.g., `_compare`.
Class names are capitalized in the initial, e.g., `SynStatus`.
Class instance names are lower case in the first letter but have capitalized initial letters in the following words, e.g., `synStatus` and `refreshButton`.

* All `QLineEdit` instance names end with `Fill` (fill text).
* All `QComboBox` instance names end with `Sel` (select options).
* `QLabel` instance names do not have a specific ending.

# Unit of variables

Keeping the unit of variables consistent across the program is essential for the science.
There are hundreds of variables, and their values are across orders of magnitudes, from tiny numbers such as the pressure in high vacuum, to gigantic numbers such as the frequencies of millimeter light.
The best way to keep the unit conversion ease of mind is to use S.I. unit across the board.
Specifically, `pyqtgraph` provides two neat methods to deal with float numbers: `siFormat` and `siEval`.
`siFormat` converts a float number to a string with a unit with proper metric prefix, e.g.,

    pyqtgraph.siFormat(3e9, suffix='Hz')

returns string `"3 GHz"`, and you can specify the precision.
Reversely, `siEval` evaluates a string in such format, and returns the float number in the correct order of magnitude.

There are two exceptions to this general unit conversion rule:
1.  Synthesizer AM modulation depth.
    The AM depth is expressed in % in `PySpec`.
    Both the instrument write and query code use % as its unit.
2.  Synthesizer frequency.
    `PySpec` internally uses `Hz` as the unit.
    It applies to the validator, the instrument communication codes, and the instrument information classes.
    In the user input widgets and scanning routine, however, `MHz` is used for convenience.
    This includes the synthesizer control panel, and the setting entries in the JPL scanning routine.
    When saving the data array, the frequency vector is also in the unit of `MHz`.
    This means unit conversion of a factor of `1e6` or `1e-6` will be involved in the conversion of user inputs and data arrays to `PySpec` internal and instrumental frequency values.
3.  QTimer.
    `Qt.QTimer` uses millisecond, instead of second, as the time unit.
    The `waittime` in lockin scans also use millisecond.
    In estimating the batch project time for JPL scanning routine, the batch time, as well as the `QProgressBar`, is calculated in the unit of second.
    Make sure to use the correct unit, otherwise time estimation will be off by *a lot*.


# Test Mode

In developing new GUI windows for various data collection routines, intense tests on the GUI components are necessary.
Only one computer, however, has physical access to the lab instruments.
A test mode is therefore designed for developers to develop and test GUI components on other computers without actually connecting to a lab instrument.

In the main GUI window, there is a menu action called `Test Mode` that is checkable.
Once checked, test mode is activated and developers can launch GUI windows and test GUI components without physically connecting to instruments.
A message warning the test mode activity will be displayed in the left bottom of the main GUI window, as well as in the window title.

This functionality is made possible by enabling the `checkable` option in Qt's menu action object.
In the `QtGui.QMainWindow` class, define `testModeAction` as a checkable action.

    class MainWindow(QtGui.QMainWindow):

        def __init__(self, parent=None):

            QtGui.QMainWindow.__init__(self)
            self.testModeAction = QtGui.QAction('Test Mode', self)
            self.testModeAction.setCheckable(True)
            self.testModeAction.setShortcut('Ctrl+T')
            menuTest = self.menuBar().addMenu('&Test')
            menuTest.addAction(self.testModeAction)

Now before each communication with the instrument, use a conditional statement to bypass the instrument communication.

    # self.main is pointed to the MainWindow instance.
    if self.main.testModeAction.isChecked():
        # bypass instrument API
    else:
        # call instrument API

# Foolproof

Foolproof mechanisms are one of the key components in the `PySpec` development.
It is extremely important to protect the valuable instruments and to ensure correct experimental settings.
Foolproof codes are implemented in multiple levels.

## Use validation functions

Use validation functions to check every input values, and return error message code.
All validation functions need to be defined in `./api/validator.py`.
All validation functions need to return *two* values.
The first returned value is the error message code: 0 is fatal, 1 is warning, and 2 is safe/valid.
All foolproof mechanisms are build upon the error message codes returned from validation functions.
The second (and so on so forth) returned value(s) are the text input converted to the correct data type: `str`, `float`, or `int`.
These returned values can then be used internally in `PySpec`.

## Display error message

We can notify the user error messages in varies scenarios.

* Change frame color in `QLineEdit` objects.
The color is defined in `msgcolor` function located in `./gui/SharedWidgets.py`

        import SharedWidgets as Shared
        obj = QtGui.QLineEdit()
        obj.setStyleSheet('border:  1px solid {:s}'.format(Shared.msgcolor(msgcode)))

* Change text color in 'QLabel' objects.

        import SharedWidgets as Shared
        obj = QtGui.QLabel()
        obj.setStyleSheet('color: {:s}'.format(Shared.msgcolor(msgcode)))

* Pop up message dialog. You may choose to pop up error message only at fatal scenarios, or you may construct more detailed pop-up windows.

        import SharedWidgets as Shared
        if msgcode:     # remember 0 is fatal
            pass
        else:
            msg = Shared.MsgError(self.main, 'Invalid input!', 'Please fix invalid inputs before proceeding.')
            msg.exec_()

## Use built-in PyQt functionality

PyQt (or actually Qt, because PyQt is just a Python wrapper) offers a rich collection of built-in classes and objects.
Try to use their built-in functionality to foolproof.

For example, the RF power switch uses the `QInputDialog` class to confine the input values between -20 and 0.

    # Grab manual input power
    target_power, okay = QtGui.QInputDialog.getInt(self, 'RF Power',
                         'Manual Input (-20 to 0)', current_power, -20, 0, 1)

`QComboBox` provides a list of options for user to choose. These options can be coded in advance to prevent user from doing something crazy.
