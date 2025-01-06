#! encoding = utf-8

import pyvisa
import serial
import socket
from time import sleep, time
import os.path
from PyMMSp.inst.synthesizer import Syn_Info, SYN_MODELS, get_syn_info
from PyMMSp.inst.lockin import Lockin_Info, LOCKIN_MODELS, get_lockin_info
from PyMMSp.inst.awg import AWG_Info, AWG_MODELS, get_awg_info
from PyMMSp.inst.oscillo import Oscilloscope_Info, OSCILLO_MODELS, get_oscillo_info
from PyMMSp.inst.power_supp import Power_Supp_Info, POWER_SUPP_MODELS, get_power_supp_info
from PyMMSp.inst.flow import Flow_Info, FLOW_CTRL_MODELS, get_flow_info
from PyMMSp.inst.gauge import Gauge_Info, GAUGE_CTRL_MODELS, get_gauge_info

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
        self.info_syn = Syn_Info()
        self.h_lockin = None
        self.info_lockin = Lockin_Info()
        self.h_awg = None
        self.info_awg = AWG_Info()
        self.h_oscillo = None
        self.info_oscillo = Oscilloscope_Info()
        self.h_uca = None
        self.info_uca = Power_Supp_Info()
        self.h_flow = None
        self.info_flow = Flow_Info()
        self.h_gauge1 = None
        self.info_gauge1 = Gauge_Info()
        self.h_gauge2 = None
        self.info_gauge2 = Gauge_Info()

    def close_all(self):
        for key, value in self.__dict__.items():
            # make sure they are instrument handles
            if key.startswith('h_'):
                if value and value.is_active:
                    value.close()

    def connect(self, inst_type, connection_type, inst_addr, inst_model, is_sim=False):

        if is_sim:
            if connection_type == 'Ethernet':
                # split the IP address and port
                ip, port = inst_addr.split(':')
                conn = _SimSocketHandle(ip, port, inst_model)
            elif connection_type == 'COM':
                conn = _SimCOMHandle(inst_addr, inst_model)
            elif connection_type == 'GPIB VISA':
                conn = _SimVISAHanlde(inst_addr, inst_model)
            else:
                raise ConnectionError('Connection type not supported.')
        else:
            if connection_type == 'Ethernet':
                # split the IP address and port
                ip, port = inst_addr.split(':')
                conn = _SocketHandle(ip, port, inst_model)
            elif connection_type == 'COM':
                conn = _COMHandle(inst_addr, inst_model)
            elif connection_type == 'GPIB VISA':
                conn = _VISAHandle(inst_addr, inst_model)
            else:
                raise ConnectionError('Connection type not supported.')

        if inst_type == 'Synthesizer':
            self.h_syn = conn
        elif inst_type == 'Lock-in':
            self.lockin = conn
        elif inst_type == 'AWG':
            self.h_awg = conn
        elif inst_type == 'Oscilloscope':
            self.h_oscillo = conn
        elif inst_type == 'Power Supply':
            self.h_uca = conn
        elif inst_type == 'Flow Controller':
            self.h_flow = conn
        elif inst_type == 'Gauge Controller 1':
            self.h_gauge1 = conn
        elif inst_type == 'Gauge Controller 2':
            self.h_gauge2 = conn

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


class Infos:
    """ Holder for instrument information.
    This insures the information can be updated in the GUI,
    because each info object is immutable.
    """

    def __init__(self):

        self.syn = Syn_Info()
        self.lockin = Lockin_Info()
        self.awg = AWG_Info()
        self.oscillo = Oscilloscope_Info()
        self.uca = Power_Supp_Info()
        self.flow = Flow_Info()
        self.gauge1 = Gauge_Info()
        self.gauge2 = Gauge_Info()


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

    def __init__(self, ip, port, model, timeout=1, line_ending='\n', encoding='ASCII', terminal_code=None):

        self._handle = socket.create_connection((ip, port), timeout=timeout)
        self._le = line_ending
        self._enc = encoding
        self._term = terminal_code
        self._ip = ip
        self._port = port
        self._model = model
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
        return None

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


