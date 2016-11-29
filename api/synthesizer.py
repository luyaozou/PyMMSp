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
        num, vcode = synHandle.write(':AM1:SOUR INT1; :AM1:STAT 0; :FM1:SOUR INT1; :FM1:STAT 0; :OUTP:MOD 0; :LFO:SOUR INT1; :LFO:AMPL 0VP; :POW:MODE FIX; :FREQ:MODE CW; :DISP:REM 0')
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
        Returns current_freq, float (Hz)
    '''

    try:
        text = synHandle.query(':FREQ:CW?')
        current_freq = float(text.strip())
        return current_freq
    except:
        return 0


def set_syn_freq(synHandle, freq):
    ''' Set the synthesizer frequency to freq.
        Arguments
            synHandle: pyvisa.resources.Resource, synthesizer handle
            freq: float (MHz)
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
        depth = float(text.strip()) * 100
        text = synHandle.query(':AM1:STAT?')
        status = bool(int(text.strip()))
        return freq, depth, status
    except:
        return 0, 0, False


def read_am_source(synHandle, channel):
    ''' Read synthesizer AM source for channel (1 or 2)
        Arguments
            synHandle: pyvisa.resources.Resource
            channel: int
        Returns
            text: str
    '''

    try:
        text = synHandle.query(':AM{:d}:SOUR?'.format(channel))
        return text.strip()
    except:
        return 'N.A.'


def read_am_state(synHandle, channel):
    ''' Read synthesizer AM state for channel (1 or 2)
        Arguments
            synHandle: pyvisa.resources.Resource
            channel: int
        Returns
            status: boolean
    '''

    try:
        text = synHandle.query(':AM{:d}:STAT?'.format(channel))
        return bool(int(text.strip()))
    except:
        return False


def read_am_depth(synHandle, channel):
    ''' Read synthesizer AM depth for channel (1 or 2)
        Arguments
            synHandle: pyvisa.resources.Resource
            channel: int
        Returns
            depth_linear: float, depth in %
            depth_exp: float, depth in dB
    '''

    try:
        text = synHandle.query(':AM{:d}:DEPT?'.format(channel))
        depth_linear = float(text) * 100
        text = synHandle.query(':AM{:d}:DEPT:EXP?'.format(channel))
        depth_exp = float(text)
        return depth_linear, depth_exp
    except:
        return 0, 0


def read_am_freq(synHandle, channel):
    ''' Read synthesizer AM freq for channel (1 or 2)
        Arguments
            synHandle: pyvisa.resources.Resource
            channel: int
        Returns
            freq: float
    '''

    try:
        text = synHandle.query(':AM{:d}:INT{:d}:FREQ?'.format(channel, channel))
        return float(text)
    except:
        return 0


def read_am_waveform(synHandle, channel):
    ''' Read synthesizer AM freq for channel (1 or 2)
        Arguments
            synHandle: pyvisa.resources.Resource
            channel: int
        Returns
            text: str
    '''

    try:
        text = synHandle.query(':AM{:d}:INT{:d}:FUNC:SHAP?'.format(channel, channel))
        return text.strip()
    except:
        return 'N.A.'


def set_am(synHandle, freq, depth, toggle_stat):
    ''' Set synthesizer AM to freq and depth.
        Arguments
            freq: float (Hz)
            depth: float
            toggle_stat: boolean
        Returns visaCode
    '''

    try:
        # set up AM freq and depth
        set_mod_toggle(synHandle, toggle_stat)
        num, vcode = synHandle.write(':AM1:INT1:FREQ {:.9f}HZ; :AM1 {:.3f}'.format(freq, depth))
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


def read_fm_source(synHandle, channel):
    ''' Read synthesizer FM source for channel (1 or 2)
        Arguments
            synHandle: pyvisa.resources.Resource
            channel: int
        Returns
            text: str
    '''

    try:
        text = synHandle.query(':FM{:d}:SOUR?'.format(channel))
        return text.strip()
    except:
        return 'N.A.'


def read_fm_state(synHandle, channel):
    ''' Read synthesizer FM state for channel (1 or 2)
        Arguments
            synHandle: pyvisa.resources.Resource
            channel: int
        Returns
            status: boolean
    '''

    try:
        text = synHandle.query(':FM{:d}:STAT?'.format(channel))
        return bool(int(text.strip()))
    except:
        return False


