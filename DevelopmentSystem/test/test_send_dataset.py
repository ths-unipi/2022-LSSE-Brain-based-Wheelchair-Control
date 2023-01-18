import json
import os
from requests import post

if __name__ == '__main__':
    with open(os.path.join(os.path.abspath('.'), 'dataset.json')) as f:
        dataset = json.load(f)

    post('http://localhost:5000/json', json=dataset)
