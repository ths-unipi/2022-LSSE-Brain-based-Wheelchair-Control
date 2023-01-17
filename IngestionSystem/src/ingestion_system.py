import os
import json
from jsonschema import validate, ValidationError
from threading import Thread

from src.json_io import JsonIO
from src.raw_sessions_store import RawSessionsStore

CONFIG_FILENAME = 'ingestion_system_config.json'
CONFIG_SCHEMA_FILENAME = 'ingestion_system_config_schema.json'


class IngestionSystem:
    """
        IngestionSystem class
    """

    def __init__(self) -> None:
        loaded_config = self.load_json(json_filename=CONFIG_FILENAME)
        loaded_schema = self.load_json(json_filename=CONFIG_SCHEMA_FILENAME)

        if self.validate_schema(loaded_json=loaded_config, schema=loaded_schema):
            self.ingestion_system_config = loaded_config
        else:
            print('[-] Error during the ingestion system initialization phase')
            exit(1)

    def load_json(self, json_filename: str) -> dict:
        try:
            with open(os.path.join(os.path.abspath('..'), 'resources', json_filename)) as f:
                loaded_json = json.load(f)
                return loaded_json

        except FileNotFoundError:
            print(f'[-] Failed to open resources/{json_filename}')
            exit(-1)

    def validate_schema(self, loaded_json: dict, schema: dict) -> bool:
        try:
            validate(instance=loaded_json, schema=schema)
        except ValidationError:
            print('[-] Configuration validation failed')
            return False

        return True

    def run(self) -> None:
        print('[!] Configuration loaded:')
        print(self.ingestion_system_config)

        operative_mode = self.ingestion_system_config["operative_mode"]
        print(f'Operative Mode: {operative_mode}')

        # Create an instance of RawSessionsStore
        raw_sessions_store = RawSessionsStore()

        # Run REST server
        listener = Thread(target=JsonIO.get_instance().listen, args=('0.0.0.0', 5000))
        listener.start()

        while True:
            # Wait for a new record
            received_record = JsonIO.get_instance().get_received_record()
            # print(f'[+] Received record: {received_record}')

            uuid = received_record['UUID']

            if raw_sessions_store.store_record(record=received_record):
                if raw_sessions_store.is_session_complete(uuid=uuid, operative_mode=operative_mode):
                    print(f'[+] SESSION {uuid} IS COMPLETE')

                    # Load Raw Session from the Data Store
                    raw_session = dict()
                    raw_session = raw_sessions_store.load_raw_session(uuid=uuid)

                    # TODO: Mark missing samples
                    if raw_session['UUID'] is not None:
                        pass

                    # Delete Raw Session from the Data Store
                    if raw_sessions_store.delete_raw_session(uuid=uuid):
                        print(f'SESSION {uuid} DELETED SUCCESSFULLY')

                    '''  
                    # Check mark missing samples threshold and send it to the Preparation System            
                    if missing_samples < self.ingestion_system_config['missing_samples_threshold']:
                        res = JsonIO.get_instance().send(endpoint_ip=self.ingestion_system_config['endpoint_ip'],
                                                   endpoint_port=self.ingestion_system_config['endpoint_port'],
                                                   raw_session=raw_session)
                        if res:
                            print(f'[+] SESSION {uuid} SENT TO THE PREPARATION SYSTEM')'''

        # =======================================================================
        # End while
