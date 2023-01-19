import os, json

class MonitoringPhase:

    def __init__(self):
        self._session_counter = 0
        self._label = None

    def increment_session_counter(self):
        self._session_counter+1

