import json
import os
from jsonschema import validate, ValidationError


class AccuracyReportGenerator:

    def __init__(self):
        self.json_path = os.path.join(os.path.abspath('..'), 'data', 'accuracy_report.json')

    def generate_accuracy_report(self, labels, max_errors_tolerated, testing_mode, expected_accuracy):
        #compute evaluated labels
        _evaluated_labels = len(labels)
        _errors = 0
        _accuracy = None
        _classifier_accepted = None

        #compute errors
        for row in labels:

            _label1 = row['label1']
            _label2 = row['label2']
            if _label1 != _label2:
                _errors += 1
                print(f"uuid:{row['uuid']}, label1:{row['label1']}, label2:{row['label2']}\n")


        #compute accuracy
        _accuracy = ((_evaluated_labels - _errors) / _evaluated_labels)
        print("ACCURACY : ", _accuracy)

        #create accuracy report
        accuracy_report = {
            'evaluated_labels' : _evaluated_labels,
            'max_errors_tolerated' : max_errors_tolerated,
            'errors' : _errors,
            'accuracy' : _accuracy,
            'classifier_accepted' : None
        }

        # -------------- TESTING MODE --------------#
        if testing_mode:
            if accuracy_report['accuracy'] >= expected_accuracy:
                accuracy_report['classifier_accepted'] = True
            else:
                accuracy_report['classifier_accepted'] = False

        #save report as a Json file
        with open(self.json_path, "w") as f:
            json.dump(accuracy_report, f, indent=4)
        print('[+] AccuracyReportGenerator - Accuracy Report exported')

        return accuracy_report

