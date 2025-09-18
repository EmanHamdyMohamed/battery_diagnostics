from datetime import datetime

from models.battery_health_report import BatteryHealthReport
from analyzer.anomaly_strategies import AnomalyDetectionContext
from analyzer.battery_health import BatteryHealth


class BatteryReportBuilder:
    def __init__(self):
        # Initialize anomaly detection context with strategy pattern
        self.anomaly_context = AnomalyDetectionContext()
        self.battery_health = BatteryHealth()

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