class _SimSocketHandle(_SocketHandle):
    """ Ethernet socket connection simulator
    Make the simulator a child class of the real socket handle to ensure same behavior and less code duplication.
    We only need to override certain methods & properties
    """

    def __init__(self, ip, port, model, timeout=1, line_ending='\n', encoding='ASCII', terminal_code=None):
        try:    # we catch the connection exception because the simulator is used without real connection
            super().__init__(ip, port, model, timeout=1, line_ending='\n', encoding='ASCII', terminal_code=None)
            # if there exists a real connection, close it
            self._handle.close()
        except:
            pass
        self._handle = None
        self._le = line_ending
        self._enc = encoding
        self._term = terminal_code
        self._ip = ip
        self._port = port
        self._model = model
        self._buffer = bytearray()  # this is the new stuff for simulator, a buffer to store all commands
        self.msg = ''

    def send(self, code):
        """ Override _SocketHandle send method. Send the code to internal buffer """

        code_str = code + self._le
        self._buffer.extend(code_str.encode(self._enc))
        return None

    def recv(self, byte, skip=0):
        """ Override _SocketHandle recv method. Read from internal buffer """
        data = self._buffer[skip:byte+skip]
        self._buffer = self._buffer[byte+skip:]
        return data.decode(self._enc).strip()

    def close(self):
        """ Override _SocketHandle close method. Do nothing """
        pass

    @property
    def is_sim(self):
        """ Override _SocketHandle is_sim property. It is a simulator """
        return True

    @property
    def is_active(self):
        """ Override _SocketHandle is_active property. It is always active """
        return True


class _COMHandle:
    """ pyserial.Serial handle for COM ports """
    def __init__(self, addr, model, timeout=1, baudrate=57600, line_ending='\n', encoding='ASCII', terminal_code=None):
        self._handle = serial.Serial(port=addr, timeout=timeout, baudrate=baudrate)
        self._addr = addr
        self._le = line_ending
        self._enc = encoding
        self._term = terminal_code
        self._model = model
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
        return None

    def recv(self, byte, skip=0):
        return self._handle.read(byte)[skip:].decode(self._enc).strip()

    @property
    def is_sim(self):
        return False

    @property
    def is_active(self):
        return self._handle.is_open


class _SimCOMHandle(_COMHandle):
    """ Serial connection simulator
    Make the simulator a child class of the real serial handle to ensure same behavior and less code duplication.
    We only need to override certain methods & properties
    """

    def __init__(self, addr, model, timeout=1, baudrate=57600, line_ending='\n', encoding='ASCII', terminal_code=None, decoder=None):
        try:
            super().__init__(addr, model, timeout=1, baudrate=57600, line_ending='\n', encoding='ASCII', terminal_code=None)
            self._handle.close()
        except:
            pass
        self._handle = None
        self._addr = addr
        self._le = line_ending
        self._enc = encoding
        self._term = terminal_code
        self._model = model
        self._buffer = bytearray()
        self._decoder = decoder
        self.msg = ''

    def send(self, code):
        """ Override _COMHandle send method. Send the code to internal buffer """

        code_str = code + self._le
        self._buffer.extend(code_str.encode(self._enc))
        return None

    def recv(self, byte, skip=0):
        """ Override _COMHandle recv method. Read from internal buffer """
        data = self._buffer[skip:byte+skip]
        self._buffer = self._buffer[byte+skip:]
        return data.decode(self._enc).strip()

    @property
    def is_sim(self):
        """ Override _COMHandle is_sim property. It is a simulator """
        return True

    @property
    def is_active(self):
        """ Override _COMHandle is_active property. It is always active """
        return True


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

    def __init__(self, addr, model, timeout=1, line_ending='\n', encoding='ASCII', terminal_code=None):
        self._rm = pyvisa.highlevel.ResourceManager()
        self._handle = self._rm.open_resource(addr, open_timeout=timeout, read_termination=line_ending)
        self._addr = addr
        self._le = line_ending
        self._enc = encoding
        self._term = terminal_code
        self._model = model
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
        stat = True

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
            return stat, msg

    def send(self, code):
        """ Send only """

        code_str = code + self._le
        num, vcode = self._handle.write(code_str.encode(self._enc))
        return vcode

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


