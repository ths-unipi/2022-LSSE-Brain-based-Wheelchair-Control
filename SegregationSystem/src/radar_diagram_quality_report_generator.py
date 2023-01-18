import pandas as pd
import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go
import os
import json
from jsonschema import validate, ValidationError


class RadarDiagramQualityReportGenerator:

    def __init__(self):
        pass

    def _save_radar_diagram(self, data, band, labels, title, file_name):

        '''
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
        '''
        fig = go.Figure()
        for session in data:
            fig.add_trace(go.Scatterpolar(
                    r=session['features'][band],
                    theta=labels,
                    fill='toself',
                    name=f"uuid: {session['uuid']} ",
            ))

        fig.update_layout(showlegend=False, title=title)
        pio.write_image(fig, os.path.join(os.path.abspath('..'), 'data', 'quality', file_name))



    def generate_radar_diagram(self, dataset):

        '''
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

        info = dict()
        info['alpha'] = alpha
        info['beta'] = beta
        info['delta'] = delta
        info['theta'] = theta
        '''

        channels = len(dataset[0]['features']['alpha'])
        labels = [f'ch{i + 1}' for i in range(channels)]

        self._save_radar_diagram(dataset, 'alpha', labels, 'Alpha Radar Diagram', 'alpha_radar_diagram.png')
        self._save_radar_diagram(dataset, 'beta', labels, 'Beta Radar Diagram', 'beta_radar_diagram.png')
        self._save_radar_diagram(dataset, 'delta', labels, 'Delta Radar Diagram', 'delta_radar_diagram.png')
        self._save_radar_diagram(dataset, 'theta', labels, 'Theta Radar Diagram', 'theta_radar_diagram.png')

        info = dict()
        info['alpha'] = []
        info['beta'] = []
        info['delta'] = []
        info['theta'] = []

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