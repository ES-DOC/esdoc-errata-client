from subprocess import CalledProcessError

from esgissue.esgissue import process_command
from esgissue.constants import *
# from esgissue.utils import set_credentials, reset_passphrase, encrypt_with_key, reset_credentials, get_datasets, \
#                             prepare_persistence, _get_f

from esgissue.utils import _set_credentials, _reset_passphrase, _encrypt_with_key, _reset_credentials, _get_datasets, \
                           _get_retrieve_dirs, _get_file_location, _encapsulate_pid_api_response, \
                           _sanitize_input_and_call_ws

from esgissue.errata_object_factory import ErrataCollectionObject, ErrataObject
from b2handle.handleclient import EUDATHandleClient
import uuid
import os
import subprocess as sub
import json
import esgfpid
import requests
from time import sleep


prefix = '21.14100/'
download_dir = 'samples/download/'
download_issue = 'dw_issue.json'
download_dset = 'dw_dset.txt'
username = 'AtefBN'
token = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
passphrase = 'atef'
new_passphrase = 'newPassphrase@=#125_a'


class Actionwords:
    def __init__(self, test_issue_file, test_dset_file, extra_dsets_file=None, uid=None):
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
        process_command(command=CREATE, issue_file=self.issue, dataset_file=self.dsets, passphrase=passphrase,
                        issue_path=self.issue_path, dataset_path=self.dsets_path)
        self.check_issue_files()
        _reset_credentials()

    def update_issue(self):
        _set_credentials(username=username, token=token, passphrase=passphrase)
        process_command(command=UPDATE, issue_file=self.issue, dataset_file=self.dsets, passphrase=passphrase,
                        issue_path=self.issue_path, dataset_path=self.dsets_path)
        self.check_issue_files()
        _reset_credentials()

    def close_issue(self):
        _set_credentials(username=username, token=token, passphrase=passphrase)
        process_command(command=CLOSE, issue_file=self.issue, dataset_file=self.dsets, passphrase=passphrase,
                        issue_path=self.issue_path, dataset_path=self.dsets_path, status=STATUS_RESOLVED)
        self.check_issue_files()
        _reset_credentials()

    def retrieve_issue(self):
        process_command(command=RETRIEVE, issue_path=self.issue, dataset_path=self.dsets,
                        list_of_ids=[self.uid])

    def check_issue_pid(self):
        # Checking PID HANDLE
        print('checkin PIDs')
        sleep(5)
        handle_client = EUDATHandleClient.instantiate_for_read_access()
        self.uid = self.issue['uid']
        for line in self.dsets:
            print('CHECKING {} ERRATA IDS'.format(line))
            exists = False
            dataset = line.split('#')
            dset_id = dataset[0]
            dset_version = dataset[1]
            hash_basis = dset_id+'.v'+dset_version
            hash_basis_utf8 = hash_basis.encode('utf-8')
            handle_string = uuid.uuid3(uuid.NAMESPACE_URL, hash_basis_utf8)
            encoded_dict = handle_client.retrieve_handle_record(prefix + str(handle_string))
            if encoded_dict is not None:
                    handle_record = {k.decode('utf8'): v.decode('utf8') for k, v in encoded_dict.items()}
                    if 'ERRATA_IDS' in handle_record.keys():
                        for uid in str(handle_record['ERRATA_IDS']).split(';'):
                            if uid == self.uid:
                                exists = True
                                break
            if not exists:
                print('An error occurred updating handle.')
                return exists

    def check_issue_files(self):
        # Comparing local file to server copy.
        self.uid = self.issue['uid']
        issue_dw = ''
        dataset_dw = ''
        process_command(command=RETRIEVE, issue_path=issue_dw, dataset_path=dataset_dw, list_of_ids=[self.uid])
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
        if issue_file_test and dataset_file_test:
            return True
        else:
            return False

    def change_severity(self):
        self.change_attribute('severity', 'medium')

    def change_description(self):
        self.change_attribute('description', "An issue with a single dataset but multiple notations updated.")

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
        self.dsets = _get_datasets([item for item in lines[:-1]])
        with open(os.path.abspath(self.dsets_path.name), 'w') as dsets_file:
            for dset in self.dsets:
                print(dset)
                dsets_file.write(dset + '\n')

    def change_attribute(self, key, new_value):
        data = self.issue
        data[key] = new_value
        with open(self.issue_path, 'w') as issue:
            json.dump(data, issue)

    def check_pid_utilitites(self):
        self.sanitize_user_input()
        self.encapsulation_test()

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
        file_username = content[0].split('entry:')[1].replace('\n', '')
        file_token = content[1].split('entry:')[1].replace('\n', '')
        if file_username == encrypted_username and file_token == encrypted_token:
            return True
        else:
            return False

    @staticmethod
    def check_installation():
        try:
            print sub.check_output(['esgissue', '-v'], shell=True)
            sub.check_output(['esgissue', '-v'], shell=True)
            return True
        except CalledProcessError:
            return False

    @staticmethod
    def compare_json(d1, d2, ignore_keys):
        d1_filtered = dict((k, v) for k, v in d1.iteritems() if k not in ignore_keys)
        d2_filtered = dict((k, v) for k, v in d2.iteritems() if k not in ignore_keys)
        return d1_filtered == d2_filtered

    @staticmethod
    def sanitize_user_input():
        input_repo = 'samples/inputs'
        output_repo = 'samples/outputs'
        test_result = True
        for flag in range(1, 4):
            with open(os.path.join(input_repo, 'pid_'+str(flag)+'.txt')) as input_file:
                data = input_file.read()
            sanitized_list = []
            for element in data.split(','):
                sanitized_element = _sanitize_input_and_call_ws(element)
                sanitized_list.append(sanitized_element)
            sanitized_data = ','.join(sanitized_list)
            print(sanitized_data)
            with open(os.path.join(output_repo, 'pid_'+ str(flag) + '.txt')) as output_file:
                expected_data = output_file.read()
            if expected_data != sanitized_data:
                print(sanitized_data)
                test_result = False
                print('Issue detected with file pid_'+str(flag)+'.txt')
        return test_result

    @staticmethod
    def encapsulation_test():
        """
        tests whether object generated from response json is not None.
        :return: Boolean
        """
        input_repo = 'samples/inputs'
        for flag in range(1, 3):
            with open(os.path.join(input_repo, 'response_'+str(flag)+'.json')) as test_file:
                test_json = json.load(test_file)
                test_result = _encapsulate_pid_api_response(test_json, 200)
                if test_result is None:
                    return False
        return True


