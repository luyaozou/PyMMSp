#! encoding = utf-8
from dataclasses import dataclass, fields
from abc import ABC
import json

SYN_MODELS = (
    'Rohde & Schwarz SMF100A',
)

# VDI band information.
# Keys are the indices used in VDIBandComboBox,
# and values are the names, multiplication factors, and recommended frequency ranges.
_VDI_BAND_NAME = {0: '1',
                  1: '2',
                  2: '3',
                  3: '4',
                  4: '5',
                  5: '6',
                  6: '7',
                  7: '8a',
                  8: '8b',
                  9: '9'}
VDI_BAND_NAME = tuple(_VDI_BAND_NAME.values())

_VDI_BAND_MULTI = {0: 1,
                   1: 2,
                   2: 3,
                   3: 3,
                   4: 6,
                   5: 9,
                   6: 12,
                   7: 18,
                   8: 27,
                   9: 27}
VDI_BAND_MULTI = tuple(_VDI_BAND_MULTI.values())

_VDI_BAND_RANGE = {0: (20, 50),  # !!! in the unit of GHz !!!
                   1: (50, 75),
                   2: (70, 115),
                   3: (90, 140),
                   4: (140, 225),
                   5: (220, 330),
                   6: (270, 460),
                   7: (430, 700),
                   8: (650, 800),
                   9: (700, 1000)}
VDI_BAND_RANGE = tuple(_VDI_BAND_RANGE.values())

MODU_MODE = ('NONE', 'AM', 'FM')


def yield_band_str():
    """ Yield band information string """

    for key in _VDI_BAND_NAME:
        txt = 'Band {:s} (x{:d}): {:d}-{:d} GHz'.format(
            _VDI_BAND_NAME[key], _VDI_BAND_MULTI[key], *_VDI_BAND_RANGE[key])
        yield txt


@dataclass
class Syn_Info:
    """ Synthesizer information """

    inst_name: str = ''
    inst_interface: str = ''
    inst_interface_num: int = 0
    inst_remote_disp: bool = False
    conn_status: bool = False  # connection status
    rf_toggle: bool = False
    syn_power: float = -20.
    syn_freq: float = 3e10  # Hz
    band_idx: int = 4
    freq: float = 12e10  # Hz
    modu_toggle: bool = False
    modu_mode_idx: int = 0
    modu_freq: float = 0  # update according to modMode
    modu_amp: float = 0  # update according to modMode
    am1_toggle: bool = False
    am1_freq: float = 0  # Hz
    am1_depth_pct: float = 1.  # float, percent
    am1_depth_db: float = -20.  # db
    am1_src: str = ''
    am1_wave: str = 'SINE'  # ['SINE', 'SQU', 'TRI', 'RAMP']
    am2_toggle: bool = False
    am2_freq: float = 0  # Hz
    am2_depth_pct: float = 1.  # float, percent
    am2_depth_db: float = -20.  # db
    am2_src: str = ''
    am2_wave: str = 'SINE'  # ['SINE', 'SQU', 'TRI', 'RAMP']
    fm1_toggle: bool = False
    fm1_freq: float = 0.  # Hz
    fm1_dev: float = 0  # Hz
    fm1_src: str = ''
    fm1_wave: str = 'SINE'  # ['SINE', 'SQU', 'TRI', 'RAMP']
    fm2_toggle: bool = False
    fm2_freq: float = 0.  # Hz
    fm2_dev: float = 0  # Hz
    fm2_src: str = ''
    fm2_wave: str = 'SINE'  # ['SINE', 'SQU', 'TRI', 'RAMP']
    pm1_toggle: bool = False
    pm1_freq: float = 0.  # Hz
    pm1_dev: float = 0  # Hz
    pm1_src: str = ''
    pm1_wave: str = 'SINE'  # ['SINE', 'SQU', 'TRI', 'RAMP']
    pm2_toggle: bool = False
    pm2_freq: float = 0.  # Hz
    pm2_dev: float = 0  # Hz
    pm2_src: str = ''
    pm2_wave: str = 'SINE'  # ['SINE', 'SQU', 'TRI', 'RAMP']
    lf_toggle: bool = False
    lf_vol: float = 0.
    lf_src: str = ''
    err_msg: str = ''

    def reset(self):
        for field in fields(self):
            setattr(self, field.name, field.default)

    @property
    def band_multi(self):
        return _VDI_BAND_MULTI[self.band_idx]

    @property
    def modu_mode_txt(self):
        return MODU_MODE[self.modu_mode_idx]


