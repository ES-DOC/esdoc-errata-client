#!/usr/bin/env python
"""
   :platform: Unix
   :synopsis: Manages ESGF issues on BitBucket repository.

"""

# Module imports
import os
import sys
import uuid
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
    __DSETS_HELP__ = """Required path of the affected dataset IDs list."""
    main = argparse.ArgumentParser(
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
    main._optionals.title = "Optional arguments"
    main._positionals.title = "Positional arguments"
    main.add_argument(
        '-h', '--help',
        action='help',
        help="""Show this help message and exit.""")
    main.add_argument(
        '-V',
        action='version',
        version='%(prog)s ({0})'.format(__version__),
        help="""Program version.""")
    subparsers = main.add_subparsers(
        title='Issue actions',
        dest='command',
        metavar='',
        help='')

    #######################################
    # Parent parser with common arguments #
    #######################################
    parent = argparse.ArgumentParser(add_help=False)
    parent.add_argument(
        '-i',
        metavar='/esg/config/esgcet/.',
        type=str,
        default='/esg/config/esgcet/.',
        help="""Initialization/configuration directory containing "esg.ini"|n
            and "esg.<project>.ini" files. If not specified, the usual|n
            datanode directory is used.""")
    parent.add_argument(
        '--log',
        metavar='$PWD',
        type=str,
        const=os.getcwd(),
        nargs='?',
        help="""Logfile directory. If not, standard output is used.""")
    parent.add_argument(
        '-v',
        action='store_true',
        default=False,
        help="""Verbose mode.""")
    parent.add_argument(
        '-h', '--help',
        action='help',
        help="""Show this help message and exit.""")

    ###################################
    # Subparser for "esgissue create" #
    ###################################
    create = subparsers.add_parser(
        'create',
        prog='esgissue create',
        description=""""esgissue create" registers one or several issues on a defined GitHub repository. The data
                    provider submits one or several JSON files gathering all issues information with a list of all
                    affected dataset IDs (see http://esgissue.readthedocs.org/configuration.html to get a template).|n|n

                    This action returns to the corresponding local JSON template:|n
                    - the corresponding issue number,|n
                    - the ESGF issue ID (as UUID),|n
                    - the creation date,|n
                    - the last updated date (same as the creation date).|n|n

                    The issue registration sets:|n
                    - the issue status to "New",|n
                    - the data provider GitHub login as the issue responsible,|n
                    - the issue format using a fixed HTML schema.|n|n

                    SEE http://esgissue.readthedocs.org/usage.html TO FOLLOW ALL REQUIREMENTS TO REGISTER AN ISSUE.|n|n

                    See "esgissue -h" for global help.""",
        formatter_class=MultilineFormatter,
        help="""Creates ESGF issues from a JSON template to the GitHub repository.|n
                See "esgissue create -h" for full help.""",
        add_help=False,
        parents=[parent])
    create._optionals.title = "Arguments"
    create._positionals.title = "Positional arguments"
    create.add_argument(
        '--issue',
        nargs='?',
        required=True,
        metavar='PATH/issue.json',
        type=argparse.FileType('r'),
        help=__TEMPLATE_HELP__)
    create.add_argument(
        '--dsets',
        nargs='?',
        required=True,
        metavar='PATH/dsets.list',
        type=argparse.FileType('r'),
        help=__DSETS_HELP__)

    ###################################
    # Subparser for "esgissue update" #
    ###################################
    update = subparsers.add_parser(
        'update',
        prog='esgissue update',
        description=""""esgissue update" updates one or several issues on a defined GitHub repository. The data
                    provider submits one or several JSON files gathering all issues information with a list of all
                    affected dataset IDs (see http://esgissue.readthedocs.org/configuration.html to get a template).|n|n

                    This action returns the last updated date to the corresponding local JSON template.|n|n

                    SEE http://esgissue.readthedocs.org/usage.html TO FOLLOW ALL REQUIREMENTS TO UPDATE AN ISSUE.|n|n

                    See "esgissue -h" for global help.""",
        formatter_class=MultilineFormatter,
        help="""Updates ESGF issues from a JSON template to the GitHub repository.|n
                See "esgissue update -h" for full help.""",
        add_help=False,
        parents=[parent])
    update._optionals.title = "Optional arguments"
    update._positionals.title = "Positional arguments"
    update.add_argument(
        '--issue',
        nargs='?',
        required=True,
        metavar='PATH/issue.json',
        type=argparse.FileType('r'),
        help=__TEMPLATE_HELP__)
    update.add_argument(
        '--dsets',
        nargs='?',
        required=True,
        metavar='PATH/dsets.list',
        type=argparse.FileType('r'),
        help=__DSETS_HELP__)

    ##################################
    # Subparser for "esgissue close" #
    ##################################
    close = subparsers.add_parser(
        'close',
        prog='esgissue close',
        description=""""esgissue close" closes one or several issues on a defined GitHub repository. The data
                    provider submits one or several JSON files gathering all issues information with a list of all
                    affected dataset IDs (see http://esgissue.readthedocs.org/configuration.html to get a template).|n|n

                    This action returns the date of closure to the corresponding local JSON template (as the same of
                    the last updated date).|n|n

                    SEE http://esgissue.readthedocs.org/usage.html TO FOLLOW ALL REQUIREMENTS TO CLOSE AN ISSUE.|n|n

                    See "esgissue -h" for global help.""",
        formatter_class=MultilineFormatter,
        help="""Closes ESGF issues on the GitHub repository.|n
                See "esgissue close -h" for full help.""",
        add_help=False,
        parents=[parent])
    close._optionals.title = "Optional arguments"
    close._positionals.title = "Positional arguments"
    close.add_argument(
        '--issue',
        nargs='?',
        required=True,
        metavar='PATH/issue.json',
        type=argparse.FileType('r'),
        help=__TEMPLATE_HELP__)
    close.add_argument(
        '--dsets',
        nargs='?',
        required=True,
        metavar='PATH/dsets.list',
        type=argparse.FileType('r'),
        help=__DSETS_HELP__)

    #####################################
    # Subparser for "esgissue retrieve" #
    #####################################
    retrieve = subparsers.add_parser(
        'retrieve',
        prog='esgissue retrieve',
        description=""""esgissue retrieve" retrieves one or several issues from a defined GitHub repository. The data
                    provider submits one or several issue number he wants to retrieve and optional paths to write
                    them.|n|n

                    This action rebuilds:|n
                    - the corresponding issue template as a JSON file,|n
                    - the attached affected datasets list as a TEXT file.|n|n

                    SEE http://esgissue.readthedocs.org/usage.html TO FOLLOW ALL REQUIREMENTS TO RETRIEVE AN ISSUE.|n|n

                    See "esgissue -h" for global help.""",
        formatter_class=MultilineFormatter,
        help="""Retrieves ESGF issues from the GitHub repository to a JSON template.|n
                See "esgissue retrieve -h" for full help.""",
        add_help=False,
        parents=[parent])
    retrieve._optionals.title = "Optional arguments"
    retrieve._positionals.title = "Positional arguments"
    retrieve.add_argument(
        '--id',
        metavar='ID',
        type=str,
        nargs='+',
        help='One or several issue number(s) or ESGF id(s) to retrieve.|n Default is to retrieve all GitHub issues.')
    retrieve.add_argument(
        '--issue',
        nargs='?',
        metavar='$PWD/issues',
        default='{0}/issues'.format(os.getcwd()),
        type=str,
        help="""Output directory for the retrieved JSON templates.""")
    retrieve.add_argument(
        '--dsets',
        nargs='?',
        metavar='$PWD/dsets',
        default='{0}/dsets'.format(os.getcwd()),
        type=str,
        help="""Output directory for the retrieved lists of affected dataset IDs.""")

    return main.parse_args()


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
    logging.info('Connection to the GitHub repository "{0}/{1}"'.format(team, repo.lower()))
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
    issues = gh.iter_issues(state='all')
    if issues:
        for issue in issues:
            content = GitHubIssue.issue_content_parser(issue.body)
            descriptions[issue.number] = content['description']
        return descriptions
    else:
        raise Exception('Cannot retrieve all descriptions from GitHub repository')


def get_number(gh, id):
    """
    Gets issue number depending on ESGF id.

    :param GitHubObj gh: The GitHub repository connector (as a :func:`github3.repos.repo` class instance)
    :param str id: The ESGF id
    :returns: The corresponding issue number
    :rtype: *int*
    :raises Error: If retrieval fails without any results

    """
    if not isinstance(id, uuid.UUID):
        return id
    issues = gh.iter_issues(state='all')
    if issues:
        for issue in issues:
            content = GitHubIssue.issue_content_parser(issue.body)
            if id == content['id']:
                return issue.number
    else:
        raise Exception('Cannot retrieve all ESGF IDs from GitHub repository')


def run():
    """
    Main process that\:
     * Parse command-line arguments,
     * Parse configuration file,
     * Initiates logger,
     * Check GitHub permissions,
     * Check Handle Service connection,
     * Run the issue action.

    """
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
    hs = pid_connector(prefix=cfg.get('issues', 'prefix'),
                       url_messaging_service=cfg.get('issues', 'url_messaging_service'),
                       messaging_exchange=cfg.get('issues', 'messaging_exchange'),
                       rabbit_username=cfg.get('issues', 'rabbit_username'),
                       rabbit_password=cfg.get('issues', 'rabbit_password'))
    # Run command
    if args.command == 'create':
        # Instantiate ESGF issue from issue template and datasets list
        local_issue = ESGFIssue(issue_f=args.issue,
                                dsets_f=args.dsets)
        # Validate ESGF issue against JSON schema
        local_issue.validate(action=args.command,
                             projects=get_projects(cfg))
        # Create ESGF issue on GitHub repository
        local_issue.create(gh=gh,
                           assignee=gh_login,
                           descriptions=get_descriptions(gh))
        # Send issue id to Handle Service
        # TODO : Uncomment for master release
        # #local_issue.send(hs, gh_repo.name)
    elif args.command == 'update':
        # Instantiate ESGF issue from issue template and datasets list
        local_issue = ESGFIssue(issue_f=args.issue,
                                dsets_f=args.dsets)
        # Validate ESGF issue against JSON schema
        local_issue.validate(action=args.command,
                             projects=get_projects(cfg))
        # Get corresponding GitHub issue
        remote_issue = GitHubIssue(gh=gh,
                                   number=local_issue.get('number'))
        # Validate GitHub issue against JSON schema
        remote_issue.validate(action=args.command,
                              projects=get_projects(cfg))
        # Update ESGF issue information on GitHub repository
        local_issue.update(gh=gh,
                           remote_issue=remote_issue)
        # Update issue id to Handle Service
        # TODO : Uncomment for master release
        #local_issue.send(hs, gh_repo.name)
    elif args.command == 'close':
        # Instantiate ESGF issue from issue template and datasets list
        local_issue = ESGFIssue(issue_f=args.issue,
                                dsets_f=args.dsets)
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
        for directory in [args.issue, args.dsets]:
            if not os.path.exists(directory):
                os.makedirs(directory)
        if args.N:
            for n in args.N:
                # Get issue number
                number = get_number(gh, n)
                # Get corresponding GitHub issue
                remote_issue = GitHubIssue(gh=gh,
                                           number=number)
                # Validate GitHub issue against JSON schema
                remote_issue.validate(action=args.command,
                                      projects=get_projects(cfg))
                # Retrieve the corresponding GitHub issue
                remote_issue.retrieve(issue_f=open('{0}/issue{1}.json'.format(os.path.realpath(args.issue),
                                                                              number), 'w'),
                                      dsets_f=open('{0}/dsets{1}.list'.format(os.path.realpath(args.dsets),
                                                                              number), 'w'))
        else:
            for issue in gh.iter_issues(state='all'):
                # Get corresponding GitHub issue
                remote_issue = GitHubIssue(gh=gh,
                                           number=get_number(gh, issue.number))
                # Validate GitHub issue against JSON schema
                remote_issue.validate(action=args.command,
                                      projects=get_projects(cfg))
                # Retrieve the corresponding GitHub issue
                remote_issue.retrieve(issue_f=open('{0}/issue{1}.json'.format(os.path.realpath(args.issue),
                                                                              issue.number), 'w'),
                                      dsets_f=open('{0}/dsets{1}.list'.format(os.path.realpath(args.dsets),
                                                                              issue.number), 'w'))


# Main entry point for stand-alone call.
if __name__ == "__main__":
    run()
