import json
import os
import random
from datetime import datetime
import time


class AccuracyReportGenerator:

    def __init__(self):
        pass

    def generate_accuracy_report(self, labels, max_errors_tolerated, testing_mode):
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


        #compute accuracy
        _accuracy = ((_evaluated_labels - _errors) / _evaluated_labels)

        #create accuracy report
        accuracy_report = {
            'evaluated_labels' : _evaluated_labels,
            'max_errors_tolerated' : max_errors_tolerated,
            'errors' : _errors,
            'accuracy' : _accuracy,
            'classifier_accepted' : ""
        }

        # -------------- TESTING MODE --------------#
        if testing_mode:
            expected_accuracy = random.uniform(0.1, 1)
            print("[+] AccuracyReportGenerator - Testing Mode, Expected Accuracy: ", expected_accuracy)
            if accuracy_report['accuracy'] >= expected_accuracy:
                accuracy_report['classifier_accepted'] = "Yes"
            else:
                accuracy_report['classifier_accepted'] = "No"

        #get the current time (for the json name)
        date_time = datetime.fromtimestamp(time.time())
        date_time_string = date_time.strftime("%d-%m-%Y_%H-%M") + '.json'

        # save report as a Json file
        json_path = os.path.join(os.path.abspath('..'), 'data', 'accuracy_report' + str(date_time_string))
        with open(json_path, "w") as f:
            json.dump(accuracy_report, f, indent=4)
        print('[+] AccuracyReportGenerator - Accuracy Report exported')

        return accuracy_report

