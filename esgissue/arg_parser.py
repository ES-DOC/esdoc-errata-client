import argparse
import os
from constants import *
from utils import MultilineFormatter


# Program version
__version__ = VERSION_NUMBER


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

    #####################################
    # Subparser for "esgissue check" #
    #####################################
    check = subparsers.add_parser(
        'check',
        prog='esgissue check',
        description=PID_DESC,
        formatter_class=MultilineFormatter,
        help=PID_HELP,
        add_help=False,
        parents=[parent])
    check._optionals.title = "Optional arguments"
    check._positionals.title = "Positional arguments"
    check.add_argument(
        '--id', '-i',
        metavar='dataset ID/dataset-file pid',
        type=str,
        nargs='*',
        default=None,
        help='One or several dataset identifier or dataset/file pid.')
    check.add_argument(
        '--full', '-f',
        action='store_true',
        help="""If set this returns the full history of the queried ids.""")
    check.add_argument(
        '--latest', '-lat',
        action='store_true',
        help="""if set this returns the latest version of the queried dataset/file only."""
    )
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


