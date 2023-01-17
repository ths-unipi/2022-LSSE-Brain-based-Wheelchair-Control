import os
import json
from jsonschema import validate, ValidationError
from src.json_io import JsonIO
from src.prepared_session_collector import PreparedSessionCollector
from src.balance_bar_chart_report_generator import BalanceBarChartReportGenerator
from src.radar_diagram_quality_report_generator import RadarDiagramQualityReportGenerator
from src.learning_session_set_splitter import LearningSessionSetSplitter


class SegregationSystem:

    _instance = None

    def __init__(self):
        self.segregation_system_config = None

    @staticmethod
    def get_instance():
        if SegregationSystem._instance is None:
            SegregationSystem._instance = SegregationSystem()
        return SegregationSystem._instance

    def _import_config(self):
        config_path = os.path.join(os.path.abspath('..'), 'data', 'segregation_system_config.json')
        schema_path = os.path.join(os.path.abspath('..'), 'data', 'segregation_system_config_schema.json')

        try:
            with open(config_path) as file:
                segregation_system_config = json.load(file)

            with open(schema_path) as file:
                segregation_system_config_schema = json.load(file)

            validate(segregation_system_config, segregation_system_config_schema)

        except FileNotFoundError:
            print(f'Failed to open segregation_system_config.json')
            exit(1)

        except ValidationError:
            print('Config validation failed')
            exit(1)

        self.segregation_system_config = segregation_system_config

    def _save_config(self):
        config_path = os.path.join(os.path.abspath('..'), 'data', 'segregation_system_config.json')
        with open(config_path, "w") as file:
            json.dump(self.segregation_system_config, file, indent=4)

    def run(self):
        self._import_config()
        collector = PreparedSessionCollector(self.segregation_system_config)
        collector.segregation_system_config = self.segregation_system_config

        while True:
            op_mode = self.segregation_system_config['operative_mode']

            print(f"Mode: {op_mode}")
            
            # --------------- COLLECTING OP MODE -------------------

            if op_mode == 'collecting_op_mode':
                # if the queue is empty the thread is blocked
                received_json = JsonIO.get_instance().get_received_json()

                print(f"Received Json: {received_json}")

                if collector.store_prepared_session(received_json):
                    collector.increment_prepared_session_counter()
                else:
                    continue

                if collector.check_collecting_threshold() is False:
                    continue

                self.segregation_system_config['operative_mode'] = 'balancing_op_mode'
                self._save_config()
                continue

            # ---------------- BALANCING OP MODE -----------------------

            elif op_mode == 'balancing_op_mode':

                dataset = collector.load_learning_session_set()
                if dataset is None:
                    print("Load database error")
                    continue

                b_generator = BalanceBarChartReportGenerator()
                info = b_generator.generate_balance_bar_chart(dataset)
                b_generator.generate_balancing_report(info)

                self.segregation_system_config['operative_mode'] = 'quality_op_mode'
                self._save_config()
                exit(0)

            # ---------------- QUALITY OP MODE -----------------------

            elif op_mode == 'quality_op_mode':

                b_generator = BalanceBarChartReportGenerator()
                if b_generator.check_balancing_evaluation_from_report() is True:
                    pass
                else:
                    exit(1)

                dataset = collector.load_learning_session_set()
                if dataset is None:
                    print("Load database error")
                    continue

                q_generator = RadarDiagramQualityReportGenerator()
                info = q_generator.generate_radar_diagram(dataset)
                q_generator.generate_quality_report(info)

                self.segregation_system_config['operative_mode'] = 'splitting_op_mode'
                self._save_config()
                exit(0)

            # ---------------- SPLITTING OP MODE -----------------------

            elif op_mode == 'splitting_op_mode':
                splitter = LearningSessionSetSplitter(self.segregation_system_config)
                dataset = collector.load_learning_session_set()
                splitted_dataset = splitter.generate_training_validation_testing_set(dataset)
                print(splitted_dataset)

                # JsonIO.send(self.segregation_system_config['port'], self.segregation_system_config['ip'], splitted_dataset)

                self.segregation_system_config['operative_mode'] = 'collecting_op_mode'
                self.segregation_system_config['user_id'] += 1
                self._save_config()

            else:
                print('Invalid operative mode')
                exit(1)


