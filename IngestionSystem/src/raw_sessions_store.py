import os
import sqlite3
import json
from jsonschema import validate, ValidationError

DB_NAME = 'RawSessionsStore.db'
RECORD_TYPE = ['CALENDAR', 'LABEL', 'SETTINGS', 'CHANNEL']
NUM_CHANNELS = 22


class RawSessionsStore:
    """
    This class is responsible for handling the database operations.
    """

    def __init__(self) -> None:
        """
        Initializes the Raw Sessions Store
        """
        self._conn = None

        db_path = os.path.join(os.path.abspath('..'), 'data', DB_NAME)
        if os.path.exists(db_path):
            print('[+] sqlite3 previous database deleted')
            os.remove(db_path)

        if self.open_connection() and self.create_table():
            print('[+] sqlite3 connection established and raw_session table initialized')
        else:
            print('[-] sqlite3 initialize failed')
            exit(-1)

    def open_connection(self) -> bool:
        """
        Creates the connection to the database
        :return: True if the connection is successful. False if the connection fails.
        """
        try:
            self._conn = sqlite3.connect(os.path.join(os.path.abspath('..'), 'data', DB_NAME))
            return True
        except sqlite3.Error as e:
            print(f'[-] sqlite3 open connection error [{e}]')

        return False

    def close_connection(self) -> None:
        """
        Closes the connection to the database
        :return: True if the disconnection is successful. False otherwise.
        """
        try:
            self._conn.close()
        except sqlite3.Error as e:
            print(f'[-] sqlite3 close connection error [{e}]')
            exit(-1)

    def check_connection(self) -> None:
        """
        Checks if the connection with the database is established.
        It terminates the system if the connection is not set.
        """
        if self._conn is None:
            print('[-] sqlite3 connection not established')
            exit(-1)

    def create_table(self) -> bool:
        """
        Creates the table used to synchronize records and join them in order to build a Raw Session
        :return: True if the creation is successful. False otherwise.
        """
        self.check_connection()

        try:
            channel_columns = str()
            for i in range(1, NUM_CHANNELS + 1):
                channel_columns += RECORD_TYPE[3] + '_' + str(i) + ' TEXT, '

            query = 'CREATE TABLE IF NOT EXISTS raw_session ( \
                uuid TEXT NOT NULL, \
                ' + RECORD_TYPE[0] + ' TEXT, \
                ' + RECORD_TYPE[1] + ' TEXT, \
                ' + RECORD_TYPE[2] + ' TEXT, \
                ' + channel_columns + \
                    'UNIQUE(uuid), PRIMARY KEY (uuid))'
            self._conn.cursor().execute(query)
            self._conn.commit()
        except sqlite3.Error as e:
            print(f'[-] sqlite3 "create_tables" error [{e}]')
            return False

        return True

    def get_record_type(self, record: dict) -> str:
        """
        Identifies the record type. The possible ones are CALENDAR, LABELS, SETTINGS and CHANNEL.
        :param record: record to identify
        :return: type of the record
        """
        keys = list(record.keys())[0:3]

        for record_type in RECORD_TYPE:
            if record_type in keys:
                return record_type
        return 'None'

    def validate_schema_record(self, record: dict, record_type: str) -> bool:
        """
        Validates a received record given a pre-defined schema
        :param record: dictionary that represents the received record
        :param record_type: type of the record to validate
        :return: True if the validation is successful. False if the validation fails.
        """
        try:
            record_schema_path = os.path.join(os.path.abspath('..'), 'resources', record_type.lower() + '_schema.json')
            with open(record_schema_path) as f:
                loaded_schema = json.load(f)
                validate(record, loaded_schema)

        except ValidationError:
            print('[-] Record schema validation failed')
            return False

        except FileNotFoundError:
            print(f'[-] Failed to open schema path ({record_type})')
            exit(-1)

        return True

    def generate_query_parameters(self, record: dict, record_type: str) -> tuple:

        parameters = {
            'UUID': record['UUID'],
            'CALENDAR': None,
            'LABEL': None,
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

    def row_exists(self, uuid: str) -> bool:
        """

        :param uuid:
        :return:
        """
        try:
            cursor = self._conn.cursor()
            cursor.execute('SELECT COUNT(1) FROM raw_session WHERE uuid = ?', (uuid,))
            self._conn.commit()

            result = cursor.fetchone()
            if result[0] == 0:
                return False

        except sqlite3.Error as e:
            print(f'[-] sqlite3 "row_exists" error [{e}]')
            # TODO: check if this return is correct (it can be ambiguous)
            return False

        return True

    def store_record(self, record: dict) -> bool:
        """
        Stores the received record into the database after its type identification and validation.
        :param record: dictionary representing the received record to store
        :return: True if the store is successful. False if it fails.
        """
        self.check_connection()

        # Get record type in order to save it in the correct column the record
        record_type = self.get_record_type(record)

        # Record validation
        if not self.validate_schema_record(record, record_type):
            print("[-] Record schema not valid (record discarded)")
            return False

        # Check if the record received belongs to a session already in the database or to a new one
        if self.row_exists(record['UUID']):
            # Update
            if record_type == 'CHANNEL':
                column_name = record_type + '_' + str(record['CHANNEL'])
            else:
                column_name = record_type
            query_result = self.update_record(record=record, column_to_set=column_name)
        else:
            # Insert
            query_parameters = self.generate_query_parameters(record=record, record_type=record_type)
            query_result = self.insert_record(parameters=query_parameters)

        return query_result

    def insert_record(self, parameters: tuple) -> bool:
        """
        Inserts a row in the database upon receiving a record belonging to a new session (uuid and last_uuid_received
        are different)
        :param parameters: query parameters in order to set the right column
        :return: True if the insert is successful. False otherwise.
        """
        try:
            query = 'INSERT INTO raw_session (uuid, calendar, label, settings, ' \
                    'channel_1, channel_2, channel_3, channel_4, channel_5, channel_6, channel_7, channel_8, ' \
                    'channel_9, channel_10, channel_11, channel_12, channel_13, channel_14, channel_15, channel_16, ' \
                    'channel_17, channel_18, channel_19, channel_20, channel_21, channel_22 ) ' \
                    'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
            cursor = self._conn.cursor()
            cursor.execute(query, parameters)
            self._conn.commit()
        except sqlite3.Error as e:
            print(f'[-] sqlite3 "insert_record" error [{e}]')
            return False

        return True

    def update_record(self, record: dict, column_to_set: str) -> bool:
        """
        Updates a row in the database upon receiving a record belonging to a session already in the database (uuid and
        last_uuid_received are equal)
        :param record: dictionary representing the received record to store
        :param column_to_set: column to update
        :return: True if the update is successful. False otherwise.
        """
        try:
            query = 'UPDATE raw_session SET ' + column_to_set + ' = ? WHERE uuid = ?'
            cursor = self._conn.cursor()
            cursor.execute(query, (json.dumps(record), record['UUID']))
            self._conn.commit()
        except sqlite3.Error as e:
            print(f'[-] sqlite3 "update_record" error [{e}]')
            return False

        return True

    def load_raw_session(self, uuid: str) -> dict:
        """
        Loads a Raw Session from the data store
        :param uuid: string that represents the primary key of the row to load from the data store
        :return: dictionary representing the loaded Raw Session
        """
        self.check_connection()

        try:
            query = 'SELECT * FROM raw_session WHERE uuid = ?'
            cursor = self._conn.cursor()
            cursor.execute(query, (uuid,))
            self._conn.commit()

            result = cursor.fetchone()
            if result is None:
                return {}

            # Building the loaded Raw Session as a dictionary
            raw_session = {
                'UUID': result[0],
                'calendar': json.loads(result[1])['CALENDAR'],
                'commandThought': None,
                'environment': json.loads(result[3])['SETTINGS'],
                'headset': list()
            }

            # Handling missing label
            if result[2] is not None:
                raw_session['commandThought'] = json.loads(result[2])['LABEL']

            # Handling missing channels eeg data
            for channel in result[4:]:
                if channel is not None:
                    channel_json = json.loads(channel)
                    headset_eeg_data = list(channel_json.values())
                    raw_session['headset'].append(headset_eeg_data[3:])
                else:
                    raw_session['headset'].append([])

            return raw_session
        except sqlite3.Error as e:
            print(f'[-] sqlite3 "load_raw_session" error [{e}]')
            return {}

    def delete_raw_session(self, uuid: str) -> bool:
        """
        Deletes a Raw Session from the data store
        :param uuid: string that represents the primary key of the row to delete form the data store
        :return: True if the 'delete' is successful. False otherwise.
        """
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

    def check_required_fields(self, query_result: dict, operative_mode: str) -> bool:
        """
        Checks if required fields are missing
        """
        if operative_mode == 'development':
            for column_name in query_result.keys():
                if query_result.get(column_name) is None:
                    return False
        else:
            # In execution mode the 'label' is not required
            for column_name in query_result.keys():
                if query_result.get(column_name) is None and column_name != 'LABEL':
                    return False
        return True

    def is_session_complete(self, uuid: str, operative_mode: str, last_missing_sample: bool) -> bool:
        """
        Checks if the synchronization and building of the Raw Session has been completed meaning there are no more
        records related to the session.
        :param last_missing_sample:
        :param uuid: string that identifies the session to check
        :param operative_mode: mode in which the system is working (development or execution)
        :return: True if the session is completed. False otherwise.
        """
        self.check_connection()

        try:
            query = 'SELECT * FROM raw_session WHERE uuid = ?'
            cursor = self._conn.cursor()
            cursor.execute(query, (uuid,))
            self._conn.commit()

            # Fetch raw session from the data store
            result = cursor.fetchone()

            if last_missing_sample:
                # Since last_missing_samples is True it means that there will be no more records related to this session
                # So the task to check if the session is good or not is shifted to the RawSessionIntegrity class
                # Here the only important thing is to check if the required fields are not missing
                column_names = [description[0] for description in cursor.description][0:len(RECORD_TYPE)]
                # res contains only the following (required) fields: ['CALENDAR, 'LABEL', 'SETTINGS']
                res = dict(zip(column_names, result[0:len(RECORD_TYPE)]))
                return self.check_required_fields(query_result=res, operative_mode=operative_mode)
            else:
                # The session is still in the synchronization/building phase,
                # So it is necessary to check all the possible fields (except for the labels during the execution mode)
                # If all the records exist, the session can be labeled as 'fully complete'
                column_names = [description[0] for description in cursor.description]
                # res has all the possible fields: ['CALENDAR, 'LABEL', 'SETTINGS', 'CHANNELS_1', ETC..]
                res = dict(zip(column_names, result))
                return self.check_required_fields(query_result=res, operative_mode=operative_mode)

        except sqlite3.Error as e:
            print(f'[-] sqlite3 "is_session_complete" error [{e}]')
            return False