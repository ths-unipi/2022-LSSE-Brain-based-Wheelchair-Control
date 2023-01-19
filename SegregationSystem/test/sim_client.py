from requests import post
import random
import json

if __name__ == '__main__':
    sessions = 100
    while sessions > 0:
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

        i = 0
        while i < 22:
            data['features']['alpha'].append(random.randint(-5, 6))
            data['features']['beta'].append(random.randint(-5, 6))
            data['features']['delta'].append(random.randint(-5, 6))
            data['features']['theta'].append(random.randint(-5, 6))
            i += 1

        response = post('http://localhost:5000/json', json=data)
        if response.status_code != 200:
            error_message = response.json()['error']
            print(f'Error: {error_message}')

        sessions -= 1
