#! encoding = utf-8
import time
import pyvisa


def ramp_up(start, stop):
    ''' A integer list generator. start < stop '''

    n = start
    while n < stop:
        n = n + 1
        yield n


def ramp_down(start, stop):
    ''' A integer list generator. start > stop '''

    n = start
    while n > stop:
        n = n - 1
        yield n


def init_syn(synHandle):
    ''' Initialize synthesizer.
        Returns visaCode
    '''

    try:
        num, vcode = synHandle.write(':AM1:SOUR INT1; :FM1:SOUR INT1; :LFO:SOUR INT1; :LFO:AMPL 0.1VP; :POW:MODE FIX; :FREQ:MODE CW')
        return vcode
    except:
        return 'IOError'


def query_inst_name(synHandle):
    ''' Query instrument name
        Returns instrument name, str
    '''

    try:
        text = synHandle.query('*IDN?')
        return text.strip()
    except:
        return 'N.A.'


def read_power_toggle(synHandle):
    ''' Read current synthesizer power output.
        Returns status (bool)
    '''

    try:
        text = synHandle.query(':OUTP?')
        status = bool(int(text.strip()))
        return status
    except:
        return False


def set_power_toggle(synHandle, toggle_stat):
    ''' Turn RF power on/off.
        Returns visaCode
    '''

    try:
        if toggle_stat:     # user want to turn on RF
            num, vcode = synHandle.write(':OUTP 1')
            # only ramp up power if the RF is successfully turned on
            if vcode == pyvisa.constants.StatusCode.success:
                vcode = set_syn_power(synHandle, 0)
            else:
                pass
        else:               # user want to turn off RF
            vcode = set_syn_power(synHandle, -20)
            # only turn off RF if power is successfully ramped down
            if vcode == pyvisa.constants.StatusCode.success:
                num, vcode = synHandle.write(':OUTP 0')
            else:
                pass
        return vcode
    except:
        return 'IOError'


def read_syn_power(synHandle):
    ''' Read current synthesizer power.
        Returns current_power, float (dbm)
    '''

    try:
        text = synHandle.query(':POW?')
        current_power = float(text.strip())
        return current_power
    except:
        return -20


def set_syn_power(synHandle, set_power):
    ''' Set synthesizer power.
        Returns visaCode
    '''

    current_power = read_syn_power(synHandle)

    try:
        if set_power > current_power:
            # turn on RF
            for n in ramp_up(current_power, set_power):
                num, vcode = synHandle.write(':POW {:g}DBM'.format(n))
                time.sleep(0.5)   # pause 0.5 second
        elif set_power < current_power:
            for n in ramp_down(current_power, set_power):
                num, vcode = synHandle.write(':POW {:g}DBM'.format(n))
                time.sleep(0.5)   # pause 0.5 second
        else:
            vcode = pyvisa.constants.StatusCode.success
        return vcode
    except:
        return 'IOError'


def read_syn_freq(synHandle):
    ''' Read current synthesizer frequecy.
        Returns current_freq, float (MHz)
    '''

    try:
        text = synHandle.query(':FREQ:CW?')
        current_freq = float(text.strip()) * 1e-6
        return current_freq
    except:
        return 0


def set_syn_freq(synHandle, freq):
    ''' Set the synthesizer frequency to freq.
        Arguments
            lcHandle: pyvisa.resources.Resource, synthesizer handle
            freq: float
        Returns visaCode
    '''

    try:
        num, vcode = synHandle.write(':FREQ:CW {:.9f}MHZ'.format(freq))
        return vcode
    except:
        return 'IOError'


def set_mod_mode(synHandle, mod_index):
    ''' Set synthesizer modulation mode.
        Arguments: mod_index, int
            0: no modulation
            1: AM
            2: FM
        Returns visaCode
    '''

    a_dict = {0: ':AM1:STAT 0; :FM1:STAT 0',
              1: ':FM1:STAT 0; :AM1:STAT 1',
              2: ':AM1:STAT 0; :FM1:STAT 1'}

    try:
        num, vcode = synHandle.write(a_dict[mod_index])
        return vcode
    except:
        return 'IOError'


