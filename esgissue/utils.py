#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
   :platform: Unix
   :synopsis: Useful functions to use with esgissue module.

"""

# Module imports
import os
import re
import sys
import logging
import textwrap
import pbkdf2
import platform
import datetime
import json
import requests
import getpass
import StringIO
import pyDes

from argparse import HelpFormatter
from constants import *
from collections import OrderedDict
from uuid import getnode as get_mac
from time import time
from fnmatch import fnmatch
from ConfigParser import ConfigParser
from config import _get_config_contents

# # SNI required fix for py2.7
# from requests.packages.urllib3.contrib import pyopenssl
# pyopenssl.inject_into_urllib3()
cf = _get_config_contents()
class MultilineFormatter(HelpFormatter):
    """
    Custom formatter class for argument parser to use with the Python
    `argparse <https://docs.python.org/2/library/argparse.ht__JSON_SCHEMA_PATHS__ml>`_ module.

    """
    def __init__(self, prog):
        # Overload the HelpFormatter class.
        super(MultilineFormatter, self).__init__(prog, max_help_position=60, width=100)

    def _fill_text(self, text, width, indent):
        # Rewrites the _fill_text method to support multiline description.
        text = self._whitespace_matcher.sub(' ', text).strip()
        multiline_text = ''
        paragraphs = text.split('|n|n ')
        for paragraph in paragraphs:
            lines = paragraph.split('|n ')
            for line in lines:
                formatted_line = textwrap.fill(line, width,
                                               initial_indent=indent,
                                               subsequent_indent=indent) + '\n'
                multiline_text += formatted_line
            multiline_text += '\n'
        return multiline_text

    def _split_lines(self, text, width):
        # Rewrites the _split_lines method to support multiline helps.
        text = self._whitespace_matcher.sub(' ', text).strip()
        lines = text.split('|n ')
        multiline_text = []
        for line in lines:
            multiline_text.append(textwrap.fill(line, width))
        multiline_text[-1] += '\n'
        return multiline_text

# Validation


def _test_url(url):
    """
    Tests an url response.

    :param str url: The url to test
    :returns: True if the url exists
    :rtype: *boolean*
    :raises Error: If an HTTP request fails

    """
    try:
        r = requests.head(str(url))
        if not r.ok:
            logging.debug('The url {0} is invalid, HTTP response: {1}'.format(url, r.status_code))
        return r.ok
    except Exception as e:
        _logging_error('Return code {}'.format(r.status_code), url)
        _logging_error(ERROR_DIC[URLS], url)


def _test_pattern(text, pattern):
    """
    Tests a regex pattern on a string.

    :param str text: The item as a string
    :returns: True if matched
    :rtype: *boolean*

    """
    if not re.match(re.compile(pattern), text):
        _logging_error(ERROR_DIC['malformed_dataset_id'], additional_data=text)
        return False
    else:
        return True


def _traverse(l, tree_types=(list, tuple)):
    """
    Iterates through a list of lists and extracts items

    :param list l: The list to parse
    :param tuple tree_types: Iterable types
    :returns: A list of extracted items
    :rtype: *list*

    """
    if isinstance(l, tree_types):
        for item in l:
            for child in _traverse(item, tree_types):
                yield child
    else:
        yield l


def _get_file_location(file_name, download_dir=None):
    """
    Tests whether ESDOC_HOME variable is declared in user environment, uses it as directory base if it's the case.
    :param file_name:
    :param download_dir:
    :return:
    """
    file_location = get_target_path(target='')
    if download_dir is not None:
        file_location += download_dir
    file_location = os.path.join(file_location, file_name)
    if not os.path.isdir(os.path.dirname(file_location)):
        os.makedirs(os.path.dirname(file_location))
    return file_location

# Logging


def _init_logging(logdir=None, level='INFO'):
    """
    Initiates the logging configuration (output, message formatting).
    In the case of a logfile, the logfile name is unique and formatted as follows:
    ``name-YYYYMMDD-HHMMSS-JOBID.log``

    :param str logdir: The relative or absolute logfile directory. If ``None`` the standard output is used.
    :param str level: The log level.

    """
    __LOG_LEVELS__ = {'CRITICAL': logging.CRITICAL,
                      'ERROR': logging.ERROR,
                      'WARNING': logging.WARNING,
                      'INFO': logging.INFO,
                      'DEBUG': logging.DEBUG,
                      'NOTSET': logging.NOTSET}
    logging.getLogger("requests").setLevel(logging.CRITICAL)  # Disables logging message from request library
    if logdir:
        logfile = 'esgissue-{0}-{1}.log'.format(datetime.datetime.now().strftime("%Y%m%d-%H%M%S"), os.getpid())
        if not os.path.isdir(logdir):
            os.makedirs(logdir)
        logging.basicConfig(filename=os.path.join(logdir, logfile),
                            level=__LOG_LEVELS__[level],
                            format='%(asctime)s %(levelname)s %(message)s',
                            datefmt='%Y/%m/%d %I:%M:%S %p')
    else:
        logging.basicConfig(level=__LOG_LEVELS__[level],
                            format='%(asctime)s %(levelname)s %(message)s',
                            datefmt='%Y/%m/%d %I:%M:%S %p')


def _logging_error(error, additional_data=None):
    """

    :param error: error dic
    :param additional_data: additional information
    :return: logs error
    """
    if error is not None:
        logging.error(str(error[1]) + ' Error code: {}.'.format(str(error[0])))
        if additional_data:
            logging.error('Error caused by {}.'.format(str(additional_data)))
        sys.exit(error[1])


def _resolve_validation_error_code(message):
    """
    Gives sense to validation error messages by affecting respective codes to them.
    :param message: string of error message
    :return: error code
    """
    for key, value in ERROR_DIC.iteritems():
        if key in message.lower():
            return value
    return ERROR_DIC['unknown_error']

# Preparing operations


def _resolve_status(status):
    """
    resolves user input for status when closing.
    :param status: user input
    :return: status
    """
    if status not in ['r', 'R', 'w', 'W', STATUS_WONTFIX, STATUS_RESOLVED]:
        _logging_error(ERROR_DIC[STATUS])
    else:
        if status in ['r', 'R', STATUS_RESOLVED]:
            return STATUS_RESOLVED
        else:
            return STATUS_WONTFIX


def _prepare_retrieve_ids(id_list):
    """
    Parses retrieval arguments, resolves directories
    :param id_list: list of ids
    :return: List of ids
    """
    logging.info('Processing requested issue id list...')
    # Case the user specified that he wants a specific issue with a specific uid.
    if id_list is None:
        list_of_ids = []
    elif len(id_list) > 0:
        list_of_ids = id_list
    return list_of_ids


def _prepare_retrieve_dirs(issues, dsets, list_of_ids):
    """
    :param issues: user input for issues files.
    :param dsets: user input for dsets files.
    :param list_of_ids: list of requested issues.
    :return:
    """
    logging.info('Processing requested download directories...')
    if len(list_of_ids) == 1:
        pass
    else:
        for directory in [issues, dsets]:
            if fnmatch(directory, '*.*'):
                _logging_error(ERROR_DIC['multiple_ids'])
    return issues, dsets


def get_target_path(target=None):
    """
    :param target can be a filename or a directory
    returns
    """
    if os.environ.get(ESDOC_HOME) is not None:
        return os.path.join(os.environ.get(ESDOC_HOME), target)
    else:
        return os.path.join('{}/.esdoc/errata'.format(os.getenv('HOME')), target)


def _get_retrieve_dirs(path_to_issues, path_to_dsets, uid):
    """
    Based on the user input, this function returns the destination of the issue and datasets' file.
    :param path_to_issues: args.issues
    :param path_to_dsets: args.dsets
    :param uid: the issue's identifier
    :return: path_to_issue, path_to_datasets
    """
    if path_to_dsets is None and path_to_dsets is None:
        path_to_dsets = ''
        path_to_issues = ''
        download_dir_i = get_target_path('issue_dw')
        download_dir_d = get_target_path('dsets_dw')
    elif path_to_issues == '.' and path_to_dsets == '.':
        path_to_issues = ''
        path_to_dsets = ''
        download_dir_i = get_target_path('issue_dw')
        download_dir_d = get_target_path('dsets_dw')
    elif path_to_issues is None or path_to_dsets is None:
        path_to_dsets = ''
        path_to_issues = ''
        download_dir_i = os.path.join(os.getcwd(), 'issue_dw')
        download_dir_d = os.path.join(os.getcwd(), 'dsets_dw')
    elif path_to_issues is not None and path_to_dsets is not None:
        download_dir_i = os.path.abspath(path_to_issues)
        download_dir_d = os.path.abspath(path_to_dsets)
        path_to_dsets = ''
        path_to_issues = ''
    if not os.path.isdir(download_dir_i):
        os.makedirs(download_dir_i)
    if not os.path.isdir(download_dir_d):
        os.makedirs(download_dir_d)
    if os.path.isdir(os.path.join(download_dir_i, path_to_issues)) and os.path.isdir(os.path.join(download_dir_d,
                                                                                                  path_to_dsets)):
        path_to_issues = os.path.join(download_dir_i, ISSUE_1+uid+ISSUE_2)
        path_to_dsets = os.path.join(download_dir_d, path_to_dsets, DSET_1+uid+DSET_2)
    else:
        path_to_issues = os.path.join(_get_file_location(path_to_issues, download_dir='downloads'), ISSUE_1 + uid +
                                      ISSUE_2)
        path_to_dsets = os.path.join(_get_file_location(path_to_dsets, download_dir='downloads'), DSET_1 + uid + DSET_2)
    return path_to_issues, path_to_dsets


def _prepare_persistence(data):
    """
    prepares downloaded data for persistence
    :param data: json file
    :return: json file
    """
    to_del = []
    for key, value in data.iteritems():
        if value is None or value == '' or value == [] or value == [u'']:
            to_del.append(key)
        if type(value) == list:
            for item in value:
                if item == '' or item == u"":
                    value.remove(item)
            if not value:
                to_del.append(key)

    for key in to_del:
        if key in data:
            del data[key]
    return data

# TXT operations


def _test_datasets_for_version_and_empty(datasets):
    """
    of a list of datasets, this function tests empty list and version number
    :param datasets: list of dataset id as strings
    :returns dataset_version_dict: dictionary containing dataset id as key and version as value stripped from .v or #
    """
    # Testing for empty list
    logging.info('Pre-validating dataset list...')
    if datasets is None or len(datasets) == 0:
        _logging_error(ERROR_DIC['empty_dset_list'])
        sys.exit(1)
    # Testing for version number and preparing dataset:version dictionary
    dataset_version_dict = dict()
    dataset_index = 0
    for dset in datasets:
        if re.search(VERSION_REGEX, dset) is None:
            _logging_error(ERROR_DIC['malformed_dataset_id'], additional_data=dset)
            sys.exit(1)
        else:
            match = re.search(VERSION_REGEX, dset)
            version_string = match.group('version_string')
            # Remove the found version string from the dataset id.
            dset = dset.replace(version_string, '')
            if '.v' in version_string:
                version_string = version_string.replace('.v', '')
            else:
                version_string = version_string.replace('#', '')
            dataset_version_dict[dataset_index] = (dset, version_string)
            dataset_index += 1
    # Making sure the dataset list elements are unique.
    datasets = list(set(dataset_version_dict.values()))
    dataset_version_dict = dict()
    real_idx = 0
    for dset_and_ver in datasets:
        dataset_version_dict[real_idx] = dset_and_ver
        real_idx += 1
    logging.info('Pre-validated dataset list successfully.')
    return dataset_version_dict


def _format_datasets(dataset_version_dict, dset_file):
    """
    After dataset_id extraction and validation (using the appropriate project ini file), the ids need to be formatted to
    meet the errata system expectations in notation.
    This was separated from the pre-validation workflow in order to maximize compliance with different projects ini
    files.
    :param dataset_version_dict: dataset list
    :param dset_file: path to the local datasets file.
    :return: modified txt file.
    """
    logging.info('Reformatting dataset file...')
    uniform_list = list()
    for dset_and_version in dataset_version_dict.values():
        uniform_list.append(dset_and_version[0]+'#'+dset_and_version[1])
    uniform_list = list(set(uniform_list))
    with open(dset_file.name, 'w+') as df:
        try:
            logging.info('Rearranging dataset file (removing duplicates and updating version format)...')
            for dset in uniform_list:
                df.write(dset + '\n')
            logging.info('Local dataset file rearranged.')
        except Exception as e:
            print(e.message)
    logging.info('Dataset file reformatted, changes persisted locally.')
    return uniform_list


def _get_datasets(dataset_file):
    """Returns test affected  datasets by a given issue from the respective txt file.
    :param dataset_file: txt file
    """
    dsets = list()
    for dset in dataset_file:
        dsets.append(unicode(dset.strip(' \n\r\t')))
    # Removing redundancy
    dsets = list(set(dsets))
    return dsets

# JSON operations


def _get_issue(path):
    """reads json file containing issue from path to file.
    :param path: issue json file
    """
    try:
        with open(path, 'r') as data_file:
            return json.load(data_file)
    except ValueError as ve:
        logging.error('json file is malformed, check the commas.')
        logging.error(ve.message)
        sys.exit(1)


def _order_json(json_body):
    """
    :param json_body: raw json in dictionary without order
    :return: ordered json dictionary
    """
    index_tuple = ()
    for key, value in INDEX_DICT.iteritems():
        if value in json_body.keys():
            index_tuple += ((value, json_body[value]),)
    return OrderedDict(index_tuple)


# WS OPS

def _get_ws_call(action, payload=None, uid=None, credentials=None):
    """
    This function builds the url for the outgoing call to the different errata ws.
    :param payload: payload to be posted
    :param action: one of the 4 actions: create, update, close, retrieve
    :param uid: in case of a retrieve call, uid is needed
    :param credentials: username & token
    :return: requests call
    """
    if action not in ACTIONS:
        logging.error(ERROR_DIC['unknown_command'][1] + '. Error code: {}'.format(ERROR_DIC['unknown_command'][0]))
        sys.exit(ERROR_DIC['unknown_command'][0])
    url = cf['url_base'] + cf['api_map'][action.upper()]
    # Checking if the errata ws server is up.
    _check_ws_heartbeat()
    if action in [CREATE, UPDATE]:
        try:
            r = requests.post(url, json.dumps(payload), headers=HEADERS, auth=credentials)
        except Exception as e:
            print(e.message)
    elif action == CLOSE:
        r = requests.post(url + uid + '&status=' + payload, auth=credentials)
    elif action == RETRIEVE:
        r = requests.get(url+uid)
    elif action == CREDTEST:
        r = requests.get(url.format(credentials[0], credentials[1], payload['team'], payload['project']))
    else:
        r = requests.get(url)
    if r.status_code != requests.codes.ok:
        try:
            error_json = json.loads(r.text)
            if r.status_code == 401:
                _logging_error(ERROR_DIC['authentication'])
            elif r.status_code == 403:
                _logging_error(ERROR_DIC['authorization'])
            _logging_error([error_json['errorMessage'], error_json['errorCode']], error_json['errorType'])
        except Exception:
            _logging_error(ERROR_DIC['unknown_command'], str(r.status_code))
    return r


def _check_ws_heartbeat():
    """
    checks whether the configured errata ws server is up
    :return: raises exception if down.
    """
    r = requests.get(cf['url_base'])
    if r.status_code != 200:
        sys.exit(ERROR_DIC['server_down'][0])
    else:
        return


def _translate_dataset_regex(pattern, sections):
    """
    translates the regex expression retrieved from esg.ini
    :param pattern: str
    :param sections: dictionary of configuration
    :return: pattern
    """
    facets = set(re.findall(re.compile(r'%\(([^()]*)\)s'), pattern))
    for facet in facets:
        # If a facet has a specific pattern to follow.
        if '{}_pattern'.format(facet) in sections.keys():
            pattern = re.sub(re.compile(r'%\(({0})\)s'.format(facet)), sections['{}_pattern'.format(facet)], pattern)
        # version:
        elif facet == 'version':
            pattern = re.sub(re.compile(r'%\((version)\)s'), r'(?P<\1>v[\d]+|latest)', pattern)
        # Rest of facets:
        else:
            pattern = re.sub(re.compile(r'%\(([^()]*)\)s'), r'(?P<\1>[\w-]+)', pattern)
    return pattern

# Credentials management tools.

def _get_credentials(list_of_args):
    """
    checks whether a passphrase has been passed in options or not.
    :param list_of_args: kwargs
    """
    if 'passphrase' in list_of_args:
        return _authenticate(passphrase=list_of_args['passphrase'])
    else:
        return _authenticate()


def _encrypt_with_key(data, passphrase=''):
    """
    method for key-encryption, uses 24 bits keys, adds fillers in case its less.
    :param passphrase: user selected key
    :param data: data to encrypt
    :return: data encrypted, safe to save.
    """
    if passphrase is None:
        passphrase = ''
    if passphrase != '':
        key = pbkdf2.PBKDF2(passphrase, "\0\0\0\0\0\0\0\0").read(24)
        k = pyDes.triple_des(key, pyDes.ECB, pad=None, padmode=pyDes.PAD_PKCS5)
        return k.encrypt(data).encode('string_escape').replace('\\\\', '\\')
    else:
        return data


def _decrypt_with_key(data, passphrase=''):
    """
    uses key to decrypt data.
    :param data: data to decrypt
    :param passphrase: key used in encryption
    :return: decrypted data
    """
    data = data.decode('string_escape').replace('\\', '\\\\')
    if passphrase is None:
        passphrase = ''
    if passphrase != '':
        key = pbkdf2.PBKDF2(passphrase, "\0\0\0\0\0\0\0\0").read(24)
        k = pyDes.triple_des(key, pyDes.ECB, pad=None, padmode=pyDes.PAD_PKCS5)
        return k.decrypt(data)
    else:
        return data


def _authenticate(**kwargs):
    if os.environ.get(GITHUB_TOKEN) is not None and os.environ.get(GITHUB_USERNAME) is not None:
        token = os.environ.get(GITHUB_TOKEN)
        username = os.environ.get(GITHUB_USERNAME)
        if os.environ.get(GITHUB_CREDS_ENCRYPTED) is not None:
            if str(os.environ.get(GITHUB_CREDS_ENCRYPTED)) == '1':
                passphrase = getpass.getpass('Passphrase: ')
                token = _decrypt_with_key(token, passphrase)
                username = _decrypt_with_key(username, passphrase)
        return username, token
    else:
        path_to_creds = _get_file_location('cred.txt')
        if os.path.isfile(path_to_creds) and os.path.getsize(path_to_creds) > 0:
            with open(path_to_creds, 'r') as credfile:
                content = credfile.readlines()
                enc_username = content[0].split('entry:')[1].replace('\n', '')
                enc_token = content[1].split('entry:')[1].replace('\n', '')
                is_encrypted = content[2].split('entry:')[1]

            if is_encrypted == "1":
                if 'passphrase' in kwargs and kwargs['passphrase'] is not None:
                    key = kwargs['passphrase']
                else:
                    key = getpass.getpass('Passphrase: ')
                token = _decrypt_with_key(enc_token, key)
                username = _decrypt_with_key(enc_username, key)
            else:
                username = enc_username
                token = enc_token
        else:
            username = raw_input('Username: ')
            token = raw_input('Token: ')
            save_cred = raw_input('Would you like to save your credentials for later uses? (y/n): ')
            if save_cred.lower() == 'y':
                key = getpass.getpass('Select passphrase to encrypt credentials, this will log you in from now on: ')
                with open(path_to_creds, 'wb+') as credfile:
                    if key != '':
                        credfile.write('entry:'+_encrypt_with_key(username, key)+'\n')
                        credfile.write('entry:'+_encrypt_with_key(token, key)+'\n')
                        credfile.write('entry:'+'1')
                    else:
                        credfile.write('entry:'+username+'\n')
                        credfile.write('entry:'+token+'\n')
                        credfile.write('entry:'+'0')
                logging.info('Credentials were successfully saved.')
    return username, token


def _reset_passphrase(**kwargs):
    """
    Resets user's pass-phrase used in credentials' encryption
    :param kwargs: oldpass and newpass
    :return: nada
    """
    # check if data exists
    if os.environ.get(GITHUB_CREDS_ENCRYPTED):
        # if yes:
        is_encrypted = '1'
        username = os.environ.get(GITHUB_USERNAME)
        token = os.environ.get(GITHUB_TOKEN)
    path_to_creds = _get_file_location('cred.txt')
    if os.path.isfile(path_to_creds) and os.path.getsize(path_to_creds) > 0:
        # if yes:
        with open(path_to_creds, 'rb') as cred_file:
            content = cred_file.readlines()
        username = content[0].split('entry:')[1].replace('\n', '')
        token = content[1].split('entry:')[1].replace('\n', '')
        is_encrypted = content[2].split('entry:')[1]
    if username is None or token is None:
        logging.warn('No credentials found.')
    if 'old_pass' in kwargs and 'new_pass' in kwargs:
        logging.info('Using new credentials from user input...')
        old_pass = kwargs['old_pass']
        new_pass = kwargs['new_pass']
    else:
        logging.info('Old and new pass-phrases are required, if you forgot yours, use: esgissue credremove')
        old_pass = ''
        if is_encrypted == '0':
            pass
        else:
            old_pass = getpass.getpass('Old Passphrase: ')
        new_pass = getpass.getpass('New Passphrase: ')
    username = _decrypt_with_key(username, old_pass)
    token = _decrypt_with_key(token, old_pass)
    # Writing new data
    os.environ[GITHUB_USERNAME] = _encrypt_with_key(username, new_pass)
    os.environ[GITHUB_TOKEN] = _encrypt_with_key(token, new_pass)
    # Writing new data
    with open(path_to_creds, 'wb') as cred_file:
        if new_pass != '':
            cred_file.write('entry:'+_encrypt_with_key(username, new_pass)+'\n')
            cred_file.write('entry:'+_encrypt_with_key(token, new_pass)+'\n')
            cred_file.write('entry:'+'1')
        else:
            cred_file.write('entry:'+username+'\n')
            cred_file.write('entry:'+token+'\n')
            cred_file.write('entry:'+'0')
    logging.info('Passphrase has been successfully updated.')


def _reset_credentials():
    """
    resets credentials.
    :return: nada
    """
    path_to_creds = _get_file_location('cred.txt')
    if os.path.isfile(path_to_creds):
        os.remove(path_to_creds)
        logging.info('Credentials have been successfully reset.')
    else:
        logging.warn('No existing credentials found.')


def _set_credentials(**kwargs):
    """
    set credentials
    :return: nada
    """
    if 'username' in kwargs and 'token' in kwargs:
        logging.info('Using token found in user input...')
        logging.info('Using credentials found in user input...')
        username = kwargs['username']
        tkn = kwargs['token']
        if 'passphrase' in kwargs:
            passphrase = kwargs['passphrase']
        else:
            passphrase = ''
    else:
        username = raw_input('Username: ')
        tkn = raw_input('Token: ')
        passphrase = getpass.getpass('Passphrase: ')
        if passphrase != '' and passphrase is not None:
            os.environ[GITHUB_CREDS_ENCRYPTED] = '1'
            os.environ[GITHUB_USERNAME] = _encrypt_with_key(username, passphrase)
            os.environ[GITHUB_TOKEN] = _encrypt_with_key(tkn, passphrase)
        else:
            os.environ[GITHUB_CREDS_ENCRYPTED] = '0'
            os.environ[GITHUB_USERNAME] = username
            os.environ[GITHUB_TOKEN] = tkn

    path_to_creds = _get_file_location('cred.txt')
    if os.path.isfile(path_to_creds):
        logging.info('Older credentials file was found, resetting...')
        _reset_credentials()
    with open(path_to_creds, 'wb') as cred_file:
        if passphrase != '':
            cred_file.write('entry:'+_encrypt_with_key(username, passphrase)+'\n')
            cred_file.write('entry:'+_encrypt_with_key(tkn, passphrase)+'\n')
            cred_file.write('entry:'+'1')
        else:
            cred_file.write('entry:'+username+'\n')
            cred_file.write('entry:'+tkn+'\n')
            cred_file.write('entry:'+'0')
    logging.info('Your credentials were successfully set.')


def _cred_test(team=None, project=None, passphrase=None):
    """
    Test credentials validity.
    :return:
    """
    while not team:
        team = raw_input('Please specify the institute you wish to test authorization to: ')
    while not project:
        project = raw_input('Please specify the project you wish to test authorization to: ')
    credentials = _authenticate(passphrase=passphrase)
    _get_ws_call('credtest', uid=None, credentials=credentials, payload={'team': team.lower(),
                                                                         'project': project.lower()})
    logging.info('HTTP CODE 200: User allowed to post issues related to institute {}'.format(team))
