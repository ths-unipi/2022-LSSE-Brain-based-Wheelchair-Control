import os
import warnings
from sklearn.exceptions import ConvergenceWarning, DataConversionWarning
from src.mental_command_classifier import MentalCommandClassifier


class TopFiveClassifierEvaluators:

    def __init__(self, dataset) -> None:
        self.top_five_classifiers = []
        self.dataset = dataset

        # remove the warnings
        warnings.filterwarnings("ignore", category=ConvergenceWarning)
        warnings.filterwarnings("ignore", category=DataConversionWarning)

    def evaluate_new_classifier(self, new_classifier: MentalCommandClassifier) -> bool:
        # compute validation error
        validation_error = new_classifier.get_error(self.dataset['validation_data'], self.dataset['validation_labels'])

        # add new classifier with validation error in the list, orded by descending validation_error
        self.top_five_classifiers.append({'classifier': new_classifier, 'validation_error': validation_error})
        self.top_five_classifiers = sorted(self.top_five_classifiers, key=lambda x: x["validation_error"], reverse=True)

        # the new classifier is one of the top five
        if len(self.top_five_classifiers) > 5 and self.top_five_classifiers[5]['classifier'] != new_classifier:
            # save to disk
            new_classifier.store()

            # remove the sexth from disk
            uuid_to_remove = self.top_five_classifiers[5].get_uuid()
            os.remove(os.path.join(os.path.abspath('..'), 'data', f'{uuid_to_remove}.sav'))

            # remove the sixth from the list
            self.top_five_classifiers = self.top_five_classifiers[:5]
            print(len(self.top_five_classifiers))

    def get_top_classifiers(self, number_of_generations: int, validation_error_threshold: float) -> dict:
        # structure of the report
        top_five_classifiers = {
            'number_of_generations': number_of_generations,
            'validation_error_threshold': validation_error_threshold,
            'classifiers': []
        }

        # iterate the top five classifier
        for classifier in self.top_five_classifiers:
            # insert the classifier in the report
            info_classifier = {
                'uuid': classifier['classifier'].get_uuid(),
                'hidden_layer_sizes': classifier['classifier'].get_hidden_layer_sizes(),
                'training_error': classifier['classifier'].get_error(self.dataset['training_data'],
                                                                     self.dataset['training_labels']),
                'validation_error': classifier['validation_error'],
                'actual_best': False
            }
            top_five_classifiers['classifiers'].append(info_classifier)

        return top_five_classifiers
