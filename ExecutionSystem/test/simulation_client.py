import json
import os

from requests import post

if __name__ == '__main__':
    path = os.path.join(os.path.abspath('..'), 'classifier.json')
    print(path)
    with open(path, 'r') as f:
        classifier = json.load(f)
        print(classifier)
        post("http://192.168.1.11:5000/json", json=classifier)