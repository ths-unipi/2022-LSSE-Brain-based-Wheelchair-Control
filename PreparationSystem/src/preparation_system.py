import json
import os
from threading import Thread
from jsonschema import validate, ValidationError
from json_io import JsonIO


class PreparationSystem:

    def __init__(self):
        self._preparation_system_configuration = validate_configuration()
        self._raw_session = None
        self._prepared_session = None

    def run(self):
        while True:
            self._raw_session = JsonIO.get_instance().get_received_json()


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
