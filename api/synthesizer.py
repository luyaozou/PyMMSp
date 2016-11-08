#! encoding = utf-8
import time


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


def read_syn_power():
    ''' Read current synthesizer power '''

    return -20


def set_syn_power(synHandle, set_power):
    ''' Set synthesizer power '''

    current_power = read_syn_power()

    if set_power > current_power:
        # turn on RF
        for n in ramp_up(current_power, set_power):
            # talk to synthesizer
            time.sleep(0.5)   # pause 0.5 second
        return 0
    elif set_power < current_power:
        for n in ramp_down(current_power, set_power):
            # talk to synthesizer
            time.sleep(0.5)   # pause 0.5 second
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

def set_syn_freq(synHandle, freq):
    ''' Set the synthesizer frequency to freq.
        Arguments
            lcHandle: pyvisa.resources.Resource, synthesizer handle
            freq: float
        Returns communication status
            0: safe
            1: fatal
    '''

    try:
        status = synHandle.write()
        return status
    except:
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

    status = 0

    return status


def set_am(synHandle, freq, depth, toggle_stat):
    ''' Set synthesizer AM to freq and depth.
        Arguments
            freq: float
            depth: float
            toggle_stat: boolean
        Returns communication status
            0: safe
            1: fatal
    '''

    # if all valid, call synthesizer
    status = synHandle.write()
    # call synthesizer
    mod_toggle(toggle_stat)

    return status


def set_fm(synHandle, freq, depth, toggle_stat):
    ''' Set synthesizer FM to freq and depth.
        Arguments
            freq: float
            depth: float
            toggle_stat: boolean
        Returns communication status
            0: safe
            1: fatal
    '''


    status = synHandle.write()
    mod_toggle(toggle_stat)
    return status


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
