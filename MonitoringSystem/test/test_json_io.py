import os
import json
from src.json_io import JsonIO



def test_receive():
    '''
    In this test is made a post request to test the receive method of the JsonIO class
    :return: True if the json is correctly received, Otherwise False
    '''
    json_path = os.path.join(os.path.abspath('..'), 'data', 'session_label_test1.json')
    with open(json_path) as f:
        json_to_send = json.load(f)
    res1 = JsonIO.get_instance().send(json_to_send)

    if res1:
        assert True
    else:
        assert False

def test2_receive():
    '''
    In this test is made a post request to test the receive method of the JsonIO class
    :return: True if the json is correctly received, Otherwise False
    '''

    json_path = os.path.join(os.path.abspath('..'), 'data', 'session_label_test2.json')
    with open(json_path) as f:
        json_to_send = json.load(f)
    res2 = JsonIO.get_instance().send(json_to_send)

    if res2:
        assert True
    else:
        assert False