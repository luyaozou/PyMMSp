#! encoding = utf-8
from dataclasses import dataclass, fields
from importlib.resources import files
from abc import ABC
import yaml
from PyMMSp.inst.base_simulator import BaseSimDecoder


FLOW_CTRL_MODELS = (
    'MKS 946',
)

@dataclass
class Flow_Info:
    inst_name: str = ''

    def reset(self):
        for field in fields(self):
            setattr(self, field.name, field.default)


class FlowAPI(ABC):
    """ Base API with method stubs in order to enable IDE features
    Contains all functions need to be defined in the API_MAP file

    Get functions always returns a tuple (bool, value) where first element is the status of the query
    Set functions always returns a boolean value indicating the success of the operation
    """

    def get_inst_name(self, handle) -> (bool, str):
        pass


class FlowSimDecoder(BaseSimDecoder):

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
        self._info = Flow_Info(inst_name=inst_name)
        self._enc = enc
        self._sep_cmd = sep_cmd
        self._sep_level = sep_level


def get_flow_info(handle, info):
    """ Get flow controller information """
    pass


def load_gcf_gases():
    """ Load GCF gas data from file """
    gcf_gases = []
    with open(files('PyMMSp.inst').joinpath('consts_gcf.dat'), 'r') as f:
        for a_line in f:
            if a_line.strip() and not a_line.startswith('#'):
                a_list = a_line.split()
                gcf_gases.append((a_list[0], int(a_list[1]), a_list[2], a_list[3],
                                  float(a_list[4]), float(a_list[5])))
    return tuple(gcf_gases)