def get_syn_info(handle, info):
    """ Get synthesizer information """
    pass


class _SynAPI(ABC):
    """ Base API with method stubs in order to enable IDE features
    Contains all functions need to be defined in the API_MAP file

    Get functions always returns a tuple (bool, value) where first element is the status of the query
    Set functions always returns a boolean value indicating the success of the operation
    """

    def get_inst_name(self, handle) -> (bool, str):
        pass

    def init_syn(self, handle) -> None:
        pass

    def get_power_stat(self, handle) -> (bool, bool):
        pass

    def set_power_stat(self, handle, stat: bool) -> bool:
        pass

    def get_power_level(self, handle) -> (bool, float):
        pass

    def set_power_level(self, handle, power: float) -> bool:
        pass

    def get_cw_freq(self, handle) -> (bool, float):
        pass

    def set_cw_freq(self, handle, freq: float, unit: str) -> bool:
        pass

    def get_modu_stat(self, handle) -> (bool, bool):
        pass

    def set_modu_stat(self, handle, stat: bool) -> bool:
        pass

    def get_am_stat(self, handle, chan: int) -> (bool, bool):
        pass

    def set_am_stat(self, handle, chan: int, stat: bool) -> bool:
        pass

    def get_am_source(self, handle, chan: int) -> (bool, str):
        pass

    def set_am_source(self, handle, chan: int, source: str) -> bool:
        pass

    def get_am_waveform(self, handle, chan: int) -> (bool, str):
        pass

    def set_am_waveform(self, handle, chan: int, wave: str) -> bool:
        pass

    def get_am_freq(self, handle, chan: int) -> (bool, float):
        pass

    def set_am_freq(self, handle, chan: int, freq: float, unit: str) -> bool:
        pass

    def get_am_depth(self, handle, chan: int) -> (bool, float):
        pass

    def get_am_depth_db(self, handle, chan: int) -> (bool, float):
        pass

    def set_am_depth(self, handle, chan: int, depth: float) -> bool:
        pass

    def get_fm_stat(self, handle, chan: int) -> (bool, bool):
        pass

    def set_fm_stat(self, handle, chan: int, stat: bool) -> bool:
        pass

    def get_fm_freq(self, handle, chan: int) -> (bool, float):
        pass

    def set_fm_freq(self, handle, chan: int, freq: float, unit: str) -> bool:
        pass

    def get_fm_dev(self, handle, chan: int) -> (bool, float):
        pass

    def set_fm_dev(self, handle, chan: int, dev: float, unit: str) -> bool:
        pass

    def get_fm_waveform(self, handle, chan: int) -> (bool, str):
        pass

    def set_fm_waveform(self, handle, chan: int, wave: str) -> bool:
        pass

    def get_pm_stat(self, handle, chan: int) -> (bool, bool):
        pass

    def set_pm_stat(self, handle, chan: int, stat: bool) -> bool:
        pass

    def get_pm_freq(self, handle, chan: int) -> (bool, float):
        pass

    def set_pm_freq(self, handle, chan: int, freq: float, unit: str) -> bool:
        pass

    def get_pm_dev(self, handle, chan: int) -> (bool, float):
        pass

    def set_pm_dev(self, handle, chan: int, dev: float, unit: str) -> bool:
        pass

    def get_pm_waveform(self, handle, chan: int) -> (bool, str):
        pass

    def set_pm_waveform(self, handle, chan: int, wave: str) -> bool:
        pass

    def get_lfo_stat(self, handle) -> (bool, bool):
        pass

    def set_lfo_stat(self, handle, stat: bool) -> bool:
        pass

    def get_lfo_source(self, handle) -> (bool, float):
        pass

    def get_lfo_ampl(self, handle) -> (bool, float):
        pass

    def set_lfo_ampl(self, handle, ampl: float) -> bool:
        pass

    def get_err(self, handle) -> (bool, str):
        pass

    def get_remote_disp_stat(self, handle) -> (bool, bool):
        pass


class DynamicSynAPI(_SynAPI):
    """ Dynamic API loading API_MAP file to create real functions """

    def __init__(self, api_map_file):
        functions = create_functions(api_map_file)
        for name, func in functions.items():
            setattr(self, name, func)


