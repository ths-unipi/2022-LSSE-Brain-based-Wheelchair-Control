from flask import Flask, request
from requests import post
from threading import Thread

import queue

class JsonIO:

    _instance = None

    def __init__(self):
        self.app = Flask(__name__)
        self._received_json_queue = queue.Queue()
        self.json_io_instance = JsonIO()

    @staticmethod
    def get_instance():
        if JsonIO._instance is None:
            JsonIO._instance = JsonIO()
        return JsonIO._instance

    def listener(self, ip, port):
        self.app.run(host=ip, port=port, debug=False)

    # -------- SERVER HANDLER --------

    def get_received_json(self):
        return self._received_json_queue.get(block=True)

    def receive(self, received_json):
        # if the queue is full the thread is blocked
        try:
            self._received_json_queue.put(received_json, block=True)
        except queue.Full:
            print("Full queue exception")
    # -------- CLIENT REQUEST --------

    def send_json(self, endpoint_ip, endpoint_port, json_to_send):
        response = post(f'http://{endpoint_ip}:{endpoint_port}/json', json=json_to_send)

        if response.status_code != 200:
            error_message = response.json()['error']
            print(f'[-] Error: {error_message}')
            return False
        return True

app = JsonIO.get_instance().app

@app.post('/json')
def post_json():
    if request.json is None:
        return {'error': 'No JSON received'}, 500

    received_json = request.json

    thread_receive = Thread(target=JsonIO.get_instance().receive, args=(received_json,))
    thread_receive.start()

    return {}, 200