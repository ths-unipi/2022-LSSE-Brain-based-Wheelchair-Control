import json
import os
from datetime import datetime
from threading import Thread
from jsonschema import validate, ValidationError
from src.json_io import JsonIO
from src.session_cleaning import SessionCleaning
from src.features_extractor import FeaturesExtractor


class PreparationSystem:

    def __init__(self):
        self._preparation_system_configuration = self.get_configuration()
        self._raw_session = None
        self._prepared_session = None

    def run(self):
        while True:
            # get received raw session
            self._raw_session = JsonIO.get_instance().get_received_json()
            print('[+] raw session received')

            # correct missing samples
            SessionCleaning().correct_missing_samples(self._raw_session['headset'])

            # correct outliers
            SessionCleaning.correct_outliers(self._raw_session['headset'],
                                             self._preparation_system_configuration['min_eeg'],
                                             self._preparation_system_configuration['max_eeg'])

            # extract features and prepare session
            self._prepared_session = {}
            FeaturesExtractor().extract_features \
                (self._preparation_system_configuration['features'], self._raw_session, self._prepared_session,
                 self._preparation_system_configuration['operative_mode'])

            print('[+] features extracted and session prepared')

            # Send prepared session to the endpoint corresponding to the current operating mode
            if self._preparation_system_configuration['operative_mode'] == 'development':
                JsonIO.get_instance().send(self._preparation_system_configuration['segregation_endpoint_IP'],
                                           self._preparation_system_configuration['segregation_endpoint_port'],
                                           self._prepared_session)
            elif self._preparation_system_configuration['operative_mode'] == 'execution':
                JsonIO.get_instance().send(self._preparation_system_configuration['execution_endpoint_IP'],
                                           self._preparation_system_configuration['execution_endpoint_port'],
                                           self._prepared_session)
            print(f'[+] prepared session sent at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
            print(self._prepared_session)

    @staticmethod
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
            return None

        except ValidationError:
            print('Config validation failed')
            return None

    def get_configuration(self):
        configuration = self.validate_configuration()
        if configuration is None:
            exit(1)
        return configuration


if __name__ == '__main__':
    preparation_thread = Thread(target=PreparationSystem().run, args=())
    preparation_thread.start()
    JsonIO.get_instance().listener("0.0.0.0", "5000")
