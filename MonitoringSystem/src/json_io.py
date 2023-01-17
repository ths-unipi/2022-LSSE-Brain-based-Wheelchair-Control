from flask import Flask, send_file
from requests import post,get
import queue


#to test receive method
connection_string = f'http://10.102.25.52:5000' + '/'

class JsonIO:

    _json_io_instance = None

    @staticmethod
    def get_instance():
        if JsonIO._json_io_instance is None:
            JsonIO._json_io_instance = JsonIO()
        return JsonIO._json_io_instance


    def __init__(self):
        self._app = Flask(__name__)
        self.queue = queue.Queue()

    def listener(self, ip, port):
        self._app.run(host=ip, port=port, debug=False)

    def get_app(self):
        return self._app


    def receive(self, received_json):
        self.queue.put(received_json, block=True)

    def get_queue(self):
        return self.queue

    #to test the receive() method
    def send(self, json_to_send):
        response = post(connection_string + 'json', json=json_to_send)
        if response.status_code != 200:
            return False

        return True