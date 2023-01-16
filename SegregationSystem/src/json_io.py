from flask import Flask
from requests import post
import queue


class JsonIO:

    _instance = None

    def __init__(self):
        self._app = Flask(__name__)
        self._received_json_queue = queue.Queue()

    @staticmethod
    def get_instance():
        if JsonIO._instance is None:
            JsonIO._instance = JsonIO()
        return JsonIO._instance

    def listener(self, ip, port):
        self._app.run(host=ip, port=port, debug=True)

    def get_app(self):
        return self._app

    def get_received_json(self):
        return self._received_json_queue.get()

    def receive(self, received_json):
        # if the queue is full the thread is blocked
        try:
            self._received_json_queue.put(received_json, timeout=5)
        except queue.Full:
            print("Full queue exception")

    def send(self, port, ip, data):
        connection_string = f'http://{ip}:{port}/json'
        response = post(connection_string, json=data)

        if response.status_code != 200:
            error_message = response.json()['error']
            print(f'[-] Error: {error_message}')
            return False

        return True