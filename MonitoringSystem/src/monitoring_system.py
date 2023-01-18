import json
import os

from jsonschema import validate, ValidationError
from threading import Thread

from src.json_io import JsonIO
from src.labels_store import LabelsStore


MONITORING_SYSTEM_CONFIG_PATH = os.path.join(os.path.abspath('..'), 'monitoring_system_config.json')
MONITORING_SYSTEM_CONFIG_SCHEMA_PATH = os.path.join(os.path.abspath('..'), 'resources', 'monitoring_system_config_schema.json')
SESSION_LABEL_SCHEMA = os.path.join(os.path.abspath('..'), 'resources', 'session_label_schema.json')


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
            print("[-] File not found")

        except ValidationError:
            print('[-] Config validation failed')
            exit(1)




    def run(self) -> None:
        print("[+] Starting Monitoring System \n")

        new_thread = Thread(target=JsonIO.get_instance().listener, args=("0.0.0.0","5000"), daemon=True)
        new_thread.start()

        #monitoring system operations
        while True:
            _labels_store = LabelsStore()
            #---------------- RECEIVE LABELS (EXECUTION AND EXPERT) ----------------#
            session_label = JsonIO.get_instance().get_queue().get(block=True, timeout=None)
            print("[+]MonitoringSystem - Received label :", session_label)
            with open(SESSION_LABEL_SCHEMA) as f:
                _label_schema = json.load(f)
            validate(session_label, _label_schema)


            #---------------------- STORE LABEL ----------------------#
            _labels_store.store_session_label(session_label)



            #----------------- CHECK LABELS THRESHOLD -----------------#
            #si devono controllare sia quelle dell'execution che quelle dell'esperto,
            #se una delle due non supera la soglia non si può creare il report
            _labels_threshold = self._monitoring_system_config['labels_threshold']
            print("[+]MonitoringSystem - labels threshold: ", _labels_threshold)


                #-------------- GENERATE ACCURACY REPORT --------------#
                # ------------------ LOAD ALL LABELS ------------------#
            labels = _labels_store.load_labels()



            # -------------- TESTING MODE --------------#


