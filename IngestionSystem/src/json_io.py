from typing import Any

from flask import Flask, request
from threading import Thread
from requests import post
import queue


class JsonIO:
    """
        JsonIO class
    """

    instance = None

    def __init__(self):
        self.app = Flask(__name__)
        self.received_records_queue = queue.Queue()

    @staticmethod
    def get_instance() -> Any:
        if JsonIO.instance is None:
            JsonIO.instance = JsonIO()
        return JsonIO.instance

    def listen(self, ip: str, port: int) -> None:
        self.app.run(host=ip, port=port, debug=False)

    def get_app(self) -> Any:
        return self.app

    def get_received_record(self) -> Any:
        return self.received_records_queue.get(block=True)

    def receive(self, received_record) -> bool:
        try:
            self.received_records_queue.put(received_record, timeout=10)
        except queue.Full:
            print('Full queue exception')
            return False
        return True

    def send(self, endpoint_ip: str, endpoint_port: int, raw_session: dict) -> bool:
        connection_string = f'http://{endpoint_ip}:{endpoint_port}/json'
        response = post(connection_string, json=raw_session)

        if response.status_code != 200:
            error_message = response.json()['error']
            print(f'[-] Error: {error_message}')
            return False
        return True


app = JsonIO.get_instance().get_app()


@app.post('/record')
def post_json():
    if request.json is None:
        return {'error': 'No record received'}, 500

    received_record = request.json
    new_thread = Thread(target=JsonIO.get_instance().receive, args=(received_record, ))
    new_thread.start()

    return {}, 200
