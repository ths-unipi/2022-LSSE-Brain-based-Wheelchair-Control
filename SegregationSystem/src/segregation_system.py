import os
import json
from jsonschema import validate, ValidationError
from src.json_io import JsonIO
from src.prepared_session_collector import PreparedSessionCollector
from src.balance_bar_chart_report_generator import BalanceBarChartReportGenerator
from src.radar_diagram_quality_report_generator import RadarDiagramQualityReportGenerator
from src.learning_session_set_splitter import LearningSessionSetSplitter
from threading import Thread


class SegregationSystem:

    def __init__(self):
        self.segregation_system_config = None

    def _import_config(self):
        config_path = os.path.join(os.path.abspath('..'), 'data', 'segregation_system_config.json')
        schema_path = os.path.join(os.path.abspath('..'), 'schemas', 'segregation_system_config_schema.json')

        try:
            with open(config_path) as file:
                segregation_system_config = json.load(file)

            with open(schema_path) as file:
                segregation_system_config_schema = json.load(file)

            validate(segregation_system_config, segregation_system_config_schema)

        except FileNotFoundError:
            print(f'[-] Failed to open segregation_system_config.json')
            print('[!] Shutdown')
            exit(1)

        except ValidationError:
            print('[-] Config validation failed')
            print('[!] Shutdown')
            exit(1)

        self.segregation_system_config = segregation_system_config

    def _save_config(self):
        config_path = os.path.join(os.path.abspath('..'), 'data', 'segregation_system_config.json')
        try:
            with open(config_path, "w") as file:
                json.dump(self.segregation_system_config, file, indent=4)
        except:
            print('[-] Failure to save segregation_system_config.json')
            return False
        return True

    def run(self):

        listener = Thread(target=JsonIO.get_instance().listener, args=("0.0.0.0", "5000"))
        listener.setDaemon(True)
        listener.start()

        self._import_config()
        collector = PreparedSessionCollector(self.segregation_system_config)
        collector.segregation_system_config = self.segregation_system_config
        collector.retrive_counter()

        while True:
            op_mode = self.segregation_system_config['operative_mode']
            testing_mode = self.segregation_system_config['testing_mode']

            print(f"[!] Mode: {op_mode}")
            print(f"[!] Testing mode: {testing_mode}")

            # --------------- COLLECTING OP MODE -------------------

            if op_mode == 'collecting_op_mode':
                # if the queue is empty the thread is blocked
                received_json = JsonIO.get_instance().get_received_json()

                print(f"[+] Received Json: {received_json}")

                if collector.store_prepared_session(received_json):
                    collector.increment_prepared_session_counter()
                else:
                    continue

                if not collector.check_collecting_threshold():
                    continue

                self.segregation_system_config['operative_mode'] = 'balancing_op_mode'
                self._save_config()
                continue

            # ---------------- BALANCING OP MODE -----------------------

            elif op_mode == 'balancing_op_mode':

                dataset = collector.load_learning_session_set()
                if dataset is None:
                    print("[-] Load database error")
                    continue

                b_generator = BalanceBarChartReportGenerator()
                info = b_generator.generate_balance_bar_chart(dataset)
                b_generator.generate_balancing_report(info, testing_mode)

                self.segregation_system_config['operative_mode'] = 'quality_op_mode'
                self._save_config()

                if not self.segregation_system_config['testing_mode']:
                    print('[!] Shutdown')
                    exit(0)
                else:
                    continue

            # ---------------- QUALITY OP MODE -----------------------

            elif op_mode == 'quality_op_mode':

                b_generator = BalanceBarChartReportGenerator()
                if b_generator.check_balancing_evaluation_from_report():
                    pass
                else:
                    self.segregation_system_config['operative_mode'] = 'collecting_op_mode'
                    self.segregation_system_config['user_id'] += 1
                    self._save_config()
                    continue

                dataset = collector.load_learning_session_set()
                if dataset is None:
                    print("[-] Load database error")
                    continue

                q_generator = RadarDiagramQualityReportGenerator()
                q_generator.generate_radar_diagram(dataset)
                q_generator.generate_quality_report(testing_mode)

                self.segregation_system_config['operative_mode'] = 'splitting_op_mode'
                self._save_config()

                if not self.segregation_system_config['testing_mode']:
                    print('[!] Shutdown')
                    exit(0)
                else:
                    continue

            # ---------------- SPLITTING OP MODE -----------------------

            elif op_mode == 'splitting_op_mode':

                q_generator = RadarDiagramQualityReportGenerator()
                if q_generator.check_quality_evaluation_from_report():
                    pass
                else:
                    self.segregation_system_config['operative_mode'] = 'collecting_op_mode'
                    self.segregation_system_config['user_id'] += 1
                    self._save_config()
                    continue

                splitter = LearningSessionSetSplitter(self.segregation_system_config)
                dataset = collector.load_learning_session_set()
                splitted_dataset = splitter.generate_training_validation_testing_set(dataset)
                print(splitted_dataset)

                ip = self.segregation_system_config['endpoint_ip']
                port = self.segregation_system_config['endpoint_port']

                if not JsonIO.get_instance().send(ip, port, splitted_dataset):
                    print('[!] Shutdown')
                    exit(1)

                self.segregation_system_config['operative_mode'] = 'collecting_op_mode'
                self.segregation_system_config['user_id'] += 1
                self._save_config()
                collector.retrive_counter()

            else:
                print('[-] Invalid operative mode')
                print('[!] Shutdown')
                exit(1)



