import os

VERSION_NUMBER = '0.1.4'
# JSON issue schemas full path
JSON_SCHEMA_PATHS = {'create': '{0}/templates/create.json'.format(os.path.dirname(os.path.abspath(__file__))),
                     'update': '{0}/templates/update.json'.format(os.path.dirname(os.path.abspath(__file__))),
                     'close': '{0}/templates/close.json'.format(os.path.dirname(os.path.abspath(__file__))),
                     'retrieve': '{0}/templates/retrieve.json'.format(os.path.dirname(os.path.abspath(__file__)))}

# JSON FIELDS

UID = 'uid'
DATE_CREATED = 'dateCreated'
DATE_UPDATED = 'dateUpdated'
DATE_CLOSED = 'dateClosed'
CREATED_BY = 'createdBy'
UPDATED_BY = 'updatedBy'
CLOSED_BY = 'closedBy'
DATASETS = 'datasets'
URL = 'url'
URLS = 'urls'
MATERIALS = 'materials'
ISSUES = 'issues'
ISSUE = 'issue'
STATUS = 'status'
STATUS_NEW = 'new'
STATUS_ONHOLD = 'onhold'
STATUS_WONTFIX = 'wontfix'
STATUS_RESOLVED = 'resolved'
PROJECT = 'mip_era'
COUNT = 'count'

# ACTIONS

CREATE = 'create'
UPDATE = 'update'
CLOSE = 'close'
RETRIEVE = 'retrieve'
RETRIEVE_ALL = 'retrieve_all'
CREDENTIALS = 'credentials'
CHANGEPASS = 'changepass'
CREDRESET = 'credreset'
CREDSET = 'credset'
ACTIONS = [CREATE, UPDATE, CLOSE, RETRIEVE, RETRIEVE_ALL]


# PATH CONSTANTS
ISSUE_1 = 'issue_'
ISSUE_2 = '.json'
DSET_1 = 'dset_'
DSET_2 = '.txt'

# WebService

WEBSERVICE = 'WEBSERVICE'
# URL_BASE = 'url_base'
HEADERS = {'Content-type': 'application/json', 'Accept': 'text/plain'}

# JSON FILE ORDER

INDEX_DICT = {1: 'uid', 2: 'title', 3: 'description', 4: 'mip_era', 5: 'severity', 6: 'status', 7: 'url',
              8: 'materials', 9: 'dateCreated', 10: 'dateUpdated', 11: 'dateClosed'}


# ERROR DICTIONARY
ERROR_DIC = {
                 'title': [1, 'Title field missing or invalid.'],
                 'description': [2, 'Description field missing or invalid.'],
                 'datasets': [3, 'Datasets are missing or invalid.'],
                 'severity': [4, 'Issue severity missing or invalid.'],
                 'mip_era': [5, 'Project field missing or invalid.'],
                 'source_id': [6, 'Models are missing or invalid.'],
                 'status': [7, 'Status field missing or invalid.'],
                 'institution_id': [8, 'Institute field missing or invalid.'],
                 'experiment_id': [9, 'Experiment id missing or invalid'],
                 'materials': [10, 'Materials field missing or invalid.'],
                 'urls': [11, 'URLs are missing or invalid.'],
                 'uid': [12, 'UID missing or invalid.'],
                 'datecreated': [13, 'Creation date missing or invalid.'],
                 'dateupdated': [14, 'Update date missing or invalid.'],
                 'dateclosed': [15, 'Closed date missing or invalid.'],
                 'dataset_incoherent': [16, 'Incoherent dataset id with declared project DRS structure, '
                                            'please make sure both are coherent.'],
                 'authentication': [17, 'Authentication failed. Make sure the credentials are correct.'],
                 'authorization': [18, 'User lacks required privilege. Contact admins for further information.'],
                 'connection_error': [19, 'Connection failed, server probably down. Contact admins.'],
                 'connection_timeout': [20, 'Connection timed out, try again later.'],
                 'multiple_ids': [21, 'Multiple issue ids were provided along with a single file destination, aborting.'],
                 'validation_failed': [22, 'Json file validation failed for an unknown reason, please check said file.'],
                 'unknown_command': [23, 'Command is unknown, check the documentation or help for further information'],
                 'ws_request_failed': [24, 'WS request failed for unknown reason.'],
                 'single_entry_field': [25, 'Field only supports single input per issue declaration.'],
                 'project_not_supported': [26, 'Project indicated in issue is not supported by errata service'],
                 'unknown_error': [99, 'An unknown error has been detected. '
                                       'Please provide the admins with the error stack.']
             }

# MISC

GH_FILE_API = 'https://api.github.com/repos/ESGF/config/contents/publisher-configs/ini/esg.{}.ini?ref=devel'
DOWNLOAD_URL = 'download_url'
URL_BASE = 'URL_BASE'
PATTERN = 'PATTERN'
DATASET_ID = 'dataset_id'
TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
FILE_EXPIRATION_TIME = 15

# WEBSERVICE
URL_BASE = 'https://test-errata-api.es-doc.org'

# URL_BASE = 'http://localhost:5001'
URL_MAP = {'CREATE': '/1/issue/create',
           'UPDATE': '/1/issue/update',
           'CLOSE': '/1/issue/close?uid=',
           'RETRIEVE': '/1/issue/retrieve?uid=',
           'RETRIEVE_ALL': '/1/issue/retrieve-all'
           }

ESDOC_VAR = 'ESDOC_HOME'
# Argparse:

ESGISSUE_GENERAL = """
                    The publication workflow on the ESGF nodes requires to deal with errata issues.
                    The cause behind the version changes has to be published alongside the data: what was updated,
                    retracted or removed, and why. Consequently, the publication of a new version of a dataset has to
                    be motivated by an issue.|n|n

                    "esgissue" allows the referenced data providers to easily create, document, update, close or remove
                    a validated issue.

                    The issue registration always appears prior to the publication process and should be mandatory
                    for additional version, version removal or retraction.|n|n

                    "esgissue" works with both JSON and TXT files. This allows the data provider in charge of ESGF
                    issues to manage one or several JSON templates gathering the issues locally.|n|n

                    See full documentation on https://es-doc.github.io/esdoc-errata-client/"""
EPILOG = """Developed by:|n
         Levavasseur, G. (UPMC/IPSL - glipsl@ipsl.jussieu.fr)|n
         Bennasser, A. (UPMC/IPSL - abennasser@ipsl.jussieu.fr"""

OPTIONAL = 'Optional arguments'
POSITIONAL = 'Positional arguments'
HELP = 'Show this help message and exit'
VERSION_HELP = 'Software version'
ISSUE_ACTIONS = 'Issue actions'
LOG_HELP = 'Logfile directory. If not, standard output is used'
ISSUE_HELP = "Required path of the issue JSON template."
DSETS_HELP = "Required path of the affected dataset IDs list."
CREATE_DESC = """esgissue create" registers one or several issues on a defined errata repository. The data
                    provider submits one or several JSON files gathering all issues information with a list of all
                    affected dataset IDs (see http://esgissue.readthedocs.org/configuration.html to get a template).|n|n

                    This action returns to the corresponding local JSON template:|n
                    - the ESGF issue ID (as UUID),|n
                    - the creation date,|n
                    - the last updated date (same as the creation date).|n|n

                    The issue registration sets:|n
                    - the issue status to "new",|n

                    SEE http://esgissue.readthedocs.org/usage.html TO FOLLOW ALL REQUIREMENTS TO REGISTER AN ISSUE.|n|n

                    See "esgissue -h" for global help."""
CREATE_HELP = """Creates ESGF issues from a JSON template to the errata database.|n
                See "esgissue create -h" for full help."""
UPDATE_DESC = """"esgissue update" updates one or several issues on a defined errata repository. The data
                    provider submits one or several JSON files gathering all issues information with a list of all
                    affected dataset IDs (see http://esgissue.readthedocs.org/configuration.html to get a template).|n|n

                    This action returns the time and date of the update to the corresponding local JSON template.|n|n

                    SEE http://esgissue.readthedocs.org/usage.html TO FOLLOW ALL REQUIREMENTS TO UPDATE AN ISSUE.|n|n

                    See "esgissue -h" for global help."""
UPDATE_HELP = """Updates ESGF issues from a JSON template to the errata database.|n
                See "esgissue update -h" for full help."""
CLOSE_DESC = """"esgissue close" closes one or several issues on a defined errata database. The data
                    provider submits one or several JSON files gathering all issues information with a list of all
                    affected dataset IDs (see http://esgissue.readthedocs.org/configuration.html to get a template).|n|n

                    This action returns the date of closure to the corresponding local JSON template (which is the same
                    as the date of the last update).|n|n

                    SEE http://esgissue.readthedocs.org/usage.html TO FOLLOW ALL REQUIREMENTS TO CLOSE AN ISSUE.|n|n

                    See "esgissue -h" for global help."""
CLOSE_HELP = """Closes ESGF issues on the errata repository.|n
                See "esgissue close -h" for full help."""
RETRIEVE_DESC = """"esgissue retrieve" retrieves one or several issues from a defined errata repository. The data
                    provider submits one or several issue number he wants to retrieve and optional paths to write
                    them.|n|n

                    This action rebuilds:|n
                    - the corresponding issue template as a JSON file,|n
                    - the attached affected datasets list as a TEXT file.|n|n

                    SEE http://esgissue.readthedocs.org/usage.html TO FOLLOW ALL REQUIREMENTS TO RETRIEVE AN ISSUE.|n|n

                    See "esgissue -h" for global help."""
RETRIEVE_HELP = """Retrieves ESGF issues from the errata repository to a JSON template.|n
                See "esgissue retrieve -h" for full help."""
CREDRESET_DESC = """"esgissue credreset" allows users to interact with their established credentials.
            It mainly allows users who have locally saved credentials to modify their pass-phrase or reset it by deleting
            them and having to redo the credentials input all over again. This can be useful in case someone forgets the passphrase
            set before.

            See "esgissue -h" for global help."""
CREDRESET_HELP = """Helps user interact with registered credentials.|n
                    See "esgissue credreset -h" for full help."""

CREDSET_DESC = """"esgissue credset" allows users to establish new credentials. Just like cred-reset except this tool allows users
            to delete any previously stored information and establish new ones.

            See "esgissue -h" for global help."""
CREDSET_HELP = """Helps user register credentials.|n
                    See "esgissue credset -h" for full help."""

CHANGEPASS_DESC = """"esgissue credentials" allows users to interact with their established credentials.
            It mainly allows users who have locally saved credentials to modify their pass-phrase or reset it by deleting
            them and having to redo the credentials input all over again. This can be useful in case someone forgets the passphrase
            set before.

            See "esgissue -h" for global help."""
CHANGEPASS_HELP = """Helps user change passphrase for registered credentials.|n
                    See "esgissue changepass -h" for full help."""