def create_functions(api_map_file):
    """ Create functions from the API_MAP file """
    with open(api_map_file, 'r') as f:
        api_map = json.load(f)
    functions = {}
    for item in api_map['functions']:
        name = item['name']
        args = item['args']
        kwargs = item['kwargs']
        cmd = item['cmd']
        if name.startswith('set_'):
            def func(handle, *args, cmd=cmd, **kwargs):
                code = cmd.format(*args, **kwargs)
                stat = handle.send(code)
                return stat
        elif name.startswith('get_'):
            def func(handle, *args, cmd=cmd, **kwargs):
                code = cmd.format(*args, **kwargs)
                stat, value = handle.query(code)
                return stat, value
        else:
            def func(handle, *args, **kwargs):
                pass
        functions[name] = func
    return functions


def ramp_up(start, stop):
    """ A integer list generator. start < stop """

    n = start
    while n < stop:
        n = n + 1
        yield n


def ramp_down(start, stop):
    """ A integer list generator. start > stop """

    n = start
    while n > stop:
        n = n - 1
        yield n


def init_syn(handle):
    """ Initialize synthesizer.
        Returns visaCode
    """

    try:
        num, vcode = handle.write(':AM1:SOUR INT1; :AM1:STAT 0; :FM1:SOUR INT1; :FM1:STAT 0; :OUTP:MOD 0; '
                                  ':LFO:SOUR INT1; :LFO:AMPL 0VP; :POW:MODE FIX; :FREQ:MODE CW; :DISP:REM 0')
        return vcode
    except:
        return 'Synthesizer initialization: IOError'


def query_inst_name(handle):
    """ Query instrument name
        Returns instrument name, str
    """

    try:
        text = handle.query('*IDN?')
        return text.strip()
    except:
        return 'N.A.'


def read_power_toggle(handle):
    """ Read current synthesizer power output.
        Returns status (bool)
    """

    try:
        text = handle.query(':OUTP?')
        status = bool(int(text.strip()))
        return status
    except:
        return False


def set_power_toggle(handle, toggle_state):
    """ Turn RF power on/off.
        Returns visaCode
    """

    try:
        if toggle_state:  # user want to turn on RF
            num, vcode = handle.write(':OUTP 1')
        else:  # user want to turn off RF
            num, vcode = handle.write(':OUTP 0')
        return vcode
    except:
        return 'Synthesizer set RF power toggle: IOError'


def read_syn_power(handle):
    """ Read current synthesizer power.
        Returns current_power, float (dbm)
    """

    try:
        text = handle.query(':POW?')
        return float(text.strip())
    except:
        return -20


def set_syn_power(handle, set_power):
    """ Set synthesizer power.
        Returns visaCode
    """

    # the ultimate protection
    if set_power > 0:
        set_power = 0
    elif (set_power > -20) and (not read_power_toggle(handle)):
        return 'Error: RF not on'
    else:
        pass

    try:
        num, vcode = handle.write(':POW {:g}DBM'.format(set_power))
        return vcode
    except:
        return 'Synthesizer set RF power: IOError'


def read_syn_freq(handle):
    """ Read current synthesizer frequecy.
        Returns current_freq, float (Hz)
    """

    try:
        text = handle.query(':FREQ:CW?')
        current_freq = float(text.strip())
        return current_freq
    except:
        return 0


def set_syn_freq(handle, freq):
    """ Set the synthesizer frequency to freq.
        Arguments
            handle: pyvisa.resources.Resource, synthesizer handle
            freq: float (MHz)
        Returns visaCode
    """

    try:
        num, vcode = handle.write(':FREQ:CW {:.3f}HZ'.format(freq))
        return vcode
    except:
        return 'Synthesizer set syn freq: IOError'


def set_mod_mode(handle, mod_index):
    """ Set synthesizer modulation mode.
        Arguments: mod_index, int
            0: no modulation
            1: AM
            2: FM
        Returns visaCode
    """

    a_dict = {0: ':AM1:STAT 0; :FM1:STAT 0',
              1: ':FM1:STAT 0; :AM1:STAT 1',
              2: ':AM1:STAT 0; :FM1:STAT 1'}

    try:
        num, vcode = handle.write(a_dict[mod_index])
        return vcode
    except:
        return 'Synthesizer set modulation mode: IOError'


