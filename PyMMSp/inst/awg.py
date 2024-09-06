#! encoding = utf-8
from dataclasses import dataclass, fields

AWG_MODELS = (
    'Tektronix AWG520',
)

@dataclass
class AWG_Info:
    inst_name: str = ''

    def reset(self):
        for field in fields(self):
            setattr(self, field.name, field.default)


def get_awg_info(handle, info):
    """ Get AWG information """
    pass