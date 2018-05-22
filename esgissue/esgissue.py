#!/usr/bin/env python
"""
   :platform: Unix
   :synopsis: Manages ESGF issues on BitBucket repository.

"""

# Module imports
import argparse
import os
from uuid import uuid4
from issue_handler import LocalIssue
from constants import *
from utils import MultilineFormatter, _init_logging, _get_datasets, _get_issue, _authenticate, _reset_passphrase,\
                  _set_credentials, _prepare_retrieve_ids, _reset_credentials, _cred_test, _get_credentials

# Program version
__version__ = VERSION_NUMBER

# Rabbit MQ unsent messages directory


def get_args():
    """
    Returns parsed command-line arguments. See ``esgissue -h`` for full description.

    :returns: The corresponding ``argparse`` Namespace

    """

    main = argparse.ArgumentParser(
        prog='esgissue',
        description=ESGISSUE_GENERAL,
        formatter_class=MultilineFormatter,
        add_help=False,
        epilog=EPILOG)
    main._optionals.title = OPTIONAL
    main._positionals.title = POSITIONAL
    main.add_argument(
        '-h', '--help',
        action='help',
        help=HELP)
    main.add_argument(
        '-v', '--version',
        action='version',
        version='%(prog)s ({0})'.format(__version__),
        help=VERSION_HELP)
    subparsers = main.add_subparsers(
        title=ISSUE_ACTIONS,
        dest='command',
        metavar='',
        help='')

    #######################################
    # Parent parser with common arguments #
    #######################################
    parent = argparse.ArgumentParser(add_help=False)
    parent.add_argument(
        '--log', '-l',
        metavar='$PWD',
        type=str,
        const=os.getcwd(),
        nargs='?',
        help=LOG_HELP)
    parent.add_argument(
        '-v', '--version',
        action='store_true',
        default=False,
        help=VERSION_HELP)
    parent.add_argument(
        '-h', '--help',
        action='help',
        help=HELP)

    ###################################
    # Subparser for "esgissue create" #
    ###################################
    create = subparsers.add_parser(
        'create',
        prog='esgissue create',
        description=CREATE_DESC,
        formatter_class=MultilineFormatter,
        help=CREATE_HELP,
        add_help=False,
        parents=[parent])
    create._optionals.title = "Arguments"
    create._positionals.title = "Positional arguments"
    create.add_argument(
        '--issue', '-i',
        nargs='?',
        required=True,
        metavar='PATH/issue.json',
        type=str,
        help=ISSUE_HELP)
    create.add_argument(
        '--dsets', '-d',
        nargs='?',
        required=True,
        metavar='PATH/dsets.list',
        type=argparse.FileType('r+'),
        help=DSETS_HELP)

    ###################################
    # Subparser for "esgissue update" #
    ###################################
    update = subparsers.add_parser(
        'update',
        prog='esgissue update',
        description=UPDATE_DESC,
        formatter_class=MultilineFormatter,
        help=UPDATE_HELP,
        add_help=False,
        parents=[parent])
    update._optionals.title = "Optional arguments"
    update._positionals.title = "Positional arguments"
    update.add_argument(
        '--issue', '-i',
        nargs='?',
        required=True,
        metavar='PATH/issue.json',
        type=str,
        help=ISSUE_HELP)
    update.add_argument(
        '--dsets', '-d',
        nargs='?',
        required=True,
        metavar='PATH/dsets.list',
        type=argparse.FileType('r+'),
        help=DSETS_HELP)

    ##################################
    # Subparser for "esgissue close" #
    ##################################
    close = subparsers.add_parser(
        'close',
        prog='esgissue close',
        description=CLOSE_DESC,
        formatter_class=MultilineFormatter,
        help=CLOSE_HELP,
        add_help=False,
        parents=[parent])
    close._optionals.title = "Optional arguments"
    close._positionals.title = "Positional arguments"
    close.add_argument(
        '--issue', '-i',
        nargs='?',
        required=True,
        metavar='PATH/issue.json',
        type=str,
        help=ISSUE_HELP)
    close.add_argument(
        '--dsets', '-d',
        nargs='?',
        required=True,
        metavar='PATH/dsets.list',
        type=argparse.FileType('r+'),
        help=DSETS_HELP)
    close.add_argument(
        '--status', '-s',
        nargs='?',
        required=False,
        type=str,
        help='specifies status of closed issue, please choose either (r)esolved or (w)ontfix.'
    )

    #####################################
    # Subparser for "esgissue retrieve" #
    #####################################
    retrieve = subparsers.add_parser(
        'retrieve',
        prog='esgissue retrieve',
        description=RETRIEVE_DESC,
        formatter_class=MultilineFormatter,
        help=RETRIEVE_HELP,
        add_help=False,
        parents=[parent])
    retrieve._optionals.title = "Optional arguments"
    retrieve._positionals.title = "Positional arguments"
    retrieve.add_argument(
        '--id',
        metavar='ID',
        type=str,
        nargs='*',
        default=None,
        help='One or several issue number(s) or ESGF id(s) to retrieve.|n Default is to retrieve all errata issues.')
    retrieve.add_argument(
        '--issues', '-i',
        nargs='?',
        metavar='$PWD/issues',
        type=str,
        help="""Output directory for the retrieved JSON templates.""")
    retrieve.add_argument(
        '--dsets', '-d',
        nargs='?',
        metavar='$PWD/dsets',
        type=str,
        help="""Output directory for the retrieved lists of affected dataset IDs.""")

    ########################################
    # Subparser for "esgissue changepass" #
    ########################################
    changepass = subparsers.add_parser(
            'changepass',
            prog='esgissue changepass',
            description=CHANGEPASS_DESC,
            formatter_class=MultilineFormatter,
            help=CHANGEPASS_HELP,
            add_help=False,
            parents=[parent])
    changepass._optionals.title = "Optional arguments"
    changepass._positionals.title = "Positional arguments"
    changepass.add_argument('--oldpass',
                            nargs='?',
                            required=False,
                            type=str)
    changepass.add_argument('--newpass',
                            nargs='?',
                            required=False,
                            type=str)
    ######################################
    # Subparser for "esgissue credremove" #
    ######################################
    credremove = subparsers.add_parser(
            'credremove',
            prog='esgissue credremove',
            description=CREDRESET_DESC,
            formatter_class=MultilineFormatter,
            help=CREDRESET_HELP,
            add_help=False,
            parents=[parent])
    ####################################
    # Subparser for "esgissue credset" #
    ####################################
    credset = subparsers.add_parser(
            'credset',
            prog='esgissue credset',
            description=CREDSET_DESC,
            formatter_class=MultilineFormatter,
            help=CREDSET_HELP,
            add_help=False,
            parents=[parent])
    credset.add_argument('--username', '-u',
                         nargs='?',
                         required=False,
                         type=str)
    credset.add_argument('--token', '-t',
                         nargs='?',
                         required=False,
                         type=str)
    #####################################
    # Subparser for "esgissue credtest" #
    #####################################
    credtest = subparsers.add_parser(
            'credtest',
            prog='esgissue credtest',
            description=CREDTEST_DESC,
            formatter_class=MultilineFormatter,
            help=CREDTEST_HELP,
            add_help=False,
            parents=[parent])
    credtest.add_argument('--institute',
                          '-i',
                          nargs='?',
                          type=str)
    credtest.add_argument('--project',
                          '-p',
                          nargs='?',
                          type=str)
    credtest.add_argument('--passphrase',
                      '-pass',
                      nargs='?',
                      type=str)
    return main.parse_args()


