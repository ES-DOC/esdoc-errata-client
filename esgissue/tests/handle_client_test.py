import esgfpid
import uuid
import requests
import logging
import datetime
from pid_ops import check_drs, add_errata_to_handle, clear_handle, print_handle


def init_logging():
    path = 'logs'
    logdate = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
    filename = path + '/log_' + logdate + logging.getLevelName(LOGLEVEL)+'.log'
    esgfpid.utils.ensure_directory_exists(path)
    myformat = '%(asctime)-15s %(levelname)-5s: %(name)s [%(threadName)s]: %(message)s'
    logging.basicConfig(level=LOGLEVEL, filename=filename, filemode='w', format=myformat)
    pikalogger = logging.getLogger('pika')
    pikalogger.setLevel(logging.WARNING)
    print('Logging to file "{}"'.format(filename))

LOGLEVEL = logging.DEBUG
PREFIX = '21.14100'
RABBIT_EXCHANGE = 'esgffed-exchange'
RABBIT_USER_TRUSTED = 'esgf-publisher'
RABBIT_URL_TRUSTED = 'handle-esgf-trusted.dkrz.de'
RABBIT_PASSWORD_TRUSTED = 'd6cab9be14'
RABBIT_URLS_OPEN = []
RABBIT_USER_OPEN = 'esgf-publisher-open'
IS_TEST = True

init_logging()
created_handles = []
data_node1 = 'foo'
thredds_service_path1 = 'bar'
trusted_node_1 = {
    'user': RABBIT_USER_TRUSTED,
    'password': RABBIT_PASSWORD_TRUSTED,
    'url': RABBIT_URL_TRUSTED,
    'priority': 1
    }
open_node = {
    'user': RABBIT_USER_OPEN,
    'url': RABBIT_URLS_OPEN
    }
list_cred = [trusted_node_1, open_node]
dataset_id = 'cmip5.output1.IPSL.IPSL-CM5A-MR.rcp45.mon.ocnBgchem.Omon.r2i2p2'
# dataset_id = 'cmip5.output1.IPSL.IPSL-CM5A-LR.abrupt4xCO2.mon.ocnBgchem.Omon.r10i1p1'
version_number = '20000101'
is_replica = False
number_of_files = 1
errata_dictionary = dict()


connector = esgfpid.Connector(
    messaging_service_credentials=list_cred,
    handle_prefix=PREFIX,
    messaging_service_exchange_name=RABBIT_EXCHANGE,
    data_node=data_node1,
    thredds_service_path=thredds_service_path1,
    test_publication=IS_TEST
    )
connector.start_messaging_thread()
print('Connection established.')
print('connector created, started messaging thread...')
print('Starting 5 Datasets test.')

while int(version_number) < 20050101:
    # If the handle doesn't exist we need to create it first.
    if not check_drs(dataset_id+'#'+version_number):
        wizard = connector.create_publication_assistant(
            drs_id=dataset_id,
            version_number=int(version_number),
            is_replica=is_replica
        )
        ds_handle = wizard.get_dataset_handle()
        created_handles.append(ds_handle)

        # Adding test file info:
        file_handle = 'hdl:'+PREFIX+'/erratatestfile_'+str(uuid.uuid1())
        created_handles.append(file_handle)
        if version_number == '20020101':
            saved_file_handle = file_handle
        if version_number != '20030101':
            file_name = 'rainfall'+version_number+'.nc'
        else:
            file_name = 'rainfall20020101.nc'
            file_handle = saved_file_handle
        file_size = 1000
        file_checksum = 'foo'
        file_publish_path = 'my/path/'+file_name
        file_checksum_type = 'SHA256'
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
        print('Checking created handle PID existence')
        handle = ds_handle.replace('hdl:', '')
        resp = requests.get('http://hdl.handle.net/api/handles/'+handle+'?auth=True')
        print('Handle '+handle)
        print('HTTP code: '+str(resp.status_code))
        print('Content:   '+str(resp.content))
    else:
        print('Clearing handle in case it has pre-existing erratas.')
        clear_handle(dataset_id+'#'+version_number, connector)
    # appending a random UUID for an errata.
    errata_uid = uuid.uuid4()
    add_errata_to_handle(dataset_id+'#'+version_number, [str(errata_uid)], connector)
    errata_dictionary[dataset_id+'#'+version_number] = errata_uid
    print("/n VERSION {}:".format(version_number))
    print_handle(dataset_id+'#'+version_number)
    version_number = str(int(version_number)+10000)
print('Test data creation finished...')
connector.finish_messaging_thread()
