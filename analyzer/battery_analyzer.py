from datetime import datetime
import statistics


class BatteryAnalyzer:
    def __init__(self):
        self.voltage_imbalance_threshold = 0.1  # V - max difference between cells
        self.overheating_threshold = 60  # °C - cell overheating threshold
        self.critical_temp_threshold = 80  # °C - critical temperature
        self.capacity_fade_threshold = 20  # % - significant capacity loss

    @staticmethod
    def calculate_state_of_health(
        original_capacity: float, current_capacity: float
    ) -> float:
        """
        Calculate State of Health (SoH) as percentage
        SoH = (Current Usable Capacity / Original Rated Capacity) × 100%
        """
        if original_capacity <= 0:
            raise ValueError("Original capacity must be positive")
        soh = (current_capacity / original_capacity) * 100
        return round(soh, 2)

    @staticmethod
    def count_charge_cycles(battery_usage_log: list[dict]) -> int:
        """
        Count full charge cycles from usage log
        Full_Cycles = Σ(|SoC_End - SoC_Start|) / 100
        """
        charge_accumulated = 0
        charge_cycles = 0
        for log in battery_usage_log:
            if log['event'] == 'charge':
                charge_accumulated += abs(log['soc_end'] - log['soc_start'])
                while charge_accumulated >= 100:
                    charge_cycles += 1
                    charge_accumulated -= 100
        return charge_cycles

    @staticmethod
    def count_discharge_cycles(battery_usage_log: list[dict]) -> int:
        """
        Count full discharge cycles from usage log
        Full_Cycles = Σ(|SoC_Start - SoC_End|) / 100
        """
        discharge_accumulated = 0
        discharge_cycles = 0
        for log in battery_usage_log:
            if log['event'] == 'discharge':
                discharge_accumulated += abs(log['soc_start'] - log['soc_end'])
                while discharge_accumulated >= 100:
                    discharge_cycles += 1
                    discharge_accumulated -= 100
        return discharge_cycles

    def detect_voltage_imbalance(self, cells: list[dict]) -> dict[str, any]:
        """
        Detect voltage imbalance between cells
        Returns anomaly details if voltage difference exceeds threshold
        """
        if not cells:
            return {"anomaly": False, "message": "No voltage data available"}

        cell_voltages = [c['voltage'] for c in cells]

        min_voltage = min(cell_voltages)
        max_voltage = max(cell_voltages)
        voltage_spread = round((max_voltage - min_voltage), 3)

        anomaly = voltage_spread > self.voltage_imbalance_threshold

        return {
            "anomaly": anomaly,
            "voltage_spread": voltage_spread,
            "min_voltage": round(min_voltage, 3),
            "max_voltage": round(max_voltage, 3),
            "threshold": self.voltage_imbalance_threshold,
            "message": f"Voltage imbalance detected: {voltage_spread}V spread" if anomaly else "Voltage levels normal"
        }

    def detect_overheating(self, cells: list[dict]) -> dict[str, any]:
        """
        Detect cell overheating
        Returns anomaly details if any cell exceeds temperature thresholds
        """
        if not cells:
            return {"anomaly": False, "message": "No temperature data available"}

        cell_temperatures = [c['temperature'] for c in cells]

        max_temp = max(cell_temperatures)
        avg_temp = statistics.mean(cell_temperatures)
        hot_cells = [temp for temp in cell_temperatures if temp > self.overheating_threshold]
        critical_cells = [temp for temp in cell_temperatures if temp > self.critical_temp_threshold]

        anomaly = len(hot_cells) > 0

        severity = "critical" if len(critical_cells) > 0 else "warning" if anomaly else "normal"

        return {
            "anomaly": anomaly,
            "max_temperature": round(max_temp, 1),
            "avg_temperature": round(avg_temp, 1),
            "hot_cells_count": len(hot_cells),
            "critical_cells_count": len(critical_cells),
            "severity": severity,
            "thresholds": {
                "overheating": self.overheating_threshold,
                "critical": self.critical_temp_threshold
            },
            "message": f"Overheating detected: {len(hot_cells)} cells above {self.overheating_threshold}°C" if anomaly else "Temperature levels normal"
        }

    def detect_capacity_fade(
        self, original_capacity: float, current_capacity: float
    ) -> dict[str, any]:
        """
        Detect significant capacity fade
        Returns anomaly details if capacity loss exceeds threshold
        """
        capacity_loss = ((original_capacity - current_capacity) / original_capacity) * 100
        anomaly = capacity_loss > self.capacity_fade_threshold
        
        return {
            "anomaly": anomaly,
            "capacity_loss_percent": round(capacity_loss, 2),
            "original_capacity": original_capacity,
            "current_capacity": current_capacity,
            "threshold": self.capacity_fade_threshold,
            "message": f"Significant capacity fade detected: {capacity_loss:.1f}% loss" if anomaly else "Capacity levels normal"
        }

    @staticmethod
    def detect_soc_drift(battery_usage_log: list[dict]) -> dict[str, any]:
        """
        Detect SoC estimation drift by analyzing charge/discharge patterns
        Returns anomaly details if SoC changes are unrealistic
        """
        if not battery_usage_log:
            return {"anomaly": False, "message": "No usage data available"}
            
        unrealistic_changes = []
        for log in battery_usage_log:
            soc_change = abs(log['soc_end'] - log['soc_start'])
            if soc_change > 100:  # SoC should never change by more than 100%
                unrealistic_changes.append({
                    "timestamp": log.get('timestamp', 'unknown'),
                    "soc_change": soc_change,
                    "event": log['event']
                })
        
        anomaly = len(unrealistic_changes) > 0
        
        return {
            "anomaly": anomaly,
            "unrealistic_changes_count": len(unrealistic_changes),
            "unrealistic_changes": unrealistic_changes,
            "threshold": 100,
            "message": f"SoC drift detected: {len(unrealistic_changes)} unrealistic changes" if anomaly else "SoC estimation normal"
        }

    def detect_anomalies(self, battery_data: dict) -> dict[str, any]:
        """
        Comprehensive anomaly detection for battery pack
        Returns all detected anomalies with severity levels
        anomalies usually fall into categories
        1. Voltage Imbalance => done
        2. Overheating (cell or pack) => done
        3. High Internal Resistance
        4. Abnormal Current Flow
        5. Capacity Fade => done
        6. SoC Drift / Estimation Error => done
        """
        anomalies = {
            "voltage_imbalance": self.detect_voltage_imbalance(battery_data.get('cells', [])),
            "overheating": self.detect_overheating(battery_data.get('cells', [])),
            "capacity_fade": self.detect_capacity_fade(
                battery_data.get('battery_pack', {}).get('baseline_capacity_kWh', 0),
                battery_data.get('battery_pack', {}).get('current_capacity_kWh', 0)
            ),
            "soc_drift": self.detect_soc_drift(battery_data.get('battery_usage_log', []))
        }

        return anomalies

    def generate_battery_report(self, battery_data: dict) -> dict[str, any]:
        """
        Generate comprehensive battery health report
        """
        try:
            # Basic calculations
            battery_pack = battery_data.get('battery_pack', {})
            usage_log = battery_data.get('battery_usage_log', [])
            
            soh = self.calculate_state_of_health(
                battery_pack.get('baseline_capacity_kWh', 0),
                battery_pack.get('current_capacity_kWh', 0)
            )
            
            charge_cycles = self.count_charge_cycles(usage_log)
            discharge_cycles = self.count_discharge_cycles(usage_log)
            
            # Anomaly detection
            anomalies = self.detect_anomalies(battery_data)
            
            # Generate report
            report = {
                "vehicle_id": battery_data.get('vehicle_id', 'Unknown'),
                "timestamp": battery_data.get('timestamp', datetime.now().isoformat()),
                "battery_health": {
                    "state_of_health_percent": soh,
                    "charge_cycles": charge_cycles,
                    "discharge_cycles": discharge_cycles,
                },
                "anomalies": anomalies,
            }
            
            return report
            
        except Exception as e:
            return {
                "error": f"Failed to generate battery report: {str(e)}",
                "vehicle_id": battery_data.get('vehicle_id', 'Unknown'),
                "timestamp": datetime.now().isoformat()
            }
