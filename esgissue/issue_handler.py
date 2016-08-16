#!/usr/bin/env python
"""
   :platform: Unix
   :synopsis: Manages ESGF issues on BitBucket repository.

"""

# TODO: Handle Service interaction with errors in case of drs_id and version number does not exists
# TODO: Handle Service interaction should consider dictionary to records hundreds of PIDs per issue

# Module imports
import os
import sys
import logging
from utils import test_url, test_pattern, traverse, get_ws_call, get_file_path
from json import load
from jsonschema import validate, ValidationError
import simplejson
import datetime

# Fill value for undocumented URL or MATERIALS
__FILL_VALUE__ = unicode('Not documented')

# JSON issue schemas full path
__JSON_SCHEMA_PATHS__ = {'create': '{0}/templates/create.json'.format(os.path.dirname(os.path.abspath(__file__))),
                         'update': '{0}/templates/update.json'.format(os.path.dirname(os.path.abspath(__file__))),
                         'close': '{0}/templates/update.json'.format(os.path.dirname(os.path.abspath(__file__))),
                         'retrieve': '{0}/templates/retrieve.json'.format(os.path.dirname(os.path.abspath(__file__)))}

# GitHub labels
__LABELS__ = {'Low': '#e6b8af',
              'Medium': '#dd7e6b',
              'High': '#cc4125',
              'Critical': '#a61c00',
              'New': '#00ff00',
              'On hold': '#ff9900',
              'Wontfix': '#0c343d',
              'Resolved': '#38761d',
              'project': '#a4c2f4',
              'institute': '#351c75',
              'models': '#a2c4c9'}

# Description ratio change
__RATIO__ = 20

# Fields to remove from retrieved issue
fields_to_remove = ['rowCreateDate', 'rowUpdateDate', 'state']
# Fields to modify from retrieved issue
fields_to_modify = {'dateUpdated': 'date_updated', 'dateCreated': 'date_created', 'dateClosed': 'date_closed'
                    , 'uid': 'id'}


