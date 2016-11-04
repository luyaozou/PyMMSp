#! encoding = utf-8

def set_phase(phase_text):
    ''' Set the lockin phase to phase_text.
        Arguments
            phase_text: str, user input
        Returns communication status
            0: safe
            1: fatal
    '''

    try:
        phase = float(phase_text)
        if phase >= 0 and phase < 360:
            # call lockin
            return 0
        else:
            return 1
    except ValueError:
        return 1


def set_harm(harm_text):
    ''' Set the lockin harmonics to idx. '''

    try:
        harm = int(harm_text)
        if harm > 0 and harm < 5:
            # call lockin
            return 0
        else:
            return 1
    except ValueError:
        return 1

def set_sensitivity(sens_index):
    ''' Set the lockin sensitivity '''

    sens_list = [1, 0.5, 0.2, 0.1, 0.05, 0.02, 0.01,
                 1e-3, 5e-4, 2e-4, 1e-4, 5e-5, 2e-5, 1e-5, 5e-6, 2e-6, 1e-6]

    if sens_index >= len(sens_list):
        return 1
    else:
        # call lockin
        return 0

def set_tc(tc_index):
    ''' Set the lockin time constant '''

    tc_list = [3e-5, 1e-4, 3e-4, 1e-3, 3e-3, 1e-2, 3e-2, 1e-1, 3e-1, 1, 3, 10]

    if tc_index >= len(tc_list):
        return 1
    else:
        # call lockin
        return 0

def set_couple(couple_text):
    ''' Set the lockin couple '''

    if couple_text == 'AC':
        return 0
    elif couple_text == 'DC':
        return 0
    else:
        return 1

def set_reserve(reserve_text):
    ''' Set the lockin reserve '''

    if reserve_text == 'Low Noise':
        return 0
    elif reserve_text == 'Normal':
        return 0
    elif reserve_text == 'High Reserve':
        return 0
    else:
        return 1
