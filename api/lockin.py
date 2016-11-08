#! encoding = utf-8

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


def init_lia(LIAHandle):
    ''' Initiate the lockin with default settings. '''

    LIAHandle.write('OUTX1\n')      # GPIB output
    LIAHandle.write('FMOD0;ISRC0;IGND1;DDEF1,0,0;DDEF2,1,0;FPOP1,1\n')


def set_phase(LIAHandle, phase_text):
    ''' Set the lockin phase to phase_text.
        Arguments
            LIAHandle: pyvisa.resources.Resource, Lockin handle
            phase_text: str, user input
        Returns communication status
            0: safe
            1: fatal
    '''

    try:
        phase = float(phase_text)
        phase = wrap_phase(phase)
        stat = LIAHandle.write('PHAS{:.2f}'.format(phase), '\n')
        return stat
    except ValueError:
        return 1


def auto_phase(LIAHandle):
    ''' Autophase in lockin '''

    LIAHandle.write('APHS\n')


def set_harm(LIAHandle, harm_text):
    ''' Set the lockin harmonics to idx.
        Arguments
            LIAHandle: pyvisa.resources.Resource, Lockin handle
            harm_text: str, user input
        Returns communication status
            0: safe
            1: fatal
    '''

    freq = LIAHandle.query('FREQ?', '\n')
    try:
        harm = int(harm_text)
        if harm > 0 and harm < (102000/freq):
            LIAHandle.write('HARM{:d}'.format(harm), '\n')
            return 0
        else:
            return 1
    except ValueError:
        return 1


def set_sensitivity(LIAHandle, sens_index):
    ''' Set the lockin sensitivity.
        Arguments
            LIAHandle: pyvisa.resources.Resource, Lockin handle
            sens_index: int, user input.
                        The index directly map to the lockin command
        Returns communication status
            0: safe
            1: fatal
    '''

    stat = LIAHandle.write('SENS{:d}'.format(sens_index), '\n')
    return stat


def set_tc(LIAHandle, tc_index):
    ''' Set the lockin time constant.
        Arguments
            LIAHandle: pyvisa.resources.Resource, Lockin handle
            tc_index: int, user input.
                      The index directly map to the lockin command
        Returns communication status
            0: safe
            1: fatal
    '''

    stat = LIAHandle.write('OFLT{:d}'.format(tc_index), '\n')
    return stat


def set_couple(LIAHandle, couple_text):
    ''' Set the lockin couple.
        Arguments
            LIAHandle: pyvisa.resources.Resource, Lockin handle
            couple_text: str, user input.
        Returns communication status
            0: safe
            1: fatal
    '''

    if couple_text == 'AC':
        LIAHandle.write('ICPL0\n')
    elif couple_text == 'DC':
        LIAHandle.write('ICPL1\n')
    else:
        return 1


def set_reserve(reserve_text):
    ''' Set the lockin reserve '''

    if reserve_text == 'Low Noise':
        LIAHandle.write('RMOD2\n')
    elif reserve_text == 'Normal':
        LIAHandle.write('RMOD1\n')
    elif reserve_text == 'High Reserve':
        LIAHandle.write('RMOD0\n')
    else:
        return 1
