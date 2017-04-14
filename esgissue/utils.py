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
from time import time
from fnmatch import fnmatch

# SNI required fix for py2.7
from requests.packages.urllib3.contrib import pyopenssl
pyopenssl.inject_into_urllib3()


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
        elif r.status_code == 301:
            logging.warn('Provided URL {} has redirects, please replace it with proper URL.'.format(url))
        return r.status_code == requests.codes.ok
    except Exception as e:
        logging_error('Return code {}'.format(r.status_code), url)
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
    else:
        path_to_issues = os.path.join(get_file_location(path_to_issues, download_dir='downloads'), ISSUE_1+uid+ISSUE_2)
        path_to_dsets = os.path.join(get_file_location(path_to_dsets, download_dir='downloads'), DSET_1+uid+DSET_2)
    return path_to_issues, path_to_dsets


def get_file_location(file_name, download_dir=None):
    """
    Tests whether ESDOC_HOME variable is declared in user environment, uses it as directory base if it's the case.
    :param file_name:
    :param download_dir:
    :return:
    """
    if ESDOC_VAR in os.environ.keys():
        file_location = os.path.join(os.environ['ESDOC_HOME'], '.esdoc/errata/')
        if download_dir is not None:
            file_location += download_dir
        file_location = os.path.join(file_location, file_name)
        if not os.path.isdir(file_location) and not os.path.isfile(file_location):
            os.makedirs(file_location)
        return file_location

    else:
        logging.warn('ESDOC_HOME environment variable is not defined, using installation location for files')
        fpath = 'cred.txt'
    return fpath


# Logging


def init_logging(logdir=None, level='INFO'):
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
    if error is not None:
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

# Preparing operations


def resolve_status(status):
    """
    resolves user input for status when closing.
    :param status: user input
    :return: status
    """
    if status not in ['r', 'R', 'w', 'W', STATUS_WONTFIX, STATUS_RESOLVED]:
        logging_error(ERROR_DIC[STATUS])
    else:
        if status in ['r', 'R', STATUS_RESOLVED]:
            return STATUS_RESOLVED
        else:
            return STATUS_WONTFIX


def prepare_retrieve_ids(id_list):
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


def prepare_retrieve_dirs(issues, dsets, list_of_ids):
    """
    :param issues: user input for issues files.
    :param dsets: user input for dsets files.
    :param list_of_ids: list of requested issues.
    :return:
    """
    logging.info('Processing requested download directories...')
    if len(list_of_ids) == 1:
        for directory in [issues, dsets]:
            if not fnmatch(directory, '*.*'):
                if not os.path.isdir(directory):
                    os.makedirs(directory)
    else:
        for directory in [issues, dsets]:
            if fnmatch(directory, '*.*'):
                logging_error(ERROR_DIC['multiple_ids'])
            else:
                if not os.path.isdir(directory):
                    os.makedirs(directory)
    return issues, dsets


def prepare_persistence(data):
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
    multiple_facets = ['experiment_id', 'source_id', 'variable_id']
    allowed_facets = ['mip_era', 'activity_id', 'source_id', 'variable_id', 'institution_id', 'experiment_id']
    for key, value in facets.iteritems():
        if key not in original_json and key in allowed_facets:
            if key not in multiple_facets:
                # Case of a single value field like the institute.
                original_json[key] = value.lower()
            else:
                # Case of a field that supports a list.
                original_json[key] = [value.lower()]
        elif key in original_json and key in multiple_facets:
            # This is the case of an attempt to change an extracted facet manually and should not be tolerated.
            # However an error is not raised because this is not the way things should be done.
            # pass
            if value not in original_json[key]:
                original_json[key].append(value)
        elif key in original_json and key not in multiple_facets and original_json[key] != value.lower():
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

def get_ws_call(action, payload=None, uid=None, credentials=None):
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
    url = URL_BASE + URL_MAP[action.upper()]
    if action in [CREATE, UPDATE]:
        try:
            r = requests.post(url, json.dumps(payload), headers=HEADERS, auth=credentials)
        except Exception as e:
            print(e.message)
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


def extract_facets(dataset_id, project, config):
    """
    Given a specific project, this function extracts the facets as described in the ini file.
    :param dataset_id: dataset id containing the facets
    :param project: project identifier
    :return: dict
    """
    try:
        sections = config._sections['project:{}'.format(project)]
        regex_str = sections[DATASET_ID]
        regex_str = translate_dataset_regex(regex_str, sections)
        match = re.match(regex_str, dataset_id)
        if match:
            logging.info('Extracting facets...')
            return match_facets_to_cmip6(match.groupdict())
        else:
            logging_error(ERROR_DIC['dataset_incoherent'], 'dataset id {} is incoherent with {} DRS structure'.format(
                dataset_id, project))
    except KeyError:
        logging_error(ERROR_DIC['project_not_supported'])


def match_facets_to_cmip6(input_dict):
    matching_dict = {'project': 'mip_era', 'institute': 'institution_id', 'model': 'source_id',
                     'variable': 'variable_id', 'experiment': 'experiment_id', 'activity': 'activity_id',
                     'ensemble': 'member_id', 'product': 'product',
                     'ensemble_member': 'variant_label', 'version': 'version', 'frequency': 'frequency',
                     'modeling_realm': 'realm', 'cmor_table': 'table_id', 'grid_label': 'grid_label'}
    output_dict = dict()
    for key, value in input_dict.iteritems():
        output_dict[matching_dict[key]] = input_dict[key]
    return output_dict


