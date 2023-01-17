import numpy as np
import os
import json
from jsonschema import validate, ValidationError
import matplotlib.pyplot as plt


class BalanceBarChartReportGenerator:

    def __init__(self):
        pass

    def generate_balance_bar_chart(self, dataset):

        labels = ['move', 'left', 'right', 'stop']
        values = [0, 0, 0, 0]

        for p_session in dataset:
            ct = p_session['command_thought']
            index = None
            if ct == 'move':
                index = 0
            elif ct == 'left':
                index = 1
            elif ct == 'right':
                index = 2
            elif ct == 'stop':
                index = 3

            values[index] += 1

        plt.bar(labels, values, width=0.4, align='center')
        plt.xlabel('Command Thoughts')
        plt.ylabel('Number of Occurrences')
        plt.title(f'Histogram of Command Thoughts')
        plt.grid(True)

        info = dict()
        info['move'] = values[0]
        info['left'] = values[1]
        info['right'] = values[2]
        info['stop'] = values[3]

        chart_path = os.path.join(os.path.abspath('..'), 'data', 'balancing', 'balance_bar_chart.png')
        plt.savefig(chart_path)
        return info

    def generate_balancing_report(self, info, testing_mode):

        if testing_mode:
            info['evaluation'] = 'balanced'
        else:
            info['evaluation'] = ''
        report_path = os.path.join(os.path.abspath('..'), 'data', 'balancing', 'balancing_report.json')
        with open(report_path, "w") as file:
            json.dump(info, file, indent=4)

    def check_balancing_evaluation_from_report(self):

        report_path = os.path.join(os.path.abspath('..'), 'data', 'balancing', 'balancing_report.json')
        schema_path = os.path.join(os.path.abspath('..'), 'schemas', 'balancing_report_schema.json')

        try:
            with open(report_path) as file:
                report = json.load(file)

            with open(schema_path) as file:
                report_schema = json.load(file)

            validate(report, report_schema)

        except FileNotFoundError:
            print(f'Failed to open balancing_report.json')
            return False

        except ValidationError:
            print('Balancing Report has invalid schema')
            return False

        evaluation = report['evaluation']

        if evaluation == 'not balanced':
            print("Dataset not balanced")
            return False
        elif evaluation == 'balanced':
            print("Dataset balanced")
            return True