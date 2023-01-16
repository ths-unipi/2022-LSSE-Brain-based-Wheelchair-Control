from flask import request
from threading import Thread
from src.json_io import JsonIO
from src.segregation_system import SegregationSystem

app = JsonIO.get_instance().get_app()


@app.post('/json')
def post_json():
    if request.json is None:
        return {'error': 'No JSON received'}, 500

    received_json = request.json
    new_thread = Thread(target=JsonIO.get_instance().receive, args=(received_json,))
    new_thread.start()

    return {}, 200


if __name__ == '__main__':

    segregation_system = Thread(target=SegregationSystem.get_instance().run, args=())
    segregation_system.start()

    JsonIO.get_instance().listener("0.0.0.0", "5000")



