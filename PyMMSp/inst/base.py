#! encoding = utf-8

import pyvisa
import serial
import socket
from importlib.resources import files
from time import sleep, time
import os.path
import yaml
import inspect
from PyMMSp.inst.synthesizer import Syn_Info, SYN_MODELS, SynAPI, SynSimDecoder, get_syn_info
from PyMMSp.inst.lockin import Lockin_Info, LOCKIN_MODELS, LockinAPI, LockinSimDecoder, get_lockin_info
from PyMMSp.inst.awg import AWG_Info, AWG_MODELS, AWGAPI, AWGSimDecoder, get_awg_info
from PyMMSp.inst.oscillo import Oscilloscope_Info, OSCILLO_MODELS, OscilloAPI, OscilloSimDecoder, get_oscillo_info
from PyMMSp.inst.power_supp import Power_Supp_Info, POWER_SUPP_MODELS, PowerSuppAPI, PowerSuppSimDecoder, get_power_supp_info
from PyMMSp.inst.flow import Flow_Info, FLOW_CTRL_MODELS, FlowAPI, FlowSimDecoder, get_flow_info
from PyMMSp.inst.gauge import Gauge_Info, GAUGE_CTRL_MODELS, GaugeAPI, GaugeSimDecoder, get_gauge_info
from PyMMSp.inst.base_simulator import SimHandle


INST_TYPES = (
    'Synthesizer',
    'Lock-in',
    'AWG',
    'Oscilloscope',
    'Power Supply',
    'Flow Controller',
    'Gauge Controller 1',
    'Gauge Controller 2',
)

INST_MODEL_DICT = {
    'Synthesizer': SYN_MODELS,
    'Lock-in': LOCKIN_MODELS,
    'AWG': AWG_MODELS,
    'Oscilloscope': OSCILLO_MODELS,
    'Power Supply': POWER_SUPP_MODELS,
    'Flow Controller': FLOW_CTRL_MODELS,
    'Gauge Controller 1': GAUGE_CTRL_MODELS,
    'Gauge Controller 2': GAUGE_CTRL_MODELS,
}

CONNECTION_TYPES = (
    'Ethernet',
    'COM',
    'GPIB VISA',
)


