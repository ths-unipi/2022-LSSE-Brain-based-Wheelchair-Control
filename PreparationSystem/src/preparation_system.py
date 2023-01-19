import json
import os
from threading import Thread
from jsonschema import validate, ValidationError
from src.json_io import JsonIO
from src.session_cleaning import SessionCleaning
from src.features_extractor import FeaturesExtractor


class PreparationSystem:

    def __init__(self):
        self._preparation_system_configuration = validate_configuration()
        self._raw_session = None
        self._prepared_session = {}

    def run(self):
        while True:
            # get received raw session
            self._raw_session = JsonIO.get_instance().get_received_json()

            print(self._raw_session['headset'][9])
            self._raw_session['headset'][9] = []
            print(self._raw_session['headset'][9])

            # correct missing samples
            SessionCleaning().correct_missing_samples(self._raw_session['headset'])
            # print(self._raw_session)
            print(self._raw_session['headset'][9])
            print(self._raw_session['headset'][8])
            print(self._raw_session['headset'][10])
            print(self._raw_session['headset'][15])
            print(self._raw_session['headset'][3])

            # correct outliers
            SessionCleaning.correct_outliers(self._raw_session['headset'],
                                             self._preparation_system_configuration['min_eeg'],
                                             self._preparation_system_configuration['max_eeg'])
            # print(self._raw_session['headset'][0])

            # extract features and prepare session
            FeaturesExtractor().extract_features \
                (self._preparation_system_configuration['features'], self._raw_session, self._prepared_session,
                 self._preparation_system_configuration['operative_mode'])

            # print(self._prepared_session)

            # Send prepared session to the endpoint corresponding to the current operating mode
            # if self._preparation_system_configuration['operative_mode'] == 'development':
            #     JsonIO.get_instance().send(self._preparation_system_configuration['segregation_endpoint_IP'],
            #                                self._preparation_system_configuration['segregation_endpoint_port'],
            #                                self._prepared_session)
            # elif self._preparation_system_configuration['operative_mode'] == 'execution':
            #     JsonIO.get_instance().send(self._preparation_system_configuration['execution_endpoint_IP'],
            #                                self._preparation_system_configuration['execution_endpoint_port'],
            #                                self._prepared_session)


def validate_configuration():
    try:
        # load configuration from file
        with open(os.path.join(os.path.abspath('..'), 'PreparationSystemConfiguration.json')) as f:
            _configuration = json.load(f)
        # load schema from file
        with open(os.path.join(os.path.abspath('..'), 'configuration_schema.json')) as f:
            _configuration_schema = json.load(f)

        # validate configuration schema
        validate(_configuration, _configuration_schema)
        return _configuration

    except FileNotFoundError:
        print('Failed to open configuration file')
        exit(1)

    except ValidationError:
        print('Config validation failed')
        exit(1)


if __name__ == '__main__':
    preparation_thread = Thread(target=PreparationSystem().run, args=())
    preparation_thread.start()
    JsonIO.get_instance().listener("0.0.0.0", "5000")
