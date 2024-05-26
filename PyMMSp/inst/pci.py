#! encoding = utf-8


def query_inst_name(pciHandle):
    ''' Query instrument name
        Returns instrument name, str
    '''

    try:
        text = pciHandle.query('*IDN?')
        return text.strip()
    except:
        return 'N.A.'


def set_sampling_len(len_text):
    ''' Set the oscilloscope sampling length to len_text
        Arguments
            len_text: str (user input)
        Returns communication status
            0: safe
            1: fatal
            2: warning
    '''

    try:
        length = int(len_text)
    except ValueError:
        return 1

    if length > 0 and length < 10000:
        return 0
    elif length > 10000:
        return 2
    else:
        return 1


def set_sampling_rate(rate_text):
    ''' Set the oscilloscope sampling rate to rate_text
        Arguments
            rate_text: str (user input, unit in MHz)
        Returns communication status
            0: safe
            1: fatal
            2: warning
    '''

    try:
        rate = int(rate_text)
    except ValueError:
        return 1

    if rate > 0.1 and rate < 10:
        return 0
    elif rate < 0:
        return 1
    else:
        return 2


def set_osc_avg(avg_text):
    ''' Set the oscilloscope average to avg_text
        Arguments
            avg_text: str (user input)
        Returns communication status
            0: safe
            1: fatal
            2: warning
    '''

    try:
        avg_text = int(avg_text)
    except ValueError:
        return 1


def set_sensitivity(sens_index):
    ''' Set the oscilloscope sensitivity to sens_index
        Arguments
            sens_index: int (user input)
        Returns communication status
            0: safe
            1: fatal
    '''

    sens_list = [20, 5, 1, 0.5, 0.2]

    sens_list[sens_index]
