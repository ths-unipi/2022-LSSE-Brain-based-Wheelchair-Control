import logging
from typing import Any

from flask import Flask, request
from threading import Thread
from requests import post
import queue


class JsonIO:
    """
    This class implements the methods for receiving records and sending the raw sessions to the Preparation System.
    """

    instance = None

    def __init__(self):
        """
        Initializes the JsonIO object
        """
        self.app = Flask(__name__)
        self.received_records_queue = queue.Queue()

    @staticmethod
    def get_instance() -> Any:
        """
        :return: instance of the JsonIO class
        """
        if JsonIO.instance is None:
            JsonIO.instance = JsonIO()
        return JsonIO.instance

    def get_app(self) -> Any:
        """
        :return: instance of the app Flask
        """
        return self.app

    def get_received_record(self, received_record: dict) -> bool:
        """
        Receives a record and enqueues it in a thread-safe queue
        :param received_record: record sent from a data source (calendar, labels, settings, headset_eeg_data)
        :return: True if the record is entered correctly. False if the insertion fails.
        """
        try:
            self.received_records_queue.put(received_record, timeout=None)
            if 300 < self.received_records_queue.qsize() < 350:
                print(f'[!] Record queue size: {self.received_records_queue.qsize()}')
        except queue.Full:
            print('Full queue exception')
            return False
        return True

    def receive(self) -> Any:
        """
        Extracts a record from the queue containing all the received records
        :return: record
        """
        return self.received_records_queue.get(block=True)

    def send(self, endpoint_ip: str, endpoint_port: int, data: dict) -> bool:
        """
        Sends data to the Preparation System
        :param endpoint_ip: IP of the Preparation System
        :param endpoint_port: Port of the Preparation System
        :param data: dictionary containing the data to send
        :return: True if the 'send' is successful. False otherwise.
        """
        connection_string = f'http://{endpoint_ip}:{endpoint_port}/json'
        response = post(connection_string, json=data)

        if response.status_code != 200:
            error_message = response.json()['error']
            print(f'[-] Error: {error_message}')
            return False
        return True

    def listen(self, ip: str, port: int) -> None:
        """
        Runs the application server
        :param ip: IP of the local server
        :param port: Port of the local server
        :return: None
        """
        self.app.run(host=ip, port=port, debug=False)


app = JsonIO.get_instance().get_app()
log = logging.getLogger('werkzeug')
log.disabled = True


@app.post('/record')
def post_json():
    """
    Flask view function that handles requests related to records sent from the different data sources
    """
    if request.json is None:
        return {'error': 'No record received'}, 500

    received_record = request.json
    new_thread = Thread(target=JsonIO.get_instance().get_received_record, args=(received_record, ))
    new_thread.start()

    return {}, 200
