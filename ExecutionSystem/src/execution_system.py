from jsonschema import validate, ValidationError
from src.json_io import JsonIO
from flask import request
from threading import Thread

import json
import os

json_io_instance = JsonIO()
app = json_io_instance.app

@app.post('/json')
def post_json():
    if request.json is None:
        return {'error': 'No JSON received'}, 500

    received_json = request.json

    thread_receive = Thread(target=json_io_instance.receive, args=(received_json,))
    thread_receive.start()

    return {}, 200

class ExecutionSystem:

    def __init__(self):
        try:
            # load configuration file
            with open(os.path.join(os.path.abspath('..'), 'configurationExecutionSystem.json')) as configuration_file:
                self._configuration_execution_system = json.load(configuration_file)

            # load validator file
            with open( os.path.join(os.path.abspath('..'),'configurationExecutionSystemValidator.json')) \
                    as configuration_validator:
                validator_schema = json.load(configuration_validator)

            # validate json
            validate(self._configuration_execution_system, validator_schema)
            print("Validation complete")



        except FileNotFoundError:
            print('Failed to open file')
            exit(1)

        except ValidationError:
            print('Config validation failed')
            exit(1)

    def run(self):
        operating_mode = self._configuration_execution_system['operating_mode']
        while(True):
            json_file = json_io_instance._received_json_queue.get(block=True)
            print(json_file)


if __name__ == '__main__':
    # new thread for execution system
    execution_thread = Thread(target=ExecutionSystem().run, args=())
    execution_thread.start()

    # rest server in main thread
    json_io_instance.listener('0.0.0.0', 5000)