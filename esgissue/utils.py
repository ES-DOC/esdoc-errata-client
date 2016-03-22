#!/usr/bin/env python
"""
   :platform: Unix
   :synopsis: Useful functions to use with esgissue module.

"""

# Module imports
import os
import re
import requests
import logging
import sys
import ConfigParser


class DictDiff(object):
    """
    Calculates the difference between two dictionaries as:
     * items added,
     * items removed,
     * changed key-value pairs,
     * unchanged key-value pairs.

    """
    def __init__(self, new_dict, old_dict):
        self.new_dict, self.old_dict = new_dict, old_dict
        self.new_keys, self.old_keys = [
            set(d.keys()) for d in (new_dict, old_dict)
        ]
        self.intersect = self.new_keys.intersection(self.old_keys)

    def added(self):
        return self.new_keys.difference(self.intersect)

    def removed(self):
        return self.old_keys.difference(self.intersect)

    def changed(self):
        return set(item for item in self.intersect
                   if self.old_dict[item] != self.new_dict[item])

    def unchanged(self):
        return set(item for item in self.intersect
                   if self.old_dict[item] == self.new_dict[item])


class ListDiff(object):
    """
    Calculates the difference between two lists as:
     * items added,
     * items removed.

    """
    def __init__(self, new_list, old_list):
        self.new_list, self.old_list = set(new_list), set(old_list)
        self.intersect = self.new_list.intersection(self.old_list)

    def added(self):
        return self.new_list.difference(self.intersect)

    def removed(self):
        return self.old_list.difference(self.intersect)


def config_parse(config_path):
    """
    Parses the configuration file if exists. Tests if required options are declared.

    :param str config_path: The absolute or relative path of the configuration file
    :returns: The configuration file parser
    :rtype: *dict*
    :raises Error: If no configuration file exists
    :raises Error: If the configuration file parsing fails

    """
    if not os.path.isfile(config_path):
        raise Exception('Configuration file not found')
    cfg = ConfigParser.ConfigParser()
    cfg.read(config_path)
    if not cfg:
        raise Exception('Configuration file parsing failed')
    if not cfg.has_section('BITBUCKET'):
        raise Exception('No "[BITBUCKET]" section found in "{0}"'.format(config_path))
    for option in ['bb_login', 'bb_password', 'bb_team', 'bb_repo']:
        if not cfg.has_option('BITBUCKET', option):
            raise Exception('"{0}" option is missing in "{1}"'.format(option, config_path))
    return cfg


def test_url(url):
    """
    Tests an url response.

    :param str url: The url to test
    :returns: True if the url exists
    :rtype: *boolean*
    :raises Error: If an HTTP request fails

    """
    try:
        r = requests.head(url)
        return r.status_code == requests.codes.ok
    except:
        logging.warning('Registration: FAIL')
        logging.exception('Cannot reach URL: {0}'.format(url))
        sys.exit(1)


def test_pattern(item):
    """
    Tests a regex pattern on each item list.

    :param str item: The item as a string
    :returns: True if matched, the item itself if not
    :rtype: *boolean* or *str*

    """
    pattern = "^[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+#[0-9]{8}$"
    if not re.match(re.compile(pattern), item):
        logging.warning('{0} has invalid format'.format(item))
        return False
    else:
        return True
