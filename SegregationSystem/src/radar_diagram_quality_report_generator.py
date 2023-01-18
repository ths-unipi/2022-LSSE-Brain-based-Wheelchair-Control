import plotly.io as pio
import plotly.graph_objects as go
import os
import json
from jsonschema import validate, ValidationError
import random


class RadarDiagramQualityReportGenerator:

    def __init__(self):
        pass


    def generate_radar_diagram(self, dataset):

        channels = len(dataset[0]['features']['alpha'])
        labels = [f'ch{i + 1}' for i in range(channels)]
        bands = ['alpha', 'beta', 'delta', 'theta']
        titles = ['Alpha Radar Diagram', 'Beta Radar Diagram', 'Delta Radar Diagram', 'Theta Radar Diagram']
        file_names = [ 'alpha_radar_diagram.png', 'beta_radar_diagram.png', 'delta_radar_diagram.png', 'theta_radar_diagram.png']

        i = 0
        for _ in bands:
            band = bands[i]
            title = titles[i]
            file_name = file_names[i]
            fig = go.Figure()
            for session in dataset:
                fig.add_trace(go.Scatterpolar(
                    r=session['features'][band],
                    theta=labels,
                    fill='toself',
                    name=f"uuid: {session['uuid']} ",
                ))

            fig.update_layout(showlegend=False, title=title)
            try:
                pio.write_image(fig, os.path.join(os.path.abspath('..'), 'data', 'quality', file_name))
            except:
                print(f'[-] Failure to save {file_name}')
                return False
            print(f'[+] {title} generated')
            i += 1

        return True

    def generate_quality_report(self, testing_mode):

        info = dict()
        if testing_mode:
            if random.randint(1, 5) == 1:
                info['evaluation'] = 'bad quality'
            else:
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