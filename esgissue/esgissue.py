#!/usr/bin/env python
"""
   :platform: Unix
   :synopsis: Manages ESGF issues on BitBucket repository.

"""

# TODO: Add possibility to scan a directory of JSON issues to handle

# Module imports
import os
import sys
import logging
import argparse
from esgfpid import ESGF_PID_connector
from issue_handler import ESGFIssue, GitHubIssue
from datetime import datetime
from utils import MultilineFormatter, config_parse, init_logging, split_line
from github3 import GitHub

# Program version
__version__ = 'v{0} {1}'.format('0.1', datetime(year=2016, month=04, day=11).strftime("%Y-%d-%m"))

# Rabbit MQ unsent messages directory
__UNSENT_MESSAGES_DIR__ = "{0}/unsent_rabbit_messages".format(os.path.dirname(os.path.abspath(__file__)))


def get_args():
    """
    Returns parsed command-line arguments. See ``esgissue -h`` for full description.

    :returns: The corresponding ``argparse`` Namespace

    """
    __TEMPLATE_HELP__ = """Required path of the issue JSON template."""
    __DSETS_HELP__ = """Required path of the dataset IDs list corresponding to the issue."""
    __HELP__ = """Show this help message and exit."""
    __BB_USER_HELP__ = """BitBucket username. If not, the $BB_USER environment |n
                       variable is used."""
    __BB_PASSWORD_HELP__ = """BitBucket password. If not the $BB_PASSWORD environment |n
                           variable is used."""
    __LOG_HELP__ = """Logfile directory. If not, standard output is used."""
    parser = argparse.ArgumentParser(
        prog='esgissue',
        description="""The publication workflow on the ESGF nodes requires to deal with errata issues.
                    The background of the version changes has to be published alongside the data: what was updated,
                    retracted or removed, and why. Consequently, the publication of a new version of a dataset has to
                    be motivated by an issue.|n|n

                    "esgissue" allows the referenced data providers to easily create, document, update, close or remove
                    a validated issue. "esgissue" relies on the GitHub API v3 to deal with private repositories.|n|n

                    The issue registration always appears prior to the publication process and should be mandatory
                    for additional version, version removal or retraction.|n|n

                    "esgissue" works with both JSON and TXT files. This allows the data provider in charge of ESGF
                    issues to manage one or several JSON templates gathering the issues locally.|n|n

                    See full documentation on http://esgissue.readthedocs.org/""",
        formatter_class=MultilineFormatter,
        add_help=False,
        epilog="""Developed by:|n
                  Levavasseur, G. (UPMC/IPSL - glipsl@ipsl.jussieu.fr)|n
                  Bennasser, A. (UPMC/IPSL - abennasser@ipsl.jussieu.fr""")
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
        description=""""esgissue create" registers one or several issues. and returns:|n
                    - the corresponding issue number,
                    - |n
                    |n|n

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
    create._optionals.title = "Arguments"
    create._positionals.title = "Positional arguments"
    create.add_argument(
        '-I',
        nargs='?',
        required=True,
        metavar='PATH/issue.json',
        type=argparse.FileType('r'),
        help=__TEMPLATE_HELP__)
    create.add_argument(
        '-D',
        nargs='?',
        required=True,
        metavar='PATH/dsets.list',
        type=argparse.FileType('r'),
        help=__DSETS_HELP__)
    create.add_argument(
        '-i',
        metavar='/esg/config/esgcet/.',
        type=str,
        default='/esg/config/esgcet/.',
        help="""Initialization/configuration directory containing "esg.ini"|n
                and "esg.<project>.ini" files. If not specified, the usual|n
                datanode directory is used.""")
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
        '-I',
        nargs='?',
        required=True,
        metavar='PATH/issue.json',
        type=argparse.FileType('r'),
        help=__TEMPLATE_HELP__)
    update.add_argument(
        '-D',
        nargs='?',
        required=True,
        metavar='PATH/dsets.list',
        type=argparse.FileType('r'),
        help=__DSETS_HELP__)
    update.add_argument(
        '-i',
        metavar='/esg/config/esgcet/.',
        type=str,
        default='/esg/config/esgcet/.',
        help="""Initialization/configuration directory containing "esg.ini"|n
                and "esg.<project>.ini" files. If not specified, the usual|n
                datanode directory is used.""")
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

    close = subparsers.add_parser(
        'close',
        prog='esgissue close',
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
    close._optionals.title = "Optional arguments"
    close._positionals.title = "Positional arguments"
    close.add_argument(
        '-I',
        nargs='?',
        required=True,
        metavar='PATH/issue.json',
        type=argparse.FileType('r'),
        help=__TEMPLATE_HELP__)
    close.add_argument(
        '-D',
        nargs='?',
        required=True,
        metavar='PATH/dsets.list',
        type=argparse.FileType('r'),
        help=__DSETS_HELP__)
    close.add_argument(
        '-i',
        metavar='/esg/config/esgcet/.',
        type=str,
        default='/esg/config/esgcet/.',
        help="""Initialization/configuration directory containing "esg.ini"|n
                and "esg.<project>.ini" files. If not specified, the usual|n
                datanode directory is used.""")
    close.add_argument(
        '--log',
        metavar='$PWD',
        type=str,
        const=os.getcwd(),
        nargs='?',
        help=__LOG_HELP__)
    close.add_argument(
        '-v',
        action='store_true',
        default=False,
        help="""Verbose mode.""")
    close.add_argument(
        '-h', '--help',
        action='help',
        help=__HELP__)

    retrieve = subparsers.add_parser(
        'retrieve',
        prog='esgissue retrieve',
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
    retrieve._optionals.title = "Optional arguments"
    retrieve._positionals.title = "Positional arguments"
    retrieve.add_argument(
        '-N',
        metavar='INT',
        type=int,
        required=True,
        help='GitHub issue number to retrieve')
    retrieve.add_argument(
        '-I',
        nargs='?',
        metavar='$PWD/issue.json',
        default='{0}/issue.json'.format(os.getcwd()),
        type=argparse.FileType('w'),
        help=__TEMPLATE_HELP__)
    retrieve.add_argument(
        '-D',
        nargs='?',
        metavar='$PWD/dsets.list',
        default='{0}/dsets.list'.format(os.getcwd()),
        type=argparse.FileType('w'),
        help=__DSETS_HELP__)
    retrieve.add_argument(
        '-i',
        metavar='/esg/config/esgcet/.',
        type=str,
        default='/esg/config/esgcet/.',
        help="""Initialization/configuration directory containing "esg.ini"|n
                and "esg.<project>.ini" files. If not specified, the usual|n
                datanode directory is used.""")
    retrieve.add_argument(
        '--log',
        metavar='$PWD',
        type=str,
        const=os.getcwd(),
        nargs='?',
        help=__LOG_HELP__)
    retrieve.add_argument(
        '-v',
        action='store_true',
        default=False,
        help="""Verbose mode.""")
    retrieve.add_argument(
        '-h', '--help',
        action='help',
        help=__HELP__)
    return parser.parse_args()


def github_connector(username, password, team, repo):
    """
    Instantiates the GitHub repository connector if granted for user.

    :param username: The GitHub login
    :param password: The GitHub password
    :param team: The GitHub team to connect
    :param repo: The GitHub repository to reach
    :returns: The GitHub repository connector and the GitHub user login
    :rtype: *tuple* of (*str*, *github3.repos.repo*)
    :raises Error: If the GitHub connection fails because of invalid inputs

    """
    gh_link = {'team': cfg.get('issues', 'gh_team'),
               'repo': cfg.get('issues', 'gh_repo').lower()}
    logging.info('Connection to the GitHub repository "{team}/{repo}"'.format(**gh_link))
    try:
        gh_user = GitHub(username, password)
        gh_repo = gh_user.repository(team, repo.lower())
        logging.info('Result: SUCCESSFUL')
        return username, gh_repo
    except:
        logging.exception('Result: FAILED // Access denied')
        sys.exit(1)


def pid_connector(prefix, url_messaging_service, messaging_exchange, rabbit_username,
                  rabbit_password, successful_messages=True):
    """
    Instantiates the PID Handle Service connector if granted for user.

    :param str prefix: The PID prefix to use
    :param str url_messaging_service: The Handle Service URL
    :param str messaging_exchange: The message header
    :param str rabbit_username: The RabbitMQ username
    :param str rabbit_password: The RabbitMQ password
    :param boolean successful_messages: True to store successful messages
    :returns: The Handle Service connector
    :rtype: *ESGF_PID_connector*
    :raises Error: If the Handle Service connection fails because of invalid inputs

    """
    logging.info('Connection to the RabbitMQ Server of the Handle Service')
    try:
        if not os.path.isdir(__UNSENT_MESSAGES_DIR__):
            os.mkdir(__UNSENT_MESSAGES_DIR__)
        pid = ESGF_PID_connector(prefix=prefix,
                                 url_messaging_service=url_messaging_service,
                                 messaging_exchange=messaging_exchange,
                                 data_node='foo.fr',
                                 thredds_service_path='/what/ever/',
                                 solr_url='http://i-will.not/be/used',
                                 rabbit_username=rabbit_username,
                                 rabbit_password=rabbit_password,
                                 directory_unsent_messages=__UNSENT_MESSAGES_DIR__,
                                 store_successful_messages=successful_messages)
        logging.info('Result: SUCCESSFUL')
        return pid
    except:
        logging.exception('Result: FAILED // Access denied')
        sys.exit(1)


def get_projects(config):
    """
    Gets project options from esg.ini file.

    :param dict config: The configuration file parser
    :returns: The project options
    :rtype: *list*

    """
    project_options = split_line(config.get('DEFAULT', 'project_options'), sep='\n')
    return [option[0].upper() for option in map(lambda x: split_line(x), project_options[1:])]


def get_descriptions(gh):
    """
    Gets description strings from all registered GitHub issues.

    :param GitHubObj gh: The GitHub repository connector (as a :func:`github3.repos.repo` class instance)
    :returns: The descriptions strings and associated issue numbers
    :rtype: *dict*
    :raises Error: If retrieval fails without any results

    """
    descriptions = {}
    issues = gh.iter_issues()
    if issues:
        for issue in issues:
            content = GitHubIssue.issue_content_parser(issue.body)
            descriptions[issue.number] = content['description']
        return descriptions
    else:
        logging.error('   Result: FAILED')
        raise Exception('Cannot retrieve all descriptions from GitHub repository')


# Main entry point for stand-alone call.
if __name__ == "__main__":
    # Get command-line arguments
    args = get_args()
    # Parse configuration INI file
    cfg = config_parse(args.i)
    # Init logging
    if args.v:
        init_logging(args.log, level='DEBUG')
    elif cfg.has_option('initialize', 'log_level'):
        init_logging(args.log, cfg.get('initialize', 'log_level'))
    else:
        init_logging(args.log)
    # Connection to the GitHub repository
    gh_login, gh = github_connector(username=cfg.get('issues', 'gh_login'),
                                    password=cfg.get('issues', 'gh_password'),
                                    team=cfg.get('issues', 'gh_team'),
                                    repo=cfg.get('issues', 'gh_repo'))
    # Connection to the Handle Service
    # hs = pid_connector(prefix=cfg.get('issues', 'prefix'),
    #                    url_messaging_service=cfg.get('issues', 'url_messaging_service'),
    #                    messaging_exchange=cfg.get('issues', 'messaging_exchange'),
    #                    rabbit_username=cfg.get('issues', 'rabbit_username'),
    #                    rabbit_password=cfg.get('issues', 'rabbit_password'))
    # Run command
    if args.command == 'create':
        # Instantiate ESGF issue from issue template and datasets list
        local_issue = ESGFIssue(issue_f=args.I,
                                dsets_f=args.D)
        # Validate ESGF issue against JSON schema
        local_issue.validate(action=args.command,
                             projects=get_projects(cfg))
        # Create ESGF issue on GitHub repository
        local_issue.create(assignee=gh_login,
                           gh=gh,
                           descriptions=get_descriptions(gh))
        #local_issue.send(hs, gh_repo.name)  # Send issue id to Handle Service
    elif args.command == 'update':
        # Instantiate ESGF issue from issue template and datasets list
        local_issue = ESGFIssue(issue_f=args.I,
                                dsets_f=args.D)
        # Validate ESGF issue against JSON schema
        local_issue.validate(action=args.command,
                             projects=get_projects(cfg))
        print local_issue.get('salut')
        # Get corresponding GitHub issue
        remote_issue = GitHubIssue(gh=gh,
                                   number=local_issue.get('number'))
        # Validate GitHub issue against JSON schema
        remote_issue.validate(action=args.command,
                              projects=get_projects(cfg))
        # Update ESGF issue information on GitHub repository
        local_issue.update(gh=gh,
                           remote_issue=remote_issue)
        #issue.push(hs)    # Push new issue information to update Handle Service metadata
    elif args.command == 'close':
        # Instantiate ESGF issue from issue template and datasets list
        local_issue = ESGFIssue(issue_f=args.I,
                                dsets_f=args.D)
        # Validate ESGF issue against JSON schema
        local_issue.validate(action=args.command,
                             projects=get_projects(cfg))
        # Get corresponding GitHub issue
        remote_issue = GitHubIssue(gh=gh,
                                   number=local_issue.get('number'))
        # Validate GitHub issue against JSON schema
        remote_issue.validate(action=args.command,
                              projects=get_projects(cfg))
        # Close the ESGF issue on the Github repository
        local_issue.close(gh=gh,
                          remote_issue=remote_issue)
    elif args.command == 'retrieve':
        # Get corresponding GitHub issue
        remote_issue = GitHubIssue(gh=gh,
                                   number=args.N)
        # Validate GitHub issue against JSON schema
        remote_issue.validate(action=args.command,
                              projects=get_projects(cfg))
        # Retrieve the corresponding GitHub issue
        remote_issue.retrieve(issue_f=args.I,
                              dsets_f=args.D)
