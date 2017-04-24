#! encoding = utf-8
import pyvisa


# internal code dictionaries
_P_STATUS = {'0': 'Okay',
             '1': 'Underrange',
             '2': 'Overrange',
             '3': 'Transmitter error',
             '4': 'Transmitter switched off',
             '5': 'No transmitter',
             '6': 'Identification error',
             '7': 'ITR error'}

_P_UNIT_CODE = {0: 'mBar',
                1: 'Torr',
                2: 'Pascal',
                3: 'μmHg'}


def query_p(pressureHandle, chn):
    ''' Query pressure reading.
        Arguments
            chn: channel number. Text. '1' or '2'
        Returns
            msgcode: my status msg code. 0:fatal, 1:warning, 2:safe
            status_txt: instrument status string
            p: pressure reading in current unit if available
        Query Syntax:
            sender:   PR{X}<CR><LF>
            receiver: <ACK><CR><LF>  \x06: positive; \x15 negative
            sender:   \x05
            receiver: a,+b.bbbbE+bb<CR><LF>  a: status; b: value
    '''

    try:
        text = pressureHandle.query('PR{:s}'.format(chn))
        if text.strip() == '\x06':     # if positive acknowledgement
            text = pressureHandle.query('\x05') # query for values
            status, p = text.strip().split(',')
            if status == '0':
                msgcode = 2
            elif status in ['1', '2']:
                msgcode = 1
            else:
                msgcode = 0
            return msgcode, _P_STATUS[status], float(p)
        else:
            return 0, 'Negative acknowledgement', 0
    except:
        return 0, 'System Error', 0


def set_query_p_unit(pressureHandle, unit_idx=-1):
    ''' set/query current pressure unit.
        Arguments
            unit_idx: unit code, int
                      If specified, set the unit; if -1, query the current unit
        Returns
            msgcode: my msg code
            unit_string: name of current unit
        Query Syntax:
            sender:   UNI[,a]<CR><LF>
            receiver: <ACK><CR><LF>  \x06: positive; \x15 negative
            sender:   \x05
            receiver: a<CR><LF>   a: unit code in _UNIT_CODE
    '''

    if unit_idx == -1:
        query_str = 'UNI'
    else:
        query_str = 'UNI,{:d}'.format(unit_idx)

    try:
        text = pressureHandle.query(query_str)
        if text.strip() == '\x06':     # if positive acknowledgement
            text = pressureHandle.query('\x05')
            return 2, _P_UNIT_CODE[int(text.strip())]
        else:
            return 0, 'Negative acknowledgement'
    except:
        return 0, 'System Error'
