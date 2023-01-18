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
        self.top_five_classifiers.append({'uuid': new_classifier.get_uuid(), 'validation_error': validation_error})
        self.top_five_classifiers = sorted(self.top_five_classifiers, key=lambda x: x["validation_error"], reverse=True)

        if len(self.top_five_classifiers) > 5:

            # if the new classifier is one of the top five remove from list and disk the sixth
            if self.top_five_classifiers[5]['uuid'] != new_classifier.get_uuid():
                # save classifier to disk
                new_classifier.store()

                # remove the sexth from disk
                try:
                    uuid_to_remove = self.top_five_classifiers[5]['uuid']
                    os.remove(os.path.join(os.path.abspath('..'), 'data', f'{uuid_to_remove}.sav'))
                except FileNotFoundError:
                    print('[-] Serialized Classifier not found')
                    exit(1)

                # remove the sixth from the list
                self.top_five_classifiers = self.top_five_classifiers[:5]

            # if the new classifier isn't one of the top five remove it from list
            else:
                self.top_five_classifiers = self.top_five_classifiers[:5]

        else:
            # save classifier to disk
            new_classifier.store()

        # debug
        deh = []
        for classifier in self.top_five_classifiers:
            deh.append(classifier)
        print(deh)

    def get_top_classifiers(self, number_of_generations: int, validation_error_threshold: float) -> dict:
        # structure of the report
        top_five_classifiers = {
            'number_of_generations': number_of_generations,
            'validation_error_threshold': validation_error_threshold,
            'classifiers': []
        }

        # iterate the top five classifier
        for classifier in self.top_five_classifiers:
            # reload the classifier from disk
            classifier_name = f'{classifier["uuid"]}.sav'
            mental_command_classifier = MentalCommandClassifier(file_name=classifier_name)

            # insert the classifier in the report
            info_classifier = {
                'uuid': classifier["uuid"],
                'hidden_layer_sizes': mental_command_classifier.get_hidden_layer_sizes(),
                'training_error': mental_command_classifier.get_error(self.dataset['training_data'],
                                                                      self.dataset['training_labels']),
                'validation_error': classifier['validation_error'],
                'actual_best': False
            }
            top_five_classifiers['classifiers'].append(info_classifier)

        return top_five_classifiers