def read_mod_toggle(synHandle):
    ''' Read current modulation toggle status.
        Returns toggle status (bool)
    '''

    try:
        text = synHandle.query(':OUTP:MOD?')
        return bool(int(text.strip()))
    except:
        return False


def set_mod_toggle(synHandle, toggle_stat):
    ''' Turn on/off modulation.
        Arguments
            toggle_stat: boolean
        Returns visaCode
    '''

    try:
        num, vcode = synHandle.write(':OUTP:MOD {:d}'.format(toggle_stat))
        return vcode
    except:
        return 'IOError'


def read_am_par(synHandle):
    ''' Read current amplitude modulation setting.
        Returns
            freq:  mod freq, float (kHz)
            depth: mod depth, float (%)
            status: on/off, bool
    '''

    try:
        text = synHandle.query(':AM1:INT1:FREQ?')
        freq = float(text.strip())
        text = synHandle.query(':AM1:DEPT?')
        depth = float(text.strip())
        text = synHandle.query(':AM1:STAT?')
        status = bool(int(text.strip()))
        return freq, depth, status
    except:
        return 0, 0, False


def set_am(synHandle, freq, depth, toggle_stat):
    ''' Set synthesizer AM to freq and depth.
        Arguments
            freq: float (kHz)
            depth: float ('%')
            toggle_stat: boolean
        Returns visaCode
    '''

    try:
        # set up AM freq and depth
        set_mod_toggle(synHandle, toggle_stat)
        num, vcode = synHandle.write(':AM1:INT1:FREQ {:.6f}KHZ; :AM1 {:.2f}'.format(freq, depth))
    except:
        vcode = 'IOError'

    return vcode


def read_fm_par(synHandle):
    ''' Read current frequency modulation setting.
        Returns
            freq:  mod freq, float (kHz)
            depth: mod depth, float (kHz)
            status: on/off, bool
    '''

    try:
        text = synHandle.query(':FM1:INT1:FREQ?')
        freq = float(text.strip()) * 1e-3
        text = synHandle.query(':FM1:DEV?')
        depth = float(text.strip()) * 1e-3
        text = synHandle.query(':FM1:STAT?')
        status = bool(int(text.strip()))
        return freq, depth, status
    except:
        return 0, 0, False


def set_fm(synHandle, freq, depth, toggle_stat):
    ''' Set synthesizer FM to freq and depth.
        Arguments
            freq: float (kHz)
            depth: float (kHz)
            toggle_stat: boolean
        Returns visaCode
    '''

    try:
        # set up FM freq and depth
        set_mod_toggle(synHandle, toggle_stat)
        num, vcode = synHandle.write(':FM1:INT1:FREQ {:.6f}KHZ; :FM1:DEV {:.6f}KHZ'.format(freq, depth))
    except:
        vcode = 'IOError'

    return vcode


def read_lf(synHandle):
    ''' Read current LF settings.
        Returns
            vol: LF voltage, str
            status: on/off, bool
    '''

    try:
        text = synHandle.query(':LFO:AMPL?')
        vol = float(text.strip())
        text = synHandle.query(':LFO:STAT?')
        status = bool(int(text.strip()))
        return vol, status
    except:
        return 0, False


def set_lf_toggle(synHandle, toggle_stat):
    ''' Turn on/off modulation.
        Arguments
            toggle_stat: boolean
        Returns visaCode
    '''

    try:
        num, vcode = synHandle.write(':LFO:STAT {:d}'.format(toggle_stat))
        return vcode
    except:
        return 'IOError'


def set_lf_amp(synHandle, lf_amp):
    ''' Set synthesizer LF Amplitude.
        Arguments
            lf_amp: float (V)
        Returns visaCode
    '''

    try:
        num, vcode = synHandle.write(':LFO:AMPL {.3f}VP'.format(lf_amp))
        return vcode
    except:
        return 'IOError'


def query_err_msg(synHandle):
    ''' Query the most recent error message. Keep doing it can clear all
        error messages.
        Returns msg, str
    '''

    try:
        msg = synHandle.query(':SYST:ERR?')
        return msg.strip()
    except:
        return 'N.A.'
