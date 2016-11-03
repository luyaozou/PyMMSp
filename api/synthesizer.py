#! encoding = utf-8

def read_syn_power():
    ''' Read current synthesizer power '''

    return '-20 dbm'


def set_syn_freq(freq):
    ''' Set the synthesizer frequency to freq '''
    pass


def set_am(freq, depth):
    ''' Set synthesizer AM to freq and depth '''
    pass


def set_fm(freq, depth):
    ''' Set synthesizer FM to freq and depth '''
    pass


def set_nomod():
    ''' Set synthesizer to NO modulation '''

    pass

def mod_on(toggle_bool):
    ''' Turn on/off modulation '''

    if toggle_bool:
        print('On')
    else:
        print('Off')

    return None
