import sqlite3
import os
import json
import jsonschema


class PreparedSessionCollector:

    def __init__(self):
        self.segregation_system_config = None
        self.prepared_session_counter = 0

    def increment_prepared_session_counter(self):
        self.prepared_session_counter += 1

    def check_collecting_threshold(self):

        threshold = self.segregation_system_config['collecting_threshold']
        if self.prepared_session_counter > threshold:
            self.prepared_session_counter = 0
            return True
        else:
            return False

    def load_learning_session_set(self):
        pass

    def store_prepared_session(self, psession):
        pass