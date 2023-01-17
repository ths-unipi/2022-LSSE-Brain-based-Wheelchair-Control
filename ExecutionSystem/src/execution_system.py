from jsonschema import validate, ValidationError
from src.json_io import JsonIO
from threading import Thread

import json
import os
import pickle


def validate_configuration():
    try:
        # load configuration file
        with open(os.path.join(os.path.abspath('..'), 'configurationExecutionSystem.json')) as configuration_file:
            configuration = json.load(configuration_file)

        # load validator file
        with open( os.path.join(os.path.abspath('..'),'configurationExecutionSystemValidator.json')) \
                as configuration_validator:
            validator_schema = json.load(configuration_validator)

        # validate json
        validate(configuration, validator_schema)
        print("Validation complete")
        return configuration

    except FileNotFoundError:
        print('Failed to open file')
        exit(1)

    except ValidationError:
        print('Config validation failed')
        exit(1)


class ExecutionSystem:

    def __init__(self):
        self._configuration_execution_system = validate_configuration()

    def run(self):
        operating_mode = self._configuration_execution_system['operating_mode']
        while(True):
            json_file = JsonIO.get_instance().get_received_json()
            # if operating_mode == 'execution':
            #     with open('mental_command_session_classifier.json') as f:
            #         classifier = json.load(f)
            #         mlp_classifier = pickle.loads(classifier['classifier'].encode('ISO-8859-1'))
            #         # prediction = mlp_classifier.predict(session)



if __name__ == '__main__':
    # new thread for execution system
    execution_thread = Thread(target=ExecutionSystem().run, args=())
    execution_thread.start()

    # rest server in main thread
    JsonIO.get_instance().listener('0.0.0.0', 5000)