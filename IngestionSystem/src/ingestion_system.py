import json
from jsonschema import validate, ValidationError

CONFIG_PATH = '../ingestion_system_config.json'
CONFIG_SCHEMA_PATH = '../ingestion_system_config_schema.json'


class IngestionSystem:
    """
        IngestionSystem class acts as a controller for the system
    """

    def __init__(self) -> None:
        loaded_config = self.load_json(CONFIG_PATH)

        if self.validate_schema(loaded_config):
            print('[+] Configuration loaded')
            self.ingestion_system_config = loaded_config
        else:
            print('[-] Error during the ingestion system initialization phase')
            exit(1)

    def load_json(self, json_path: str) -> dict:
        try:
            with open(json_path) as f:
                loaded_json = json.load(f)
                return loaded_json

        except FileNotFoundError:
            print(f'[-] Failed to open {json_path}')
            exit(-1)

    def validate_schema(self, loaded_config: dict) -> bool:
        try:
            loaded_schema = self.load_json(CONFIG_SCHEMA_PATH)
            validate(loaded_config, loaded_schema)

        except ValidationError:
            print('[-] Configuration validation failed')
            return False

        return True

    def run(self) -> None:
        print('[!] Configuration loaded:')
        print(self.ingestion_system_config)