class Handles:
    """ Holder for instrument handles.
    This insures the handles can be updated in the GUI,
    because each handle object is immutable.
    """

    def __init__(self):

        self.h_syn = None
        self.api_syn = None
        self.info_syn = Syn_Info()
        self.h_lockin = None
        self.api_lockin = None
        self.info_lockin = Lockin_Info()
        self.h_awg = None
        self.api_awg = None
        self.info_awg = AWG_Info()
        self.h_oscillo = None
        self.api_oscillo = None
        self.info_oscillo = Oscilloscope_Info()
        self.h_uca = None
        self.api_uca = None
        self.info_uca = Power_Supp_Info()
        self.h_flow = None
        self.api_flow = None
        self.info_flow = Flow_Info()
        self.h_gauge1 = None
        self.api_gauge1 = None
        self.info_gauge1 = Gauge_Info()
        self.h_gauge2 = None
        self.api_gauge2 = None
        self.info_gauge2 = Gauge_Info()

    def close_all(self):
        for key, value in self.__dict__.items():
            # make sure they are instrument handles
            if key.startswith('h_'):
                if value and value.is_active:
                    value.close()

    def connect(self, inst_type: str, connection_type: str, inst_addr: str,
                inst_model: str, is_sim=False):

        if is_sim:
            if connection_type == 'Ethernet':
                # split the IP address and port
                ip, port = inst_addr.split(':')
                conn = SimHandle()
            elif connection_type == 'COM':
                conn = SimHandle()
            elif connection_type == 'GPIB VISA':
                conn = SimHandle()
            else:
                raise ConnectionError('Connection type not supported.')
        else:
            if connection_type == 'Ethernet':
                # split the IP address and port
                ip, port = inst_addr.split(':')
                conn = _SocketHandle(ip, port)
            elif connection_type == 'COM':
                conn = _COMHandle(inst_addr)
            elif connection_type == 'GPIB VISA':
                conn = _VISAHandle(inst_addr)
            else:
                raise ConnectionError('Connection type not supported.')

        if inst_type == 'Synthesizer':
            self.h_syn = conn
            self.api_syn = DynamicSynAPI(files('PyMMSp.inst').joinpath(f'API_MAP_{inst_model:s}.yaml'))
            if is_sim:
                self.h_syn.set_decoder(SynSimDecoder(files('PyMMSp.inst').joinpath(f'API_MAP_{inst_model:s}.yaml'),
                                                     inst_model))
        elif inst_type == 'Lock-in':
            self.h_lockin = conn
            self.api_lockin = DynamicLockinAPI(files('PyMMSp.inst').joinpath(f'API_MAP_{inst_model:s}.yaml'))
            if is_sim:
                self.h_lockin.set_decoder(LockinSimDecoder(files('PyMMSp.inst').joinpath(f'API_MAP_{inst_model:s}.yaml'),
                                                           inst_model))
        elif inst_type == 'AWG':
            self.h_awg = conn
            self.api_awg = DynamicAWGAPI(files('PyMMSp.inst').joinpath(f'API_MAP_{inst_model:s}.yaml'))
            if is_sim:
                self.h_awg.set_decoder(AWGSimDecoder(files('PyMMSp.inst').joinpath(f'API_MAP_{inst_model:s}.yaml'),
                                                     inst_model))
        elif inst_type == 'Oscilloscope':
            self.h_oscillo = conn
            self.api_oscillo = DynamicOscilloAPI(files('PyMMSp.inst').joinpath(f'API_MAP_{inst_model:s}.yaml'))
            if is_sim:
                self.h_oscillo.set_decoder(OscilloSimDecoder(files('PyMMSp.inst').joinpath(f'API_MAP_{inst_model:s}.yaml'),
                                                             inst_model))
        elif inst_type == 'Power Supply':
            self.h_uca = conn
            self.api_uca = DynamicPowerSuppAPI(files('PyMMSp.inst').joinpath(f'API_MAP_{inst_model:s}.yaml'))
            if is_sim:
                self.h_uca.set_decoder(PowerSuppSimDecoder(files('PyMMSp.inst').joinpath(f'API_MAP_{inst_model:s}.yaml'),
                                                           inst_model))
        elif inst_type == 'Flow Controller':
            self.h_flow = conn
            self.api_flow = DynamicFlowAPI(files('PyMMSp.inst').joinpath(f'API_MAP_{inst_model:s}.yaml'))
            if is_sim:
                self.h_flow.set_decoder(FlowSimDecoder(files('PyMMSp.inst').joinpath(f'API_MAP_{inst_model:s}.yaml'),
                                                       inst_model))
        elif inst_type == 'Gauge Controller 1':
            self.h_gauge1 = conn
            self.api_gauge1 = DynamicGaugeAPI(files('PyMMSp.inst').joinpath(f'API_MAP_{inst_model:s}.yaml'))
            if is_sim:
                self.h_gauge1.set_decoder(GaugeSimDecoder(files('PyMMSp.inst').joinpath(f'API_MAP_{inst_model:s}.yaml'),
                                                          inst_model))
        elif inst_type == 'Gauge Controller 2':
            self.h_gauge2 = conn
            self.api_gauge2 = DynamicGaugeAPI(files('PyMMSp.inst').joinpath(f'API_MAP_{inst_model:s}.yaml'))
            if is_sim:
                self.h_gauge2.set_decoder(GaugeSimDecoder(files('PyMMSp.inst').joinpath(f'API_MAP_{inst_model:s}.yaml'),
                                                          inst_model))
        else:
            raise ValueError('Instrument type not supported.')

    def refresh(self, inst_type):
        if inst_type == 'Synthesizer':
            get_syn_info(self.h_syn, self.info_syn)
        elif inst_type == 'Lock-in':
            get_lockin_info(self.h_lockin, self.info_lockin)
        elif inst_type == 'AWG':
            get_awg_info(self.h_awg, self.info_awg)
        elif inst_type == 'Oscilloscope':
            get_oscillo_info(self.h_oscillo, self.info_oscillo)
        elif inst_type == 'Power Supply':
            get_power_supp_info(self.h_uca, self.info_uca)
        elif inst_type == 'Flow Controller':
            get_flow_info(self.h_flow, self.info_flow)
        elif inst_type == 'Gauge Controller 1':
            get_gauge_info(self.h_gauge1, self.info_gauge1)
        elif inst_type == 'Gauge Controller 2':
            get_gauge_info(self.h_gauge2, self.info_gauge2)


class _BadHandle:
    """ A "bad" instrument handle class.
    Used for representing the error instrument connection.

    """

    is_active = False
    is_sim = False

    def __init__(self, addr='', port='', msg='Connection failure'):
        self.addr = addr
        self.port = port
        self.msg = msg

    def close(self):
        pass

    def set(self, *args):
        pass


