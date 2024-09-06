#! encoding = utf-8
from dataclasses import dataclass, fields

POWER_SUPP_MODELS = (
    'Agilent E3631A',
)

@dataclass
class Power_Supp_Info:
    inst_name: str = ''

    def reset(self):
        for field in fields(self):
            setattr(self, field.name, field.default)



def get_power_supp_info(handle, info):
    """ Get power supply information """
    pass