def process_command(command, issue_file=None, dataset_file=None, issue_path=None, dataset_path=None, status=None,
                    list_of_ids=None, **kwargs):
    payload = issue_file

    if command in [CREATE, UPDATE, CLOSE]:
        credentials = _get_credentials(kwargs)
        # Initializing non-mandatory fields to pass validation process.
        if URL not in payload.keys():
            payload[URL] = []
        if MATERIALS not in payload.keys():
            payload[MATERIALS] = []
    # intializing mandatory new issue fields
    if command == CREATE:
        payload[UID] = str(uuid4())
        payload[STATUS] = unicode(STATUS_NEW)

    # instatiating a localissue object
    local_issue = LocalIssue(action=command, issue_file=payload, dataset_file=dataset_file, issue_path=issue_path,
                             dataset_path=dataset_path)

    # issue file validation
    if command not in [RETRIEVE, RETRIEVE_ALL]:
        local_issue.validate(command)
    # WS Call
    if command == CREATE:
        local_issue.create(credentials)
    elif command == UPDATE:
        local_issue.update(credentials)
    elif command == CLOSE:
        local_issue.close(credentials, status)
    elif command == RETRIEVE:
        local_issue.retrieve(list_of_ids, issue_path, dataset_path)
    elif command == RETRIEVE_ALL:
        local_issue.retrieve_all(issue_path, dataset_path)


def run():
    """
    Main process that\:
     * Parse command-line arguments,
     * Parse configuration file,
     * Initiates logger,
     * Check Handle Service connection,
     * Run the issue action.

    """
    try:
        # Get command-line arguments
        args = get_args()
        # init logging
        if args.version and args.log is not None:
            _init_logging(args.log, level='DEBUG')
        elif args.log is not None:
            _init_logging(args.log)
        else:
            _init_logging()
        if args.command == CHANGEPASS:
            if args.oldpass is not None and args.newpass is not None:
                _reset_passphrase(old_pass=args.oldpass, new_pass=args.newpass)
            else:
                _reset_passphrase()
        elif args.command == CREDSET:
            if args.username is not None and args.token is not None:
                _set_credentials(username=args.username, token=args.token)
            else:
                _set_credentials()
        elif args.command == CREDREMOVE:
            _reset_credentials()
        elif args.command == CREDTEST:
            # credentials = _authenticate(passphrase=args.passphrase)
            _cred_test(args.institute, args.project, args.passphrase)
        # Retrieve command has a slightly different behavior from the rest so it's singled out
        elif args.command not in [RETRIEVE, CLOSE]:
            issue_file = _get_issue(args.issue)
            dataset_file = _get_datasets(args.dsets)
            process_command(command=args.command, issue_file=issue_file, dataset_file=dataset_file,
                            issue_path=args.issue, dataset_path=args.dsets)
        elif args.command == CLOSE:
            issue_file = _get_issue(args.issue)
            dataset_file = _get_datasets(args.dsets)
            process_command(command=args.command, issue_file=issue_file, dataset_file=dataset_file,
                            issue_path=args.issue, dataset_path=args.dsets, status=args.status)
        elif args.command == RETRIEVE:
            list_of_id = _prepare_retrieve_ids(args.id)
            # issues, dsets = prepare_retrieve_dirs(args.issues, args.dsets, list_of_id)
            if len(list_of_id) >= 1:
                process_command(command=RETRIEVE, issue_path=args.issues, dataset_path=args.dsets, list_of_ids=list_of_id)
            else:
                process_command(command=RETRIEVE_ALL, issue_path=args.issues, dataset_path=args.dsets)
    except KeyboardInterrupt:
        print('Keyboard interruption, exiting...')


# Main entry point for stand-alone call.
if __name__ == "__main__":
    run()