class LocalIssue(object):
    """
    An object representing the local issue.
    """
    def __init__(self, issue_json, dset_list, issue_path, dataset_path, action):
        self.action = action

        if issue_json is not None:
            self.json = issue_json
            self.json['datasets'] = dset_list
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
        with open(__JSON_SCHEMA_PATHS__[action]) as f:
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
            logging.exception('Result: FAILED // {0} has an invalid JSON schema, error code: {1}'.format(self.issue_path
                                                                                                         , 1))
            sys.exit(1)
        # Test landing page and materials URLs
        urls = filter(None, traverse(map(self.json.get, ['url', 'materials'])))
        if not all(map(test_url, urls)):
            logging.error('Result: FAILED // URLs cannot be reached, error code {}'.format(2))
            sys.exit(1)
        # Validate the datasets list against the dataset id pattern
        if not all(map(test_pattern, self.json['datasets'])):
            logging.error('Result: FAILED // Dataset IDs have invalid format, error code: {}'.format(3))
            sys.exit(1)
        logging.info('Result: SUCCESSFUL')

    def create(self):
        """
        Creates an issue on the GitHub repository.
        :raises Error: If the issue registration fails without any result

        """
        try:
            logging.info('Requesting issue creation from errata service...')
            r = get_ws_call(self.action, self.json, None)
            logging.info('Updating fields of payload after remote issue creation...')
            if r.json()['status'] == 0:
                self.json['date_created'] = r.json()['dateCreated']
                self.json['date_updated'] = r.json()['dateUpdated']
                logging.info('Issue json schema has been updated, persisting in file...')
            else:
                logging.error('Errata service rejected the request for the following reasons: {0}, error code: {1}'
                              .format(r.json()['message'], 4))
                sys.exit(1)
            with open(self.issue_path, 'w') as issue_file:
                if 'datasets' in self.json.keys():
                    del self.json['datasets']

                # Replacing the id field by a uid key. Should be fixed in next versions
                # self.json['uid'] = self.json['id']
                # del self.json['id']

                issue_file.write(simplejson.dumps(self.json, indent=4, sort_keys=True))
                logging.info('Issue file has been created successfully!')
        except Exception as e:
            logging.error('An unknown error has occurred, this is the stack {0}, error code: {1}'.format(repr(e), 99))

    def update(self):
        """
        Updates an issue on the GitHub repository.
        """
        logging.info('Update issue #{}'.format(self.json['id']))

        try:
            r = get_ws_call(self.action, self.json, None)
            if r.json()['status'] == 0:
                # TODO fix ws return to ensure the value is not null
                if 'dateUpdated' in r.json().keys() and r.json()['dateUpdated'] is not None:
                    self.json['date_updated'] = r.json()['dateUpdated']
                else:
                    self.json['date_updated'] = datetime.datetime.utcnow
                del self.json['datasets']
                # updating the issue body.
                with open(self.issue_path, 'w+') as data_file:
                    data_file.write(simplejson.dumps(self.json, indent=4, sort_keys=True))
                logging.info('Issue has been updated successfully!')
            else:
                logging.error('Errata service rejected the request for the following reasons: {0}, error code: {1}'
                              .format(r.json()['message'], 4))
                sys.exit(1)
        except Exception as e:
            logging.error('An unknown error has occurred, this is the stack {0}, error code: {1}'.format(repr(e), 99))

    def close(self):
        """
        Close the GitHub issue
        """
        logging.info('Closing issue #{}'.format(self.json['id']))
        if 'datasets' in self.json.keys():
            del self.json['datasets']
        try:
            r = get_ws_call(self.action, self.json, None)
            # Only in case the webservice operation succeeded.
            if r.json()['status'] == 0:
                self.json['date_updated'] = r.json()['dateClosed']
                self.json['date_closed'] = r.json()['dateClosed']
                if 'datasets' in self.json.keys():
                    del self.json['datasets']
                with open(self.issue_path, 'w+') as data_file:
                    data_file.write(simplejson.dumps(self.json, indent=4, sort_keys=True))
                logging.info('Issue has been closed successfully!')
            else:
                logging.error('Errata service rejected the request for the following reasons: {0}, error code: {1}'
                              .format(r.json()['message'], 4))
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
            r = get_ws_call('retrieve', None, n)
            self.json = r.json()['issue']
            self.json['materials'] = self.json['materials'].split(',')
            if 'dataset' in r.json().keys():
                self.json['datasets'] = r.json()['datasets']
            else:
                self.json['datasets'] = []
            self.validate('retrieve')
            del self.json['datasets']
            path_to_issue, path_to_dataset = get_file_path(issues, dsets, self.json['uid'])
            # Todo find a better fix
            for key in fields_to_remove:
                del self.json[key]

            # Modifying keys to keep a constant naming schema.
            for key, value in fields_to_modify.iteritems():
                self.json[value] = self.json[key]
                del self.json[key]

            # Removing the closing date to avoid having null value for currently active issues.
            if 'date_closed' in self.json.keys() and self.json['date_closed'] is None:
                del self.json['date_closed']

            # Fix models from string to list
            if 'models' in self.json.keys() and self.json['models'] is not None:
                models = self.json['models']
                models = models.replace('{', '')
                models = models.replace('}', '')
                models = models.split(',')
                self.json['models'] = models
            # Todo raise this issue of non existence of Models field in the db
            if 'models' not in self.json.keys():
                self.json['models'] = []
            # Todo investigate a better fix than this.
            self.json['project'] = self.json['project'].upper()
            # Writing dataset file
            with open(path_to_dataset, 'w') as dset_file:
                if not r.json()['datasets']:
                    logging.info('The issue {} seems to be affecting no datasets.'.format(self.json['uid']))
                    dset_file.write('No datasets provided with issue.')
                for dset in r.json()['datasets']:
                    dset_file.write(dset[0] + '\n')
            # Writing issue file.
            with open(path_to_issue, 'w') as data_file:
                data_file.write(simplejson.dumps(self.json, indent=4, sort_keys=True))

        except Exception as e:
            logging.error('An unknown error has occurred, this is the stack {0}, error code: {1}'.format(repr(e), 99))






