# Externals
import uuid
import os
import subprocess as sub
import json
import requests
from time import sleep
from subprocess import CalledProcessError
# Internals
from essential_generators import DocumentGenerator
from esgissue.main import process_command
from esgissue.utils import _set_credentials
from esgissue.utils import _reset_passphrase
from esgissue.utils import _encrypt_with_key
from esgissue.utils import _reset_credentials
from esgissue.utils import _get_datasets
from esgissue.utils import _get_retrieve_dirs
from esgissue.utils import _get_file_location
from esgissue.utils import _encapsulate_pid_api_response
from esgissue.utils import _sanitize_input_and_call_ws
from esgissue.exceptions import ServerIssueValidationFailedException
from esgissue.errata_object_factory import ErrataCollectionObject
from esgissue.errata_object_factory import ErrataObject
from esgissue.constants import *

gen = DocumentGenerator()
prefix = '21.14100/'
cwd = os.path.dirname(os.path.realpath(__file__))
download_dir = os.path.join(cwd, 'samples/download/')
download_issue = 'dw_issue.json'
download_dset = 'dw_dset.txt'
username = 'AtefBN'
token = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
passphrase = 'atef'
new_passphrase = gen.sentence()


class Actionwords:
    def __init__(self, test_issue_file, test_dset_file, extra_dsets_file=None, uid=None):
        # Issue has to have a different title and description from what exists in the database.
        # Which forces us to rely on randomly generated title and description instead of fixed ones.
        with open(test_issue_file, 'r') as issue_file:
            self.issue = json.load(issue_file)
        self.issue_path = test_issue_file
        with open(test_dset_file, 'r') as dset_file:
            self.dsets = _get_datasets(dset_file)
        self.dsets_path = open(test_dset_file, 'r+')
        self.extra_dsets = extra_dsets_file
        self.uid = uid

    def create_issue(self):
        _set_credentials(username=username, token=token, passphrase=passphrase)
        # Required if the datasets don't have handles before.
        # create_handle_for_dataset(self.dsets)
        self.issue['title'] = gen.sentence()
        self.issue['description'] = gen.paragraph()
        process_command(command=CREATE, issue_file=self.issue, dataset_file=self.dsets, passphrase=passphrase,
                        issue_path=self.issue_path, dataset_path=self.dsets_path, dry_run=True)
        self.check_issue_files()
        _reset_credentials()

    def update_issue(self):
        _set_credentials(username=username, token=token, passphrase=passphrase)
        process_command(command=UPDATE, issue_file=self.issue, dataset_file=self.dsets, passphrase=passphrase,
                        issue_path=self.issue_path, dataset_path=self.dsets_path, dry_run=True)
        self.check_issue_files()
        _reset_credentials()

    def close_issue(self):
        _set_credentials(username=username, token=token, passphrase=passphrase)
        process_command(command=CLOSE, issue_file=self.issue, dataset_file=self.dsets, passphrase=passphrase,
                        issue_path=self.issue_path, dataset_path=self.dsets_path, status=STATUS_RESOLVED, dry_run=True)
        self.check_issue_files()
        _reset_credentials()

    def retrieve_issue(self):
        process_command(command=RETRIEVE, issue_path=self.issue, dataset_path=self.dsets,
                        list_of_ids=[self.uid], dry_run=True)

    # def check_issue_pid(self):
    #     # Checking PID HANDLE
    #     print('checkin PIDs')
    #     sleep(5)
    #     handle_client = EUDATHandleClient.instantiate_for_read_access()
    #     self.uid = self.issue['uid']
    #     for line in self.dsets:
    #         print('CHECKING {} ERRATA IDS'.format(line))
    #         exists = False
    #         dataset = line.split('#')
    #         dset_id = dataset[0]
    #         dset_version = dataset[1]
    #         hash_basis = dset_id+'.v'+dset_version
    #         hash_basis_utf8 = hash_basis.encode('utf-8')
    #         handle_string = uuid.uuid3(uuid.NAMESPACE_URL, hash_basis_utf8)
    #         encoded_dict = handle_client.retrieve_handle_record(prefix + str(handle_string))
    #         if encoded_dict is not None:
    #                 handle_record = {k.decode('utf8'): v.decode('utf8') for k, v in encoded_dict.items()}
    #                 if 'ERRATA_IDS' in handle_record.keys():
    #                     for uid in str(handle_record['ERRATA_IDS']).split(';'):
    #                         if uid == self.uid:
    #                             exists = True
    #                             break
    #         if not exists:
    #             print('An error occurred updating handle.')
    #             return exists

    def check_issue_files(self):
        # Comparing local file to server copy.
        self.uid = self.issue['uid']
        issue_dw = ''
        dataset_dw = ''
        process_command(command=RETRIEVE,
                        issue_path=issue_dw,
                        dataset_path=dataset_dw,
                        list_of_ids=[self.uid],
                        dry_run=True)
        issue_dw, dataset_dw = _get_retrieve_dirs(os.getcwd(), os.getcwd(), self.uid)
        with open(self.issue_path, 'r') as issue:
            local_data = json.load(issue)
        with open(issue_dw, 'r') as remote_issue:
            downloaded_data = json.load(remote_issue)
        # Server copy and local copy of date updated and closed will never match
        # on second level.
        issue_file_test = self.compare_json(local_data, downloaded_data, [URL, MATERIALS])
        if not issue_file_test:
            print(local_data)
            print(downloaded_data)
        self.dsets_path.close()
        with open(os.path.abspath(self.dsets_path.name), 'r') as dsets:
            datasets = dsets.readlines()
        with open(dataset_dw, 'r') as remote_dsets:
            remote_datasets = remote_dsets.readlines()
        # Test must be manual, retrieved list is not sorted
        dataset_file_test = set(datasets) == set(remote_datasets)
        if not dataset_file_test:
            print(datasets)
            print(remote_datasets)
        os.remove(issue_dw)
        os.remove(dataset_dw)
        if issue_file_test and dataset_file_test:
            return True
        else:
            return False

    def change_description_slightly(self):
        """Returns description string without the first 10 characters"""
        return self.issue['description'][10:]

    def change_severity(self):
        self.change_attribute('severity', 'medium')

    def change_description(self):
        new_desc = self.change_description_slightly()
        self.change_attribute('description', new_desc)

    def change_status(self):
        self.change_attribute('status', 'onhold')

    def change_url(self):
        self.change_attribute('url', 'http://www.ipsl.fr/')

    def clear_issue(self):
        data = self.issue
        if 'uid' in data.keys():
            del data['uid']
        if 'dateCreated' in data.keys():
            del data['dateCreated']
        if 'dateUpdated' in data.keys():
            del data['dateUpdated']
        if 'status' in data.keys():
            del data['status']
        if 'dateClosed' in data.keys():
            del data['dateClosed']
        self.issue = data
        with open(self.issue_path, 'w') as issue_file:
            json.dump(data, issue_file)
            print('Issue file cleared.')

    def add_dsets_to_file(self):
        with open(self.extra_dsets, 'r') as extra_file:
            extra_dsets = extra_file.readlines()
        with open(self.dsets_path, 'w+') as dset_file:
            for dset in extra_dsets:
                dset_file.write(dset)

    def remove_dsets_from_file(self):
        self.dsets_path.close()
        with open(os.path.abspath(self.dsets_path.name)) as dset_file:
            lines = dset_file.readlines()
        if len(lines) < 2:
            print('Not enough datasets in test file to conduct this unittest.')
            return
        self.dsets = _get_datasets([item for item in lines[:-1]])
        with open(os.path.abspath(self.dsets_path.name), 'w') as dsets_file:
            for dset in self.dsets:
                print(dset)
                dsets_file.write(dset + '\n')
        # added to prevent i/o keeping file open
        return

    def change_attribute(self, key, new_value):
        data = self.issue
        data[key] = new_value
        with open(self.issue_path, 'w') as issue:
            json.dump(data, issue)

    # def check_pid_utilitites(self):
    #     self.sanitize_user_input()
    #     self.encapsulation_test()

    @staticmethod
    def reformat_downloaded_json(dw_json):
        dw_json[URL] = []
        dw_json[MATERIALS] = []

    @staticmethod
    def save_credentials():
        _set_credentials(username=username, token=token, passphrase=passphrase)

    @staticmethod
    def reset_passphrase():
        oldpass = passphrase
        newpass = new_passphrase
        _reset_passphrase(old_pass=oldpass, new_pass=newpass)

    @staticmethod
    def reset_credentials():
        _reset_credentials()

    @staticmethod
    def check_credentials(test):
        if test:
            passphrase_key = passphrase
        else:
            passphrase_key = new_passphrase
        encrypted_username = _encrypt_with_key(username, passphrase_key)
        encrypted_token = _encrypt_with_key(token, passphrase_key)
        with open(_get_file_location('cred.txt'), 'rb') as cred_file:
            content = cred_file.readlines()
        file_username = content[0][6:][:-1]
        file_token = content[1][6:][:-1]
        if file_username == encrypted_username and file_token == encrypted_token:
            return True
        else:
            return False

    @staticmethod
    def check_installation():
        try:
            print(sub.check_output(['esgissue', '-v'], shell=True))
            sub.check_output(['esgissue', '-v'], shell=True)
            return True
        except CalledProcessError:
            return False

    @staticmethod
    def compare_json(d1, d2, ignore_keys):
        d1_filtered = dict((k, v) for k, v in d1.items() if k not in ignore_keys)
        d2_filtered = dict((k, v) for k, v in d2.items() if k not in ignore_keys)
        return d1_filtered == d2_filtered

    # @staticmethod
    # def sanitize_user_input():
    #     input_repo = os.path.join(cwd, 'samples/inputs')
    #     output_repo = os.path.join(cwd, 'samples/outputs')
    #     test_result = True
    #     for flag in range(1, 4):
    #         with open(os.path.join(input_repo, 'pid_' + str(flag) + '.txt')) as input_file:
    #             data = input_file.read()
    #         sanitized_list = []
    #         for element in data.split(','):
    #             sanitized_element = _sanitize_input_and_call_ws(element)
    #             sanitized_list.append(sanitized_element)
    #         sanitized_data = ','.join(sanitized_list)
    #         with open(os.path.join(output_repo, 'pid_' + str(flag) + '.txt')) as output_file:
    #             expected_data = output_file.read()
    #         if expected_data != sanitized_data:
    #             test_result = False
    #             print('Issue detected with file pid_' + str(flag) + '.txt')
    #     return test_result
    #
    # @staticmethod
    # def encapsulation_test():
    #     """
    #     tests whether object generated from response json is not None.
    #     :return: Boolean
    #     """
    #     input_repo = 'samples/inputs'
    #     for flag in range(1, 3):
    #         with open(os.path.join(input_repo, 'response_' + str(flag) + '.json')) as test_file:
    #             test_json = json.load(test_file)
    #             test_result = _encapsulate_pid_api_response(test_json, 200)
    #             if test_result is None:
    #                 return False
    #     return True
