#!/usr/bin/env python
"""
   :platform: Unix
   :synopsis: Manages ESGF issues on BitBucket repository.

"""

# Module imports
import os
import logging
import textwrap
import argparse
from issue_handler import ESGFIssue, BitBucketIssue
from datetime import datetime
from bb_client import Bitbucket
from argparse import HelpFormatter
from utils import config_parse

# Program version
__version__ = 'v{0} {1}'.format('0.1', datetime(year=2016, month=01, day=15).strftime("%Y-%d-%m"))


class MultilineFormatter(HelpFormatter):
    """
    Custom formatter class for argument parser to use with the Python
    `argparse <https://docs.python.org/2/library/argparse.html>`_ module.

    """

    def __init__(self, prog):
        # Overload the HelpFormatter class.
        super(MultilineFormatter, self).__init__(prog, max_help_position=60, width=100)

    def _fill_text(self, text, width, indent):
        # Rewrites the _fill_text method to support multiline description.
        text = self._whitespace_matcher.sub(' ', text).strip()
        multiline_text = ''
        paragraphs = text.split('|n|n ')
        for paragraph in paragraphs:
            lines = paragraph.split('|n ')
            for line in lines:
                formatted_line = textwrap.fill(line, width,
                                               initial_indent=indent,
                                               subsequent_indent=indent) + '\n'
                multiline_text += formatted_line
            multiline_text += '\n'
        return multiline_text

    def _split_lines(self, text, width):
        # Rewrites the _split_lines method to support multiline helps.
        text = self._whitespace_matcher.sub(' ', text).strip()
        lines = text.split('|n ')
        multiline_text = []
        for line in lines:
            multiline_text.append(textwrap.fill(line, width))
        multiline_text[-1] += '\n'
        return multiline_text


