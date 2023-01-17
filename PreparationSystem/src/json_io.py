import queue
from threading import Thread

from flask import Flask, request
from requests import post


class JsonIO:
    json_io_instance = None

    def __init__(self):
        self.app = Flask(__name__)
        self._received_json_queue = queue.Queue()

    def listener(self, ip, port):
        self.app.run(host=ip, port=port, debug=False)

    def get_received_json(self):
        return self._received_json_queue.get(block=True)

    # -------- SERVER HANDLER --------

    def receive_json(self, received_json):
        # if the queue is full the thread is blocked
        try:
            self._received_json_queue.put(received_json, timeout=5)
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

    @staticmethod
    def get_instance():
        if JsonIO.json_io_instance is None:
            JsonIO.json_io_instance = JsonIO()
        return JsonIO.json_io_instance


app = JsonIO.get_instance().app


@app.post('/json')
def post_json():
    if request.json is None:
        return {'error': 'No JSON received'}, 500

    received_json = request.json

    new_thread = Thread(target=JsonIO.get_instance().receive_json, args=(received_json,))
    new_thread.start()

    return {}, 200
