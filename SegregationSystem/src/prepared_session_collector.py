import sqlite3
import os
import json
from jsonschema import validate, ValidationError


class PreparedSessionCollector:

    def __init__(self, config):
        self.segregation_system_config = config
        self._prepared_session_counter = 0
        self._conn = None

    def _open_connection(self):
        db_name = self.segregation_system_config['db_name']
        db_path = os.path.join(os.path.abspath('..'), 'data', db_name)
        if not os.path.exists(db_path):
            print("[-] Sqlite db doesn't exist, the db will be created")
            return False
        try:
            self._conn = sqlite3.connect(db_path)
        except sqlite3.Error as e:
            print(f'[-] Sqlite Connection Error [{e}]')
            return False

        return True

    def _close_connection(self):
        if self._conn is None:
            return True
        try:
            self._conn.close()
            self._conn = None
        except sqlite3.Error as e:
            print(f"[-] Close Connection Error [{e}]")
            return False

        return True

    def _validate_prepared_session(self, p_session):

        schema_path = os.path.join(os.path.abspath('..'), 'schemas', 'p_session_schema.json')
        try:

            with open(schema_path) as file:
                p_session_schema = json.load(file)

            validate(p_session, p_session_schema)

        except FileNotFoundError:
            print(f'[-] Failure to open p_session_schema.json')
            return False

        except ValidationError:
            print('[-] Prepared Session validation failed')
            return False

        return True

    def retrive_counter(self):

        if not self._open_connection():
            return None

        user_id = self.segregation_system_config['user_id']

        query = "SELECT session_id FROM p_session WHERE user_id = ? ORDER BY session_id DESC LIMIT 1"
        cursor = self._conn.cursor()
        try:
            cursor.execute(query, (user_id,))
        except sqlite3.Error as e:
            print(f'[-] Sqlite Execution Error [{e}]')
            return None

        res = cursor.fetchone()  # fetchall for more results
        if res is None:
            self._prepared_session_counter = 0
        else:
            self._prepared_session_counter = res[0] + 1

    def increment_prepared_session_counter(self):
        self._prepared_session_counter += 1

    def check_collecting_threshold(self):

        threshold = self.segregation_system_config['collecting_threshold']
        if self._prepared_session_counter > threshold:
            self._prepared_session_counter = 0
            return True
        else:
            return False

    def load_learning_session_set(self):
        user_id = self.segregation_system_config['user_id']

        if not self._open_connection():
            return None

        query = "SELECT * FROM p_session WHERE user_id = ? "
        cursor = self._conn.cursor()
        try:
            cursor.execute(query, (user_id,))
        except sqlite3.Error as e:
            print(f'[-] Sqlite Execution Error [{e}]')
            return None

        res = cursor.fetchall()  # fetchall for more results
        if res is None:
            return None
        dataset = []
        for p_session in res:
            dataset.append(json.loads(p_session[2]))
        return dataset

    def store_prepared_session(self, p_session):

        if not self._validate_prepared_session(p_session):
            print("[-] Invalid data")
            return False

        user_id = self.segregation_system_config['user_id']
        session_id = self._prepared_session_counter

        if not self._open_connection():
            return False

        query = "INSERT INTO p_session (user_id, session_id, json) \
                        VALUES(?, ?, ?) "
        cursor = self._conn.cursor()

        try:
            cursor.execute(query, (user_id, session_id, json.dumps(p_session)))
            self._conn.commit()
        except sqlite3.Error as e:
            print(f"[-] Sqlite Execution Error [{e}]")
            self._close_connection()
            return False

        print(f"[+] Stored new prepared session (user_id: {user_id} session_id: {session_id})")
        self._close_connection()
        return True
