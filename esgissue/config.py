import os
import json


def _get_config_fpath(config_path):
    """
    returns configuration file path
    """
    fpath = os.path.dirname(os.path.abspath(__file__))
    fpath = os.path.join(fpath, config_path)
    if os.path.exists(fpath):
        return fpath
    else:
        err = "ESDOC-ERRATA CLIENT configuration file ({0}) could not be found".format(config_path)


def _get_config_contents():
    """
    returns configuration file contents.
    """
    with open(_get_config_fpath('conf.json')) as cf:
        return json.load(cf)
