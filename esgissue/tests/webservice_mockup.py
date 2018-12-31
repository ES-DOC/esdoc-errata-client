"""
This file conatains all the mockup responses of webservices.
"""

import json
from esgissue.utils import _sanitize_input_and_call_ws, _encapsulate_pid_api_response

response_repo = 'samples/outputs'
input_repo = 'samples/inputs'

def esgfissue_check_issue(flag=1):
    """
    Resolves input, returns 3 different responses according to flag.
    1: Single errata id
    2: Multiple errata ids
    3: Nothing
    :param dataset_or_file_id:
    :return:
    """
    with open('samples/pid_' + flag + '.txt', 'r') as myfile:
        test_data = myfile.read()
        test_data = _sanitize_input_and_call_ws(test_data)
    response_full = json.load('samples/responses/response_' + flag + '.json')
    return _encapsulate_pid_api_response(api_code=200, api_json=response_full)
