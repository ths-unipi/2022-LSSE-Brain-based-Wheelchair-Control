import json
import os
from jsonschema import validate, ValidationError

from src.json_io import JsonIO

MONITORING_SYSTEM_CONFIG_PATH = "../monitoring_system_config.json"
MONITORING_SYSTEM_CONFIG_SCHEMA_PATH = "../resources/monitoring_system_config_schema.json"

class MonitoringSystem:
    _monitoring_system_instance = None

    @staticmethod
    def get_instance():
        if MonitoringSystem._monitoring_system_instance is None:
            MonitoringSystem._monitoring_system_instance = MonitoringSystem()
        return MonitoringSystem._monitoring_system_instance

    def __init__(self):
        try:
            with open(MONITORING_SYSTEM_CONFIG_PATH) as f:
                self._monitoring_system_config = json.load(f)

            with open(MONITORING_SYSTEM_CONFIG_SCHEMA_PATH) as f:
                _config_schema = json.load(f)

            validate(self._monitoring_system_config,_config_schema)

        except FileNotFoundError:
            print("File not found")

        except ValidationError:
            print('Config validation failed')
            exit(1)



    def run(self):
        print("**START MONITORING SYSTEM**\n")
        #execute operations

        received_label = JsonIO.get_instance().get_queue().get(block=True, timeout=None)
        print("MonitoringSystem - Received label :", received_label)

        _labels_threshold = self._monitoring_system_config['labels_threshold']
        print("MonitoringSystem - labels threshold: ", _labels_threshold)



