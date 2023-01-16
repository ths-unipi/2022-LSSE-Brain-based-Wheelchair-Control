from src.json_io import JsonIO
from src.prepared_session_collector import PreparedSessionCollector
from src.balance_bar_chart_report_generator import BalanceBarChartReportGenerator
from src.radar_diagram_quality_report_generator import RadarDiagramQualityReportGenerator

class SegregationSystem:

    instance = None

    def __init__(self):
        self.segregation_system_config = None

    @staticmethod
    def get_instance():
        if SegregationSystem.instance is None:
            SegregationSystem.instance = SegregationSystem()
        return SegregationSystem.instance

    def run(self):
        if self.segregation_system_config is None:
            print("Configuration Error")
            exit(1)

        while True:
            op_mode = self.segregation_system_config['operative_mode']
            if op_mode == 'collecting_op_mode':
                # if the queue is empty the thread is blocked
                received_json = JsonIO.get_instance().get_received_json()
                print(f"Received Json (SG): {received_json}")
            elif op_mode == 'balancing_op_mode':
                pass
            elif op_mode == 'quality_op_mode':
                pass
            else:
                print('Invalid operative mode')
                exit(1)