def create_handle_for_dataset(dataset_list):
    data_node1 = "foo"
    is_test  = True
    is_synchronous = True
    prefix =  21.14100
    rabbit_exchange = "esgffed-exchange"
    rabbit_password_trusted = "LDfj5784T4VeKTxwhpqk8UmSqbC9DkTW"
    rabbit_user_open = "esgf-publisher-open"
    rabbit_user_trusted = "esgf-publisher"
    rabbit_urls_open = []
    rabbit_url_trusted = "207.38.94.86"
    port = "32272"
    vhost = "esgf-pid"


    sync_retry_interval_in_seconds = 900
    thredds_service_path1 = "bar"
    ssl_enabled = "true"

    cred = dict(user=rabbit_user_trusted, password=rabbit_password_trusted, url=rabbit_url_trusted,
                vhost=vhost, port=port, ssl_enabled=ssl_enabled)

    connector = esgfpid.Connector(
        messaging_service_credentials=[cred],
        handle_prefix=prefix,
        messaging_service_exchange_name=rabbit_exchange,
        data_node=data_node1,
        test_publication=is_test,
        thredds_service_path=thredds_service_path1,
        message_service_synchronous=is_synchronous
        )
    connector.start_messaging_thread()
    for dset in dataset_list:
        dataset = dset.split('#')
        dataset_id = dataset[0]
        version_number = dataset[1]
        is_replica = False
        number_of_files = 1
        print('Creating handle for dataset {}'.format(dataset_id))
        wizard = connector.create_publication_assistant(
            drs_id=dataset_id,
            version_number=int(version_number),
            is_replica=is_replica
            )
        ds_handle = wizard.get_dataset_handle() # HERE YOU GET THE DATASET PID

    # Adding a number of files
        for i in xrange(number_of_files):
            # Test file info:       ### PLEASE COMPLETE!
            file_num = i+1
            file_handle = 'hdl:'+prefix+'/erratatestfile_'+str(uuid.uuid1())
            file_name = 'testfile_number_'+str(file_num)+'.nc'
            file_size = 1000
            file_checksum = 'foo'
            file_publish_path = 'my/path/'+file_name
            file_checksum_type='SHA256'
            file_version = 'foo'

            # Add this test file info:
            wizard.add_file(
                file_name=file_name,
                file_handle=file_handle,
                file_size=file_size,
                checksum=file_checksum,
                publish_path=file_publish_path,
                checksum_type=file_checksum_type,
                file_version=file_version
            )

        wizard.dataset_publication_finished()
        print('\n\nChecking PID existence')
        handle = ds_handle.replace('hdl:', '')
        resp = requests.get('http://hdl.handle.net/api/handles/'+handle+'?auth=True')
        print('\n\nHandle '+handle)
        print('HTTP code: '+str(resp.status_code))
        print('Content:   '+str(resp.content))
    # Finish messaging thread
    connector.finish_messaging_thread()
