import os
import json
import pickle


class MentalCommandClassifier:

    def __init__(self):
        self._prepared_session = None
        self._mental_command_classifier = None

    def deploy_classifier(self, json_file: dict):
        if json_file is None:
            print('No classifier received')
            return False

        received_json_path = \
            os.path.join(os.path.abspath('..'), 'data', 'mental_command_classifier.json')
        try:
            with open(received_json_path, 'w') as f:
                json.dump(json_file, f)
        except IOError:
            print("Failed to load classifier on the .json file")
            exit(1)

        return True

    def execute_classifier(self, classifier):
        mlp_classifier = pickle.loads(classifier['classifier'].encode('ISO-8859-1'))
        # the final label from the classifier is generated
        session = [self._prepared_session['features']]
        return mlp_classifier.predict(session)
