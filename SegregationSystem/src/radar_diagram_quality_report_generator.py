import pandas as pd
import plotly.express as px
import plotly.io as pio
import os
import json
from jsonschema import validate, ValidationError


class RadarDiagramQualityReportGenerator:

    def __init__(self):
        pass

    def generate_radar_diagram(self, dataset):

        channels = len(dataset[0]['features']['alpha'])
        alpha = [0 for _ in range(channels)]
        beta = [0 for _ in range(channels)]
        delta = [0 for _ in range(channels)]
        theta = [0 for _ in range(channels)]
        labels = [f'ch{i+1}' for i in range(channels)]

        for p_session in dataset:
            features = p_session['features']
            i = 0
            while i < channels:
                alpha[i] += features['alpha'][i]
                beta[i] += features['beta'][i]
                delta[i] += features['delta'][i]
                theta[i] += features['theta'][i]
                i += 1

        i = 0
        while i < channels:
            alpha[i] = alpha[i] / len(dataset)
            beta[i] = beta[i] / len(dataset)
            delta[i] = delta[i] / len(dataset)
            theta[i] = theta[i] / len(dataset)
            i += 1

        alpha_df = pd.DataFrame(dict(r=alpha, theta=labels))
        fig = px.line_polar(alpha_df, r='r', theta='theta', line_close=True, title="Alpha Radar Diagram")
        fig.update_traces(fill='toself')
        pio.write_image(fig, os.path.join(os.path.abspath('..'), 'data', 'alpha_radar_diagram.png'))

        beta_df = pd.DataFrame(dict(r=beta, theta=labels))
        fig = px.line_polar(beta_df, r='r', theta='theta', line_close=True, title="Beta Radar Diagram")
        fig.update_traces(fill='toself')
        pio.write_image(fig, os.path.join(os.path.abspath('..'), 'data', 'beta_radar_diagram.png'))

        delta_df = pd.DataFrame(dict(r=delta, theta=labels))
        fig = px.line_polar(delta_df, r='r', theta='theta', line_close=True, title="Delta Radar Diagram")
        fig.update_traces(fill='toself')
        pio.write_image(fig, os.path.join(os.path.abspath('..'), 'data', 'delta_radar_diagram.png'))

        theta_df = pd.DataFrame(dict(r=theta, theta=labels))
        fig = px.line_polar(theta_df, r='r', theta='theta', line_close=True, title="Theta Radar Diagram")
        fig.update_traces(fill='toself')
        pio.write_image(fig, os.path.join(os.path.abspath('..'), 'data', 'theta_radar_diagram.png'))

        info = dict()
        info['alpha'] = alpha
        info['beta'] = beta
        info['delta'] = delta
        info['theta'] = theta

        return info

    def generate_quality_report(self, info):

        info['evaluation'] = ''
        report_path = os.path.join(os.path.abspath('..'), 'data', 'quality_report.json')
        with open(report_path, "w") as file:
            json.dump(info, file, indent=4)
        pass

    def check_quality_evaluation_from_report(self):

        report_path = os.path.join(os.path.abspath('..'), 'data', 'quality_report.json')
        schema_path = os.path.join(os.path.abspath('..'), 'schemas', 'quality_report_schema.json')

        try:
            with open(report_path) as file:
                report = json.load(file)

            with open(schema_path) as file:
                report_schema = json.load(file)

            validate(report, report_schema)

        except FileNotFoundError:
            print(f'Failed to open quality_report.json')
            return False

        except ValidationError:
            print('Quality Report has invalid schema')
            return False

        evaluation = report['evaluation']

        if evaluation == 'bad quality':
            print("Dataset bad quality")
            return False
        elif evaluation == 'good quality':
            print("Dataset good quality")
            return True