#! encoding = utf-8
''' A collection of user input validators.
    Always returns input status first, and converted  values, if possible.
    Status Code: 0 - fatal; 1 - warning; 2 - safe
'''

from math import pi
from pyqtgraph import siEval

# VDI MULTIPLICATION FACTOR
MULTIPLIER = [1, 3, 3, 3, 6, 9, 12, 18, 27, 27]
# LOCKIN AMPLIFIER SENSTIVITY LIST (IN VOLTS)
LIASENSLIST = [2e-9, 5e-9, 1e-8, 2e-8, 5e-8, 1e-7, 2e-7, 5e-7,
               1e-6, 2e-6, 5e-6, 1e-5, 2e-5, 5e-5, 1e-4, 2e-4, 5e-4,
               1e-3, 2e-3, 5e-3, 1e-2, 2e-2, 5e-2, 1e-1, 2e-1, 5e-1, 1
               ]
# LOCKIN AMPLIFIER TIME CONSTANT LIST (IN MILLISECONDS)
LIATCLIST = [1e-2, 3e-2, 1e-1, 3e-1, 1, 3, 10, 30, 1e2, 3e2, 1e3, 3e3, 1e4, 3e4]


def wrap_phase(phase):
    ''' Wrap phase into the range of [-180, 180] degrees.
        Arguments
            phase: float
        Returns
            phase: float
    '''

    if phase > 180:
        while phase > 180:
            phase -= 360
    elif phase <= -180:
        while phase <= -180:
            phase += 360
    else:
        pass

    return phase


def val_int(text):
    ''' General validator for int number '''

    try:
        number = int(text)
        return 2, number
    except ValueError:
        return 1, 0


def val_float(text):
    ''' General validator for float number '''

    try:
        number = float(text)
        return 2, number
    except ValueError:
        return 1, 0.


def val_lc_phase(text):
    ''' Validate locking phase input.
        Arguments: text: str
        Returns
            status: int (2: safe; 1: warning; 0: fatal)
            phase: float
    '''

    try:
        phase = float(text)
        if phase <= 180 and phase > -180:
            return 2, phase
        else:
            return 1, wrap_phase(phase)
    except ValueError:
        return 0, 0


def val_lc_harm(harm_text, freq):
    ''' Validate locking phase input.
        Arguments
            harm_text: str, harmonics input text
            freq: float, locked frequency input
        Returns
            status: int (2: safe; 1: warning; 0: fatal)
            harm: int
    '''
    try:
        harm = int(harm_text)
        if harm > 0 and harm < (102000/freq):
            return 2, harm
        else:
            return 0, 1
    except (ValueError, ZeroDivisionError):
        return 0, 1


def calc_syn_freq(probf, band_index):
    ''' Calculate synthesizer frequency from probing frequency.
        Arguments
            probf: float, probing frequency (MHz)
            band_index: int, VDI band index
        Returns
            synfreq: float, synthesizer frequency (MHz)
    '''

    syn_freq = probf / MULTIPLIER[band_index]
    return syn_freq


def val_syn_freq(probf_text, band_index):
    ''' Validate synthesizer prob frequency input.
        Arguments
            probf_text: str, prob frequency input text
            band_index: int, VDI band index
        Returns
            status: int (2: safe; 1: warning; 0: fatal)
            syn_freq: float, synthesizer frequency
    '''

    try:
        probf = float(probf_text)
        syn_freq = calc_syn_freq(probf, band_index)
        if syn_freq > 0 and syn_freq < 50000:
            return 2, syn_freq
        else:
            return 0, 50000
    except ValueError:
        return 0, 50000


def val_prob_freq(probf_text, band_index):
    ''' Validate prob frequency input.
        Arguments
            probf_text: str, prob frequency input text
            band_index: int, VDI band index
        Returns
            status: int (2: safe; 1: warning; 0: fatal)
            probf: float, probing frequency
    '''

    try:
        probf = float(probf_text)
        syn_freq = calc_syn_freq(probf, band_index)
        if syn_freq > 0 and syn_freq < 50000:
            return 2, probf
        else:
            return 0, 50000
    except ValueError:
        return 0, 50000


