from src.monitoring_system import MonitoringSystem
from src.json_io import JsonIO

from requests import post,get
from flask import Flask, request
from threading import Thread

app = JsonIO().get_instance().get_app()

@app.post('/json')
def post_json():
    if request.json is None:
        return {'error': 'No JSON received'}, 500

    received_json = request.json

    new_thread = Thread(target= JsonIO.get_instance().receive, args=(received_json,))
    new_thread.start()

    new_thread = Thread(target=MonitoringSystem.get_instance().run(), args=(received_json))
    new_thread.start()

    return {}, 200




if __name__ == '__main__':

    # start the listener
    JsonIO.get_instance().listener("0.0.0.0", "5000")
