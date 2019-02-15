from b2handle.handleclient import EUDATHandleClient
import uuid
import logging
import esgfpid

handle_client = EUDATHandleClient.instantiate_for_read_access()


def check_drs(drs_id):
    drs_id = drs_id.split('#')
    prefix = '21.14100/'
    hash_basis = drs_id[0]+'.v'+drs_id[1]
    hash_basis_utf8 = hash_basis.encode('utf-8')
    handle_string = uuid.uuid3(uuid.NAMESPACE_URL, hash_basis_utf8)
    encoded_dict = handle_client.retrieve_handle_record(prefix + str(handle_string))
    if encoded_dict is not None:
        return True
    else:
        print('Handle not found.')
        return False


def clear_handle(drs_id, connector):
    drs_id = drs_id.split('#')
    prefix = '21.14100/'
    hash_basis = drs_id[0]+'.v'+drs_id[1]
    hash_basis_utf8 = hash_basis.encode('utf-8')
    handle_string = uuid.uuid3(uuid.NAMESPACE_URL, hash_basis_utf8)
    encoded_dict = handle_client.retrieve_handle_record(prefix + str(handle_string))
    if encoded_dict is not None:
        handle_record = {k.decode('utf8'): v.decode('utf8') for k, v in encoded_dict.items()}
        if 'ERRATA_IDS' in handle_record.keys():
            print('Found some erratas, cleaning...')
            connector.remove_errata_ids(errata_ids=[uid for uid in str(handle_record['ERRATA_IDS']).split(';')],
                                        drs_id=drs_id[0], version_number=drs_id[1])
    else:
        print('Handle not found.')


def print_handle(drs_id):
    drs_id = drs_id.split('#')
    prefix = '21.14100/'
    hash_basis = drs_id[0]+'.v'+drs_id[1]
    hash_basis_utf8 = hash_basis.encode('utf-8')
    handle_string = uuid.uuid3(uuid.NAMESPACE_URL, hash_basis_utf8)
    encoded_dict = handle_client.retrieve_handle_record(prefix + str(handle_string))
    if encoded_dict is not None:
        handle = {k.decode('utf8'): v.decode('utf8') for k, v in encoded_dict.items()}
        print('DATASET ID : {}, VERSION {} contains '.format(drs_id[0], drs_id[1]))
        if "ERRATA_IDS" in handle.keys():
            for uid in handle['ERRATA_IDS'].split(';'):
                print uid
        else:
            print('EMPTY !')
    else:
        print('Handle not found.')


def get_handle(drs_id):
    drs_id = drs_id.split('#')
    prefix = '21.14100/'
    hash_basis = drs_id[0]+'.v'+drs_id[1]
    hash_basis_utf8 = hash_basis.encode('utf-8')
    handle_string = uuid.uuid3(uuid.NAMESPACE_URL, hash_basis_utf8)
    encoded_dict = handle_client.retrieve_handle_record(prefix + str(handle_string))
    if encoded_dict is not None:
        if encoded_dict is not None:
            handle_record = {k.decode('utf8'): v.decode('utf8') for k, v in encoded_dict.items()}
            return handle_record


def add_errata_to_handle(dataset_id, errata_id_list, connector):
    """
    given pid connector updates given handle with proper errata uids
    :param dataset_id: dataset DRS + version separated by '#'
    :param errata_id_list: the uid of the issue
    :param connector: RabbitMQ connector
    :return: nada
    """
    print('Dataset pid: ' + dataset_id)
    drs_id = dataset_id.split('#')
    print('Adding errata to {}, {}'.format(drs_id[0], drs_id[1]))
    connector.add_errata_ids(errata_ids=errata_id_list, drs_id=drs_id[0], version_number=drs_id[1])
    print('Finishing the thread...')


def check_errata_information(local_errata, remote_errata):
    for dataset_id, errata_id in remote_errata:
        if dataset_id in local_errata.keys():
            if local_errata[dataset_id] != errata_id:
                return False
        else:
            return False
    return True
