#!/usr/bin/env python
"""
   :platform: Unix
   :synopsis: Manages ESGF issues on BitBucket repository.

"""

# TODO: Handle Service interaction with errors in case of drs_id and version number does not exists
# TODO: Handle Service interaction should consider dictionary to records hundreds of PIDs per issue

# Module imports
import sys
import time
import linecache
import logging
from json import load
from jsonschema import validate, ValidationError
import simplejson
import datetime
from constants import *
from requests.exceptions import ConnectionError, ConnectTimeout
from utils import test_url, test_pattern, traverse, get_ws_call, get_file_path, resolve_validation_error_code, \
                  extract_facets, update_json, logging_error, order_json, get_remote_config, prepare_persistence


class LocalIssue(object):
    """
    An object representing the local issue.
    """
    def __init__(self, action, issue_file=None, dataset_file=None, issue_path=None, dataset_path=None):
        self.action = action
        self.project = None
        if issue_file is not None:
            self.json = issue_file
            self.json[DATASETS] = dataset_file
            self.project = self.json[PROJECT].lower()
        self.issue_path = issue_path
        self.dataset_path = dataset_path
        if self.project is not None:
            self.config = get_remote_config(self.json[PROJECT])

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
            facets = extract_facets(dataset, self.project, self.config)
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
                print(test_url(url))
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
            get_ws_call(action=self.action, payload=self.json,credentials=credentials)
            logging.info('Updating fields of payload after remote issue creation...')
            self.json[DATE_UPDATED] = self.json[DATE_CREATED]
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
            get_ws_call(action=self.action, payload=self.json, credentials=credentials)
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
            else:
                status = self.json[STATUS]
            get_ws_call(action=self.action, payload=status, uid=self.json[UID], credentials=credentials)
            # Only in case the webservice operation succeeded.
            self.json[DATE_UPDATED] = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            self.json[DATE_CLOSED] = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
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

    def retrieve(self, list_of_ids, issues, dsets):
        """
        :param list_of_ids:
        :param issues:
        :param dsets:
        :return:
        """
        for n in list_of_ids:
            logging.info('processing id {}'.format(n))
            try:
                r = get_ws_call(action=RETRIEVE, uid=n)
                if r.json() is not None:
                    data = prepare_persistence(r.json()[ISSUE])
                    self.dump_issue(data, issues, dsets)
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
            r = get_ws_call(action=RETRIEVE_ALL)
            logging.info('Webservice provided content...')
            logging.info('Persisting information...')
            results = r.json()[ISSUES]
            print('looping around issues')
            for issue in results:
                data = prepare_persistence(issue)
                print('dumping issue {}'.format(data['uid']))
                self.dump_issue(data, issues, dsets)
                print('issue dumped')
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
        if DATASETS in issue:
            with open(path_to_dataset, 'w') as dset_file:
                for dset in issue[DATASETS]:
                    dset_file.write(dset + '\n')
                del issue[DATASETS]
        else:
            logging.warn('Issue {} has no datasets affected.'.format(issue[UID]))
        with open(path_to_issue, 'w') as data_file:
            issue = order_json(issue)
            data_file.write(simplejson.dumps(issue, indent=4))











