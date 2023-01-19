from jsonschema import validate, ValidationError
from src.json_io import JsonIO
from threading import Thread
from src.mental_command_classifier import MentalCommandClassifier
from src.monitoring_phase import MonitoringPhase

import json
import os
import pickle


def open_json_file(path):
    try:
        with open(os.path.join(path)) as f:
            json_file =json.load(f)

    except FileNotFoundError:
        print('Failed to open file')
        exit(1)

    return json_file



def validate_configuration():
    try:
        # load configuration file
        configuration = open_json_file(os.path.join(os.path.abspath('..'), 'configurationExecutionSystem.json'))

        # load validator file
        validator_schema = open_json_file(os.path.join(os.path.abspath('..'),'configurationExecutionSystemValidator.json'))

        # validate json
        validate(configuration, validator_schema)
        print("Validation complete")
        return configuration



    except ValidationError:
        print('Config validation failed')
        exit(1)


class ExecutionSystem:

    def __init__(self):
        self._configuration_execution_system = validate_configuration()

    def run(self):

        operating_mode = self._configuration_execution_system['operating_mode']
        while(True):
            if operating_mode == 'development':
                json_file = JsonIO.get_instance().get_received_json()
                # if we are in the development flow, we receive the best classifier and save it on a file
                if (MentalCommandClassifier().deploy_classifier(json_file)):
                    print("Deployment completed successfully")
                    exit(0)
                print("Classifier not loaded correctly")
            else:
                # if we are in the execution flow:
                # we receive the prepared session
                MentalCommandClassifier()._prepared_session = JsonIO.get_instance().get_received_json()
                # we increment the counter of the Monitoring Phase
                MonitoringPhase().increment_session_counter()
                # we load the best classifier from the .json file
                #     classifier = open_json_file(os.path.join(os.path.abspath('..'), 'mental_command_classifier.json'))
                #     mlp_classifier = pickle.loads(classifier['classifier'].encode('ISO-8859-1'))

                   # prediction = mlp_classifier.predict(session)

        exit(0)


if __name__ == '__main__':
    execution_thread = Thread(target=ExecutionSystem().run, args=())
    execution_thread.setDaemon(True)
    execution_thread.start()
    JsonIO.get_instance().listener('0.0.0.0', 5000)


