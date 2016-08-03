#!/usr/bin/env python
"""
   :platform: Unix
   :synopsis: Manages ESGF issues on BitBucket repository.

"""

# TODO: Handle Service interaction with errors in case of drs_id and version number does not exists
# TODO: Handle Service interaction should consider dictionary to records hundreds of PIDs per issue

# Module imports
import re
import os
import sys
import logging
from uuid import uuid4
from copy import copy
from bs4 import BeautifulSoup
from utils import MyOrderedDict, DictDiff, ListDiff, test_url, test_pattern, traverse
from json import dump, load, dumps
from jsonschema import validate
from fuzzywuzzy.fuzz import token_sort_ratio
from wheezy.template.engine import Engine
from wheezy.template.ext.core import CoreExtension
from wheezy.template.loader import FileLoader
import requests

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


class ESGFIssue(object):
    """
    Encapsulates the following issue context/information from local JSON template and
    provides related methods to deal with:

    +--------------------+-------------+------------------------------------+
    | Attribute          | Type        | Description                        |
    +====================+=============+====================================+
    | *self*.issue_f     | *FileObj*   | The issue template JSON file       |
    +--------------------+-------------+------------------------------------+
    | *self*.dsets_f     | *FileObj*   | The affected dataset list file     |
    +--------------------+-------------+------------------------------------+
    | *self*.attributes  | *dict*      | The issues attributes              |
    +--------------------+-------------+------------------------------------+
    | *self*.dsets       | *list*      | The affected datasets              |
    +--------------------+-------------+------------------------------------+

    The attributes keys are:
    +--------------------+-------------+------------------------------------+
    | Key                | Value type  | Description                        |
    +====================+=============+====================================+
    | *self*.number      | *int*       | The issue number                   |
    +--------------------+-------------+------------------------------------+
    | *self*.id          | *str*       | The issue ESGF id (UUID format)    |
    +--------------------+-------------+------------------------------------+
    | *self*.title       | *str*       | The issue title                    |
    +--------------------+-------------+------------------------------------+
    | *self*.description | *str*       | The issue description              |
    +--------------------+-------------+------------------------------------+
    | *self*.severity    | *str*       | The issue priority/severity level  |
    +--------------------+-------------+------------------------------------+
    | *self*.project     | *str*       | The affected project               |
    +--------------------+-------------+------------------------------------+
    | *self*.institute   | *str*       | The affected institute             |
    +--------------------+-------------+------------------------------------+
    | *self*.models      | *list*      | The affected models                |
    +--------------------+-------------+------------------------------------+
    | *self*.url         | *str*       | The landing page URL               |
    +--------------------+-------------+------------------------------------+
    | *self*.materials   | *list*      | The materials URLs                 |
    +--------------------+-------------+------------------------------------+
    | *self*.workflow    | *str*       | The issue workflow                 |
    +--------------------+-------------+------------------------------------+
    | *self*.created_at  | *str*       | The registration date (ISO format) |
    +--------------------+-------------+------------------------------------+
    | *self*.updated_at  | *str*       | The last updated date (ISO format) |
    +--------------------+-------------+------------------------------------+
    | *self*.closed_at   | *str*       | The closure date (ISO format)      |
    +--------------------+-------------+------------------------------------+

    :param FileObj issue_f: The issue template JSON file
    :param FileObj dsets_f: The affected datasets list file
    :returns: The issue context
    :rtype: *ESGFIssue*

    """
    def __init__(self, issue_f, dsets_f):
        self.issue_f, self.dsets_f = issue_f, dsets_f
        self.attributes = self.get_template(issue_f)
        self.dsets = self.get_dsets(dsets_f)
        # Ensure that local files are writable to avoid registration/update/closure of an issue without file returns.
        if not os.access(self.issue_f.name, os.W_OK):
            logging.error('Result: FAILED // JSON template {0} is not writable'.format(self.issue_f.name))
            sys.exit(1)
        if not os.access(self.dsets_f.name, os.W_OK):
            logging.error('Result: FAILED // Dataset list {0} is not writable'.format(self.issue_f.name))
            sys.exit(1)

    def get(self, key):
        """
        Returns the attribute value corresponding to the key.
        The submitted key can refer to `File.key` or `File.attributes[key]`.

        :param str key: The key
        :returns: The corresponding value
        :rtype: *str* or *list* or *dict* depending on the key

        """
        if key in self.attributes:
            return self.attributes[key]
        elif key in self.__dict__.keys():
            return self.__dict__[key]
        else:
            raise Exception('{0} not found. Available keys '
                            'are {1}'.format(key, self.attributes.keys() + self.__dict__.keys()))

    @staticmethod
    def get_template(issue_f):
        """
        Loads an issue template from a JSON file.

        :param FileObj issue_f: The JSON issue template as file object
        :returns: The issue attributes
        :rtype: *dict*
        :raises Error: If the JSON file parsing fails

        """
        try:
            return load(issue_f, object_pairs_hook=MyOrderedDict)
        except:
            raise Exception('{0} is not a valid JSON file'.format(issue_f.name))

    @staticmethod
    def get_dsets(dsets_f):
        """
        Gets the affected datasets list from a text file.

        :param FileObj dsets_f: The affected datasets list file
        :returns: The affected datasets
        :rtype: *iter*

        """
        dsets = list()
        for dset in dsets_f:
            dsets.append(unicode(dset.strip(' \n\r\t')))
        return dsets

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
        logging.info('Validation of template {0}'.format(self.issue_f.name))
        # Load JSON schema for issue template
        with open(__JSON_SCHEMA_PATHS__[action]) as f:
            schema = load(f)
        # Validate issue attributes against JSON issue schema
        try:
            validate(self.attributes, schema)
        except Exception as e:
            logging.exception(repr(e.message))
            logging.exception('Result: FAILED // {0} has an invalid JSON schema'.format(self.issue_f.name))
            sys.exit(1)
        # Test landing page and materials URLs
        urls = filter(None, traverse(map(self.attributes.get, ['url', 'materials'])))
        if not all(map(test_url, urls)):
            logging.error('Result: FAILED // URLs cannot be reached')
            sys.exit(1)
        # Validate the datasets list against the dataset id pattern
        if not all(map(test_pattern, self.dsets)):
            logging.error('Result: FAILED // Dataset IDs have invalid format')
            sys.exit(1)
        logging.info('Result: SUCCESSFUL')

    def create(self):
        """
        Creates an issue on the GitHub repository.
        :raises Error: If the issue registration fails without any result

        """
        logging.info('Started issue creation process...')
        # Test if description is not already published
        # if self.attributes['description'] in descriptions.values():
        #     number = [k for k, v in descriptions.iteritems() if v == self.attributes['description']]
        #     logging.error('Result: FAILED // Issue description is already published'
        #                   ' within issue(s) #{0}'.format(number))
        #     logging.debug('Local "{0}" -> "{1}"'.format('description', self.attributes['description']))
        #     for n in number:
        #         logging.debug('Remote "{0}" #{1} <- "{2}"'.format('description', n, descriptions[n]))
        #     sys.exit(1)
        logging.info('Adding id and workflow to json file.')
        self.attributes.prepend('id', str(uuid4()))
        self.attributes.update({'workflow': unicode('New')})
        self.attributes['datasets'] = self.dsets
        print('here..')
        print(type(self.attributes))
        logging.info('json has been completed.')
        url = 'http://localhost:5001/1/issue/create'
        payload = load(self.attributes)
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        r = requests.post(url, dumps(payload), headers=headers)
        print(r.text)
        # issue = gh.create_issue(title=self.attributes['title'],
        #                         body=self.issue_content(self.attributes, self.dsets),
        #                         assignee=assignee,
        #                         labels=self.get_labels(gh, self.attributes))
        print(self.attributes)

    @staticmethod
    def get_labels(gh, attributes):
        """
        Gets the labels to attach to an issue. Creates the corresponding labels is necessary.

        :param GitHubObj gh: The GitHub repository connector (as a :func:`github3.repos.repo` class instance)
        :param dict attributes: The issue attributes to get labels
        :returns: The label names
        :rtype: *list*

        """
        labels = dict()
        labels['Severity: ' + attributes['severity']] = __LABELS__[attributes['severity']]
        labels['Project: ' + attributes['project']] = __LABELS__['project']
        labels['Workflow: ' + attributes['workflow']] = __LABELS__[attributes['workflow']]
        labels['Institute: ' + attributes['institute']] = __LABELS__['institute']
        for model in attributes['models']:
            labels['Model: ' + model] = __LABELS__['models']
        for name, color in labels.items():
            if not gh.label(name):
                gh.create_label(name=name, color=color)
                logging.warning('GitHub label "{0}" was created'.format(name))
        return labels.keys()

    def send(self, hs, repo):
        """
        Updates the errata id PID metadata for correspond affected datasets.

        :param ESGF_PID_connector hs: The Handle Service connector
        (as a :func:`esgfpid.ESGF_PID_connector` class instance)
        :param str repo: The BitBucket repository
        :raises Error: If the PID update fails for any other reason.

        """
        logging.info('Send issue information to the Handle Service')
        try:
            errata_id = '{0}.{1}.{2}'.format(repo, self.attributes['number'], self.attributes['esgf_id'])
            for dset in self.dsets:
                drs_id, version_number = dset.split('#')
                hs.add_errata_ids(drs_id=drs_id,
                                  version_number=version_number,
                                  errata_ids=errata_id)
            logging.info('Result: SUCCESSFUL')
        except:
            logging.exception('Result: FAILED')
            sys.exit(1)

    def update(self, gh, remote_issue):
        """
        Updates an issue on the GitHub repository.

        :param GitHubObj gh: The GitHub repository connector (as a :func:`github3.repos.repo` class instance)
        :param GitHubIssue remote_issue: The corresponding GitHub issue (as a :func:`GitHubIssue` class instance)
        :raises Error: If the id, title, project or dates are different
        :raises Error: If the workflow changes back to new
        :raises Error: If the issue update fails for any other reason

        """
        logging.info('Update GitHub issue #{0}'.format(remote_issue.number))
        # Test that workflow should not change back to "New"
        if remote_issue.attributes['workflow'] != 'New' and self.attributes['workflow'] == 'New':
            logging.error('Result: FAILED // Issue workflow should not change back to "New"')
            logging.debug('Local "{0}"  -> "{1}"'.format('workflow', self.attributes['workflow']))
            logging.debug('Remote "{0}" <- "{1}"'.format('workflow', remote_issue.attributes['workflow']))
            sys.exit(1)
        # Test if id, title, project, institute and dates are unchanged.
        for key in ['id', 'title', 'project', 'institute', 'created_at', 'last_updated_at']:
            if self.attributes[key] != remote_issue.attributes[key]:
                logging.error('Result: FAILED // "{0}" attribute should be unchanged'.format(key))
                logging.debug('Local "{0}"  -> "{1}"'.format(key, self.attributes[key]))
                logging.debug('Remote "{0}" <- "{1}"'.format(key, remote_issue.attributes[key]))
                sys.exit(1)
        # Test the description changes by no more than 80%
        if token_sort_ratio(self.attributes['description'], remote_issue.attributes['description']) < __RATIO__:
            logging.warning('Issue description changes by more than 80%')
            logging.debug('Local "{0}"  -> "{1}"'.format('description', self.attributes['description']))
            logging.debug('Remote "{0}" <- "{1}"'.format('description', remote_issue.attributes['description']))
            sys.exit(1)
        keys = DictDiff(remote_issue.attributes, self.attributes)
        dsets = ListDiff(remote_issue.dsets, self.dsets)
        if (not keys.changed() and not keys.added() and not keys.removed() and not dsets.added() and
                not dsets.removed()):
            logging.info('Nothing to change on GitHub issue #{0}'.format(remote_issue.number))
        else:
            # for dset in dsets.removed():
            for key in keys.changed():
                logging.info('CHANGE {0}'.format(key))
                logging.debug('Old "{0}" <- "{1}"'.format(key, remote_issue.attributes[key]))
                logging.debug('New "{0}" -> "{1}"'.format(key, self.attributes[key]))
                remote_issue.attributes[key] = self.attributes[key]
            for key in keys.added():
                logging.info('ADD {0}'.format(key))
                logging.debug('Old "{0}" <- "{1}"'.format(key, __FILL_VALUE__))
                logging.debug('New "{0}" -> "{1}"'.format(key, self.attributes[key]))
                remote_issue.attributes[key] = self.attributes[key]
            for key in keys.removed():
                logging.info('REMOVE {0}'.format(key))
                logging.debug('Old "{0}" <- "{1}"'.format(key, remote_issue.attributes[key]))
                logging.debug('New "{0}" -> "{1}"'.format(key, __FILL_VALUE__))
                del remote_issue.attributes[key]
            for dset in dsets.removed():
                logging.info('REMOVE {0}'.format(dset))
            for dset in dsets.added():
                logging.info('ADD {0}'.format(dset))
            remote_issue.dsets = self.dsets
            # Update issue information keeping status unchanged
            issue = gh.issue(remote_issue.number)
            success = issue.edit(title=remote_issue.attributes['title'],
                                 body=self.issue_content(remote_issue.attributes,
                                                         remote_issue.dsets),
                                 labels=self.get_labels(gh, remote_issue.attributes))
            if success:
                logging.info('Result: SUCCESSFUL')
                self.attributes.update({'last_updated_at': issue.updated_at.isoformat()})
                logging.debug('Updated at <- "{0}"'.format(self.attributes['last_updated_at']))
                self.write()
            else:
                logging.error('Result: FAILED // "{0}" issue returned.'.format(issue))
                sys.exit(1)

    def close(self, gh, remote_issue):
        """
        Close the GitHub issue

        :param GitHubObj gh: The GitHub repository connector (as a :func:`github3.repos.repo` class instance)
        :param GitHubIssue remote_issue: The corresponding GitHub issue (as a :func:`GitHubIssue` class instance)
        :raises Error: If the workflow is not "Wontfix" or "Resolved"
        :raises Error: If the issue status update fails

        """
        logging.info('Close GitHub issue #{0}'.format(remote_issue.number))
        # Test if all attributes are unchanged.
        for key in self.attributes:
            if self.attributes[key] != remote_issue.attributes[key]:
                logging.error('Result: FAILED // "{0}" attribute should be unchanged'.format(key))
                logging.debug('Local "{0}"  -> "{1}"'.format(key, self.attributes[key]))
                logging.debug('Remote "{0}" <- "{1}"'.format(key, remote_issue.attributes[key]))
                sys.exit(1)
        # Test if issue workflow is "Wontfix" or "Resolved"
        if not remote_issue.attributes['workflow'] in ['Wontfix', 'Resolved']:
            logging.error('Result: FAILED // Issue workflow should be "Wontfix" or "Resolved')
            logging.debug('Local "{0}"  -> "{1}"'.format('workflow', self.attributes['workflow']))
            logging.debug('Remote "{0}" <- "{1}"'.format('workflow', remote_issue.attributes['workflow']))
            sys.exit(1)
        issue = gh.issue(remote_issue.number)
        success = issue.close()
        if success:
            logging.info('Result: SUCCESSFUL')
            self.attributes.update({'last_updated_at': issue.updated_at.isoformat()})
            logging.debug('Updated at <- "{0}"'.format(self.attributes['last_updated_at']))
            self.attributes.update({'closed_at': issue.closed_at.isoformat()})
            logging.debug('Closed at <- "{0}"'.format(self.attributes['closed_at']))
            self.write()
        else:
            logging.error('Result: FAILED // "{0}" issue returned.'.format(issue))
            sys.exit(1)

    @staticmethod
    def issue_content(attributes, dsets):
        """
        Format the ESGF issue content.

        :param dict attributes: The issue attributes
        :param list dsets: The affected datasets
        :return: The html rendering
        :rtype: *str*

        """
        template = copy(attributes)
        template.update({'dsets': dsets})
        for key in ['url', 'materials']:
            if key not in attributes:
                template.update({key: None})
        engine = Engine(loader=FileLoader({'{0}/templates'.format(os.path.dirname(os.path.abspath(__file__)))}),
                        extensions=[CoreExtension()])
        html_template = engine.get_template('issue_content.html')
        return html_template.render(template)

    def write(self):
        """
        Writes an ESGF issue into JSON file.

        """
        logging.info('Writing ESGF issue into JSON template {0}'.format(self.issue_f.name))
        try:
            with open(self.issue_f.name, 'w') as json_file:
                dump(self.attributes, json_file, indent=0)
            logging.info('Result: SUCCESSFUL')
        except:
            logging.exception('Result: FAILED // JSON template {0} is not writable'.format(self.issue_f.name))
            sys.exit(1)


