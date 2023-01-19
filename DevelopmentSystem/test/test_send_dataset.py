import json
import os
from time import sleep

from requests import post

if __name__ == '__main__':
    with open(os.path.join(os.path.abspath('.'), 'dataset.json')) as f:
        dataset = json.load(f)

    sleep(20)
    for i in range(5):
        post('http://localhost:5000/json', json=dataset)
        print(f'[+] sent dataset {i}')
        sleep(1)
