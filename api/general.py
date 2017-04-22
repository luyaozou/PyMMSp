#! encoding = utf-8

import pyvisa
import os.path

def list_inst():
    '''
        List current available instruments.
        Returns
            inst_list: a sorted list of available instrument addresses, list
            inst_str: formated text for GUI display, str
    '''

    # open pyvisa resource manager
    try:
        rm = pyvisa.highlevel.ResourceManager()
    except OSError:
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
    '''
        Open single instrument by its address.
        Returns
            inst_handle: pyvisa object for the instrument
            None:        if cannot open the instrument
    '''

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
    '''
        Close all connecting instruments
    '''

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
