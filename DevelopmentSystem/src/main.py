from threading import Thread
from flask import request

from src.development_system import DevelopmentSystem
from src.json_io import JsonIO

app = JsonIO.get_instance().app


@app.post('/dataset')
def handle_post_dataset() -> None:
    if request.json is None:
        return {'error': 'No JSON received'}, 500

    received_json = request.json

    # a new thread will analyze the received JSON, the actual one will respond to Segregation System
    receive_thread = Thread(target=JsonIO.get_instance().receive, args=(received_json,))
    receive_thread.start()

    return {}, 200


if __name__ == '__main__':
    development_system = DevelopmentSystem()
    development_system.open_server()
    run_thread = Thread(target=development_system.run)
    run_thread.start()
