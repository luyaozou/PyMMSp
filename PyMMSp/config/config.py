#! encoding = utf-8

""" System configuration files """

import json
from dataclasses import dataclass, field
from PyMMSp.libs.consts import VERSION, TEMP_DIR


def to_json(obj, filename):
    """ Serialize an object to json and save on disk
    :argument
        obj: plan object
        filename: str           filename to be saved
    """

    with open(filename, 'w') as fp:
        json.dump(_obj2dict(obj), fp, indent=2)


def from_json_(obj, filename):
    """ Load data from json. Mutable functiona and replace obj in place
    :argument
        obj: the object to write value in
        f: str          filename to load
    """
    with open(filename, 'r') as fp:
        dict_ = json.load(fp)
        _dict2obj_(obj, dict_)


def _obj2dict(obj):
    """ Convert plain object to dictionary (for json dump) """
    d = {}
    for attr in dir(obj):
        if not attr.startswith('__'):
            d[attr] = getattr(obj, attr)
    return d


def _dict2obj_(obj, dict_):
    """ Convert dictionary values back to plain obj. Mutable function
    :argument
        obj: object to be updated
        dict_: dictionary
    """

    for key, value in dict_.items():
        if isinstance(value, dict):
            for k, v in value.items():
                if isinstance(v, list):
                    # convert list to tuple
                    if len(v) > 0 and isinstance(v[0], list):
                        # convert list in list to tuple as well
                        value[k] = (tuple(vv) for vv in v)
                    else:
                        value[k] = tuple(v)
        setattr(obj, key, value)


@dataclass
class Prefs:
    """ Global preferences """

    debug: bool = False
    version: str = VERSION
    geometry: tuple = (100, 100, 1600, 900)
    is_test: bool = False
    tmp_dir: str = str(TEMP_DIR)

    syn_harm: int = 1
    syn_freq: float = 50000.

    # monitor settings
    syn_panel_to_monitor_idx: int = 1
    lockin_panel_to_monitor_idx: int = 2
    oscillo_panel_to_monitor_idx: int = 3
    awg_panel_to_monitor_idx: int = 4
    dc_panel_to_monitor_idx: int = 0
    flow_panel_to_monitor_idx: int = 5
    gauge_panel_to_monitor_idx: int = 6
    motor_panel_to_monitor_idx: int = 0

    n_monitors: int = 6
    monitor_xrange_idx: list = field(default_factory=lambda: [0 for _ in range(6)])
    monitor_yrange_idx: list = field(default_factory=lambda: [0 for _ in range(6)])
    monitor_x_pts: list = field(default_factory=lambda: [100 for _ in range(6)])
    monitor_refresh_rate_idx: list = field(default_factory=lambda: [0 for _ in range(6)])

    # abs scan settings
    abs_data_dir: str = str(TEMP_DIR)
    abs_is_press: bool = False
    abs_sum_mode_idx: int = 0
    abs_is_auto_range_x: bool = True
    abs_is_auto_range_y: bool = True
    abs_is_link_x: bool = True
    abs_is_link_y: bool = True
    abs_f_start: float = 50000.
    abs_f_stop: float = 50000.
    abs_f_center: float = 50000.
    abs_f_range: float = 1.
    abs_f_step: float = 1.
    abs_dwell_time: float = 50
    abs_avg: int = 1
    abs_buffer_len: int = 100
    abs_sens_idx: int = 0
    abs_tau_idx: int = 0
    abs_modu_mode_idx: int = 0
    abs_modu_freq: float = 0.
    abs_modu_amp: float = 0.
    abs_ac_gain: int = 0
    abs_press: float = 1.
    abs_press_tol: float = 1.



@dataclass
class AbsScanSetting:
    """ Absorption scan settings """

    freq_start: float = 0
    freq_stop: float = 0
    freq_step: float = 0
    avg: int = 1
    sens_idx: int = 0
    tau_idx: int = 0
    dwell_time: float = 0
    buffer_len: int = 0
    modu_mode_idx: int = 0
    modu_freq: float = 0
    modu_amp: float = 0
    ac_gain: int = 0
    is_press: bool = True
    press: float = 0
    press_tol: float = 0