def val_syn_power(power):
    ''' Validate synthesizer power input.
        Arguments
            power: int
        Returns
            status: int
    '''

    if set_power <= 0 or set_power >= -20:
        return 2
    else:
        return 0


def val_syn_mod_freq(freq_text, freq_unit_text):
    ''' Validate synthesizer modulation frequency input.
        Arguments
            freq_text: str, modulation frequency user input
            freq_unit_text: str, modulation frequency unit
        Returns
            status: int (2: safe; 1: warning; 0: fatal)
            freq: float (Hz)
    '''

    if freq_text:   # if not empty string
        modfreq = siEval(freq_text + freq_unit_text)
    else:
        return 0, 0

    if modfreq < 1e5 and modfreq >= 0:    # valid input
        return 2, modfreq
    else:               # out of range
        return 0, 0


def val_syn_mod_depth(depth_text, depth_unit_text):
    ''' Validate synthesizer modulation depth input.
        Arguments
            depth_text: str, modulation depth user input
            depth_unit_text: int, modulation depth unit
        Returns
            status: int (2: safe; 1: warning; 0: fatal)
            freq: float (dimensionless for AM, Hz for FM)
    '''

    if depth_unit_text == '%':
        try:
            depth = float(depth_text) * 1e-2
            if depth <= 0.75 and depth >= 0:       # valid input
                return 2, depth
            else:
                return 0, 0
        except ValueError:
            return 0, 0
    else:
        if depth_text:  # if not empty string
            depth = siEval(depth_text + depth_unit_text)
        else:
            return 0, 0
        if depth >= 0 and depth <= 5e6:       # valid input
            return 2, depth
        elif depth > 5e6:          # large depth, warning
            return 1, depth
        else:                       # invalid
            return 0, 0


def val_syn_lf_vol(vol_text):
    ''' Validate synthesizer LF output voltage.
        Arguments
            vol_text: str, LF voltage user input
        Returns
            status: int (2: safe; 1: warning; 0: fatal)
            vol: float (V)
    '''

    try:
        vol = float(vol_text)
        if vol >=0 and vol < 3.5:
            return 2, vol
        else:
            return 0, 0
    except ValueError:
        return 0, 0


def val_monitor_sample_len(len_text):
    ''' Validate sample length for real-time monitor.
        Arguments
            len_text: str, samplen length user input
        Returns
            status: int (2: safe; 1: warning; 0: fatal)
            slen: int
    '''

    try:
        slen = int(len_text)
        if slen>10 and slen<=1000:
            return 2, slen
        elif slen>1000 or (slen>0 and slen<=10):
            return 1, slen
        else:
            return 0, 1
    except ValueError:
        return 0, 1


def val_lc_monitor_srate(srate_index, tc_index):
    ''' Validate screen update speed of the lockin monitor.
        Arguments
            srate_index: lc sample rate index, int
            tc_index: lc time constant index, int
        Returns
            status: int (2: safe; 1: warning; 0: fatal)
            waittime: screen update waittime in milliseconds, float
    '''

    waittime_list = [100, 200, 500, 1000, 2000, 5000, 10000]    # milliseconds
    waittime = waittime_list[srate_index]
    tc = LIATCLIST[tc_index]
    if tc*4*pi < waittime:
        return 2, waittime
    elif tc*2*pi < waittime:
        return 1, waittime
    else:
        return 0, tc*2*pi


def val_lc_waittime(text, tc_index):
    ''' Validate the wait time setting for lockin scans. The wait
        time must be longer than 2pi*time_const. Best > 3pi*time_const
        Arguments
            text: integration time user input, str
            tc_index: lc time constant index, int
        Returns
            status: int (2: safe; 1: warning; 0: fatal)
            waittime: wait time, float in ms
    '''

    time_const = LIATCLIST[tc_index]

    try:
        waittime = float(text)
        if (waittime > time_const * 3 * pi):
            return 2, waittime
        elif (waittime > time_const * 2 * pi):
            return 1, waittime
        else:
            return 0, 0
    except ValueError:
        return 0, 0
