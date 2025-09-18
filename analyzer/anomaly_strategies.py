from abc import ABC, abstractmethod
from models.battery_health_report import (
    SoCDrift,
    CapacityFade,
    Overheating,
    VoltageImbalance,
    T,
)


# After implmentaion I found anomalies look like strategy design pattern fit
# and instead of create function for every anomaly it may look better this way
# every anomaly has type and has detect function they can vary in output so defined generic type T
class AnomalyDetectionStrategy(ABC):
    """Abstract base class for anomaly detection strategies"""

    def __init__(self):
        """Configuration for anomaly detection strategies"""
        self.voltage_imbalance_threshold: float = 0.1
        self.overheating_threshold: float = 60.0
        self.critical_temp_threshold: float = 80.0
        self.capacity_fade_threshold: float = 20.0
    
    @abstractmethod
    def detect(self, data: dict[str, any]) -> T:
        """Detect anomalies in the provided data"""
        pass
    
    @abstractmethod
    def get_anomaly_type(self) -> str:
        """Return the type of anomaly this strategy detects"""
        pass

    @abstractmethod
    def display_in_streamlit(self, anomaly_data: T, st) -> None:
        """Display the anomaly data in Streamlit"""
        pass


class VoltageImbalanceStrategy(AnomalyDetectionStrategy):
    """Strategy for detecting voltage imbalance between cells"""

    def get_anomaly_type(self) -> str:
        return "voltage_imbalance"

    def detect(self, data: dict[str, any]) -> VoltageImbalance:
        cells = data.get('cells', [])
        if not cells:
            return {"anomaly": False, "message": "No voltage data available"}

        cell_voltages = [c['voltage'] for c in cells]
        min_voltage = min(cell_voltages)
        max_voltage = max(cell_voltages)
        voltage_spread = round((max_voltage - min_voltage), 3)

        anomaly = voltage_spread > self.voltage_imbalance_threshold

        return VoltageImbalance(
            anomaly=anomaly,
            voltage_spread=voltage_spread,
            min_voltage=round(min_voltage, 3),
            max_voltage=round(max_voltage, 3),
            message=f"Voltage imbalance detected: {voltage_spread}V spread" if anomaly else "Voltage levels normal"
        )

    def display_in_streamlit(self, anomaly_data: VoltageImbalance, st):
        st.write(f"**{self.get_anomaly_type().replace('_', ' ').title()}**: {anomaly_data.message}")
        if not anomaly_data.anomaly:
            return
        st.write(f"  - Voltage spread: {anomaly_data.voltage_spread}V")
        st.write(f"  - Min voltage: {anomaly_data.min_voltage}V")
        st.write(f"  - Max voltage: {anomaly_data.max_voltage}V")


class OverheatingStrategy(AnomalyDetectionStrategy):
    """Strategy for detecting cell overheating"""
    
    def get_anomaly_type(self) -> str:
        return "overheating"
    
    def detect(self, data: dict[str, any]) -> Overheating:
        cells = data.get('cells', [])
        if not cells:
            return {"anomaly": False, "message": "No temperature data available"}

        cell_temperatures = [c['temperature'] for c in cells]
        max_temp = max(cell_temperatures)
        hot_cells = [temp for temp in cell_temperatures if temp > self.overheating_threshold]
        critical_cells = [temp for temp in cell_temperatures if temp > self.critical_temp_threshold]

        anomaly = len(hot_cells) > 0

        return Overheating(
            anomaly=anomaly,
            max_temperature=round(max_temp, 1),
            hot_cells_count=len(hot_cells),
            critical_cells_count=len(critical_cells),
            message=f"Overheating detected: {len(hot_cells)} cells above {self.overheating_threshold}°C" if anomaly else "Temperature levels normal"
        )
        
    def display_in_streamlit(self, anomaly_data: Overheating, st):
        st.write(f"**{self.get_anomaly_type().replace('_', ' ').title()}**: {anomaly_data.message}")
        if not anomaly_data.anomaly:
            return
        st.write(f"  - Max temperature: {anomaly_data.max_temperature}°C")
        st.write(f"  - Hot cells: {anomaly_data.hot_cells_count}")
        if anomaly_data.critical_cells_count > 0:
            st.write(f"  - Critical cells: {anomaly_data.critical_cells_count}")