class _SocketHandle:
    """ Ethernet socket connection. """

    def __init__(self, ip, port, timeout=1, line_ending='\n', encoding='ASCII', terminal_code=None):

        self._handle = socket.create_connection((ip, port), timeout=timeout)
        self._le = line_ending
        self._enc = encoding
        self._term = terminal_code
        self._ip = ip
        self._port = port
        self.msg = ''

    def query(self, code=None, byte=64, skip=0):
        """ Send and read

        Arguments
            code: str               code to send for query
            byte: int               query byte
            skip: int               skip leading characters
        Returns
            msg: str                query message
        """

        if code:
            self.send(code)
        else:
            pass

        if self._term:      # loop until get terminal char
            ml = []
            while True:
                msg = self.recv(byte, skip=skip)
                ml.append(msg)
                if msg.endswith(self._term):
                    break
                else:
                    pass
            return ''.join(ml)
        else:
            msg = self.recv(byte, skip=skip)
            return msg

    def send(self, code):
        """ Send only """

        code_str = code + self._le
        self._handle.send(code_str.encode(self._enc))

    def recv(self, byte, skip=0):
        return self._handle.recv(byte)[skip:].decode(self._enc).strip()

    def close(self):
        self._handle.close()

    @property
    def addr(self):
        return ':'.join([self._ip, self._port])

    @property
    def port(self):
        return self._port

    @property
    def ip(self):
        return self._ip

    @property
    def is_sim(self):
        return False

    @property
    def is_active(self):
        # fileno() returns -1 for closed socket object
        return self._handle.fileno() != -1

    def set_decoder(self, decoder):
        # real instrument handle does not need decoder
        pass


class _COMHandle:
    """ pyserial.Serial handle for COM ports """
    def __init__(self, addr, timeout=1, baudrate=57600, line_ending='\n', encoding='ASCII', terminal_code=None):
        self._handle = serial.Serial(port=addr, timeout=timeout, baudrate=baudrate)
        self._addr = addr
        self._le = line_ending
        self._enc = encoding
        self._term = terminal_code
        self.msg = ''

    def query(self, code=None, byte=64, skip=0):
        """ Send and read

        Arguments
            code: str               code to send for query
            byte: int               query byte
            skip: int               skip leading characters
        Returns
            msg: str                query message
        """

        if code:
            self.send(code)
        else:
            pass

        if self._term:      # loop until get terminal char
            ml = []
            while True:
                msg = self.recv(byte, skip=skip)
                ml.append(msg)
                if msg.endswith(self._term):
                    break
                else:
                    pass
            return ''.join(ml)
        else:
            msg = self.recv(byte, skip=skip)
            return msg

    def send(self, code):
        """ Send only """

        code_str = code + self._le
        self._handle.write(code_str.encode(self._enc))

    def recv(self, byte, skip=0):
        return self._handle.read(byte)[skip:].decode(self._enc).strip()

    @property
    def is_sim(self):
        return False

    @property
    def is_active(self):
        return self._handle.is_open

    def set_decoder(self, decoder):
        # real instrument handle does not need decoder
        pass


class _VISAHandle:
    """ pyvisa.Resource handle for GPIB instruments

    Attributes
    ----------
        addr: str               address
        timeout: float          timeout
        baudrate: int           baud rate
        is_sim: False           Is inst simulator ? (False)
        is_active: bool         Is session active ?

    Public methods
        query(code, byte, skip) -> str             query inst
        send(code)                                 send code to inst
        recv(byte)                                 receive byte from inst
        close()                                    close connection

    """

    def __init__(self, addr, timeout=1, line_ending='\n', encoding='ASCII', terminal_code=None):
        self._rm = pyvisa.highlevel.ResourceManager()
        self._handle = self._rm.open_resource(addr, open_timeout=timeout, read_termination=line_ending)
        self._addr = addr
        self._le = line_ending
        self._enc = encoding
        self._term = terminal_code
        self.msg = ''

    def query(self, code=None, byte=64, skip=0):
        """ Send and read

        Arguments
            code: str               code to send for query
        Returns
            msg: str                query message
        """

        if code:
            self.send(code)
        else:
            pass

        if self._term:  # loop until get terminal char
            ml = []
            while True:
                msg = self.recv(byte, skip=skip)
                ml.append(msg)
                if msg.endswith(self._term):
                    break
                else:
                    pass
            return ''.join(ml)
        else:
            msg = self.recv(byte, skip=skip)
            return msg

    def send(self, code):
        """ Send only """

        code_str = code + self._le
        _ = self._handle.write(code_str.encode(self._enc))

    def recv(self, byte, skip=0):
        return self._handle.read(byte)[skip:].decode(self._enc).strip()

    def close(self):
        pass

    @property
    def is_sim(self):
        return False

    @property
    def is_active(self):
        return self._handle.is_open

    def set_decoder(self, decoder):
        # real instrument handle does not need decoder
        pass


class DynamicSynAPI(SynAPI):
    """ Dynamic API loading API_MAP file to create real functions """

    def __init__(self, api_map_file):
        functions = _create_funcs(api_map_file)
        for name, func in functions.items():
            setattr(self, name, func)


class DynamicLockinAPI(LockinAPI):
    """ Dynamic API loading API_MAP file to create real functions """

    def __init__(self, api_map_file):
        functions = _create_funcs(api_map_file)
        for name, func in functions.items():
            setattr(self, name, func)


