#! encoding = utf-8

import numpy as np


def init_lia(lcHandle):
    ''' Initiate the lockin with default settings.
        Returns visaCode
    '''

    num, vcode = lcHandle.write('OUTX1')      # GPIB output
    num, vcode = lcHandle.write('FMOD0;ISRC0;IGND1;DDEF1,0,0;DDEF2,1,0;FPOP1,1')

    return vcode


def query_inst_name(lcHandle):
    ''' Query instrument name
        Returns instrument name, str
    '''

    try:
        text = lcHandle.query('*IDN?')
        return text.strip()
    except:
        return 'N.A.'


def query_err_msg(lcHandle):


    try:
        text = lcHandle.query('ERRS?')
    except:
        return 'N.A.'


def read_freq(lcHandle):
    ''' Read current lockin frequency.
        Returns frequency in Hz (float)
    '''

    try:
        text = lcHandle.query('FREQ?')
        return float(text.strip())
    except:
        return 0


def read_harm(lcHandle):
    ''' Read current lockin harmonics.
        Returns harm: int
    '''

    try:
        text = lcHandle.query('HARM?')
        return int(text.strip())
    except:
        return 0


def set_harm(lcHandle, harm):
    ''' Set the lockin harmonics to idx.
        Arguments
            lcHandle: pyvisa.resources.Resource, Lockin handle
            harm: int
        Returns visaCode
    '''

    try:
        num, vcode = lcHandle.write('HARM{:d}'.format(harm))
        return vcode
    except:
        return 'IOError'


def read_phase(lcHandle):
    ''' Read current lockin phase.
        Returns phase: float
    '''

    try:
        text = lcHandle.query('PHAS?')
        return float(text.strip())
    except:
        return 0


def set_phase(lcHandle, phase):
    ''' Set the lockin phase to phase_text.
        Arguments
            lcHandle: pyvisa.resources.Resource, Lockin handle
            phase: float
        Returns visaCode
    '''

    try:
        num, vcode = lcHandle.write('PHAS{:.2f}'.format(phase))
        return vcode
    except:
        return 'IOError'


