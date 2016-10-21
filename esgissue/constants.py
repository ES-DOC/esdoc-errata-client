import os

# JSON issue schemas full path
JSON_SCHEMA_PATHS = {'create': '{0}/templates/create.json'.format(os.path.dirname(os.path.abspath(__file__))),
                     'update': '{0}/templates/update.json'.format(os.path.dirname(os.path.abspath(__file__))),
                     'close': '{0}/templates/update.json'.format(os.path.dirname(os.path.abspath(__file__))),
                     'retrieve': '{0}/templates/retrieve.json'.format(os.path.dirname(os.path.abspath(__file__)))}

# JSON FIELDS

UID = 'uid'
DATE_CREATED = 'dateCreated'
DATE_UPDATED = 'dateUpdated'
DATE_CLOSED = 'dateClosed'
DATASETS = 'datasets'
URL = 'url'
URLS = 'urls'
MATERIALS = 'materials'
ISSUES = 'issues'
ISSUE = 'issue'
STATUS = 'status'
STATUS_NEW = 'new'
PROJECT = 'project'

# ACTIONS

CREATE = 'create'
UPDATE = 'update'
CLOSE = 'close'
RETRIEVE = 'retrieve'
RETRIEVE_ALL = 'retrieve_all'
ACTIONS = [CREATE, UPDATE, CLOSE, RETRIEVE, RETRIEVE_ALL]


# PATH CONSTANTS
ISSUE_1 = 'issue_'
ISSUE_2 = '.json'
DSET_1 = 'dset_'
DSET_2 = '.txt'

# WebService

WEBSERVICE = 'WebService'
URL_BASE = 'url_base'
HEADERS = {'Content-type': 'application/json', 'Accept': 'text/plain'}

# Regex

REGEX = 'Regex'

# ERROR DICTIONARY
ERROR_DIC = {'title': [1, 'Title field missing or invalid.'], 'description': [2, 'Description field missing or invalid.'],
             'datasets': [3, 'Datasets are missing or invalid.'], 'severity': [4, 'Issue severity missing or invalid.'],
             'project': [5, 'Project field missing or invalid'], 'models': [6, 'Models are missing or invalid'],
             'status': [7, 'Status field missing or invalid'], 'institute': [8, 'Institute field missing or invalid'],
             'materials': [9, 'Materials field missing or invalid'], 'urls': [10, 'URLs are missing or invalid'],
             'id': [11, 'ID missing or invalid'], 'uid': [11, 'UID missing or invalid'],
             'datecreated': [12, 'Creation date missing or invalid'],
             'dateupdated': [13, 'Update date missing or invalid'],
             'dateclosed': [14, 'Closed date missing or invalid']}

