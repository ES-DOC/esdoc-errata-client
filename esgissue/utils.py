#!/usr/bin/env python
"""
   :platform: Unix
   :synopsis: Useful functions to use with esgissue module.

"""

# Module imports
import re
import sys
import logging
import textwrap
from argparse import HelpFormatter
import datetime
import json
import requests
from constants import *
from collections import OrderedDict
import getpass
import ConfigParser
import StringIO
import pyDes
from uuid import getnode as get_mac
import pbkdf2
import platform
import binascii

# Misc operations
from requests.packages.urllib3.exceptions import InsecureRequestWarning, SNIMissingWarning, InsecurePlatformWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
requests.packages.urllib3.disable_warnings(InsecurePlatformWarning)
requests.packages.urllib3.disable_warnings(SNIMissingWarning)


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
        if r.status_code != requests.codes.ok:
            logging.debug('The url {0} is invalid, HTTP response: {1}'.format(url, r.status_code))
        return r.status_code == requests.codes.ok
    except Exception as e:
        logging_error(ERROR_DIC[URLS], url)


def test_pattern(text):
    """
    Tests a regex pattern on a string.

    :param str text: The item as a string
    :returns: True if matched
    :rtype: *boolean*

    """
    pattern = "^[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+#[0-9]{8}$"
    if not re.match(re.compile(pattern), text):
        logging.debug('{0} is malformed'.format(text))
        return False
    else:
        return True


def traverse(l, tree_types=(list, tuple)):
    """
    Iterates through a list of lists and extracts items

    :param list l: The list to parse
    :param tuple tree_types: Iterable types
    :returns: A list of extracted items
    :rtype: *list*

    """
    if isinstance(l, tree_types):
        for item in l:
            for child in traverse(item, tree_types):
                yield child
    else:
        yield l


def get_file_path(path_to_issues, path_to_dsets, uid):
    """
    Based on the user input, this function returns the destination of the issue and datasets' file.
    :param path_to_issues: args.issues
    :param path_to_dsets: args.dsets
    :param uid: the issue's identifier
    :return: path_to_issue, path_to_datasets
    """
    if os.path.isdir(path_to_issues) and os.path.isdir(path_to_dsets):
        path_to_issues = os.path.join(path_to_issues, ISSUE_1+uid+ISSUE_2)
        path_to_dsets = os.path.join(path_to_dsets, DSET_1+uid+DSET_2)
        return path_to_issues, path_to_dsets
    else:
        return path_to_issues, path_to_dsets


# Logging


def init_logging(logdir, level='INFO'):
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


def logging_error(error, additional_data=None):
    """

    :param error: error dic
    :param additional_data: additional information
    :return: logs error
    """
    logging.error(error[1] + ' Error code: {}.'.format(error[0]))
    if additional_data:
        logging.error('Error caused by {}.'.format(additional_data))
    sys.exit(error[0])


def resolve_validation_error_code(message):
    """
    Gives sense to validation error messages by affecting respective codes to them.
    :param message: string of error message
    :return: error code
    """
    for key, value in ERROR_DIC.iteritems():
        if key in message.lower():
            return value

# TXT operations


def get_datasets(dataset_file):
    """Returns test affected  datasets by a given issue from the respective txt file.
    :param dataset_file: txt file
    """
    dsets = list()
    for dset in dataset_file:
        dsets.append(unicode(dset.strip(' \n\r\t')))
    return dsets


# JSON operations


def get_issue(path):
    """reads json file containing issue from path to file.
    :param path: issue json file
    """
    with open(path, 'r') as data_file:
        return json.load(data_file)


def update_json(facets, original_json):
    """
    update self.json with the newly detected facets from dataset ids.
    :param facets: dictionary
    :param original_json: dictionary
    :return: dictionary with new facets detected.
    """
    multiple_facets = ['experiments', 'models', 'variables', 'materials', 'url']
    for key, value in facets.iteritems():
        if key not in original_json:
            if key not in multiple_facets:
                # Case of a single value field like the institute.
                original_json[key] = value.lower()
            else:
                # Case of a field that supports a list.
                original_json[key] = [value.lower()]
        elif key in original_json and key in multiple_facets:
            # This is the case of an attempt to change an extracted facet manually and should not be tolerated.
            # However an error is not raised because this is not the way things should be done.
            pass
            # if value not in original_json[key]:
            #     original_json[key].append(value)
        elif key in original_json and key not in multiple_facets and original_json[key] != value.lower():
            print(original_json[key].lower(), value.lower())
            logging_error(ERROR_DIC['single_entry_field'], 'attempt to insert {} in {}'.format(original_json[key],
                                                                                               str(key)))
    return original_json


