from flask import Flask
from requests import post

import queue

class JsonIO:

    def __init__(self):
        self.app = Flask(__name__)
        self._received_json_queue = queue.Queue()

    def listener(self, ip, port):
        self.app.run(host=ip, port=port, debug=False)

    # -------- SERVER HANDLER --------

    def get_received_json(self):
        return self._received_json_queue.get()

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