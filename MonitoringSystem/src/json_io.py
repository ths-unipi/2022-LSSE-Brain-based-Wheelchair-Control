from flask import Flask, send_file
from requests import post,get



#to test receive method
connection_string = f'http://127.0.0.1:5000/'

class JsonIO:

    _json_io_instance = None

    @staticmethod
    def get_instance():
        if JsonIO._json_io_instance is None:
            JsonIO._json_io_instance = JsonIO()
        return JsonIO._json_io_instance


    def __init__(self):
        self._app = Flask(__name__)

    def listener(self, ip, port):
        self._app.run(host=ip, port=port, debug=True)

    def get_app(self):
        return self._app

    def receive(self, json_received):
        print(f'Received JSON : {json_received}')


    #to test the receive method
    def send(self, json_to_send):
        response = post(connection_string + 'json', json=json_to_send)

        if response.status_code != 200:
            return False

        return True