def get_args():
    """
    Returns parsed command-line arguments. See ``esgissue -h`` for full description.

    :returns: The corresponding ``argparse`` Namespace

    """
    __GLOBAL_DESCRIPTION__ = """The publication workflow on the ESGF nodes requires to deal with errata issues.
                    The background of the version changes has to be published alongside the data: what was updated,
                    retracted or removed, and why. Consequently, the publication of a new version of a dataset has to
                    be motivated by an issue.|n|n

                    "esgissue" allows the referenced data providers to easily create, document, update, close or remove
                    a validated issue. "esgissue" relies on the BitBucket Python-API to deal with the BitBucket private
                    repository giving read access to ESGF issues for community.|n|n

                    The issue registration always appears prior to the publication process and should be mandatory
                    for additional version, version removal or retraction.|n|n

                    "esgissue" works with a JSON file. This allows the data provider in charge of ESGF issues
                    to manage one or several JSON templates gathering the issues locally.|n|n

                    See full documentation on http://esgissue.readthedocs.org/"""
    __TEMPLATE_HELP__ = """Path of the issue JSON template."""
    __DSETS_HELP__ = """Path of the dataset IDs list corresponding to the issue."""
    __HELP__ = """Show this help message and exit."""
    __BB_USER_HELP__ = """BitBucket username. If not, the $BB_USER environment |n
                       variable is used."""
    __BB_PASSWORD_HELP__ = """BitBucket password. If not the $BB_PASSWORD environment |n
                           variable is used."""
    __LOG_HELP__ = """Logfile directory. If not, standard output is used."""
    parser = argparse.ArgumentParser(
        prog='esgissue',
        description= __GLOBAL_DESCRIPTION__,
        formatter_class=MultilineFormatter,
        add_help=False,
        epilog="""Developed by:|n
                  Levavasseur, G. (UPMC/IPSL - glipsl@ipsl.jussieu.fr)""")
    parser._optionals.title = "Optional arguments"
    parser._positionals.title = "Positional arguments"
    parser.add_argument(
        '-h', '--help',
        action='help',
        help=__HELP__)
    parser.add_argument(
        '-V',
        action='version',
        version='%(prog)s ({0})'.format(__version__),
        help="""Program version.""")
    subparsers = parser.add_subparsers(
        title='Issue actions',
        dest='command',
        metavar='',
        help='')
    create = subparsers.add_parser(
        'create',
        prog='esgissue create',
        description=""""esgissue create" registers one or several issues and returns the corresponding issue numbers.|n|n

                    The data provider submits an JSON file gathering all issues information (see
                    http://esgissue.readthedocs.org/configuration.html to get a template). The issues
                    with a status set to "new" are created on the BitBucket repository. Otherwise the issue attributes
                    are updated/overwritten from the template to the BitBucket repository. In both cases the
                    issue ID/number is returned from the BitBucket repository and overwritten to the JSON
                    template.|n|n

                    If one or several issue ID (i.e., the issue(s) key(s) from the template) are submitted, the
                    corresponding issues are created if their status are set to "new". Otherwise the issue(s)
                    attributes are updated/overwritten on the BitBucket repository. In both cases the issues IDs are
                    returned from the BitBucket repository.|n|n

                    If another flag is set to True, only the corresponding issue information is updated/overwritten.
                    The other flags are unchanged even they are different between the BitBucket repository and
                    the JSON template.|n|n

                    Usage examples:|n|n

                    $> esgissue push myissues.json|n
                    -> Creates all issues with "status = new" on the BitBucket repository,|n
                    -> Updates all issues with "status != new" from the template to the BitBucket repository,|n
                    -> (Over)writes issues IDs from the Bitbucket repository to the template in both cases.|n|n

                    $> esgissue push myissues.json --issue-id ID|n
                    -> Creates the issue #ID if "status = new" on the BitBucket repository,|n
                    -> Updates the issue #ID if "status != new" from the template to the BitBucket repository,|n
                    -> Overwrites the issue ID from the BitBucket repository to the template in both cases.|n|n

                    $> esgissue push myissues.json --issue-id ID --status [...]|n
                    -> Updates the issue #ID information from the template to the BitBucket repository,|n
                    -> Overwrites the issue ID from the BitBucket repository to the template.|n|n

                    An ESGF issue is defined by:|n|n

                    - The project name affected by the issue, |n
                    - A short but clear title (please avoid purposeless title as "Issue 1"),|n
                    - A precise and concise description of the issue that makes sense for end users (please avoid brief
                    description as "wrong data"),|n
                    - The BitBucket username of the issue responsible (i.e., the data provider in charge of the
                    issue),|n
                    - The issue type. The accepted terms are:|n
                    -- bug: the new version will correct an error in comparison with the previous version,|n
                    -- enhancement: the new version will improve or complete the previous version.|n
                    - The issue severity level. The accepted terms are:|n
                    -- minor: the issue concerns file management (e.g., period extension, removal, etc.),|n
                    -- major: the issue concerns metadata without undermining the values of the
                    involved variable,|n
                    -- critical: the issue concerns single point variable or axis values,|n
                    -- blocker: the issue concerns the variable or axis values undermining the analysis. The use of
                    this data is strongly discouraged.|n
                    - The issue status. The accepted terms are:|n
                    -- new: the issue has been registered,|n
                    -- on hold: the issue is in the care of the corresponding data provider,|n
                    -- wontfix: the issue cannot be fixed/corrected, |n
                    -- closed: the issue has been fixed leading to a new dataset version.|n
                    - The issue landing page with the complete description of the issue (or the issues list of the
                    corresponding institute/model).|n
                    - The list of URLs pointing to issue materials (e.g., pictures, graphs, documents).|n|n

                    See "esgissue -h" for global help.""",
        formatter_class=MultilineFormatter,
        help="""Creates/updates ESGF issues from a JSON template to the BitBucket repository. See |n
             "esgissue push -h" for full help.""",
        add_help=False)
    create._optionals.title = "Optional arguments"
    create._positionals.title = "Positional arguments"
    create.add_argument(
        'template',
        nargs='?',
        metavar='PATH/issue.json',
        type=argparse.FileType('r'),
        help=__TEMPLATE_HELP__)
    create.add_argument(
        'dsets',
        nargs='?',
        metavar='PATH/dsets.list',
        type=argparse.FileType('r'),
        help=__DSETS_HELP__)
    create.add_argument(
        '-i',
        metavar='$PWD/config.ini',
        type=str,
        default='{0}/config.ini'.format(os.getcwd()),
        help="""Path of configuration INI file.""")
    create.add_argument(
        '--log',
        metavar='$PWD',
        type=str,
        const=os.getcwd(),
        nargs='?',
        help=__LOG_HELP__)
    create.add_argument(
        '-v',
        action='store_true',
        default=False,
        help="""Verbose mode.""")
    create.add_argument(
        '-h', '--help',
        action='help',
        help=__HELP__)

    update = subparsers.add_parser(
        'update',
        prog='esgissue update',
        description=""""esgissue update" registers one or several issues and returns the corresponding issue numbers.|n|n

                    The data provider submits an JSON file gathering all issues information (see
                    http://esgissue.readthedocs.org/configuration.html to get a template). The issues
                    with a status set to "new" are created on the BitBucket repository. Otherwise the issue attributes
                    are updated/overwritten from the template to the BitBucket repository. In both cases the
                    issue ID/number is returned from the BitBucket repository and overwritten to the JSON
                    template.|n|n

                    If one or several issue ID (i.e., the issue(s) key(s) from the template) are submitted, the
                    corresponding issues are created if their status are set to "new". Otherwise the issue(s)
                    attributes are updated/overwritten on the BitBucket repository. In both cases the issues IDs are
                    returned from the BitBucket repository.|n|n

                    If another flag is set to True, only the corresponding issue information is updated/overwritten.
                    The other flags are unchanged even they are different between the BitBucket repository and
                    the JSON template.|n|n

                    Usage examples:|n|n

                    $> esgissue push myissues.json|n
                    -> Creates all issues with "status = new" on the BitBucket repository,|n
                    -> Updates all issues with "status != new" from the template to the BitBucket repository,|n
                    -> (Over)writes issues IDs from the Bitbucket repository to the template in both cases.|n|n

                    $> esgissue push myissues.json --issue-id ID|n
                    -> Creates the issue #ID if "status = new" on the BitBucket repository,|n
                    -> Updates the issue #ID if "status != new" from the template to the BitBucket repository,|n
                    -> Overwrites the issue ID from the BitBucket repository to the template in both cases.|n|n

                    $> esgissue push myissues.json --issue-id ID --status [...]|n
                    -> Updates the issue #ID information from the template to the BitBucket repository,|n
                    -> Overwrites the issue ID from the BitBucket repository to the template.|n|n

                    An ESGF issue is defined by:|n|n

                    - The project name affected by the issue, |n
                    - A short but clear title (please avoid purposeless title as "Issue 1"),|n
                    - A precise and concise description of the issue that makes sense for end users (please avoid brief
                    description as "wrong data"),|n
                    - The BitBucket username of the issue responsible (i.e., the data provider in charge of the
                    issue),|n
                    - The issue type. The accepted terms are:|n
                    -- bug: the new version will correct an error in comparison with the previous version,|n
                    -- enhancement: the new version will improve or complete the previous version.|n
                    - The issue severity level. The accepted terms are:|n
                    -- minor: the issue concerns file management (e.g., period extension, removal, etc.),|n
                    -- major: the issue concerns metadata without undermining the values of the
                    involved variable,|n
                    -- critical: the issue concerns single point variable or axis values,|n
                    -- blocker: the issue concerns the variable or axis values undermining the analysis. The use of
                    this data is strongly discouraged.|n
                    - The issue status. The accepted terms are:|n
                    -- new: the issue has been registered,|n
                    -- on hold: the issue is in the care of the corresponding data provider,|n
                    -- wontfix: the issue cannot be fixed/corrected, |n
                    -- closed: the issue has been fixed leading to a new dataset version.|n
                    - The issue landing page with the complete description of the issue (or the issues list of the
                    corresponding institute/model).|n
                    - The list of URLs pointing to issue materials (e.g., pictures, graphs, documents).|n|n

                    See "esgissue -h" for global help.""",
        formatter_class=MultilineFormatter,
        help="""Creates/updates ESGF issues from a JSON template to the BitBucket repository. See |n
             "esgissue push -h" for full help.""",
        add_help=False)
    update._optionals.title = "Optional arguments"
    update._positionals.title = "Positional arguments"
    update.add_argument(
        'template',
        nargs='?',
        metavar='PATH',
        type=argparse.FileType('r'),
        help=__TEMPLATE_HELP__)
    update.add_argument(
        '-i',
        metavar='$PWD/config.ini',
        type=str,
        default='{0}/config.ini'.format(os.getcwd()),
        help="""Path of configuration INI file.""")
    update.add_argument(
        '--log',
        metavar='$PWD',
        type=str,
        const=os.getcwd(),
        nargs='?',
        help=__LOG_HELP__)
    update.add_argument(
        '-v',
        action='store_true',
        default=False,
        help="""Verbose mode.""")
    update.add_argument(
        '-h', '--help',
        action='help',
        help=__HELP__)

    pull = subparsers.add_parser(
        'pull',
        prog='esgissue pull',
        description=""""esgissue pull" retrieves or displays one or several issues from the BitBucket repository.|n|n

                    If one or several issue ID is(are) submitted, the corresponding issue(s) is(are) returned from the
                    BitBucket repository.|n|n

                    If a JSON file is submitted (see http://esgissue.readthedocs.org/configuration.html) the issues
                    information are overwritten from the BitBucket repository to the JSON template (as the opposite of
                    "esgissue push" mode).|n|n

                    If another flag is set to True (e.g., --status), only the corresponding issue information is
                    displayed or overwritten to the JSON template. The other flags are unchanged to the template even
                    they are different between the BitBucket repository and the template.|n|n

                    Usage examples:|n|n

                    esgissue pull|n
                    -> Gets all issues from the BitBucket repository|n|n

                    esgissue pull --issue-id ID|n
                    -> Gets issue #ID from the BitBucket repository|n|n

                    esgissue pull --issue-id ID --project [...]|n
                    -> Gets issue #ID information from the BitBucket repository|n|n

                    esgissue pull --template myissues.json|n
                    -> (Over)writes all issues from the BitBucket repository to the template|n|n

                    esgissue pull --template --issue-id|n
                    -> (Over)write issue #ID from the BitBucket repository to the template|n|n

                    esgissue pull --template --issue-id --project|n
                    -> (Over)write issue #ID information from the BitBucket repository to the template|n|n

                    See "esgissue -h" for global help.""",
        formatter_class=MultilineFormatter,
        help="""Retrieves ESGF issues from the BitBucket repository to a JSON template. See |n
             "esgissue pull -h" for full help.""",
        add_help=False)
    pull._optionals.title = "Optional arguments"
    pull._positionals.title = "Positional arguments"
    pull.add_argument(
        '--template',
        nargs='?',
        metavar='PATH',
        type=argparse.FileType('r'),
        help=__TEMPLATE_HELP__)
    pull.add_argument(
        '--local-id',
        nargs='+',
        metavar='ID',
        type=str,
        help="""The issue identifier/number to retrieve.""")
    pull.add_argument(
        '--project',
        action='store_true',
        default=False,
        help="""Gets the project name affected by the issue.""")
    pull.add_argument(
        '--title',
        action='store_true',
        default=False,
        help="""Gets the issue title.""")
    pull.add_argument(
        '--description',
        action='store_true',
        default=False,
        help="""Gets the issue description.""")
    pull.add_argument(
        '--type',
        action='store_true',
        default=False,
        help="""Gets the issue type.""")
    pull.add_argument(
        '--severity',
        action='store_true',
        default=False,
        help="""Gets the issue severity level.""")
    pull.add_argument(
        '--status',
        action='store_true',
        default=False,
        help="""Gets the issue status.""")
    pull.add_argument(
        '--url',
        action='store_true',
        default=False,
        help="""Gets the issue landing page URL.""")
    pull.add_argument(
        '--materials',
        action='store_true',
        default=False,
        help="""Gets the URLs list pointing to issue materials.""")
    pull.add_argument(
        '--bb-user',
        metavar='USERNAME',
        default=os.getenv("BB_USER"),
        type=str,
        help=__BB_USER_HELP__)
    pull.add_argument(
        '--bb-passwd',
        metavar='PASSWORD',
        default=os.getenv("BB_PASSWORD"),
        type=str,
        help=__BB_PASSWORD_HELP__)
    pull.add_argument(
        '--log',
        metavar='$PWD',
        type=str,
        const=os.getcwd(),
        nargs='?',
        help=__LOG_HELP__)
    pull.add_argument(
        '-v',
        action='store_true',
        default=False,
        help="""Verbose mode.""")
    pull.add_argument(
        '-h', '--help',
        action='help',
        help=__HELP__)

    remove = subparsers.add_parser(
        'remove',
        prog='esgissue remove',
        description=""""esgissue remove" deletes an existing issue from the BitBucket repository. To use with
                    caution !|n|n

                    If one or several issue ID is(are) submitted, the corresponding issue(s) is(are) deleted from the
                    BitBucket repository. If not, all issues are deleted.|n|n

                    If a JSON file is submitted (see http://esgissue.readthedocs.org/configuration.html) the issue(s)
                    (is)are deleted from the JSON template.|n|n

                    Usage examples:|n|n

                    esgissue remove|n
                    -> Deletes all issues assigned to the data provider from the BitBucket repository|n|n

                    esgissue remove --issue-id ID|n
                    -> Deletes issue #ID from the BitBucket repository|n|n

                    esgissue remove --template --issue-id #ID|n
                    -> Deletes issue #ID from the BitBucket repository and the JSON template|n|n

                    esgissue remove --template|n
                    -> Deletes all issues assigned to the data provider from the BitBucket repository and the JSON
                    template|n|n

                    See "esgissue -h" for global help.""",
        formatter_class=MultilineFormatter,
        help="""Deletes existing ESGF issues. Please just use in case of mistakes, a closed issue |n
             don't have to be removed. See "esgissue remove -h" for full help""",
        add_help=False)
    remove._optionals.title = "Optional arguments"
    remove._positionals.title = "Positional arguments"
    remove.add_argument(
        '--template',
        nargs='?',
        metavar='PATH',
        type=argparse.FileType('r'),
        help=__TEMPLATE_HELP__)
    remove.add_argument(
        '--local-id',
        nargs='+',
        metavar='ID',
        type=str,
        help="""The issue identifier/number to delete.""")
    remove.add_argument(
        '--bb-user',
        metavar='USERNAME',
        default=os.getenv("BB_USER"),
        type=str,
        help=__BB_USER_HELP__)
    remove.add_argument(
        '--bb-passwd',
        metavar='PASSWORD',
        default=os.getenv("BB_PASSWORD"),
        type=str,
        help=__BB_PASSWORD_HELP__)
    remove.add_argument(
        '--log',
        metavar='$PWD',
        type=str,
        const=os.getcwd(),
        nargs='?',
        help=__LOG_HELP__)
    remove.add_argument(
        '-v',
        action='store_true',
        default=False,
        help="""Verbose mode.""")
    remove.add_argument(
        '-h', '--help',
        action='help',
        help=__HELP__)

    return parser.parse_args()


