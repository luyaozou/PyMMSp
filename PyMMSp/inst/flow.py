#! encoding = utf-8
from dataclasses import dataclass, fields

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