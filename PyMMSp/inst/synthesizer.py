#! encoding = utf-8
from dataclasses import dataclass, fields, field
from abc import ABC
import yaml
import re
from PyMMSp.inst.base_simulator import BaseSimDecoder


SYN_MODELS = (
    'Agilent_E8257D',
    'Rohde_Schwarz_SMF100A',
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
    inst_stat = False
    conn_status: bool = False  # connection status
    pow_stat: bool = False
    pow: float = -20.
    harm: int = 1   # harmonics
    freq_cw: float = 12e10  # Hz
    modu_stat: bool = False
    modu_mode_idx: int = 0
    modu_freq: float = 0  # update according to modMode
    modu_amp: float = 0  # update according to modMode
    am_stat: list[int] = field(default_factory=lambda: [0,])
    am_freq: list[float] = field(default_factory=lambda: [0., ])  # Hz
    am_depth_pct: list[float] = field(default_factory=lambda: [1., ])  # float, percent
    am_depth_db: list[float] = field(default_factory=lambda: [-20., ])  # db
    am_src: list[str] = field(default_factory=lambda: ['', ])
    am_waveform: list[str] = field(default_factory=lambda: ['', ])  # ['SINE', 'SQU', 'TRI', 'RAMP']
    fm_stat: list[int] = field(default_factory=lambda: [0,])
    fm_freq: list[float] = field(default_factory=lambda: [0., ])  # Hz
    fm_dev: list[float] = field(default_factory=lambda: [0., ])  # Hz
    fm_src: list[str] = field(default_factory=lambda: ['', ])
    fm_waveform: list[str] = field(default_factory=lambda: ['', ])  # ['SINE', 'SQU', 'TRI', 'RAMP']
    pm_stat: list[int] = field(default_factory=lambda: [0, ])
    pm_freq: list[float] = field(default_factory=lambda: [0., ])  # Hz
    pm_dev: list[float] = field(default_factory=lambda: [0., ])  # Hz
    pm_src: list[str] = field(default_factory=lambda: ['', ])
    pm_waveform: list[str] = field(default_factory=lambda: ['', ])  # ['SINE', 'SQU', 'TRI', 'RAMP']
    lfo_stat: bool = False
    lfo_volt: float = 0.
    lfo_src_idx: list[int] = field(default_factory=lambda: [0, ])
    err_msg: str = ''
    remote_disp_stat: bool = False

    def reset(self):
        for f in fields(self):
            setattr(self, f.name, f.default)

    @property
    def band_multi(self):
        return _VDI_BAND_MULTI[self.band_idx]

    @property
    def modu_mode_txt(self):
        return MODU_MODE[self.modu_mode_idx]

    @property
    def freq_mm(self):
        """ Return output millimeter wave frequency """
        return self.freq_cw * self.harm


def get_syn_info(handle, info):
    """ Get synthesizer information """
    pass


class SynAPI(ABC):
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

    def get_am_depth_pct(self, handle, chan: int) -> (bool, float):
        pass

    def get_am_depth_db(self, handle, chan: int) -> (bool, float):
        pass

    def set_am_depth_pct(self, handle, chan: int, depth: float) -> bool:
        pass

    def set_am_depth_db(self, handle, chan: int, depth: float) -> bool:
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

    def set_lfo_ampl(self, handle, ampl: float, unit: str) -> bool:
        pass

    def get_err(self, handle) -> (bool, str):
        pass

    def get_remote_disp_stat(self, handle) -> (bool, bool):
        pass


class SynSimDecoder(BaseSimDecoder):

    def __init__(self, api_map_file, inst_name, enc='ASCII', sep_cmd=';', sep_level=':'):
        """ Initialize synthesizer simulator decoder
        Arguments
            api_map_file: str, path to the API_MAP file
            enc: str, encoding used in the simulator (pass to bytebuffer. Default is ASCII)
            sep_cmd: str, separator of multiple commands in the command queue, default is ;
            sep_level: str, separator of multiple levels in one command, default is :
        """
        super().__init__()
        with open(api_map_file, 'r') as f:
            self._api_map = yaml.safe_load(''.join(f.readlines()))
        self._info = Syn_Info(inst_name=inst_name)
        self._enc = enc
        self._sep_cmd = sep_cmd
        self._sep_level = sep_level

    def interpret(self, cmd_queue):
        """ Interpret code and return its value """
        # determine the nature of the command:
        # multiple commands may be separated by ;
        # - action without return (like ':INIT')
        # - setting value   (like ':POW -10DBM')
        # - getting value   (like ':POW?')
        for cmd in cmd_queue.split(self._sep_cmd):
            cmd = cmd.strip()
            if cmd.endswith('?'):
                self._interpret_get(cmd)
            elif ' ' in cmd:
                self._interpret_set(cmd)
            else:
                self._interpret_action(cmd)

    def _interpret_get(self, cmd):
        """ Interpret get value command
        Push the response to internal buffer
        """
        # the exact command should be registered in the API_MAP.
        # try to find it
        for item in self._api_map['functions']:
            if self._match_code_multilevel(item['cmd'], cmd):
                if item['channel']:
                    # if this attribute has channel number, pick the correct one
                    # note that the channel number starts from 1
                    chan = self._get_chan(cmd, self._sep_level)
                    v = getattr(self._info, item['attribute'])[chan - 1]
                else:
                    v = getattr(self._info, item['attribute'])
                self.str_in(str(v))
                self.byte_in(str(v).encode(self._enc))
            else:
                pass

    def _interpret_set(self, cmd):
        """ Interpret set value command
        Register the value to the internal Info class
        """
        # the command code and value are separated by blank space.
        # the command code should be registered in the API_MAP.
        code_str, value_str = cmd.upper().split(' ')
        factor = 1  # default scaling factor
        for item in self._api_map['functions']:
            if (not item['cmd'].endswith('?') and
                    self._match_code_multilevel(item['cmd'], code_str)):
                # check if there is unit specified
                if 'unit' in item:
                    # check if there is unit prefixes
                    if 'prefix' in item['unit']:
                        is_found = False
                        # find the prefix used in the value_str
                        base = item['unit']['base']
                        for pre in item['unit']['prefix'].keys():
                            if value_str.endswith(pre+base):
                                # strip the unit in value
                                value_str = value_str.strip(pre+base)
                                factor = float(item['unit']['prefix'][pre])
                                is_found = True
                                break
                        if not is_found:
                            value_str = value_str.strip(base)
                            factor = 1
                    else:
                        # strip the unit in value
                        value_str = value_str.strip(item['unit']['base'])
                else:   # nothing to do
                    pass
                if item['channel']:
                    # if this attribute has channel number, pick the correct one
                    chan = self._get_chan(code_str, self._sep_level)
                    # note that the channel number starts from 1
                    # and since there is channel, the attribute should be a list
                    # we can directly assign the value to the correct list element
                    current_attr_list = getattr(self._info, item['attribute'])
                    n = len(current_attr_list)
                    # assign the value to the correct channel
                    if item['dtype'] == 'str':
                        # if the channel number is out of range, append the list to the correct length
                        if chan > n:
                            current_attr_list.extend(['',] * (chan - n))
                        current_attr_list[chan - 1] = value_str
                    elif item['dtype'] == 'float':
                        # if the channel number is out of range, append the list to the correct length
                        if chan > n:
                            current_attr_list.extend([0., ] * (chan - n))
                        current_attr_list[chan - 1] = float(value_str) * factor
                    elif item['dtype'] == 'int':
                        # if the channel number is out of range, append the list to the correct length
                        if chan > n:
                            current_attr_list.extend([0, ] * (chan - n))
                        current_attr_list[chan - 1] = int(int(value_str) * factor)
                    elif item['dtype'] == 'bool':
                        # if the channel number is out of range, append the list to the correct length
                        if chan > n:
                            current_attr_list.extend([0, ] * (chan - n))
                        # in the instrument boolean value is still represented as integer
                        current_attr_list[chan - 1] = int(value_str)
                else:
                    # attribute is not a list (therefore immutable)
                    # use the setattr to assign new value to the attribute
                    if item['dtype'] == 'str':
                        setattr(self._info, item['attribute'], value_str)
                    elif item['dtype'] == 'float':
                        setattr(self._info, item['attribute'], float(value_str) * factor)
                    elif item['dtype'] == 'int':
                        setattr(self._info, item['attribute'], int(int(value_str) * factor))
                    elif item['dtype'] == 'bool':
                        # in the instrument boolean value is still represented as integer
                        setattr(self._info, item['attribute'], int(value_str))
            else:
                pass

    def _interpret_action(self, cmd):
        """ Interpret action command
        Currently no direct action command is defined """
        pass

    def _match_code_multilevel(self, code_api, code_usr):
        """ Match multi-level code
        Arguments
            code1: str, code from API_MAP, string formatter
            code2: str, code from user (each level may contain channel integers
        Returns
            stat: bool
        """
        # define the replace char of : in curly brace (which is the : used in python string formatter)
        # it needs to be different from self._sep_level
        if self._sep_level == '-':
            rep_char = '*'
        else:
            rep_char = '-'
        list_code1 = self._replace_colon_in_curly_brace(code_api, rep_char).split(self._sep_level)
        list_code2 = code_usr.split(self._sep_level)
        if len(list_code1) != len(list_code2):
            return False
        else:
            for code1, code2 in zip(list_code1, list_code2):
                for char1, char2 in zip(code1, code2):
                    # match each character until the appearance of {
                    if char1 != '{':
                        if char1 != char2:
                            return False
                        else:
                            pass
                    else:
                        pass
            return True

    @staticmethod
    def _replace_colon_in_curly_brace(str_in, rep_char):
        """ Replace colon in curly brace with channel number
        Arguments:
            str_in: str, input string
            rep_char: str, replacement character
        """
        new = []
        in_brace = False
        for char in str_in:
            if char == '{':
                in_brace = True
            elif char == '}':
                in_brace = False
            elif char == ':' and in_brace:
                char = rep_char
            new.append(char)
        return ''.join(new)

    @staticmethod
    def _get_chan(cmd, sep):
        """ Get channel number from the command string
        The channel number is the integer of the first level of the command
        """
        cmd_list = cmd.strip(sep).split(sep)
        match = re.search(r'\d+', cmd_list[0])
        if match:
            return int(match.group())
        else:
            raise ValueError('Channel number not found')


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
        info.pow_stat = read_power_toggle(handle)
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
        info.lfo_src = read_lf_source(handle)
        info.err_msg = ''
    else:
        info.reset()
        info.inst_name = 'No Instrument'
