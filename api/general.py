#! encoding = utf-8

import visa


def list_inst():
    '''
        List current available instruments.
        Returns
            inst_dict: directory of instrument address and description
            inst_str: formated text for GUI display
    '''

    # open pyvisa resource manager
    try:
        rm = visa.ResourceManager()
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
