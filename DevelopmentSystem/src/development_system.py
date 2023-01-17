import json
import os.path
from threading import Thread
from jsonschema import validate, ValidationError

from src.early_training_controller import EarlyTrainingController
from src.json_io import JsonIO


class DevelopmentSystem:

    def __init__(self) -> None:
        # open config and schema
        with open(os.path.join(os.path.abspath('..'), 'resources', 'development_system_config_schema.json')) as f:
            config_schema = json.load(f)
        with open(os.path.join(os.path.abspath('..'), 'development_system_config.json')) as f:
            self.config = json.load(f)

        # validate the schema
        try:
            validate(self.config, config_schema)
        except ValidationError:
            print('[-] Config validation failed')
            exit(1)

        self.mental_command_classifier = None

    def run(self):
        print('[+] Development System thread started')

        # start the rest server in a new thread as daemon
        run_thread = Thread(target=JsonIO.get_instance().listen, args=('0.0.0.0', 5000))
        run_thread.setDaemon(True)
        run_thread.start()

        # main cycle
        while True:
            # ====================== Receive dataset ======================

            if self.config['operational_mode'] == 'waiting_for_dataset':
                # get new received learning set
                learning_session_set = JsonIO.get_instance().get_queue().get(block=True)

                # save to database and change operational mode
                # TODO: database
                self.change_operational_mode('early_training')

            # ====================== Early training =======================

            if self.config['operational_mode'] == 'early_training':
                # TODO: get dataset from database if not loaded
                training_dataset = {
                    'training_data': [[2, 3, 4, 5], [6, 7, 8, 9], [2, 3, 4, 5], [10, 13, 14, 15]],
                    'training_labels': [1, 2, 1, 3]
                }

                # start the early training controller
                EarlyTrainingController(mental_command_classifier=self.mental_command_classifier,
                                        number_of_generations=self.config['initial_number_of_generations'],
                                        number_of_hidden_layers_range=self.config['number_of_hidden_layers_range'],
                                        number_of_hidden_neurons_range=self.config['number_of_hidden_neurons_range'])\
                    .run(self.config['operational_mode'], training_dataset)

                # change operational mode and stop
                self.change_operational_mode('check_early_training_report')
                break

            # ====================== Early training Report Evaluation ======================

            if self.config['operational_mode'] == 'check_early_training_report':
                # the Early Training Controller will return the ML Engineer evaluation
                report_evaluation = EarlyTrainingController().run(self.config['operational_mode'])
                if report_evaluation is True:
                    self.change_operational_mode('grid_search')
                    print('[+] The Number of Generations is good, Early Training ended')
                else:
                    self.change_operational_mode('early_training')
                    print('[+] The Number of Generations has changed, restart from Early Training')

            # ====================== Grid search =======================

            if self.config['operational_mode'] == 'grid_search':
                break

        # close all threads
        exit(0)

    def change_operational_mode(self, new_mode: str):
        self.config['operational_mode'] = new_mode

        # save the new version of config
        with open(os.path.join(os.path.abspath('..'), 'development_system_config.json'), "w") as f:
            json.dump(self.config, f, indent=4)

        print(f'[+] Switch to \'{new_mode}\' operational mode')
