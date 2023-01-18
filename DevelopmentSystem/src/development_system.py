import json
import os.path
from threading import Thread
from jsonschema import validate, ValidationError
from sklearn.datasets import make_classification  # TODO: toglilo

from src.early_training_controller import EarlyTrainingController
from src.json_io import JsonIO
from src.mental_command_classifier import MentalCommandClassifier
from src.validation_controller import ValidationController


class DevelopmentSystem:

    def __init__(self) -> None:
        # open config and schema
        with open(os.path.join(os.path.abspath('..'), 'resources', 'development_system_config_schema.json')) as f:
            config_schema = json.load(f)
        with open(os.path.join(os.path.abspath('..'), 'development_system_config.json')) as f:
            self.config = json.load(f)

        # validate the config
        try:
            validate(self.config, config_schema)
        except ValidationError:
            print('[-] Config validation failed')
            exit(1)

        self.mental_command_classifier = None

    def run(self):
        print(f'[+] Development System started on main thread in \'{self.config["operational_mode"]}\' mode')

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

                # create JSON file containing the number of generations
                with open(os.path.join(os.path.abspath('..'), 'data', 'number_of_generations.json'), "w") as f:
                    json.dump({'number_of_generations': self.config['initial_number_of_generations']}, f, indent=4)

                # save to database and change operational mode
                # TODO: database
                self.change_operational_mode('early_training')

            # ====================== Early training =======================

            if self.config['operational_mode'] == 'early_training':
                # TODO: get dataset from database if not loaded
                x, y = make_classification(n_features=(22 * 4), n_redundant=0)
                training_dataset = {'training_data': x, 'training_labels': y}

                # start the early training controller
                EarlyTrainingController(mental_command_classifier=self.mental_command_classifier,
                                        number_of_hidden_layers_range=self.config['number_of_hidden_layers_range'],
                                        number_of_hidden_neurons_range=self.config['number_of_hidden_neurons_range']) \
                    .run(self.config['operational_mode'], training_dataset)

                # change operational mode and stop
                self.change_operational_mode('check_early_training_report')
                break

            # ====================== Early training Report Evaluation ======================

            if self.config['operational_mode'] == 'check_early_training_report':
                # the early training controller will return the ML Engineer evaluation
                report_evaluation = EarlyTrainingController().run(self.config['operational_mode'])
                if report_evaluation is True:
                    print('[+] The Number of Generations is good, Early Training ended')
                    self.change_operational_mode('grid_search')
                else:
                    print('[+] The Number of Generations has changed, restart from Early Training')
                    self.change_operational_mode('early_training')

            # ====================== Grid search =======================

            if self.config['operational_mode'] == 'grid_search':
                # TODO: get dataset from database if not loaded
                x, y = make_classification(n_features=(22 * 4), n_redundant=0)
                z, n = make_classification(n_features=(22 * 4), n_redundant=0)
                dataset = {
                    'training_data': x,
                    'training_labels': y,
                    'validation_data': z,
                    'validation_labels': n
                }

                # start the validation contoller
                ValidationController(mental_command_classifier=self.mental_command_classifier,
                                     number_of_hidden_layers_range=self.config['number_of_hidden_layers_range'],
                                     number_of_hidden_neurons_range=self.config['number_of_hidden_neurons_range']) \
                    .run(self.config['operational_mode'], dataset, self.config['validation_error_threshold'])

                # change operational mode and stop
                self.change_operational_mode('check_top_five_classifiers_report')
                break

            # ====================== Top Five Classifiers Report Evaluation ======================

            if self.config['operational_mode'] == 'check_top_five_classifiers_report':
                # the validation controller will return the uuid of the best classifier (-1 if there isn't)
                best_classifier_uuid = ValidationController().run(self.config['operational_mode'])
                if best_classifier_uuid == -1:
                    print('[+] No valid Best Classifier found, restart from Early Training with new Number of '
                          'Generations')
                    self.change_operational_mode('early_training')
                else:
                    print(f'[+] Best Classifier found with UUID:({best_classifier_uuid}), Validation Phase ended')
                    self.change_operational_mode('test_best_classifier')

                    # load from disk the best classifier
                    print(f'Loading: \'{best_classifier_uuid}.sav\'')
                    self.mental_command_classifier = MentalCommandClassifier(file_name=f'{best_classifier_uuid}.sav')

            # ====================== Test Best Classifier =======================

            if self.config['operational_mode'] == 'test_best_classifier':
                print(f'Test phase for classifier {self.mental_command_classifier.get_uuid()}')
                break

        # close all threads
        exit(0)

    def change_operational_mode(self, new_mode: str):
        self.config['operational_mode'] = new_mode

        # save the new version of config
        with open(os.path.join(os.path.abspath('..'), 'development_system_config.json'), "w") as f:
            json.dump(self.config, f, indent=4)

        print(f'[+] Switch to \'{new_mode}\' operational mode')