def read_mod_toggle(handle):
    """ Read current modulation toggle status.
        Returns toggle status (bool)
    """

    try:
        text = handle.query(':OUTP:MOD?')
        return bool(int(text.strip()))
    except:
        return False


def set_mod_toggle(handle, toggle_state):
    """ Turn on/off modulation.
        Arguments
            toggle_state: boolean
        Returns visaCode
    """

    try:
        num, vcode = handle.write(':OUTP:MOD {:d}'.format(toggle_state))
        return vcode
    except:
        return 'Synthesizer set modulation toggle: IOError'


def read_am_par(handle):
    """ Read current amplitude modulation setting.
        Returns
            freq:  mod freq, float (Hz)
            depth: mod depth, float (percent)
            status: on/off, bool
    """

    try:
        text = handle.query(':AM1:INT1:FREQ?')
        freq = float(text.strip())
        text = handle.query(':AM1:DEPT?')
        depth = float(text.strip()) * 1e2
        text = handle.query(':AM1:STAT?')
        status = bool(int(text.strip()))
        return freq, depth, status
    except:
        return 0, 0, False


def read_am_source(handle, channel):
    """ Read synthesizer AM source for channel (1 or 2)
        Arguments
            handle: pyvisa.resources.Resource
            channel: int
        Returns text: str
    """

    try:
        text = handle.query(':AM{:d}:SOUR?'.format(channel))
        return text.strip()
    except:
        return 'N.A.'


def read_am_state(handle, channel):
    """ Read synthesizer AM state for channel (1 or 2)
        Arguments
            handle: pyvisa.resources.Resource
            channel: int
        Returns status: boolean
    """

    try:
        text = handle.query(':AM{:d}:STAT?'.format(channel))
        return bool(int(text.strip()))
    except:
        return False


def read_am_depth(handle, channel):
    """ Read synthesizer AM depth for channel (1 or 2)
        Arguments
            handle: pyvisa.resources.Resource
            channel: int
        Returns
            depth_linear: float, depth in percent
            depth_exp: float, depth in dB
    """

    try:
        text = handle.query(':AM{:d}:DEPT?'.format(channel))
        depth_linear = float(text.strip())
        text = handle.query(':AM{:d}:DEPT:EXP?'.format(channel))
        depth_exp = float(text.strip())
        return depth_linear, depth_exp
    except:
        return 0, 0


def read_am_freq(handle, channel):
    """ Read synthesizer AM freq for channel (1 or 2)
        Arguments
            handle: pyvisa.resources.Resource
            channel: int
        Returns freq: float
    """

    try:
        text = handle.query(':AM{:d}:INT{:d}:FREQ?'.format(channel, channel))
        return float(text.strip())
    except:
        return 0


def read_am_waveform(handle, channel):
    """ Read synthesizer AM freq for channel (1 or 2)
        Arguments
            handle: pyvisa.resources.Resource
            channel: int
        Returns text: str
    """

    try:
        text = handle.query(':AM{:d}:INT{:d}:FUNC:SHAP?'.format(channel, channel))
        return text.strip()
    except:
        return 'N.A.'


def set_am(handle, freq, depth, toggle_state):
    """ Set synthesizer AM to freq and depth.
        Arguments
            freq: float (Hz)
            depth: float (percent)
            toggle_state: boolean
        Returns visaCode
    """

    try:
        # set up AM freq and depth
        set_mod_toggle(handle, toggle_state)
        num, vcode = handle.write(':AM1:INT1:FREQ {:.9f}HZ; :AM1 {:.1f}'.format(freq, depth))
    except:
        vcode = 'Synthesizer set AM: IOError'

    return vcode


def read_fm_par(handle):
    """ Read current frequency modulation setting.
        Returns
            freq:  mod freq, float (Hz)
            depth: mod depth, float (Hz)
            status: on/off, bool
    """

    try:
        text = handle.query(':FM1:INT1:FREQ?')
        freq = float(text.strip())
        text = handle.query(':FM1:DEV?')
        depth = float(text.strip())
        text = handle.query(':FM1:STAT?')
        status = bool(int(text.strip()))
        return freq, depth, status
    except:
        return 0, 0, False