class DynamicAWGAPI(AWGAPI):
    """ Dynamic API loading API_MAP file to create real functions """

    def __init__(self, api_map_file):
        functions = _create_funcs(api_map_file)
        for name, func in functions.items():
            setattr(self, name, func)


class DynamicOscilloAPI(OscilloAPI):
    """ Dynamic API loading API_MAP file to create real functions """

    def __init__(self, api_map_file):
        functions = _create_funcs(api_map_file)
        for name, func in functions.items():
            setattr(self, name, func)


class DynamicPowerSuppAPI(PowerSuppAPI):
    """ Dynamic API loading API_MAP file to create real functions """

    def __init__(self, api_map_file):
        functions = _create_funcs(api_map_file)
        for name, func in functions.items():
            setattr(self, name, func)


class DynamicFlowAPI(FlowAPI):
    """ Dynamic API loading API_MAP file to create real functions """

    def __init__(self, api_map_file):
        functions = _create_funcs(api_map_file)
        for name, func in functions.items():
            setattr(self, name, func)


class DynamicGaugeAPI(GaugeAPI):
    """ Dynamic API loading API_MAP file to create real functions """

    def __init__(self, api_map_file):
        functions = _create_funcs(api_map_file)
        for name, func in functions.items():
            setattr(self, name, func)


def _create_funcs(api_map_file):
    """ Create functions from the API_MAP file """
    with open(api_map_file, 'r') as f:
        api_map = yaml.safe_load(''.join(f.readlines()))
    functions = {}
    for item in api_map['functions']:
        func_name = item['name']
        arg_names = item['args']
        kwarg_names = item['kwargs']
        cmd = item['cmd']
        if func_name.startswith('set_'):
            # check if there is linked presets to call
            if 'link_preset' in item:
                # we need to find which argument(s) matches the linked
                # preset, and replace the input value with the preset dict value
                arg_indices = []
                for i, arg in enumerate(arg_names):
                    if arg == item['link_preset']:
                        preset_dict = api_map['presets'][arg]
                        arg_indices.append(i)
                kwarg_indices = []
                for i, kwarg in enumerate(kwarg_names):
                    if kwarg == item['link_preset']:
                        preset_dict = api_map['presets'][kwarg]
                        kwarg_indices.append(i)
                def func(handle, *args, **kwargs):
                    new_args = []
                    new_kwargs = {}
                    for i, arg in enumerate(args):
                        if i in arg_indices:
                            new_args.append(preset_dict[arg])
                        else:
                            new_args.append(arg)
                    for i, kwarg in enumerate(kwargs):
                        if kwarg in kwarg_indices:
                            new_kwargs[kwarg] = preset_dict[kwarg]
                        else:
                            new_kwargs[kwarg] = kwargs[kwarg]
                    code = cmd.format(*new_args, **new_kwargs)
                    handle.send(code)
            else:
                def func(handle, *args, **kwargs):
                    code = cmd.format(*args, **kwargs)
                    handle.send(code)
        elif func_name.startswith('get_'):
            # The data type choice must be done outside the function
            # declaration. Otherwise, each function will go through the
            # conditional statements and fail to match the correct data type.
            # check if there is linked presets to call
            if 'link_preset' in item:
                # we need to find which argument(s) matches the linked
                # preset, and replace the input value with the preset dict value
                preset_name = item['link_preset']
                def func(handle, *args, **kwargs):
                    print('Inside:', cmd)
                    code = cmd.format(*args, **kwargs)
                    value_str = handle.query(code)
                    print(value_str)
                    # find the corresponding key in preset
                    is_found = False
                    for key, value in api_map['presets'][preset_name].items():
                        if str(value) == value_str:
                            return key
                    if not is_found:
                        raise ValueError('Returned value not found in preset.')
            else:
                if item['dtype'] == 'float':
                    def func(handle, *args, **kwargs):
                        code = cmd.format(*args, **kwargs)
                        value_str = handle.query(code)
                        return float(value_str)
                elif item['dtype'] == 'int':
                    def func(handle, *args, **kwargs):
                        code = cmd.format(*args, **kwargs)
                        value_str = handle.query(code)
                        return int(value_str)
                elif item['dtype'] == 'bool':
                    def func(handle, *args, **kwargs):
                        code = cmd.format(*args, **kwargs)
                        value_str = handle.query(code)
                        return bool(int(value_str))
                elif item['dtype'] == 'str':
                    def func(handle, *args, **kwargs):
                        code = cmd.format(*args, **kwargs)
                        value_str = handle.query(code)
                        return value_str
                else:
                    raise ValueError('Data type not supported.')
        else:
            def func(handle, *args, **kwargs):
                pass
        functions[func_name] = func
    return functions
