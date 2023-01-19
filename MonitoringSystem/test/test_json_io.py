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
    for i in range (0,100):
        json_to_send['uuid'] = "a923-45b7-gh12-7408003775." + str(i)
        JsonIO.get_instance().send(json_to_send)

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