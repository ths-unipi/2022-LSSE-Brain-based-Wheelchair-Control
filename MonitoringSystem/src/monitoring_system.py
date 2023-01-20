import json
import os

from jsonschema import validate, ValidationError
from threading import Thread

from src.json_io import JsonIO
from src.labels_store import LabelsStore
from src.collecting_phase import CollectingPhase
from src.accuracy_report_generator import AccuracyReportGenerator


MONITORING_SYSTEM_CONFIG_PATH = os.path.join(os.path.abspath('..'), 'monitoring_system_config.json')
ACCURACY_REPORT_PATH = os.path.join(os.path.abspath('..'),'data', 'accuracy_report.json')

ACCURACY_REPORT_SCHEMA = os.path.join(os.path.abspath('..'), 'resources', 'accuracy_report_schema.json')
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

            MonitoringSystem._validate_schema(self, self._monitoring_system_config, MONITORING_SYSTEM_CONFIG_SCHEMA_PATH)

        except FileNotFoundError as err:
            print("[-] File not found: ", err)

    def _validate_schema(self,file_to_validate,schema_path):
        try:
            with open(schema_path) as f:
                _schema = json.load(f)
            validate(file_to_validate, _schema)

        except ValidationError as err:
            print('[-] Config validation failed: ',err)
            exit(1)





    def run(self) -> None:
        print("[+]MonitoringSystem - Starting Monitoring System \n")

        new_thread = Thread(target=JsonIO.get_instance().listener, args=("0.0.0.0","5000"), daemon=True)
        new_thread.start()

        # load labels_threshold from configuration
        _labels_threshold = self._monitoring_system_config['labels_threshold']

        # class objects
        _labels_store = LabelsStore()
        _collecting_phase = CollectingPhase(_labels_threshold)
        _accuracy_report_generator = AccuracyReportGenerator()


        while True:
            #---------------- RECEIVE LABELS (EXECUTION AND EXPERT) ----------------#
            _received_label = JsonIO.get_instance().get_queue().get(block=True, timeout=None)
            print("[+]MonitoringSystem - Received label :", _received_label)
            MonitoringSystem._validate_schema(self, _received_label,SESSION_LABEL_SCHEMA)


            #---------------------- STORE LABEL ----------------------#
            _labels_store.store_session_label(_received_label)


            #----------------- CHECK LABELS THRESHOLD -----------------#
            _increment = _labels_store.row_label_complete(_received_label['uuid'])
            if _increment is True:
                _collecting_phase.increment_counter()
                _increment = False

            #check if the threshold is exceeded, if yes generate the report
            _threshold_exceeded = _collecting_phase.check_labels_thresold()
            if _threshold_exceeded is True:
                #-------------- GENERATE ACCURACY REPORT --------------#
                #load all labels
                _labels = _labels_store.load_labels()

                #metrics used to create the accuracy report
                _max_errors_tolerated = self._monitoring_system_config['max_errors_tolerated']
                _testing_mode = self._monitoring_system_config['testing_mode']

                # create accuracy report
                _accuracy_report = _accuracy_report_generator.generate_accuracy_report(_labels, _max_errors_tolerated, _testing_mode)
                #validate accuracy report created
                MonitoringSystem._validate_schema(self,_accuracy_report, ACCURACY_REPORT_SCHEMA)
                print(f"[+] MonitoringSystem - Accuracy Report Generated, with Accuracy :  {_accuracy_report['accuracy']*100} % \n")


                # -------------- DELETE LABELS --------------#
                _labels_store.delete_labels()
                _collecting_phase.reset_counter()
