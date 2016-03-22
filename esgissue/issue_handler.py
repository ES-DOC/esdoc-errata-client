#!/usr/bin/env python
"""
   :platform: Unix
   :synopsis: Manages ESGF issues on BitBucket repository.

"""

# Module imports
import re
import os
import sys
import logging
from hashlib import md5
from bs4 import BeautifulSoup
from utils import DictDiff, ListDiff, test_url, test_pattern
from json import dump, load
from jsonschema import validate
from collections import OrderedDict

# Available issue status
__STATUS__ = ['new', 'on hold', 'wontfix', 'close']

# Fill value for undocumented URL or MATERIALS
__FILL_VALUE__ = unicode('Not documented')

# JSON key order to keep user-friendly readability
__KEYS_ORDER__ = ['title',
                  'description',
                  'project',
                  'kind',
                  'severity',
                  'url',
                  'materials',
                  'assignee',
                  'dset_ids']

# JSON issue schema full path
__JSON_SCHEMA_PATH__ = "{0}/schema.json".format(os.path.dirname(os.path.abspath(__file__)))


class ESGFIssue(object):
    """
    Encapsulates the following issue context/information and provides related methods to deal with:

    +--------------------+-------------+------------------------------------+
    | Attribute          | Type        | Description                        |
    +====================+=============+====================================+
    | *self*.id          | *int*       | Remote BitBucket issue id          |
    +--------------------+-------------+------------------------------------+
    | *self*.title       | *str*       | Issue title                        |
    +--------------------+-------------+------------------------------------+
    | *self*.description | *str*       | Issue description                  |
    +--------------------+-------------+------------------------------------+
    | *self*.project     | *str*       | Project affected by the issue      |
    +--------------------+-------------+------------------------------------+
    | *self*.severity    | *str*       | Issue priority/severity level      |
    +--------------------+-------------+------------------------------------+
    | *self*.type        | *str*       | Issue type/kind                    |
    +--------------------+-------------+------------------------------------+
    | *self*.url         | *str*       | Landing page URL                   |
    +--------------------+-------------+------------------------------------+
    | *self*.materials   | *list*      | Materials URLs                     |
    +--------------------+-------------+------------------------------------+
    | *self*.hash_key    | *str*       | The title hash key                 |
    +--------------------+-------------+------------------------------------+
    | *self*.description | *str*       | Issue description                  |
    +--------------------+-------------+------------------------------------+


    :param dict args: Parsed command-line arguments
    :returns: The issue context
    :rtype: *dict*

    """
    def __init__(self, template, dsets):
        self.attributes = self.get_template(template)
        self.path = template.name
        self.dsets = self.get_dsets(dsets)

    def get(self, key):
        """
        Returns the template value to the corresponding key.

        :param str key: The template key
        :returns: The template value
        :rtype: *str* or *list* or *dict* depending on the key

        """
        return self.attributes[key]

    @staticmethod
    def get_template(path):
        """
        Loads an issue template from a JSON file.

        :param *file* path: The JSON issue template as file object
        :returns: The issue attributes
        :rtype: *dict*
        :raises Error: If the JSON file parsing fails

        """
        try:
            return load(path, object_pairs_hook=OrderedDict)
        except:
            logging.exception('{0} is not a valid JSON file'.format(path.name))
            sys.exit(1)

    @staticmethod
    def get_dsets(dsets_list):
        """
        Gets the affected datasets list from a text file.

        :param *file* dsets_list: The path of the text file as file object
        :returns: An iterator on the datasets list
        :rtype: *iter*

        """
        with dsets_list as dsets:
            for dset in dsets:
                yield dset.strip(' \n\r\t')

    def validate(self):
        """
        Validates JSON template against predefined JSON schema

        :raises Error: If the template has an invalid JSON schema.
        :raises Error: If the landing page or materials urls cannot be reached.

        """
        logging.info('Validation of template {0}'.format(self.path))
        with open(__JSON_SCHEMA_PATH__) as f:
            __JSON_SCHEMA__ = load(f)
        try:
            validate(self.attributes, __JSON_SCHEMA__)
        except:
            logging.warning('Result: FAILED')
            logging.exception('{0} has an invalid JSON schema'.format(self.path))
            sys.exit(1)
        # Test landing page and materials URLs
    #    for key in ['url', 'materials']:
    #        self.attributes[key]
    #           test_url(url)
    #    
    #    map(self.attributes.__getitem__, ['url','materials'])                
