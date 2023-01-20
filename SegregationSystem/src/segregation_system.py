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

        # start the listening server that will receive json messages
        listener = Thread(target=JsonIO.get_instance().listener, args=("0.0.0.0", "5000"))
        listener.setDaemon(True)
        listener.start()

        # import the configuration and initialize the PreparedSessionCollector
        self._import_config()
        collector = PreparedSessionCollector(self.segregation_system_config)
        collector.segregation_system_config = self.segregation_system_config
        collector.retrieve_counter()

        # set the testing mode
        testing_mode = self.segregation_system_config['testing_mode']
        print(f"[!] Testing mode: {testing_mode}")

        while True:
            op_mode = self.segregation_system_config['operative_mode']

            print(f"[!] Mode: {op_mode}")

            # --------------- COLLECTING OP MODE -------------------

            if op_mode == 'collecting_op_mode':

                received_json = JsonIO.get_instance().receive()

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
                # the bar chart info to build the report
                b_generator.generate_balancing_report(info, testing_mode)

                self.segregation_system_config['operative_mode'] = 'quality_op_mode'
                self._save_config()

                # if the system is in the testing mode, it must not shut down it because the humen evaluation
                # has been simulated
                if not self.segregation_system_config['testing_mode']:
                    print('[!] Shutdown')
                    exit(0)
                else:
                    continue

            # ---------------- QUALITY OP MODE -----------------------

            elif op_mode == 'quality_op_mode':

                b_generator = BalanceBarChartReportGenerator()
                res = b_generator.check_balancing_evaluation_from_report()
                if res == 0:
                    # if the balance bar chart was evaluated with 'balanced', it's possible continue with
                    # the actual dataset
                    pass
                elif res == -1:
                    # if the balance bar chart was evaluated with 'not balanced', the dataset is not usable, so
                    # it's possible continue collecting new data and build a new dataset (new user_id)
                    self.segregation_system_config['operative_mode'] = 'collecting_op_mode'
                    if not testing_mode:
                        self.segregation_system_config['user_id'] += 1
                    self._save_config()
                    collector.retrieve_counter()
                    continue
                else:
                    # if the balance bar char evaluation hasn't been done yet, the system shuts down because the human
                    # has to make it
                    print('[!] Shutdown')
                    exit(0)

                dataset = collector.load_learning_session_set()
                if dataset is None:
                    print("[-] Load database error")
                    continue

                q_generator = RadarDiagramQualityReportGenerator()
                q_generator.generate_radar_diagram(dataset)
                q_generator.generate_quality_report(testing_mode)

                self.segregation_system_config['operative_mode'] = 'splitting_op_mode'
                self._save_config()

                # if the system is in the testing mode, it must not shut down it because the humen evaluation
                # has been simulated
                if not self.segregation_system_config['testing_mode']:
                    print('[!] Shutdown')
                    exit(0)
                else:
                    continue

            # ---------------- SPLITTING OP MODE -----------------------

            elif op_mode == 'splitting_op_mode':

                q_generator = RadarDiagramQualityReportGenerator()
                res = q_generator.check_quality_evaluation_from_report()
                if res == 0:
                    # if the radar diagram was evaluated with 'good quality', it's possible continue with
                    # the actual dataset
                    pass
                elif res == -1:
                    # if the radar diagram was evaluated with 'bad quality', the dataset is not usable, so
                    # it's possible continue collecting new data and build a new dataset (new user_id)
                    self.segregation_system_config['operative_mode'] = 'collecting_op_mode'
                    if not testing_mode:
                        self.segregation_system_config['user_id'] += 1
                    self._save_config()
                    collector.retrieve_counter()
                    continue
                else:
                    # if the radar diagram evaluation hasn't been done yet, the system shuts down because the human
                    # has to make it
                    print('[!] Shutdown')
                    exit(0)

                splitter = LearningSessionSetSplitter(self.segregation_system_config)
                dataset = collector.load_learning_session_set()
                splitted_dataset = splitter.generate_training_validation_testing_set(dataset)
                print(splitted_dataset)

                ip = self.segregation_system_config['endpoint_ip']
                port = self.segregation_system_config['endpoint_port']

                JsonIO.get_instance().send(ip, port, splitted_dataset)

                # the dataset is evaluated and sent, so it's possible continue collecting new data
                # and build a new dataset (new user_id)
                self.segregation_system_config['operative_mode'] = 'collecting_op_mode'
                if not testing_mode:
                    self.segregation_system_config['user_id'] += 1
                self._save_config()
                collector.retrieve_counter()

            else:
                print('[-] Invalid operative mode')
                print('[!] Shutdown')
                exit(1)



