import json
import os
from jsonschema import validate, ValidationError


class EarlyTrainingReportGenerator:

    def __init__(self) -> None:
        self.json_path = os.path.join(os.path.abspath('..'), 'data', 'early_trainin_report.json')

    def generate_report(self, training_parameter: dict, training_error: float) -> None:
        # create the model
        early_training_report = {
            'number_of_generations':  training_parameter['number_of_generations'],
            'hidden_layer_sizes': training_parameter['hidden_layer_sizes'],
            'training_error': training_error,
            'valid_generations': None
        }

        # save the report in a JSON file
        with open(self.json_path, "w") as f:
            json.dump(early_training_report, f, indent=4)
        print('[+] Early Training Report exported')

    def evaluate_report(self) -> bool:
        # open report and schema
        with open(os.path.join(os.path.abspath('..'), 'resources', 'early_training_report_schema.json')) as f:
            report_schema = json.load(f)
        with open(self.json_path) as f:
            report = json.load(f)

        # validate the schema
        try:
            validate(report, report_schema)
        except ValidationError:
            print('[-] Early Training Report validation failed')
            exit(1)

        if report['valid_generations'] is None:
            print('[-] valid_generations parameter can\'t be None')
            exit(1)

        return report['valid_generations']