class _SimVISAHanlde(_VISAHandle):
    """ VISA connection simulator
    Make the simulator a child class of the real VISA handle to ensure same behavior and less code duplication.
    We only need to override certain methods & properties
    """

    def __init__(self, addr, model, timeout=1, line_ending='\n', encoding='ASCII', terminal_code=None):
        try:
            super().__init__(addr, model, timeout=1, line_ending='\n', encoding='ASCII', terminal_code=None)
            self._handle.close()
        except:
            pass
        self._rm = None
        self._handle = None
        self._addr = addr
        self._le = line_ending
        self._enc = encoding
        self._term = terminal_code
        self._model = model
        self._buffer = bytearray()
        self.msg = ''

    def send(self, code):
        """ Override _VISAHandle send method. Send the code to internal buffer """

        code_str = code + self._le
        self._buffer.extend(code_str.encode(self._enc))
        return 1

    def recv(self, byte, skip=0):
        """ Override _VISAHandle recv method. Read from internal buffer """
        data = self._buffer[skip:byte + skip]
        self._buffer = self._buffer[byte + skip:]
        return data.decode(self._enc).strip()

    def close(self):
        pass
    @property
    def is_sim(self):
        """ Override _VISAHandle is_sim property. It is a simulator """
        return True

    @property
    def is_active(self):
        """ Override _VISAHandle is_active property. It is always active """
        return True


class BaseSimDecoder:
    """ Basic simulator decoder class
    It provides an internal buffer to stack any code sent to the simulator,
    and pop the buffer on query request.
    Other specific instrument simulators can inherit this parent class
    and override the decoding method.
    """

    def __init__(self):
        self._buffer = []
        self._buffer_byte = bytearray()

    def str_in(self, code):
        """ Send code to simulator """
        self._buffer.append(code)

    def str_out(self):
        return self._buffer.pop()

    def byte_in(self, byte):
        """ Send byte to simulator """
        self._buffer_byte.extend(byte)

    def byte_out(self, byte, skip=0):
        """ Pop byte from simulator """
        data = self._buffer_byte[skip:byte + skip]
        self._buffer_byte = self._buffer_byte[byte + skip:]
        return data


def list_visa_inst():
    """
        List current available instruments.
        Returns
            inst_list: a sorted list of available instrument addresses, list
            inst_str: formated text for GUI display, str
    """

    # open pyvisa resource manager
    try:
        rm = pyvisa.highlevel.ResourceManager()
    except (OSError, ValueError):
        return [], 'Cannot open VISA library!'
    # get available instrument address list
    inst_list = list(rm.list_resources())
    inst_list.sort()
    inst_dict = {}
    for inst in inst_list:
        try:
            # open each instrument and get instrument information
            temp = rm.open_resource(inst, read_termination='\r\n')
            # If the instrument is GPIB, query for the instrument name
            if int(temp.interface_type) == 1:
                text = temp.query('*IDN?')
                inst_dict[inst] = text.strip()
            else:
                inst_dict[inst] = inst
            # close instrument right way in case of unexpected crashes
            temp.close()
        except:
            inst_dict[inst] = 'Visa IO Error'

    inst_str = 'Detected Instrument:\n'
    if inst_dict:
        for inst in inst_list:
            inst_str = inst_str + '{:s}\t{:s}\n'.format(inst, inst_dict[inst])
    else:
        inst_str = 'No instrument available. Check your connection/driver.'

    return inst_list, inst_str


def open_inst(inst_address):
    """
        Open single instrument by its address.
        Returns
            inst_handle: pyvisa object for the instrument
            None:        if cannot open the instrument
    """

    if inst_address == 'N.A.':
        return None
    else:
        try:
            rm = pyvisa.highlevel.ResourceManager()
            inst_handle = rm.open_resource(inst_address)
            return inst_handle
        except:
            return None


def close_inst(*inst_handle):
    """
        Close all connecting instruments
    """

    status = False

    for inst in inst_handle:
        if inst:
            try:
                inst.close()
            except:
                status = True
        else:
            pass

    return status
