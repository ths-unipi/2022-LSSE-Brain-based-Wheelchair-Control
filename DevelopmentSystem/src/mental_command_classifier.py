import os.path
import joblib
from pandas import DataFrame
from sklearn.neural_network import MLPClassifier


class MentalCommandClassifier:

    def __init__(self, uuid: int = 0, training_parameters: dict = None, file_name: str = None) -> None:
        # if file_name isn't given create it
        if file_name is None:
            self.uuid = uuid
            if training_parameters is None:
                self.classifier = None
            else:
                self.classifier = MLPClassifier(max_iter=training_parameters['number_of_generations'],
                                                hidden_layer_sizes=training_parameters['hidden_layer_sizes'])

        # file_name is given load it from disk
        else:
            self.load(file_name)

    def train_classifier(self, training_data: DataFrame, training_labels: DataFrame) -> None:
        self.classifier.fit(training_data, training_labels)

    def get_error(self, data: DataFrame, label: DataFrame) -> float:
        return self.classifier.score(data, label)

    def get_losses(self) -> list:
        return self.classifier.loss_curve_

    def get_uuid(self) -> int:
        return self.uuid

    def get_hidden_layer_sizes(self) -> list:
        return list(self.classifier.get_params()['hidden_layer_sizes'])

    def load(self, file_name: str) -> None:
        self.uuid = int(file_name.split('.')[0])        # get uuid from the file name (es. 1.sav)
        file_path = os.path.join(os.path.abspath('..'), 'data', file_name)
        self.classifier = joblib.load(file_path)

    def store(self) -> None:
        file_path = os.path.join(os.path.abspath('..'), 'data', f'{self.uuid}.sav')
        joblib.dump(self.classifier, file_path)

    def rebuild(self, training_parameters: dict, uuid: int = None) -> None:
        if uuid is None:
            self.uuid += 1                              # autoincrement useful during the grid search
        else:
            self.uuid = uuid
        self.classifier = MLPClassifier(training_parameters)
