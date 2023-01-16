from threading import Thread
from flask import request

from src.development_system import DevelopmentSystem
from src.json_io import JsonIO

app = JsonIO.get_instance().get_app()


@app.post('/json')
def post_json():
    if request.json is None:
        return {'error': 'No JSON received'}, 500

    received_json = request.json

    receive_thread = Thread(target=JsonIO.get_instance().receive, args=(received_json,))
    receive_thread.start()

    return {}, 200


if __name__ == '__main__':
    # new thread for development system execution
    run_thread = Thread(target=DevelopmentSystem().run, args=())
    run_thread.start()

    # rest server in main thread
    JsonIO.get_instance().listen('0.0.0.0', 5000)
