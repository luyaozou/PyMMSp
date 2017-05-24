#! encoding = utf-8

import numpy as np

# LOCKIN AMPLIFIER SENSTIVITY LIST
SENS_LIST = ['2 nV', '5 nV', '10 nV', '20 nV', '50 nV', '100 nV',
             '200 nV', '500 nV', '1 uV', '2 uV', '5 uV', '10 uV',
             '20 uV', '50 uV', '100 uV', '200 uV', '500 uV', '1 mV',
             '2 mV', '5 mV', '10 mV', '20 mV', '50 mV', '100 mV',
             '200 mV', '500 mV', '1 V'
             ]

# LOCKIN AMPLIFIER TIME CONSTANT LIST
TC_LIST = ['10 us', '30 us', '100 us', '300 us', '1 ms', '3 ms', '10 ms',
           '30 ms', '100 ms', '300 ms', '1 s', '3 s', '10 s', '30 s'
           ]

# LOCKIN COUPLE LIST
COUPLE_LIST = ['AC', 'DC']

# LOCKIN RESERVE LIST
RESERVE_LIST = ['High Reserve', 'Normal', 'Low Noise']

# LOCKIN REF SOURCE LIST
REF_SRC_LIST = ['External', 'Internal']

# LOCKIN INPUT CONFIG LIST
INPUT_CONFIG_LIST = ['A', 'B', 'I (1 MΩ)', 'I (100 MΩ)']

# LOCKIN INPUT GROUNDING LIST
INPUT_GND_LIST = ['Float', 'Ground']

# LOCKIN INPUT FILTER LIST
INPUT_FILTER_LIST = ['No filter', '1× Line notch',
                     '2× Line notch', '1× & 2× Line notch']

# LOCKIN LP SLOPE LIST
LPSLOPE_LIST = ['6 dB/oct', '12 dB/oct', '18 dB/oct', '24 dB/oct']

# LOCKIN SAMPLE RATE LIST
SAMPLE_RATE_LIST = ['1/16 Hz', '1/8 Hz', '1/4 Hz', '1/2 Hz', '1 Hz',
                    '2 Hz', '4 Hz', '8 Hz', '16 Hz', '32 Hz', '64 Hz',
                    '128 Hz', '256 Hz', '512 Hz', 'Trigger']


def init_lia(liaHandle):
    ''' Initiate the lockin with default settings.
        Returns visaCode
    '''

    num, vcode = liaHandle.write('OUTX1')      # GPIB output
    num, vcode = liaHandle.write('FMOD0;ISRC0;ICPL1;IGND1;HARM1;DDEF1,0,0;DDEF2,1,0;FPOP1,1')

    return vcode


def reset(liaHandle):
    ''' Reset lockin to default values
        Returns visaCode
    '''

    try:
        num, vcode = liaHandle.write('*RST')
        vcode = init_lia(liaHandle)
        return vcode
    except:
        return 'Lockin reset: IOError'


def query_inst_name(liaHandle):
    ''' Query instrument name
        Returns instrument name, str
    '''

    try:
        text = liaHandle.query('*IDN?')
        return text.strip()
    except:
        return 'N.A.'


def query_err_msg(liaHandle):


    try:
        text = liaHandle.query('ERRS?')
    except:
        return 'N.A.'


def read_freq(liaHandle):
    ''' Read current lockin frequency.
        Returns frequency in Hz (float)
    '''

    try:
        text = liaHandle.query('FREQ?')
        return float(text.strip())
    except:
        return 0


def read_harm(liaHandle):
    ''' Read current lockin harmonics.
        Returns harmonics: int
    '''

    try:
        text = liaHandle.query('HARM?')
        return int(text.strip())
    except:
        return 0