def order_json(json_body):
    """
    :param json_body: raw json in dictionary without order
    :return: ordered json dictionary
    """
    index_tuple = ()
    for key, value in INDEX_DICT.iteritems():
        if value in json_body.keys():
            index_tuple += ((value, json_body[value]),)
    return OrderedDict(index_tuple)


# Web Service related operations

def get_ws_call(action, payload, uid, credentials):
    """
    This function builds the url for the outgoing call to the different errata ws.
    :param payload: payload to be posted
    :param action: one of the 4 actions: create, update, close, retrieve
    :param uid: in case of a retrieve call, uid is needed
    :param credentials: username & token
    :return: requests call
    """
    config = get_remote_config()
    if action not in ACTIONS:
        logging.error(ERROR_DIC['unknown_command'][1] + '. Error code: {}'.format(ERROR_DIC['unknown_command'][0]))
        sys.exit(ERROR_DIC['unknown_command'][0])

    # url = URLS_LIST['URL_BASE'] + URLS_LIST[action.upper()]
    url = config.get(WEBSERVICE, URL_BASE)+config.get(WEBSERVICE, action.upper())
    if action in [CREATE, UPDATE]:
        r = requests.post(url, json.dumps(payload), headers=HEADERS, auth=credentials)
    elif action == CLOSE:
        r = requests.post(url + uid + '&status=' + payload, auth=credentials)
    elif action == RETRIEVE:
        r = requests.get(url+uid)
    else:
        r = requests.get(url)
    if r.status_code != requests.codes.ok:
        if r.status_code == 401:
            logging_error(ERROR_DIC['authentication'], 'HTTP CODE: '+str(r.status_code))

        elif r.status_code == 403:
            logging_error(ERROR_DIC['authorization'], 'HTTP CODE: '+str(r.status_code))

        else:
            logging_error(ERROR_DIC['ws_request_failed'], 'HTTP CODE: '+str(r.status_code))
    return r


def extract_facets(dataset_id, project):
    """
    Given a specific project, this function extracts the facets as described in the ini file.
    :param dataset_id: dataset id containing the facets
    :param project: project identifier
    :return: dict
    """
    config = get_remote_config()
    result_dict = dict()
    try:
        regex_str = config.get(project.upper()+'_REGEX', PATTERN)
        pos = config.items(project.upper()+'_POS')
    except KeyError:
        logging_error(ERROR_DIC['project_not_supported'])
    match = re.match(regex_str, dataset_id)
    if match:
        for i in pos:
            if i[0] != '__name__':
                result_dict[i[0]] = match.group(int(i[1])).lower()
    else:
        logging_error(ERROR_DIC['dataset_incoherent'], 'dataset id {} is incoherent with {} DRS structure'.format(
            dataset_id, project))
    return result_dict


def get_remote_config():
    """
    Using github api, this returns config file contents.
    :return: ConfigParser instance with proper configuration
    """
    r = requests.get(GH_FILE_API)
    if r.status_code == 200:
        raw_file = requests.get(r.json()[DOWNLOAD_URL])
        config = ConfigParser.ConfigParser()
        config.readfp(StringIO.StringIO(raw_file.text))
        return config
    else:
        print('GITHUB FILE API IS DOWN.')


def encrypt_with_key(data, passphrase=''):
    """
    method for key-encryption, uses 24 bits keys, adds fillers in case its less.
    :param passphrase: user selected key
    :param data: data to encrypt
    :return: data encrypted, safe to save.
    """
    print('Encrypting {} with {}'.format(data, passphrase))
    if passphrase is None:
        passphrase = ''
    # Generate machine specific key
    key = pbkdf2.PBKDF2(passphrase, platform.machine() + platform.processor() + str(get_mac())).read(24)
    print('HERE IS THE GENERATED KEY {}'.format(key))
    k = pyDes.triple_des(key, pyDes.ECB, pad=None, padmode=pyDes.PAD_PKCS5)
    print('GENERATED ENCRYPTED DATA SIZE: {}'.format(len(k.encrypt(data))))
    return k.encrypt(data)


