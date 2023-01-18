import pandas as pd
import plotly.express as px
import plotly.io as pio
import os
import json
from jsonschema import validate, ValidationError


class RadarDiagramQualityReportGenerator:

    def __init__(self):
        pass

    def _save_radar_diagram(self, data, labels, title, file_name):

        df = pd.DataFrame(dict(r=data, theta=labels))
        fig = px.line_polar(df, r='r', theta='theta', line_close=True, title=title)
        fig.update_traces(fill='toself')
        try:
            pio.write_image(fig, os.path.join(os.path.abspath('..'), 'data', 'quality', file_name))
        except:
            print(f'[-] Failure to save {file_name}')
            return False

        print(f'[+] {title} generated')
        return True

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

        self._save_radar_diagram(alpha, labels, 'Alpha Radar Diagram', 'alpha_radar_diagram.png')
        self._save_radar_diagram(beta, labels, 'Beta Radar Diagram', 'beta_radar_diagram.png')
        self._save_radar_diagram(delta, labels, 'Delta Radar Diagram', 'delta_radar_diagram.png')
        self._save_radar_diagram(theta, labels, 'Theta Radar Diagram', 'theta_radar_diagram.png')
        '''
        alpha_df = pd.DataFrame(dict(r=alpha, theta=labels))
        fig = px.line_polar(alpha_df, r='r', theta='theta', line_close=True, title="Alpha Radar Diagram")
        fig.update_traces(fill='toself')
        pio.write_image(fig, os.path.join(os.path.abspath('..'), 'data', 'quality', 'alpha_radar_diagram.png'))

        beta_df = pd.DataFrame(dict(r=beta, theta=labels))
        fig = px.line_polar(beta_df, r='r', theta='theta', line_close=True, title="Beta Radar Diagram")
        fig.update_traces(fill='toself')
        pio.write_image(fig, os.path.join(os.path.abspath('..'), 'data', 'quality', 'beta_radar_diagram.png'))

        delta_df = pd.DataFrame(dict(r=delta, theta=labels))
        fig = px.line_polar(delta_df, r='r', theta='theta', line_close=True, title="Delta Radar Diagram")
        fig.update_traces(fill='toself')
        pio.write_image(fig, os.path.join(os.path.abspath('..'), 'data', 'quality', 'delta_radar_diagram.png'))

        theta_df = pd.DataFrame(dict(r=theta, theta=labels))
        fig = px.line_polar(theta_df, r='r', theta='theta', line_close=True, title="Theta Radar Diagram")
        fig.update_traces(fill='toself')
        pio.write_image(fig, os.path.join(os.path.abspath('..'), 'data', 'quality', 'theta_radar_diagram.png'))
        '''

        info = dict()
        info['alpha'] = alpha
        info['beta'] = beta
        info['delta'] = delta
        info['theta'] = theta

        return info

    def generate_quality_report(self, info, testing_mode):

        if testing_mode:
            info['evaluation'] = 'good quality'
        else:
            info['evaluation'] = ''
        report_path = os.path.join(os.path.abspath('..'), 'data', 'quality', 'quality_report.json')
        try:
            with open(report_path, "w") as file:
                json.dump(info, file, indent=4)
        except:
            print("[-] Failure to save quality_report.json")
            return False
        return True

    def check_quality_evaluation_from_report(self):

        report_path = os.path.join(os.path.abspath('..'), 'data', 'quality', 'quality_report.json')
        schema_path = os.path.join(os.path.abspath('..'), 'schemas', 'quality_report_schema.json')

        try:
            with open(report_path) as file:
                report = json.load(file)

            with open(schema_path) as file:
                report_schema = json.load(file)

            validate(report, report_schema)

        except FileNotFoundError:
            print(f'[-] Failure to open quality_report.json')
            return False

        except ValidationError:
            print('[-] Quality Report has invalid schema')
            return False

        evaluation = report['evaluation']

        if evaluation == 'bad quality':
            print("[-] Quality evaluation: Dataset bad quality")
            return False
        elif evaluation == 'good quality':
            print("[+] Quality evaluation: Dataset good quality")
            return True
        else:
            print("[!] Quality evaluation non done")
            return False