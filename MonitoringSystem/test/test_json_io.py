import os
import json
from src.json_io import JsonIO



def test_receive():
    '''
    In this test is made a post request to test the receive method of the JsonIO class
    :return: True if the json is correctly received, Otherwise False
    '''
    json_path = os.path.join(os.path.abspath('..'), 'data', 'test.json')

    with open(json_path) as f:
        json_to_send = json.load(f)
    res = JsonIO.get_instance().send(json_to_send)

    if res:
        assert True
    else:
        assert False
