#! encoding = utf-8
''' A collection of user input validators.
    Always returns status code first, and converted values, if possible.
    Status Code: 0 - fatal; 1 - warning; 2 - safe
'''

from math import pi
import operator
from pyqtgraph import siEval

# LOCKIN AMPLIFIER SENSTIVITY LIST (IN VOLTS)
LIASENSLIST= [2e-9, 5e-9, 1e-8, 2e-8, 5e-8, 1e-7, 2e-7, 5e-7,
               1e-6, 2e-6, 5e-6, 1e-5, 2e-5, 5e-5, 1e-4, 2e-4, 5e-4,
               1e-3, 2e-3, 5e-3, 1e-2, 2e-2, 5e-2, 1e-1, 2e-1, 5e-1, 1
               ]

# LOCKIN AMPLIFIER TIME CONSTANT LIST (IN MILLISECONDS)
LIATCLIST = [1e-2, 3e-2, 1e-1, 3e-1, 1, 3, 10, 30, 1e2, 3e2, 1e3, 3e3, 1e4, 3e4]

# VDI band information.
# Keys are the indices used in VDIBandComboBox, and values are the names, multiplication factors, and recommended frequency ranges.
VDIBANDNAME = {0: '1',
               1: '2',
               2: '3',
               3: '4',
               4: '5',
               5: '6',
               6: '7',
               7: '8a',
               8: '8b',
               9: '9'}

VDIBANDMULTI = {0: 1,
                1: 2,
                2: 3,
                3: 3,
                4: 6,
                5: 9,
                6: 12,
                7: 18,
                8: 27,
                9: 27}

VDIBANDRANGE = {0: (20, 50),    # !!! in the unit of GHz !!!
                1: (50, 75),
                2: (70, 115),
                3: (90, 140),
                4: (140, 225),
                5: (220, 330),
                6: (270, 460),
                7: (430, 700),
                8: (650, 800),
                9: (700, 1000)}


def _compare(num1, op, num2):
    ''' An comparison operator generator '''

    ops = {'>': operator.gt,
           '<': operator.lt,
           '>=': operator.ge,
           '<=': operator.le,
           '==': operator.eq}

    return ops[op](num1, num2)


def _wrap_phase(phase):
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


def val_int(text, safe=[], warning=[]):
    ''' General validator for int number.
        Comparison operators can be passed through safe & warning
        Each comparison list contains tuples of (op, num)
    '''

    try:
        number = int(text)
        # 1st test if the number is in the safe range
        boolean = True
        for op, num in safe:
            boolean *= _compare(number, op, num)
        if boolean:
            code = 2
        else:
            boolean = True
            for op, num in warning:
                boolean *= _compare(number, op, num)
            if boolean and warning: # make sure there is something to _compare
                code = 1
            else:
                code = 0
        return code, number
    except ValueError:
        return 0, 0


def val_float(text, safe=[], warning=[]):
    ''' General validator for int number.
        Comparison operators can be passed through safe & warning
        Each comparison list contains tuples of (op, num)
    '''

    try:
        number = float(text)
        # 1st test if the number is in the safe range
        boolean = True
        for op, num in safe:
            boolean *= _compare(number, op, num)
        if boolean:
            code = 2
        else:
            boolean = True
            for op, num in warning:
                boolean *= _compare(number, op, num)
            if boolean:
                code = 1
            else:
                code = 0
        return code, number
    except ValueError:
        return 0, 0


def val_lia_phase(text):
    ''' Validate locking phase input.
        Arguments: text: str
        Returns
            code: int (2: safe; 1: warning; 0: fatal)
            phase: float
    '''

    try:
        phase = float(text)
        if phase <= 180 and phase > -180:
            return 2, phase
        else:
            return 1, _wrap_phase(phase)
    except ValueError:
        return 0, 0