#
#
        if 'url' in self.attributes:
            test_url(self.attributes['url'])
        if 'materials' in self.attributes:
            for url in self.attributes['materials']:
                test_url(url)
        # Test dataset id format
        if not all(map(test_pattern, self.dsets)):
            sys.exit(1)
        logging.info('Result: SUCCESSFUL')


    def hash(self):
        """
        Hashable function to attach a unique hash key to the issue. The hashing is applied on the all keys of
        the JSON template without the hash key. If one the other fields changes the hash key is modified and added
        to the JSON template.

        :returns: The hash key
        :rtype: *str*

        """
        hash_key = md5()
        for key in self.template.keys():
            if isinstance(self.template[key], list):
                for item in self.template[key]:
                    hash_key.update(item)
            else:
                hash_key.update(self.template[key])
        self.template['hash_key'] = hash_key.hexdigest()
        return self.template['hash_key']

# TODO: add verbosity through LOG_LEVEL in config file and -v on command-line
# TODO: consider raw content for issue content parser with complete regex to ensure template writing and parsing.
# TODO: implement BitBucketIssue.history
# TODO: implement BitBucketIssue.url
# TODO: implement BitBucketIssue.responsible
# TODO: implement BitBucketIssue.status
# TODO: Handle Service interaction with errors in case of drs_id and version number does not exists
# TODO: Handle Service interaction should consider dictionary to records hundreds/thousands of PIDs per issue

    def create(self, bb):
        """
        Creates an issue on the BitBucket repository.

        :param Bitbucket bb: The BitBucket object (as a :func:`bb_client.Bitbucket` class instance)
        :raises Error: If the JSON template already has a hash key.
        :raises Error: If the issue is already registered.
        :raises Error: If the issue registration fails for any other reason.

        """
        if 'hash_key' in self.attributes.keys():
            logging.warning('Registration: FAIL')
            raise Exception('The {0} template already has a hash key'.format(self.path))
        local_key = self.hash()
        remote_keys = self.get_remote_hash_keys(bb)
        if local_key in remote_keys.values():
            remote_id = remote_keys.keys()[remote_keys.values().index(local_key)]
            logging.warning('Registration: FAIL')
            raise Exception('Issue already registered as BitBucket issue #{0}'.format(remote_id))
        success, result = bb.issue.create(title=self.attributes['title'],
                                          content=self.issue_content(self.attributes),
                                          component=self.attributes['project'],
                                          status='new',
                                          priority=self.attributes['severity'],
                                          kind=self.attributes['type'])
        if success:
            logging.info('Registration: SUCCESSFUL as BitBucket issue #{0}'.format(result['local_id']))
            self.write()
        else:
            logging.error(result)
            raise Exception('Registration: FAIL')

    @staticmethod
    def get_remote_hash_keys(bb):
        """
        Gets hash keys from all remote BitBucket issues.

        :param Bitbucket bb: The BitBucket object (as a :func:`bb_client.Bitbucket` class instance)
        :returns: The remote hash keys and issue ids
        :rtype: *dict*

        """
        remote_keys = {}
        success, result = bb.issue.all()
        if success:
            for issue in result['values']:
                html_content = BeautifulSoup(issue['content']['html'], 'html.parser')
                hash_content = html_content.find('h2', id='markdown-header-hash-key').find_next_sibling('div').string
                remote_keys[issue['id']] = hash_content.strip(' \n\r\t')
        else:
            logging.warning('Update: FAIL')
            raise Exception('Cannot retrieve all hash keys from BitBucket repository')
        return remote_keys

    def get_remote_id(self, bb):
        """
        Gets the corresponding BitBucket issue id/number.

        :param Bitbucket bb: The BitBucket object (as a :func:`bb_client.Bitbucket` class instance)
        :returns: The BitBucket issue id
        :rtype: *int*

        """
        if 'hash_key' not in self.template.keys():
            logging.warning('Update: FAIL')
            raise Exception('Cannot retrieve the corresponding BitBucket issue because '
                            'the {0} template does not have any hash key'.format(self.path))
        old_local_key = self.template['hash_key']
        remote_keys = self.get_remote_hash_keys(bb)
        if old_local_key not in remote_keys.values():
            logging.warning('Update: FAIL')
            raise Exception('Issue not registered on BitBucket repository. '
                            'Please run "esgissue create {0}".'.format(self.path))
        return int(remote_keys.keys()[remote_keys.values().index(old_local_key)])

    def update(self, bb, remote_issue):
        """
        Updates an issue on the BitBucket repository.

        :param Bitbucket bb: The BitBucket object (as a :func:`bb_client.Bitbucket` class instance)
        :param Bitbucket remote_issue: The BitBucket remote issue (as a :func:`BitBucketIssue` class instance)
        :raises Error: If the issue is NOT already registered.
        :raises Error: If the issue update fails for any other reason.

        """
        print set(self.template.keys() + ['url', 'materials'])
        print self.template.keys()
        print remote_issue.template.keys()
        template_diff = DictDiff(self.template, remote_issue.template)
        print template_diff.unchanged()
        print template_diff.changed()
        print template_diff.removed()
        print template_diff.added()

        # Probleme entre quoi et quoi on compare

        if set(self.template.keys() + ['url','materials']) == template_diff.unchanged():
            logging.info('Nothing to change on BitBucket issue #{0}'.format(remote_issue.id))
        else:
            self.hash()
            changes = {'id': remote_issue.id}
            for key in template_diff.changed():
                changes.update({'key': key.upper()})
                if key in ['dset_ids', 'materials']:
                    list_diff = ListDiff(self.template[key], set(remote_issue.template[key]))
                    added, removed = list_diff.added(), list_diff.removed()
                    for item in added:
                        changes.update({'item': item})
                        logging.info('Update BitBucket issue #{id}: '
                                     '{key} adds "{item}"'.format(**changes))
                    for item in removed:
                        changes.update({'item': item})
                        logging.info('Update BitBucket issue #{id}: '
                                     '{key} removes "{item}"'.format(**changes))
                else:
                    changes.update({'from_value': remote_issue.template[key],
                                    'to_value': self.template[key]})
                    logging.info('Update BitBucket issue #{id}: '
                                 '{key} changes from "{from_value}" to "{to_value}"'.format(**changes))
                remote_issue.template[key] = self.template[key]
            for key in template_diff.removed():
                # This can only concern "url" and "materials" keys because of __JSON_SCHEMA__
                changes.update({'key': key.upper(),
                                'to_value': 'Not documented'})
                if key == 'materials':
                    for item in remote_issue.template[key]:
                        changes.update({'item': item})
                        logging.info('Update BitBucket issue #{id}: '
                                     '{key} removes "{item}"'.format(**changes))
                    logging.info('Update BitBucket issue #{id}: '
                                 '{key} changes to "{to_value}"'.format(**changes))
                else:
                    changes.update({'from_value': remote_issue.template[key]})
                    logging.info('Update BitBucket issue #{id}: '
                                 '{key} changes from "{from_value}" to "{to_value}"'.format(**changes))
                del remote_issue.template[key]
            for key in template_diff.added():
                # This can only concern "url" and "materials" keys because of __JSON_SCHEMA__
                changes.update({'key': key.upper(),
                                'from_value': 'Not documented'})
                if key == 'materials':
                    for item in remote_issue.template[key]:
                        changes.update({'item': item})
                        logging.info('Update BitBucket issue #{id}: '
                                     '{key} adds "{item}"'.format(**changes))
                    logging.info('Update BitBucket issue #{id}: '
                                 '{key} changes to "{to_value}"'.format(**changes))
                else:
                    changes.update({'to_value': self.template[key]})
                    logging.info('Update BitBucket issue #{id}: '
                                 '{key} changes from "{from_value}" to "{to_value}"'.format(**changes))
                remote_issue.template[key] = self.template[key]
            # Update issue information keeping status unchanged
            success, result = bb.issue.update(issue_id=remote_issue.id,
                                              title=remote_issue.template['title'],
                                              content=self.issue_content(remote_issue.template),
                                              component=remote_issue.template['project'],
                                              priority=remote_issue.template['severity'],
                                              kind=remote_issue.template['type'])
            if success:
                logging.info('Update BitBucket issue #{0}: SUCCESSFUL'.format(result['local_id']))
                self.write()
            else:
                raise Exception('Registration: FAIL')

    def status_update(self, bb, status):
        """
        Close an issue on the BitBucket repo

        :param Bitbucket bb: The BitBucket object (as a :func:`Bitbucket` class instance)
        :param str status: The issue status to apply
        :return: The update status
        :rtype: *boolean*
        :raises Error: If the issue update failed

        """
        success, _ = bb.issue.update(issue_id=self.id, status=status)
        if success:
            print 'Issue #{0} status set to "{1}"'.format(self.id, status)
        else:
            print 'Issue status update failed.'.format(self.id)
        return success


    @staticmethod
    def issue_content(template):
        """
        Format the issue content.

        :param dict template: The issue template to format
        :return: The formatted issue content
        :rtype: *str*

        """
        # Embeds content into dictionary
        content = template.copy()
        if 'materials' in template.keys():
            content['materials'] = ''.join(['![]({0})\n'.format(m) for m in template['materials']])
        else:
            content['materials'] = '*{0}*\n'.format(__FILL_VALUE__)
        if 'url' not in template.keys():
            content['url'] = '*{0}*\n'.format(__FILL_VALUE__)
        content['hash_key'] = template['hash_key'].rjust(len(template['hash_key'])+4)
        content['dset_ids'] = ''.join(['{0}\n'.format(m).rjust(len(m)+5) for m in template['dset_ids']])
        # Format whole content using markdown
        return '\n'.join(['##Description##',
                          '{description}',
                          '##Materials##',
                          '{materials}',
                          '----',
                          '##Landing Page##',
                          '{url}',
                          '##Hash Key##',
                          '{hash_key}',
                          '##Affected Datasets##',
                          '{dset_ids}']).format(**content)

    def write(self):
        """
        Writes an issue template into JSON file using the ``with`` statement.

        """
        try:
            with open(self.path, 'w') as json_file:
                dump(self.template, json_file, indent=0)
            logging.info('Dump new hash key to {0}: SUCCESSFUL'.format(self.path))
        except:
            logging.warning('Registration: FAIL')
            logging.exception('Dump new hash key to {0}: FAILED'.format(self.path))
            sys.exit(1)


