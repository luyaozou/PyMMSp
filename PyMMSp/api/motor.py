#! encoding = utf-8


def query_inst_name(motorHandle):
    ''' Query instrument name
        Returns instrument name, str
    '''

    try:
        text = motorHandle.query('*IDN?')
        return text.strip()
    except:
        return 'N.A.'


def move(motorHandle, step):
    '''
        Move motor by step
    '''

    motorHandle.write('1PA+{:d}\n'.format(step))
