import os
import sqlite3


class LearningSessionStore:

    def __init__(self) -> None:
        self._store_path = os.path.join(os.path.abspath('..'), 'data', 'learning_session_store.db')
        self._conn = None

        if self.open_connection() and self.create_table():
            print('[+] connection to DB established and \'learning_session\' table initialized')
        else:
            print('[-] failed to initialize learning session store')
            exit(1)

    def open_connection(self) -> bool:
        try:
            self._conn = sqlite3.connect(self._store_path)
        except sqlite3.Error:
            print(f'[-] failed to open connection to DB')
            return False

        return True

    def close_connection(self) -> bool:
        try:
            self._conn.close()
        except sqlite3.Error:
            print(f'[-] failed to close connection to DB')
            return False

        return True

    def check_connection(self) -> bool:
        return self._conn is not None

    def create_table(self) -> bool:
        if self.check_connection() is False:
            return False

        # generate all column names
        channels = ['ALPHA', 'BETA', 'DELTA', 'THETA']
        column_names = []
        for channel in channels:
            for i in range(22):
                column_names.append(f'{channel}_{i}')
        column_names.append('ENVIRONMENT')
        column_names.append('LABEL')

        try:
            # create the base of the query
            query = '(UUID TEXT PRIMARY KEY UNIQUE'
            for column_name in column_names:
                query += ', ' + column_name + ' INTEGER'
            query += ');'

            # create the three tables
            for table_name in ['training_set', 'validation_set', 'test_set']:
                query = 'CREATE TABLE ' + table_name + query
                print(query)
                self._conn.cursor().execute(query)
                self._conn.commit()

        except sqlite3.Error:
            print('[-] failed to create table')
            return False

        return True

    def insert_dataset(self, dataset: list, dataset_name: str) -> bool:
        try:
            query = 'INSERT INTO ' + dataset_name + ' VALUES (?' + (',?' * (22 * 4 + 2)) + ')'
            cursor = self._conn.cursor()
            cursor.executemany(query, dataset)
            self._conn.commit()
        except sqlite3.Error as e:
            print(f'[-] failed to insert dataset')
            return False

        return True

    def store_dataset(self):
        pass

    def delete_dataset(self):
        pass

    def get_training_set(self):
        pass

    def get_validation_set(self):
        pass

    def get_test_set(self):
        pass
