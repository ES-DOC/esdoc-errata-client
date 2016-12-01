#!/usr/bin/env python
"""
   :platform: Unix
   :synopsis: Manages ESGF issues on BitBucket repository.

"""

# TODO: Handle Service interaction with errors in case of drs_id and version number does not exists
# TODO: Handle Service interaction should consider dictionary to records hundreds of PIDs per issue

# Module imports
import sys, time, linecache
import logging
from utils import test_url, test_pattern, traverse, get_ws_call, get_file_path, resolve_validation_error_code, \
                  extract_facets, update_json, logging_error, order_json
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
                logging_error(ERROR_DIC[DATASETS], dataset)
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
            logging_error(error_code)
        except ValueError as e:
            logging.error(repr(e.message))
        except Exception as e:
            logging.error(repr(e.message))
            logging_error(ERROR_DIC['validation_failed'], self.issue_path)
        # Test landing page and materials URLs
        urls = filter(None, traverse(map(self.json.get, [URL, MATERIALS])))
        for url in urls:
            if not test_url(url):
                logging_error(ERROR_DIC[URLS], url)
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
            self.json[CREATED_BY] = credentials[0]
            get_ws_call(self.action, self.json, None, credentials)
            logging.info('Updating fields of payload after remote issue creation...')
            self.json[DATE_UPDATED] = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            logging.info('Issue json schema has been updated, persisting in file...')
            with open(self.issue_path, 'w') as issue_file:
                if DATASETS in self.json.keys():
                    del self.json[DATASETS]
                self.json = order_json(self.json)
                issue_file.write(simplejson.dumps(self.json, indent=4))
                logging.info('Issue file has been created successfully!')
        except ConnectionError:
            logging_error(ERROR_DIC['connection_error'])
        except ConnectTimeout:
            logging_error(ERROR_DIC['connection_timeout'])
        except Exception as e:
            logging_error(ERROR_DIC['unknown_error'], repr(e))

    def update(self, credentials):
        """
        :param credentials: username & token
        Updates an issue on the GitHub repository.
        """
        logging.info('Update issue #{}'.format(self.json[UID]))

        try:
            self.json[UPDATED_BY] = credentials[0]
            get_ws_call(self.action, self.json, None, credentials)
            self.json[DATE_UPDATED] = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            del self.json[DATASETS]
            # updating the issue body.
            with open(self.issue_path, 'w+') as data_file:
                self.json = order_json(self.json)

                data_file.write(simplejson.dumps(self.json, indent=4))
            logging.info('Issue has been updated successfully!')
        except ConnectionError:
            logging_error(ERROR_DIC['connection_error'], None)
        except ConnectTimeout:
            logging.error(ERROR_DIC['connection_timeout'], None)
        except Exception as e:
            exc_type, exc_obj, tb = sys.exc_info()
            f = tb.tb_frame
            lineno = tb.tb_lineno
            filename = f.f_code.co_filename
            linecache.checkcache(filename)
            line = linecache.getline(filename, lineno, f.f_globals)
            print 'EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj)

            logging_error(ERROR_DIC['unknown_error'], repr(e))

    def close(self, credentials, status):
        """
        :param credentials: username & token
        :param status: issue status
        Close the GitHub issue
        """
        logging.info('Closing issue #{}'.format(self.json[UID]))
        try:
            if self.json[STATUS] in [STATUS_NEW, STATUS_ONHOLD]:
                if status is not None:
                    if status not in [STATUS_RESOLVED, STATUS_WONTFIX]:
                        logging_error(ERROR_DIC[STATUS])
                    else:
                        self.json[STATUS] = status
                        self.action = UPDATE
                        self.update(credentials)
                        self.action = CLOSE
                else:
                    time.sleep(0.5)
                    status = raw_input('Issue status does not allow direct closing. '
                                       'Please change it to either (w)ontfix/(r)esolved: ')
                    if status not in ['w', 'r', 'W', 'R']:
                        logging.error(STATUS)
                    else:
                        if status in ['r', 'R']:
                            status = STATUS_RESOLVED
                        else:
                            status = STATUS_WONTFIX
                        self.json[STATUS] = status
                        self.action = UPDATE
                        self.update(credentials)
                        self.action = CLOSE
            get_ws_call(self.action, status, self.json[UID], credentials)
            # Only in case the webservice operation succeeded.
            self.json[DATE_UPDATED] = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            self.json[DATE_CLOSED] = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            self.json[CLOSED_BY] = credentials[1]
            if DATASETS in self.json.keys():
                del self.json[DATASETS]
            with open(self.issue_path, 'w+') as data_file:
                self.json = order_json(self.json)
                data_file.write(simplejson.dumps(self.json, indent=4))
            logging.info('Issue has been closed successfully!')
        except ConnectionError:
            logging_error(ERROR_DIC['connection_error'])
        except ConnectTimeout:
            logging_error(ERROR_DIC['connection_timeout'])
        except Exception as e:
            logging_error(ERROR_DIC['unknown_error'], repr(e))

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
            logging_error(ERROR_DIC['connection_error'])
        except ConnectTimeout:
            logging_error(ERROR_DIC['connection_timeout'])
        except Exception as e:
            logging_error(ERROR_DIC['unknown_error'], repr(e))

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
            logging_error(ERROR_DIC['connection_error'])
        except ConnectTimeout:
            logging_error(ERROR_DIC['connection_timeout'])
        except Exception as e:
            logging_error(ERROR_DIC['unknown_error'], repr(e))

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
            issue = order_json(issue)
            data_file.write(simplejson.dumps(issue, indent=4))