def val_lia_harm(harm_text, freq):
    ''' Validate locking phase input.
        Arguments
            harm_text: str, harmonics input text
            freq: float, locked frequency input
        Returns
            code: int (2: safe; 1: warning; 0: fatal)
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

    syn_freq = probf / VDIBANDMULTI[band_index]
    return syn_freq


def val_syn_freq(probf_text, band_index):
    ''' Validate synthesizer prob frequency input.
        Arguments
            probf_text: str, prob frequency input text (MHz)
            band_index: int, VDI band index
        Returns
            code: int (2: safe; 1: warning; 0: fatal)
            syn_freq: float, synthesizer frequency (Hz)
    '''

    try:
        probf = float(probf_text)
        syn_freq = calc_syn_freq(probf, band_index)
        if syn_freq > 0 and syn_freq < 50000:
            return 2, syn_freq * 1e6
        else:
            return 0, 5 * 1e10
    except ValueError:
        return 0, 5 * 1e10


def val_prob_freq(probf_text, band_index):
    ''' Validate prob frequency input.
        Arguments
            probf_text: str, prob frequency input text (MHz)
            band_index: int, VDI band index
        Safe range: specified in VDIBANDRANGE (GHz)
        Warning range: [20, 50] GHz * multiplication
        Returns
            code: int (2: safe; 1: warning; 0: fatal)
            syn_freq: float, synthesizer frequency (Hz)
    '''

    try:
        probf = float(probf_text)
        syn_freq = calc_syn_freq(probf, band_index)
        safe_range = VDIBANDRANGE[band_index]
        if syn_freq > 20000 and syn_freq < 50000:
            # prob freq in safe_range
            if (probf > safe_range[0]*1e3) and (probf < safe_range[1]*1e3):
                return 2, syn_freq * 1e6
            else:   # return a warning sign
                return 1, syn_freq * 1e6
        else:
            return 0, 5 * 1e10
    except ValueError:
        return 0, 5 * 1e10


def val_syn_mod_freq(freq_text, freq_unit_text):
    ''' Validate synthesizer modulation frequency input.
        Arguments
            freq_text: str, modulation frequency user input
            freq_unit_text: str, modulation frequency unit
        Safe range: [0, 1e5] Hz
        Warning range: (1e5, 16] Hz
    '''

    if freq_text:   # if not empty string
        freq_num = siEval(freq_text + freq_unit_text)
    else:
        return 0, 0

    code, freq = val_float(freq_num, safe=[('>=', 0), ('<=', 1e5)],
                           warning=[('>', 1e5), ('<=', 1e6)])
    return code, freq


def val_syn_am_depth(depth_text, depth_unit_text):
    ''' Validate synthesizer AM modulation depth input.
        Arguments
            depth_text: str, modulation depth user input
            depth_unit_text: int, modulation depth unit
        Safe range: (0, 75] '%'
        Warning range: (0, 75] '%'
    '''

    if depth_unit_text == '%':
        code, depth = val_float(depth_text, safe=[('>', 0), ('<=', 75)],
                                warning=[('>', 0), ('<=', 75)])
        return code, depth
    else:
        return 0, 0


def val_syn_fm_depth(depth_text, depth_unit_text):
    ''' Validate synthesizer FM modulation depth input.
        Arguments
            depth_text: str, modulation depth user input
            depth_unit_text: int, modulation depth unit
        Safe range: (0, 5e6] Hz for FM
        Warning range: (5e6, 64e6] Hz for FM (max 64 MHz)
    '''

    if depth_text:  # if not empty string
        depth_num = siEval(depth_text + depth_unit_text)
    else:
        return 0, 0

    code, depth = val_float(depth_num, safe=[('>', 0), ('<=', 5e6)],
                            warning=[('>', 5e6), ('<=', 6.4e7)])
    return code, depth


def val_syn_lf_vol(vol_text):
    ''' Validate synthesizer LF output voltage.
        Arguments
            vol_text: str, LF voltage user input
        Safe range: [0, 1]
        Warning range: (1, 3.5)
    '''

    code, volt = val_float(vol_text, safe=[('>=', 0), ('<=', 1.0)],
                           warning=[('>', 1.0), ('<', 3.5)])
    return code, volt


def val_monitor_sample_len(len_text):
    ''' Validate sample length for real-time monitor.
        Arguments
            len_text: str, samplen length user input
        Safe range: [20, 500]
        Warning range: > 0
    '''

    code, slen = val_int(len_text, safe=[('>=', 20), ('<=', 500)],
                         warning=[('>', 0)])
    return code, slen


def val_lia_monitor_srate(srate_index, tc_index):
    ''' Validate screen update speed of the lockin monitor.
        Arguments
            srate_index: LIA sample rate index, int
            tc_index: LIA time constant index, int
        Safe range: > 3pi*tc + 10
        Warning range: > 2pi*tc + 10
    '''

    waittime_list = [100, 200, 500, 1000, 2000, 5000, 10000]    # milliseconds
    waittime = waittime_list[srate_index]
    tc = LIATCLIST[tc_index]

    code, waittime = val_float(waittime, safe=[('>', tc*3*pi + 10)],
                               warning=[('>', tc*2*pi + 10)])
    if code:
        return code, waittime
    else:
        return code, tc*3*pi


def val_lia_waittime(text, tc_index):
    ''' Validate the wait time setting for lockin scans. The wait
        time must be longer than 2pi*time_const. Best > 3pi*time_const
        Arguments
            text: integration time user input, str
            tc_index: LIA time constant index, int
        Safe range: > 3pi*tc + 10
        Warning range: > 2pi*tc + 10
    '''

    time_const = LIATCLIST[tc_index]
    code, waittime = val_float(text, safe=[('>', time_const*3*pi + 10)],
                                 warning=[('>', time_const*2*pi + 10)])
    return code, waittime
