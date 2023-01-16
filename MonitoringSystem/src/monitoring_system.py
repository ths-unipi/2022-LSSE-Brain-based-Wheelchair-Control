import json
import os
from jsonschema import validate, ValidationError

from src.json_io import JsonIO


class MonitoringSystem:
    _monitoring_system_instance = None

    @staticmethod
    def get_instance():
        if MonitoringSystem._monitoring_system_instance is None:
            MonitoringSystem._monitoring_system_instance = MonitoringSystem()
        return MonitoringSystem._monitoring_system_instance

    def __init__(self):
        try:
            with open("../monitoring_system_config.json", 'r') as f:
                self._monitoring_system_config = json.load(f)
                print(self._monitoring_system_config)

            with open("schema/monitoring_system_config_schema.json") as f:
                _config_schema = json.load(f)

            validate(self._monitoring_system_config,_config_schema)

        except FileNotFoundError:
            print("File not found")

        except ValidationError:
            print('Config validation failed')
            exit(1)



    def run(self,received_json):
        _labels_threshold = self._monitoring_system_config['labels_threshold']
        print("labels threshold: " , _labels_threshold)



