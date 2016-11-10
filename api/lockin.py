#! encoding = utf-8

def init_lia(lcHandle):
    ''' Initiate the lockin with default settings. '''

    lcHandle.write('OUTX1')      # GPIB output
    lcHandle.write('FMOD0;ISRC0;IGND1;DDEF1,0,0;DDEF2,1,0;FPOP1,1')


def read_freq(lcHandle):
    ''' Read current lockin frequency.
        Returns frequency in kHz (float)
    '''

    try:
        text = lcHandle.query('FREQ?')
        freq = float(text.strip()) * 1e-3
    except:
        freq = 0

    return freq


def read_harm(lcHandle):
    ''' Read current lockin harmonics.
        Returns verbatim text
    '''

    try:
        text = lcHandle.query('HARM?')
    except:
        text = 'N.A.'

    return text.strip()


def set_harm(lcHandle, harm):
    ''' Set the lockin harmonics to idx.
        Arguments
            lcHandle: pyvisa.resources.Resource, Lockin handle
            harm: int
        Returns communication status
            0: safe
            1: fatal
    '''

    try:
        lcHandle.write('HARM{:d}'.format(harm))
        return 0
    except:
        return 1


def read_phase(lcHandle):
    ''' Read current lockin phase.
        Returns verbatim text
    '''

    try:
        text = lcHandle.query('PHAS?')
    except:
        text = 'N.A.'

    return text.strip()


def set_phase(lcHandle, phase):
    ''' Set the lockin phase to phase_text.
        Arguments
            lcHandle: pyvisa.resources.Resource, Lockin handle
            phase: float
        Returns communication status
            0: safe
            1: fatal
    '''

    try:
        lcHandle.write('PHAS{:.2f}'.format(phase))
        return 0
    except:
        return 1


def auto_phase(lcHandle):
    ''' Autophase in lockin '''

    try:
        lcHandle.write('APHS')
        return 0
    except:
        return 1


def read_sens(lcHandle):
    ''' Read current lockin sensitivity.
        Returns index number (int)
    '''

    try:
        text = lcHandle.query('SENS?')
        index = int(text.strip())
    except:
        index = 0

    return index


def set_sens(lcHandle, sens_index):
    ''' Set the lockin sensitivity.
        Arguments
            lcHandle: pyvisa.resources.Resource, Lockin handle
            sens_index: int, user input.
                        The index directly map to the lockin command
        Returns communication status
            0: safe
            1: fatal
    '''

    try:
        lcHandle.write('SENS{:d}'.format(sens_index))
        return 0
    except:
        return 1


def read_tc(lcHandle):
    ''' Read current lockin sensitivity.
        Returns index number (int)
    '''

    try:
        text = lcHandle.query('OFLT?')
        index = int(text.strip())
    except:
        index = 0

    return index


def set_tc(lcHandle, tc_index):
    ''' Set the lockin time constant.
        Arguments
            lcHandle: pyvisa.resources.Resource, Lockin handle
            tc_index: int, user input.
                      The index directly map to the lockin command
        Returns communication status
            0: safe
            1: fatal
    '''

    try:
        lcHandle.write('OFLT{:d}'.format(tc_index))
        return 0
    except:
        return 1


def read_couple(lcHandle):
    ''' Read current lockin couple.
        Returns couple text (str)
    '''

    a_dict = {'0': 'AC', '1': 'DC'}

    try:
        text = lcHandle.query('ICPL?')
        return a_dict[text.strip()]
    except:
        return 'N.A.'


def set_couple(lcHandle, couple_text):
    ''' Set the lockin couple.
        Arguments
            lcHandle: pyvisa.resources.Resource, Lockin handle
            couple_text: str, user input.
        Returns communication status
            0: safe
            1: fatal
    '''

    a_dict = {'AC': 'ICPL0',
              'DC': 'ICPL1'}

    try:
        lcHandle.write(a_dict[couple_text])
        return 0
    except:
        return 1


def read_reserve(lcHandle):
    ''' Read current lockin reserve.
        Returns reserve text (str)
    '''

    a_dict = {'2': 'Low Noise',
              '1': 'Normal',
              '0':'High Reserve'}

    try:
        text = lcHandle.query('RMOD?')
        return a_dict[text.strip()]
    except:
        return 'N.A.'


def set_reserve(lcHandle, reserve_text):
    ''' Set the lockin reserve '''

    a_dict = {'Low Noise': 'RMOD2',
              'Normal': 'RMOD1',
              'High Reserve': 'RMOD0'}

    try:
        lcHandle.write(a_dict[reserve_text])
    except:
        return 1
