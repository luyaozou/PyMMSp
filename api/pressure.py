#! encoding = utf-8
import pyvisa

def query_pressure(pressureHandle, chn):
    ''' Query pressure reading.
        Arguments
            chn: channel number. Text. '1' or '2'
        Returns
            p: pressure reading in current unit
    '''

    try:
        text = pressureHandle.query('PR{:s}\r\n'.format(chn))
        p = float(text.strip())
        return p
    except:
        return 0


def sel_unit(pressureHandle, chn, idx):
    ''' Select pressure unit.
        Arguments
            chn: channel number. Text. '1' or '2'
            idx: unit index in PresReaderWindow.pUnitSel
                0: mBar
                1: Torr
                2: Pascal
                3: umHg
        Returns
            visaCode
    '''

    try:
        num, vcode = synHandle.write('UNI'.format(toggle_state))
        return vcode
    except:
        return 'IOError'


def query_unit(pressureHandle, chn):
    ''' query current pressure unit.
        Arguments
            chn: channel number. Text. '1' or '2'
        Returns
            idx: unit '''

    unit_dict = {0: 'mBar', 1: 'Torr', 2:'Pascal', 3:'μmHg'}
    try:
        text = pressureHandle.query('UNI,{:s}\r\n'.format(chn))
        return unit_dict[int(text.strip())]
    except:
        return 0
