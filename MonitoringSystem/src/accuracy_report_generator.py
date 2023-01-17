import json
import os
from jsonschema import validate, ValidationError


class AccuracyReportGenerator:

    def __init__(self):
        self.accuracy_report_path = os.path.abspath('..','data','accuracy_report.json')

    def generate_accuracy_report(self):
        pass


