import io
from datetime import datetime
from fpdf import FPDF

from models.battery_health_report import BatteryHealthReport
from analyzer.anomaly_strategies import AnomalyDetectionContext
from analyzer.battery_health import BatteryHealth


class BatteryReportBuilder:
    def __init__(self):
        # Initialize anomaly detection context with strategy pattern
        self.anomaly_context = AnomalyDetectionContext()
        self.battery_health = BatteryHealth()
        
    @staticmethod
    def draw_title(pdf, txt: str):
        # Draw title
        pdf.set_font("Arial", size=16, style='B')
        pdf.cell(0, 20, txt, align="C", ln=True)

    def create_pdf(self, report_data):
        battery_health = report_data.battery_health
        anomalies = report_data.anomalies
        pdf = FPDF()
        pdf.set_title("Battery Health Report")
        pdf.add_page()

        # Draw title
        self.draw_title(pdf, "Battery Health Report")

        # Add vehicle id
        pdf.set_font("Arial", size=12, style='B')
        pdf.cell(25, 20, "Vehicle ID:")
        pdf.set_font("Arial", size=12)
        pdf.cell(65, 20, report_data.vehicle_id)

        # Add datetime
        pdf.set_font("Arial", size=12, style='B')
        pdf.cell(40, 20, "Report Generated:")
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 20, report_data.timestamp, ln=True)
        
        # new line
        # Add soh
        pdf.set_font("Arial", size=12, style='B')
        pdf.cell(50, 20, "SOH: ")
        pdf.set_font("Arial", size=12)
        pdf.cell(30, 20, str(battery_health.state_of_health_percent) + '%', ln=True)
        
        # Add charge cycle count
        pdf.set_font("Arial", size=12, style='B')
        pdf.cell(50, 20, "Charge Cycles Count: ")
        pdf.set_font("Arial", size=12)
        pdf.cell(30, 20, str(battery_health.charge_cycles), ln=True)

        # Add discharge cycle count
        pdf.set_font("Arial", size=12, style='B')
        pdf.cell(50, 20, "Discharge Cycles Count: ")
        pdf.set_font("Arial", size=12)
        pdf.cell(30, 20, str(battery_health.discharge_cycles), ln=True)

        # Anomaly Detection
        self.draw_title(pdf, 'Anomaly Detection')
        pdf.set_font("Arial", size=12, style='B')

        for anomaly_type, anomaly_data in anomalies.items():
            pdf.set_font("Arial", size=12, style='B')
            pdf.cell(50, 20, anomaly_type.replace('_', ' ').title())
            pdf.set_font("Arial", size=12)
            pdf.cell(30, 20, anomaly_data.anomaly_data.message, ln=True)

        pdf_output = pdf.output(dest="S").encode("latin1")
        return io.BytesIO(pdf_output)

    def generate_battery_report(
        self, battery_data: dict
    ) -> BatteryHealthReport:
        """
        Generate comprehensive battery health report
        """
        try:
            battery_health = self.battery_health.generate_battery_health(battery_data)
            
            # Anomaly detection
            anomalies = self.anomaly_context.detect_all_anomalies(battery_data)
            
            # Generate report
            report = BatteryHealthReport(
                vehicle_id=battery_data.get('vehicle_id', 'Unknown'),
                timestamp=battery_data.get('timestamp', datetime.now().isoformat()),
                battery_health=battery_health,
                anomalies=anomalies,
            )
            return report
            
        except Exception as e:
            return {
                "error": f"Failed to generate battery report: {str(e)}",
                "vehicle_id": battery_data.get('vehicle_id', 'Unknown'),
                "timestamp": datetime.now().isoformat()
            }