def read_fm_source(handle, channel):
    """ Read synthesizer FM source for channel (1 or 2)
        Arguments
            handle: pyvisa.resources.Resource
            channel: int
        Returns text: str
    """

    try:
        text = handle.query(':FM{:d}:SOUR?'.format(channel))
        return text.strip()
    except:
        return 'N.A.'


def read_fm_state(handle, channel):
    """ Read synthesizer FM state for channel (1 or 2)
        Arguments
            handle: pyvisa.resources.Resource
            channel: int
        Returns status: boolean
    """

    try:
        text = handle.query(':FM{:d}:STAT?'.format(channel))
        return bool(int(text.strip()))
    except:
        return False


def read_fm_dev(handle, channel):
    """ Read synthesizer FM depth for channel (1 or 2)
        Arguments
            handle: pyvisa.resources.Resource
            channel: int
        Returns dev: float
    """

    try:
        text = handle.query(':FM{:d}:DEV?'.format(channel))
        return float(text.strip())
    except:
        return 0


def read_fm_freq(handle, channel):
    """ Read synthesizer FM freq for channel (1 or 2)
        Arguments
            handle: pyvisa.resources.Resource
            channel: int
        Returns freq: float
    """

    try:
        text = handle.query(':FM{:d}:INT{:d}:FREQ?'.format(channel, channel))
        return float(text.strip())
    except:
        return 0


def read_fm_waveform(handle, channel):
    """ Read synthesizer FM freq for channel (1 or 2)
        Arguments
            handle: pyvisa.resources.Resource
            channel: int
        Returns text: str
    """

    try:
        text = handle.query(':FM{:d}:INT{:d}:FUNC:SHAP?'.format(channel, channel))
        return text.strip()
    except:
        return 'N.A.'


def set_fm(handle, freq, depth, toggle_state):
    """ Set synthesizer FM to freq and depth.
        Arguments
            freq: float (Hz)
            depth: float (Hz)
            toggle_state: boolean
        Returns visaCode
    """

    try:
        # set up FM freq and depth
        set_mod_toggle(handle, toggle_state)
        num, vcode = handle.write(':FM1:INT1:FREQ {:.9f}HZ; :FM1:DEV {:.9f}HZ'.format(freq, depth))
    except:
        vcode = 'Synthesizer set FM: IOError'

    return vcode


def read_pm_source(handle, channel):
    """ Read synthesizer PM source for channel (1 or 2)
        Arguments
            handle: pyvisa.resources.Resource
            channel: int
        Returns text: str
    """

    try:
        text = handle.query(':PM{:d}:SOUR?'.format(channel))
        return text.strip()
    except:
        return 'N.A.'


def read_pm_state(handle, channel):
    """ Read synthesizer PM state for channel (1 or 2)
        Arguments
            handle: pyvisa.resources.Resource
            channel: int
        Returns status: boolean
    """

    try:
        text = handle.query(':PM{:d}:STAT?'.format(channel))
        return bool(int(text.strip()))
    except:
        return False


def read_pm_dev(handle, channel):
    """ Read synthesizer PM depth for channel (1 or 2)
        Arguments
            handle: pyvisa.resources.Resource
            channel: int
        Returns dev: float
    """

    try:
        text = handle.query(':PM{:d}:DEV?'.format(channel))
        return float(text.strip())
    except:
        return 0


def read_pm_freq(handle, channel):
    """ Read synthesizer PM freq for channel (1 or 2)
        Arguments
            handle: pyvisa.resources.Resource
            channel: int
        Returns
            freq: float
    """

    try:
        text = handle.query(':PM{:d}:INT{:d}:FREQ?'.format(channel, channel))
        return float(text)
    except:
        return 0


def read_pm_waveform(handle, channel):
    """ Read synthesizer PM freq for channel (1 or 2)
        Arguments
            handle: pyvisa.resources.Resource
            channel: int
        Returns
            text: str
    """

    try:
        text = handle.query(':PM{:d}:INT{:d}:FUNC:SHAP?'.format(channel, channel))
        return text.strip()
    except:
        return 'N.A.'


def read_lf_toggle(handle):
    """ Read current LF settings.
        Returns
            status: on/off, bool
    """

    try:
        text = handle.query(':LFO:STAT?')
        status = bool(int(text.strip()))
        return status
    except:
        return False


