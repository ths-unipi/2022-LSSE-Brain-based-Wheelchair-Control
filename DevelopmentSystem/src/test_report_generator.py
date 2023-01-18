import json
import os
from jsonschema import validate, ValidationError


class TestReportGenerator:

    def __init__(self) -> None:
        self._json_path = os.path.join(os.path.abspath('..'), 'data', 'test_best_classifier_report.json')

    def generate_report(self, training_parameter: dict, errors: dict, test_error_threshold: float) -> None:
        # create the model
        test_report = {
            'number_of_generations':  training_parameter['number_of_generations'],
            'hidden_layer_sizes': training_parameter['hidden_layer_sizes'],
            'test_error_threshold': test_error_threshold,
            'training_error': errors['training_error'],
            'test_error': errors['test_error'],
            'valid_classifier': None
        }

        # save the report in a JSON file
        with open(self._json_path, "w") as f:
            json.dump(test_report, f, indent=4)
        print('[+] Test Best Classifier Report exported')

    def evaluate_report(self) -> bool:
        # open report and schema
        with open(os.path.join(os.path.abspath('..'), 'resources', 'test_best_classifier_report_schema.json')) as f:
            report_schema = json.load(f)
        with open(self._json_path) as f:
            report = json.load(f)

        # validate the schema
        try:
            validate(report, report_schema)
        except ValidationError:
            print('[-] Test Best Classifier Report validation failed')
            exit(1)

        if report['valid_classifier'] is None:
            print('[-] valid_classifier parameter can\'t be None')
            exit(1)

        return report['valid_classifier']