def translate_dataset_regex(pattern, sections):
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


def get_remote_config(project):
    """
    Using github api, this returns config file contents.
    :param project: str
    :return: ConfigParser instance with proper configuration
    """
    project_ini_file = '{}.ini'.format(project)
    config = ConfigParser.ConfigParser()
    if os.path.isfile(project_ini_file) and (time()-os.path.getmtime(project_ini_file))/60 < FILE_EXPIRATION_TIME:
        # Reading local file.
        logging.info('RECENT PROJECT CONFIGURATION FILE FOUND LOCALLY. READING...')
        config.read(project_ini_file)
        return config
    else:
        r = requests.get(GH_FILE_API.format(project))
        if r.status_code == 200:
            logging.info('NO LOCAL PROJECT CONFIG FILE FOUND OR DEPRECATED FILE FOUND, RETRIEVING FROM REPO...')
            # Retrieving distant configuration file
            raw_file = requests.get(r.json()[DOWNLOAD_URL])
            config.readfp(StringIO.StringIO(raw_file.text))
            logging.info('FILE RETRIEVED, PERSISTING LOCALLY...')
            # Keeping local copy
            with open(project_ini_file, 'w') as project_file:
                config.write(project_file)
            logging.info('FILE PERSISTED.')
            return config
        else:
            raise Exception('CONFIG FILE NOT FOUND {}.'.format(r.status_code))


def encrypt_with_key(data, passphrase=''):
    """
    method for key-encryption, uses 24 bits keys, adds fillers in case its less.
    :param passphrase: user selected key
    :param data: data to encrypt
    :return: data encrypted, safe to save.
    """
    if passphrase is None:
        passphrase = ''
    # Generate machine specific key
    key = pbkdf2.PBKDF2(passphrase, platform.machine() + platform.processor() + str(get_mac())).read(24)
    k = pyDes.triple_des(key, pyDes.ECB, pad=None, padmode=pyDes.PAD_PKCS5)
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
    k = pyDes.triple_des(key, pyDes.ECB, pad=None, padmode=pyDes.PAD_PKCS5)
    return k.decrypt(data)


def authenticate(**kwargs):
    path_to_creds = get_file_location('cred.txt')
    if os.path.isfile(path_to_creds):
        if 'passphrase' in kwargs:
            key = kwargs['passphrase']
        else:
            key = getpass.getpass('Passphrase: ')
        with open(path_to_creds, 'rb') as credfile:
            content = credfile.readlines()
        username = decrypt_with_key(content[0].split('entry:')[1].replace('\n', ''), key)
        token = decrypt_with_key(content[1].split('entry:')[1], key)
    else:
        username = raw_input('Username: ')
        token = raw_input('Token: ')
        save_cred = raw_input('Would you like to save your credentials for later uses? (y/n): ')
        if save_cred.lower() == 'y':
            key = getpass.getpass('Select passphrase to encrypt credentials, this will log you in from now on: ')
            with open(path_to_creds, 'wb') as credfile:
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
    path_to_creds = get_file_location('cred.txt')
    if os.path.isfile(path_to_creds):
        # if yes:
        with open(path_to_creds, 'rb') as cred_file:
            content = cred_file.readlines()
        username = content[0].split('entry:')[1].replace('\n', '')
        token = content[1].split('entry:')[1]
        if 'old_pass' in kwargs and 'new_pass' in kwargs:
            logging.info('Using new credentials from user input...')
            old_pass = kwargs['old_pass']
            new_pass = kwargs['new_pass']
        else:
            logging.info('Old and new pass-phrases are required, if you forgot yours, use: esgissue credreset')
            old_pass = getpass.getpass('Old Passphrase: ')
            new_pass = getpass.getpass('New Passphrase: ')
        username = decrypt_with_key(username, old_pass)
        token = decrypt_with_key(token, old_pass)
        # Writing new data
        with open(path_to_creds, 'wb') as cred_file:
            cred_file.write('entry:'+encrypt_with_key(username, new_pass)+'\n')
            cred_file.write('entry:'+encrypt_with_key(token, new_pass))
        logging.info('Passphrase has been successfully updated.')
    # if no print warning.
    else:
        logging.warn('No credentials file found.')


def reset_credentials():
    """
    resets credentials.
    :return: nada
    """
    path_to_creds = get_file_location('cred.txt')
    if os.path.isfile(path_to_creds):
        os.remove('cred.txt')
        logging.info('Credentials have been successfully reset.')
    else:
        logging.warn('No existing credentials found.')


def set_credentials(**kwargs):
    """
    set credentials
    :return: nada
    """
    if 'username' in kwargs and 'token' in kwargs and 'passphrase' in kwargs:
        logging.info('Using credentials found in user input...')
        username = kwargs['username']
        tkn = kwargs['token']
        passphrase = kwargs['passphrase']
    else:
        username = raw_input('Username: ')
        tkn = raw_input('Token: ')
        passphrase = getpass.getpass('Passphrase: ')
    path_to_creds = get_file_location('cred.txt')
    with open(path_to_creds, 'wb') as cred_file:
        cred_file.write('entry:'+encrypt_with_key(username, passphrase)+'\n')
        cred_file.write('entry:'+encrypt_with_key(tkn, passphrase))
    logging.info('Your credentials were successfully set.')