def auto_phase(lcHandle):
    ''' Autophase in lockin.
        Returns visaCode
    '''

    try:
        num, vcode = lcHandle.write('APHS')
        return vcode
    except:
        return 'IOError'


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
        Returns visaCode
    '''

    try:
        num, vcode = lcHandle.write('SENS{:d}'.format(sens_index))
        return vcode
    except:
        return 'IOError'


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
        Returns visaCode
    '''

    try:
        num, vcode = lcHandle.write('OFLT{:d}'.format(tc_index))
        return vcode
    except:
        return 'IOError'


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
        Returns visaCode
    '''

    a_dict = {'AC': 'ICPL0',
              'DC': 'ICPL1'}

    try:
        num, vcode = lcHandle.write(a_dict[couple_text])
        return vcode
    except:
        return 'IOError'


def read_reserve(lcHandle):
    ''' Read current lockin reserve.
        Returns reserve text (str)
    '''

    a_dict = {'2': 'Low Noise',
              '1': 'Normal',
              '0': 'High Reserve'}

    try:
        text = lcHandle.query('RMOD?')
        return a_dict[text.strip()]
    except:
        return 'N.A.'


def set_reserve(lcHandle, reserve_text):
    ''' Set the lockin reserve.
        Returns visaCode
    '''

    a_dict = {'Low Noise': 'RMOD2',
              'Normal': 'RMOD1',
              'High Reserve': 'RMOD0'}

    try:
        num, vcode = lcHandle.write(a_dict[reserve_text])
        return vcode
    except:
        return 'IOError'


def query_single_x(lcHandle):
    ''' Query single x reading from lockin.
        Returns x (float)
    '''

    try:
        x = lcHandle.query('OUTP?1')
        return x
    except:
        return 0


def read_ref_source(lcHandle):
    ''' Read reference source
        Returns
            text: str
    '''

    a_dict = {0:'External', 1:'Internal'}
    try:
        text = lcHandle.query('FMOD?')
        return a_dict[int(text.strip())]
    except:
        return 'N.A.'


def read_input_config(lcHandle):
    ''' Read input configuration
        Returns
            text: str
    '''

    a_dict = {0:'A', 1:'B', 2:'I (1 MΩ)', 3:'I (100 MΩ)'}
    try:
        text = lcHandle.query('ISRC?')
        return a_dict[int(text.strip())]
    except:
        return 'N.A.'


def read_input_grounding(lcHandle):
    ''' Read input grounding
        Returns
            text: str
    '''

    a_dict = {0:'Float', 1:'Ground'}
    try:
        text = lcHandle.query('IGND?')
        return a_dict[int(text.strip())]
    except:
        return 'N.A.'


def read_input_coupling(lcHandle):
    ''' Read input coupling
        Returns
            text: str
    '''

    a_dict = {0:'AC', 1:'DC'}
    try:
        text = lcHandle.query('ICPL?')
        return a_dict[int(text.strip())]
    except:
        return 'N.A.'


def read_input_filter(lcHandle):
    ''' Read input notch filter
        Returns
            text: str
    '''

    a_dict = {0:'No filter', 1:'Line notch',
              2:'2×Line notch', 3:'Both line notch'}
    try:
        text = lcHandle.query('ILIN?')
        return a_dict[int(text.strip())]
    except:
        return 'N.A.'


def read_lp_slope(lcHandle):
    ''' Read low pass filter slope
        Returns
            text: str
    '''

    a_dict = {0:'6 dB/oct', 1:'12 dB/oct',
              2:'18 dB/oct', 3:'24 dB/oct'}
    try:
        text = lcHandle.query('OFSL?')
        return a_dict[int(text.strip())]
    except:
        return 'N.A.'


def read_disp(lcHandle):
    ''' Read display parameter
        Returns
            text1, text2: str, for CH1 & CH2
    '''

    a_dict = {0:'X', 1:'R', 2:'X Noise', 3:'Aux In 1', 4:'Aux In 2'}
    b_dict = {0:'Y', 1:'θ', 2:'Y Noise', 3:'Aux In 3', 4:'Aux In 4'}

    try:
        text = lcHandle.query('DDEF?1')
        j, k = text.strip().split(',')
        ch1 = a_dict[int(j)]
        if k:
            ch1 += '; Ratio {:s}'.format(a_dict[k+2])
        else:
            pass
    except:
        ch1 = 'N.A.'

    try:
        text = lcHandle.query('DDEF?2')
        j, k = text.strip().split(',')
        ch2 = b_dict[int(j)]
        if k:
            ch2 += '; Ratio {:s}'.format(a_dict[k+2])
        else:
            pass
    except:
        ch2 = 'N.A.'

    return ch1, ch2


def read_front_panel(lcHandle):
    ''' Read front panel output source, for CH1 & CH2
        Returns
            text1, text2: str
    '''

    a_dict = {(1, 0):'CH1 Display', (1, 1):'X',
              (2, 0):'CH2 Display', (2, 1):'Y'}
    try:
        text = lcHandle.query('FPOP?1')
        code = (1, int(text.strip()))
        ch1 = a_dict[code]
    except:
        ch1 = 'N.A.'

    try:
        text = lcHandle.query('FPOP?2')
        code = (2, int(text.strip()))
        ch2 = a_dict[code]
    except:
        ch2 = 'N.A.'

    return ch1, ch2


def read_output_interface(lcHandle):
    ''' Read output interface
        Returns
            text: str
    '''

    a_dict = {0:'RS232', '1':'GPIB'}

    try:
        text = lcHandle.query('OUTX?')
        return a_dict[int(text.strip())]
    except:
        return 'N.A.'


def read_sample_rate(lcHandle):
    ''' Read the data sample rate
        Returns:
            index: int
    '''

    a_dict = {0:'per 16s', 1:'per 8s', 2:'per 4s', 3:'per 2s', 4:'1 Hz',
              5:'2 Hz', 6:'4 Hz', 7:'8 Hz', 8:'16 Hz', 9:'32 Hz', 10:'64 Hz',
              11:'128 Hz', 12:'256 Hz', 13:'512 Hz', 14:'Trigger'}
    try:
        text = lcHandle.query('SRAT?')
        return a_dict[int(text.strip())]
    except:
        return 'N.A.'
