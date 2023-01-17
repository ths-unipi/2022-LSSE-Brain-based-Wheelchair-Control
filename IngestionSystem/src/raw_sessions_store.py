import sqlite3
import json
from jsonschema import validate, ValidationError

from src.raw_session import RawSession

DB_PATH = '../data/RawSessionsStore.db'
RECORD_TYPE = ['CALENDAR', 'LABELS', 'SETTINGS', 'CHANNEL']
NUM_CHANNELS = 12


class RawSessionsStore:
    """
        RawSessionsStore class
    """

    def __init__(self) -> None:
        self._conn = None

        if self.open_connection() and self.create_table():
            print('[+] sqlite3 connection established and raw_session table initialized')
        else:
            print('[-] sqlite3 initialize failed')
            exit(-1)

    def open_connection(self) -> bool:
        try:
            self._conn = sqlite3.connect(DB_PATH)
            return True
        except sqlite3.Error as e:
            print(f'[-] sqlite3 open connection error [{e}]')

        return False

    def close_connection(self) -> None:
        try:
            self._conn.close()
        except sqlite3.Error as e:
            print(f'[-] sqlite3 close connection error [{e}]')
            exit(-1)

    def check_connection(self) -> None:
        if self._conn is None:
            print('[-] sqlite3 connection not established')
            exit(-1)

    def create_table(self) -> bool:
        self.check_connection()

        try:
            channel_columns = str()
            for i in range(1, NUM_CHANNELS + 1):
                channel_columns += RECORD_TYPE[3] + '_' + str(i) + ' text, '

            query = 'CREATE TABLE IF NOT EXISTS raw_session ( \
                uuid text NOT NULL, \
                ' + RECORD_TYPE[0] + ' text, \
                ' + RECORD_TYPE[1] + ' text, \
                ' + RECORD_TYPE[2] + ' text, \
                ' + channel_columns + ' \
                UNIQUE(uuid), PRIMARY KEY (uuid)' \
                                      ')'
            self._conn.cursor().execute(query)
            self._conn.commit()
        except sqlite3.Error as e:
            print(f'[-] sqlite3 "create_tables" error [{e}]')
            return False

        return True

    def drop_table(self) -> bool:
        self.check_connection()

        try:
            self._conn.cursor().execute('DROP TABLE IF EXISTS raw_session')
            self._conn.commit()
        except sqlite3.Error as e:
            print(f'[-] sqlite3 "drop_table" error [{e}]')
            return False

        return True

    def get_record_type(self, record: dict) -> str:
        for record_type in RECORD_TYPE:
            if record_type in record.keys():
                return record_type

        return 'None'

    def load_record_schema(self, schema_path: str) -> dict:
        try:
            with open(schema_path) as f:
                loaded_schema = json.load(f)
                return loaded_schema

        except FileNotFoundError:
            print(f'[-] Failed to open {schema_path}')
            exit(-1)

    def validate_schema_record(self, record: dict, record_type: str) -> bool:
        try:
            loaded_schema = self.load_record_schema('../resources/' + record_type.lower() + '_schema.json')
            validate(record, loaded_schema)

        except ValidationError:
            print('[-] Record schema validation failed')
            return False

        return True

    def generate_query_parameters(self, record: dict, record_type: str) -> tuple:

        parameters = {
            'UUID': record['UUID'],
            'CALENDAR': None,
            'LABELS': None,
            'SETTINGS': None,
            'CHANNELS': [None] * NUM_CHANNELS
        }

        if record_type == 'CHANNEL':
            channel = record['CHANNEL'] - 1
            parameters['CHANNELS'][channel] = json.dumps(record)
        else:
            parameters[record_type] = json.dumps(record)

        values = list(parameters.values())
        query_parameters = values[0:-1] + values[-1]

        return tuple(query_parameters)

    def update_record(self, record: dict, column_to_set: str) -> bool:
        try:
            query = 'UPDATE raw_session SET ' + column_to_set + ' = ? WHERE uuid = ?'
            cursor = self._conn.cursor()
            cursor.execute(query, (json.dumps(record), record['UUID']))
            self._conn.commit()
        except sqlite3.Error as e:
            print(f'[-] sqlite3 "update_record" error [{e}]')
            return False

    def insert_record(self, parameters: tuple) -> bool:
        try:
            query = 'INSERT INTO raw_session (uuid, calendar, labels, settings, ' \
                    'channel_1, channel_2, channel_3, channel_4, channel_5, channel_6, ' \
                    'channel_7, channel_8, channel_9, channel_10, channel_11, channel_12 ) ' \
                    'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
            cursor = self._conn.cursor()
            cursor.execute(query, parameters)
            self._conn.commit()
        except sqlite3.Error as e:
            print(f'[-] sqlite3 "insert_record" error [{e}]')
            return False

        return True

    def row_exists(self, uuid: str) -> bool:
        try:
            cursor = self._conn.cursor()
            cursor.execute('SELECT COUNT(1) FROM raw_session WHERE uuid = ?', (uuid,))
            self._conn.commit()

            result = cursor.fetchone()
            if result[0] == 0:
                return False
            else:
                return True

        except sqlite3.Error as e:
            print(f'[-] sqlite3 "row_exists" error [{e}]')
            # TODO: check if this return is correct (it can be ambiguous)
            return False

    def store_record(self, record: dict) -> bool:
        self.check_connection()

        print(f'[!] record to store: {record}')
        record_type = self.get_record_type(record)
        print(f'[!] record type: {record_type}')

        if not self.validate_schema_record(record, record_type):
            print("[-] Record schema not valid (record discarded)")
            return False

        if self.row_exists(record['UUID']):
            if record_type == 'CHANNEL':
                column_name = record_type + '_' + str(record['CHANNEL'])
            else:
                column_name = record_type
            self.update_record(record=record, column_to_set=column_name)
        else:
            self.insert_record(parameters=self.generate_query_parameters(record, record_type))

    def delete_raw_session(self, uuid: str) -> bool:
        self.check_connection()

        try:
            query = 'DELETE FROM raw_session WHERE uuid = ?'
            cursor = self._conn.cursor()
            cursor.execute(query, (uuid,))
            self._conn.commit()
        except sqlite3.Error as e:
            print(f'[-] sqlite3 "delete_raw_session" error [{e}]')
            return False

        return True

    def load_raw_session(self, uuid: str) -> None:
        self.check_connection()

        try:
            query = 'SELECT * FROM raw_session WHERE uuid = ?'
            cursor = self._conn.cursor()
            cursor.execute(query, (uuid,))
            self._conn.commit()

            result = cursor.fetchone()
            if result is None:
                return None

            uuid = result[0]
            calendar = json.loads(result[1])['CALENDAR']
            labels = json.loads(result[2])['LABELS']
            settings = json.loads(result[3])['SETTINGS']
            headset = list()

            for channel in result[4:]:
                if channel is not None:
                    channel_json = json.loads(channel)
                    headset_eeg_data = list(channel_json.values())
                    headset.append(headset_eeg_data[3:])

            raw_session = RawSession(uuid=uuid, calendar=calendar, command_thought=labels, environment=settings,
                                     headset=headset)
            print(raw_session)
            # return raw_session

        except sqlite3.Error as e:
            print(f'[-] sqlite3 "load_raw_session" error [{e}]')
            return None

    def is_session_complete(self, uuid: str, operative_mode: str) -> bool:
        self.check_connection()

        try:
            query = 'SELECT * FROM raw_session WHERE uuid = ?'
            cursor = self._conn.cursor()
            cursor.execute(query, (uuid,))
            self._conn.commit()

            result = cursor.fetchone()
            column_names = [description[0] for description in cursor.description]
            res = dict(zip(column_names, result))
            print(res)

            if operative_mode == 'development':
                for column_name in res.keys():
                    if res.get(column_name) is None:
                        print(str(column_name) + ' - ' + str(res.get(column_name)))
                        return False

            else:
                for column_name in res.keys():
                    if res.get(column_name) is None and column_name != 'LABELS':
                        print(str(column_name) + ' - ' + str(res.get(column_name)))
                        return False

            return True

        except sqlite3.Error as e:
            print(f'[-] sqlite3 "is_session_complete" error [{e}]')
            return False
