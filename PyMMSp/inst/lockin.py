#! encoding = utf-8
from dataclasses import dataclass, fields


_WAVE_STR = ('SINE', 'SQU', 'TRI', 'RAMP')

# LOCKIN AMPLIFIER SENSTIVITY LIST
_SENS_STR = ('2 nV', '5 nV', '10 nV', '20 nV', '50 nV', '100 nV',
                   '200 nV', '500 nV', '1 μV', '2 μV', '5 μV', '10 μV',
                   '20 μV', '50 μV', '100 μV', '200 μV', '500 μV', '1 mV',
                   '2 mV', '5 mV', '10 mV', '20 mV', '50 mV', '100 mV',
                   '200 mV', '500 mV', '1 V')

# LOCKIN AMPLIFIER SENSTIVITY LIST (IN VOLTS)
_SEN_VAL = (2e-9, 5e-9, 1e-8, 2e-8, 5e-8, 1e-7, 2e-7, 5e-7,
            1e-6, 2e-6, 5e-6, 1e-5, 2e-5, 5e-5, 1e-4, 2e-4, 5e-4,
            1e-3, 2e-3, 5e-3, 1e-2, 2e-2, 5e-2, 1e-1, 2e-1, 5e-1, 1
            )

# LOCKIN AMPLIFIER TIME CONSTANT LIST
_TAU_STR = ('10 μs', '30 μs', '100 μs', '300 μs', '1 ms', '3 ms', '10 ms',
            '30 ms', '100 ms', '300 ms', '1 s', '3 s', '10 s', '30 s')

# LOCKIN AMPLIFIER TIME CONSTANT LIST (IN MILLISECONDS)
_TAU_VAL = (1e-2, 3e-2, 1e-1, 3e-1, 1, 3, 10, 30, 1e2, 3e2, 1e3, 3e3, 1e4, 3e4)

# LOCKIN COUPLE LIST
_COUPLE = ('AC', 'DC')

# LOCKIN RESERVE LIST
_RESERVE = ('High Reserve', 'Normal', 'Low Noise')

# LOCKIN REF SOURCE LIST
_REF_SRC = ('External', 'Internal')

# LOCKIN INPUT CONFIG LIST
_INPUT_CONFIG = ('A', 'B', 'I (1 MΩ)', 'I (100 MΩ)')

# LOCKIN INPUT GROUNDING LIST
_GND = ('Float', 'Ground')

# LOCKIN INPUT FILTER LIST
_FILTER = ('No filter', '1× Line notch', '2× Line notch', '1× & 2× Line notch')

# LOCKIN LP SLOPE LIST
_OCTAVE = ('6 dB/oct', '12 dB/oct', '18 dB/oct', '24 dB/oct')

# LOCKIN SAMPLE RATE LIST
_SAMPLE_RATE = ('1/16 Hz', '1/8 Hz', '1/4 Hz', '1/2 Hz', '1 Hz',
                      '2 Hz', '4 Hz', '8 Hz', '16 Hz', '32 Hz', '64 Hz',
                      '128 Hz', '256 Hz', '512 Hz', 'Trigger')

_MODU_MODE = ('NONE', 'AM', 'FM')


@dataclass
class Lockin_Info:
    inst_name: str = ''
    inst_interface: str = ''
    inst_interface_num: int = 0
    ref_src_idx: int = 0
    ref_src_txt: str = ''
    ref_freq: float = 1
    ref_phase: float = 0
    ref_harm: int = 1
    ref_harm_txt: str = '1'
    ref_harm_idx: int = 0
    config_idx: int = 1
    config_txt: str = ''
    gnd_idx: int = 1
    gnd_txt: str = ''
    couple_idx: int = 1
    couple_txt: str = ''
    input_filter_idx: int = 1
    input_filter_txt: str = ''
    sens_idx: int = 26
    sens_txt: str = ''
    sens_val: float = 1e-6
    tau_idx: int = 5
    tau_txt: str = ''
    tau_val: float = 1e-7
    reserve_idx: int = 1
    reserve_txt: str = ''
    octave_idx: int = 0
    octave_txt: str = ''
    disp1_txt: str = ''
    disp2_txt: str = ''
    front1_txt: str = ''
    front2_txt: str = ''
    sample_rate_idx: int = 0
    sample_rate_txt: str = ''

    def reset(self):
        for field in fields(self):
            setattr(self, field.name, field.default)


def init_lia(handle):
    """ Initiate the lockin with default settings.
        Returns visaCode
    """

    num, vcode = handle.write('OUTX1')      # GPIB output
    num, vcode = handle.write('FMOD0;ISRC0;ICPL1;IGND1;HARM1;DDEF1,0,0;DDEF2,1,0;FPOP1,1')

    return vcode


def reset(handle):
    """ Reset lockin to default values
        Returns visaCode
    """

    try:
        num, vcode = handle.write('*RST')
        vcode = init_lia(handle)
        return vcode
    except:
        return 'Lockin reset: IOError'


