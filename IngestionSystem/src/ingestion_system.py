import json
from jsonschema import validate, ValidationError

from src.raw_sessions_store import RawSessionsStore

CONFIG_PATH = '../resources/ingestion_system_config.json'
CONFIG_SCHEMA_PATH = '../resources/ingestion_system_config_schema.json'


class IngestionSystem:
    """
        IngestionSystem class
    """

    def __init__(self) -> None:
        loaded_config = self.load_json(json_path=CONFIG_PATH)
        loaded_schema = self.load_json(json_path=CONFIG_SCHEMA_PATH)

        if self.validate_schema(loaded_json=loaded_config, schema=loaded_schema):
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

        # RawSessionsStore
        raw_sessions_store = RawSessionsStore()

        example_record = '{ \
            "LABELS": "stop", \
            "TIMESTAMP": "26-Oct-2021 09:03:38", \
            "UUID": "a923-45b7-gh12-7408003775.463" \
        }'

        rec = json.loads(example_record)
        raw_sessions_store.store_record(record=rec)

        example_record = '{ \
            "TIMESTAMP": "26-Oct-2021 09:04:40", \
            "UUID" : "a923-45b7-gh12-7408003775.463", \
            "CALENDAR": "working" \
        }'
        rec = json.loads(example_record)
        raw_sessions_store.store_record(record=rec)

        example_record = '{ \
            "TIMESTAMP": "26-Oct-2021 09:04:40", \
            "UUID" : "a923-45b7-gh12-7408003775.463", \
            "SETTINGS": "indoor" \
        }'
        rec = json.loads(example_record)
        raw_sessions_store.store_record(record=rec)

        example_record = '{ \
            "TIMESTAMP": "26-Oct-2021 09:03:46", \
            "UUID" : "a923-45b7-gh12-7408003775.463", \
            "CHANNEL": 2, \
            "Var5": 3.564453125, \
            "Var6": 3.759765625, \
            "Var7": 6.0546875, \
            "Var8": 3.515625, \
            "Var9": 15.576171875, \
            "Var10": 1.611328125, \
            "Var11": 3.80859375, \
            "Var12": 7.861328125, \
            "Var13": 1.611328125, \
            "Var14": 2.5390625, \
            "Var15": -5.615234375, \
            "Var16": 6.201171875, \
            "Var17": 0, \
            "Var18": 0, \
            "Var19": 7.71484375, \
            "Var20": 4.8828125 \
        }'
        rec = json.loads(example_record)
        raw_sessions_store.store_record(record=rec)

        example_record = '{ \
            "TIMESTAMP": "26-Oct-2021 09:04:40", \
            "UUID" : "a923-45b7-gh12-7408003775.463", \
            "CHANNEL": 12, \
            "Var5": 1.865453125, \
            "Var6": 6.059765625, \
            "Var7": 0, \
            "Var8": 1.331625, \
            "Var9": 5.766171875, \
            "Var10": 1.611328125, \
            "Var11": 3.80859375, \
            "Var12": 7.861328125, \
            "Var13": 1.611328125, \
            "Var14": 2.5390625, \
            "Var15": -5.615234375, \
            "Var16": 6.201171875, \
            "Var17": 0, \
            "Var18": 0, \
            "Var19": 7.71484375, \
            "Var20": 4.8828125 \
        }'
        rec = json.loads(example_record)
        raw_sessions_store.store_record(record=rec)

        example_record = '{ \
            "TIMESTAMP": "26-Oct-2021 09:03:40", \
            "UUID" : "a923-45b7-gh12-7408003775.463", \
            "CHANNEL": 1, \
            "Var5": 3.564453125, \
            "Var6": 3.759765625, \
            "Var7": 6.0546875, \
            "Var8": 3.515625, \
            "Var9": 15.576171875, \
            "Var10": 1.611328125, \
            "Var11": 3.80859375, \
            "Var12": 7.861328125, \
            "Var13": 1.611328125, \
            "Var14": 2.5390625, \
            "Var15": -5.615234375, \
            "Var16": 6.201171875, \
            "Var17": 0, \
            "Var18": 0, \
            "Var19": 7.71484375, \
            "Var20": 4.8828125 \
        }'
        rec = json.loads(example_record)
        raw_sessions_store.store_record(record=rec)

        raw_sessions_store.load_raw_session(rec['UUID'])
        if raw_sessions_store.is_session_complete(rec['UUID'], self.ingestion_system_config['operative_mode']):
            print(f'[{self.ingestion_system_config["operative_mode"]}] SESSION IS COMPLETE')
        else:
            print(f'[{self.ingestion_system_config["operative_mode"]}] SESSION IS NOT COMPLETE')

        #if raw_sessions_store.delete_raw_session(uuid=rec['UUID']):
        #    print(f'[+] {rec["UUID"]} deleted from the store')

        # JsonIO
        # RawSessionIntegrity
