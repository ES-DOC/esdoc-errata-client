#!/usr/bin/env python
"""
   :platform: Unix
   :synopsis: Manages ESGF issues on BitBucket repository.

"""
import pytest
from uuid import uuid4
from esgissue.issue_handler import LocalIssue
from esgissue.arg_parser import get_args
from esgissue.constants import *
from esgissue.utils import _init_logging
from esgissue.utils import _get_datasets
from esgissue.utils import _get_issue
from esgissue.utils import _reset_passphrase
from esgissue.utils import _set_credentials
from esgissue.utils import _prepare_retrieve_ids
from esgissue.utils import _reset_credentials
from esgissue.utils import _cred_test
from esgissue.utils import _get_credentials
from esgissue.utils import _check_pid


# Rabbit MQ unsent messages directory


def process_command(command, issue_file=None, dataset_file=None, issue_path=None, dataset_path=None, status=None,
                    list_of_ids=None, dry_run=False, **kwargs):
    """
    Process command is the utility called to do the necessary for each of the client's command.
    If you're debugging an issue this is where you need to start.
    :param command: action command needs to be one of Create, Update, Close or Retrieve
    :param issue_file: issue json file
    :param dataset_file: dataset list in txt form
    :param issue_path: local path to the issue file
    :param dataset_path: local path to the dataset file
    :param status: status of the issue [new, on_hold, wontfix, resolved]
    :param list_of_ids: List of issue uids
    :param dry_run: parameter used by the test suite to target test nodes.
    :param kwargs: credentials retrieved from here.
    :return:
    """
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
        payload[STATUS] = STATUS_NEW

    # instatiating a localissue object
    local_issue = LocalIssue(action=command, issue_file=payload, dataset_file=dataset_file, issue_path=issue_path,
                             dataset_path=dataset_path, dry_run=dry_run)

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
    Main process that:
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
            _cred_test(args.institute, args.project, args.passphrase)

        elif args.command == CHECK:
            result = _check_pid(",".join(args.id), args.full, args.latest)
            # result printing.
            # For the time being bare print. Need better method for this.
            for element in result:
                print(element)
        # Retrieve & close commands have a slightly different behavior from the rest so it's singled out
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
            if len(list_of_id) >= 1:
                process_command(command=RETRIEVE, issue_path=args.issues, dataset_path=args.dsets,
                                list_of_ids=list_of_id)
            else:
                process_command(command=RETRIEVE_ALL, issue_path=args.issues, dataset_path=args.dsets)

    except KeyboardInterrupt:
        print('Keyboard interruption, exiting...')


# Main entry point for stand-alone call.
if __name__ == "__main__":
    run()
