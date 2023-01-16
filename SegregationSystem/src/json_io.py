from flask import Flask
from requests import post


class JsonIO:

    instance = None

    def __init__(self):
        self._app = Flask(__name__)

    @staticmethod
    def get_instance():
        if JsonIO.instance is None:
            JsonIO.instance = JsonIO()
        return JsonIO.instance

    def listener(self, ip, port):
        self._app.run(host=ip, port=port, debug=True)

    def get_app(self):
        return self._app

    def receive(self, received_json):
        print(f'Received JSON : {received_json}')
        return received_json

    def send(self, port, ip, data):
        connection_string = f'http://{ip}:{port}/json'
        response = post(connection_string, json=data)

        if response.status_code != 200:
            error_message = response.json()['error']
            print(f'[-] Error: {error_message}')
            return False

        return True