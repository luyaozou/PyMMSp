#! encoding = utf-8
""" Constants for PyMMSp """
from importlib.resources import files

VERSION = '1.0.0'

BUTTONLABEL = {'confirm': ['Okay',],
               'complete': ['Mission complete'],
               'accept': ['Okay',],
               'reject': ['Cancel',],
               'error': ['Oops!',]
               }

TEMP_DIR = files('PyMMSp.data')
