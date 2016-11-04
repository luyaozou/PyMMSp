#! encoding = utf-8
import time

MULTIPLIER = [1, 3, 3, 6, 9, 12, 18, 27, 27]    # VDI multiplication factor

def ramp_up(start, stop):
    ''' A integer list generator. start < stop '''

    n = start
    while n < stop:
        n = n + 1
        yield n


def ramp_down(start, stop):
    ''' A integer list generator. start > stop '''

    n = start
    while n > stop:
        n = n - 1
        yield n


def calc_syn_freq(probfreq, band_index):
    ''' Calculate synthesizer frequency from prob frequency '''

    synfreq = probfreq / MULTIPLIER[band_index]

    return synfreq

def read_syn_power():
    ''' Read current synthesizer power '''

    return -20


def set_syn_power(set_power):
    ''' Set synthesizer power '''

    current_power = read_syn_power()

    if set_power > 0 or set_power < 20:
        return 1
    elif set_power > current_power:
        # turn on RF
        for n in ramp_up(current_power, set_power):
            # talk to synthesizer
            time.sleep(1)   # pause 1 second
        return 0
    elif set_power < current_power:
        for n in ramp_down(current_power, set_power):
            # talk to synthesizer
            time.sleep(1)   # pause 1 second
        return 0
    else:
        pass
        return 0


def syn_power_toggle(toggle_stat):
    ''' Turn RF power on/off.
        Returns communication status
            0: off
            1: on
    '''

    if toggle_stat:     # user want to turn on RF
        set_syn_power(0)
        return 1
    else:               # user want to turn off RF
        set_syn_power(-20)
        # turn off RF
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


def set_am(freqtext, depthtext, toggle_stat):
    ''' Set synthesizer AM to freq and depth.
        Arguments
            freqtext: str (user input)
            depthtext: str (user input)
            toggle_stat: boolean
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
        mod_toggle(toggle_stat)

    return freq_stat, depth_stat


def set_fm(freqtext, depthtext, toggle_stat):
    ''' Set synthesizer FM to freq and depth.
        Arguments
            freqtext: str (user input)
            depthtext: str (user input)
            toggle_stat: boolean
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
        mod_toggle(toggle_stat)

    return freq_stat, depth_stat


def mod_toggle(toggle_stat):
    ''' Turn on/off modulation.
        Arguments
            toggle_stat: boolean
        Returns
            None
    '''

    if toggle_stat:
        print('On')
    else:
        print('Off')

    return None
