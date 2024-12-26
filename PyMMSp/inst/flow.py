#! encoding = utf-8
from dataclasses import dataclass, fields
from importlib.resources import files


FLOW_CTRL_MODELS = (
    'MKS 946',
)

@dataclass
class Flow_Info:
    inst_name: str = ''

    def reset(self):
        for field in fields(self):
            setattr(self, field.name, field.default)


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