def init_logging(logdir, level):
    """
    Initiates the logging configuration (output, message formatting).
    In the case of a logfile, the logfile name is unique and formatted as follows:
    ``name-YYYYMMDD-HHMMSS-JOBID.log``

    :param str logdir: The relative or absolute logfile directory. If ``None`` the standard \
    output is used.

    """
    __LOG_LEVELS__ = {'CRITICAL': logging.CRITICAL,
                      'ERROR': logging.ERROR,
                      'WARNING': logging.WARNING,
                      'INFO': logging.INFO,
                      'DEBUG': logging.DEBUG,
                      'NOTSET': logging.NOTSET}
    logging.getLogger("requests").setLevel(logging.CRITICAL)  # Disables logging message from request library
    if logdir:
        logfile = 'esgissue-{0}-{1}.log'.format(datetime.now().strftime("%Y%m%d-%H%M%S"),
                                                os.getpid())
        if not os.path.isdir(logdir):
            os.makedirs(logdir)
        logging.basicConfig(filename=os.path.join(logdir, logfile),
                            level=__LOG_LEVELS__[level],
                            format='%(asctime)s %(levelname)s %(message)s',
                            datefmt='%Y/%m/%d %I:%M:%S %p')
    else:
        logging.basicConfig(level=__LOG_LEVELS__[level],
                            format='%(asctime)s %(levelname)s %(message)s',
                            datefmt='%Y/%m/%d %I:%M:%S %p')