class GitHubIssue(object):
    """
    Encapsulates the following issue context/information from GitHub and
    provides related methods to deal with:

    +--------------------+-------------+------------------------------------+
    | Attribute          | Type        | Description                        |
    +====================+=============+====================================+
    | *self*.number      | *int*       | The issue number                   |
    +--------------------+-------------+------------------------------------+
    | *self*.raw         | *dict*      | The raw GitHub issue               |
    +--------------------+-------------+------------------------------------+
    | *self*.attributes  | *dict*      | The issues attributes              |
    +--------------------+-------------+------------------------------------+
    | *self*.dsets       | *list*      | The affected datasets              |
    +--------------------+-------------+------------------------------------+
    | *self*.url         | *str*       | The issue HTML url                 |
    +--------------------+-------------+------------------------------------+
    | *self*.assignee    | *str*       | The GitHub login of issue assignee |
    +--------------------+-------------+------------------------------------+

    The attributes keys are the same as the :func:`ESGFIssue` class.

    :param GitHubObj gh: The GitHub repository connector (as a :func:`github3.repos.repo` class instance)
    :param int number: The issue number
    :returns: The issue context
    :rtype: *GitHubIssue*

    """
    def __init__(self, gh, number):
        self.number = number
        self.raw = None
        self.assignee = None
        self.attributes, self.dsets = self.get_template(gh)

    def get(self, key):
        """
        Returns the attribute value corresponding to the key.
        The submitted key can refer to `GitHubIssue.key` or `GitHubIssue.attributes[key]`.

        :param str key: The key
        :returns: The corresponding value
        :rtype: *str* or *list* or *dict* depending on the key

        """
        if key in self.attributes:
            return self.attributes[key]
        elif key in self.__dict__.keys():
            return self.__dict__[key]
        else:
            raise Exception('{0} not found. Available keys are {1}'.format(key, self.attributes.keys()))

    def get_template(self, gh):
        """
        Loads an issue template from the GitHub repository.

        :param *GitHubObj* gh: The GitHub repository connector (as a :func:`github3.repos.repo` class instance)
        :returns: The issue attributes
        :rtype: *dict*
        :raises Error: If the GitHub issue cannot be reached

        """
        self.raw = gh.issue(self.number)
        if not self.raw:
            raise Exception('Cannot get GitHub issue number {0}'.format(self.number))
        self.assignee = self.raw.assignee.login
        return self.format()

    def format(self):
        """
        Formats a GitHub issue to an ESGFIssue template.

        :returns: The formatted issue
        :rtype: *dict*

        """
        content = self.issue_content_parser(self.raw.body)
        labels = [tuple(label.name.split(': ')) for label in self.raw.labels]
        issue = MyOrderedDict()
        issue[unicode('number')] = self.raw.number
        issue[unicode('id')] = content['id']
        issue[unicode('title')] = self.raw.title
        issue[unicode('description')] = content['description']
        issue[unicode('project')] = [label[1] for label in labels if 'Project' in label][0]
        issue[unicode('institute')] = [label[1] for label in labels if 'Institute' in label][0]
        issue[unicode('models')] = [label[1] for label in labels if 'Model' in label]
        issue[unicode('severity')] = [label[1] for label in labels if 'Severity' in label][0]
        if content['url'] != __FILL_VALUE__:
            issue[unicode('url')] = content['url']
        if content['materials'] != __FILL_VALUE__:
            issue[unicode('materials')] = content['materials']
        issue[unicode('workflow')] = [label[1] for label in labels if 'Workflow' in label][0]
        issue[unicode('created_at')] = self.raw.created_at.isoformat()
        issue[unicode('last_updated_at')] = self.raw.updated_at.isoformat()
        if self.raw.is_closed():
            issue[unicode('closed_at')] = self.raw.closed_at.isoformat()
        return issue, content['dsets']

    @staticmethod
    def issue_content_parser(content):
        """
        Parses a raw issue content from GitHub and translates it into an ESGF issue template.

        :param str content: The issue content
        :returns: The issue attributes
        :rtype: *dict*

        """
        html_content = BeautifulSoup(re.sub('[\n\t\r]', '', content), "html.parser")
        html_dict = dict()
        for elt in html_content.find_all('div'):
            output_img = []
            output_dsets = []
            for parent in elt.contents:
                if parent.name == 'img':
                    output_img.append(parent['src'])
                    html_dict[elt['id']] = output_img
                elif parent.name == 'ul':
                    for child in parent.find_all('li'):
                        output_dsets.append(child.string)
                        html_dict[elt['id']] = output_dsets
                else:
                    html_dict[elt['id']] = parent.string
        return html_dict

    def validate(self, action, projects):
        """
        Validates GitHub issue template against predefined JSON schema

        :param str action: The issue action/command
        :param list projects: The projects options from esg.ini
        :raises Error: If the template has an invalid JSON schema
        :raises Error: If the project option does not exist in esg.ini
        :raises Error: If the landing page or materials urls cannot be reached.
        :raises Error: If dataset ids are malformed

        """
        logging.info('Validation of GitHub issue {0}'.format(self.attributes['number']))
        # Load JSON schema for issue template
        with open(__JSON_SCHEMA_PATHS__[action]) as f:
            schema = load(f)
        # Validate issue attributes against JSON issue schema
        try:
            validate(self.attributes, schema)
        except:
            logging.exception('Result: FAILED // GitHub issue {0} has an invalid JSON schema'.format(self.number))
            sys.exit(1)
        # Test if project is declared in esg.ini
        if not self.attributes['project'] in projects:
            logging.error('Result: FAILED // Project should be one of {0}'.format(projects))
            logging.debug('Local "{0}" -> "{1}"'.format('project', self.attributes['project']))
            sys.exit(1)
        # Test landing page and materials URLs
        urls = filter(None, traverse(map(self.attributes.get, ['url', 'materials'])))
        if not all(map(test_url, urls)):
            logging.error('Result: FAILED // URLs cannot be reached')
            sys.exit(1)
        # Validate the datasets list against the dataset id pattern
        if not all(map(test_pattern, self.dsets)):
            logging.error('Result: FAILED // Dataset IDs have invalid format')
            sys.exit(1)
        logging.info('Result: SUCCESSFUL')

    def retrieve(self, issue_f, dsets_f):
        """
        Retrieves a GitHub issue and writes ESGF template into JSON file and affected datasets list into TXT file

        :param FileObj issue_f: The JSON file to write in
        :param FileObj dsets_f: The TXT file to write in

        """
        logging.info('Retrieve GitHub issue #{0} JSON template'.format(self.number))
        try:
            with issue_f as json_file:
                dump(self.attributes, json_file, indent=0)
            logging.info('Result: SUCCESSFUL')
        except Exception as e:
            logging.exception('Result: FAILED // JSON template {0} is not writable'.format(issue_f.name))
            sys.exit(1)
        logging.info('Retrieve GitHub issue #{0} affected datasets list'.format(self.number))
        try:
            with dsets_f as list_file:
                list_file.write('\n'.join(self.dsets))
            logging.info('Result: SUCCESSFUL')
        except:
            logging.exception('Result: FAILED // Dataset list {0} is not writable'.format(dsets_f.name))
            sys.exit(1)
