import os
import json
from jsonschema import validate, ValidationError
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
    segregation_system_config = import_config()
    segregation_system = SegregationSystem()
    segregation_system.segregation_system_config = segregation_system_config

    new_thread = Thread(target=segregation_system.run, args=(received_json,))
    new_thread.start()

    return {}, 200


def import_config():

    config_path = os.path.join(os.path.abspath('..'), 'segregation_system_config.json')
    schema_path = os.path.join(os.path.abspath('..'), 'segregation_system_config_schema.json')

    try:
        with open(config_path) as file:
            segregation_system_config = json.load(file)

        with open(schema_path) as file:
            segregation_system_config_schema = json.load(file)

        validate(segregation_system_config, segregation_system_config_schema)

    except FileNotFoundError:
        print(f'Failed to open segregation_system_config.json')
        return None

    except ValidationError:
        print('Config validation failed')
        return None

    return segregation_system_config


if __name__ == '__main__':
    JsonIO.get_instance().listener("0.0.0.0", "5000")

