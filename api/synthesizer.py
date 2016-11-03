#! encoding = utf-8

MULTIPLIER = [1, 3, 3, 6, 9, 12, 18, 27, 27]    # VDI multiplication factor

def calc_syn_freq(probfreq, band_index):
    ''' Calculate synthesizer frequency from prob frequency '''

    synfreq = probfreq / MULTIPLIER[band_index]

    return synfreq

def read_syn_power():
    ''' Read current synthesizer power '''

    return -20


def set_syn_power(power):
    ''' Set synthesizer power '''
    if power > 0 or power < 20:
        return 1
    else:
        return 0


def read_syn_freq():
    ''' Read current synthesizer frequecy '''

    return 0

def set_syn_freq(probfreqtext, band_index):
    ''' Set the synthesizer frequency to freq.
        Arguments
            probfreqtext: str (user input)
            band_index:   int (list index)
        Returns communication status
            0: safe
            1: fatal
    '''

    try:
        probfreq = float(probfreqtext)
        synfreq = calc_syn_freq(probfreq, band_index)
        if synfreq > 0 and synfreq < 50000:
            # call synthesizer
            return 0
        else:
            return 1
    except ValueError:
        return 1


def read_mod_par():
    ''' Read current modulation setting.
        Returns
            freq:  mod freq, str
            depth: mod depth, str
    '''

    return '1', '1'


def set_mod_mode(mod_index):
    ''' Set synthesizer modulation mode.
        Arguments: mod_index, int
            0: no modulation
            1: AM
            2: FM
        Returns communication status.
            0: safe
            1: fatal
    '''

    if not mod_index:
        # turn of modulation
        pass
    elif mod_index == 1:
        # turn of FM (if necessary)
        # turn on AM
        pass
    elif mod_index == 2:
        # turn of AM (if necessary)
        # turn on FM
        pass
    else:
        pass

    comm_stat = 0

    return comm_stat


def set_am(freqtext, depthtext, toggle_bool):
    ''' Set synthesizer AM to freq and depth.
        Arguments
            freqtext: str (user input)
            depthtext: str (user input)
            toggle_bool: boolean
        Returns freq_stat and depth_stat
            0: safe
            1: fatal
            2: warning
    '''

    try:
        modfreq = float(freqtext)
        if modfreq < 100 and modfreq > 0:    # valid input
            freq_stat = 0
        else:               # out of range: fatal
            freq_stat = 2
    except ValueError:      # invalid
        freq_stat = 1

    try:
        depth = float(depthtext)
        if depth <= 75 and depth > 0:       # valid input
            depth_stat = 0
        else:
            depth_stat = 1  # out of range: fatal
    except ValueError:
        depth_stat = 1

    # if all valid, call synthesizer
    if not freq_stat and not depth_stat:
        # call synthesizer
        mod_toggle(toggle_bool)

    return freq_stat, depth_stat


def set_fm(freqtext, depthtext, toggle_bool):
    ''' Set synthesizer FM to freq and depth.
        Arguments
            freqtext: str (user input)
            depthtext: str (user input)
            toggle_bool: boolean
        Returns freq_stat and depth_stat
            0: safe
            1: fatal
            2: warning
    '''

    try:
        modfreq = float(freqtext)
        if modfreq < 100 and modfreq > 0:    # valid input
            freq_stat = 0
        else:               # out of range: fatal
            freq_stat = 1
    except ValueError:      # invalid
        freq_stat = 1

    try:
        depth = float(depthtext)
        if depth <= 10000 and depth > 0:       # valid input
            depth_stat = 0
        elif depth > 10000:
            depth_stat = 2  # out of range: warning
        else:
            depth_stat = 1  # out of range: fatal
    except ValueError:
        depth_stat = 1      # invalid

    # if all valid, call synthesizer
    if not freq_stat and (not depth_stat or depth_stat==2):
        # call synthesizer
        mod_toggle(toggle_bool)

    return freq_stat, depth_stat


def mod_toggle(toggle_bool):
    ''' Turn on/off modulation.
        Arguments
            toggle_bool: boolean
        Returns
            None
    '''

    if toggle_bool:
        print('On')
    else:
        print('Off')

    return None
