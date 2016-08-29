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
from utils import test_url, test_pattern, traverse, get_ws_call, get_file_path
from json import load
from jsonschema import validate, ValidationError
import simplejson
import datetime
from constants import *

# Fields to remove from retrieved issue
# fields_to_remove = ['state']


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
        logging.info('Validating of issue...')
        # Load JSON schema for issue template
        with open(JSON_SCHEMA_PATHS[action]) as f:
            schema = load(f)
        # Validate issue attributes against JSON issue schema
        try:
            validate(self.json, schema)
        except ValidationError as ve:
            logging.exception('Validation has encountered an issue, error stack {}'.format(ve.message), 6)
            logging.exception('The value that has caused this behavior is {0}, picked up by the validator {1}'.format(
                ve.validator_value, ve.validator))
            sys.exit(6)
        except ValueError as e:
            logging.exception(e.message)
        except Exception as e:
            logging.exception(repr(e.message))
            logging.exception('Validation Result: FAILED // {0} has an invalid JSON schema, error code: {1}'.
                              format(self.issue_path, 1))
            sys.exit(1)
        # Test landing page and materials URLs
        urls = filter(None, traverse(map(self.json.get, [URL, MATERIALS])))
        if not all(map(test_url, urls)):
            logging.error('Validation Result: FAILED // URLs cannot be reached, error code {}'.format(2))
            sys.exit(1)
        # Validate the datasets list against the dataset id pattern
        if not all(map(test_pattern, self.json[DATASETS])):
            logging.error('Validation Result: FAILED // Dataset IDs have invalid format, error code: {}'.format(3))
            sys.exit(1)
        logging.info('Validation Result: SUCCESSFUL')

    def create(self):
        """
        Creates an issue on the GitHub repository.
        :raises Error: If the issue registration fails without any result

        """
        try:
            logging.info('Requesting issue #{} creation from errata service...'.format(self.json[UID]))
            get_ws_call(self.action, self.json, None)
            logging.info('Updating fields of payload after remote issue creation...')
            self.json[DATE_UPDATED] = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            logging.info('Issue json schema has been updated, persisting in file...')
            with open(self.issue_path, 'w') as issue_file:
                if DATASETS in self.json.keys():
                    del self.json[DATASETS]
                issue_file.write(simplejson.dumps(self.json, indent=4, sort_keys=True))
                logging.info('Issue file has been created successfully!')
        except Exception as e:
            logging.error('An unknown error has occurred, this is the stack {0}, error code: {1}'.format(repr(e), 99))

    def update(self):
        """
        Updates an issue on the GitHub repository.
        """
        logging.info('Update issue #{}'.format(self.json[UID]))

        try:
            get_ws_call(self.action, self.json, None)
            print(self.json)
            self.json[DATE_UPDATED] = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            del self.json[DATASETS]
            # updating the issue body.
            with open(self.issue_path, 'w+') as data_file:
                data_file.write(simplejson.dumps(self.json, indent=4, sort_keys=True))
            logging.info('Issue has been updated successfully!')
        except Exception as e:
            logging.error('An unknown error has occurred, this is the stack {0}, error code: {1}'.format(repr(e), 99))

    def close(self):
        """
        Close the GitHub issue
        """
        logging.info('Closing issue #{}'.format(self.json[UID]))
        try:
            get_ws_call(self.action, None, self.json[UID])
            # Only in case the webservice operation succeeded.
            self.json[DATE_UPDATED] = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            self.json[DATE_CLOSED] = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            if DATASETS in self.json.keys():
                del self.json[DATASETS]
            with open(self.issue_path, 'w+') as data_file:
                data_file.write(simplejson.dumps(self.json, indent=4, sort_keys=True))
            logging.info('Issue has been closed successfully!')

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
            r = get_ws_call(RETRIEVE, None, n)
            if r.json() is not None:
                self.dump_issue(r.json()[ISSUE], issues, dsets)
                logging.info('Issue has been downloaded.')
            else:
                logging.info("Issue id didn't match any issues in the errata db")
        except Exception as e:
            logging.error('An unknown error has occurred, this is the stack {0}, error code: {1}'.format(repr(e), 99))

    def retrieve_all(self, issues, dsets):
        """

        :param issues:
        :param dsets:
        :return:
        """
        try:
            print('Calling WS')
            r = get_ws_call(RETRIEVE_ALL, None, None)
            print('Answer received')
            results = r.json()[ISSUES]
            for issue in results:
                self.dump_issue(issue, issues, dsets)
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