class CapacityFadeStrategy(AnomalyDetectionStrategy):
    """Strategy for detecting capacity fade"""
    
    def get_anomaly_type(self) -> str:
        return "capacity_fade"
    
    def detect(self, data: dict[str, any]) -> CapacityFade:
        battery_pack = data.get('battery_pack', {})
        original_capacity = battery_pack.get('baseline_capacity_kWh', 0)
        current_capacity = battery_pack.get('current_capacity_kWh', 0)
        
        if original_capacity == 0:
            return {"anomaly": False, "message": "No capacity data available"}
            
        capacity_loss = ((original_capacity - current_capacity) / original_capacity) * 100
        anomaly = capacity_loss > self.capacity_fade_threshold
        
        return CapacityFade(
            anomaly=anomaly,
            capacity_loss_percent=round(capacity_loss, 2),
            message=f"Significant capacity fade detected: {capacity_loss:.1f}% loss" if anomaly else "Capacity levels normal"

        )
        
    def display_in_streamlit(self, anomaly_data: CapacityFade, st):
        st.write(f"**{self.get_anomaly_type().replace('_', ' ').title()}**: {anomaly_data.message}")
        if not anomaly_data.anomaly:
            return
        st.write(f"  - Capacity loss: {anomaly_data.capacity_loss_percent}%")


class SoCDriftStrategy(AnomalyDetectionStrategy):
    """Strategy for detecting SoC estimation drift"""
    
    def get_anomaly_type(self) -> str:
        return "soc_drift"
    
    def detect(self, data: dict[str, any]) -> SoCDrift:
        battery_usage_log = data.get('battery_usage_log', [])
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
        
        return SoCDrift(
            anomaly=anomaly,
            unrealistic_changes_count=len(unrealistic_changes),
            unrealistic_changes=unrealistic_changes,
            message=f"SoC drift detected: {len(unrealistic_changes)} unrealistic changes" if anomaly else "SoC estimation normal"
        )


    def display_in_streamlit(self, anomaly_data: SoCDrift, st):
        st.write(f"**{self.get_anomaly_type().replace('_', ' ').title()}**: {anomaly_data.message}")
        if not anomaly_data.anomaly:
            return

        st.write(f"  - Unrealistic changes: {anomaly_data.unrealistic_changes_count}")
        if anomaly_data.unrealistic_changes:
            st.write(f"  - Recent changes:")
            for i, change in enumerate(anomaly_data.unrealistic_changes[:3]):  # Show first 3
                st.write(f"    • {change.get('timestamp', 'Unknown')}: {change.get('change', 'N/A')}%:{change.get('event')}")
            if len(anomaly_data.unrealistic_changes) > 3:
                st.write(f"    • ... and {len(anomaly_data.unrealistic_changes) - 3} more")


class AnomalyDetectionContext:
    """Context class that uses anomaly detection strategies"""
    
    def __init__(self):
        self.strategies: list[AnomalyDetectionStrategy] = {
            VoltageImbalanceStrategy(),
            OverheatingStrategy(),
            CapacityFadeStrategy(),
            SoCDriftStrategy()
        }

    def detect_all_anomalies(
        self, battery_data: dict[str, any]
    ) -> dict[str, T]:
        """Run all registered strategies on the battery data"""
        results = {}

        for strategy in self.strategies:
            anomaly_type = strategy.get_anomaly_type()
            results[anomaly_type] = {
                'anomaly_data': strategy.detect(battery_data),
                'display_in_streamlit': strategy.display_in_streamlit
            }

        return results
