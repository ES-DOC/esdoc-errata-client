#!/usr/bin/env python
"""
   :platform: Unix
   :synopsis: Manages ESGF issues on BitBucket repository.

"""

# Module imports
import uuid
import argparse
from issue_handler import ESGFIssue, GitHubIssue
from utils import MultilineFormatter, split_line, init_logging, get_file_path, get_ws_call
from datetime import datetime
import os
import sys
import json
import simplejson
import requests
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
    # parent.add_argument(
    #     '-i',
    #     metavar='/esg/config/esgcet/.',
    #     type=str,
    #     default='/esg/config/esgcet/.',
    #     help="""Initialization/configuration directory containing "esg.ini"|n
    #         and "esg.<project>.ini" files. If not specified, the usual|n
    #         datanode directory is used.""")
    # parent.add_argument(
    #     '--log',
    #     metavar='$PWD',
    #     type=str,
    #     const=os.getcwd(),
    #     nargs='?',
    #     help="""Logfile directory. If not, standard output is used.""")
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
        type=str,
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
        type=str,
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
        type=str,
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
        default=None,
        help='One or several issue number(s) or ESGF id(s) to retrieve.|n Default is to retrieve all GitHub issues.')
    retrieve.add_argument(
        '--issues',
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


# def github_connector(username, password, team, repo):
#     """
#     Instantiates the GitHub repository connector if granted for user.
#
#     :param username: The GitHub login
#     :param password: The GitHub password
#     :param team: The GitHub team to connect
#     :param repo: The GitHub repository to reach
#     :returns: The GitHub repository connector and the GitHub user login
#     :rtype: *tuple* of (*str*, *github3.repos.repo*)
#     :raises Error: If the GitHub connection fails because of invalid inputs
#
#     """
#     logging.info('Connection to the GitHub repository "{0}/{1}"'.format(team, repo.lower()))
#     try:
#         gh_user = GitHub(username, password)
#         gh_repo = gh_user.repository(team, repo.lower())
#         logging.info('Result: SUCCESSFUL')
#         return username, gh_repo
#     except:
#         logging.exception('Result: FAILED // Access denied')
#         sys.exit(1)


# def pid_connector(prefix, url_messaging_service, messaging_exchange, rabbit_username,
#                   rabbit_password, successful_messages=True):
#     """
#     Instantiates the PID Handle Service connector if granted for user.
#
#     :param str prefix: The PID prefix to use
#     :param str url_messaging_service: The Handle Service URL
#     :param str messaging_exchange: The message header
#     :param str rabbit_username: The RabbitMQ username
#     :param str rabbit_password: The RabbitMQ password
#     :param boolean successful_messages: True to store successful messages
#     :returns: The Handle Service connector
#     :rtype: *ESGF_PID_connector*
#     :raises Error: If the Handle Service connection fails because of invalid inputs
#
#     """
#     logging.info('Connection to the RabbitMQ Server of the Handle Service')
#     try:
#         if not os.path.isdir(__UNSENT_MESSAGES_DIR__):
#             os.mkdir(__UNSENT_MESSAGES_DIR__)
#         pid = ESGF_PID_connector(prefix=prefix,
#                                  url_messaging_service=url_messaging_service,
#                                  messaging_exchange=messaging_exchange,
#                                  data_node='foo.fr',
#                                  thredds_service_path='/what/ever/',
#                                  solr_url='http://i-will.not/be/used',
#                                  rabbit_username=rabbit_username,
#                                  rabbit_password=rabbit_password,
#                                  directory_unsent_messages=__UNSENT_MESSAGES_DIR__,
#                                  store_successful_messages=successful_messages)
#         logging.info('Result: SUCCESSFUL')
#         return pid
#     except:
#         logging.exception('Result: FAILED // Access denied')
#         sys.exit(1)


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
    # cfg = config_parse(args.i)
    # Init logging
    if args.v:
        init_logging(args.log, level='DEBUG')
    # elif cfg.has_option('initialize', 'log_level'):
    #     init_logging(args.log, cfg.get('initialize', 'log_level'))
    # else:
    #     init_logging(args.log)
    # Run command
    if args.command == 'create':
        # First step: get dataset list.
        # Instantiate ESGF issue from issue template and datasets list
        with open(args.issue, 'r') as data_file:
            print(data_file)
            payload = json.load(data_file)
        # Adding id and workflow
        payload['id'] = str(uuid.uuid4())
        print('creating issue with id {}'.format(payload['id']))
        payload['workflow'] = unicode('new')
        dsets = list()
        for dset in args.dsets:
            dsets.append(unicode(dset.strip(' \n\r\t')))
        payload['datasets'] = dsets
        url = 'http://localhost:5001/1/issue/create'
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        # Updating local issue with webservice response.
        try:
            r = get_ws_call(args.command, payload, None)
            if r.status_code != requests.codes.ok:
                print('query failed')
                print('Some issue has occurred please make sure your request is well formed, here is the response text:')
                print(r.text)
                sys.exit(1)
            print('updating fields of payload')
            if r.json()['status'] == 0:
                payload['date_created'] = r.json()['dateCreated']
                payload['date_updated'] = r.json()['dateUpdated']
                print('fields updated for payload json.')
            else:
                print('Something went wrong, error message:')
                print(r.json()['message'])
            with open(args.issue, 'w') as data_file:
                if 'datasets' in payload.keys():
                    del payload['datasets']
                print('Opened file attempting update..')
                data_file.write(simplejson.dumps(payload, indent=4, sort_keys=True))
                print('dumped updated version!')
        except Exception as e:
            print(repr(e))
    elif args.command == 'update':
        print(args.issue)
        print(type(args.issue))
        with open(args.issue, 'r') as data_file:
            payload = json.load(data_file)
        dsets = list()
        for dset in args.dsets:
            dsets.append(unicode(dset.strip(' \n\r\t')))
        payload['datasets'] = dsets
        print('here is the uid {}'.format(payload['id']))
        try:
            print('preparing request...')
            r = get_ws_call(args.command, json.dumps(payload), None)
            print('query sent, heres the response')
            if r.status_code != requests.codes.ok:
                print('query failed')
                print('Some issue has occurred please make sure your request is well formed,'
                      ' here is the response text:')
                print(r.text)
                sys.exit(1)
            if r.json()['status'] == 0:
                payload['date_updated'] = r.json()['dateUpdated']
                del payload['datasets']
                # updating the issue body.
                with open(args.issue, 'w+') as data_file:
                    data_file.write(simplejson.dumps(payload, indent=4, sort_keys=True))
                print('Local issue updated.')
            else:
                print('Webservice rejected your call for the following reasons:{}'.format(r.text))
            print('update operation over.')
        except Exception as e:
            print(repr(e))

    elif args.command == 'close':
        with open(args.issue, 'r') as data_file:
            payload = json.load(data_file)
        try:
            r = get_ws_call(args.command, payload, None)
            # Catch the case where the http webservice call failed.
            if r.status_code != requests.codes.ok:
                print('query failed')
                print('Some issue has occurred please make sure your request is well formed,'
                      ' here is the response text:')
                print(r.text)
                sys.exit(1)

            # Only in case the webservice operation succeeded.
            if r.json()['status'] == 0:
                payload['date_updated'] = r.json()['dateClosed']
                payload['date_closed'] = r.json()['dateClosed']
                if 'datasets' in payload.keys():
                    del payload['datasets']
                with open(args.issue, 'w+') as data_file:
                    data_file.write(simplejson.dumps(payload, indent=4, sort_keys=True))
            else:
                print('Webservice rejected your call for the following reasons:{}'.format(r.text))
            print('Close operation ended.')
        except Exception as e:
            print(repr(e))

    elif args.command == 'retrieve':
        list_of_ids = args.id
        # In the case the user is requesting more than one issue
        for directory in [args.issues, args.dsets]:
            # Added the '.' test to avoid creating directories that are intended to be files.
            if not os.path.exists(directory) and '.' not in directory:
                os.makedirs(directory)
            # This tests whether a list of ids is provided with a directory where to dump the retrieved
            # issues and related datasets.
        if len(list_of_ids) > 1 and not os.path.isdir(directory):
            print('For multiple issue retrieval please provide a directory path.')
            sys.exit(1)
        # Looping over list of ids provided
        for n in list_of_ids:
            print('processing id {}'.format(n))
            try:
                r = get_ws_call(args.command, None, n)
                if r.status_code == requests.codes.ok:
                    payload = r.json()['issue']
                    path_to_issue, path_to_dataset = get_file_path(args.issues, args.dsets, payload['uid'])
                    with open(path_to_dataset, 'w') as dset_file:
                        if not r.json()['datasets']:
                            print('The issue {} seems to be affecting no datasets.'.format(payload['uid']))
                            dset_file.write('No datasets provided with issue.')
                        for dset in r.json()['datasets']:
                            print('Now writing this element {}'.format(dset[0]))
                            dset_file.write(dset[0] + '\n')
                    with open(path_to_issue, 'w') as data_file:
                        data_file.write(simplejson.dumps(payload, indent=4, sort_keys=True))
                else:
                    print('something went wrong, here is the server response:')
                    print(r.text)
            except Exception as e:
                print(repr(e))


# Main entry point for stand-alone call.
if __name__ == "__main__":
    run()
