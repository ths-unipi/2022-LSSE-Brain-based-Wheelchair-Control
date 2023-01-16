import json
import os.path
from threading import Thread
from jsonschema import validate, ValidationError

from src.json_io import JsonIO


class DevelopmentSystem:

    def __init__(self) -> None:
        # open config and schema
        with open(os.path.join(os.path.abspath('..'), 'resources', 'development_system_config_schema.json')) as f:
            config_schema = json.load(f)
        with open(os.path.join(os.path.abspath('..'), 'development_system_config.json')) as f:
            self.config = json.load(f)

        # validate the schema
        try:
            validate(self.config, config_schema)
        except ValidationError:
            print('[-] Config validation failed')
            exit(1)

        self.mental_command_classifier = None

    def run(self):
        if self.config['operational_mode'] == 'waiting_for_dataset':
            learning_session_set = JsonIO.get_instance().get_queue().get(block=True)
            print(learning_session_set)

    def open_server(self):
        JsonIO.get_instance().listen('0.0.0.0', 5000)
