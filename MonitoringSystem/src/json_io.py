from flask import Flask, request
from requests import post,get
from threading import Thread

import queue


#to data receive method
connection_string = 'http://192.168.178.22:5000' + '/'

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

    def get_app(self) -> Flask:
        return self._app


    def receive(self, received_json) -> None:
        self.queue.put(received_json, block=True)

    def get_queue(self) -> queue:
        return self.queue

    #to data the receive() method
    def send(self, json_to_send):
        response = post(connection_string + 'json', json=json_to_send)
        if response.status_code != 200:
            return False

        return True



app = JsonIO().get_instance().get_app()

@app.post('/json')
def post_json():
    if request.json is None:
        return {'error': 'No JSON received'}, 500

    received_json = request.json

    new_thread = Thread(target= JsonIO.get_instance().receive, args=(received_json,))
    new_thread.start()

    return {}, 200