def decrypt_with_key(data, passphrase=''):
    """
    uses key to decrypt data.
    :param data: data to decrypt
    :param passphrase: key used in encryption
    :return: decrypted data
    """
    if passphrase is None:
        passphrase = ''
    key = pbkdf2.PBKDF2(passphrase, platform.machine() + platform.processor() + str(get_mac())).read(24)
    print('HERE IS THE GENERATED KEY {}'.format(key))
    k = pyDes.triple_des(key, pyDes.ECB, pad=None, padmode=pyDes.PAD_PKCS5)
    # print(len(data))
    # while len(data) < 48:
    #     data += ' '
    print('DATA TO DECRYPT SIZE: {}'.format(len(data)))
    return k.decrypt(data)


def authenticate():
    if os.path.isfile('cred.txt'):
        key = getpass.getpass('Passphrase: ')
        with open('cred.txt', 'rb') as credfile:
            content = credfile.readlines()
            print(len(content))
        username = decrypt_with_key(content[0].split('entry:')[1].replace('\n', ''), key)
        token = decrypt_with_key(content[1].split('entry:')[1], key)
    else:
        username = raw_input('Username: ')
        token = raw_input('Token: ')
        save_cred = raw_input('Would you like to save your credentials for later uses? (y/n): ')
        if save_cred.lower() == 'y':
            key = getpass.getpass('Select passphrase to encrypt credentials, this will log you in from now on: ')
            with open('cred.txt', 'wb') as credfile:
                credfile.write('entry:'+encrypt_with_key(username, key)+'\n')
                credfile.write('entry:'+encrypt_with_key(token, key))
            logging.info('Credentials were successfully saved.')
    return username, token


def reset_passphrase(**kwargs):
    """
    Resets user's pass-phrase used in credentials' encryption
    :param kwargs: oldpass and newpass
    :return: nada
    """
    # check if data exists
    if os.path.isfile('cred.txt'):
        # if yes:
        with open('cred.txt', 'rb') as credfile:
            content = credfile.readlines()
        username = content[0].split('entry:')[1].replace('\n', '')
        token = content[1].split('entry:')[1]
        if kwargs['old_pass'] is not None and kwargs['new_pass'] is not None:
            old_pass = kwargs['old_pass']
            new_pass = kwargs['new_pass']
        else:
            logging.info('Old and new pass-phrases are required, if you forgot yours, use: esgissue credreset')
            old_pass = raw_input('Old Passphrase: ')
            new_pass = raw_input('New Passphrase: ')
        username = decrypt_with_key(username, old_pass)
        token = decrypt_with_key(token, old_pass)
        # Writing new data
        with open('cred.txt', 'wb') as credfile:
            credfile.write('entry:'+encrypt_with_key(username, new_pass)+'\n')
            credfile.write('entry:'+encrypt_with_key(token, new_pass))
        logging.info('Passphrase has been successfully updated.')
    # if no print warning.
    else:
        logging.warn('No credentials file found.')


def reset_credentials():
    """
    resets credentials.
    :return: nada
    """
    if os.path.isfile('cred.txt'):
        os.remove('cred.txt')
        logging.info('Credentials have been successfully reset.')
    else:
        logging.warn('No existing credentials found.')


import difflib
with open('cred.txt', 'rb') as credfile:
    content = credfile.readlines()

username = content[0].split('entry:')[1].replace('\n', '')
token = content[1].split('entry:')[1]
data = '44a1819308d6a804ab614fcfc8261174176c65c7'
# data = 'AtefBN'
passphrase = 'yolo'
key = pbkdf2.PBKDF2(passphrase, platform.machine() + platform.processor() + str(get_mac())).read(24)
k = pyDes.triple_des(key, pyDes.ECB, pad=None, padmode=pyDes.PAD_PKCS5)
data = k.encrypt(data)
print(data, token)
print(token == data)