class BitBucketIssue(object):
    """
    Encapsulates a remote BitBucket issue context/information and provides related methods to deal with:

    """
    def __init__(self, bb, bb_id):
        self.id = bb_id
        self.raw = None
        self.template = self.get_template(bb)

    def get_template(self, bb):
        """
        Loads an issue template from the BitBucket repository.

        :param Bitbucket bb: The BitBucket object (as a :func:`bb_client.Bitbucket` class instance)
        :returns: The formatted template
        :rtype: *dict*
        :raises Error: If the BitBucket issue cannot be reached
        :raises Error: If the Bitbucket issue parsing fails

        """
        success, self.raw = bb.issue.get(issue_id=self.id)
        if not success:
            logging.warning('Update: FAIL')
            raise Exception('Cannot get BitBucket issue #{0}'.format(self.id))
        try:
            return self.format()
        except:
            logging.warning('Update: FAIL')
            logging.exception('Cannot parse BitBucket issue #{0}'.format(self.id))
            sys.exit(1)

    def format(self):
        """
        Formats a raw issue dictionary from BitBucket to template JSON schema.

        :returns: The formatted issue
        :rtype: *dict*

        """
        content = self.issue_content_parser(self.raw['content']['html'])
        issue = OrderedDict()
        issue[unicode('title')] = self.raw['title']
        issue[unicode('description')] = content['description']
        issue[unicode('project')] = self.raw['component']['name']
        issue[unicode('type')] = self.raw['kind']
        issue[unicode('severity')] = self.raw['priority']
        if content['materials']:
            issue[unicode('materials')] = content['materials']
        if content['url'] != __FILL_VALUE__:
            issue[unicode('url')] = content['url']
        issue[unicode('dset_ids')] = content['dset_ids']
        issue[unicode('hash_key')] = content['hash_key']
        return issue

    @staticmethod
    def issue_content_parser(content):
        """
        Parse a raw issue content from BitBucket and translates it to the template JSON schema.
        :param str content: The issue content
        :returns: The issue(s) information
        :rtype: *dict*

        """
        html_content = BeautifulSoup(content, 'html.parser')
        html_content.prettify()
        # Get issue description from content
        description_content = html_content.find('h2', id='markdown-header-description').find_next_sibling('p')
        description = unicode(description_content.string.strip(' \n\r\t'))
        # Get issue materials urls from content
        materials_content = html_content.find('h2', id='markdown-header-materials').find_next_sibling('p')
        materials = []
        for material in materials_content.find_all('img'):
            materials.append(unicode(material.get('src')))
        # Get issue landing page url from content
        url_content = html_content.find('h2', id='markdown-header-landing-page').find_next_sibling('p')
        if url_content.find("a") is None:
            url = unicode(url_content.string.strip(' \n\r\t'))
        else:
            url = unicode(url_content.find('a').get('href'))
        # Get issue hash key from content
        hash_content = html_content.find('h2', id='markdown-header-hash-key').find_next_sibling('div')
        hash_key = unicode(hash_content.string.strip(' \n\r\t'))
        # Get issue dsets from content
        dset_ids = []
        dset_ids_content = html_content.find('h2', id='markdown-header-affected-datasets').find_next_sibling('div')
        for dset_id in dset_ids_content.string.split('\n'):
            # re.sub('\r', '\n')
            dset_ids.append(unicode(dset_id.strip(' \n\r\t')))
        dset_ids = filter(None, dset_ids)
        return {'description': description,
                'url': url,
                'materials': materials,
                'hash_key': hash_key,
                'dset_ids': dset_ids}

    def validate(self):
        """
        Validates JSON template against predefined JSON schema

        :raises Error: If the template has an invalid JSON schema.
        :raises Error: If the landing page or materials urls cannot be reached.

        """
        try:
            with open(__JSON_SCHEMA_PATH__) as f:
                json_schema = load(f)
            validate(self.template, json_schema)
        except:
            logging.warning('Registration: FAIL')
            logging.exception('{0} has an invalid JSON schema'.format(self.id))
            sys.exit(1)
        # Test landing page and materials URLs
        if 'url' in self.template.keys():
            test_url(self.template['url'])
        if 'materials' in self.template.keys():
            for url in self.template['materials']:
                test_url(url)



