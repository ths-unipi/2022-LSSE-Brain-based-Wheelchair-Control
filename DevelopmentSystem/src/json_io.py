import queue
from threading import Thread

from flask import Flask, request
from requests import post


class JsonIO:
    # singleton
    json_io_instance = None

    def __init__(self):
        self.app = Flask(__name__)
        self.queue = queue.Queue()

    def receive(self, learning_session_set: dict) -> None:
        self.queue.put(learning_session_set, block=True)

    def send(self, endpoint: str, classifier: dict) -> bool:
        response = post(endpoint + '/classifier', json=classifier)

        if response.status_code != 200:
            error_message = response.json()['error']
            print(f'[-] Failed to send Classifier\n\t-> Error: {error_message}')
            return False

        print(f'[+] Classifier sent to Execution System')
        return True

    def listen(self, ip, port):
        self.app.run(host=ip, port=port, debug=False)

    def get_app(self) -> Flask:
        return self.app

    def get_queue(self) -> queue:
        return self.queue

    @staticmethod
    def get_instance():
        if JsonIO.json_io_instance is None:
            JsonIO.json_io_instance = JsonIO()
        return JsonIO.json_io_instance


app = JsonIO.get_instance().get_app()


@app.post('/json')
def post_json():
    if request.json is None:
        return {'error': 'No JSON received'}, 500

    received_json = request.json

    receive_thread = Thread(target=JsonIO.get_instance().receive, args=(received_json,))
    receive_thread.start()

    return {}, 200