def read_lf_voltage(handle):
    """ Read current LF voltage
        Returns
            vol: LF voltage, float (V)
    """

    try:
        text = handle.query(':LFO:AMPL?')
        vol = float(text.strip())
        return vol
    except:
        return 0


def read_lf_source(handle):
    """ Read synthesizer LF source
        Returns
            status: boolean
    """

    try:
        text = handle.query(':LFO:SOUR?')
        return text.strip()
    except:
        return 'N.A.'


def set_lf_toggle(handle, toggle_state):
    """ Turn on/off modulation.
        Arguments
            toggle_state: boolean
        Returns visaCode
    """

    try:
        num, vcode = handle.write(':LFO:STAT {:d}'.format(toggle_state))
        return vcode
    except:
        return 'Synthesizer set LF toggle: IOError'


def set_lf_amp(handle, lf_amp):
    """ Set synthesizer LF Amplitude.
        Arguments
            lf_amp: float (V)
        Returns visaCode
    """

    try:
        num, vcode = handle.write(':LFO:AMPL {:.3f}VP'.format(lf_amp))
        return vcode
    except:
        return 'Synthesizer set LF AMP: IOError'


def query_err_msg(handle):
    """ Query the most recent error message. Keep doing it can clear all
        error messages.
        Returns msg: str
    """

    try:
        msg = handle.query(':SYST:ERR?')
        return msg.strip()
    except:
        return 'N.A.'


def read_remote_disp(handle):
    """ Read remote display setting.
        Returns status (bool)
    """

    try:
        text = handle.query(':DISP:REM?')
        status = bool(int(text.strip()))
        return status
    except:
        return False


def full_info_query_(info, handle):
    """ Query all information
    Overwrite properties of the 'info' object
    """

    if handle:
        info.inst_name = handle.resource_name
        info.inst_interface = str(handle.interface_type)
        info.inst_interface_num = handle.interface_number
        info.inst_remote_disp = read_remote_disp(handle)
        info.rf_toggle = read_power_toggle(handle)
        info.syn_power = read_syn_power(handle)
        info.syn_freq = read_syn_freq(handle)
        info.freq = info.syn_freq * info.band_multi
        info.modu_toggle = read_mod_toggle(handle)
        info.am1_toggle = read_am_state(handle, 1)
        info.am1_freq = read_am_freq(handle, 1)
        info.am1_depth_pct, info.am1_depth_db = read_am_depth(handle, 1)
        info.am1_src = read_am_source(handle, 1)
        info.am1_wave = read_am_waveform(handle, 1)
        info.am2_toggle = read_am_state(handle, 2)
        info.am2_freq = read_am_freq(handle, 2)
        info.am2_depth_pct, info.am2_depth_db = read_am_depth(handle, 2)
        info.am2_src = read_am_source(handle, 2)
        info.am2_wave = read_am_waveform(handle, 2)
        info.fm1_toggle = read_fm_state(handle, 1)
        info.fm1_freq = read_fm_freq(handle, 1)
        info.fm1_dev = read_fm_dev(handle, 1)
        info.fm1_src = read_fm_source(handle, 1)
        info.fm1_wave = read_fm_waveform(handle, 1)
        info.fm2_toggle = read_fm_state(handle, 2)
        info.fm2_freq = read_fm_freq(handle, 2)
        info.fm2_dev = read_fm_dev(handle, 2)
        info.fm2_src = read_fm_source(handle, 2)
        info.fm2_wave = read_fm_waveform(handle, 2)
        info.pm1_toggle = read_pm_state(handle, 1)
        info.pm1_freq = read_pm_freq(handle, 1)
        info.pm1_dev = read_pm_dev(handle, 1)
        info.pm1_src = read_pm_source(handle, 1)
        info.pm1_wave = read_pm_waveform(handle, 1)
        info.pm2_toggle = read_pm_state(handle, 2)
        info.pm2_freq = read_pm_freq(handle, 2)
        info.pm2_dev = read_pm_dev(handle, 2)
        info.pm2_src = read_pm_source(handle, 2)
        info.pm2_wave = read_pm_waveform(handle, 2)
        info.lf_toggle = read_lf_toggle(handle)
        info.lf_vol = read_lf_voltage(handle)
        info.lf_src = read_lf_source(handle)
        info.err_msg = ''
    else:
        info.reset()
        info.inst_name = 'No Instrument'
