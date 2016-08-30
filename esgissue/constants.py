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
MATERIALS = 'materials'
ISSUES = 'issues'
ISSUE = 'issue'
STATUS = 'status'
STATUS_NEW = 'new'

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