def read_fm_dev(synHandle, channel):
    ''' Read synthesizer FM depth for channel (1 or 2)
        Arguments
            synHandle: pyvisa.resources.Resource
            channel: int
        Returns
            dev: float
    '''

    try:
        text = synHandle.query(':FM{:d}:DEV?'.format(channel))
        dev = float(text)
        return dev
    except:
        return 0


def read_fm_freq(synHandle, channel):
    ''' Read synthesizer FM freq for channel (1 or 2)
        Arguments
            synHandle: pyvisa.resources.Resource
            channel: int
        Returns
            freq: float
    '''

    try:
        text = synHandle.query(':AM{:d}:INT{:d}:FREQ?'.format(channel, channel))
        return float(text)
    except:
        return 0


def read_fm_waveform(synHandle, channel):
    ''' Read synthesizer FM freq for channel (1 or 2)
        Arguments
            synHandle: pyvisa.resources.Resource
            channel: int
        Returns
            text: str
    '''

    try:
        text = synHandle.query(':FM{:d}:INT{:d}:FUNC:SHAP?'.format(channel, channel))
        return text.strip()
    except:
        return 'N.A.'


def set_fm(synHandle, freq, depth, toggle_stat):
    ''' Set synthesizer FM to freq and depth.
        Arguments
            freq: float (Hz)
            depth: float (Hz)
            toggle_stat: boolean
        Returns visaCode
    '''

    try:
        # set up FM freq and depth
        set_mod_toggle(synHandle, toggle_stat)
        num, vcode = synHandle.write(':FM1:INT1:FREQ {:.9f}HZ; :FM1:DEV {:.9f}HZ'.format(freq, depth))
    except:
        vcode = 'IOError'

    return vcode


def read_pm_source(synHandle, channel):
    ''' Read synthesizer PM source for channel (1 or 2)
        Arguments
            synHandle: pyvisa.resources.Resource
            channel: int
        Returns
            text: str
    '''

    try:
        text = synHandle.query(':PM{:d}:SOUR?'.format(channel))
        return text.strip()
    except:
        return 'N.A.'


def read_pm_state(synHandle, channel):
    ''' Read synthesizer PM state for channel (1 or 2)
        Arguments
            synHandle: pyvisa.resources.Resource
            channel: int
        Returns
            status: boolean
    '''

    try:
        text = synHandle.query(':PM{:d}:STAT?'.format(channel))
        return bool(int(text.strip()))
    except:
        return False


def read_pm_dev(synHandle, channel):
    ''' Read synthesizer PM depth for channel (1 or 2)
        Arguments
            synHandle: pyvisa.resources.Resource
            channel: int
        Returns
            dev: float
    '''

    try:
        text = synHandle.query(':PM{:d}:DEV?'.format(channel))
        dev = float(text)
        return dev
    except:
        return 0


def read_pm_freq(synHandle, channel):
    ''' Read synthesizer PM freq for channel (1 or 2)
        Arguments
            synHandle: pyvisa.resources.Resource
            channel: int
        Returns
            freq: float
    '''

    try:
        text = synHandle.query(':PM{:d}:INT{:d}:FREQ?'.format(channel, channel))
        return float(text)
    except:
        return 0


def read_pm_waveform(synHandle, channel):
    ''' Read synthesizer PM freq for channel (1 or 2)
        Arguments
            synHandle: pyvisa.resources.Resource
            channel: int
        Returns
            text: str
    '''

    try:
        text = synHandle.query(':PM{:d}:INT{:d}:FUNC:SHAP?'.format(channel, channel))
        return text.strip()
    except:
        return 'N.A.'


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


def read_lf_source(synHandle):
    ''' Read synthesizer LF source
        Returns
            status: boolean
    '''

    try:
        text = synHandle.query(':LFO:SOUR?')
        return text.strip()
    except:
        return 'N.A.'


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


def read_remote_disp(synHandle):
    ''' Read remote display setting.
        Returns status (bool)
    '''

    try:
        text = synHandle.query(':DISP:REM?')
        status = bool(int(text.strip()))
        return status
    except:
        return False