def set_harm(liaHandle, harm):
    ''' Set the lockin harmonics to idx.
        Arguments
            liaHandle: pyvisa.resources.Resource, Lockin handle
            harm: int
        Returns visaCode
    '''

    try:
        num, vcode = liaHandle.write('HARM{:d}'.format(harm))
        return vcode
    except:
        return 'Lockin set harmonics: IOError'


def read_phase(liaHandle):
    ''' Read current lockin phase.
        Returns phase: float
    '''

    try:
        text = liaHandle.query('PHAS?')
        return float(text.strip())
    except:
        return 0


def set_phase(liaHandle, phase):
    ''' Set the lockin phase to phase_text.
        Arguments
            liaHandle: pyvisa.resources.Resource, Lockin handle
            phase: float
        Returns visaCode
    '''

    try:
        num, vcode = liaHandle.write('PHAS{:.2f}'.format(phase))
        return vcode
    except:
        return 'Lockin set phase: IOError'


def auto_phase(liaHandle):
    ''' Autophase in lockin.
        Returns visaCode
    '''

    try:
        num, vcode = liaHandle.write('APHS')
        return vcode
    except:
        return 'Lockin auto phase: IOError'


def auto_gain(liaHandle):
    ''' Autogain in lockin.
        Returns visaCode
    '''

    try:
        num, vcode = liaHandle.write('AGAN')
        return vcode
    except:
        return 'Lockin auto gain: IOError'


def read_sens(liaHandle):
    ''' Read current lockin sensitivity.
        Returns index number (int)
    '''

    try:
        text = liaHandle.query('SENS?')
        index = int(text.strip())
    except:
        index = 0

    return index


def set_sens(liaHandle, sens_index):
    ''' Set the lockin sensitivity.
        Arguments
            liaHandle: pyvisa.resources.Resource, Lockin handle
            sens_index: int, user input.
                        The index directly map to the lockin command
        Returns visaCode
    '''

    try:
        num, vcode = liaHandle.write('SENS{:d}'.format(sens_index))
        return vcode
    except:
        return 'Lockin set sensitivity: IOError'


def read_tc(liaHandle):
    ''' Read current lockin sensitivity.
        Returns index number (int)
    '''

    try:
        text = liaHandle.query('OFLT?')
        index = int(text.strip())
    except:
        index = 0

    return index


def set_tc(liaHandle, tc_index):
    ''' Set the lockin time constant.
        Arguments
            liaHandle: pyvisa.resources.Resource, Lockin handle
            tc_index: int, user input.
                      The index directly maps to the lockin command
        Returns visaCode
    '''

    try:
        num, vcode = liaHandle.write('OFLT{:d}'.format(tc_index))
        return vcode
    except:
        return 'Lockin set time constant: IOError'


def read_couple(liaHandle):
    ''' Read current lockin couple.
        Returns couple index number (int)
    '''

    try:
        text = liaHandle.query('ICPL?')
        return int(text.strip())
    except:
        return 0


def set_couple(liaHandle, couple_index):
    ''' Set the lockin couple.
        Arguments
            liaHandle: pyvisa.resources.Resource, Lockin handle
            couple_index: int, user input.
                          The index directly maps to the lockin command
        Returns visaCode
    '''

    try:
        num, vcode = liaHandle.write('ICPL{:d}'.format(couple_index))
        return vcode
    except:
        return 'Lockin set couple: IOError'


def read_reserve(liaHandle):
    ''' Read current lockin reserve.
        Returns reserve index (int)
    '''

    try:
        text = liaHandle.query('RMOD?')
        return int(text.strip())
    except:
        return 1    # default is normal


def set_reserve(liaHandle, reserve_index):
    ''' Set the lockin reserve.
        Returns visaCode
    '''

    try:
        num, vcode = liaHandle.write('RMOD{:d}'.format(reserve_index))
        return vcode
    except:
        return 'Lockin set reserve: IOError'


def query_single_x(liaHandle):
    ''' Query single x reading from lockin.
        Returns x (float)
    '''

    try:
        x = liaHandle.query('OUTP?1')
        return x
    except:
        return 0


