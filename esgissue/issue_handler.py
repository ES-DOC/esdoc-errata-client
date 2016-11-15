#!/usr/bin/env python
"""
   :platform: Unix
   :synopsis: Manages ESGF issues on BitBucket repository.

"""

# TODO: Handle Service interaction with errors in case of drs_id and version number does not exists
# TODO: Handle Service interaction should consider dictionary to records hundreds of PIDs per issue

# Module imports
import sys
import logging
from utils import test_url, test_pattern, traverse, get_ws_call, get_file_path, resolve_validation_error_code, \
                  extract_facets, update_json
from json import load
from jsonschema import validate, ValidationError
import simplejson
import datetime
from constants import *
from requests.exceptions import ConnectionError, ConnectTimeout


class LocalIssue(object):
    """
    An object representing the local issue.
    """
    def __init__(self, issue_json, dset_list, issue_path, dataset_path, action):
        self.action = action
        if issue_json is not None:
            self.json = issue_json
            self.json[DATASETS] = dset_list
        self.issue_path = issue_path
        self.dataset_path = dataset_path

    def validate(self, action):
        """
        Validates ESGF issue template against predefined JSON schema

        :param str action: The issue action/command
        :raises Error: If the template has an invalid JSON schema
        :raises Error: If the project option does not exist in esg.ini
        :raises Error: If the description is already published on GitHub
        :raises Error: If the landing page or materials urls cannot be reached
        :raises Error: If dataset ids are malformed

        """
        logging.info('Validating issue...')
        # Load JSON schema for issue template
        with open(JSON_SCHEMA_PATHS[action]) as f:
            schema = load(f)
        # Validate issue attributes against JSON issue schema
        for dataset in self.json[DATASETS]:
            if not test_pattern(dataset):
                logging.error('Validation Result: FAILED // Dataset ID {} have invalid format, error code {}.'.
                              format(dataset, ERROR_DIC[DATASETS]))
                sys.exit(ERROR_DIC[DATASETS][0])
            facets = extract_facets(dataset, self.json[PROJECT])
            self.json = update_json(facets, self.json)
        try:
            validate(self.json, schema)
        except ValidationError as ve:
            # REQUIRED BECAUSE SOMETIMES THE RELATIVE PATH RETURNS EMPTY DEQUE FOR SOME REASON.
            if len(ve.relative_path) != 0:
                error_code = resolve_validation_error_code(ve.message + ve.validator + ve.relative_path[0])
            else:
                error_code = resolve_validation_error_code(ve.message + ve.validator)
            logging.error('Validation error: error message: {}'.format(error_code[1]))
            logging.error('Validation error: code {}, check documentation for error list.'.format(error_code[0]))
            # logging.error('Validation error: {} for {}, while validating {}.'.format(ve.message, ve.validator,
            #                                                                          ve.relative_path))
            # logging.error('The responsible schema part is: {}'.format(ve.schema))
            sys.exit(error_code[0])
        except ValueError as e:
            logging.error(repr(e.message))
        except Exception as e:
            logging.error(repr(e.message))
            logging.error(ERROR_DIC['validation_failed'][1] + '. Error code: {}'.format(ERROR_DIC['validation_failed'][0]))
            logging.error('File path: {}'.format(self.issue_path))
            sys.exit(ERROR_DIC['validation_failed'])
        # Test landing page and materials URLs
        urls = filter(None, traverse(map(self.json.get, [URL, MATERIALS])))
        for url in urls:
            if not test_url(url):
                logging.error('Validation Result: FAILED // this url {} cannot be reached, error code {}.'.
                              format(url, ERROR_DIC[URLS][0]))
                sys.exit(ERROR_DIC[URLS][0])
        # Validate the datasets list against the dataset id pattern
        logging.info('Validation Result: SUCCESSFUL')

    def create(self, credentials):
        """
        Creates an issue on the GitHub repository.
        :param credentials: username & token
        :raises Error: If the issue registration fails without any result

        """
        try:
            logging.info('Requesting issue #{} creation from errata service...'.format(self.json[UID]))
            get_ws_call(self.action, self.json, None, credentials)
            logging.info('Updating fields of payload after remote issue creation...')
            self.json[DATE_UPDATED] = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            logging.info('Issue json schema has been updated, persisting in file...')
            with open(self.issue_path, 'w') as issue_file:
                if DATASETS in self.json.keys():
                    del self.json[DATASETS]
                issue_file.write(simplejson.dumps(self.json, indent=4, sort_keys=True))
                logging.info('Issue file has been created successfully!')
        except ConnectionError:
            logging.error(ERROR_DIC['connection_error'][1] + '. Error code: {}'.format(ERROR_DIC['connection_error'][0]))
        except ConnectTimeout:
            logging.error(ERROR_DIC['connection_timeout'][1] + '. Error code: {}'.format(ERROR_DIC['connection_timeout'][0]))

        except Exception as e:
            logging.error('An unknown error has occurred, this is the stack {0}, error code: {1}'.format(repr(e), 99))

    def update(self, credentials):
        """
        :param credentials: username & token
        Updates an issue on the GitHub repository.
        """
        logging.info('Update issue #{}'.format(self.json[UID]))

        try:
            get_ws_call(self.action, self.json, None, credentials)
            self.json[DATE_UPDATED] = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            del self.json[DATASETS]
            # updating the issue body.
            with open(self.issue_path, 'w+') as data_file:
                data_file.write(simplejson.dumps(self.json, indent=4, sort_keys=True))
            logging.info('Issue has been updated successfully!')
        except ConnectionError:
            logging.error(ERROR_DIC['connection_error'][1] + '. Error code: {}'.format(ERROR_DIC['connection_error'][0]))
        except ConnectTimeout:
            logging.error(ERROR_DIC['connection_timeout'][1] + '. Error code: {}'.format(ERROR_DIC['connection_timeout'][0]))
        except Exception as e:
            logging.error('An unknown error has occurred, this is the stack {0}, error code: {1}'.format(repr(e), 99))

    def close(self, credentials):
        """
        :param credentials: username & token
        Close the GitHub issue
        """
        logging.info('Closing issue #{}'.format(self.json[UID]))
        try:
            get_ws_call(self.action, None, self.json[UID], credentials)
            # Only in case the webservice operation succeeded.
            self.json[DATE_UPDATED] = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            self.json[DATE_CLOSED] = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            if DATASETS in self.json.keys():
                del self.json[DATASETS]
            with open(self.issue_path, 'w+') as data_file:
                data_file.write(simplejson.dumps(self.json, indent=4, sort_keys=True))
            logging.info('Issue has been closed successfully!')
        except ConnectionError:
            logging.error(ERROR_DIC['connection_error'][1] + '. Error code: {}'.format(ERROR_DIC['connection_error'][0]))
        except ConnectTimeout:
            logging.error(ERROR_DIC['connection_timeout'][1] + '. Error code: {}'.format(ERROR_DIC['connection_timeout'][0]))
        except Exception as e:
            logging.error('An unknown error has occurred, this is the stack {0}, error code: {1}'.format(repr(e), 99))

    def retrieve(self, n, issues, dsets):
        """
        :param n:
        :param issues:
        :param dsets:
        :return:
        """
        logging.info('processing id {}'.format(n))
        try:
            r = get_ws_call(RETRIEVE, None, n, None)
            if r.json() is not None:
                self.dump_issue(r.json()[ISSUE], issues, dsets)
                logging.info('Issue has been downloaded.')
            else:
                logging.info("Issue id didn't match any issues in the errata db")
        except ConnectionError:
            logging.error(ERROR_DIC['connection_error'][1] + '. Error code: {}'.format(ERROR_DIC['connection_error'][0]))
        except ConnectTimeout:
            logging.error(ERROR_DIC['connection_timeout'][1] + '. Error code: {}'.format(ERROR_DIC['connection_timeout'][0]))
        except Exception as e:
            logging.error('An unknown error has occurred, this is the stack {0}, error code: {1}'.format(repr(e), 99))

    def retrieve_all(self, issues, dsets):
        """

        :param issues:
        :param dsets:
        :return:
        """
        try:
            logging.info('Starting archive process...')
            r = get_ws_call(RETRIEVE_ALL, None, None, None)
            logging.info('Webservice provided content...')
            logging.info('Persisting information...')
            results = r.json()[ISSUES]
            for issue in results:
                self.dump_issue(issue, issues, dsets)
        except ConnectionError:
            logging.error(ERROR_DIC['connection_error'][1] + '. Error code: {}'.format(ERROR_DIC['connection_error'][0]))
        except ConnectTimeout:
            logging.error(ERROR_DIC['connection_timeout'][1] + '. Error code: {}'.format(ERROR_DIC['connection_timeout'][0]))
        except Exception as e:
            logging.error('An unknown error has occurred, this is the stack {0}, error code: {1}'.format(repr(e), 99))

    @staticmethod
    def dump_issue(issue, issues, dsets):

        if DATE_CLOSED in issue.keys() and issue[DATE_CLOSED] is None:
            del issue[DATE_CLOSED]
        path_to_issue, path_to_dataset = get_file_path(issues, dsets, issue[UID])
        with open(path_to_dataset, 'w') as dset_file:
            if not issue[DATASETS]:
                logging.info('The issue {} seems to be affecting no datasets.'.format(issue[UID]))
                dset_file.write('No datasets provided with issue.')
            for dset in issue[DATASETS]:
                dset_file.write(dset + '\n')
            del issue[DATASETS]
        with open(path_to_issue, 'w') as data_file:
            data_file.write(simplejson.dumps(issue, indent=4, sort_keys=True))