def query_inst_name(handle):
    """ Query instrument name
        Returns instrument name, str
    """

    try:
        text = handle.query('*IDN?')
        return text.strip()
    except:
        return 'N.A.'


def query_err_msg(handle):


    try:
        text = handle.query('ERRS?')
    except:
        return 'N.A.'


def read_freq(handle):
    """ Read current lockin frequency.
        Returns frequency in Hz (float)
    """

    try:
        text = handle.query('FREQ?')
        return float(text.strip())
    except:
        return 0


def read_harm(handle):
    """ Read current lockin harmonics.
        Returns harmonics: int
    """

    try:
        text = handle.query('HARM?')
        return int(text.strip())
    except:
        return 0


def set_harm(handle, harm):
    """ Set the lockin harmonics to idx.
        Arguments
            handle: pyvisa.resources.Resource, Lockin handle
            harm: int
        Returns visaCode
    """

    try:
        num, vcode = handle.write('HARM{:d}'.format(harm))
        return vcode
    except:
        return 'Lockin set harmonics: IOError'


def read_phase(handle):
    """ Read current lockin phase.
        Returns phase: float
    """

    try:
        text = handle.query('PHAS?')
        return float(text.strip())
    except:
        return 0


def set_phase(handle, phase):
    """ Set the lockin phase to phase_text.
        Arguments
            handle: pyvisa.resources.Resource, Lockin handle
            phase: float
        Returns visaCode
    """

    try:
        num, vcode = handle.write('PHAS{:.2f}'.format(phase))
        return vcode
    except:
        return 'Lockin set phase: IOError'


def auto_phase(handle):
    """ Autophase in lockin.
        Returns visaCode
    """

    try:
        num, vcode = handle.write('APHS')
        return vcode
    except:
        return 'Lockin auto phase: IOError'


def auto_gain(handle):
    """ Autogain in lockin.
        Returns visaCode
    """

    try:
        num, vcode = handle.write('AGAN')
        return vcode
    except:
        return 'Lockin auto gain: IOError'


def read_sens(handle):
    """ Read current lockin sensitivity.
        Returns index number (int)
    """

    try:
        text = handle.query('SENS?')
        index = int(text.strip())
    except:
        index = 0

    return index


def set_sens(handle, sens_index):
    """ Set the lockin sensitivity.
        Arguments
            handle: pyvisa.resources.Resource, Lockin handle
            sens_index: int, user input.
                        The index directly map to the lockin command
        Returns visaCode
    """

    try:
        num, vcode = handle.write('SENS{:d}'.format(sens_index))
        return vcode
    except:
        return 'Lockin set sensitivity: IOError'


def read_tc(handle):
    """ Read current lockin sensitivity.
        Returns index number (int)
    """

    try:
        text = handle.query('OFLT?')
        index = int(text.strip())
    except:
        index = 0

    return index


def set_tc(handle, tc_index):
    """ Set the lockin time constant.
        Arguments
            handle: pyvisa.resources.Resource, Lockin handle
            tc_index: int, user input.
                      The index directly maps to the lockin command
        Returns visaCode
    """

    try:
        num, vcode = handle.write('OFLT{:d}'.format(tc_index))
        return vcode
    except:
        return 'Lockin set time constant: IOError'


def read_couple(handle):
    """ Read current lockin couple.
        Returns couple index number (int)
    """

    try:
        text = handle.query('ICPL?')
        return int(text.strip())
    except:
        return 0


def set_couple(handle, couple_index):
    """ Set the lockin couple.
        Arguments
            handle: pyvisa.resources.Resource, Lockin handle
            couple_index: int, user input.
                          The index directly maps to the lockin command
        Returns visaCode
    """

    try:
        num, vcode = handle.write('ICPL{:d}'.format(couple_index))
        return vcode
    except:
        return 'Lockin set couple: IOError'


def read_reserve(handle):
    """ Read current lockin reserve.
        Returns reserve index (int)
    """

    try:
        text = handle.query('RMOD?')
        return int(text.strip())
    except:
        return 1    # default is normal


def set_reserve(handle, reserve_index):
    """ Set the lockin reserve.
        Returns visaCode
    """

    try:
        num, vcode = handle.write('RMOD{:d}'.format(reserve_index))
        return vcode
    except:
        return 'Lockin set reserve: IOError'


def query_single_x(handle):
    """ Query single x reading from lockin.
        Returns x (float)
    """

    try:
        x = handle.query('OUTP?1')
        return x
    except:
        return 0


def read_ref_source(handle):
    """ Read reference source
        Returns
            reference source index (int)
    """

    try:
        text = handle.query('FMOD?')
        return int(text.strip())
    except:
        return 0


def read_input_config(handle):
    """ Read input configuration
        Returns
            input config index (int)
    """

    try:
        text = handle.query('ISRC?')
        return int(text.strip())
    except:
        return 0


def read_input_grounding(handle):
    """ Read input grounding
        Returns grounding index (int)
    """

    try:
        text = handle.query('IGND?')
        return int(text.strip())
    except:
        return 1    # default is gound


