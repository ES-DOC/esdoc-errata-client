#!/usr/bin/env python
"""
   :platform: Unix
   :synopsis: Manages ESGF issues.

"""

# Module imports
import sys
import time
import linecache
import logging
import os
from json import load
from jsonschema import validate, ValidationError
import simplejson
from constants import *
from config import _get_config_contents
from requests.exceptions import ConnectionError, ConnectTimeout
from utils import _test_url, _traverse, _get_ws_call, _get_retrieve_dirs, _resolve_validation_error_code, \
                  _logging_error, _order_json, _prepare_persistence, _resolve_status, _prepare_retrieve_dirs,\
                  _format_datasets, _test_datasets_for_version_and_empty

cf = _get_config_contents()
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
            if PROJECT in self.json.keys():
                self.project = self.json[PROJECT].lower()
                self.json[PROJECT] = self.project
            else:
                _logging_error(ERROR_DIC[PROJECT])
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
        # Load JSON schema for issue template
        # Get schema path by using JSON_SCHEMA_PATH constants.
        with open(cf['json_schema_paths'][action].format(os.path.dirname(os.path.abspath(__file__)))) as f:
            schema = load(f)

        # Pre-validate issue attributes against action-defined JSON issue schema
        try:
            logging.info('Validating json file input...')
            validate(self.json, schema)
            logging.info('Initial json is valid.')
        except ValidationError as ve:
            # REQUIRED BECAUSE SOMETIMES THE RELATIVE PATH RETURNS EMPTY DEQUE FOR SOME REASON.
            print(ve.message)
            print(ve.validator)
            if len(ve.relative_path) != 0:
                error_code = _resolve_validation_error_code(ve.message + ve.validator + ve.relative_path[0])
            else:
                error_code = _resolve_validation_error_code(ve.message + ve.validator)
            _logging_error(error_code)
        except ValueError as e:
            _logging_error(repr(e.message))
        except Exception as e:
            _logging_error(repr(e.message))
            _logging_error(ERROR_DIC['validation_failed'], self.issue_path)

        # Pre-validation of dataset list + reformatting local files.
        dataset_version_dictionary = _test_datasets_for_version_and_empty(self.json[DATASETS])

        # Test landing page and materials URLs
        urls = filter(None, _traverse(map(self.json.get, [URL, MATERIALS])))
        if cf['validate_issue_urls']:
            logging.info('Validating issue urls...')
            for url in urls:
                if url != '':
                    if not _test_url(url):
                        _logging_error(ERROR_DIC[URLS], url)
            logging.info('Issue urls validated.')
        # Once validated, persisting changes to local dataset file.
        logging.info('Formatting and persisting datasets...')
        # Persisting datasets locally and updating issue file accordingly.
        self.json[DATASETS] = _format_datasets(dataset_version_dictionary, self.dataset_path)
        logging.info('Datasets persisted successfully.')

    def create(self, credentials):
        """
        Creates an issue on the GitHub repository.
        :param credentials: username & token
        :raises Error: If the issue registration fails without any result

        """
        try:
            logging.info('Requesting issue #{} creation from errata service...'.format(self.json[UID]))
            _get_ws_call(action=self.action, payload=self.json, credentials=credentials)
            logging.info('Updating fields of payload after remote issue creation...')
            logging.info('Issue json schema has been updated, persisting in file...')
            with open(self.issue_path, 'w') as issue_file:
                if DATASETS in self.json.keys():
                    del self.json[DATASETS]
                self.json = _order_json(self.json)
                issue_file.write(simplejson.dumps(self.json, indent=4))
                logging.info('Issue file has been created successfully!')
                logging.info('Issue can be viewed at {}'.format(cf['url_viewer']+self.json[UID]))
        except ConnectionError:
            _logging_error(ERROR_DIC['connection_error'])
        except ConnectTimeout:
            _logging_error(ERROR_DIC['connection_timeout'])
        except Exception as e:
            _logging_error(ERROR_DIC['unknown_error'], repr(e))

    def update(self, credentials):
        """
        :param credentials: username & token
        Updates an issue on the GitHub repository.
        """
        logging.info('Update issue #{}'.format(self.json[UID]))

        try:
            _get_ws_call(action=self.action, payload=self.json, credentials=credentials)
            del self.json[DATASETS]
            # updating the issue body.
            with open(self.issue_path, 'w+') as data_file:
                self.json = _order_json(self.json)
                data_file.write(simplejson.dumps(self.json, indent=4))
            logging.info('Issue has been updated successfully!')
            logging.info('Issue can be viewed at {}'.format(cf['url_viewer']+self.json[UID]))

        except ConnectionError:
            _logging_error(ERROR_DIC['connection_error'], None)
        except ConnectTimeout:
            logging.error(ERROR_DIC['connection_timeout'], None)
        except Exception as e:
            exc_type, exc_obj, tb = sys.exc_info()
            f = tb.tb_frame
            lineno = tb.tb_lineno
            filename = f.f_code.co_filename
            linecache.checkcache(filename)
            line = linecache.getline(filename, lineno, f.f_globals)
            logging.error('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))

            _logging_error(ERROR_DIC['unknown_error'], repr(e))

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
                    status = _resolve_status(status)
                    if status not in [STATUS_RESOLVED, STATUS_WONTFIX]:
                        _logging_error(ERROR_DIC[STATUS])
                    else:
                        self.json[STATUS] = status
                        self.action = UPDATE
                        self.update(credentials)
                        self.action = CLOSE
                else:
                    time.sleep(0.25)
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
            _get_ws_call(action=self.action, payload=status, uid=self.json[UID], credentials=credentials)
            # Only in case the webservice operation succeeded.
            if DATASETS in self.json.keys():
                del self.json[DATASETS]
            with open(self.issue_path, 'w+') as data_file:
                self.json = _order_json(self.json)
                data_file.write(simplejson.dumps(self.json, indent=4))
            logging.info('Issue has been closed successfully!')
            logging.info('Issue can be viewed at {}'.format(cf['url_viewer']+self.json[UID]))
        except ConnectionError:
            _logging_error(ERROR_DIC['connection_error'])
        except ConnectTimeout:
            _logging_error(ERROR_DIC['connection_timeout'])
        except Exception as e:
            _logging_error(ERROR_DIC['unknown_error'], repr(e))

    def retrieve(self, list_of_ids, issues, dsets):
        """
        :param list_of_ids:
        :param issues:
        :param dsets:
        :return:
        """
        issues, dsets = _prepare_retrieve_dirs(issues, dsets, list_of_ids)
        for n in list_of_ids:
            logging.info('Processing id {}'.format(n))
            try:
                logging.info('Contacting ESDoc-Errata server for issue #{} information'.format(n))
                r = _get_ws_call(action=RETRIEVE, uid=n)
                if r.json() is not None:
                    logging.info('Retrieved issue #{} information from ESDoc-Errata server, persisting...'.format(n))
                    data = _prepare_persistence(r.json()[ISSUE])
                    self.dump_issue(data, issues, dsets)
                    logging.info('Issue #{} has been downloaded.'.format(n))
                else:
                    logging.info("Issue #{} didn't match any issues in the errata db".format(n))
            except ConnectionError:
                _logging_error(ERROR_DIC['connection_error'])
            except ConnectTimeout:
                _logging_error(ERROR_DIC['connection_timeout'])
            except Exception as e:
                _logging_error(ERROR_DIC['unknown_error'], repr(e))

    def retrieve_all(self, issues, dsets):
        """
        Different api endpoint than simple retrieve.
        :param issues:
        :param dsets:
        :return:
        """
        try:
            logging.info('Starting issue archiving process...')
            r = _get_ws_call(action=RETRIEVE_ALL)
            logging.info('Successfully retrieved {} issues from ESDoc-Errata server...'.format(r.json()[COUNT]))
            results = r.json()[ISSUES]
            for issue in results:
                data = _prepare_persistence(issue)
                self.dump_issue(data, issues, dsets)
        except ConnectionError:
            _logging_error(ERROR_DIC['connection_error'])
        except ConnectTimeout:
            _logging_error(ERROR_DIC['connection_timeout'])
        except Exception as e:
            _logging_error(ERROR_DIC['unknown_error'], repr(e))

    @staticmethod
    def dump_issue(data, issues, dsets):
        """
        Resolves the user input directories and dumps the issue information in the indicated location
        :param data: issue information json file
        :param issues: issue directory
        :param dsets: dset directory
        :return:
        """
        # Getting the directory where the issue file is going to be persisted.
        path_to_issue, path_to_dataset = _get_retrieve_dirs(issues, dsets, data[UID])
        logging.info('Issue #{} data to issue file {}'.format(data[UID], path_to_issue))
        logging.info('Issue #{} datasets to dataset file {}'.format(data[UID], path_to_dataset))
        # Persisting Datasets
        if DATASETS in data:
            with open(path_to_dataset, 'w') as dset_file:
                for dset in data[DATASETS]:
                    dset_file.write(dset + '\n')
                del data[DATASETS]
        else:
            logging.warn('Issue #{} has no datasets affected.'.format(data[UID]))
        # Persisting issues.
        with open(path_to_issue, 'w') as data_file:
            data = _order_json(data)
            data_file.write(simplejson.dumps(data, indent=4))
        logging.info("Finished processing issue #{}".format(data[UID]))




