from jsonschema import validate, ValidationError
from src.json_io import JsonIO
from threading import Thread
from src.mental_command_classifier import MentalCommandClassifier
from src.monitoring_phase import MonitoringPhase

import json
import os


def open_json_file(path):
    try:
        with open(os.path.join(path)) as f:
            json_file = json.load(f)

    except FileNotFoundError:
        print('***Execution System***   Failed to open file')
        exit(1)

    return json_file


def validate_configuration():
    try:
        # load configuration file
        configuration = open_json_file(os.path.join(os.path.abspath('..'), 'configurationExecutionSystem.json'))

        # load validator file
        validator_schema = \
            open_json_file(os.path.join(os.path.abspath('..'), 'configurationExecutionSystemValidator.json'))

        # validate json
        validate(configuration, validator_schema)
        print("***Execution System***   Validation complete")
        return configuration

    except ValidationError:
        print('***Execution System***   Config validation failed')
        exit(1)


class ExecutionSystem:

    def __init__(self):
        self._configuration_execution_system = validate_configuration()

    def run(self):
        mental_command_classifier_instance = MentalCommandClassifier()
        monitoring_instance = MonitoringPhase()
        while True:
            if self._configuration_execution_system['operating_mode'] == 'development':
                json_file = JsonIO.get_instance().get_received_json()
                # if there is the development flow, the best classifier is received and saved on a file
                if mental_command_classifier_instance.deploy_classifier(json_file):
                    print("***Execution System***   Deployment completed successfully")
                    exit(0)

            else:
                # if there is the execution flow:
                # the prepared session is received
                mental_command_classifier_instance._prepared_session = JsonIO.get_instance().get_received_json()
                # the counter of the Monitoring Phase is incremented
                monitoring_instance.increment_session_counter()
                # the best classifier from the .json file is loaded
                classifier = open_json_file(os.path.join
                                            (os.path.abspath('..'), 'data','mental_command_classifier.json'))
                #print(classifier)
                # the response of the classifier is computed
                final_label = list(mental_command_classifier_instance.execute_classifier(classifier))[0]
                # the label is sent to the client
                print(f"***Execution System***   The final prediction is: {final_label}")
                if monitoring_instance.check_threshold(self._configuration_execution_system['threshold_value']):
                # if the number of session received is equal or greater than the threshold:
                # the final label is prepared for the monitoring system
                    label_to_send = monitoring_instance.prepare_label \
                        (mental_command_classifier_instance._prepared_session['uuid'], final_label)
                    print(f"***Execution System***   The label to send is: {label_to_send}")
                # the label is sent to the monitoring system
                    JsonIO.get_instance().send_json("172.16.0.15", 5000, label_to_send)
        exit(0)


if __name__ == '__main__':
    execution_thread = Thread(target=ExecutionSystem().run, args=())
    execution_thread.setDaemon(True)
    execution_thread.start()
    JsonIO.get_instance().listener('0.0.0.0', 5000)