def set_input_grounding(handle, gnd_index):
    """ Set input grounding
        Returns visaCode
    """

    try:
        num, vcode = handle.write('IGND{:d}'.format(gnd_index))
        return vcode
    except:
        return 'Lockin set input grounding: IOError'


def read_input_filter(handle):
    """ Read input notch filter
        Returns
            filter index: int
    """

    try:
        text = handle.query('ILIN?')
        return int(text.strip())
    except:
        return 0


def set_input_filter(handle, filter_index):
    """ Set input notch filter
        Returns visaCode
    """

    try:
        num, vcode = handle.write('ILIN{:d}'.format(filter_index))
        return vcode
    except:
        return 'Lockin set input filter: IOError'


def read_lp_slope(handle):
    """ Read low pass filter slope
        Returns
            lp slope index: int
    """

    try:
        text = handle.query('OFSL?')
        return int(text.strip())
    except:
        return 0


def read_disp(handle):
    """ Read display parameter
        Returns
            text1, text2: str, for CH1 & CH2
    """

    a_dict = {0:'X', 1:'R', 2:'X Noise', 3:'Aux In 1', 4:'Aux In 2'}
    b_dict = {0:'Y', 1:'θ', 2:'Y Noise', 3:'Aux In 3', 4:'Aux In 4'}

    try:
        text = handle.query('DDEF?1')
        j, k = text.strip().split(',')
        ch1 = a_dict[int(j)]
        if k:
            ch1 += '; Ratio {:s}'.format(a_dict[int(k) + 2])
        else:
            pass
    except:
        ch1 = 'N.A.'

    try:
        text = handle.query('DDEF?2')
        j, k = text.strip().split(',')
        ch2 = b_dict[int(j)]
        if k:
            ch2 += '; Ratio {:s}'.format(a_dict[int(k) + 2])
        else:
            pass
    except:
        ch2 = 'N.A.'

    return ch1, ch2


def read_front_panel(handle):
    """ Read front panel output source, for CH1 & CH2
        Returns
            text1, text2: str
    """

    a_dict = {(1, 0):'CH1 Display', (1, 1):'X',
              (2, 0):'CH2 Display', (2, 1):'Y'}
    try:
        text = handle.query('FPOP?1')
        code = (1, int(text.strip()))
        ch1 = a_dict[code]
    except:
        ch1 = 'N.A.'

    try:
        text = handle.query('FPOP?2')
        code = (2, int(text.strip()))
        ch2 = a_dict[code]
    except:
        ch2 = 'N.A.'

    return ch1, ch2


def read_output_interface(handle):
    """ Read output interface
        Returns
            text: str
    """

    a_dict = {0:'RS232', '1':'GPIB'}

    try:
        text = handle.query('OUTX?')
        return a_dict[int(text.strip())]
    except:
        return 'N.A.'


def read_sample_rate(handle):
    """ Read the data sample rate
        Returns:
            index: int
    """

    try:
        text = handle.query('SRAT?')
        return int(text.strip())
    except:
        return 0


def full_info_query_(info, handle):
    """ Query all information
    Overwrite properties of the 'info' object
    """

    if handle:
        info.inst_name = handle.resource_name
        info.inst_interface = str(handle.interface_type)
        info.inst_interface_num = handle.interface_number
        info.ref_src_idx = read_ref_source(handle)
        info.ref_src_txt = _REF_SRC[info.ref_src_idx]
        info.ref_freq = read_freq(handle)
        info.ref_phase = read_phase(handle)
        info.ref_harm = read_harm(handle)
        info.ref_harm_txt = str(info.ref_harm)
        info.ref_harm_idx = info.ref_harm - 1
        info.config_idx = read_input_config(handle)
        info.config_txt = _INPUT_CONFIG[info.config_idx]
        info.gnd_idx = read_input_grounding(handle)
        info.gnd_txt = _GND[info.gnd_idx]
        info.couple_idx = read_couple(handle)
        info.couple_txt = _COUPLE[info.couple_idx]
        info.input_filter_idx = read_input_filter(handle)
        info.input_filter_txt = _FILTER[info.input_filter_idx]
        info.sens_idx = read_sens(handle)
        info.sens_txt = _SENS_STR[info.sens_idx]
        info.sens_val = _SEN_VAL[info.sens_idx]
        info.tau_idx = read_tc(handle)
        info.tau_txt = _TAU_STR[info.tau_idx]
        info.tau_val = _TAU_VAL[info.tau_idx]
        info.reserve_idx = read_reserve(handle)
        info.reserve_txt = _RESERVE[info.reserve_idx]
        info.octave_idx = read_lp_slope(handle)
        info.octave_txt = _OCTAVE[info.octave_idx]
        info.disp1_txt, info.disp2_txt = read_disp(handle)
        info.front1_txt, info.front2_txt = read_front_panel(handle)
        info.sample_rate_idx = read_sample_rate(handle)
        info.sample_rate_txt = _SAMPLE_RATE[info.sample_rate_idx]
    else:
        info.reset()
        info.inst_name = 'No Instrument'
