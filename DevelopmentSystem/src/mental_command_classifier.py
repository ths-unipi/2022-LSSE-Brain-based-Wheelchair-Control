import os.path
import string
import joblib
from pandas import DataFrame
from sklearn.neural_network import MLPClassifier


class MentalCommandClassifier:

    def __init__(self, uuid: int, training_parameters: dict) -> None:
        self.uuid = uuid
        self.classifier = MLPClassifier(max_iter=training_parameters['number_of_generations'],
                                        hidden_layer_sizes=training_parameters['hidden_layer_size'])

    def __int__(self, file_name: string) -> None:
        self.uuid = int(file_name.split('.')[0])        # get uuid from the file name (es. 1.sav)
        self.classifier = joblib.load(file_name)
        # parameters = self.classifier.get_params()     # TODO: valuta se rimuovere
        # self.training_parameter = TrainingParameter(parameters['max_iter'], parameters['hidden_layer_sizes'])

    def train_classifier(self, training_data: DataFrame, training_labels: DataFrame) -> None:
        self.classifier.fit(training_data, training_labels)

    def get_error(self, data: DataFrame, label: DataFrame) -> float:
        return self.classifier.score(data, label)

    def get_losses(self) -> list:
        return self.classifier.loss_curve_

    def load(self, file_name: string) -> None:
        self.uuid = int(file_name.split('.')[0])        # get uuid from the file name (es. 1.sav)
        self.classifier = joblib.load(file_name)

    def store(self) -> None:
        file_path = os.path.join(os.path.abspath('..'), 'data', f'{self.uuid}.sav')
        joblib.dump(self.classifier, file_path)

    def rebuild(self, training_parameters: dict, uuid=None) -> None:
        if uuid is None:
            self.uuid += 1                              # autoincrement useful during the grid search
        else:
            self.uuid = uuid
        self.classifier = MLPClassifier(max_iter=training_parameters['number_of_generations'],
                                        hidden_layer_sizes=training_parameters['hidden_layer_size'])
