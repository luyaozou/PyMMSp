#! encoding = utf-8

""" System configuration files """

import json
from dataclasses import dataclass
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
    mod_mode_idx: int = 0
    mod_freq: float = 0
    mod_depth: float = 0
    press: float = 0
    press_tol: float = 0
