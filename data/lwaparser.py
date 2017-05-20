#! encoding = utf-8

''' LWA file parser '''

import re
import numpy as np

def scan_header(filename):
    ''' Scan headers in the lwa file.
    Returns
        entry_settings: list of entry setting tuples
        line_numbers: start line number of each header in the file
    '''

    if filename:
        entry_settings = [(1, 2, 1, 2, 0, 0, 60, 'scan1'),
                          (1, 2, 1, 2, 0, 0, 60, 'scan2')]
    else:
        entry_settings = None

    return entry_settings
