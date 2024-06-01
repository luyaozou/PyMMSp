#! encoding = utf-8
from dataclasses import dataclass, fields


@dataclass
class Motor_Info:
    inst_name: str = ''

    def reset(self):
        for field in fields(self):
            setattr(self, field.name, field.default)


def query_inst_name(motor_handle):
    """ Query instrument name
        Returns instrument name, str
    """

    try:
        text = motor_handle.query('*IDN?')
        return text.strip()
    except:
        return 'N.A.'


def move(motor_handle, step):
    """
        Move motor by step
    """

    motor_handle.write('1PA+{:d}\n'.format(step))
