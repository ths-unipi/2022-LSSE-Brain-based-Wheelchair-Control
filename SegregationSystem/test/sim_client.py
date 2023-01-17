from requests import post
import random
import json

if __name__ == '__main__':
    uuid = random.randint(0, 1000)
    command_thought = None
    e = random.randint(0, 3)
    if e == 0:
        command_thought = 'move'
    elif e == 1:
        command_thought = 'right'
    elif e == 2:
        command_thought = 'left'
    else:
        command_thought = 'stop'

    with open('p_session_example.json') as file:
        data = json.load(file)

    data['uuid'] = str(uuid)
    data['command_thought'] = command_thought

    response = post('http://localhost:5000/json', json=data)
    if response.status_code != 200:
        error_message = response.json()['error']
        print(f'Error: {error_message}')