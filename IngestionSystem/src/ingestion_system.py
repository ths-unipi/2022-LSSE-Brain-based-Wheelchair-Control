import os
import json
from datetime import datetime
from jsonschema import validate, ValidationError
from threading import Thread

from src.json_io import JsonIO
from src.log_utilities import red, blue, green, cyan, yellow
from src.raw_session_integrity import RawSessionIntegrity
from src.raw_sessions_store import RawSessionsStore

CONFIG_FILENAME = 'ingestion_system_config.json'
CONFIG_SCHEMA_FILENAME = 'ingestion_system_config_schema.json'


class IngestionSystem:
    """
    This class acts as a controller for the system
    """

    def __init__(self) -> None:
        """
        Initializes the system
        """
        self.last_uuid_received = None

        loaded_config = self.load_json(json_filename=CONFIG_FILENAME)
        loaded_schema = self.load_json(json_filename=CONFIG_SCHEMA_FILENAME)

        if self.validate_schema(loaded_json=loaded_config, schema=loaded_schema):
            self.ingestion_system_config = loaded_config
        else:
            print(red('[-] Error during the Ingestion System initialization phase'))
            exit(1)

    def load_json(self, json_filename: str) -> dict:
        """
        Loads a configuration file written using the JSON format
        :param json_filename: filename of the file to load
        :return: dictionary containing the configuration parameters
        """
        try:
            with open(os.path.join(os.path.abspath('..'), 'resources', json_filename)) as f:
                loaded_json = json.load(f)
                return loaded_json

        except FileNotFoundError:
            print(red(f'[-] Failed to open resources/{json_filename}'))
            exit(-1)

    def validate_schema(self, loaded_json: dict, schema: dict) -> bool:
        """
        Validates a JSON file given a schema
        :param loaded_json: JSON file loaded as a dictionary
        :param schema: schema loaded as a dictionary used for the validation
        :return: True if the validation is successful. False if the validation fails
        """
        try:
            validate(instance=loaded_json, schema=schema)
        except ValidationError:
            print(red('[-] Configuration validation failed'))
            return False

        return True

    def run(self) -> None:
        """
        Runs the Ingestion System main process
        """
        operative_mode = self.ingestion_system_config["operative_mode"]
        print(blue(f'[!] Operative Mode: {operative_mode}'))

        # Create an instance of RawSessionsStore
        raw_sessions_store = RawSessionsStore()

        # Run REST server
        listener = Thread(target=JsonIO.get_instance().listen, args=('0.0.0.0', 4000), daemon=True)
        listener.start()

        while True:
            # Wait for a new record
            received_record = JsonIO.get_instance().receive()

            # Sending Label to Monitoring System if the system is in Execution Mode
            if operative_mode == 'execution' and 'label' in received_record.keys():
                sent = JsonIO.get_instance().send(endpoint_ip=self.ingestion_system_config['monitoring_system_ip'],
                                                  endpoint_port=self.ingestion_system_config['monitoring_system_port'],
                                                  data=received_record)
                if sent:
                    current_time = datetime.now().strftime("%H:%M:%S.%f")
                    print(f'({current_time})' + blue(
                        f' [+] Label "{received_record["label"]}" sent to the Monitoring System'))

                continue

            last_missing_sample = False
            if raw_sessions_store.store_record(record=received_record):
                if self.last_uuid_received is not None:
                    if self.last_uuid_received == received_record['uuid']:
                        # Check on the current session
                        session_complete = raw_sessions_store.is_session_complete(uuid=received_record['uuid'],
                                                                                  operative_mode=operative_mode,
                                                                                  last_missing_sample=False)
                        uuid = received_record['uuid']
                    else:
                        # Check on the previous session because of a missing sample
                        current_time = datetime.now().strftime("%H:%M:%S.%f")
                        print(f'({current_time})' + yellow(
                            f' [!] Raw Session {self.last_uuid_received} missing sample detected'))
                        session_complete = raw_sessions_store.is_session_complete(uuid=self.last_uuid_received,
                                                                                  operative_mode=operative_mode,
                                                                                  last_missing_sample=True)
                        uuid = self.last_uuid_received
                        self.last_uuid_received = received_record['uuid']
                        last_missing_sample = True

                    if session_complete:
                        # If the session is complete there is no need for the next record to test "is_session_complete"
                        self.last_uuid_received = None

                        current_time = datetime.now().strftime("%H:%M:%S.%f")
                        print(f'({current_time})' + green(f' [+] Raw Session {uuid} complete'))

                        # Load Raw Session from the Data Store
                        raw_session = raw_sessions_store.load_raw_session(uuid=uuid)

                        if raw_session['uuid'] is None:
                            continue

                        # Delete Raw Session from the Data Store
                        raw_sessions_store.delete_raw_session(uuid=uuid)

                        # Check Raw Session integrity
                        threshold = self.ingestion_system_config['missing_samples_threshold']
                        raw_session_integrity = RawSessionIntegrity()
                        good_session = raw_session_integrity.mark_missing_samples(headset_eeg=raw_session['headset'],
                                                                                  threshold=threshold)

                        if good_session:
                            # Send Raw Session to the Preparation System
                            preparation_system_ip = self.ingestion_system_config['preparation_system_ip']
                            preparation_system_port = self.ingestion_system_config['preparation_system_port']
                            sent = JsonIO.get_instance().send(endpoint_ip=preparation_system_ip,
                                                              endpoint_port=preparation_system_port,
                                                              data=raw_session)
                            if sent:
                                current_time = datetime.now().strftime("%H:%M:%S.%f")
                                print(f'({current_time})' + cyan(
                                    f' [+] Raw Session {uuid} sent to the Preparation System'))
                        else:
                            current_time = datetime.now().strftime("%H:%M:%S.%f")
                            print(f'({current_time})' + red(
                                f' [-] Raw Session {uuid} discarded [threshold not satisfied]'))
                    else:
                        if last_missing_sample:
                            current_time = datetime.now().strftime("%H:%M:%S.%f")
                            print(f'({current_time})' + red(
                                f' [+] Raw Session {uuid} not complete [no recovery possible]'))
                            # Session not complete (meaning that some required record is missing)
                            # Being last_missing_samples equal to True, the system will not receive any other record
                            # related to this session (session is lost) so it must be deleted from the data store
                            raw_sessions_store.delete_raw_session(uuid=uuid)
                else:
                    self.last_uuid_received = received_record['uuid']
