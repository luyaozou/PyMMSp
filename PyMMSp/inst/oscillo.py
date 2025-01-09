#! encoding = utf-8
from dataclasses import dataclass, fields
from abc import ABC
import yaml
from PyMMSp.inst.base_simulator import BaseSimDecoder


SENS = (20, 5, 1, 0.5, 0.2)
SENS_STR = ('20 V', '5 V', '1 V', '0.5 V', '0.2 V')
OSCILLO_MODELS = (
    'Tektronix TDS1002',
)

@dataclass
class Oscilloscope_Info:
    inst_name: str = ''

    def reset(self):
        for field in fields(self):
            setattr(self, field.name, field.default)


class OscilloAPI(ABC):
    """ Base API with method stubs in order to enable IDE features
    Contains all functions need to be defined in the API_MAP file

    Get functions always returns a tuple (bool, value) where first element is the status of the query
    Set functions always returns a boolean value indicating the success of the operation
    """

    def get_inst_name(self, handle) -> (bool, str):
        pass


class OscilloSimDecoder(BaseSimDecoder):

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
        self._info = Oscilloscope_Info(inst_name=inst_name)
        self._enc = enc
        self._sep_cmd = sep_cmd
        self._sep_level = sep_level


def get_oscillo_info(handle, info):
    """ Get oscilloscope information """
    pass


def query_inst_name(handle):
    """ Query instrument name
        Returns instrument name, str
    """

    try:
        text = handle.query('*IDN?')
        return text.strip()
    except:
        return 'N.A.'


def set_sampling_len(len_txt):
    """ Set the oscilloscope sampling length to len_text
        Arguments
            len_text: str (user input)
        Returns communication status
            0: safe
            1: fatal
            2: warning
    """

    try:
        length = int(len_txt)
    except ValueError:
        return 1

    if length > 0 and length < 10000:
        return 0
    elif length > 10000:
        return 2
    else:
        return 1


def set_sampling_rate(rate_txt):
    """ Set the oscilloscope sampling rate to rate_text
        Arguments
            rate_text: str (user input, unit in MHz)
        Returns communication status
            0: safe
            1: fatal
            2: warning
    """

    try:
        rate = int(rate_txt)
    except ValueError:
        return 1

    if rate > 0.1 and rate < 10:
        return 0
    elif rate < 0:
        return 1
    else:
        return 2


def set_osc_avg(avg_txt):
    """ Set the oscilloscope average to avg_text
        Arguments
            avg_text: str (user input)
        Returns communication status
            0: safe
            1: fatal
            2: warning
    """

    try:
        avg_txt = int(avg_txt)
    except ValueError:
        return 1


def set_sensitivity(sens_idx):
    """ Set the oscilloscope sensitivity to sens_index
        Arguments
            sens_index: int (user input)
        Returns communication status
            0: safe
            1: fatal
    """

    return SENS[sens_idx]
