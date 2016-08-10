#!/usr/bin/env python
"""
   :platform: Unix
   :synopsis: Useful functions to use with esgissue module.

"""

# Module imports
import os
import re
import sys
import logging
import string
import textwrap
from argparse import HelpFormatter
import datetime
import json
import requests
from jsonschema import validate
__JSON_SCHEMA_PATHS__ = {'create': '{0}/templates/create.json'.format(os.path.dirname(os.path.abspath(__file__))),
                         'update': '{0}/templates/update.json'.format(os.path.dirname(os.path.abspath(__file__))),
                         'close': '{0}/templates/update.json'.format(os.path.dirname(os.path.abspath(__file__))),
                         'retrieve': '{0}/templates/retrieve.json'.format(os.path.dirname(os.path.abspath(__file__)))}

actions = ['create', 'update', 'close', 'retrieve']
urls = {
        'create': 'http://localhost:5001/1/issue/create',
        'update': 'http://localhost:5001/1/issue/update',
        'close': 'http://localhost:5001/1/issue/close',
        'retrieve': 'http://localhost:5001/1/issue/retrieve?uid='
        }


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
        logfile = 'esgissue-{0}-{1}.log'.format(datetime.now().strftime("%Y%m%d-%H%M%S"), os.getpid())
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
            logging.debug('{0}: {1}'.format(r.status_code, url))
        return r.status_code == requests.codes.ok
    except:
        logging.exception('Result: FAILED // Bad HTTP request')
        sys.exit(1)


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


def split_line(line, sep='|'):
    """
    Split a line into fields removing trailing and leading characters.

    :param str line: String line to split
    :param str sep: Separator character
    :returns:  A list of string fields

    """
    fields = map(string.strip, line.split(sep))
    return fields


def _get_issue(path):
    """reads json file containing issue from path to file.

    """
    with open(path, 'r') as data_file:
        return json.load(data_file)


def _get_datasets(dataset_file):
    """Returns test affected  datasets by a given issue from the respective txt file.

    """
    dsets = list()
    for dset in dataset_file:
        dsets.append(unicode(dset.strip(' \n\r\t')))
    return dsets


def validate_schema(json_schema, action):
        """
        Validates ESGF issue template against predefined JSON schema

        :param str action: The issue action/command
        :param list json_schema: the json to be validated.
        :raises Error: If the template has an invalid JSON schema
        :raises Error: If the project option does not exist in esg.ini
        :raises Error: If the description is already published on GitHub
        :raises Error: If the landing page or materials urls cannot be reached
        :raises Error: If dataset ids are malformed

        """
        logging.info('Validation of template {0}'.format(json_schema['uid']))
        # Load JSON schema for issue template
        with open(__JSON_SCHEMA_PATHS__[action]) as f:
            schema = json.load(f)
        # Validate issue attributes against JSON issue schema
        try:
            validate(json_schema, schema)
        except Exception as e:
            logging.exception(repr(e.message))
            logging.exception('Result: FAILED // {0} has an invalid JSON schema'.format(json_schema['uid']))
            sys.exit(1)

        # TODO TEST URLS FOR URL AND MATERIALS ENTRY.
        # Test landing page and materials URLs
        # urls = filter(None, traverse(map(self.attributes.get, ['url', 'materials'])))
        # if not all(map(test_url, urls)):
        #     logging.error('Result: FAILED // URLs cannot be reached')
        #     sys.exit(1)
        # Validate the datasets list against the dataset id pattern

        if not all(map(test_pattern, json_schema['datasets'])):
            logging.error('Result: FAILED // Dataset IDs have invalid format')
            sys.exit(1)
        logging.info('Result: SUCCESSFUL')


def get_ws_call(action, payload, uid):
    """
    This function builds the url for the outgoing call to the different errata ws.
    :param payload: payload to be posted
    :param action: one of the 4 actions: create, update, close, retrieve
    :param uid: in case of a retrieve call, uid is needed
    :return: requests call
    """
    if action not in actions:
        print('Action is not in allowed actions to be performed via the issue client, please check the docs.')
        sys.exit(1)
    if action in ['create', 'update', 'close']:
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        r = requests.post(urls[action], json.dumps(payload), headers)
    else:
        r = requests.get(urls[action]+uid)
    if r.status_code != requests.codes.ok:
        logging.warn('Create ws call has failed, please refer to the error text for further information: ')
        logging.warn(r.text)
        sys.exit(1)
    return r


def get_file_path(path_to_issues, path_to_dsets, uid):
    """
    Based on the user input, this function returns the destination of the issue and datasets' file.
    :param path_to_issues: args.issues
    :param path_to_dsets: args.dsets
    :param uid: the issue's identifier
    :return: path_to_issue, path_to_datasets
    """
    if os.path.isdir(path_to_issues) and os.path.isdir(path_to_dsets):
        path_to_issues = os.path.join(path_to_issues, 'issue_'+uid+'.json')
        path_to_dsets = os.path.join(path_to_dsets, 'dset_'+uid+'.txt')
        return path_to_issues, path_to_dsets
    else:
        return path_to_issues, path_to_dsets



