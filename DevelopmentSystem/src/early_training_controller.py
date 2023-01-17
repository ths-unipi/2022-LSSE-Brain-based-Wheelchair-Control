import json
import math
import os

from jsonschema import validate, ValidationError

from src.early_trainin_report_generator import EarlyTrainingReportGenerator
from src.gradient_descent_plot_generator import GradientDescentPlotGenerator
from src.mental_command_classifier import MentalCommandClassifier


class EarlyTrainingController:

    def __init__(self, mental_command_classifier: MentalCommandClassifier = None,
                 number_of_hidden_layers_range: list = None, number_of_hidden_neurons_range: list = None) -> None:
        self.mental_command_classifier = mental_command_classifier
        self.number_of_hidden_layers_range = number_of_hidden_layers_range
        self.number_of_hidden_neurons_range = number_of_hidden_neurons_range

    def run(self, operational_mode: str, training_dataset: list = None) -> bool:
        if operational_mode == 'early_training':
            # get the average number of hidden layer
            training_parameters = self.generate_training_parameters()

            # generate the first classifier
            self.mental_command_classifier = MentalCommandClassifier(uuid=0, training_parameters=training_parameters)

            # train the classifier
            self.mental_command_classifier.train_classifier(training_dataset['training_data'],
                                                            training_dataset['training_labels'])
            print('[+] Early Training completed')

            # generate the report
            training_error = self.mental_command_classifier.get_error(
                training_dataset['training_data'], training_dataset['training_labels'])
            EarlyTrainingReportGenerator().generate_report(training_parameters, training_error)

            # generate the gradient descent plot
            GradientDescentPlotGenerator().generate_plot(self.mental_command_classifier.get_losses())

        elif operational_mode == 'check_early_training_report':
            return EarlyTrainingReportGenerator().evaluate_report()

    def generate_training_parameters(self) -> dict:
        # load number of generations file and schema
        with open(os.path.join(os.path.abspath('..'), 'data', 'number_of_generations.json')) as f:
            number_of_generations_file = json.load(f)
        with open(os.path.join(os.path.abspath('..'), 'resources', 'number_of_generations_schema.json')) as f:
            number_of_generations_schema = json.load(f)

        # validate number of generations
        try:
            validate(number_of_generations_file, number_of_generations_schema)
            number_of_generations = number_of_generations_file['number_of_generations']
        except ValidationError:
            print('[-] Number of generations validation failed')
            exit(1)

        # get the average hyperparameters
        average_layers = int((self.number_of_hidden_layers_range[1] + self.number_of_hidden_layers_range[0]) / 2)
        average_neurons = int((self.number_of_hidden_neurons_range[1] + self.number_of_hidden_neurons_range[0]) / 2)

        # get the sizes of hidden layers with descending lorithmic number of neurons
        hidden_layer_sizes = tuple([math.ceil(average_neurons / (2 ** i)) for i in range(average_layers)])
        print(f'[+] The Early Training Network has this hidden layer sizes: {hidden_layer_sizes}')

        return {'number_of_generations': number_of_generations, 'hidden_layer_sizes': hidden_layer_sizes}

    def evaluate_early_training_results(self) -> bool:
        return EarlyTrainingReportGenerator().evaluate_report()
