from src.prepared_session_collector import PreparedSessionCollector
from src.balance_bar_chart_report_generator import BalanceBarChartReportGenerator
from src.radar_diagram_quality_report_generator import RadarDiagramQualityReportGenerator

class SegregationSystem:

    def __init__(self):
        self.segregation_system_config = None

    def run(self, prepared_session):
        if self.segregation_system_config is None:
            print("Configuration Error")
            exit(1)

        # prepared session collecting
        print(prepared_session)


        # balance bar chart generation

        # radar diagram generation


        # splitting dataset

