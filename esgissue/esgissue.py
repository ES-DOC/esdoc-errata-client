#!/usr/bin/env python
"""
   :platform: Unix
   :synopsis: Manages ESGF issues on BitBucket repository.

"""

# Module imports
import argparse
from uuid import uuid4
from datetime import datetime
from issue_handler import LocalIssue
from constants import *
from utils import MultilineFormatter, init_logging, get_datasets, get_issue, authenticate, reset_passphrase,\
                  reset_credentials, set_credentials, prepare_retrieval

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
        description="""
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
        description=""""esgissue create" registers one or several issues on a defined errata repository. The data
                    provider submits one or several JSON files gathering all issues information with a list of all
                    affected dataset IDs (see http://esgissue.readthedocs.org/configuration.html to get a template).|n|n

                    This action returns to the corresponding local JSON template:|n
                    - the ESGF issue ID (as UUID),|n
                    - the creation date,|n
                    - the last updated date (same as the creation date).|n|n

                    The issue registration sets:|n
                    - the issue status to "new",|n

                    SEE http://esgissue.readthedocs.org/usage.html TO FOLLOW ALL REQUIREMENTS TO REGISTER AN ISSUE.|n|n

                    See "esgissue -h" for global help.""",
        formatter_class=MultilineFormatter,
        help="""Creates ESGF issues from a JSON template to the errata database.|n
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
        description=""""esgissue update" updates one or several issues on a defined errata repository. The data
                    provider submits one or several JSON files gathering all issues information with a list of all
                    affected dataset IDs (see http://esgissue.readthedocs.org/configuration.html to get a template).|n|n

                    This action returns the time and date of the update to the corresponding local JSON template.|n|n

                    SEE http://esgissue.readthedocs.org/usage.html TO FOLLOW ALL REQUIREMENTS TO UPDATE AN ISSUE.|n|n

                    See "esgissue -h" for global help.""",
        formatter_class=MultilineFormatter,
        help="""Updates ESGF issues from a JSON template to the errata database.|n
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
        description=""""esgissue close" closes one or several issues on a defined errata database. The data
                    provider submits one or several JSON files gathering all issues information with a list of all
                    affected dataset IDs (see http://esgissue.readthedocs.org/configuration.html to get a template).|n|n

                    This action returns the date of closure to the corresponding local JSON template (which is the same
                    as the date of the last update).|n|n

                    SEE http://esgissue.readthedocs.org/usage.html TO FOLLOW ALL REQUIREMENTS TO CLOSE AN ISSUE.|n|n

                    See "esgissue -h" for global help.""",
        formatter_class=MultilineFormatter,
        help="""Closes ESGF issues on the errata repository.|n
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
    close.add_argument(
        '--status',
        nargs='?',
        required=False,
        type=str,
        help='specifies status of closed issue.'
    )

    #####################################
    # Subparser for "esgissue retrieve" #
    #####################################
    retrieve = subparsers.add_parser(
        'retrieve',
        prog='esgissue retrieve',
        description=""""esgissue retrieve" retrieves one or several issues from a defined errata repository. The data
                    provider submits one or several issue number he wants to retrieve and optional paths to write
                    them.|n|n

                    This action rebuilds:|n
                    - the corresponding issue template as a JSON file,|n
                    - the attached affected datasets list as a TEXT file.|n|n

                    SEE http://esgissue.readthedocs.org/usage.html TO FOLLOW ALL REQUIREMENTS TO RETRIEVE AN ISSUE.|n|n

                    See "esgissue -h" for global help.""",
        formatter_class=MultilineFormatter,
        help="""Retrieves ESGF issues from the errata repository to a JSON template.|n
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
        help='One or several issue number(s) or ESGF id(s) to retrieve.|n Default is to retrieve all errata issues.')
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

    ########################################
    # Subparser for "esgissue credentials" #
    ########################################
    changepass = subparsers.add_parser(
            'changepass',
            prog='esgissue changepass',
            description=""""esgissue credentials" allows users to interact with their established credentials.
            It mainly allows users who have locally saved credentials to modify their pass-phrase or reset it by deleting
            them and having to redo the credentials input all over again. This can be useful in case someone forgets the passphrase
            set before.

            See "esgissue -h" for global help.""",
            formatter_class=MultilineFormatter,
            help="""Helps user interact with registered credentials.|n
                    See "esgissue changepass -h" for full help.""",
            add_help=False,
            parents=[parent])
    changepass._optionals.title = "Arguments"
    changepass._positionals.title = "Positional arguments"
    changepass.add_argument('--oldpass',
                            nargs='?',
                            required=False,
                            metavar='action',
                            type=str)
    changepass.add_argument('--newpass',
                            nargs='?',
                            required=False,
                            type=str)
    ########################################
    # Subparser for "esgissue cred-reset" #
    ########################################
    credreset = subparsers.add_parser(
            'credreset',
            prog='esgissue credreset',
            description=""""esgissue credreset" allows users to interact with their established credentials.
            It mainly allows users who have locally saved credentials to modify their pass-phrase or reset it by deleting
            them and having to redo the credentials input all over again. This can be useful in case someone forgets the passphrase
            set before.

            See "esgissue -h" for global help.""",
            formatter_class=MultilineFormatter,
            help="""Helps user interact with registered credentials.|n
                    See "esgissue credreset -h" for full help.""",
            add_help=False,
            parents=[parent])

    ########################################
    # Subparser for "esgissue cred-set" #
    ########################################
    credreset = subparsers.add_parser(
            'credset',
            prog='esgissue credset',
            description=""""esgissue credset" allows users to establish new credentials. Just like cred-reset except this tool allows users
            to delete any previously stored information and establish new ones.

            See "esgissue -h" for global help.""",
            formatter_class=MultilineFormatter,
            help="""Helps user interact with registered credentials.|n
                    See "esgissue credset -h" for full help.""",
            add_help=False,
            parents=[parent])

    return main.parse_args()


def process_command(command, issue_file=None, dataset_file=None, issue_path=None, dataset_path=None, status=None,
                    list_of_ids=None):
    payload = issue_file
    if dataset_file is not None:
        dsets = get_datasets(dataset_file)
    else:
        dsets = None
    # Fill in mandatory fields
    if command in [CREATE, UPDATE, CLOSE]:
            credentials = authenticate()
    if command == CREATE:
        payload[UID] = str(uuid4())
        payload[STATUS] = unicode(STATUS_NEW)
        payload[DATE_CREATED] = datetime.utcnow().strftime(TIME_FORMAT)
    local_issue = LocalIssue(action=command, issue_file=payload, dataset_file=dsets, issue_path=issue_path,
                             dataset_path=dataset_path)
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
    # Get command-line arguments
    args = get_args()
    # init logging
    if args.v and args.log is not None:
        init_logging(args.log, level='DEBUG')
    elif args.log is not None:
        init_logging(args.log)
    else:
        init_logging()
    if args.command == CHANGEPASS:
        reset_passphrase(old_pass=args.oldpass, new_pass=args.newpass)
    elif args.command == CREDRESET:
        reset_credentials()
    elif args.command == 'credset':
        set_credentials()
    # Retrieve command has a slightly different behavior from the rest so it's singled out
    elif args.command not in [RETRIEVE, CLOSE]:
        issue_file = get_issue(args.issue)
        dataset_file = get_datasets(args.dsets)
        process_command(command=args.command, issue_file=issue_file, dataset_file=dataset_file,
                        issue_path=args.issue, dataset_path=args.dsets)
    elif args.command == CLOSE:
        issue_file = get_issue(args.issue)
        dataset_file = get_datasets(args.dsets)
        process_command(command=args.command, issue_file=issue_file, dataset_file=dataset_file,
                        issue_path=args.issue, dataset_path=args.dsets, status=args.status)
    elif args.command == RETRIEVE:
        list_of_id, issues, dsets = prepare_retrieval(args.id, args.issues, args.dsets)
        if list_of_id is not None:
            process_command(command=RETRIEVE, issue_path=issues, dataset_path=dsets, list_of_ids=list_of_id)
        else:
            print('RETRIEVING ALL')
            process_command(command=RETRIEVE_ALL, issue_path=issues, dataset_path=dsets)

# Main entry point for stand-alone call.
if __name__ == "__main__":
    run()
