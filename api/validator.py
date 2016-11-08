#! encoding = utf-8
''' A collection of user input validators.
    Always returns input status first, and converted  values, if possible.
'''

MULTIPLIER = [1, 3, 3, 6, 9, 12, 18, 27, 27]    # VDI multiplication factor

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


def val_lc_phase(text):
    ''' Validate locking phase input.
        Arguments: text: str
        Returns
            status: int (0: safe; 1: error; 2: warning)
            phase: float
    '''

    try:
        phase = float(text)
        if phase <= 180 and phase > -180:
            return 0, phase
        else:
            return 2, wrap_phase(phase)
    except ValueError:
        return 1, 0


def val_lc_harm(harm_text, freq_text):
    ''' Validate locking phase input.
        Arguments
            harm_text: str, harmonics input text
            freq_text: str, locked frequency input text
        Returns
            status: int (0: safe; 1: error; 2: warning)
            harm: int
    '''
    try:
        harm = int(harm_text)
        freq = float(freq_text)
        if harm > 0 and harm < (102000/freq):
            return 0, harm
        else:
            return 2, 1
    except ValueError:
        return 1, 1


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
            status: int (0: safe; 1: error)
            syn_freq: float, synthesizer frequency
    '''

    try:
        probf = float(probfreqtext)
        syn_freq = calc_syn_freq(probf, band_index)
        if syn_freq > 0 and synfreq < 50000:
            return 0, syn_freq
        else:
            return 1, syn_freq
    except ValueError:
        return 1, syn_freq


def val_syn_power(power):
    ''' Validate synthesizer power input.
        Arguments
            power: int
        Returns
            status: int
    '''

    if set_power <= 0 or set_power >= -20:
        return 0
    else:
        return 1


def conv_mod_freq_kHz(freq_text, freq_unit_text):
    ''' calculate modulation frequency in the unit of kHz.
        Arguments
            freq_text: str, modulation frequency user input
            freq_unit_text: str, modulation frequency unit
        Returns
            status: int (0: safe; 1: error)
            freq_kHz: float
    '''

    unit_conv = {'Hz':1e-3, 'kHz':1, 'MHz':1e3, 'GHz':1e6}

    try:
        freq_kHz = float(freq_text) * unit_conv[freq_unit_text]
        return 0, freq_kHz
    except (ValueError, KeyError):
        return 1, 0


def val_syn_mod_freq(freq_text, freq_unit_text):
    ''' Validate synthesizer modulation frequency input.
        Arguments
            freq_text: str, modulation frequency user input
            freq_unit_text: str, modulation frequency unit
        Returns
            status: int (0: safe; 1: error; 2: warning)
            freq: float
    '''

    status, modfreq = conv_mod_freq_kHz(freq_text, freq_unit_text)

    if status:      # text conversion fails
        return status, 0
    else:
        if modfreq < 100 and modfreq > 0:    # valid input
            return status, modfreq
        else:               # out of range
            return status, 0


def conv_mod_depth_kHz(depth_text, depth_unit_text):
    ''' calculate modulation depth in the unit of kHz (for FM).
        Arguments
            depth_text: str, modulation frequency user input
            depth_unit_text: str, modulation depth unit text
        Returns
            status: int (0: safe; 1: error)
            depth: float (in kHz)
    '''

    unit_conv = {'Hz':1e-3, 'kHz':1, 'MHz':1e3, '%':1}

    try:
        depth = float(depth_text) * unit_conv[depth_unit_text]
        return 0, depth
    except (ValueError, KeyError):
        return 1, 0


def val_syn_mod_depth(depth_text, depth_unit):
    ''' Validate synthesizer modulation depth input.
        Arguments
            depth_text: str, modulation depth user input
            depth_unit: int, modulation depth unit
        Returns
            status: int (0: safe; 1: error; 2: warning)
            freq: float
    '''

    status, depth = conv_mod_depth_kHz(depth_text, depth_unit)

    if status:
        return status, 0            # conversion fails

    if depth_unit == '%':
        if depth <= 75 and depth > 0:       # valid input
            return 0, depth
        else:
            return 1, 0
    else:
        if depth > 0 and depth <= 5000:       # valid input
            return 0, depth
        elif depth > 5000:          # large depth, warning
            return 2, depth
        else:                       # invalid
            return 1, 0