def read_ref_source(liaHandle):
    ''' Read reference source
        Returns
            reference source index (int)
    '''

    try:
        text = liaHandle.query('FMOD?')
        return int(text.strip())
    except:
        return 0


def read_input_config(liaHandle):
    ''' Read input configuration
        Returns
            input config index (int)
    '''

    try:
        text = liaHandle.query('ISRC?')
        return int(text.strip())
    except:
        return 0


def read_input_grounding(liaHandle):
    ''' Read input grounding
        Returns grounding index (int)
    '''

    try:
        text = liaHandle.query('IGND?')
        return int(text.strip())
    except:
        return 1    # default is gound


def set_input_grounding(liaHandle, gnd_index):
    ''' Set input grounding
        Returns visaCode
    '''

    try:
        num, vcode = liaHandle.write('IGND{:d}'.format(gnd_index))
        return vcode
    except:
        return 'Lockin set input grounding: IOError'


def read_input_filter(liaHandle):
    ''' Read input notch filter
        Returns
            filter index: int
    '''

    try:
        text = liaHandle.query('ILIN?')
        return int(text.strip())
    except:
        return 0


def set_input_filter(liaHandle, filter_index):
    ''' Set input notch filter
        Returns visaCode
    '''

    try:
        num, vcode = liaHandle.write('ILIN{:d}'.format(filter_index))
        return vcode
    except:
        return 'Lockin set input filter: IOError'


def read_lp_slope(liaHandle):
    ''' Read low pass filter slope
        Returns
            lp slope index: int
    '''

    try:
        text = liaHandle.query('OFSL?')
        return int(text.strip())
    except:
        return 0


def read_disp(liaHandle):
    ''' Read display parameter
        Returns
            text1, text2: str, for CH1 & CH2
    '''

    a_dict = {0:'X', 1:'R', 2:'X Noise', 3:'Aux In 1', 4:'Aux In 2'}
    b_dict = {0:'Y', 1:'θ', 2:'Y Noise', 3:'Aux In 3', 4:'Aux In 4'}

    try:
        text = liaHandle.query('DDEF?1')
        j, k = text.strip().split(',')
        ch1 = a_dict[int(j)]
        if k:
            ch1 += '; Ratio {:s}'.format(a_dict[int(k) + 2])
        else:
            pass
    except:
        ch1 = 'N.A.'

    try:
        text = liaHandle.query('DDEF?2')
        j, k = text.strip().split(',')
        ch2 = b_dict[int(j)]
        if k:
            ch2 += '; Ratio {:s}'.format(a_dict[int(k) + 2])
        else:
            pass
    except:
        ch2 = 'N.A.'

    return ch1, ch2


def read_front_panel(liaHandle):
    ''' Read front panel output source, for CH1 & CH2
        Returns
            text1, text2: str
    '''

    a_dict = {(1, 0):'CH1 Display', (1, 1):'X',
              (2, 0):'CH2 Display', (2, 1):'Y'}
    try:
        text = liaHandle.query('FPOP?1')
        code = (1, int(text.strip()))
        ch1 = a_dict[code]
    except:
        ch1 = 'N.A.'

    try:
        text = liaHandle.query('FPOP?2')
        code = (2, int(text.strip()))
        ch2 = a_dict[code]
    except:
        ch2 = 'N.A.'

    return ch1, ch2


def read_output_interface(liaHandle):
    ''' Read output interface
        Returns
            text: str
    '''

    a_dict = {0:'RS232', '1':'GPIB'}

    try:
        text = liaHandle.query('OUTX?')
        return a_dict[int(text.strip())]
    except:
        return 'N.A.'


def read_sample_rate(liaHandle):
    ''' Read the data sample rate
        Returns:
            index: int
    '''

    try:
        text = liaHandle.query('SRAT?')
        return int(text.strip())
    except:
        return 0