def bb_connect(username, password, team, repo):
    """
    Tries connection to the BitBucket repository.
    :param username: The BitBucket login
    :param password: The BitBucket corresponding password
    :param team: The BitBucket team to connect
    :param repo: The BitBucket repository to reach
    :raises Error: If the connection fails because of invalid input

    """
    bb_link = {'team': cfg.get('BITBUCKET', 'bb_team'),
               'repo': cfg.get('BITBUCKET', 'bb_repo').lower()}
    logging.info('Connection to the BitBucket repository "{team}/{repo}"'.format(**bb_link))
    bb = Bitbucket(username, password, team, repo)
    if bb.repository.get()[0]:
        logging.info('Result: SUCCESSFUL')
    else:
        logging.warning('Result: FAILED')
        raise Exception('Invalid BitBucket username, password, team or repository name.')


# Main entry point for stand-alone call.
if __name__ == "__main__":
    # Get command-line arguments
    args = get_args()
    # Parse configuration INI file
    cfg = config_parse(args.i)
    # Init logging
    init_logging(args.log, cfg.get('DEFAULT', 'log_level'))
    # Connection to the BitBucket repository
    bb_connect(username=cfg.get('BITBUCKET', 'bb_login'),
               password=cfg.get('BITBUCKET', 'bb_password'),
               team=cfg.get('BITBUCKET', 'bb_team'),
               repo=cfg.get('BITBUCKET', 'bb_repo'))
    # Run command
    if args.command == 'create':
        local_issue = ESGFIssue(args.template, args.dsets)
        local_issue.validate()  # Validate issue template against JSON schema
        exit()
        local_issue.create(bb)  # Create issue on BitBucket repository
        #issue.push(hs)    # Push issue information to Handle Service
    elif args.command == 'update':
        local_issue = ESGFIssue(args.template, args.dsets)
        local_issue.validate()  # Validate issue template against JSON schema
        remote_issue = BitBucketIssue(bb, local_issue.get_remote_id(bb))  # Get the corresponding BitBucket issue
        remote_issue.validate()  # Validate BitBucket issue against JSON schema
        local_issue.update(bb, remote_issue)  # Update issue information on BitBucket repository
        #issue.push(hs)    # Push new issue information to update Handle Service metadata
#    elif args.command == 'get':
        # To retrieve one or several JSON template from the BitBucket repository
        # giving the BitBucket issue number/id.
