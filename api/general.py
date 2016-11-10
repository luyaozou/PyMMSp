#! encoding = utf-8

import pyvisa
import os.path

def list_inst():
    '''
        List current available instruments.
        Returns
            inst_dict: directory of instrument address and description
            inst_str: formated text for GUI display
    '''

    # open pyvisa resource manager
    try:
        rm = pyvisa.highlevel.ResourceManager()
    except OSError:
        return {}, 'Cannot open VISA library!'
    # get available instrument address list
    inst_list = rm.list_resources()
    inst_dict = {}
    for inst in inst_list:
        # open each instrument and get instrument information
        temp = rm.open_resource(inst)
        try:
            inst_dict[inst] = temp.query('*IDN?')
        except:
            inst_dict[inst] = 'Visa IO Error'
        # close instrument right way to prevent unexpected crashes
        temp.close()

    inst_str = 'Detected Instrument:\n'
    if inst_dict:
        for key, value in inst_dict.items():
            inst_str = inst_str + '{:s}\t{:s}\n'.format(key,value)
    else:
        inst_str = 'No instrument available. Check your connection/driver.'

    return inst_dict, inst_str


def load_inst(inst_cfg_file):
    '''
        Load instruments from the internal instrument config file
        Returns
            synHandle:    pyvisa object for the synthesizer
            lcHandle:     pyvisa object for the lockin
            pciHandle:    pyvisa object for the PCI card
            motorHandle:  pyvisa object for the step motor
    '''

    # first check if configure file exists
    if os.path.exists(inst_cfg_file):
        with open(inst_cfg_file, 'r') as f:
            address = f.readline()
            synHandle = open_inst(address.strip())
            address = f.readline()
            lcHandle = open_inst(address.strip())
            address = f.readline()
            pciHandle = open_inst(address.strip())
            address = f.readline()
            motorHandle = open_inst(address.strip())
        return synHandle, lcHandle, pciHandle, motorHandle
    else:
        return None, None, None, None


def open_inst(inst_address):
    '''
        Open single instrument by its address.
        Returns
            inst_handle: pyvisa object for the instrument
            None:        if cannot open the instrument
    '''

    try:
        rm = pyvisa.highlevel.ResourceManager()
        inst_handle = rm.open_resource(inst_address)
    except:
        inst_handle = None

    return inst_handle


def close_inst(inst_handle):
    '''
        Close all connecting instruments
    '''

    inst_handle.close()

    return 0
